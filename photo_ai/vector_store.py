from __future__ import annotations

from pathlib import Path
from typing import Any

from loguru import logger

from config import CHROMA_DIR

COLLECTION_NAME = "photo_text_embeddings"


class VectorStoreUnavailable(RuntimeError):
    pass


def _client():
    try:
        import chromadb
    except Exception as exc:
        raise VectorStoreUnavailable("ChromaDB is not installed. Run `pip install -r requirements.txt`.") from exc

    Path(CHROMA_DIR).mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def get_collection():
    client = _client()
    return client.get_or_create_collection(name=COLLECTION_NAME)


def save_embedding(
    photo_id: int,
    vector: list[float],
    document: str,
    metadata: dict[str, Any],
) -> str:
    collection = get_collection()
    embedding_id = f"photo:{photo_id}:text"
    collection.upsert(
        ids=[embedding_id],
        embeddings=[vector],
        documents=[document],
        metadatas=[{**metadata, "photo_id": photo_id}],
    )
    logger.info("embedding generated: {}", embedding_id)
    return embedding_id


def query_embeddings(vector: list[float], limit: int = 24) -> list[dict[str, Any]]:
    collection = get_collection()
    result = collection.query(query_embeddings=[vector], n_results=limit)
    ids = result.get("ids", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    documents = result.get("documents", [[]])[0]
    distances = result.get("distances", [[]])[0]
    matches: list[dict[str, Any]] = []
    for index, embedding_id in enumerate(ids):
        metadata = metadatas[index] if index < len(metadatas) else {}
        matches.append(
            {
                "embedding_id": embedding_id,
                "photo_id": int(metadata.get("photo_id")),
                "path": metadata.get("path"),
                "document": documents[index] if index < len(documents) else "",
                "distance": distances[index] if index < len(distances) else None,
            }
        )
    return matches
