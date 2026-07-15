FROM python:3.11-slim

LABEL Author="CTF-HackConRD"

# Create standard user
RUN addgroup --system ctf && adduser --system --ingroup ctf ctf

WORKDIR /app

# Install dependencies
RUN pip install flask

COPY files /app

RUN chown -R ctf:ctf /app

USER ctf

EXPOSE 5022

CMD ["python", "src/backend/main.py"]
