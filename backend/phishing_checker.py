import re
from urllib.parse import urlparse

# Keywords and regex patterns for phishing detection
URGENCY_PATTERNS = [
    (r'\b(immediately|urgent(?:ly)?|action required|suspended|suspension|terminated|termination|within \d+ hours|account (?:locked|disabled)|final notice|expires? (?:today|soon|in \d+ hours?)|will expire)\b',
     "Pressure or threat language"),
    (r'\b(verify your (?:account|identity|credentials|password)|confirm (?:your )?identity|update your (?:payment|billing|banking) (?:details|information)|re-?activate|unauthori[sz]ed (?:activity|access|login)|suspicious activity)\b',
     "Asks you to verify or update account details"),
    (r'\b(wire transfer|gift cards?|crypto(?:currency)?|bitcoin|payroll update|direct deposit|bank(?:ing)? details|updated bank account)\b',
     "Money or payment request"),
    (r'\b(click here|click below|click the (?:link|button) below|log ?in now|sign in now|access (?:your )?account)\b',
     "Pushes you to click a link"),
]

SUSPICIOUS_TLDS = {'.top', '.xyz', '.click', '.club', '.work', '.info', '.live', '.cc', '.buzz', '.gq', '.cf', '.tk'}
FREE_EMAIL_DOMAINS = {'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com', 'mail.com', 'protonmail.com', 'icloud.com', 'gmx.com'}

# Brand name -> domains it legitimately sends mail / hosts links from
BRANDS = {
    'paypal': ['paypal.com'],
    'microsoft': ['microsoft.com', 'live.com', 'office.com', 'microsoftonline.com', 'outlook.com'],
    'office365': ['microsoft.com', 'office.com', 'microsoftonline.com'],
    'google': ['google.com', 'gmail.com', 'youtube.com'],
    'apple': ['apple.com', 'icloud.com'],
    'amazon': ['amazon.com', 'amazon.co.uk', 'amazon.de', 'amazonaws.com'],
    'netflix': ['netflix.com'],
    'chase': ['chase.com'],
    'wellsfargo': ['wellsfargo.com'],
    'dhl': ['dhl.com'],
    'fedex': ['fedex.com'],
    'ups': ['ups.com'],
    'docusign': ['docusign.com', 'docusign.net'],
}

BRAND_NAMES = {'paypal': 'PayPal', 'office365': 'Office 365', 'wellsfargo': 'Wells Fargo', 'dhl': 'DHL',
               'fedex': 'FedEx', 'ups': 'UPS', 'docusign': 'DocuSign'}


def brand_name(brand: str) -> str:
    return BRAND_NAMES.get(brand, brand.title())


HOMOGLYPHS = [('rn', 'm'), ('vv', 'w'), ('0', 'o'), ('1', 'l'), ('3', 'e'), ('5', 's'), ('@', 'a')]

DANGEROUS_EXTENSIONS = r'exe|scr|vbs|bat|cmd|iso|img|zip|rar|7z|docm|xlsm|pptm|js|jar|hta|lnk|msi'


def extract_urls(text: str) -> list:
    """Extracts URLs and href targets from plain text, Markdown or basic HTML"""
    urls = []
    for link in re.findall(r'https?://[^\s<>"\'\]\)]+|www\.[^\s<>"\'\]\)]+', text):
        urls.append(link.rstrip('.,;:!?'))
    return list(dict.fromkeys(urls))


def extract_link_pairs(text: str) -> list:
    """Returns (visible_text, real_target) pairs for HTML anchors and Markdown links"""
    pairs = re.findall(r'<a\s[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', text, re.IGNORECASE | re.DOTALL)
    pairs = [(re.sub(r'<[^>]+>', '', label).strip(), href) for href, label in pairs]
    pairs += [(label.strip(), href) for label, href in re.findall(r'\[([^\]]+)\]\((https?://[^)\s]+)\)', text)]
    return pairs


def host_of(url: str) -> str:
    parsed = urlparse(url if re.match(r'^https?://', url, re.I) else f'http://{url}')
    return (parsed.hostname or '').lower()


def base_domain(host: str) -> str:
    parts = host.split('.')
    if len(parts) >= 3 and len(parts[-1]) == 2 and parts[-2] in ('co', 'com', 'org', 'net', 'ac', 'gov'):
        return '.'.join(parts[-3:])
    return '.'.join(parts[-2:])


def is_domain_of(host: str, domains: list) -> bool:
    return any(host == d or host.endswith('.' + d) for d in domains)


def deglyph(text: str) -> str:
    for fake, real in HOMOGLYPHS:
        text = text.replace(fake, real)
    return text


def find_impersonated_brand(host: str):
    """Returns (brand, technique) if the host imitates a known brand without belonging to it."""
    if any(is_domain_of(host, domains) for domains in BRANDS.values()):
        return None
    tokens = re.split(r'[.\-]', host)
    flat = ''.join(tokens)
    for brand in BRANDS:
        # Short names ("ups", "chase") appear inside ordinary words, so require a whole label for them.
        if len(brand) >= 6:
            if brand in flat:
                return brand, "contains"
            if brand in deglyph(flat):
                return brand, "lookalike"
        else:
            if brand in tokens:
                return brand, "contains"
            if brand in (deglyph(t) for t in tokens):
                return brand, "lookalike"
    return None


def analyze_phishing_email(email_body: str, subject: str = "", sender: str = "", headers: str = "") -> dict:
    red_flags = []
    highlights = []
    score = 0

    def flag(category, severity, detail, points):
        nonlocal score
        score += points
        red_flags.append({"category": category, "severity": severity, "detail": detail})

    combined_text = f"{subject}\n{email_body}"
    sender_domain = ""

    # 1. Sender analysis
    if sender:
        sender_clean = sender.strip()
        email_match = re.search(r'<([^>]+)>', sender_clean)
        display_name = sender_clean.split('<')[0].strip().strip('"').lower() if email_match else ""
        actual_email = (email_match.group(1) if email_match else sender_clean).strip().lower()
        sender_domain = actual_email.split('@')[-1] if '@' in actual_email else ""

        if sender_domain:
            for brand, domains in BRANDS.items():
                if re.search(rf'\b{brand}\b', display_name.replace('wells fargo', 'wellsfargo')) and not is_domain_of(sender_domain, domains):
                    flag("Sender impersonation", "Critical",
                         f"The display name says '{brand_name(brand)}', but the email actually comes from @{sender_domain}.", 35)
                    break

            impersonation = find_impersonated_brand(sender_domain)
            if impersonation and impersonation[1] == "lookalike":
                flag("Look-alike sender domain", "Critical",
                     f"@{sender_domain} is spelled to look like {brand_name(impersonation[0])} (letters swapped for numbers or similar shapes).", 35)

            if any(sender_domain.endswith(tld) for tld in SUSPICIOUS_TLDS):
                flag("Suspicious sender domain", "High",
                     f"@{sender_domain} uses a top-level domain that is cheap to register and common in phishing.", 20)

            corporate_terms = ['password', 'invoice', 'payroll', 'security', 'account', 'hr ', 'it support', 'helpdesk', 'bank']
            if sender_domain in FREE_EMAIL_DOMAINS and any(t in combined_text.lower() or t in display_name for t in corporate_terms):
                flag("Official notice from a personal email", "High",
                     f"This reads like an official company or bank message, but was sent from a free @{sender_domain} account.", 25)

    # 2. Pressure and coercion language
    for pattern, description in URGENCY_PATTERNS:
        matches = re.findall(pattern, combined_text, re.IGNORECASE)
        if matches:
            matched_words = list(dict.fromkeys(m if isinstance(m, str) else m[0] for m in matches))
            quoted = ', '.join(f'"{w}"' for w in matched_words)
            flag("Pressure tactics", "Medium", f"{description}: {quoted}", min(30, len(matched_words) * 10))
            highlights.extend(matched_words)

    # 3. Link inspection
    urls = extract_urls(email_body)
    link_domains = set()
    for url in urls:
        host = host_of(url)
        if not host:
            continue

        if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', host):
            flag("Link to a raw IP address", "Critical",
                 f"{url} points to an IP address instead of a named website. Legitimate companies almost never do this.", 40)
            continue

        link_domains.add(base_domain(host))
        impersonation = find_impersonated_brand(host)
        if impersonation:
            brand, technique = impersonation
            how = "is spelled to look like" if technique == "lookalike" else "uses the name"
            flag("Fake brand domain", "Critical",
                 f"{host} {how} {brand_name(brand)} but is not an official {brand_name(brand)} domain.", 35)

        if any(host.endswith(tld) for tld in SUSPICIOUS_TLDS):
            flag("High-risk link domain", "Medium", f"{host} uses a top-level domain common in phishing.", 15)

        if host.count('.') >= 3:
            flag("Long, layered link domain", "Medium",
                 f"{host} has many subdomains, a common trick to make a link look official at a glance.", 10)

    for label, href in extract_link_pairs(email_body):
        label_host = host_of(label) if re.match(r'^(https?://|www\.)\S+$', label, re.I) else ""
        if label_host and base_domain(label_host) != base_domain(host_of(href)):
            flag("Link text hides the real address", "Critical",
                 f"The link shows \"{label}\" but actually opens {host_of(href)}.", 35)

    if sender_domain and link_domains and sender_domain not in FREE_EMAIL_DOMAINS:
        foreign = sorted(d for d in link_domains if d != base_domain(sender_domain))
        if foreign and len(foreign) == len(link_domains):
            flag("Links don't match the sender", "Medium",
                 f"Sent from @{sender_domain}, but every link goes somewhere else ({', '.join(foreign[:3])}).", 10)

    # 4. Attachments
    attachment_matches = re.findall(rf'\b[\w-]+\.({DANGEROUS_EXTENSIONS})\b', email_body, re.IGNORECASE)
    if attachment_matches:
        exts = ', '.join(sorted({'.' + a.lower() for a in attachment_matches}))
        flag("Dangerous attachment type", "Critical",
             f"Mentions a file type that can run code or hide malware ({exts}). Invoices and documents should be PDFs.", 35)
    if re.search(r'\.(pdf|docx?|xlsx?|jpg|png)\.(exe|scr|js|vbs|bat|cmd|hta)\b', email_body, re.IGNORECASE):
        flag("Disguised file extension", "Critical",
             "A file name uses a double extension (e.g. invoice.pdf.exe) to disguise a program as a document.", 20)

    # 5. Headers
    if headers:
        h = headers.lower()
        if "spf=fail" in h or "spf=softfail" in h:
            flag("SPF check failed", "High", "The sending server isn't authorized to send mail for this domain.", 30)
        if "dkim=fail" in h:
            flag("DKIM check failed", "High", "The email's digital signature doesn't verify, so it may have been forged or altered.", 30)
        if "dmarc=fail" in h:
            flag("DMARC check failed", "High", "The domain's own anti-spoofing policy rejected this message.", 30)
        reply_to = re.search(r'^reply-to:.*?@([\w.-]+)', headers, re.IGNORECASE | re.MULTILINE)
        if reply_to and sender_domain and base_domain(reply_to.group(1).lower()) != base_domain(sender_domain):
            flag("Reply-To goes elsewhere", "High",
                 f"Replies would go to @{reply_to.group(1).lower()}, not the sender's domain @{sender_domain}.", 25)

    score = min(100, max(0, score))

    if score >= 70:
        risk_level, badge_color = "Very likely phishing", "danger"
    elif score >= 45:
        risk_level, badge_color = "Likely phishing", "warning"
    elif score >= 20:
        risk_level, badge_color = "Be cautious", "info"
    else:
        risk_level, badge_color = "No strong warning signs", "success"

    if score >= 45:
        recommendations = [
            "Don't click any links or open attachments in this email.",
            "If it claims to be from someone you know, contact them using a phone number or address you already have, not one in the email.",
            "Report it to your IT or security team, then delete it.",
        ]
    elif score >= 20:
        recommendations = [
            "Hover over links before clicking and check the real address matches the company.",
            "If you're asked to log in, go to the website directly instead of using the link.",
        ]
    else:
        recommendations = [
            "Nothing obvious stands out, but automated checks can miss targeted attacks.",
            "Still be careful with unexpected requests for money, passwords or personal details.",
        ]

    return {
        "score": score,
        "risk_level": risk_level,
        "badge_color": badge_color,
        "red_flags_count": len(red_flags),
        "red_flags": red_flags,
        "detected_urls": urls,
        "highlighted_keywords": list(dict.fromkeys(highlights)),
        "recommendations": recommendations,
    }
