import asyncio
import re
import time
from urllib.parse import urljoin, urlparse

import httpx
import orjson
import yaml
from aiolimiter import AsyncLimiter
from selectolax.parser import HTMLParser


class RobotsCache:
    def __init__(self, client: httpx.AsyncClient, user_agent: str):
        self.client = client
        self.user_agent = user_agent
        self.cache: dict[str, tuple[float, list[tuple[str, bool]]]] = {}

    async def allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        now = time.time()
        rules = self.cache.get(base)
        if rules is None or now - rules[0] > 3600:
            robots_url = urljoin(base, "/robots.txt")
            try:
                resp = await self.client.get(robots_url, timeout=10)
                text = resp.text if resp.status_code == 200 else ""
            except Exception:
                text = ""
            parsed_rules = self._parse(text)
            self.cache[base] = (now, parsed_rules)
            rules = self.cache[base]
        return self._check(rules[1], url)

    def _parse(self, robots_text: str) -> list[tuple[str, bool]]:
        agent = None
        disallows: list[str] = []
        allows: list[str] = []
        for line in robots_text.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.lower().startswith('user-agent:'):
                agent = line.split(':', 1)[1].strip()
            elif agent in ('*', 'MyGirlGPTScraper'):
                if line.lower().startswith('disallow:'):
                    path = line.split(':', 1)[1].strip()
                    if path:
                        disallows.append(path)
                elif line.lower().startswith('allow:'):
                    path = line.split(':', 1)[1].strip()
                    if path:
                        allows.append(path)
        rules: list[tuple[str, bool]] = [(p, False) for p in disallows] + [(p, True) for p in allows]
        return rules

    def _check(self, rules: list[tuple[str, bool]], url: str) -> bool:
        path = urlparse(url).path or '/'
        decision = True
        match_len = -1
        for rule, allow in rules:
            if path.startswith(rule) and len(rule) > match_len:
                decision = allow
                match_len = len(rule)
        return decision


def is_allowed_start_url(url: str, allowlist: list[str]) -> bool:
    return any(url.startswith(prefix) for prefix in allowlist)


def extract_links(html: str, base_url: str) -> list[str]:
    tree = HTMLParser(html)
    links = []
    for a in tree.css('a[href]'):
        href = a.attributes.get('href', '')
        if href.startswith('#') or href.startswith('mailto:'):
            continue
        links.append(urljoin(base_url, href))
    return links


def extract_text(html: str) -> str:
    tree = HTMLParser(html)
    # remove scripts/styles
    for node in tree.css('script,style,noscript'):
        node.decompose()
    text = tree.text(separator=' ').strip()
    return re.sub(r"\s+", " ", text)


def is_nsfw_candidate(text: str, keywords: list[str]) -> bool:
    lower = text.lower()
    return any(k in lower for k in keywords)


def violates_exclusions(text: str, patterns: list[str]) -> bool:
    for p in patterns:
        if re.search(p, text):
            return True
    return False


async def crawl(config_path: str = './dataset/config.yaml'):
    cfg = yaml.safe_load(open(config_path, 'r'))
    allowlist = cfg['allowlist']
    ua = cfg['user_agent']
    concurrency = cfg.get('concurrency', 5)
    rate = cfg.get('rate_limit_per_host_per_minute', 60)
    timeout = cfg.get('request_timeout_seconds', 20)
    max_pages_per_domain = cfg.get('max_pages_per_domain', 200)
    nsfw_keywords = cfg.get('nsfw_keywords', [])
    exclude_patterns = cfg.get('exclude_patterns', [])
    raw_dir = cfg['raw_dir']

    client = httpx.AsyncClient(headers={'User-Agent': ua}, follow_redirects=True, timeout=timeout)
    robots = RobotsCache(client, ua)

    limiter_by_host: dict[str, AsyncLimiter] = {}
    seen: set[str] = set()
    per_domain_count: dict[str, int] = {}
    queue: asyncio.Queue[str] = asyncio.Queue()

    for start in allowlist:
        await queue.put(start)

    async def worker():
        while True:
            try:
                url = await queue.get()
            except Exception:
                break
            parsed = urlparse(url)
            domain = parsed.netloc
            limiter = limiter_by_host.setdefault(domain, AsyncLimiter(rate, 60))
            if url in seen:
                queue.task_done()
                continue
            seen.add(url)
            if not is_allowed_start_url(url, allowlist):
                queue.task_done()
                continue
            if not await robots.allowed(url):
                queue.task_done()
                continue
            count = per_domain_count.get(domain, 0)
            if count >= max_pages_per_domain:
                queue.task_done()
                continue
            async with limiter:
                try:
                    resp = await client.get(url)
                except Exception:
                    queue.task_done()
                    continue
            if resp.status_code != 200 or 'text/html' not in resp.headers.get('content-type', ''):
                queue.task_done()
                continue
            html = resp.text
            text = extract_text(html)
            # NSFW candidate + not violating exclusions
            if is_nsfw_candidate(text, nsfw_keywords) and not violates_exclusions(text, exclude_patterns):
                record = {
                    'url': url,
                    'title': None,
                    'text': text,
                }
                path = f"{raw_dir}/{hash(url)}.json"
                with open(path, 'wb') as f:
                    f.write(orjson.dumps(record))
            per_domain_count[domain] = count + 1
            for link in extract_links(html, url):
                if link not in seen and is_allowed_start_url(link, allowlist):
                    await queue.put(link)
            queue.task_done()

    tasks = [asyncio.create_task(worker()) for _ in range(concurrency)]
    await queue.join()
    for t in tasks:
        t.cancel()
    await client.aclose()


if __name__ == '__main__':
    asyncio.run(crawl())
