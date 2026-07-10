import logging

import ollama

from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelWarmupService:
    def __init__(self):
        self.client = ollama.Client(host=settings.OLLAMA_HOST)

    def warm_model(self, model: str):
        try:
            logger.info("Warming model: %s", model)

            self.client.generate(
                model=model,
                prompt="Hello",
                options={
                    "num_predict": 1,
                },
                keep_alive=settings.OLLAMA_KEEP_ALIVE,
            )

            logger.info("Model ready: %s", model)

        except Exception as e:
            logger.warning(
                "Failed to warm model %s : %s",
                model,
                e,
            )

    def warmup(self):

        if settings.LLM_PROVIDER == "ollama":
            self.warm_model(settings.OLLAMA_MODEL)

        self.warm_model(settings.EMBEDDING_MODEL)
