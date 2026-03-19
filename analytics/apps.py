from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from .cron import collect_site_analytics, collect_seller_analytics
from os import environ

scheduler = BackgroundScheduler()

class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analytics'

    def ready(self):
        if environ.get("RUN_MAIN") == "true":
            scheduler.add_job(collect_site_analytics, trigger=CronTrigger.from_crontab("*/10 * * * *"))
            scheduler.add_job(collect_seller_analytics, trigger=CronTrigger.from_crontab("*/10 * * * *"))
            scheduler.start()
