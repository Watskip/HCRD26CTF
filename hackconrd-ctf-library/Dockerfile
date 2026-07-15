FROM node:20-alpine

LABEL Author="CTF-HackConRD"

RUN addgroup -S g4l1l30 && adduser -S g4l1l30 -G g4l1l30

RUN apk add --no-cache libcap

COPY files /tmp/

RUN mkdir /app && \
    mv /tmp/src/* /app && \
    mv /tmp/docker-entrypoint /usr/local/bin/docker-entrypoint && \
    chmod +x /usr/local/bin/docker-entrypoint && \
    cd /app && npm install --only=production && \
    rm -rf /tmp/*

RUN echo 'HCRD{lfi_l1brary_tr4v3rs4l}' > /app/flag.txt && \
    chown root:root /app/flag.txt && \
    chmod 644 /app/flag.txt

RUN setcap cap_net_bind_service=+ep $(which node)

WORKDIR /app

ENV PORT=5014

USER g4l1l30

EXPOSE 5014

CMD ["/bin/sh", "-c", "docker-entrypoint"]
