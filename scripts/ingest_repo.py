import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://host.docker.internal:11434")
QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
COLLECTION = os.environ.get("QDRANT_COLLECTION", "repo_docs")

app = FastAPI(title="Local Assistant API")

# load embedder
embedder = SentenceTransformer(EMBED_MODEL)
VECTOR_SIZE = embedder.get_sentence_embedding_dimension()

# qdrant client
qclient = QdrantClient(url=QDRANT_URL)

def ensure_collection():
    try:
        qclient.get_collection(collection_name=COLLECTION)
    except Exception:
        qclient.recreate_collection(
            collection_name=COLLECTION,
            vectors_config={"size": VECTOR_SIZE, "distance": "Cosine"},
        )

ensure_collection()

class AskRequest(BaseModel):
    prompt: str
    top_k: int = 3
    model: str = "llama3.1:8b-instruct-q6_K"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(req: AskRequest):
    # embed
    try:
        q_emb = embedder.encode([req.prompt], convert_to_numpy=True)[0].tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding error: {e}")

    # retrieve
    try:
        hits = qclient.search(collection_name=COLLECTION, query_vector=q_emb, limit=req.top_k)
    except Exception:
        hits = []

    context_texts = []
    for h in hits:
        payload = getattr(h, "payload", None) or (h.get("payload") if isinstance(h, dict) else {})
        if isinstance(payload, dict):
            context_texts.append(payload.get("text", ""))

    context_block = "\n\n".join(context_texts)
    full_prompt = f"Use the following context to answer the question.\n\nContext:\n{context_block}\n\nQuestion:\n{req.prompt}"

    gen_url = f"{OLLAMA_URL.rstrip('/')}/api/generate"
    body = {"model": req.model, "prompt": full_prompt, "max_tokens": 512}
    try:
        resp = requests.post(gen_url, json=body, timeout=120)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to reach Ollama: {e}")

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Ollama error: {resp.status_code} {resp.text}")

    try:
        data = resp.json()
        if isinstance(data, dict) and "text" in data:
            text = data["text"]
        elif isinstance(data, dict) and "generated" in data:
            text = " ".join(g.get("text", "") for g in data["generated"])
        else:
            text = str(data)
    except Exception:
        text = resp.text

    return {"answer": text, "retrieved": context_texts}