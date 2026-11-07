# DocuMind AI

> WhatsApp Document Assistant powered by Microsoft Azure and RAG.

DocuMind AI allows users to upload documents (PDF, DOCX, TXT) and ask questions directly via WhatsApp. It leverages Retrieval-Augmented Generation (RAG) with Azure Blob Storage, Azure AI Search, and Microsoft Foundry / Azure OpenAI models to deliver accurate, citation-backed answers.

---

## Architecture & Tech Stack

- **Interface:** WhatsApp Cloud API (Meta)
- **Backend:** Python 3.12+, FastAPI, Uvicorn, Pydantic v2
- **Document Processing:** pypdf, python-docx, tiktoken
- **Embeddings & LLM:** Microsoft Foundry / Azure OpenAI (`AsyncAzureOpenAI`)
- **Vector Search:** Azure AI Search (HNSW vector indexing)
- **Storage:** Azure Blob Storage
- **Identity & Secrets:** Azure Managed Identity, Azure Key Vault
- **Logging:** Structlog (structured JSON logging)

---

## Getting Started

### 1. Environment Setup

Copy `.env.example` to `.env` and fill in the required environment variables:

```bash
cp .env.example .env
```

### 2. Dependency Installation

Using `uv`:

```bash
uv sync --all-groups
```

Or using standard `pip`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 3. Running the Server

```bash
uv run uvicorn documind.main:app --host 0.0.0.0 --port 8000 --reload
```

Health check endpoint:
```bash
curl http://localhost:8000/health
```

### 4. Running Tests & Quality Checks

Run test suite:
```bash
uv run pytest
```

Run linter and formatter:
```bash
uv run ruff check .
uv run ruff format .
```

Run type checking:
```bash
uv run mypy src
```

---

## Docker Deployment

Build and run the multi-stage Docker container:

```bash
docker build -t documind-ai:latest .
docker run -p 8000:8000 --env-file .env documind-ai:latest
```
