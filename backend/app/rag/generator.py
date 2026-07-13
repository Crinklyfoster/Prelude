from app.llm.provider_manager import ProviderManager


class Generator:
    def generate(self, prompt: str, provider_override: str | None = None):
        return ProviderManager.generate(prompt=prompt, provider=provider_override)

    def stream_generate(self, prompt: str, provider_override: str | None = None):
        yield from ProviderManager.stream_generate(prompt=prompt, provider=provider_override)

# --- DORMANT CODE PRESERVED BELOW ---
# import time
#
# from app.llm.errors import RetryableProviderError
# from app.llm.provider_manager import ProviderManager
#
#
# class _ProviderRetryableError(Exception):
#     def __init__(self, original_error):
#         self.original_error = original_error
#
#
# class Generator:
#
#     def _build_meta(self, provider_name, requested_provider, last_error, is_stream=False):
#         fallback = provider_name != requested_provider
#         if fallback:
#             ProviderManager.log_failover(
#                 requested_provider, provider_name, last_error or "Unknown error"
#             )
#         
#         meta = {
#             "requested_provider": requested_provider,
#             "actual_provider": provider_name,
#             "fallback": fallback,
#             "reason": last_error if fallback else None
#         }
#         if is_stream:
#             meta["type"] = "provider_meta"
#         return meta
#
#     def _record_metrics(self, provider_name, start_time, success):
#         latency_ms = (time.perf_counter() - start_time) * 1000
#         ProviderManager.track_metric(provider_name, latency_ms, success)
#
#     def _generate_with_provider(
#         self, provider_name, requested_provider, last_error, start_time, *args, **kwargs
#     ):
#         try:
#             model_name = ProviderManager.get_model_for_provider(provider_name)
#             provider = ProviderManager.get(provider_name, model_name)
#             
#             result = provider.generate(*args, **kwargs)
#             self._record_metrics(provider_name, start_time, True)
#             
#             meta = self._build_meta(provider_name, requested_provider, last_error)
#             return result, meta
#             
#         except RetryableProviderError as e:
#             self._record_metrics(provider_name, start_time, False)
#             raise _ProviderRetryableError(e)
#         except Exception:
#             self._record_metrics(provider_name, start_time, False)
#             raise
#
#     def generate(self, *args, provider_override=None, **kwargs):
#         priority = ProviderManager.get_provider_priority(override=provider_override)
#         last_error = None
#         requested_provider = priority[0]
#         
#         for provider_name in priority:
#             start_time = time.perf_counter()
#             try:
#                 return self._generate_with_provider(
#                     provider_name, requested_provider, last_error, start_time, *args, **kwargs
#                 )
#             except _ProviderRetryableError as e:
#                 last_error = str(e.original_error)
#                 
#         raise RuntimeError(f"No provider available. Last error: {last_error}")
#
#     def _stream_with_provider(
#         self, provider_name, requested_provider, last_error, start_time, *args, **kwargs
#     ):
#         token_yielded = False
#         try:
#             model_name = ProviderManager.get_model_for_provider(provider_name)
#             provider = ProviderManager.get(provider_name, model_name)
#             
#             generator = provider.stream_generate(*args, **kwargs)
#             
#             yield self._build_meta(provider_name, requested_provider, last_error, is_stream=True)
#             
#             for chunk in generator:
#                 token_yielded = True
#                 yield chunk
#                 
#             self._record_metrics(provider_name, start_time, True)
#             
#         except RetryableProviderError as e:
#             self._record_metrics(provider_name, start_time, False)
#             if token_yielded:
#                 raise
#             raise _ProviderRetryableError(e)
#         except Exception:
#             self._record_metrics(provider_name, start_time, False)
#             raise
#
#     def stream_generate(self, *args, provider_override=None, **kwargs):
#         priority = ProviderManager.get_provider_priority(override=provider_override)
#         last_error = None
#         requested_provider = priority[0]
#         
#         for provider_name in priority:
#             start_time = time.perf_counter()
#             try:
#                 yield from self._stream_with_provider(
#                     provider_name, requested_provider, last_error, start_time, *args, **kwargs
#                 )
#                 return
#             except _ProviderRetryableError as e:
#                 last_error = str(e.original_error)
#                 
#         raise RuntimeError(f"No provider available. Last error: {last_error}")
#
#        will be Implemeted later !!! once there is GPU Avaliable