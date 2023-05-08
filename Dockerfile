FROM python:3-slim

RUN mkdir app
WORKDIR app

ADD requirements.txt /app/
RUN pip install -r requirements.txt

ADD . /app/

RUN python friends/manage.py makemigrations socnet
RUN python friends/manage.py migrate

CMD python friends/manage.py runserver 0.0.0.0:8000
