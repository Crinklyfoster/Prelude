import time
from typing import Any

from google import genai
from google.genai import errors as genai_errors

from app.core.config import settings
from app.llm.base import BaseLLMProvider
from app.llm.errors import FatalProviderError, RetryableProviderError
from app.llm.rate_limiter import ProviderRateLimiter


class GeminiProvider(BaseLLMProvider):
    _limiter = ProviderRateLimiter("Gemini", settings.GEMINI_MAX_CONCURRENT, settings.GEMINI_RPM)

    def __init__(self, model: str):
        self.model = model
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    def _handle_request_error(
        self, e: Exception, attempt: int, chunks_yielded: int = 0
    ) -> None:
        """Handles API errors and retries, raising exceptions if retries are exhausted."""
        delays = [1, 2, 4]
        
        if isinstance(e, genai_errors.APIError):
            if chunks_yielded == 0 and attempt < 3 and e.code in [429, 500, 502, 503]:
                time.sleep(delays[attempt])
                return
            if e.code in [429, 503, 504]:
                raise RetryableProviderError(str(e))
            raise FatalProviderError(str(e))

        error_msg = str(e).lower()
        is_network_error = "timeout" in error_msg or "connection" in error_msg
        
        if chunks_yielded == 0 and attempt < 3 and is_network_error:
            time.sleep(delays[attempt])
            return
            
        if is_network_error:
            raise RetryableProviderError(str(e))
            
        raise FatalProviderError(str(e))

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
            for attempt in range(4):
                try:
                    response = self.client.models.generate_content(
                        model=self.model,
                        contents=prompt,
                    )
                    return response.text or ""
                except Exception as e:
                    self._handle_request_error(e, attempt)
            
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
                except Exception as e:
                    self._handle_request_error(e, attempt, chunks_yielded)
            
            raise FatalProviderError("Max retries exceeded")

    def health(self):
        try:
            self.client.models.list()
            return "healthy"
        except Exception as e:
            if "503" in str(e):
                return "degraded"
            return "unhealthy"
