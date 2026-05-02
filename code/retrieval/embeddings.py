import hashlib
import os

import numpy as np
from sentence_transformers import SentenceTransformer

from config.enums import BASE_DIR

_model = None
MODEL_NAME = "all-MiniLM-L6-v2"
CACHE_DIR = os.path.join(BASE_DIR, "data", "embeddings")

def get_model():
    global _model
    if _model is None:
        print("  [embedding] Loading MiniLM model (first run only)...")
        _model = SentenceTransformer(MODEL_NAME)
        print("  [embedding] Model ready.")
    return _model

def embed_texts(texts):
    model = get_model()
    return model.encode(texts, convert_to_tensor=False)

def _cache_path(namespace, texts):
    digest = hashlib.sha256()
    digest.update(MODEL_NAME.encode("utf-8"))
    digest.update(namespace.encode("utf-8"))
    for text in texts:
        digest.update(b"\0")
        digest.update(text.encode("utf-8", errors="ignore"))
    return os.path.join(CACHE_DIR, f"{namespace}_{digest.hexdigest()[:16]}.npy")

def embed_texts_cached(texts, namespace):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = _cache_path(namespace, texts)
    if os.path.exists(path):
        return np.load(path)

    vectors = np.asarray(embed_texts(texts))
    np.save(path, vectors)
    return vectors
