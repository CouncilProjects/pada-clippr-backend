from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from .cron import collect_site_analytics
import os
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()

class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analytics'

    def ready(self):
        if os.environ.get("RUN_MAIN") == "true":
            trigger = CronTrigger.from_crontab("*/10 * * * *")
            scheduler.add_job(collect_site_analytics, trigger=trigger)
            scheduler.start()
