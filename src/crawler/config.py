import argparse
from dataclasses import dataclass

DEFAULT_USER_AGENT = (
    "SafeCrawler/1.0 (+https://example.com; compliant; contact: crawler@example.com)"
)


@dataclass
class CrawlerConfig:
    seeds_file: str
    allowlist_domains: list[str]
    max_pages: int
    concurrency: int
    per_domain_rps: float
    output_path: str
    timeout_seconds: int
    max_content_chars: int


def parse_args() -> CrawlerConfig:
    parser = argparse.ArgumentParser(description="Safe compliant web crawler")
    parser.add_argument("--seeds", required=True, help="Path to seeds file")
    parser.add_argument("--max-pages", type=int, default=200)
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--per-domain-rps", type=float, default=1.0)
    parser.add_argument("--output", required=True, help="Output JSONL path")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--max-content-chars", type=int, default=100000)
    args = parser.parse_args()

    with open(args.seeds, "r", encoding="utf-8") as f:
        seed_urls = [line.strip() for line in f if line.strip()]

    # Allow only the domains present in the seeds list
    from tldextract import extract as tld_extract

    allowlist = sorted(
        {
            ".".join(
                [p for p in [tld_extract(u).domain, tld_extract(u).suffix] if p]
            )
            for u in seed_urls
        }
    )

    return CrawlerConfig(
        seeds_file=args.seeds,
        allowlist_domains=allowlist,
        max_pages=args.max_pages,
        concurrency=args.concurrency,
        per_domain_rps=args.per_domain_rps,
        output_path=args.output,
        timeout_seconds=args.timeout,
        max_content_chars=args.max_content_chars,
    )