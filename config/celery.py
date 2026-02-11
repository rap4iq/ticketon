import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTIGNS_MODULE', 'config.settings')

app = Celery('config')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


app.conf.beat_schedule = {
    'cancel-expired-bookings-every-5-minutes': {
        'task': 'apps.bookings.tasks.cancel_all_expired_bookings',
        'schedule': crontab(minute='*/5'),  # каждые 5 минут
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')