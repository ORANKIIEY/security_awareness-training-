import ssl
import socket
import asyncio
import ipaddress
import datetime
from urllib.parse import urlparse
import httpx

SUSPICIOUS_TLDS = {'.top', '.xyz', '.click', '.club', '.work', '.info', '.live', '.cc', '.buzz', '.gq', '.cf', '.tk'}

SECURITY_HEADERS = [
    ("strict-transport-security", "Strict-Transport-Security (HSTS)", 10,
     "Tells browsers to only ever connect over HTTPS.",
     "Missing. Browsers may still try plain HTTP first, which can be intercepted."),
    ("content-security-policy", "Content-Security-Policy", 10,
     "Restricts which scripts and resources the page may load.",
     "Missing. Injected scripts (XSS) are much harder to contain."),
    ("x-frame-options", "X-Frame-Options", 5,
     "Prevents the site being embedded in another page (clickjacking).",
     "Missing. The page can be framed by other sites to trick users into clicking."),
    ("x-content-type-options", "X-Content-Type-Options", 5,
     "Stops browsers guessing file types (MIME sniffing).",
     "Missing. Browsers may interpret uploaded files as executable content."),
    ("referrer-policy", "Referrer-Policy", 0,
     "Limits what URL information is leaked to other sites.",
     "Not set. Browser default applies."),
]


class WebsiteCheckError(Exception):
    """Raised for input the checker cannot or should not inspect."""


def normalize_target(raw: str) -> tuple[str, str, str, int]:
    url = raw.strip()
    if not url:
        raise WebsiteCheckError("Enter a website address, for example example.com.")
    if any(c.isspace() for c in url):
        raise WebsiteCheckError("A web address can't contain spaces.")
    if '://' not in url:
        url = 'https://' + url

    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    if scheme not in ('http', 'https'):
        raise WebsiteCheckError("Only http:// and https:// addresses can be checked.")

    hostname = (parsed.hostname or '').rstrip('.').lower()
    if not hostname:
        raise WebsiteCheckError("That doesn't look like a valid web address.")

    try:
        port = parsed.port or (443 if scheme == 'https' else 80)
    except ValueError:
        raise WebsiteCheckError("The port number in that address is invalid.")

    is_ip = _parse_ip(hostname) is not None
    if not is_ip and '.' not in hostname:
        raise WebsiteCheckError("Include the full domain, for example example.com.")

    return url, scheme, hostname, port


def _parse_ip(host: str):
    try:
        return ipaddress.ip_address(host.strip('[]'))
    except ValueError:
        return None


async def resolve_host(hostname: str) -> list[str]:
    try:
        infos = await asyncio.to_thread(socket.getaddrinfo, hostname, None)
    except socket.gaierror:
        raise WebsiteCheckError(f"Couldn't find '{hostname}'. Check the spelling, or the domain may not exist.")

    addresses = sorted({info[4][0] for info in infos})
    for addr in addresses:
        ip = ipaddress.ip_address(addr)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_unspecified:
            raise WebsiteCheckError("This checker only inspects public websites, not local or private network addresses.")
    return addresses


def inspect_ssl_certificate(hostname: str, port: int = 443) -> dict:
    """Performs a verified TLS handshake and reports certificate details."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=5.0) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                version = ssock.version()

        expires_ts = ssl.cert_time_to_seconds(cert['notAfter'])
        expires = datetime.datetime.fromtimestamp(expires_ts, tz=datetime.timezone.utc)
        days_left = (expires - datetime.datetime.now(datetime.timezone.utc)).days

        issuer = dict(x[0] for x in cert.get('issuer', ()) if x)
        issuer_name = issuer.get('organizationName') or issuer.get('commonName') or "Unknown issuer"

        san_list = [value for kind, value in cert.get('subjectAltName', []) if kind == 'DNS']

        return {
            "valid": True,
            "issuer": issuer_name,
            "version": version,
            "cipher": cipher[0] if cipher else "Unknown",
            "days_remaining": days_left,
            "valid_until": expires.strftime('%Y-%m-%d'),
            "san_count": len(san_list),
            "san_sample": san_list[:5],
            "error": None,
        }
    except ssl.SSLCertVerificationError as e:
        error = e.verify_message or str(e)
    except (socket.timeout, TimeoutError):
        error = "Connection timed out on port 443."
    except ConnectionRefusedError:
        error = "The server refused connections on port 443 (no HTTPS)."
    except Exception as e:
        error = str(e) or e.__class__.__name__

    return {
        "valid": False,
        "issuer": "N/A",
        "version": "N/A",
        "cipher": "N/A",
        "days_remaining": 0,
        "valid_until": "N/A",
        "san_count": 0,
        "san_sample": [],
        "error": error,
    }


async def probe_http(url: str, verify: bool) -> dict:
    """Requests the page (following redirects) and returns final URL and response headers."""
    headers = {"User-Agent": "Mozilla/5.0 (SecurityAwarenessChecker)"}
    async with httpx.AsyncClient(timeout=8.0, follow_redirects=True, verify=verify, headers=headers) as client:
        async with client.stream("GET", url) as resp:
            return {
                "final_url": str(resp.url),
                "status_code": resp.status_code,
                "headers": {k.lower(): v for k, v in resp.headers.items()},
                "redirects": [str(r.url) for r in resp.history],
            }


def _grade(score: int) -> tuple[str, str]:
    if score >= 90:
        return "A+", "success"
    if score >= 80:
        return "A", "success"
    if score >= 70:
        return "B", "info"
    if score >= 55:
        return "C", "warning"
    if score >= 40:
        return "D", "warning"
    return "F", "danger"


async def inspect_website_security(raw_url: str) -> dict:
    url, scheme, hostname, port = normalize_target(raw_url)
    addresses = await resolve_host(hostname)

    score = 100
    risk_factors = []
    checks = []

    # Domain heuristics
    if _parse_ip(hostname):
        score -= 20
        checks.append({"name": "Domain name", "status": "WARN",
                       "detail": "The site is addressed by a raw IP instead of a domain name. Legitimate services rarely do this."})
        risk_factors.append("Raw IP address used instead of a domain name.")
    elif hostname.count('.') > 3:
        score -= 10
        checks.append({"name": "Domain name", "status": "WARN",
                       "detail": f"Unusually deep subdomain ({hostname}). Phishing sites often hide a brand name inside long subdomains."})
        risk_factors.append("Unusually deep subdomain structure.")

    if any(hostname.endswith(tld) for tld in SUSPICIOUS_TLDS):
        score -= 10
        tld = hostname.rsplit('.', 1)[-1]
        checks.append({"name": "Top-level domain", "status": "WARN",
                       "detail": f".{tld} domains are cheap to register and disproportionately used for phishing."})
        risk_factors.append(f"High-risk top-level domain (.{tld}).")

    # TLS certificate (always check port 443, even if the user typed http://)
    https_port = port if scheme == 'https' else 443
    ssl_info = await asyncio.to_thread(inspect_ssl_certificate, hostname, https_port)
    https_available = ssl_info["valid"]
    error_text = ssl_info["error"] or ""
    https_refused = not https_available and ("refused" in error_text or "timed out" in error_text)

    if ssl_info["valid"]:
        if ssl_info["days_remaining"] < 15:
            score -= 10
            checks.append({"name": "TLS certificate", "status": "WARN",
                           "detail": f"Valid, but expires in {ssl_info['days_remaining']} days ({ssl_info['valid_until']})."})
        else:
            checks.append({"name": "TLS certificate", "status": "PASS",
                           "detail": f"Valid certificate from {ssl_info['issuer']}, expires {ssl_info['valid_until']}."})
    else:
        score -= 35 if https_refused else 45
        checks.append({"name": "TLS certificate", "status": "FAIL",
                       "detail": f"{'No HTTPS available' if https_refused else 'Certificate is not trusted'}: {error_text}"})
        risk_factors.append("HTTPS is unavailable." if https_refused else "The TLS certificate is invalid; browsers will show a security warning.")

    # Live HTTP probe. If the user typed a bare domain and HTTPS is down, fall back to HTTP.
    probe_url = url
    if scheme == 'https' and https_refused and "://" not in raw_url:
        probe_url = f"http://{hostname}"
    probe = None
    probe_error = None
    try:
        probe = await probe_http(probe_url, verify=https_available)
    except httpx.TimeoutException:
        probe_error = "The site took too long to respond."
    except httpx.HTTPError as e:
        probe_error = str(e) or e.__class__.__name__

    final_url = probe["final_url"] if probe else probe_url
    final_scheme = urlparse(final_url).scheme

    # Encryption in transit
    if final_scheme == 'https' and https_available:
        if urlparse(probe_url).scheme == 'http':
            checks.insert(0, {"name": "HTTPS", "status": "PASS",
                              "detail": "Plain HTTP requests are redirected to HTTPS."})
        else:
            checks.insert(0, {"name": "HTTPS", "status": "PASS",
                              "detail": "The site is served over an encrypted HTTPS connection."})
    elif final_scheme == 'https' and probe:
        checks.insert(0, {"name": "HTTPS", "status": "FAIL",
                          "detail": "The site uses HTTPS, but with an untrusted certificate, so the connection can't be verified."})
    elif final_scheme == 'http' and probe:
        score -= 30 if https_available else 0
        checks.insert(0, {"name": "HTTPS", "status": "FAIL",
                          "detail": "The site is served over plain HTTP. Anything typed into it, including passwords, can be read in transit."})
        risk_factors.append("Pages are served unencrypted over HTTP.")
    elif not probe:
        checks.insert(0, {"name": "HTTPS", "status": "WARN",
                          "detail": "Couldn't confirm how the site is served because it did not respond."})

    # Security headers
    header_info = {}
    if probe:
        headers = probe["headers"]
        for key, label, penalty, good, bad in SECURITY_HEADERS:
            if key == "strict-transport-security" and final_scheme != "https":
                continue
            if key in headers:
                checks.append({"name": label, "status": "PASS", "detail": f"{good} Value: {headers[key][:120]}"})
            else:
                score -= penalty
                checks.append({"name": label, "status": "WARN" if penalty else "INFO", "detail": bad})

        header_info = {
            "server": headers.get('server', 'Not disclosed'),
            "status_code": probe["status_code"],
            "final_url": final_url,
            "redirects": probe["redirects"],
            "hsts": 'strict-transport-security' in headers,
            "csp": 'content-security-policy' in headers,
            "x_frame": headers.get('x-frame-options', 'Missing'),
            "x_content_type": headers.get('x-content-type-options', 'Missing'),
        }
    else:
        score -= 10
        checks.append({"name": "Response headers", "status": "WARN",
                       "detail": f"Couldn't load the page to read its headers: {probe_error}"})

    score = max(0, min(100, score))
    grade, badge_color = _grade(score)
    if probe is None and grade not in ("D", "F"):
        grade, badge_color = "?", "info"

    return {
        "url": url,
        "final_url": final_url,
        "hostname": hostname,
        "ip_addresses": addresses[:4],
        "score": score,
        "grade": grade,
        "badge_color": badge_color,
        "reachable": probe is not None,
        "ssl_info": ssl_info,
        "header_info": header_info,
        "security_checks": checks,
        "risk_factors": risk_factors,
    }
