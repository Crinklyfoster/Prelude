import threading
from typing import Dict, Tuple

from app.core.config import settings
from app.llm.base import BaseLLMProvider
from app.llm.registry import PROVIDERS
from app.services.settings_service import SettingsService


class ProviderManager:
    _cache: Dict[Tuple[str, str], BaseLLMProvider] = {}
    _lock = threading.Lock()
    
    _metrics = {
        name: {"requests": 0, "failures": 0, "total_latency_ms": 0.0}
        for name in PROVIDERS
    }
    _last_failover = None

    @classmethod
    def get(cls, provider_name: str, model_name: str) -> BaseLLMProvider:
        key = (provider_name.lower(), model_name)
        
        if key in cls._cache:
            return cls._cache[key]
            
        with cls._lock:
            # Check again after acquiring lock
            if key in cls._cache:
                return cls._cache[key]
                
            provider_cls = PROVIDERS.get(key[0])
            if not provider_cls:
                raise ValueError(f"Unsupported provider: {provider_name}")
                
            provider_instance = provider_cls(model=model_name)
            cls._cache[key] = provider_instance
            return provider_instance

    @classmethod
    def get_provider_priority(cls, override: str | None = None) -> list[str]:
        if override:
            return [override.lower()]
        active = SettingsService.get_provider().lower()
        priority = [active]
        for p in settings.LLM_PROVIDER_PRIORITY:
            if p.lower() != active and p.lower() not in priority:
                priority.append(p.lower())
        return priority

    @classmethod
    def get_model_for_provider(cls, provider_name: str) -> str:
        active = SettingsService.get_provider().lower()
        if provider_name.lower() == active:
            return SettingsService.get_model()
        defaults = {
            "ollama": settings.OLLAMA_MODEL,
            "gemini": settings.GEMINI_MODEL,
            "groq": settings.GROQ_MODEL,
        }
        return defaults.get(provider_name.lower(), "default")

    @classmethod
    def log_failover(cls, from_provider: str, to_provider: str, reason: str):
        from datetime import datetime
        with cls._lock:
            cls._last_failover = {
                "from": from_provider,
                "to": to_provider,
                "reason": reason,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M")
            }

    @classmethod
    def get_last_failover(cls) -> dict | None:
        with cls._lock:
            return cls._last_failover

    @classmethod
    def track_metric(cls, provider_name: str, latency_ms: float, success: bool):
        provider_name = provider_name.lower()
        if provider_name in cls._metrics:
            with cls._lock:
                cls._metrics[provider_name]["requests"] += 1
                if not success:
                    cls._metrics[provider_name]["failures"] += 1
                cls._metrics[provider_name]["total_latency_ms"] += latency_ms

    @classmethod
    def list_providers(cls) -> list[dict]:
        active_provider = SettingsService.get_provider().lower()
        
        is_configured = {
            "ollama": bool(settings.OLLAMA_HOST),
            "gemini": bool(settings.GEMINI_API_KEY),
            "groq": bool(settings.GROQ_API_KEY),
        }
        
        result = []
        for name in PROVIDERS:
            result.append({
                "provider": name,
                "configured": is_configured.get(name, False),
                "active": name == active_provider,
            })
        return result

    @classmethod
    def _get_provider_instance_for_health(cls, name: str, provider_cls, model_to_use: str):
        key = (name, model_to_use)
        if key in cls._cache:
            return cls._cache[key]
        try:
            return provider_cls(model=model_to_use)
        except Exception:
            return None

    @classmethod
    def _check_provider_health(cls, name: str, provider_cls, model_to_use: str) -> str:
        provider_instance = cls._get_provider_instance_for_health(name, provider_cls, model_to_use)
        if not provider_instance:
            return "unhealthy"
        try:
            return provider_instance.health()
        except Exception:
            return "unhealthy"

    @classmethod
    def health(cls) -> list[dict]:
        result = []
        default_models = {
            "ollama": "qwen3:8b",
            "gemini": "gemini-2.5-flash",
            "groq": "llama-3.3-70b-versatile"
        }
        active_model = SettingsService.get_model()
        active_provider = SettingsService.get_provider().lower()
        
        for name, provider_cls in PROVIDERS.items():
            model_to_use = (
                active_model
                if name == active_provider
                else default_models.get(name, "default")
            )
            result.append({
                "provider": name,
                "status": cls._check_provider_health(name, provider_cls, model_to_use),
            })
        return result

    @classmethod
    def get_metrics(cls) -> list[dict]:
        result = []
        for name, metrics in cls._metrics.items():
            reqs = metrics["requests"]
            failures = metrics["failures"]
            total_latency = metrics["total_latency_ms"]
            avg_latency = int(total_latency / reqs) if reqs > 0 else 0
            
            result.append({
                "provider": name,
                "requests": reqs,
                "failures": failures,
                "average_latency_ms": avg_latency
            })
        return result

    @classmethod
    def _build_meta(cls, provider_name, requested_provider, last_error, is_stream=False):
        fallback = provider_name != requested_provider
        if fallback:
            cls.log_failover(
                requested_provider, provider_name, last_error or "Unknown error"
            )
        
        meta = {
            "requested_provider": requested_provider,
            "actual_provider": provider_name,
            "fallback": fallback,
            "reason": last_error if fallback else None
        }
        if is_stream:
            meta["type"] = "provider_meta"
        return meta

    @classmethod
    def _generate_with_provider(
        cls, provider_name, requested_provider, last_error, start_time, prompt
    ):
        from app.llm.errors import RetryableProviderError
        import time
        try:
            model_name = cls.get_model_for_provider(provider_name)
            provider_instance = cls.get(provider_name, model_name)
            
            result = provider_instance.generate(prompt=prompt)
            cls.track_metric(provider_name, (time.perf_counter() - start_time) * 1000, True)
            
            meta = cls._build_meta(provider_name, requested_provider, last_error)
            return result, meta
            
        except RetryableProviderError as e:
            cls.track_metric(provider_name, (time.perf_counter() - start_time) * 1000, False)
            raise e
        except Exception:
            cls.track_metric(provider_name, (time.perf_counter() - start_time) * 1000, False)
            raise

    @classmethod
    def generate(cls, prompt: str, provider: str | None = None):
        from app.llm.errors import RetryableProviderError
        import time
        priority = cls.get_provider_priority(override=provider)
        last_error = None
        requested_provider = priority[0]
        
        for provider_name in priority:
            start_time = time.perf_counter()
            try:
                return cls._generate_with_provider(
                    provider_name, requested_provider, last_error, start_time, prompt
                )
            except RetryableProviderError as e:
                last_error = str(e)
                
        raise RuntimeError(f"No provider available. Last error: {last_error}")

    @classmethod
    def _stream_with_provider(
        cls, provider_name, requested_provider, last_error, start_time, prompt
    ):
        from app.llm.errors import RetryableProviderError
        import time
        token_yielded = False
        try:
            model_name = cls.get_model_for_provider(provider_name)
            provider_instance = cls.get(provider_name, model_name)
            
            generator = provider_instance.stream_generate(prompt=prompt)
            
            yield cls._build_meta(provider_name, requested_provider, last_error, is_stream=True)
            
            for chunk in generator:
                token_yielded = True
                yield chunk
                
            cls.track_metric(provider_name, (time.perf_counter() - start_time) * 1000, True)
            
        except RetryableProviderError as e:
            cls.track_metric(provider_name, (time.perf_counter() - start_time) * 1000, False)
            if token_yielded:
                raise
            raise e
        except Exception:
            cls.track_metric(provider_name, (time.perf_counter() - start_time) * 1000, False)
            raise

    @classmethod
    def stream_generate(cls, prompt: str, provider: str | None = None):
        from app.llm.errors import RetryableProviderError
        import time
        priority = cls.get_provider_priority(override=provider)
        last_error = None
        requested_provider = priority[0]
        
        for provider_name in priority:
            start_time = time.perf_counter()
            try:
                yield from cls._stream_with_provider(
                    provider_name, requested_provider, last_error, start_time, prompt
                )
                return
            except RetryableProviderError as e:
                last_error = str(e)
                
        raise RuntimeError(f"No provider available. Last error: {last_error}")
