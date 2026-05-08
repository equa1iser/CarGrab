from celery.schedules import crontab
from app.tasks.celery_app import celery

celery.conf.beat_schedule = {
    "poll-carmax": {
        "task": "app.tasks.ingest.poll_carmax",
        "schedule": crontab(minute="*/30"),
    },
    "poll-marketcheck": {
        "task": "app.tasks.ingest.poll_marketcheck",
        "schedule": crontab(minute="*/15"),
    },
    "check-price-alerts": {
        "task": "app.tasks.ingest.check_price_alerts",
        "schedule": crontab(minute="*/5"),
    },
}
