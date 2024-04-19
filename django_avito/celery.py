# from __future__ import absolute_import, unicode_literals
# import os
# import django
# from celery import Celery
# from celery.schedules import crontab
#
# from django.conf import settings
#
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_avito.settings')
#
#
# app = Celery('django_avito')
# app.config_from_object(settings, namespace='CELERY')
#
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
#
# app.conf.beat_schedule = {
#     'fetch-ads': {
#         'task': 'ads.tasks.fetch_and_save_ads',
#         'schedule': crontab(hour="1", minute="0"),
#     },
#     'fetch-stats': {
#         'task': 'stats.tasks.fetch_and_save_statistics',
#         'schedule': crontab(hour="1", minute="0"),
#     },
# }
