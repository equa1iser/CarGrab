from app.tasks.celery_app import celery

celery.conf.beat_schedule = {
    "orchestrator": {
        "task": "app.tasks.ingest.orchestrator",
        "schedule": 60.0,  # every minute
    },
    "check-price-alerts": {
        "task": "app.tasks.ingest.check_price_alerts",
        "schedule": 300.0,  # every 5 minutes
    },
}
celery.conf.timezone = "UTC"
