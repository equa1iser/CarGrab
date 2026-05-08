from celery.schedules import crontab
from app.tasks.celery_app import celery

celery.conf.beat_schedule = {
    "poll-autodev": {
        "task": "app.tasks.ingest.poll_autodev",
        "schedule": crontab(minute="*/60"),  # hourly — conserves free-tier quota
    },
    "poll-ebay": {
        "task": "app.tasks.ingest.poll_ebay",
        "schedule": crontab(minute="*/30"),
    },
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
