# syntax=docker/dockerfile:1.7

# 1. Use the ARM64-compatible Selenium-Chromium image
FROM --platform=linux/arm64 seleniarm/standalone-chromium:latest

USER root

# 2. Update & install Python3, venv, curl (all ARM64 binaries)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      python3 \
      python3-venv \
      curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 3. Create and activate a virtual environment, then install requirements
COPY requirements.txt .
RUN python3 -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of your application
COPY . .

# 5. Ensure the venv's Python is used on startup
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# 6. Wait for Selenium (port 4444) to be ready, then run the scraper
CMD bash -c '\
  for i in {1..15}; do \
    if curl -s http://localhost:4444/wd/hub/status | grep -q "\"ready\":true"; then break; fi; \
    echo "⏳  waiting for Selenium Grid…"; sleep 2; \
  done && \
  python /app/business-standard.py'
