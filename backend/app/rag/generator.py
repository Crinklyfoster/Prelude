import time
from app.llm.provider_manager import ProviderManager
from app.services.settings_service import SettingsService


class Generator:

    def _provider(self):
        provider_name = SettingsService.get_provider()
        model_name = SettingsService.get_model()
        return ProviderManager.get(provider_name, model_name)

    def generate(self, *args, **kwargs):
        provider_name = SettingsService.get_provider()
        start = time.perf_counter()
        try:
            result = self._provider().generate(*args, **kwargs)
            ProviderManager.track_metric(provider_name, (time.perf_counter() - start) * 1000, True)
            return result
        except Exception:
            ProviderManager.track_metric(provider_name, (time.perf_counter() - start) * 1000, False)
            raise

    def stream_generate(self, *args, **kwargs):
        provider_name = SettingsService.get_provider()
        start = time.perf_counter()
        try:
            generator = self._provider().stream_generate(*args, **kwargs)
            for chunk in generator:
                yield chunk
            ProviderManager.track_metric(provider_name, (time.perf_counter() - start) * 1000, True)
        except Exception:
            ProviderManager.track_metric(provider_name, (time.perf_counter() - start) * 1000, False)
            raise
