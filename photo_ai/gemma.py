from __future__ import annotations

import base64
import json
from pathlib import Path

from loguru import logger
from openai import OpenAI

from config import (
    OPENAI_COMPAT_API_KEY,
    OPENAI_COMPAT_BASE_URL,
    OPENAI_COMPAT_VISION_MODEL,
)
from photo_ai.models import ImageAnalysis


ANALYSIS_PROMPT = """
Describe only what is visible in this photo.
Avoid inventing identities, exact locations, relationships, or events that are not visible.
Return valid JSON only with this schema:
{
  "caption": "concise but informative caption",
  "scene": "general scene",
  "objects": ["important visible objects"],
  "activities": ["visible activities"],
  "concepts": ["broad concepts where reasonable"],
  "tags": ["useful search tags"]
}
""".strip()


def _client() -> OpenAI:
    return OpenAI(
        base_url=OPENAI_COMPAT_BASE_URL,
        api_key=OPENAI_COMPAT_API_KEY,
    )


def _image_data_url(path: Path) -> str:
    suffix = path.suffix.lower().lstrip(".")
    mime = "jpeg" if suffix in {"jpg", "jpeg"} else suffix
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/{mime};base64,{encoded}"


def _extract_json(text: str) -> dict:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        stripped = stripped.removeprefix("json").strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"Model did not return JSON: {text[:300]}")
    return json.loads(stripped[start : end + 1])


def analyse_image(path: Path) -> ImageAnalysis:
    logger.info("Gemma analysis started: {}", path)
    response = _client().chat.completions.create(
        model=OPENAI_COMPAT_VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": ANALYSIS_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {"url": _image_data_url(path)},
                    },
                ],
            }
        ],
        temperature=0.1,
    )
    content = response.choices[0].message.content or ""
    analysis = ImageAnalysis.model_validate(_extract_json(content))
    logger.info("Gemma analysis completed: {}", path)
    return analysis
