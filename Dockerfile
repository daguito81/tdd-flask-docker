FROM python:3.8.1-slim-buster

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .
RUN apt-get update \
    && apt-get install -y vim \
    && apt-get clean \
    && python -m pip install --upgrade pip \
    && pip install -r requirements.txt

EXPOSE 5000

COPY . .

CMD python manage.py run -h 0.0.0.0