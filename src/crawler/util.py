from __future__ import annotations

import hashlib
from urllib.parse import urlparse

from simhash import Simhash
from url_normalize import url_normalize
from tldextract import extract as tld_extract


def normalize_url(url: str) -> str:
    return url_normalize(url)


def get_registered_domain(url: str) -> str:
    p = urlparse(url)
    ext = tld_extract(p.netloc)
    if not ext.domain:
        return ""
    return ".".join([ext.domain, ext.suffix]) if ext.suffix else ext.domain


def is_domain_allowed(url: str, allowlist: list[str]) -> bool:
    reg = get_registered_domain(url)
    return reg in allowlist


def content_simhash(text: str) -> int:
    return Simhash(text).value


def hamming_distance(x: int, y: int) -> int:
    return bin(x ^ y).count("1")