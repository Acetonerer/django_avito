FROM python:3.11

WORKDIR /code

COPY ./requirements.txt /code/

RUN pip install -r /code/requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "127.0.0.1:8000"]