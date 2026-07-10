import threading
from typing import Dict, Tuple

from app.llm.base import BaseLLMProvider
from app.llm.registry import PROVIDERS
from app.services.settings_service import SettingsService
from app.core.config import settings


class ProviderManager:
    _cache: Dict[Tuple[str, str], BaseLLMProvider] = {}
    _lock = threading.Lock()
    
    _metrics = {
        name: {"requests": 0, "failures": 0, "total_latency_ms": 0.0}
        for name in PROVIDERS
    }

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
            model_to_use = active_model if name == active_provider else default_models.get(name, "default")
            
            key = (name, model_to_use)
            if key in cls._cache:
                provider_instance = cls._cache[key]
            else:
                try:
                    provider_instance = provider_cls(model=model_to_use)
                except Exception:
                    provider_instance = None
            
            if provider_instance:
                try:
                    status = provider_instance.health()
                except Exception:
                    status = "unhealthy"
            else:
                status = "unhealthy"
                
            result.append({
                "provider": name,
                "status": status,
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
