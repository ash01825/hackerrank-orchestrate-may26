import re
from rank_bm25 import BM25Okapi
from ingestion import loader as data_loader
from config import enums as config

class Indexer:
    def __init__(self):
        self.chunks = data_loader.load_and_chunk_corpus()
        self.ecosystem_indices = {}
        
        # Build an index per ecosystem to avoid cross-contamination
        ecosystems = set(c["ecosystem"] for c in self.chunks)
        
        for eco in ecosystems:
            eco_chunks = [c for c in self.chunks if c["ecosystem"] == eco]
            tokenized_corpus = [self.tokenize(c["text"]) for c in eco_chunks]
            bm25 = BM25Okapi(tokenized_corpus)
            self.ecosystem_indices[eco] = {
                "bm25": bm25,
                "chunks": eco_chunks
            }

    def tokenize(self, text):
        # Basic lowercase and split by non-word characters
        tokens = re.findall(r'\w+', text.lower())
        expanded = []
        for t in tokens:
            expanded.append(t)
            if len(t) > 3:
                if t.endswith('ies'):
                    expanded.append(t[:-3] + 'y')
                elif t.endswith('es') and not t.endswith('ses'):
                    expanded.append(t[:-2])
                elif t.endswith('s') and not t.endswith('ss'):
                    expanded.append(t[:-1])
        return expanded

    def get_ecosystem_chunks(self, ecosystem):
        if ecosystem in self.ecosystem_indices:
            return self.ecosystem_indices[ecosystem]["chunks"]
        return []

    def get_ecosystem_bm25(self, ecosystem):
        if ecosystem in self.ecosystem_indices:
            return self.ecosystem_indices[ecosystem]["bm25"]
        return None

# Singleton instance for the app lifecycle
_instance = None
def get_indexer():
    global _instance
    if _instance is None:
        _instance = Indexer()
    return _instance

if __name__ == "__main__":
    idx = get_indexer()
    for eco in idx.ecosystem_indices:
        print(f"Ecosystem: {eco}, Chunks: {len(idx.ecosystem_indices[eco]['chunks'])}")
