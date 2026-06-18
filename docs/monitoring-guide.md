# Monitoring Guide

## Prometheus

Prometheus scrapes metrics from:

```text
http://backend:8000/metrics
```

Access:

```text
http://localhost:9090
```

## Grafana

Access:

```text
http://localhost:3001
```

Default credentials:

```text
admin / admin
```

## Available Metrics

### documents_uploaded_total

Tracks uploaded documents.

### chat_requests_total

Tracks RAG chat requests.

## Health Endpoint

```text
http://localhost/api/health
```

Reports:

* PostgreSQL
* Ollama
* ChromaDB
* Overall application health
