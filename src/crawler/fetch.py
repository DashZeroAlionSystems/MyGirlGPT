import asyncio
from collections import defaultdict
from urllib.parse import urlparse

import aiohttp
from aiolimiter import AsyncLimiter


class DomainLimiter:
    def __init__(self, rps: float):
        self._limiters: dict[str, AsyncLimiter] = defaultdict(lambda: AsyncLimiter(rps, time_period=1))

    def for_url(self, url: str) -> AsyncLimiter:
        domain = urlparse(url).netloc
        return self._limiters[domain]


async def fetch_text(session: aiohttp.ClientSession, url: str, timeout_s: int, limiter: AsyncLimiter) -> tuple[int | None, str | None]:
    async with limiter:
        try:
            async with session.get(url, timeout=timeout_s) as resp:
                status = resp.status
                if status != 200:
                    return status, None
                content_type = resp.headers.get("Content-Type", "")
                if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                    return status, None
                text = await resp.text(errors="ignore")
                return status, text
        except Exception:
            return None, None