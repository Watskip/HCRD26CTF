FROM python:3.11-slim

LABEL Author="CTF-HackConRD"

# Create standard user
RUN addgroup --system ctf && adduser --system --ingroup ctf ctf

WORKDIR /app

# Create flag file
RUN echo "HACKCON{CMD1_BL4CKL1ST_BYP4SS}" > /flag.txt

# Install dependencies
RUN apt-get update && apt-get install -y iputils-ping && pip install flask && rm -rf /var/lib/apt/lists/*

COPY files/src/backend /app/backend

RUN chown -R ctf:ctf /app

USER ctf

EXPOSE 80

CMD ["python", "backend/main.py"]
