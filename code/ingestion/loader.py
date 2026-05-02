import os
import re
from config.enums import DATA_DIR, Ecosystem

def load_and_chunk_corpus():
    chunks = []
    chunk_id = 0

    for ecosystem in [Ecosystem.HACKERRANK, Ecosystem.CLAUDE, Ecosystem.VISA]:
        eco_dir = os.path.join(DATA_DIR, ecosystem.value.lower())
        if not os.path.exists(eco_dir):
            continue

        for root, _, files in os.walk(eco_dir):
            for fname in files:
                if not fname.endswith(('.md', '.txt', '.html')):
                    continue

                path = os.path.join(root, fname)
                with open(path, encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                section_path = os.path.relpath(root, eco_dir)
                if section_path == ".":
                    section_path = "general"

                heading = ""
                for block in re.split(r'\n\s*\n', content):
                    text = block.strip()
                    if text.startswith('#'):
                        heading = text.split('\n')[0].strip('# ')
                    if len(text) <= 30:
                        continue

                    body = f"{heading}\n{text}" if heading and not text.startswith('#') else text
                    chunks.append({
                        "chunk_id": f"chunk_{chunk_id}",
                        "ecosystem": ecosystem.value,
                        "doc_id": fname,
                        "section_path": section_path,
                        "text": body,
                    })
                    chunk_id += 1

    return chunks
