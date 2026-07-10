# Enterprise RAG Benchmarks

## Models

- qwen3:4b
- qwen3:8b
- gemma3:4b

## Concurrent Users

- 1
- 5
- 10
- 20

## Metrics

- TTFT
- Tokens/sec
- Retrieval latency
- Generation latency
- Total latency
- CPU
- RAM
- Requests/sec
- Failure rate

## Procedure

1. Change CHAT_MODEL
2. Restart backend
3. Warm up model
4. Run Locust
5. Save results
