# multi-user-vision-backend

Backend designed to manage multiple users interacting with independent camera streams, enabling real-time frame ingestion, access control, and event tracking.

---

## Overview

This project provides a backend system for a multi-user vision application where:

- Users can create and manage cameras
- Cameras push frames to the backend via API keys
- Authorized users can access frames in real time
- Events (e.g. detections) can be attached to cameras
- WebSocket streams allow live frame updates

The system is designed with a clear separation between:
- API layer (FastAPI)
- Business logic (services)
- Data storage (SQLModel + Redis / in-memory)
- Repositories (abstracted frame storage)

This makes it easy to extend, replace components, or scale specific parts of the system.

---

## Architecture

High-level components:

- FastAPI REST API + WebSocket endpoints
- SQLModel (SQLite by default) for persistence
- Redis (optional) for real-time frame buffering
- Repository pattern for frame storage abstraction
- JWT-based authentication for users
- API key authentication for cameras

To write: add architecture diagram

---

## Features

- User authentication (JWT)
- Camera creation with API key
- Multi-user access control (owner / viewer roles)
- Frame ingestion via API
- Real-time frame streaming via WebSocket
- Event creation and retrieval per camera
- Pluggable frame storage (in-memory or Redis)

---

## Getting Started

### Requirements

- Docker
- Docker Compose

---

### Run with Docker (recommended)

```bash
git clone <repo_url>
cd multi-user-vision-backend/API

docker compose up --build
```

API will be available at:
http://localhost:8000

Routes details at:
http://localhost:8000/docs

## Limitations (Intentional)

This project is a functional prototype and not production-ready.

Known limitations:
- Minimal security (hardcoded secret, no rate limiting, basic auth handling)
- API key lookup not optimized for scalability
- No strict input validation (payload size, formats, user inputs)
- Inconsistent behavior between in-memory and Redis repositories
- No pagination for events (potential performance issues at scale)
- No fault tolerance (e.g., Redis failures not handled)

These aspects are documented in the code and planned for future improvements.


## Future

Phase 1
* upgrade backend security
* camera SDK
* minimal UI
Phase 2
* pagination + filters
* websocket events
Phase 3
* images storage
* AI pipeline
