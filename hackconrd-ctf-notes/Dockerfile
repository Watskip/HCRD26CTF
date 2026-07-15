FROM node:20-alpine

LABEL Author="CTF-EJS-Notes"

COPY files /tmp/

# Install deps as root; flag outside app dir with group-read for service user only (not world-readable).
RUN mkdir /app && \
    cp -a /tmp/src/. /app/ && \
    mv /tmp/docker-entrypoint /usr/local/bin/docker-entrypoint && \
    chmod +x /usr/local/bin/docker-entrypoint && \
    cd /app && npm install --only=production && \
    mkdir -p /var/lib/ctf && \
    mv /app/root_flag.txt /var/lib/ctf/flag.txt && \
    chown root:node /var/lib/ctf /var/lib/ctf/flag.txt && \
    chmod 750 /var/lib/ctf && \
    chmod 440 /var/lib/ctf/flag.txt && \
    chown -R node:node /app && \
    rm -rf /tmp/*

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=5015

USER node

EXPOSE 5015

CMD ["/bin/sh", "-c", "docker-entrypoint"]
