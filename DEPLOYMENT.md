# ULockAI Shield — Deployment Guide

## Production Architecture

```
                    ┌─────────────┐
                    │   CDN/WAF   │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │                         │
       ┌──────▼──────┐          ┌──────▼──────┐
       │  Frontend   │          │   Backend   │
       │  Next.js 15 │          │   FastAPI   │
       └─────────────┘          └──────┬──────┘
                                        │
         ┌──────────────┬───────────────┼───────────────┐
         │              │               │               │
  ┌──────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐ ┌──────▼──────┐
  │ PostgreSQL  │ │   Redis   │ │   Celery    │ │    MinIO    │
  └─────────────┘ └───────────┘ └─────────────┘ └─────────────┘
```

## Environment Variables (Production)

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | 64+ char random string for JWT |
| `ENCRYPTION_KEY` | Yes | Fernet key for API key encryption |
| `DATABASE_URL` | Yes | PostgreSQL async connection string |
| `REDIS_URL` | Yes | Redis for rate limiting / pub-sub |
| `CELERY_BROKER_URL` | Yes | Celery task broker |
| `S3_ENDPOINT` | Yes | MinIO or AWS S3 endpoint |
| `CORS_ORIGINS` | Yes | Allowed frontend origins |

## Docker Compose Production

1. Set production values in `.env`
2. Remove `--reload` from backend command in `docker-compose.yml`
3. Use external managed PostgreSQL/Redis for HA
4. Enable TLS termination at load balancer
5. Configure MinIO bucket policy for reports

```bash
docker compose -f docker-compose.yml up -d --build
docker compose exec backend python scripts/seed.py
```

## Kubernetes (Outline)

- **Deployments**: `backend`, `celery-worker`, `celery-beat`, `frontend`
- **StatefulSet**: PostgreSQL (or use RDS)
- **Services**: ClusterIP for internal, LoadBalancer for ingress
- **Secrets**: `SECRET_KEY`, `ENCRYPTION_KEY`, DB credentials via K8s Secrets
- **HPA**: Scale Celery workers based on Redis queue depth

## Security Checklist

- [ ] Rotate `SECRET_KEY` and `ENCRYPTION_KEY`
- [ ] Enable HTTPS everywhere
- [ ] Restrict CORS to production domains
- [ ] Configure rate limiting (`RATE_LIMIT_PER_MINUTE`)
- [ ] Enable PostgreSQL SSL
- [ ] Use IAM roles for S3 (instead of static keys)
- [ ] Set `APP_ENV=production`
- [ ] Disable API docs (`docs_url=None`) in production
- [ ] Configure log aggregation for structlog JSON output
- [ ] Set up Prometheus alerting on `/metrics`

## Observability

### Prometheus
Scrape `http://backend:8000/metrics` — metrics include:
- `ulockai_http_requests_total`
- `ulockai_http_request_duration_seconds`

### OpenTelemetry
Set `OTEL_EXPORTER_OTLP_ENDPOINT` to your collector (Jaeger, Datadog, etc.)

### Audit Logs
All security actions logged to `audit_logs` table with structured JSON `details`.

## Scaling Guidelines

| Component | Scaling Strategy |
|-----------|------------------|
| Backend API | Horizontal — stateless, scale on CPU |
| Celery Workers | Scale on queue depth — 1 worker per 4 parallel probes |
| PostgreSQL | Vertical + read replicas for reporting |
| Redis | Cluster mode for HA |
| MinIO | Distributed mode for large report storage |

## Backup & Recovery

- **PostgreSQL**: Daily snapshots, point-in-time recovery
- **MinIO**: Versioning enabled on `ulockai-reports` bucket
- **Redis**: AOF persistence for task state

## Health Checks

```bash
curl http://localhost:8000/health
curl http://localhost:3000
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Scan stuck in `queued` | Verify Celery worker is running |
| LLM test fails | Check API key encryption key matches |
| PDF reports empty | Install WeasyPrint system deps in Docker image |
| CORS errors | Add frontend URL to `CORS_ORIGINS` |
