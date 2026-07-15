FROM python:3.11-slim

LABEL Author="CTF-PlaintextSec"

WORKDIR /app

# Install chromium and driver for Selenium bot
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

COPY files/src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY files/src/ .
COPY docker-entrypoint .
RUN sed -i 's/\r$//' docker-entrypoint && chmod +x docker-entrypoint

EXPOSE 9745
CMD ["./docker-entrypoint"]
