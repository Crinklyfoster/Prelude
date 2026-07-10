import threading
import time
from typing import Any

from google import genai
from google.genai import errors as genai_errors

from app.core.config import settings
from app.llm.base import BaseLLMProvider
from app.llm.rate_limiter import ProviderRateLimiter
from app.llm.errors import FatalProviderError, RetryableProviderError


class GeminiProvider(BaseLLMProvider):
    _limiter = ProviderRateLimiter("Gemini", settings.GEMINI_MAX_CONCURRENT, settings.GEMINI_RPM)

    def __init__(self, model: str):
        self.model = model
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    def generate(
        self,
        context: str,
        question: str,
        conversation_history: str = "",
    ) -> str:
        prompt = self._build_prompt(
            context,
            question,
            conversation_history,
        )

        with self._limiter:
            delays = [1, 2, 4]
            for attempt in range(4):
                try:
                    response = self.client.models.generate_content(
                        model=self.model,
                        contents=prompt,
                    )
                    return response.text or ""
                except genai_errors.APIError as e:
                    if e.code in [429, 500, 502, 503]:
                        if attempt < 3:
                            time.sleep(delays[attempt])
                            continue
                    if e.code in [429, 503, 504]:
                        raise RetryableProviderError(str(e))
                    raise FatalProviderError(str(e))
                except Exception as e:
                    if "timeout" in str(e).lower() or "connection" in str(e).lower():
                        if attempt < 3:
                            time.sleep(delays[attempt])
                            continue
                        raise RetryableProviderError(str(e))
                    raise FatalProviderError(str(e))
            
            raise FatalProviderError("Max retries exceeded")

    def stream_generate(
        self,
        context: str,
        question: str,
        conversation_history: str = "",
    ) -> Any:
        prompt = self._build_prompt(
            context,
            question,
            conversation_history,
        )

        with self._limiter:
            delays = [1, 2, 4]
            chunks_yielded = 0
            for attempt in range(4):
                try:
                    response = self.client.models.generate_content_stream(
                        model=self.model,
                        contents=prompt,
                    )
                    for chunk in response:
                        if chunk.text:
                            yield chunk.text
                            chunks_yielded += 1
                    return
                except genai_errors.APIError as e:
                    if chunks_yielded == 0 and e.code in [429, 500, 502, 503]:
                        if attempt < 3:
                            time.sleep(delays[attempt])
                            continue
                    if e.code in [429, 503, 504]:
                        raise RetryableProviderError(str(e))
                    raise FatalProviderError(str(e))
                except Exception as e:
                    if chunks_yielded == 0 and ("timeout" in str(e).lower() or "connection" in str(e).lower()):
                        if attempt < 3:
                            time.sleep(delays[attempt])
                            continue
                    if "timeout" in str(e).lower() or "connection" in str(e).lower():
                        raise RetryableProviderError(str(e))
                    raise FatalProviderError(str(e))
            
            raise FatalProviderError("Max retries exceeded")

    def health(self):
        try:
            self.client.models.list()
            return "healthy"
        except Exception as e:
            if "503" in str(e):
                return "degraded"
            return "unhealthy"
