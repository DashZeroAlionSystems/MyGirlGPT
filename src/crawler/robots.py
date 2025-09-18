import asyncio
from urllib.parse import urlparse

import aiohttp
from urllib import robotparser


class RobotsCache:
    def __init__(self, user_agent: str):
        self._user_agent = user_agent
        self._cache: dict[str, robotparser.RobotFileParser] = {}
        self._lock = asyncio.Lock()

    async def allowed(self, session: aiohttp.ClientSession, url: str) -> bool:
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        async with self._lock:
            rp = self._cache.get(origin)
            if rp is None:
                rp = robotparser.RobotFileParser()
                robots_url = origin.rstrip("/") + "/robots.txt"
                try:
                    async with session.get(robots_url, timeout=10) as resp:
                        if resp.status == 200:
                            body = await resp.text(errors="ignore")
                            rp.parse(body.splitlines())
                        else:
                            rp.parse([])
                except Exception:
                    rp.parse([])
                self._cache[origin] = rp
        return self._cache[origin].can_fetch(self._user_agent, url)