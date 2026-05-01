def generate_response(top_chunk):
    if not top_chunk:
        return "I am sorry, this is out of scope from my capabilities."
        
    text = top_chunk.get("raw_text", "")
    if not text:
        text = top_chunk.get("text", "")
        
    template = f"Hi,\n\n{text}"
    return template
