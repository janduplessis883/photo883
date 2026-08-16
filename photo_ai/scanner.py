from __future__ import annotations

from pathlib import Path

from loguru import logger

from config import SUPPORTED_IMAGE_EXTENSIONS


def expand_root(root: str | Path) -> Path:
    return Path(root).expanduser().resolve()


def is_supported_image(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS


def scan_directory(root: str | Path) -> list[Path]:
    resolved_root = expand_root(root)
    if not resolved_root.exists():
        raise FileNotFoundError(f"Folder does not exist: {resolved_root}")
    if not resolved_root.is_dir():
        raise NotADirectoryError(f"Not a folder: {resolved_root}")

    photos: list[Path] = []
    for path in resolved_root.rglob("*"):
        if is_supported_image(path):
            logger.info("photo discovered: {}", path)
            photos.append(path)
    return sorted(photos)
