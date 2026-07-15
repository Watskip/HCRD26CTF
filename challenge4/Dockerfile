FROM python:3.11-slim

LABEL Author="CTF-HackConRD"

# Create standard user
RUN addgroup --system ctf && adduser --system --ingroup ctf ctf

WORKDIR /app

# Create flag file
RUN mkdir -p /home/app && echo "HACKCON{SST1_W1TH0UT_0S}" > /home/app/flag.txt

# Install dependencies
RUN pip install flask

COPY files/src/backend /app/backend

RUN chown -R ctf:ctf /app

USER ctf

EXPOSE 80

CMD ["python", "backend/main.py"]
