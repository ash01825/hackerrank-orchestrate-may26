import re
import indexer
import config

def retrieve(ticket_text, ecosystem, top_k=5):
    idx = indexer.get_indexer()
    
    # Tokenize the query
    query_tokens = idx.tokenize(ticket_text)
    
    # If ecosystem is known, search only there
    if ecosystem in [config.Ecosystem.HACKERRANK.value, config.Ecosystem.CLAUDE.value, config.Ecosystem.VISA.value]:
        bm25 = idx.get_ecosystem_bm25(ecosystem)
        chunks = idx.get_ecosystem_chunks(ecosystem)
        
        if bm25 is None or len(chunks) == 0:
            return []
            
        scores = bm25.get_scores(query_tokens)
        
        scored_chunks = list(zip(chunks, scores))
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        
        top_results = []
        for chunk, score in scored_chunks[:top_k]:
            result = chunk.copy()
            result["bm25_score"] = score
            top_results.append(result)
            
        return top_results
        
    else:
        # If unknown ecosystem, search all and combine
        all_results = []
        for eco in [config.Ecosystem.HACKERRANK.value, config.Ecosystem.CLAUDE.value, config.Ecosystem.VISA.value]:
            bm25 = idx.get_ecosystem_bm25(eco)
            chunks = idx.get_ecosystem_chunks(eco)
            if bm25 and len(chunks) > 0:
                scores = bm25.get_scores(query_tokens)
                for chunk, score in zip(chunks, scores):
                    result = chunk.copy()
                    result["bm25_score"] = score
                    all_results.append(result)
                    
        all_results.sort(key=lambda x: x["bm25_score"], reverse=True)
        return all_results[:top_k]
