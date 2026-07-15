FROM python:3.11-slim

WORKDIR /app

# No bot dependencies needed for this challenge
RUN apt-get update && rm -rf /var/lib/apt/lists/*

COPY files/src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY files/src/ .

EXPOSE 4003
CMD ["python", "app.py"]
