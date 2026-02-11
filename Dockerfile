# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Установить системные зависимости
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копировать requirements и установить
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копировать весь проект
COPY . /app/

EXPOSE 8000
