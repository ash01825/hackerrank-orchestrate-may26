import numpy as np
from .bm25 import get_indexer
from . import embeddings

class HybridRetriever:
    def __init__(self):
        self.idx = get_indexer()
        self.doc_embeddings = {}
        
        # Build embeddings per ecosystem
        for eco, data in self.idx.ecosystem_indices.items():
            chunks = data["chunks"]
            texts = [c["text"] for c in chunks]
            if texts:
                self.doc_embeddings[eco] = embeddings.embed_texts(texts)

    def retrieve(self, query, ecosystem, top_k=5):
        if ecosystem not in self.doc_embeddings:
            return []
            
        chunks = self.idx.ecosystem_indices[ecosystem]["chunks"]
        if not chunks:
            return []
            
        # BM25 scores
        query_tokens = self.idx.tokenize(query)
        bm25_scores = self.idx.ecosystem_indices[ecosystem]["bm25"].get_scores(query_tokens)
        
        # Normalize BM25
        max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1.0
        bm25_norm = np.array(bm25_scores) / max_bm25
            
        # Semantic scores
        query_emb = embeddings.embed_texts([query])[0]
        doc_embs = self.doc_embeddings[ecosystem]
        
        norm_query = np.linalg.norm(query_emb)
        norm_docs = np.linalg.norm(doc_embs, axis=1)
        sim_scores = np.dot(doc_embs, query_emb) / (norm_docs * norm_query + 1e-9)
        
        # Hybrid score (semantic prioritized)
        hybrid_scores = 0.3 * bm25_norm + 0.7 * sim_scores
        
        scored = list(zip(chunks, hybrid_scores))
        scored.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for chunk, score in scored[:top_k]:
            res = chunk.copy()
            res["hybrid_score"] = float(score)
            results.append(res)
            
        return results

_instance = None
def get_retriever():
    global _instance
    if _instance is None:
        _instance = HybridRetriever()
    return _instance
