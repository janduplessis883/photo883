from __future__ import annotations

from functools import lru_cache

from loguru import logger

from config import MLX_EMBEDDING_MODEL


class EmbeddingsUnavailable(RuntimeError):
    pass


TASK_PREFIXES = {
    "query": "task: search result | query: ",
    "document": "title: none | text: ",
}


@lru_cache(maxsize=1)
def _model_and_tokenizer():
    try:
        from mlx_embeddings import load
    except Exception as exc:
        raise EmbeddingsUnavailable(
            "MLX embeddings are not installed. Run `pip install -r requirements.txt`."
        ) from exc

    logger.info("loading MLX embedding model: {}", MLX_EMBEDDING_MODEL)
    return load(MLX_EMBEDDING_MODEL)


def embed_text(text: str, kind: str = "document") -> list[float]:
    prefix = TASK_PREFIXES.get(kind, TASK_PREFIXES["document"])
    prefixed_text = f"{prefix}{text}"
    try:
        model, tokenizer = _model_and_tokenizer()
        encoded_input = tokenizer(
            [prefixed_text],
            padding=True,
            truncation=True,
            return_tensors="mlx",
        )
        output = model(encoded_input["input_ids"], encoded_input["attention_mask"])
        vector = output.text_embeds[0].tolist()
    except Exception as exc:
        raise EmbeddingsUnavailable(
            "Could not generate an MLX embedding. Confirm `mlx-embeddings` is installed "
            f"and `{MLX_EMBEDDING_MODEL}` is available locally or downloadable."
        ) from exc

    logger.info("embedding generated: {}", kind)
    return vector
