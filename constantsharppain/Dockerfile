FROM python:3.12-alpine

WORKDIR /app

RUN apk add --no-cache chromium chromium-chromedriver

COPY files/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY files/ /app/

EXPOSE 4020

CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:4020", "--access-logfile", "-", "--error-logfile", "-", "--capture-output", "--log-level", "info", "app:app"]
