# Prelude

An enterprise-grade Retrieval-Augmented Generation (RAG) assistant built with FastAPI, PostgreSQL, ChromaDB, Ollama, and Next.js.

## Project Goal

Build a production-style RAG system capable of:

* Uploading and managing enterprise documents
* Extracting and processing document content
* Generating embeddings
* Storing vectors in a vector database
* Retrieving relevant context
* Generating answers using local LLMs via Ollama
* Providing a chat-based interface with source attribution

---

## Tech Stack

### Backend

* FastAPI
* SQLAlchemy
* PostgreSQL
* Pydantic

### AI / RAG

* Ollama
* ChromaDB
* Embedding Models (planned)

### Frontend

* Next.js
* TypeScript

### DevOps

* GitHub
* Docker (planned)

---

## Current Progress

### Sprint 1 — Backend Foundation ✅

Completed:

* FastAPI project setup
* Environment configuration
* PostgreSQL integration
* SQLAlchemy models
* Database session management
* Document CRUD APIs
* PDF upload endpoint
* Service-layer architecture

Implemented Endpoints:

* `POST /documents`
* `GET /documents`
* `GET /documents/{document_id}`
* `POST /documents/upload`
* `GET /health`

---

## Project Structure

```text
enterprise-rag-assistant/
│
├── frontend/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── database/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── rag/
│   │
│   ├── uploads/
│   └── scripts/
│
├── docs/
├── architecture/
└── README.md
```

---

## Roadmap

### Sprint 2

* PDF text extraction
* Document processing pipeline

### Sprint 3

* Text chunking
* Chunk storage

### Sprint 4

* Embedding generation
* ChromaDB integration

### Sprint 5

* Retrieval pipeline
* Context assembly

### Sprint 6

* Ollama integration
* RAG answer generation

### Sprint 7

* Chat API
* Conversation history

### Sprint 8

* Next.js frontend

---

## Running the Backend

```bash
cd backend

source venv/bin/activate

uvicorn app.main:app --reload
```

API Documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Status

Current Version:

**v0.1-backend-foundation**
