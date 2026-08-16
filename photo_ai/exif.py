from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loguru import logger
from PIL import ExifTags, Image

try:
    from pillow_heif import register_heif_opener

    register_heif_opener()
except Exception:
    pass

from photo_ai.models import ImageMetadata


EXIF_TAGS = {value: key for key, value in ExifTags.TAGS.items()}
GPS_TAGS = ExifTags.GPSTAGS


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(str(value), fmt)
        except ValueError:
            continue
    return None


def _ratio_to_float(value: Any) -> float:
    if hasattr(value, "numerator") and hasattr(value, "denominator"):
        return float(value.numerator) / float(value.denominator)
    if isinstance(value, tuple) and len(value) == 2:
        return float(value[0]) / float(value[1])
    return float(value)


def _gps_coordinate(values: Any, ref: str | None) -> float | None:
    if not values or len(values) != 3:
        return None
    degrees, minutes, seconds = [_ratio_to_float(item) for item in values]
    coordinate = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if ref in {"S", "W"}:
        coordinate *= -1
    return coordinate


def _jsonable(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    try:
        json.dumps(value)
        return value
    except TypeError:
        return str(value)


def extract_image_metadata(path: Path, file_hash: str) -> ImageMetadata:
    stat = path.stat()
    created_at = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc)
    modified_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)

    width = None
    height = None
    exif_data: dict[str, Any] = {}
    camera_make = None
    camera_model = None
    orientation = None
    taken_at = None
    latitude = None
    longitude = None

    try:
        with Image.open(path) as image:
            width, height = image.size
            raw_exif = image.getexif()
            exif_data = {
                ExifTags.TAGS.get(tag_id, str(tag_id)): _jsonable(value)
                for tag_id, value in raw_exif.items()
            }

            camera_make = exif_data.get("Make")
            camera_model = exif_data.get("Model")
            orientation = exif_data.get("Orientation")
            taken_at = _parse_datetime(
                exif_data.get("DateTimeOriginal") or exif_data.get("DateTime")
            )

            gps_info = raw_exif.get_ifd(EXIF_TAGS["GPSInfo"]) if "GPSInfo" in EXIF_TAGS else {}
            gps = {GPS_TAGS.get(key, key): value for key, value in gps_info.items()}
            latitude = _gps_coordinate(gps.get("GPSLatitude"), gps.get("GPSLatitudeRef"))
            longitude = _gps_coordinate(gps.get("GPSLongitude"), gps.get("GPSLongitudeRef"))
    except Exception as exc:
        logger.warning("EXIF extraction failed for {}: {}", path, exc)

    return ImageMetadata(
        path=path,
        filename=path.name,
        file_hash=file_hash,
        file_size=stat.st_size,
        width=width,
        height=height,
        created_at=created_at,
        modified_at=modified_at,
        taken_at=taken_at,
        camera_make=camera_make,
        camera_model=camera_model,
        orientation=orientation,
        latitude=latitude,
        longitude=longitude,
        exif_json=exif_data,
    )
