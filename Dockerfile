FROM python:3.13-slim
LABEL maintainer="wenhun1@gmail.com"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev gcc python3-dev

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
