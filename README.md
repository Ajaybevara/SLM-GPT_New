---
title: OCR & RAG Agent
emoji: 🛢️
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 8501
---
# Agent

## Run locally on Windows (Python 3.11)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8053
```

Open http://localhost:8053. Configure `.env` with the OpenAI-compatible vLLM
server used for chat and vision:

```env
VLLM_API_BASE=http://192.168.1.100:8700/v1
VLLM_API_KEY=empty
VLLM_MODEL=qwen3-vl-8b
EMBED_BASE_URL=http://192.168.1.100:8701/v1
EMBED_MODEL=qwen3-embedding-0.6b
EMBED_DIM=1024
EMBED_QUERY_INSTRUCT=Given a web search query, retrieve relevant passages that answer the query
LITELLM_LOCAL_MODEL_COST_MAP=True
DATABASE_URL=postgresql://drake@127.0.0.1:5543/drake_ai
```

Document search uses the configured Qwen embedding server over the LAN.

PostgreSQL tables and the local Guest account are created automatically on
startup. Start the dedicated Windows database before launching Streamlit:

```powershell
.\start-postgres.ps1
```

Stop it later with `.\stop-postgres.ps1`. The current app runs as a shared
Guest demo. Documents and chat history are stored in PostgreSQL; local document
vector indexes are stored under `database/`.


Restart the configured app with:

```powershell
powershell -ExecutionPolicy Bypass -File .\start-app.ps1
```

