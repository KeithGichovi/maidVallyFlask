from app import create_app
from app.extensions import celery
from celery.schedules import crontab
app = create_app()
app.app_context().push()


celery.conf.beat_schedule = {
    'weekly-reminder-for-unpaid-jobs': {
        'task': 'app.tasks.send_weekly_reminder_for_unpaid_jobs',
        'schedule': crontab(day_of_week="mon", hour=9, minute=30),
    },

    'monthly-report': {
        'task': 'app.tasks.get_monthly_report',
        'schedule': crontab(day_of_month=1, hour=0, minute=0),
    },

    # 'test-email': {
    #     'task': 'app.tasks.send_test_email',
    #     'schedule': crontab(minute='*/1'),
    # },

    'monthly_reminder_for_unpaid_jobs':{
        'task': 'app.tasks.send_monthly_reminder_for_unpaid_jobs',
        'schedule': crontab(day_of_month=1, hour=9, minute=30),
    }

}

celery.conf.timezone = 'Europe/London'