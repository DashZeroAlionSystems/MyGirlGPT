import glob
import os
import re
from typing import Iterator

import orjson
import yaml
from tqdm import tqdm


def iter_json_files(raw_dir: str) -> Iterator[dict]:
    for p in glob.glob(os.path.join(raw_dir, '*.json')):
        try:
            with open(p, 'rb') as f:
                yield orjson.loads(f.read())
        except Exception:
            continue


def split_into_turns(text: str) -> list[str]:
    # naive sentence split for dialogue seeds; you can replace with spaCy
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def to_girlfriend_dialogue(text: str) -> list[dict]:
    turns = split_into_turns(text)
    dialogue = []
    speaker = 'user'
    for t in turns[:40]:  # cap turns per sample
        dialogue.append({'role': speaker, 'content': t})
        speaker = 'assistant' if speaker == 'user' else 'user'
    # Ensure it ends with assistant message
    if dialogue and dialogue[-1]['role'] == 'user':
        dialogue.append({'role': 'assistant', 'content': 'Mm-hmm… tell me more, baby.'})
    return dialogue


def process(config_path: str = './dataset/config.yaml'):
    cfg = yaml.safe_load(open(config_path, 'r'))
    raw_dir = cfg['raw_dir']
    clean_dir = cfg['clean_dir']
    out_file = cfg['jsonl_file']
    os.makedirs(clean_dir, exist_ok=True)
    os.makedirs(os.path.dirname(out_file), exist_ok=True)

    with open(out_file, 'wb') as out:
        for rec in tqdm(iter_json_files(raw_dir)):
            text = rec.get('text', '')
            if not text:
                continue
            dialogue = to_girlfriend_dialogue(text)
            item = {
                'source_url': rec.get('url'),
                'dialogue': dialogue,
                'style': 'nsfw-girlfriend',
            }
            out.write(orjson.dumps(item))
            out.write(b"\n")


if __name__ == '__main__':
    process()
