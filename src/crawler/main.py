from __future__ import annotations

import asyncio
import json
from collections import deque
from typing import Set

import aiohttp
import orjson

from .config import CrawlerConfig, DEFAULT_USER_AGENT, parse_args
from .robots import RobotsCache
from .fetch import DomainLimiter, fetch_text
from .extract import extract_content_and_links
from .util import normalize_url, is_domain_allowed, content_simhash, hamming_distance


class JsonlWriter:
    def __init__(self, path: str):
        self._path = path
        self._fp = open(path, "wb")

    def write(self, obj: dict) -> None:
        self._fp.write(orjson.dumps(obj) + b"\n")

    def close(self) -> None:
        self._fp.close()


async def crawl(cfg: CrawlerConfig) -> None:
    seeds: list[str] = []
    with open(cfg.seeds_file, "r", encoding="utf-8") as f:
        seeds = [line.strip() for line in f if line.strip()]

    queue: deque[str] = deque(seeds)
    visited: Set[str] = set()
    fingerprints: list[int] = []

    robots = RobotsCache(user_agent=DEFAULT_USER_AGENT)
    domain_limiter = DomainLimiter(cfg.per_domain_rps)

    connector = aiohttp.TCPConnector(limit=cfg.concurrency)
    timeout = aiohttp.ClientTimeout(total=cfg.timeout_seconds)
    headers = {"User-Agent": DEFAULT_USER_AGENT}

    writer = JsonlWriter(cfg.output_path)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout, headers=headers) as session:
        pages_collected = 0
        while queue and pages_collected < cfg.max_pages:
            url = normalize_url(queue.popleft())
            if url in visited:
                continue
            visited.add(url)

            if not is_domain_allowed(url, cfg.allowlist_domains):
                continue

            if not await robots.allowed(session, url):
                continue

            status, html = await fetch_text(session, url, cfg.timeout_seconds, domain_limiter.for_url(url))
            if status != 200 or not html:
                continue

            text, links = extract_content_and_links(url, html, cfg.max_content_chars)
            if not text:
                continue

            fp = content_simhash(text)
            is_dup = any(hamming_distance(fp, prev) <= 3 for prev in fingerprints)
            if is_dup:
                continue
            fingerprints.append(fp)

            writer.write({
                "url": url,
                "text": text,
            })
            pages_collected += 1

            for link in links:
                if link not in visited:
                    queue.append(link)

    writer.close()


def main() -> None:
    cfg = parse_args()
    asyncio.run(crawl(cfg))


if __name__ == "__main__":
    main()