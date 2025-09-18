from __future__ import annotations

from typing import Iterable
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from readability import Document


SFW_BLOCK_KEYWORDS = {
    "porn",
    "xxx",
    "sex",
    "nsfw",
    "adult",
    "explicit",
}


def extract_content_and_links(url: str, html: str, max_chars: int) -> tuple[str | None, list[str]]:
    doc = Document(html)
    title = (doc.short_title() or "").strip()
    summary_html = doc.summary(html_partial=True)

    soup = BeautifulSoup(summary_html, "lxml")
    for unwanted in soup(["script", "style", "noscript"]):
        unwanted.decompose()

    text = soup.get_text(" ", strip=True)

    text_lower = text.lower()
    if any(k in text_lower for k in SFW_BLOCK_KEYWORDS):
        return None, []

    if not text:
        return None, []

    if len(text) > max_chars:
        text = text[:max_chars]

    # Discover links from original HTML for better coverage
    soup_all = BeautifulSoup(html, "lxml")
    links: list[str] = []
    for a in soup_all.find_all("a", href=True):
        href = a.get("href")
        absolute = urljoin(url, href)
        links.append(absolute)

    return (f"{title}\n\n{text}" if title else text), links