from app.llm.factory import LLMFactory


class Generator:

    def __init__(self):
        self.provider = LLMFactory.create()

    def generate(self, *args, **kwargs):
        return self.provider.generate(*args, **kwargs)

    def stream_generate(self, *args, **kwargs):
        return self.provider.stream_generate(*args, **kwargs)
