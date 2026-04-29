# Cytobot — RAG Chatbot for Cytovision

A retrieval-augmented generation (RAG) chatbot built for Cytovision's website. Combines a two-stage FAQ + LLM pipeline with a SocketIO backend, React frontend, and an admin analytics dashboard.

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.13+ | Required by `pyproject.toml` |
| Poetry | Latest | Python dependency manager |
| Node.js | 18+ | For the React frontend |
| npm | 9+ | Bundled with Node.js |
| OpenAI API Key | — | Required for LLM pipeline |


---

## Setup

### 1. Clone the Repository

```bash
git clone <YOUR_GIT_URL>
cd imtiaznn-r-chatbot-03
```

---

### 2. Backend Setup

#### 2a. Install Python dependencies

```bash
# From the project root
poetry install
```

#### 2b. Set your OpenAI API key

Create a `.env` file in `server/` or export directly:

```bash
export OPENAI_API_KEY=sk-...
```

> The key is read by `pipeline.py` via `langchain-openai`. Without it, the LLM stage will fail.

#### 2c. Populate the vector database

The Chroma vector collections must be built before the server can answer queries.

```bash
cd server

# Vectorize FAQs (reads store/faq.yml)
poetry run python -m scripts.vectorize_db --vectorize-faq

# Vectorize knowledge base PDFs (reads store/docs/*.pdf)
poetry run python -m scripts.vectorize_db --vectorize-kb

# Or both at once
poetry run python -m scripts.vectorize_db --vectorize-faq --vectorize-kb
```

> Place your knowledge base PDF files in `server/store/docs/` before running the KB step.

---

### 3. Frontend Setup

#### 3a. Install Node dependencies

```bash
cd client
npm install
```

#### 3b. Build the frontend

The Vite build outputs directly to `server/dist/`, which is where the FastAPI server serves static files from.

```bash
# Still inside client/
npm run build
```

> For development with hot-reload, use `npm run dev` instead (runs on port 8080, proxies API calls).

---

### 4. Run the Server

```bash
# From the project root
cd server
poetry run python main.py
```

The server starts on `http://localhost:5005`.

| URL | Description |
|-----|-------------|
| `http://localhost:5005/` | Chatbot frontend |
| `http://localhost:5005/dashboard` | Admin analytics dashboard |
| `http://localhost:5005/api/dashboard` | Dashboard REST API |

---

## Full Setup (Quick Reference)

```bash
# 1. Install dependencies
poetry install
cd client && npm install && cd ..

# 2. Build frontend
cd client && npm run build && cd ..

# 3. Populate vector store
cd server
poetry run python -m scripts.vectorize_db --vectorize-faq --vectorize-kb

# 4. Start server
poetry run python main.py
```

---

## Notes

- The SQLite database (`store/app.db`) is created automatically on first server startup.
- Vector collections are persisted to `store/faq_collection/` and `store/kb_collection/`. Re-run `vectorize_db.py` to rebuild them after content changes.
- The `store/app.db-shm` file is a SQLite WAL shared-memory file — do not delete it while the server is running.
- `FAQ_DISABLED` and `LLM_DISABLED` flags in `app/pipeline.py` can be toggled to isolate pipeline stages during development.
