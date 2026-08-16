from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from loguru import logger

from config import DATA_DIR, SQLITE_PATH
from photo_ai.models import ImageAnalysis, ImageMetadata, PhotoRecord


def get_connection(db_path: Path = SQLITE_PATH) -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(db_path: Path = SQLITE_PATH) -> None:
    with get_connection(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                filename TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                file_size INTEGER,
                width INTEGER,
                height INTEGER,
                created_at TEXT,
                modified_at TEXT,
                taken_at TEXT,
                camera_make TEXT,
                camera_model TEXT,
                orientation TEXT,
                latitude REAL,
                longitude REAL,
                exif_json TEXT,
                caption TEXT,
                scene TEXT,
                objects_json TEXT,
                activities_json TEXT,
                concepts_json TEXT,
                tags_json TEXT,
                indexed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                text_embedding_id TEXT,
                image_embedding_id TEXT,
                processing_error TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_photos_hash
            ON photos(file_hash)
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_photos_scene
            ON photos(scene)
            """
        )


def _datetime(value: Any) -> str | None:
    return value.isoformat() if value else None


def _json(value: Any) -> str:
    return json.dumps(value or [], ensure_ascii=False)


def _row_to_record(row: sqlite3.Row) -> PhotoRecord:
    data = dict(row)
    return PhotoRecord(
        **{
            **data,
            "objects": json.loads(data.get("objects_json") or "[]"),
            "activities": json.loads(data.get("activities_json") or "[]"),
            "concepts": json.loads(data.get("concepts_json") or "[]"),
            "tags": json.loads(data.get("tags_json") or "[]"),
        }
    )


def find_by_path(path: Path) -> PhotoRecord | None:
    initialize_database()
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM photos WHERE path = ?",
            (str(path),),
        ).fetchone()
    return _row_to_record(row) if row else None


def find_by_hash(file_hash: str) -> list[PhotoRecord]:
    initialize_database()
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM photos WHERE file_hash = ? ORDER BY filename",
            (file_hash,),
        ).fetchall()
    return [_row_to_record(row) for row in rows]


def upsert_photo_metadata(metadata: ImageMetadata) -> int:
    initialize_database()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO photos (
                path, filename, file_hash, file_size, width, height,
                created_at, modified_at, taken_at, camera_make, camera_model,
                orientation, latitude, longitude, exif_json, processing_error
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
            ON CONFLICT(path) DO UPDATE SET
                filename = excluded.filename,
                file_hash = excluded.file_hash,
                file_size = excluded.file_size,
                width = excluded.width,
                height = excluded.height,
                created_at = excluded.created_at,
                modified_at = excluded.modified_at,
                taken_at = excluded.taken_at,
                camera_make = excluded.camera_make,
                camera_model = excluded.camera_model,
                orientation = excluded.orientation,
                latitude = excluded.latitude,
                longitude = excluded.longitude,
                exif_json = excluded.exif_json,
                processing_error = NULL
            """,
            (
                str(metadata.path),
                metadata.filename,
                metadata.file_hash,
                metadata.file_size,
                metadata.width,
                metadata.height,
                _datetime(metadata.created_at),
                _datetime(metadata.modified_at),
                _datetime(metadata.taken_at),
                metadata.camera_make,
                metadata.camera_model,
                str(metadata.orientation) if metadata.orientation is not None else None,
                metadata.latitude,
                metadata.longitude,
                json.dumps(metadata.exif_json, ensure_ascii=False),
            ),
        )
        row = connection.execute(
            "SELECT id FROM photos WHERE path = ?",
            (str(metadata.path),),
        ).fetchone()
        logger.info("database insert/update: {}", metadata.path)
        return int(row["id"] if row else cursor.lastrowid)


def save_analysis(photo_id: int, analysis: ImageAnalysis) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE photos
            SET caption = ?, scene = ?, objects_json = ?, activities_json = ?,
                concepts_json = ?, tags_json = ?, indexed_at = CURRENT_TIMESTAMP,
                processing_error = NULL
            WHERE id = ?
            """,
            (
                analysis.caption,
                analysis.scene,
                _json(analysis.objects),
                _json(analysis.activities),
                _json(analysis.concepts),
                _json(analysis.tags),
                photo_id,
            ),
        )


def update_text_embedding_id(photo_id: int, embedding_id: str) -> None:
    with get_connection() as connection:
        connection.execute(
            "UPDATE photos SET text_embedding_id = ? WHERE id = ?",
            (embedding_id, photo_id),
        )


def mark_processing_error(photo_id: int, error: str) -> None:
    with get_connection() as connection:
        connection.execute(
            "UPDATE photos SET processing_error = ? WHERE id = ?",
            (error[:1000], photo_id),
        )


def get_photo(photo_id: int) -> PhotoRecord | None:
    initialize_database()
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM photos WHERE id = ?", (photo_id,)).fetchone()
    return _row_to_record(row) if row else None


def list_photos(
    folder: str | None = None,
    tag: str | None = None,
    scene: str | None = None,
    object_name: str | None = None,
    limit: int = 200,
) -> list[PhotoRecord]:
    initialize_database()
    where: list[str] = []
    params: list[Any] = []
    if folder:
        where.append("path LIKE ?")
        params.append(f"{folder.rstrip('/')}/%")
    if tag:
        where.append("tags_json LIKE ?")
        params.append(f"%{tag}%")
    if scene:
        where.append("scene = ?")
        params.append(scene)
    if object_name:
        where.append("objects_json LIKE ?")
        params.append(f"%{object_name}%")
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    params.append(limit)

    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT * FROM photos
            {where_sql}
            ORDER BY indexed_at DESC, filename ASC
            LIMIT ?
            """,
            params,
        ).fetchall()
    return [_row_to_record(row) for row in rows]


def get_filter_values() -> dict[str, list[str]]:
    initialize_database()
    photos = list_photos(limit=5000)
    folders = sorted({str(Path(photo.path).parent) for photo in photos})
    tags = sorted({tag for photo in photos for tag in photo.tags})
    scenes = sorted({photo.scene for photo in photos if photo.scene})
    objects = sorted({item for photo in photos for item in photo.objects})
    return {"folders": folders, "tags": tags, "scenes": scenes, "objects": objects}


def stats() -> dict[str, int]:
    initialize_database()
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN caption IS NOT NULL AND caption != '' THEN 1 ELSE 0 END) AS analyzed,
                SUM(CASE WHEN text_embedding_id IS NOT NULL THEN 1 ELSE 0 END) AS embedded,
                SUM(CASE WHEN processing_error IS NOT NULL THEN 1 ELSE 0 END) AS failed
            FROM photos
            """
        ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}
