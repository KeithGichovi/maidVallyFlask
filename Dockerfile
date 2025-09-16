FROM python:3.12 AS base

# Install system dependencies including MySQL client
RUN apt-get update && apt-get install -y \
    gcc \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

ENV FLASK_APP=app.py

RUN chmod +x wait-for-db.sh

CMD ["python", "app.py"] 
