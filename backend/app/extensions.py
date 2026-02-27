import os
from apscheduler.schedulers.background import BackgroundScheduler
from app.db.mongo import init_mongo
from app.jobs.openweather_job import run_openweather_job

scheduler = BackgroundScheduler()

def init_extensions(app):
    init_mongo()

    # run once immediately so you can verify it works
  #  run_openweather_job()

    enabled = os.getenv("ENABLE_SCHEDULER", "true").lower() == "true"
    interval = int(os.getenv("OPENWEATHER_INTERVAL_SECONDS", "900"))

    if enabled:
        scheduler.add_job(
            run_openweather_job,
            "interval",
            seconds=interval,
            id="openweather",
            replace_existing=True,
        )
        scheduler.start()