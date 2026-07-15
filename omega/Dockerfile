FROM python:3.9-slim

LABEL Author="CTF-Omega"

COPY files /tmp/

RUN mkdir /app && \
    mv /tmp/src/* /app && \
    mv /tmp/docker-entrypoint /usr/local/bin/docker-entrypoint && \
    chmod +x /usr/local/bin/docker-entrypoint && \
    pip install --no-cache-dir -r /app/requirements.txt && \
    rm -rf /tmp/*

WORKDIR /app

EXPOSE 5003

CMD ["/bin/sh", "-c", "docker-entrypoint"]
