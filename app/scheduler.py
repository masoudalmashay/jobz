# jobs/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from app.extensions import db
from flask import current_app
from app.models.job import Job

# Function to delete expired jobs
def delete_expired_jobs(app):
    with app.app_context():
        Job.delete_expired_jobs()  # Call the static method to delete expired jobs



def start(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=delete_expired_jobs,args=[app], trigger="interval", seconds=60)
    # scheduler.add_job(
    # func=delete_expired_jobs,
    # args=[app],
    # trigger="cron",
    # hour=0,       # 12 AM (midnight)
    # minute=0,     # 0 minutes
    # second=0      # 0 seconds
    # )
    scheduler.start()
    print("scheduler started...")
