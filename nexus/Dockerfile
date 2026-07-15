FROM python:3.9-slim

LABEL Author="CTF-Nexus"

# Instalar dependencias para compilar lxml
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libxml2-dev libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

COPY files /tmp/

RUN mkdir /app && \
    mv /tmp/src/* /app && \
    mv /tmp/docker-entrypoint /usr/local/bin/docker-entrypoint && \
    chmod +x /usr/local/bin/docker-entrypoint && \
    pip install --no-cache-dir -r /app/requirements.txt && \
    rm -rf /tmp/*

# --- AQUÍ ESTÁ LA FLAG ---
RUN echo "HCRD{xxe_w0rks_0n_l1nux_t00_r3fl3ct3d}" > /etc/secret_flag.txt
RUN chmod 644 /etc/secret_flag.txt

# Usuario no privilegiado
RUN useradd -m apache_user
USER apache_user

WORKDIR /app

EXPOSE 4001

CMD ["/bin/sh", "-c", "docker-entrypoint"]
