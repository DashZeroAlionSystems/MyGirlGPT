NSFW Dataset Pipeline (Opt-in)

Overview
- Creates an allowlisted, robots.txt-aware scraper for adult content sites
- Applies strict filters to exclude minors/illegal content and harmful topics
- Converts cleaned text into girlfriend-style dialogue JSONL for training

Safety
- Only scrapes domains in allowlist in config.yaml
- Respects robots.txt when accessible
- Exclusion regex blocks minors/illegal content; extend as needed
- For research use; ensure compliance with local laws and site ToS

Usage
1) Install deps:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r dataset/requirements.txt
```
2) Configure:
```bash
vi dataset/config.yaml
```
3) Run scraper:
```bash
python dataset/scraper.py
```
4) Process into dialogue JSONL:
```bash
python dataset/process_dataset.py
```

Output
- Raw JSON files: dataset/out/raw/*.json
- Final JSONL: dataset/out/girlfriend_dialogues.jsonl

Notes
- Consider adding site-specific parsers for higher quality
- Add deduping and language detection for larger crawls
