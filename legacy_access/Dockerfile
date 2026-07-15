FROM python:3.10-slim

LABEL Author="CTF-LegacyAccess"

COPY files /tmp/

RUN apt-get update && apt-get install -y iputils-ping && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /files/src && \
    mv /tmp/src/* /files/src && \
    mv /tmp/docker-entrypoint /usr/local/bin/docker-entrypoint && \
    chmod +x /usr/local/bin/docker-entrypoint && \
    pip install --no-cache-dir -r /files/src/requirements.txt && \
    rm -rf /tmp/*

# Flag setup (siguiendo la lógica original del reto)
RUN echo "HCRD{u53r_4g3nt_sp00f1ng_plu5_rc3}" > /flag.txt && chmod 644 /flag.txt

WORKDIR /files/src

# Puerto 80 como pide el usuario
EXPOSE 5006

CMD ["/bin/sh", "-c", "docker-entrypoint"]
