from __future__ import annotations

from photo_ai import database
from photo_ai.embeddings import embed_text
from photo_ai.models import PhotoRecord
from photo_ai.vector_store import query_embeddings


def semantic_search(query: str, limit: int = 24) -> list[tuple[PhotoRecord, float | None]]:
    if not query.strip():
        return []
    vector = embed_text(query, kind="query")
    matches = query_embeddings(vector, limit=limit)
    results: list[tuple[PhotoRecord, float | None]] = []
    for match in matches:
        photo = database.get_photo(match["photo_id"])
        if photo:
            results.append((photo, match.get("distance")))
    return results
