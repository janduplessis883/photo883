"""Local-first photo indexing and semantic search."""

from photo_ai.logging_config import setup_logging

setup_logging()

__all__ = [
    "database",
    "embeddings",
    "exif",
    "gemma",
    "hashing",
    "indexer",
    "scanner",
    "search",
    "setup_logging",
    "vector_store",
]
