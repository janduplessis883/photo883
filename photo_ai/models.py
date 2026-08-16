from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class ImageAnalysis(BaseModel):
    caption: str = ""
    scene: str | None = None
    objects: list[str] = Field(default_factory=list)
    activities: list[str] = Field(default_factory=list)
    concepts: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)

    def searchable_text(self) -> str:
        sections = [
            ("Caption", self.caption),
            ("Scene", self.scene or ""),
            ("Objects", ", ".join(self.objects)),
            ("Activities", ", ".join(self.activities)),
            ("Concepts", ", ".join(self.concepts)),
            ("Tags", ", ".join(self.tags)),
        ]
        return "\n".join(f"{label}: {value}" for label, value in sections if value)


class ImageMetadata(BaseModel):
    path: Path
    filename: str
    file_hash: str
    file_size: int | None = None
    width: int | None = None
    height: int | None = None
    created_at: datetime | None = None
    modified_at: datetime | None = None
    taken_at: datetime | None = None
    camera_make: str | None = None
    camera_model: str | None = None
    orientation: str | int | None = None
    latitude: float | None = None
    longitude: float | None = None
    exif_json: dict[str, Any] = Field(default_factory=dict)


class PhotoRecord(BaseModel):
    id: int
    path: str
    filename: str
    file_hash: str
    file_size: int | None = None
    width: int | None = None
    height: int | None = None
    created_at: str | None = None
    modified_at: str | None = None
    taken_at: str | None = None
    camera_make: str | None = None
    camera_model: str | None = None
    orientation: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    caption: str | None = None
    scene: str | None = None
    objects: list[str] = Field(default_factory=list)
    activities: list[str] = Field(default_factory=list)
    concepts: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    indexed_at: str | None = None
    text_embedding_id: str | None = None
    image_embedding_id: str | None = None
    processing_error: str | None = None
