from utils.llm_client import call_llm

def validate_and_compose(query, chunks):
    """Validates if the retrieved docs can answer the query and generates a response."""
    if not chunks:
        return {"answerable": "no", "confidence": 0.0, "response": "", "evidence_span": "", "reasoning": "No documents retrieved."}

    context = "\n\n".join([f"DOC {i+1}:\n{c['text']}" for i, c in enumerate(chunks[:5])])

    messages = [
        {"role": "system", "content": """You are a helpful, human-like customer support agent.
Read the user query and the provided documentation chunks.
1. Determine if the documents contain enough information to safely answer the query (or if the answer can be logically inferred from the documents). (yes/no)
2. Assign a confidence score from 0.0 to 1.0.
3. If answerable=yes, extract the most relevant quote as 'evidence_span'.
4. Generate a direct, professional response. Synthesize the information into a cohesive answer without overly conversational filler (do not over-apologize). Do not mention "the documentation" or "the excerpt".
5. Provide a 1-sentence reasoning for your decision.

Output JSON strictly with keys: 'answerable', 'confidence', 'evidence_span', 'response', 'reasoning'."""},
        {"role": "user", "content": f"Query: {query}\n\nDocuments:\n{context}"}
    ]

    result = call_llm(messages, response_format=True)
    if isinstance(result, dict):
        return result
    return {"answerable": "no", "confidence": 0.0, "response": "", "evidence_span": "", "reasoning": "LLM validation failed."}


def compose_response(query, chunks):
    """Dedicated response generation — called when retrieval score is strong but validator returned no response.
    Does NOT validate. Just answers from the top chunks."""
    if not chunks:
        return ""

    top_text = "\n\n".join([c["text"] for c in chunks[:5]])[:4000]

    messages = [
        {"role": "system", "content": """You are a direct, professional support agent. 
Answer the user's question by synthesizing the provided documentation excerpts.
Provide the answer clearly and concisely without overly apologetic or conversational filler.
Do not just copy-paste; connect the concepts and draw logical conclusions based on the text. 
Never say "according to the documentation".
If the excerpts do not contain enough information to deduce the answer, politely say you couldn't find the answer."""},
        {"role": "user", "content": f"Customer query: {query}\n\nDocumentation excerpt:\n{top_text}\n\nAnswer:"}
    ]

    result = call_llm(messages, response_format=False)
    return result.strip() if result else ""
