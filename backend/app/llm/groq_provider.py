import time
from typing import Any

import openai
from openai import OpenAI

from app.core.config import settings
from app.core.logger import get_logger
from app.llm.base import BaseLLMProvider
from app.llm.errors import FatalProviderError, RetryableProviderError

logger = get_logger(__name__)


class GroqProvider(BaseLLMProvider):

    def __init__(self, model: str):
        self.model = model
        self.client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )

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

        start = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
        except (
            openai.APIConnectionError,
            openai.RateLimitError,
            openai.APITimeoutError,
            openai.InternalServerError,
        ) as e:
            raise RetryableProviderError(str(e))
        except (openai.AuthenticationError, openai.BadRequestError) as e:
            raise FatalProviderError(str(e))
        except Exception as e:
            raise FatalProviderError(str(e))

        logger.info(
            "Provider=Groq Model=%s GenerationLatency=%.3fs",
            self.model,
            time.time() - start,
        )

        return response.choices[0].message.content or ""
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

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                stream=True,
            )
            for chunk in response:
                if (
                    chunk.choices
                    and chunk.choices[0].delta.content
                ):
                    yield chunk.choices[0].delta.content
        except (
            openai.APIConnectionError,
            openai.RateLimitError,
            openai.APITimeoutError,
            openai.InternalServerError,
        ) as e:
            raise RetryableProviderError(str(e))
        except (openai.AuthenticationError, openai.BadRequestError) as e:
            raise FatalProviderError(str(e))
        except Exception as e:
            raise FatalProviderError(str(e))

    def health(self):
        try:
            self.client.models.list()
            return "healthy"
        except Exception as e:
            logger.error(
                "Groq health check failed: %s",
                e,
            )
            return "unhealthy"
