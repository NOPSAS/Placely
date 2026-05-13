FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpoppler-cpp-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

# Støtte for både lokal (8001) og cloud PORT-miljøvariabel
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8001}
