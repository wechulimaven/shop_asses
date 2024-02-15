import os
from celery.schedules import crontab

TIME_ZONE = 'UTC'

BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_BROKER_URL")
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULE = {
    # "update_expired_referral_campaign_status": {
    #     "task": "update_expired_referral_campaign_status",
    #     "schedule": crontab(hour="0", minute="0"),
    # },
}
