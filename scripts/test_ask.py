import os
import requests
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

QDRANT_URL = os.environ.get(""QDRANT_URL"", ""http://localhost:6333"")
OLLAMA_URL = os.environ.get(""OLLAMA_URL"", ""http://localhost:11434"")
COLLECTION = os.environ.get(""QDRANT_COLLECTION"", ""repo_docs"")
EMBED_MODEL = os.environ.get(""EMBED_MODEL"", ""sentence-transformers/all-MiniLM-L6-v2"")

def main():
    embedder = SentenceTransformer(EMBED_MODEL)
    q = ""What is Freya?""
    q_emb = embedder.encode([q]).tolist()[0]

    qc = QdrantClient(url=QDRANT_URL)
    hits = qc.search(collection_name=COLLECTION, query_vector=q_emb, limit=3)
    contexts = []
    for h in hits:
        payload = getattr(h, ""payload"", None) or (h.get(""payload"") if isinstance(h, dict) else {})
        contexts.append(payload.get(""text"",""""))
    prompt = ""Context:\n\n"" + ""\n\n"".join(contexts) + ""\n\nQuestion:\n"" + q

    print(""Prompt to Ollama:\n"", prompt[:1000], ""...\n"")
    resp = requests.post(f""{OLLAMA_URL.rstrip('/')}/api/generate"", json={""model"":""llama3.1:8b-instruct-q6_K"",""prompt"":prompt,""max_tokens"":256}, timeout=120)
    print(""Ollama status:"", resp.status_code)
    try:
        print(resp.json())
    except Exception:
        print(resp.text)

if __name__ == ""__main__"":
    main()
