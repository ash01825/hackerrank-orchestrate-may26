import re
from rank_bm25 import BM25Okapi
from ingestion.loader import load_and_chunk_corpus

STOP_WORDS = {
    "i", "me", "my", "we", "our", "you", "your", "he", "him", "she", "her",
    "it", "its", "they", "them", "what", "which", "who", "this", "that",
    "am", "is", "are", "was", "were", "be", "been", "have", "has", "had",
    "do", "does", "did", "a", "an", "the", "and", "but", "if", "or",
    "of", "at", "by", "for", "with", "into", "to", "from", "in", "out",
    "on", "so", "no", "not", "only", "can", "will", "just", "should", "now",
    "s", "t",
}


class Indexer:
    def __init__(self):
        chunks = load_and_chunk_corpus()
        self.ecosystem_indices = {}

        for eco in set(c["ecosystem"] for c in chunks):
            eco_chunks = [c for c in chunks if c["ecosystem"] == eco]
            tokenized = [self.tokenize(c["text"]) for c in eco_chunks]
            self.ecosystem_indices[eco] = {
                "bm25": BM25Okapi(tokenized),
                "chunks": eco_chunks,
            }

    def tokenize(self, text):
        tokens = re.findall(r'\w+', text.lower())
        result = []
        for t in tokens:
            if t in STOP_WORDS:
                continue
            result.append(t)
            if len(t) > 3:
                if t.endswith('ies'):
                    result.append(t[:-3] + 'y')
                elif t.endswith('es') and not t.endswith('ses'):
                    result.append(t[:-2])
                elif t.endswith('s') and not t.endswith('ss'):
                    result.append(t[:-1])
        return result


_instance = None

def get_indexer():
    global _instance
    if _instance is None:
        _instance = Indexer()
    return _instance
