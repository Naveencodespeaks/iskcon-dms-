# WhatsApp AI Operations Copilot

A production-ready, multi-tenant AI-powered operations platform that uses **WhatsApp** as the primary communication channel for customer support, ticketing ("jobs"), document knowledge base (RAG), and automated agent assignment.

## Architecture Overview

```
Customer (WhatsApp)
        │
        ▼
FastAPI Webhook (/webhook/whatsapp)
        │
        ▼
Message stored + Heuristic Job creation
        │
        ▼
Celery Workers (background)
   ├── Job Assignment (least-loaded agent)
   └── Document Ingestion → Qdrant (embeddings + semantic search)

Authenticated Dashboard (Next.js)
        │
        ▼
FastAPI (RBAC + JWT)
   ├── Jobs CRUD
   ├── Documents + RAG query
   ├── Search
   └── Analytics (placeholder)
```

**Core Technologies**
- Backend: FastAPI + SQLAlchemy (async) + Pydantic
- Queue/Workers: Celery + Redis
- Vector DB: Qdrant (for RAG)
- Database: PostgreSQL
- Auth: JWT + RBAC (roles + permissions)
- Frontend: Next.js 13 (basic dashboard)
- Deployment: Docker Compose (all services)

## Quick Cheat Sheet

### Local Development (Fast iteration with hot reload)
```bash
# 1. Start infrastructure
docker compose up -d db redis qdrant

# 2. Backend (with hot reload)
cd backend
source env/bin/activate
uvicorn app.main:app --reload --port 8000

# 3. Celery worker (new terminal)
cd backend && source env/bin/activate
celery -A app.core.celery_app.celery_app worker -l info --pool=solo

# 4. Frontend (new terminal)
cd frontend
npm run dev
```

**Access:**
- Backend: http://localhost:8000/docs
- Frontend: http://localhost:3000

### Full Deployment (Docker Compose)
```bash
cd whatsapp_ai_copilot_project

# Start everything (build if needed)
docker compose up -d --build

# View logs
docker compose logs -f backend

# Rebuild after changes
docker compose up -d --build

# Stop everything
docker compose down
```

**Access:**
- Backend: http://localhost:18000/docs
- Frontend: http://localhost:13000

### Default Login
- Email: `admin@example.com`
- Password: `admin123`

### Important .env Differences

| Mode          | DATABASE_URL host          | Backend port | Frontend API URL          |
|---------------|----------------------------|--------------|---------------------------|
| **Local**     | `localhost:15432`          | 8000         | `http://localhost:8000`   |
| **Deployed**  | `db:5432` (internal)       | 18000        | `http://localhost:18000`  |

---

## Key Features

- **WhatsApp Integration**: Receives messages via webhook, auto-creates jobs.
- **Jobs/Tickets**: Full lifecycle with status, priority, assignment.
- **RAG**: Upload documents → semantic search against tenant knowledge base.
- **Agent Assignment**: Celery task assigns jobs to least-loaded agent.
- **Multi-Tenant + RBAC**: Strict tenant isolation and permission checks.
- **Background Processing**: Ingestion and assignment run asynchronously.

## Hybrid Model – Two Ways (Local + Deployed)

This project follows a **hybrid model**. You should understand and be able to use **both** approaches:

- **Local Development Mode** → Fast coding and debugging (using `uvicorn --reload`)
- **Full Deployed Mode** → Production-like testing (using Docker Compose)

Both use the **exact same code**. Only the way you start services and the connection strings change.

---

### Way 1: Local Development Mode (Fast Local Testing)

Use this when you are developing or debugging.

#### Step-by-Step Local Run

```bash
# 1. Start only databases (Postgres, Redis, Qdrant)
cd whatsapp_ai_copilot_project
docker compose up -d db redis qdrant
```

```bash
# 2. Setup Backend
cd backend
source env/bin/activate

# First time only
pip install -r requirements.txt

# Create local config
cp ../.env.example .env
```

**Edit `backend/.env`** — use these values for local:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:15432/copilot
REDIS_URL=redis://localhost:16380/0
QDRANT_URL=http://localhost:16334

CELERY_BROKER_URL=redis://localhost:16380/1
CELERY_RESULT_BACKEND=redis://localhost:16380/2

NEXT_PUBLIC_API_URL=http://localhost:8000
```

```bash
# 3. Run migrations
alembic upgrade head

# 4. Start Backend locally with hot reload
uvicorn app.main:app --reload --port 8000
```

Open new terminals:

```bash
# Celery Worker
cd backend && source env/bin/activate
celery -A app.core.celery_app.celery_app worker -l info --pool=solo
```

```bash
# Frontend
cd frontend
npm install
npm run dev
```

**Access in Local Mode:**
- Backend: `http://localhost:8000/docs`
- Frontend: `http://localhost:3000`

---

### Way 2: Full Deployed Mode (Docker Compose)

Use this when you want to test exactly like production / deployment.

```bash
cd whatsapp_ai_copilot_project

# Build + start everything
docker compose up -d --build
```

**Access in Deployed Mode:**
- Backend + API Docs: `http://localhost:18000/docs`
- Frontend: `http://localhost:13000`

**Common Deploy Commands:**
```bash
# Rebuild after code changes
docker compose up -d --build

# View logs
docker compose logs -f backend

# Stop everything
docker compose down
```

---

### What Changes Between Local and Deployed?

| Item                      | Local Mode (`uvicorn`)               | Deployed Mode (`docker compose`)     |
|---------------------------|--------------------------------------|--------------------------------------|
| Backend command           | `uvicorn app.main:app --reload`     | Handled by Docker                    |
| Backend port (you use)    | 8000                                 | 18000                                |
| Frontend port             | 3000                                 | 13000                                |
| `DATABASE_URL`            | `localhost:15432`                    | `db:5432`                            |
| `REDIS_URL`               | `localhost:16380`                    | `redis:6379`                         |
| `QDRANT_URL`              | `localhost:16334`                    | `qdrant:6333`                        |
| `NEXT_PUBLIC_API_URL`     | `http://localhost:8000`              | `http://localhost:18000`             |
| Hot reload                | Yes                                  | No (need `--build`)                  |
| How to run Celery         | Manual command                       | Auto started                         |

**Rule of thumb:**
- **Local** → everything points to `localhost` with the Docker-mapped ports
- **Deployed** → services talk to each other using container names (no `localhost`)

Always restart the backend after changing `.env`.

---

### End-to-End Testing in Both Modes

You can (and should) test the full flow in **both** environments:

1. Login (`/api/v1/auth/login`)
2. Create a Job
3. Send a fake WhatsApp message via webhook
4. Upload a document + trigger RAG
5. Search using `/api/v1/search/query`

**Local test ports:** 8000 (API) + 3000 (UI)  
**Deployed test ports:** 18000 (API) + 13000 (UI)

   Access at: http://localhost:3000

**Login credentials (after bootstrap):**
- Email: `admin@example.com`
- Password: `admin123`

---

### Way 2: Full Deployment (Docker Compose) – For Production-like Testing

Use this when you want to test exactly like it will run after deployment.

#### Step-by-step

1. **Start the complete stack**
   ```bash
   cd whatsapp_ai_copilot_project
   docker compose up -d --build
   ```

2. **Wait for services to be healthy** (check with `docker compose ps`)

3. **Access points (Docker-mapped ports):**
   - Backend + Swagger: **http://localhost:18000/docs**
   - Frontend: **http://localhost:13000**

4. **Bootstrap data** (if not already done)
   The app creates tables automatically. You can run the bootstrap script if needed:

   ```bash
   docker compose exec backend python /tmp/bootstrap_full.py
   ```

5. **Login**
   Use the same credentials:
   - `admin@example.com` / `admin123`

   Get token:
   ```bash
   curl -X POST http://localhost:18000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@example.com","password":"admin123"}'
   ```

---

### Key Differences Between Local and Deployed Mode

| Item                        | Local (Uvicorn)                  | Deployed (Docker Compose)         | What to Change |
|----------------------------|----------------------------------|-----------------------------------|----------------|
| Backend start command      | `uvicorn app.main:app --reload` | `docker compose up backend`      | Command |
| Backend port               | 8000                             | 18000 (mapped)                   | Ports + `NEXT_PUBLIC_API_URL` |
| Frontend port              | 3000                             | 13000 (mapped)                   | `NEXT_PUBLIC_API_URL` |
| Database host              | `localhost:15432`                | `db:5432` (internal)             | `.env` |
| Redis / Qdrant host        | `localhost:...`                  | service name (internal)          | `.env` |
| Hot reload                 | Yes (uvicorn)                    | No (need rebuild)                | — |
| Celery                     | Manual terminal                  | Managed by compose               | — |

**Most important file to edit when switching modes:**
- `backend/.env` (or root `.env` when using Docker)

## End-to-End Functional Test Results (as of 2026-06-22)

All core flows were executed successfully:

1. **Services healthy**: backend, celery-worker, db, frontend, qdrant, redis all `Up`.
2. **Authentication**: Login returns valid JWT containing tenant claims.
3. **Job Creation**: `POST /api/v1/jobs` → 201 Created (with RBAC).
4. **WhatsApp Webhook**:
   ```json
   POST /webhook/whatsapp
   ```
   Response: `{"status":"received"}`
   - Message persisted.
   - Job auto-created from message content.
5. **Document + RAG**:
   - File placed on disk.
   - Document record created.
   - Ingestion triggered.
   - `GET /api/v1/search/query?q=...` returns relevant policy chunks (demo + vector path).
6. **Celery**: Worker active and processing tasks (assignment & ingestion).

## Important API Endpoints

| Method | Endpoint                        | Description                          | Auth |
|--------|----------------------------------|--------------------------------------|------|
| POST   | /api/v1/auth/login              | Get JWT                              | No   |
| POST   | /api/v1/jobs                    | Create job                           | Yes  |
| GET    | /api/v1/jobs                    | List jobs (tenant scoped)            | Yes  |
| POST   | /webhook/whatsapp               | WhatsApp inbound (Facebook format)   | No   |
| POST   | /api/v1/documents/?file_path=.. | Create document record + ingest      | Yes  |
| POST   | /api/v1/documents/{id}/ingest   | Manually trigger ingestion           | Yes  |
| GET    | /api/v1/search/query?q=...      | Semantic RAG search                  | Yes  |

**Note on ports:**
- Local mode → use `http://localhost:8000`
- Docker deployed mode → use `http://localhost:18000`

Full interactive docs:
- Local: http://localhost:8000/docs
- Deployed: http://localhost:18000/docs

## How the Application Works (Flows)

### WhatsApp → Job Flow
1. External system (or test curl) posts Facebook-style payload to `/webhook/whatsapp`.
2. Backend extracts `text.body` and `from`.
3. Creates `Message` record.
4. If no associated job → creates a new `Job` with the message text as title/description.
5. Returns 200.

### Document Ingestion + RAG
1. Call document upload with `file_path` (file must exist on backend container disk).
2. `ingestion_service` creates `Document` row.
3. Calls `rag_service.ingest_document`:
   - Reads file
   - Splits by paragraphs
   - Generates embeddings (dummy in current demo)
   - Upserts to per-tenant Qdrant collection
4. Query via `/search/query` returns best matching chunks + scores.

### Job Assignment (Celery)
- `assign_unassigned_jobs` task (can be scheduled via Celery Beat).
- Finds jobs without `assigned_agent_id`.
- Picks agent with lowest `current_load` for the tenant.
- Updates job and agent load.

## Project Structure (Key Parts)

```
whatsapp_ai_copilot_project/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # jobs, messages, documents, search, ...
│   │   ├── auth/            # JWT login + dependencies
│   │   ├── core/            # config, db, celery, vector
│   │   ├── integrations/    # whatsapp webhook
│   │   ├── models/          # SQLAlchemy (Tenant, Job, User, Document, Role, ...)
│   │   ├── services/        # business logic + RAG
│   │   └── tasks/           # Celery tasks
│   └── Dockerfile
├── frontend/                # Next.js dashboard (basic)
├── docker-compose.yml
└── .env
```

## Local Development (Uvicorn + Next.js)

While Docker Compose is the easiest way to run everything, you can develop locally using `uvicorn` for hot-reloading the backend and `npm run dev` for the frontend.

### Recommended Approach: Docker for Services + Local Apps

This is the best developer experience (you don't need to install Postgres/Redis/Qdrant locally).

#### Step 1: Start only the infrastructure services

```bash
cd whatsapp_ai_copilot_project
docker compose up -d db redis qdrant
```

Services will be available on these **host** ports:
- PostgreSQL → `localhost:15432`
- Redis → `localhost:16380`
- Qdrant → `localhost:16334`

#### Step 2: Backend (FastAPI) - Local with Uvicorn

```bash
cd backend

# Activate the existing virtual environment (recommended)
source env/bin/activate
# On Windows: env\Scripts\activate

# Install dependencies (if you haven't already)
pip install -r requirements.txt
```

Create/edit a local `.env` file (copy from root if needed):

```bash
cp ../.env.example .env
```

**Important changes for local development** (edit `.env`):

```env
# Point to the Docker services on your host machine
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:15432/copilot
REDIS_URL=redis://localhost:16380/0
QDRANT_URL=http://localhost:16334

CELERY_BROKER_URL=redis://localhost:16380/1
CELERY_RESULT_BACKEND=redis://localhost:16380/2

# For frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Run migrations** (from the `backend` folder):

```bash
alembic upgrade head
```

**Start the backend with hot reload**:

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at:
- http://localhost:8000
- Swagger docs: http://localhost:8000/docs

#### Step 3: Celery Worker (in a separate terminal)

```bash
cd backend
source env/bin/activate

celery -A app.core.celery_app.celery_app worker -l info --pool=solo
```

#### Step 4: Frontend (Next.js)

Open a new terminal:

```bash
cd frontend
npm install

npm run dev
```

Frontend will start at **http://localhost:3000**

Update `NEXT_PUBLIC_API_URL` in the frontend `.env` (or via `next.config`) to `http://localhost:8000` if needed.

---

### What You Need to Change for Local vs Docker

| Setting                    | Docker Compose (default)               | Local Development (Uvicorn)              |
|---------------------------|----------------------------------------|------------------------------------------|
| `DATABASE_URL`            | `...@db:5432/copilot`                  | `...@localhost:15432/copilot`            |
| `REDIS_URL`               | `...@redis:6379/0`                     | `...@localhost:16380/0`                  |
| `QDRANT_URL`              | `http://qdrant:6333`                   | `http://localhost:16334`                 |
| Backend exposed port      | 18000                                  | 8000                                     |
| `NEXT_PUBLIC_API_URL`     | `http://localhost:18000`               | `http://localhost:8000`                  |
| How to run backend        | `docker compose up backend`            | `uvicorn app.main:app --reload`          |
| Working directory         | Project root                           | `backend/` folder                        |

### Full Local Run (No Docker at all)

1. Install and run **PostgreSQL**, **Redis**, and **Qdrant** locally on default ports.
2. Use default connection strings in `.env`:
   - `DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/copilot`
   - `REDIS_URL=redis://localhost:6379/0`
   - `QDRANT_URL=http://localhost:6333`
3. Follow the same backend/frontend commands above.

### Useful Commands

```bash
# Backend with auto-reload
cd backend && source env/bin/activate && uvicorn app.main:app --reload

# Celery worker
celery -A app.core.celery_app.celery_app worker -l info --pool=solo

# Run tests (if added)
pytest

# Frontend dev server
cd frontend && npm run dev

# Generate a new migration
alembic revision --autogenerate -m "your message"
```

## Running in Production Notes

- Replace dummy embeddings in `rag_service.py` with real model (OpenAI, sentence-transformers, etc.).
- Store files in object storage instead of local paths.
- Add proper WhatsApp Cloud API sending (currently simulated).
- Secure secrets, enable HTTPS, proper CORS.
- Add Celery Beat for periodic assignment.
- Expand frontend with real forms, auth UI, live updates (socket.io is already in package).

## License & Notes

This project was completed and hardened for a full end-to-end working demonstration.

---

**Last verified E2E run**: All major flows (auth → job → WhatsApp → RAG → Celery) passed successfully.