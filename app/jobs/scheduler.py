from datetime import date, timedelta

from app import create_app
from app.jobs.sync_garmin import sync_garmin_job
from app.jobs.generate_trainings import generate_training_job
from apscheduler.schedulers.blocking import BlockingScheduler

app = create_app()


def run_daily_jobs():
    today = date.today()

    with app.app_context():
        sync_garmin_job(
            start_date=today - timedelta(days=1),
            end_date=today,
        )
        generate_training_job()


if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="Europe/Paris")

    scheduler.add_job(
        run_daily_jobs,
        trigger="cron",
        hour=6,
        minute=0,
        id="daily_jobs",
        max_instances=1,
    )

    scheduler.start()