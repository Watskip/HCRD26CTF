FROM python:3.12-alpine

LABEL Author="Notify-CTF"

WORKDIR /app

RUN apk add --no-cache ca-certificates && update-ca-certificates

COPY files/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY files/ /app/

EXPOSE 4016 80

CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:4016", "--bind", "0.0.0.0:80", "--access-logfile", "-", "--error-logfile", "-", "--capture-output", "--log-level", "info", "app:app"]
