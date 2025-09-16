from app import create_app
from app.extensions import celery
from celery.schedules import crontab
app = create_app()
app.app_context().push()


celery.conf.beat_schedule = {
    'weekly-reminder-for-unpaid-jobs': {
        'task': 'app.tasks.send_weekly_reminder_for_unpaid_jobs',
        'schedule': crontab(day_of_week=1, hour=9, minute=30),  # Monday at 9:30 AM
    },

    'monthly-report': {
        'task': 'app.tasks.get_monthly_report',
        'schedule': crontab(day_of_month=1, hour=9, minute=30),  # 1st of every month at 9:30 AM
    },

    'monthly_reminder_for_unpaid_jobs': {
        'task': 'app.tasks.send_monthly_reminder_for_unpaid_jobs',
        'schedule': crontab(day_of_month=1, hour=9, minute=30),  # 1st of every month at 9:30 AM
    }
}

celery.conf.timezone = 'Europe/London'