from app.core.config import settings
from app.llm.registry import PROVIDERS


class Generator:

    def __init__(self):

        provider_cls = PROVIDERS.get(
            settings.LLM_PROVIDER.lower()
        )

        if provider_cls is None:
            raise ValueError(
                f"Unsupported provider: {settings.LLM_PROVIDER}"
            )

        self.provider = provider_cls()

    def generate(self, *args, **kwargs):
        return self.provider.generate(*args, **kwargs)

    def stream_generate(self, *args, **kwargs):
        return self.provider.stream_generate(*args, **kwargs)
