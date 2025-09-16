FROM python:3.12-slim AS base

RUN groupadd -r celeryuser && useradd -r -g celeryuser -u 1000 celeryuser

RUN apt-get update && apt-get install -y \
    gcc \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chown -R celeryuser:celeryuser /app

EXPOSE 5000

ENV FLASK_APP=app.py

RUN chmod +x wait-for-db.sh

CMD ["python", "app.py"] 
