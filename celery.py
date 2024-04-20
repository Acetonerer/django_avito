import os
from celery import Celery
from django_avito import settings

# Установка переменной окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_avito.settings')

app = Celery('django_avito')
app.conf.update(
    CELERY_BROKER_URL='redis://redis:6379/0',
    CELERY_ACCEPT_CONTENT=['json'],
    CELERY_RESULT_BACKEND='redis://redis:6379/0',
    CELERY_TIMEZONE='Europe/Moscow',
)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
