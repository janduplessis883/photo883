from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from photo_ai import database
from photo_ai.embeddings import embed_text
from photo_ai.exif import extract_image_metadata
from photo_ai.gemma import analyse_image
from photo_ai.hashing import sha256_file
from photo_ai.scanner import scan_directory
from photo_ai.vector_store import save_embedding


@dataclass
class IndexEvent:
    path: Path | None
    status: str
    current: int
    total: int
    message: str


ProgressCallback = Callable[[IndexEvent], None]


def should_skip(path: Path, file_hash: str) -> bool:
    existing = database.find_by_path(path)
    return bool(
        existing
        and existing.file_hash == file_hash
        and existing.caption
        and existing.text_embedding_id
        and not existing.processing_error
    )


def index_photo(path: Path, force: bool = False) -> int:
    file_hash = sha256_file(path)
    logger.info("hash calculated: {}", path)

    duplicates = [photo for photo in database.find_by_hash(file_hash) if photo.path != str(path)]
    if duplicates:
        logger.info("duplicate detected: {} duplicates {}", path, [item.path for item in duplicates])

    if not force and should_skip(path, file_hash):
        logger.info("photo skipped: {}", path)
        existing = database.find_by_path(path)
        return int(existing.id) if existing else 0

    metadata = extract_image_metadata(path, file_hash)
    photo_id = database.upsert_photo_metadata(metadata)

    try:
        analysis = analyse_image(path)
        database.save_analysis(photo_id, analysis)
        searchable_text = analysis.searchable_text()
        vector = embed_text(searchable_text, kind="document")
        embedding_id = save_embedding(
            photo_id=photo_id,
            vector=vector,
            document=searchable_text,
            metadata={"path": str(path), "filename": path.name},
        )
        database.update_text_embedding_id(photo_id, embedding_id)
        return photo_id
    except Exception as exc:
        logger.exception("processing failure: {}", path)
        database.mark_processing_error(photo_id, str(exc))
        raise


def index_directory(
    root: str | Path,
    force: bool = False,
    progress: ProgressCallback | None = None,
) -> Iterator[IndexEvent]:
    database.initialize_database()
    paths = scan_directory(root)
    total = len(paths)
    yield IndexEvent(None, "discovered", 0, total, f"Discovered {total} supported images")

    for current, path in enumerate(paths, start=1):
        event = IndexEvent(path, "processing", current, total, f"Processing {path.name}")
        if progress:
            progress(event)
        yield event
        try:
            file_hash = sha256_file(path)
            if not force and should_skip(path, file_hash):
                skipped = IndexEvent(path, "skipped", current, total, f"Skipped unchanged {path.name}")
                if progress:
                    progress(skipped)
                yield skipped
                continue

            metadata = extract_image_metadata(path, file_hash)
            photo_id = database.upsert_photo_metadata(metadata)
            analysis = analyse_image(path)
            database.save_analysis(photo_id, analysis)
            searchable_text = analysis.searchable_text()
            vector = embed_text(searchable_text, kind="document")
            embedding_id = save_embedding(
                photo_id=photo_id,
                vector=vector,
                document=searchable_text,
                metadata={"path": str(path), "filename": path.name},
            )
            database.update_text_embedding_id(photo_id, embedding_id)
            done = IndexEvent(path, "indexed", current, total, f"Indexed {path.name}")
            if progress:
                progress(done)
            yield done
        except Exception as exc:
            failed = IndexEvent(path, "failed", current, total, f"Failed {path.name}: {exc}")
            if progress:
                progress(failed)
            yield failed


def scan_only(root: str | Path) -> list[Path]:
    database.initialize_database()
    return scan_directory(root)
