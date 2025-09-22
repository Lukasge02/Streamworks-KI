# syntax=docker/dockerfile:1.7

# Backend runtime on Python 3.10 to satisfy langextract requirement
FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system deps needed for scientific/python packages (torch, lxml, etc.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libxml2-dev \
        libxslt1-dev \
        libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better layer caching
COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the backend source
COPY . .

# Expose API port
EXPOSE 8000

# Run uvicorn directly
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
