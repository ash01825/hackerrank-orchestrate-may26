import numpy as np
from .bm25 import get_indexer
from . import embeddings


class HybridRetriever:
    def __init__(self):
        self.idx = get_indexer()
        self.doc_embeddings = {}
        for eco, data in self.idx.ecosystem_indices.items():
            texts = [c["text"] for c in data["chunks"]]
            if texts:
                self.doc_embeddings[eco] = embeddings.embed_texts(texts)

    def retrieve(self, query, ecosystem, top_k=5):
        if ecosystem not in self.doc_embeddings:
            return []

        chunks = self.idx.ecosystem_indices[ecosystem]["chunks"]
        query_tokens = self.idx.tokenize(query)
        bm25_scores = self.idx.ecosystem_indices[ecosystem]["bm25"].get_scores(query_tokens)

        max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1.0
        bm25_norm = np.array(bm25_scores) / max_bm25

        query_emb = embeddings.embed_texts([query])[0]
        doc_embs = self.doc_embeddings[ecosystem]
        sim_scores = np.dot(doc_embs, query_emb) / (
            np.linalg.norm(doc_embs, axis=1) * np.linalg.norm(query_emb) + 1e-9
        )

        hybrid_scores = 0.5 * bm25_norm + 0.5 * sim_scores
        scored = sorted(zip(chunks, hybrid_scores), key=lambda x: x[1], reverse=True)

        results = []
        for chunk, score in scored[:top_k]:
            results.append({**chunk, "hybrid_score": float(score)})
        return results


_instance = None

def get_retriever():
    global _instance
    if _instance is None:
        _instance = HybridRetriever()
    return _instance
