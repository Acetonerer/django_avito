FROM python:3.11

WORKDIR /code

RUN pip install --upgrade pip
RUN pip install celery
RUN pip install redis
COPY ./requirements.txt /code/
RUN pip install -r /code/requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=django_avito.settings

CMD ["gunicorn", "django_avito.wsgi:application", "--bind", "0.0.0.0:8000"]
