# Notify sample webapp

Small Python app that checks whether a website is up and returns only HTTP response status information.

## Routes

- `GET /check?url=<http-or-https-url>`
  Behavior:
  - If upstream response is `200`, returns `200 OK` with status `up`
  - Otherwise returns `500` with status `error` and `HTTP/500`

## Run locally

1. Install dependencies:
   - `pip install -r requirements.txt`
2. Start app:
   - `python app.py`
3. Open:
   - `http://127.0.0.1:5000/check?url=https://example.com`

## Run with Docker

From `web/Notify`:

1. Build and start:
   - `docker compose up --build -d`
2. Open:
   - `http://localhost/check?url=https://example.com`
