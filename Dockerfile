FROM python:3.11

WORKDIR /code

COPY ./requirements.txt /code/

RUN pip install -r /code/requirements.txt

COPY . .

CMD ["gunicorn", "django_avito.wsgi:application", "--bind", "0.0.0.0:8000"]
