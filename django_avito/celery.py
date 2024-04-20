# from __future__ import absolute_import, unicode_literals
# from celery import Celery
# from celery.schedules import crontab
# from django_avito import settings
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