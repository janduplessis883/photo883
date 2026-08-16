import os
from pathlib import Path

APP_NAME = "Photo883"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SQLITE_PATH = DATA_DIR / "photos.db"
CHROMA_DIR = DATA_DIR / "chroma"
LOG_DIR = DATA_DIR / "logs"
LOG_FILE = LOG_DIR / "photo883.log"

OPENAI_COMPAT_BASE_URL = os.getenv("OPENAI_COMPAT_BASE_URL", "http://127.0.0.1:8000/v1")
OPENAI_COMPAT_API_KEY = os.getenv("OPENAI_COMPAT_API_KEY", "12345")
OPENAI_COMPAT_VISION_MODEL = os.getenv(
    "OPENAI_COMPAT_VISION_MODEL",
    "gemma-4-26b-a4b-it-4bit",
)
MLX_EMBEDDING_MODEL = os.getenv(
    "MLX_EMBEDDING_MODEL",
    "mlx-community/embeddinggemma-300m-4bit",
)

SUPPORTED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".heic",
    ".heif",
}
