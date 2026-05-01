from sentence_transformers import SentenceTransformer

_model = None

def get_model():
    global _model
    if _model is None:
        print("  [embedding] Loading MiniLM model (first run only)...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        print("  [embedding] Model ready.")
    return _model

def embed_texts(texts):
    model = get_model()
    return model.encode(texts, convert_to_tensor=False)
