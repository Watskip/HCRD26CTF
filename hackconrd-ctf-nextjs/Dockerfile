FROM node:20-alpine

LABEL Author="CTF-NextJS"

# Usuario original del CTF
RUN addgroup -S nextjs && adduser -S nextjs -G nextjs

# Dependencia para permitir a node abrir el puerto 80 sin ser root
RUN apk add --no-cache libcap

COPY files /tmp/

RUN mkdir /app && \
    cp -a /tmp/src/. /app/ && \
    mv /tmp/docker-entrypoint /usr/local/bin/docker-entrypoint && \
    chmod +x /usr/local/bin/docker-entrypoint && \
    rm -rf /tmp/*

# Permitir a node abrir el puerto 80
RUN setcap cap_net_bind_service=+ep $(which node)

# Configuramos variables de entorno requeridas por Next.js standalone
ENV NODE_ENV=production
ENV PORT=5013
ENV HOSTNAME="0.0.0.0"

WORKDIR /app

USER nextjs

EXPOSE 5013

CMD ["/bin/sh", "-c", "docker-entrypoint"]
