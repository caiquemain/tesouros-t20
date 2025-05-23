# Use uma imagem Python oficial como base
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# CORREÇÃO APLICADA AQUI:
CMD gunicorn --bind "0.0.0.0:$PORT" app:app