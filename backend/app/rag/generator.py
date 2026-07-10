import time

from app.llm.errors import RetryableProviderError
from app.llm.provider_manager import ProviderManager


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
                latency_ms = (time.perf_counter() - start) * 1000
                ProviderManager.track_metric(provider_name, latency_ms, True)
                
                fallback = provider_name != requested_provider
                if fallback:
                    ProviderManager.log_failover(
                        requested_provider, provider_name, last_error or "Unknown error"
                    )
                
                meta = {
                    "requested_provider": requested_provider,
                    "actual_provider": provider_name,
                    "fallback": fallback,
                    "reason": last_error if fallback else None
                }
                
                return result, meta
                
            except RetryableProviderError as e:
                latency_ms = (time.perf_counter() - start) * 1000
                ProviderManager.track_metric(provider_name, latency_ms, False)
                last_error = str(e)
                continue
            except Exception:
                latency_ms = (time.perf_counter() - start) * 1000
                ProviderManager.track_metric(provider_name, latency_ms, False)
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
                    ProviderManager.log_failover(
                        requested_provider, provider_name, last_error or "Unknown error"
                    )
                
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
                    
                latency_ms = (time.perf_counter() - start) * 1000
                ProviderManager.track_metric(provider_name, latency_ms, True)
                return
                
            except RetryableProviderError as e:
                latency_ms = (time.perf_counter() - start) * 1000
                ProviderManager.track_metric(provider_name, latency_ms, False)
                last_error = str(e)
                if token_yielded:
                    raise
                continue
            except Exception:
                latency_ms = (time.perf_counter() - start) * 1000
                ProviderManager.track_metric(provider_name, latency_ms, False)
                raise
                
        raise RuntimeError(f"No provider available. Last error: {last_error}")
