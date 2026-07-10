import threading
from typing import Dict, Tuple

from app.llm.base import BaseLLMProvider
from app.llm.registry import PROVIDERS


class ProviderManager:
    _cache: Dict[Tuple[str, str], BaseLLMProvider] = {}
    _lock = threading.Lock()

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
