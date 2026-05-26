from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "ulockai_shield",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "red-team-scan": {
            "task": "app.workers.tasks.red_team_continuous_scan",
            "schedule": 3600.0,
        },
        "threat-feed-sync": {
            "task": "app.workers.tasks.sync_threat_feed",
            "schedule": 1800.0,
        },
    },
)
