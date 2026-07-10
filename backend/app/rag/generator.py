import time
from app.llm.provider_manager import ProviderManager
from app.services.settings_service import SettingsService
from app.llm.errors import RetryableProviderError


class Generator:

    def generate(self, *args, **kwargs):
        priority = ProviderManager.get_provider_priority()
        last_error = None
        requested_provider = priority[0]
        
        for provider_name in priority:
            start = time.perf_counter()
            try:
                model_name = ProviderManager.get_model_for_provider(provider_name)
                provider = ProviderManager.get(provider_name, model_name)
                
                result = provider.generate(*args, **kwargs)
                ProviderManager.track_metric(provider_name, (time.perf_counter() - start) * 1000, True)
                
                fallback = provider_name != requested_provider
                if fallback:
                    ProviderManager.log_failover(requested_provider, provider_name, last_error)
                
                meta = {
                    "requested_provider": requested_provider,
                    "actual_provider": provider_name,
                    "fallback": fallback,
                    "reason": last_error if fallback else None
                }
                
                return result, meta
                
            except RetryableProviderError as e:
                ProviderManager.track_metric(provider_name, (time.perf_counter() - start) * 1000, False)
                last_error = str(e)
                continue
            except Exception:
                ProviderManager.track_metric(provider_name, (time.perf_counter() - start) * 1000, False)
                raise
                
        raise RuntimeError(f"No provider available. Last error: {last_error}")

    def stream_generate(self, *args, **kwargs):
        priority = ProviderManager.get_provider_priority()
        last_error = None
        requested_provider = priority[0]
        
        for provider_name in priority:
            start = time.perf_counter()
            token_yielded = False
            try:
                model_name = ProviderManager.get_model_for_provider(provider_name)
                provider = ProviderManager.get(provider_name, model_name)
                
                generator = provider.stream_generate(*args, **kwargs)
                
                fallback = provider_name != requested_provider
                if fallback:
                    ProviderManager.log_failover(requested_provider, provider_name, last_error)
                
                meta = {
                    "type": "provider_meta",
                    "requested_provider": requested_provider,
                    "actual_provider": provider_name,
                    "fallback": fallback,
                    "reason": last_error if fallback else None
                }
                yield meta
                
                for chunk in generator:
                    if not token_yielded:
                        token_yielded = True
                    yield chunk
                    
                ProviderManager.track_metric(provider_name, (time.perf_counter() - start) * 1000, True)
                return
                
            except RetryableProviderError as e:
                ProviderManager.track_metric(provider_name, (time.perf_counter() - start) * 1000, False)
                last_error = str(e)
                if token_yielded:
                    raise
                continue
            except Exception:
                ProviderManager.track_metric(provider_name, (time.perf_counter() - start) * 1000, False)
                raise
                
        raise RuntimeError(f"No provider available. Last error: {last_error}")
