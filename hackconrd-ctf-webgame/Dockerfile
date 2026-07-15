FROM python:3.11-slim

LABEL Author="CTF-HackConRD"

# Create standard user
RUN addgroup --system ctf && adduser --system --ingroup ctf ctf

WORKDIR /app

# Install dependencies
RUN pip install fastapi uvicorn websockets pydantic

COPY files/src/backend /app/backend
COPY files/src/frontend /app/frontend

RUN chown -R ctf:ctf /app

USER ctf

EXPOSE 80

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "80"]