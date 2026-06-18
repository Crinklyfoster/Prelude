# Enterprise RAG Assistant – Phase 2 Architecture

## Overview

Phase 2 introduces:

* Dockerized deployment
* CI/CD validation
* Monitoring and observability
* Reverse proxy architecture

## Architecture

```text
Browser
   │
   ▼
Nginx
   ├── Frontend (Next.js)
   └── Backend (FastAPI)
            ├── PostgreSQL
            ├── ChromaDB
            └── Ollama

Prometheus
      │
      ▼
Backend Metrics

Grafana
      │
      ▼
Prometheus
```

## CI Pipeline

* Backend syntax validation
* Frontend build validation
* pip-audit
* Semgrep
* Gitleaks

## Persistence

* PostgreSQL volume
* ChromaDB volume
* Prometheus volume
* Grafana volume
