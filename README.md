# Photo883

Local-first photo classification and semantic search with Streamlit, SQLite, ChromaDB, and an OpenAI-compatible local model server.

Photos stay in their original folders. SQLite stores paths, hashes, EXIF metadata, AI-generated captions/tags, and ChromaDB stores text embeddings for semantic search.

## Local model server

This app is configured for OMLX/OpenAI-compatible local serving:

- Base URL: `http://127.0.0.1:8000/v1`
- API key: `12345`
- Vision model: `gemma-4-26b-a4b-it-4bit`
- Embedding model: `mlx-community/embeddinggemma-300m-4bit` through `mlx-embeddings`

The defaults can be overridden with environment variables:

```bash
export OPENAI_COMPAT_BASE_URL="http://127.0.0.1:8000/v1"
export OPENAI_COMPAT_API_KEY="12345"
export OPENAI_COMPAT_VISION_MODEL="gemma-4-26b-a4b-it-4bit"
export MLX_EMBEDDING_MODEL="mlx-community/embeddinggemma-300m-4bit"
```

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run streamlit_app.py
```

Then open the Indexing page, point it at a local folder, scan, and index.

## Project layout

```text
streamlit_app.py       Streamlit router
app_pages/             Library, search, indexing, settings UI
photo_ai/              Scanner, EXIF, DB, vector store, model adapters, indexer
data/photos.db         SQLite catalogue, created at runtime
data/chroma/           Chroma vector database, created at runtime
```
