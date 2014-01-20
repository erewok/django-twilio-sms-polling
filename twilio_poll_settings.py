INSTALLED_APPS += (
    'twilio-polls-app',
)

SERIALIZATION_MODULES += {
    'csv': 'snippetscream.csv_serializer',
}

CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True
CELERY_IMPORT = ("twilio-polls-app",)
CELERY_USER = "celery"
CELERY_GROUP = "celery"

from datetime import timedelta
CELERYBEAT_SCHEDULE = {
    'cleanup_dbase': {
        'task': 'twilio-polls-app.tasks.cleanup_expired',
        'schedule' : timedelta(minutes=5)
        },
    'schedule_messages': {
        'task': 'twilio-polls-app.tasks.schedule_new_messages',
        'schedule' : timedelta(minutes=7)
        },
    'send_scheduled_messages' : {
        'task' : 'twilio-polls-app.tasks.send_scheduled_messages',
        'schedule' : timedelta(minutes=2),
        }
}
