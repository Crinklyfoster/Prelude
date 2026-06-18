# Deployment Guide

## Prerequisites

* Docker
* Docker Compose
* Ollama
* Git

## Clone Repository

```bash
git clone https://github.com/Crinklyfoster/enterprise-rag-assistant.git
cd enterprise-rag-assistant
```

## Configure Environment

Create:

* `.env`
* `backend/.env`
* `frontend/.env.local`

## Start Ollama

```bash
ollama serve
```

Pull required models:

```bash
ollama pull nomic-embed-text
ollama pull qwen3:8b
```

## Start Application

```bash
docker compose up -d --build
```

## Access Services

| Service        | URL                         |
| -------------- | --------------------------- |
| Application    | http://localhost            |
| Backend Health | http://localhost/api/health |
| Grafana        | http://localhost:3001       |
| Prometheus     | http://localhost:9090       |

## Stop Application

```bash
docker compose down
```
