import os
import re
from config import enums as config

def load_and_chunk_corpus():
    chunks = []
    chunk_id_counter = 0
    
    # We will look through the ecosystems
    for ecosystem in [config.Ecosystem.HACKERRANK, config.Ecosystem.CLAUDE, config.Ecosystem.VISA]:
        eco_dir = os.path.join(config.DATA_DIR, ecosystem.value.lower())
        if not os.path.exists(eco_dir):
            continue
            
        for root, _, files in os.walk(eco_dir):
            for file in files:
                if file.endswith('.md') or file.endswith('.txt') or file.endswith('.html'):
                    path = os.path.join(root, file)
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Chunking by double newline (paragraphs/headings)
                    raw_chunks = re.split(r'\n\s*\n', content)
                    doc_id = file
                    
                    # Use directory name as a rough product area proxy
                    section_path = os.path.relpath(root, eco_dir)
                    if section_path == ".":
                        section_path = "general"
                        
                    current_heading = ""
                    for rc in raw_chunks:
                        text = rc.strip()
                        
                        # Keep track of last heading for context
                        if text.startswith('#'):
                            current_heading = text.split('\n')[0].strip('# ')
                            
                        # Avoid too small chunks
                        if len(text) > 30:
                            # Prepend heading if it's not a heading itself
                            if current_heading and not text.startswith('#'):
                                combined_text = f"{current_heading}\n{text}"
                            else:
                                combined_text = text
                                
                            chunks.append({
                                "chunk_id": f"chunk_{chunk_id_counter}",
                                "ecosystem": ecosystem.value,
                                "doc_id": doc_id,
                                "section_path": section_path,
                                "text": combined_text,
                                "raw_text": text
                            })
                            chunk_id_counter += 1
    return chunks

if __name__ == "__main__":
    c = load_and_chunk_corpus()
    print(f"Loaded {len(c)} chunks.")
