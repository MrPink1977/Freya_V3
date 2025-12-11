```markdown
# Freya_V3 - Local modular assistant (Ollama + Qdrant + API)

Quick start:
1. Ensure Ollama is running on the host and reachable by containers:
   # e.g., bind to all interfaces if needed
   $env:OLLAMA_HOST="0.0.0.0:11434"
   ollama serve

2. Build and start the containerized stack (from repo root):
   docker compose up --build -d

3. Ingest your repo into qdrant (run on host):
   $env:QDRANT_URL="http://localhost:6333"
   python scripts/ingest_repo.py --path C:\AI_Projects\Freya_V3

4. Call the API:
   curl -X POST "http://localhost:8000/ask" -H "Content-Type: application/json" \
     -d '{"prompt":"Summarize the repository","top_k":3}'

Notes:
- If you run Ollama on a different port, update OLLAMA_URL in docker-compose.yml.
- On Windows/macOS Docker Desktop, containers resolve the host via host.docker.internal.
- Do not commit models or secrets into Git.
```