import chromadb
from sentence_transformers import SentenceTransformer
from app.core.config import settings

_model = None
_collection = None

def load():
    global _model, _collection
    _model = SentenceTransformer(settings.embedding_model, device="cpu")
    client = chromadb.PersistentClient(path=settings.vector_store_path)
    _collection = client.get_collection(settings.collection_name)

def retrieve(query: str, k: int = None):
    k = k or settings.top_k
    qv = _model.encode([query], normalize_embeddings=True)
    r = _collection.query(query_embeddings=qv.tolist(), n_results=k)
    return [{"text": doc, **meta, "score": round(1 - dist, 3)}
            for doc, meta, dist in zip(r["documents"][0], r["metadatas"][0], r["distances"][0])]