# Responsible AI Testing & Bias Detection Framework for LLMs

**ULockAI Shield** — Enterprise AI Firewall & LLM Vulnerability Scanning Platform

[![Repository](https://github.com/SaravanavelE/Responsible-AI-Testing-Bias-Detection-Framework-for-LLMs)](https://github.com/SaravanavelE/Responsible-AI-Testing-Bias-Detection-Framework-for-LLMs)

An MVP+ framework for evaluating LLM applications on **security, fairness, hallucination, privacy, and compliance** risks. It provides automated vulnerability scanning, a live prompt firewall, PII redaction, policy enforcement, and an enterprise dashboard for responsible AI testing.

Inspired by enterprise guardrails (Lakera Guard, ProtectAI, Promptfoo) with modules for injection detection, jailbreak testing, DLP, and compliance mapping (OWASP LLM Top 10, NIST AI RMF, GDPR, CERT-In).

> **About this project:** Evaluates LLM responses for fairness, hallucination, and privacy-related risks with automated pipelines and a monitoring dashboard for responsible AI testing and mitigation insights.

---

## What is included in this repository

| Included | Description |
|----------|-------------|
| `backend/` | FastAPI app, detection engines, scan suites, Celery workers, tests |
| `frontend/` | Next.js 15 dashboard (9 modules) |
| `docker-compose.yml` | PostgreSQL, Redis, MinIO, API, workers |
| `.env.example` | Template for all environment variables (no secrets) |
| `DEPLOYMENT.md` | Production deployment guide |

## What is NOT included (install locally)

These are **intentionally excluded** from Git for security and size. **Clone the repo, then install them on your machine:**

| Excluded | Why | What you do |
|----------|-----|-------------|
| `.env` | Contains secrets (JWT key, DB password, API encryption key) | `cp .env.example .env` and edit values |
| `node_modules/` | npm dependencies (~hundreds of MB) | `cd frontend && npm install` |
| `frontend/.next/` | Next.js build cache | Created by `npm run dev` or `npm run build` |
| `backend/.venv/` | Python virtual environment | `cd backend && py -3.11 -m venv .venv` then `pip install -r requirements-local.txt` |
| `__pycache__/`, `*.pyc` | Python bytecode | Generated automatically |
| Docker volumes | Database/redis/minio data | Created by `docker compose up` |
| Uploaded reports / logs | Runtime artifacts | Generated at runtime |

> **Security:** Never commit `.env`, API keys, or `backend/.env`. Only `.env.example` belongs in Git.

---

## Features

- **9 Application Modules**: Dashboard, LLM Connectivity, Vulnerability Scan, Scan History, Reports, Policy Engine, Tenant Management, Audit Logs, Settings
- **20+ Detection Rules**: Injection, jailbreak, DLP, agent hijacking, RAG manipulation, unicode obfuscation, and more
- **10 Static Scan Suites** + **16 Dynamic AI Probe Suites** (20 probes per run)
- **Live Prompt Firewall** — Allow / Warn / Quarantine / Redact / Block
- **PII Redaction** — email, SSN, Aadhaar, PAN, API keys, JWT, etc.
- **Compliance Auto-Mapper** — OWASP LLM, NIST AI RMF, ISO, GDPR, CERT-In, MITRE ATLAS
- **Multi-tenant RBAC**, encrypted API key storage, audit logs

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15, React, TypeScript, TailwindCSS, shadcn/ui, Recharts, Framer Motion |
| Backend | FastAPI, Python 3.11+, SQLAlchemy, Celery |
| Database | PostgreSQL |
| Queue | Redis + Celery |
| Storage | MinIO (S3-compatible) |
| Auth | JWT + RBAC |

---

## Quick Start (for visitors)

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- [Node.js 20+](https://nodejs.org/)
- [Python 3.11+](https://www.python.org/) (3.14 not recommended — use 3.11 for backend wheels)

### 1. Clone

```bash
git clone https://github.com/SaravanavelE/Responsible-AI-Testing-Bias-Detection-Framework-for-LLMs.git
cd Responsible-AI-Testing-Bias-Detection-Framework-for-LLMs
```

### 2. Environment (required)

```bash
cp .env.example .env
```

Edit `.env` — set at minimum:

- `SECRET_KEY` — random 64+ character string
- `ENCRYPTION_KEY` — Fernet key: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`

> Postgres in Docker uses port **5433** on the host (avoids conflict with local PostgreSQL on 5432).

### 3. Start infrastructure

```bash
docker compose up postgres redis -d
```

### 4. Backend

```bash
cd backend
py -3.11 -m venv .venv
# Windows: .\.venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements-local.txt
copy ..\.env .env
python scripts/seed.py
uvicorn app.main:app --reload --port 8000
```

### 5. Frontend (new terminal)

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000** — login: `admin@ulockai.com` / `Admin123!`

### 6. Optional: Celery (for scans)

```bash
cd backend
.\.venv\Scripts\celery.exe -A app.workers.celery_app worker --loglevel=info --pool=solo
```

### Full stack with Docker

```bash
docker compose up -d
docker compose exec backend python scripts/seed.py
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## Project Structure

```
├── backend/           # FastAPI + engines + workers
├── frontend/          # Next.js dashboard
├── infra/prometheus/
├── docker-compose.yml
├── .env.example       # ← copy to .env (not in Git)
├── DEPLOYMENT.md
└── README.md
```

## Testing

```bash
cd backend
.\.venv\Scripts\pytest.exe tests/ -v
```

## API Overview

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/auth/login` | JWT authentication |
| `GET /api/v1/dashboard/stats` | Dashboard metrics |
| `GET/POST /api/v1/llm-connections` | LLM tenant CRUD |
| `POST /api/v1/scans` | Start vulnerability scan |
| `POST /api/v1/policies/firewall/intercept` | Live prompt firewall |

## License

MIT License — see [LICENSE](LICENSE).

## Author

[SaravanavelE](https://github.com/SaravanavelE) — Responsible AI Testing & Bias Detection Framework for LLMs
