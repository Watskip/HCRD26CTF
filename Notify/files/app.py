import ipaddress
import logging
import socket
from flask import Flask, Response, jsonify, render_template, request
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from urllib.parse import urljoin, urlsplit, urlunsplit
from xml.sax.saxutils import escape as _escape_basic

_QUOTE_ENTITIES = {'"': "&quot;", "'": "&apos;"}


def escape(s: str) -> str:
    return _escape_basic(s, _QUOTE_ENTITIES)


app = Flask(__name__)
app.logger.setLevel(logging.INFO)
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

FLAG = "HCRD{r3d1r3ct_up0n_r3d1r3ct}"

DEFAULT_TIMEOUT_SECONDS = 5
MAX_REDIRECTS = 30
DOCKER_API_PORTS = {2375, 2376}
DOCKER_HOSTS = {"host.docker.internal", "gateway.docker.internal"}
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
STANDARD_REDIRECT_CODES = {301, 302, 303, 307, 308}


def _resolves_to_docker_reachable_ip(hostname: str, port: int | None) -> bool:
    """Return True if *hostname* resolves to a private/link-local (non-loopback)
    IP, which could reach the Docker host or other containers on the bridge."""
    try:
        results = socket.getaddrinfo(hostname, port or 80, proto=socket.IPPROTO_TCP)
    except (socket.gaierror, OSError):
        return False
    for _fam, _type, _proto, _canon, sockaddr in results:
        try:
            ip = ipaddress.ip_address(sockaddr[0])
        except ValueError:
            continue
        if ip.is_loopback:
            continue
        if ip.is_private or ip.is_reserved or ip.is_link_local:
            return True
    return False


def is_docker_socket_target(url: str) -> bool:
    """Return True if *url* could reach the Docker daemon API."""
    parsed = urlsplit(url)
    hostname = (parsed.hostname or "").lower()
    port = parsed.port

    if port in DOCKER_API_PORTS:
        return True

    if hostname in DOCKER_HOSTS:
        return True

    if _resolves_to_docker_reachable_ip(hostname, port):
        return True

    return False


def _is_loopback_target(url: str) -> bool:
    parsed = urlsplit(url)
    hostname = (parsed.hostname or "").lower()
    if hostname in LOOPBACK_HOSTS:
        return True
    try:
        results = socket.getaddrinfo(hostname, parsed.port or 80, proto=socket.IPPROTO_TCP)
        for _fam, _type, _proto, _canon, sockaddr in results:
            try:
                ip = ipaddress.ip_address(sockaddr[0])
            except ValueError:
                continue
            if ip.is_loopback:
                return True
    except (socket.gaierror, OSError):
        pass
    return False


def is_blocked_target(url: str) -> bool:
    return _is_loopback_target(url) or is_docker_socket_target(url)


def build_error_xml(url: str, message: str, headers: str = "", reason: str = ""):
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
        "<errorResponse>"
        f"<url>{escape(url)}</url>"
        "<statusCode>500</statusCode>"
        f"<reason>{escape(reason)}</reason>"
        f"<headers>{headers}</headers>"
        f"<body>{escape(message)}</body>"
        "</errorResponse>"
    )


def normalize_local_target_url(raw_url: str) -> str:
    parsed = urlsplit(raw_url)
    hostname = (parsed.hostname or "").lower()

    if hostname in {"127.0.0.1", "localhost", "::1"} and parsed.port == 4016:
        # Map external challenge port back to internal container service.
        return urlunsplit((parsed.scheme, hostname, parsed.path, parsed.query, parsed.fragment))

    return raw_url


def fetch_with_redirects(session: requests.Session, initial_url: str) -> requests.Response:
    """Follow redirects manually so each hop is visible and controlled."""
    current_url = initial_url
    redirect_count = 0
    history = []
    upstream_status = None

    while True:
        response = session.get(
            current_url,
            timeout=DEFAULT_TIMEOUT_SECONDS,
            allow_redirects=False,
        )

        if 300 <= response.status_code < 400 and response.headers.get("Location"):
            redirect_count += 1
            if redirect_count > MAX_REDIRECTS:
                raise requests.TooManyRedirects(f"Exceeded {MAX_REDIRECTS} redirects")

            history.append(response)
            next_url = urljoin(response.url, response.headers["Location"])

            if response.status_code in STANDARD_REDIRECT_CODES:
                if is_blocked_target(next_url):
                    raise requests.ConnectionError("Connection refused")
            else:
                upstream_status = response.status_code

            if is_docker_socket_target(next_url):
                raise requests.ConnectionError("Connection refused")

            current_url = normalize_local_target_url(next_url)
            continue

        if upstream_status is not None:
            response.status_code = upstream_status
        response.history = history
        return response


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/flag")
def show_flag():
    allowed_internal_hosts = {"127.0.0.1", "localhost", "::1"}
    host_without_port = request.host.split(":")[0].strip("[]").lower()
    if host_without_port not in allowed_internal_hosts or ":" in request.host:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"flag": FLAG}), 200


@app.get("/flag.txt")
def show_flag_txt():
    allowed_internal_hosts = {"127.0.0.1", "localhost", "::1"}
    host_without_port = request.host.split(":")[0].strip("[]").lower()
    if host_without_port not in allowed_internal_hosts or ":" in request.host:
        return "Not found", 404
    return FLAG, 200


@app.get("/check")
def check_website():
    target_url = request.args.get("url", "").strip()

    if not target_url:
        return jsonify({"error": "Missing query parameter: url"}), 400

    if not target_url.startswith(("http://", "https://")):
        return jsonify({"error": "URL must start with http:// or https://"}), 400

    if is_blocked_target(target_url):
        return jsonify({
            "url": target_url,
            "status": "up",
            "http_response": "HTTP/200",
        }), 200

    request_url = normalize_local_target_url(target_url)
    app.logger.info("Starting URL check: target=%s request_url=%s", target_url, request_url)
    session = requests.Session()
    session.verify = False

    try:
        response = fetch_with_redirects(session, request_url)
    except requests.RequestException as exc:
        app.logger.exception("URL check failed: target=%s error=%s", target_url, exc)
        xml_body = build_error_xml(target_url, str(exc), reason="RequestException")
        return Response(xml_body, status=500, mimetype="application/xml")

    if response.history:
        app.logger.info("Redirect chain for target=%s", target_url)
        for idx, hop in enumerate(response.history, start=1):
            app.logger.info(
                "  hop=%d status=%s location=%s url=%s",
                idx,
                hop.status_code,
                hop.headers.get("Location", ""),
                hop.url,
            )

    app.logger.info(
        "Final upstream response: target=%s status=%s url=%s",
        target_url,
        response.status_code,
        response.url,
    )

    headers_xml = "".join(
        f"<header name=\"{escape(key)}\">{escape(value)}</header>"
        for key, value in response.headers.items()
    )

    if response.status_code == 200:
        return jsonify({
            "url": target_url,
            "status": "up",
            "http_response": "HTTP/200",
        }), 200

    xml_body = build_error_xml(
        target_url,
        response.text,
        headers=headers_xml,
        reason=response.reason or "",
    )
    return Response(xml_body, status=500, mimetype="application/xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4016)
