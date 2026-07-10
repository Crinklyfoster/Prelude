from app.llm.provider_manager import ProviderManager
from app.services.settings_service import SettingsService


class Generator:

    def _provider(self):
        provider_name = SettingsService.get_provider()
        model_name = SettingsService.get_model()
        return ProviderManager.get(provider_name, model_name)

    def generate(self, *args, **kwargs):
        return self._provider().generate(*args, **kwargs)

    def stream_generate(self, *args, **kwargs):
        return self._provider().stream_generate(*args, **kwargs)
