import time
from typing import Any

import httpx
import ollama

from app.core.config import settings
from app.core.logger import get_logger
from app.llm.base import BaseLLMProvider
from app.llm.errors import FatalProviderError, RetryableProviderError

logger = get_logger(__name__)


class OllamaProvider(BaseLLMProvider):
    def __init__(self, model: str):
        self.model = model
        self.client = ollama.Client(host=settings.OLLAMA_HOST)


    def _options(self):
        return {
            "temperature": settings.LLM_TEMPERATURE,
            "num_ctx": settings.LLM_CONTEXT_WINDOW,
            "num_predict": settings.LLM_MAX_TOKENS,
        }

    def generate(
        self,
        context: str,
        question: str,
        conversation_history: str = "",
    ) -> str:
        prompt = self._build_prompt(
            context=context,
            question=question,
            conversation_history=conversation_history,
        )

        start = time.perf_counter()

        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                options=self._options(),
                keep_alive=settings.OLLAMA_KEEP_ALIVE,
            )
        except ollama.ResponseError as e:
            if e.status_code in [429, 503, 504]:
                raise RetryableProviderError(str(e))
            raise FatalProviderError(str(e))
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            raise RetryableProviderError(str(e))
        except Exception as e:
            raise FatalProviderError(str(e))

        total_time = time.perf_counter() - start

        answer = response["message"]["content"]

        token_count = len(answer.split())
        tokens_per_second = (
            token_count / total_time if total_time > 0 else 0
        )

        logger.info(
            (
                "LLM | "
                "model=%s | "
                "prompt_chars=%d | "
                "answer_tokens=%d | "
                "latency=%.3fs | "
                "tok_per_sec=%.2f"
            ),
            self.model,
            len(prompt),
            token_count,
            total_time,
            tokens_per_second,
        )

        return answer

    def stream_generate(
        self,
        context: str,
        question: str,
        conversation_history: str = "",
    ) -> Any:
        prompt = self._build_prompt(
            context=context,
            question=question,
            conversation_history=conversation_history,
        )

        start = time.perf_counter()
        first_token_time = None
        token_count = 0

        try:
            stream = self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                stream=True,
                options=self._options(),
                keep_alive=settings.OLLAMA_KEEP_ALIVE,
            )

            for chunk in stream:
                token = chunk["message"].get("content", "")

                if not token:
                    continue

                token_count += 1

                if first_token_time is None:
                    first_token_time = time.perf_counter()

                    logger.info(
                        "LLM | model=%s | TTFT=%.3fs",
                        self.model,
                        first_token_time - start,
                    )

                yield token
        except ollama.ResponseError as e:
            if e.status_code in [429, 503, 504]:
                raise RetryableProviderError(str(e))
            raise FatalProviderError(str(e))
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            raise RetryableProviderError(str(e))
        except Exception as e:
            raise FatalProviderError(str(e))

        end = time.perf_counter()

        total_time = end - start

        generation_time = (
            end - first_token_time
            if first_token_time is not None
            else 0
        )

        tokens_per_second = (
            token_count / generation_time
            if generation_time > 0
            else 0
        )

        logger.info(
            (
                "LLM | "
                "model=%s | "
                "prompt_chars=%d | "
                "tokens=%d | "
                "TTFT=%.3fs | "
                "generation=%.3fs | "
                "total=%.3fs | "
                "tok_per_sec=%.2f"
            ),
            self.model,
            len(prompt),
            token_count,
            (first_token_time - start)
            if first_token_time
            else 0,
            generation_time,
            total_time,
            tokens_per_second,
        )
