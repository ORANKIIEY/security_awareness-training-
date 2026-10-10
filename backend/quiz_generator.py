import random
import string

from password_checker import analyze_password, estimate_crack_time, calculate_entropy
from quiz_data import QUIZ_QUESTIONS

BRANDS = [
    ("PayPal", "paypal.com"),
    ("Microsoft", "microsoft.com"),
    ("Amazon", "amazon.com"),
    ("Netflix", "netflix.com"),
    ("Apple", "apple.com"),
    ("Google", "google.com"),
    ("DHL", "dhl.com"),
    ("LinkedIn", "linkedin.com"),
    ("Dropbox", "dropbox.com"),
    ("Chase", "chase.com"),
]

PATHS = ["signin", "account/security", "login", "billing", "help/contact", "settings"]
LURE_WORDS = ["account-verify", "secure-login", "support-center", "billing-update", "id-confirm", "auth-check", "service-desk"]
LURE_TLDS = [".net", ".top", ".xyz", ".info", ".online", ".site"]
WORDS = ["copper", "lantern", "orbit", "maple", "violet", "harbor", "pixel", "thunder", "marble", "canyon",
         "falcon", "velvet", "ember", "glacier", "meadow", "rocket", "saffron", "tundra", "willow", "zephyr"]
COMMON_BASES = ["Summer", "Password", "Welcome", "Football", "Dragon", "Monkey", "Sunshine", "Princess"]
FILE_BASES = ["Invoice_4821", "Payslip_October", "Shipping_Label", "Contract_Final", "Scan_0093", "Order_Details", "HR_Policy_Update"]
SAFE_EXTS = [".pdf", ".jpg", ".png", ".txt", ".docx", ".xlsx"]
DANGEROUS = [(".pdf.exe", "a program disguised as a PDF with a double extension"),
             (".exe", "a Windows program that runs as soon as it's opened"),
             (".scr", "a screensaver file, which is really an executable program"),
             (".js", "a script that Windows can run directly"),
             (".iso", "a disk image that can hide programs and bypass some security checks"),
             (".docm", "a Word document with macros that can run code"),
             (".html", "a local web page often used to show a fake login form")]
PHISH_SUBJECTS = [
    "URGENT: Your {brand} account will be suspended in 24 hours",
    "Action required: verify your {brand} payment details",
    "Final notice: unusual sign-in detected on your {brand} account",
    "Your {brand} password expires today - confirm now",
    "{brand}: Refund pending, confirm your bank details",
]
SAFE_SUBJECTS = [
    "Your {brand} receipt for order #{num}",
    "{brand} newsletter: what's new this month",
    "Reminder: team meeting moved to Thursday",
    "Your {brand} monthly statement is available in the app",
    "Thanks for your feedback",
    "Lunch on Friday?",
]


def lookalike(domain: str, rng: random.Random) -> str:
    name, tld = domain.rsplit(".", 1)
    swaps = [("l", "1"), ("o", "0"), ("i", "l"), ("m", "rn"), ("e", "3"), ("a", "4")]
    rng.shuffle(swaps)
    for real, fake in swaps:
        if real in name:
            idx = name.index(real)
            return f"{name[:idx]}{fake}{name[idx + len(real):]}.{tld}"
    idx = rng.randrange(len(name))
    return f"{name[:idx]}{name[idx]}{name[idx:]}.{tld}"


def lure_domain(rng: random.Random) -> str:
    return rng.choice(LURE_WORDS) + rng.choice(LURE_TLDS)


def gen_real_link(rng):
    brand, domain = rng.choice(BRANDS)
    name = domain.split(".")[0]
    path = rng.choice(PATHS)
    lure = lure_domain(rng)
    fake = lookalike(domain, rng)
    correct = f"https://www.{domain}/{path}"
    wrong = [
        f"https://{domain}.{lure}/{path}",
        f"https://{fake}/{path}",
        f"https://{name}-{rng.choice(['secure', 'login', 'support', 'verify'])}.com/{path}",
    ]
    return {
        "topic": "Phishing",
        "question": f"Which of these links really belongs to {brand}?",
        "correct": correct,
        "wrong": wrong,
        "explanation": f"Only {domain} belongs to {brand}. Read the domain just before the first single slash: "
                       f"'{domain}.{lure}' is really owned by {lure}, '{fake}' swaps letters to imitate the name, "
                       f"and adding words like '-secure' creates a completely different domain.",
    }


def gen_where_does_it_go(rng):
    brand, domain = rng.choice(BRANDS)
    evil = lure_domain(rng)
    url = f"https://{domain}.{evil}/{rng.choice(PATHS)}"
    return {
        "topic": "Phishing",
        "question": f"An email says 'Log in to {brand}' and links to {url}. Which website would actually open?",
        "correct": evil,
        "wrong": [domain, f"www.{domain}", f"login.{domain}"],
        "explanation": f"The real domain is the part right before the first single slash: {evil}. "
                       f"Putting '{domain}' at the start is just a subdomain the attacker chose to look trustworthy.",
    }


def gen_fake_sender(rng):
    brand, domain = rng.choice(BRANDS)
    name = domain.split(".")[0]
    mailbox = rng.choice(["support", "no-reply", "security", "billing"])
    correct = f"{mailbox}@{domain}"
    wrong = [
        f"{mailbox}@{lookalike(domain, rng)}",
        f"{name}.{mailbox}@gmail.com",
        f"{mailbox}@{name}-{rng.choice(['help', 'alerts', 'service'])}.com",
    ]
    return {
        "topic": "Phishing",
        "question": f"You get an email that claims to be from {brand}. Which sender address is genuine?",
        "correct": correct,
        "wrong": wrong,
        "explanation": f"Genuine {brand} mail comes from @{domain}. Look-alike spellings, extra words in the domain, "
                       f"and free providers like Gmail are all signs of impersonation, even if the display name says '{brand}'.",
    }


def gen_strongest_password(rng):
    passphrase = "-".join(rng.sample(WORDS, 4)) + str(rng.randint(10, 99))
    candidates = [
        f"{rng.choice(COMMON_BASES)}{rng.randint(2018, 2026)}!",
        rng.choice(["P@ssw0rd1", "Adm1n!23", "Qwerty!9", "L3tm3in!"]),
        rng.choice(["qwertyuiop", "1q2w3e4r5t", "asdfghjkl1", "zxcvbnm123"]),
    ]
    best = max(candidates, key=lambda p: analyze_password(p)["score"])
    crack = estimate_crack_time(calculate_entropy(passphrase))
    return {
        "topic": "Passwords",
        "question": "Which password would be hardest for an attacker to crack?",
        "correct": passphrase,
        "wrong": candidates,
        "explanation": f"'{passphrase}' is {len(passphrase)} characters of random words (estimated crack time: {crack.lower()}). "
                       f"The others are short or built from common words, years, keyboard rows or predictable swaps "
                       f"like @ for a. Attackers try those patterns first, so even '{best}' falls quickly.",
    }


def gen_dangerous_attachment(rng):
    bases = rng.sample(FILE_BASES, 4)
    ext, why = rng.choice(DANGEROUS)
    safe_exts = rng.sample(SAFE_EXTS, 3)
    correct = bases[0] + ext
    return {
        "topic": "Phishing",
        "question": "Which attachment from an unexpected email is the most dangerous to open?",
        "correct": correct,
        "wrong": [b + e for b, e in zip(bases[1:], safe_exts)],
        "explanation": f"'{correct}' is {why}. Only the last extension counts. Unexpected attachments are worth "
                       f"checking with the sender, but executable and macro files are the ones that can infect your device.",
    }


def gen_phishy_subject(rng):
    brand, _ = rng.choice(BRANDS)
    num = rng.randint(100000, 999999)
    phish = rng.choice(PHISH_SUBJECTS).format(brand=brand)
    safe = [s.format(brand=brand, num=num) for s in rng.sample(SAFE_SUBJECTS, 3)]
    return {
        "topic": "Phishing",
        "question": "Which email subject line is most likely to be phishing?",
        "correct": phish,
        "wrong": safe,
        "explanation": "Phishing subjects create pressure: deadlines, threats of suspension, or requests to confirm payment "
                       "or bank details. Legitimate messages rarely demand urgent action through a link.",
    }


def gen_raw_ip(rng):
    brand, domain = rng.choice(BRANDS)
    ip = f"{rng.randint(45, 210)}.{rng.randint(0, 255)}.{rng.randint(0, 255)}.{rng.randint(1, 254)}"
    path = rng.choice(PATHS)
    return {
        "topic": "Websites",
        "question": f"A '{brand}' login page asks for your password. Which address should make you stop immediately?",
        "correct": f"http://{ip}/{path}",
        "wrong": [f"https://www.{domain}/{path}", f"https://{domain}/{path}", f"https://accounts.{domain}/{path}"],
        "explanation": f"Real login pages use the company's domain over HTTPS. A raw IP address ({ip}) with plain http:// "
                       f"is unencrypted and hides who runs the server.",
    }


# Hand-written questions that ask the same thing as a generator, so a quiz never repeats itself.
COVERED_BY_GENERATORS = {"pw-length", "ph-domain", "ph-attachment"}

GENERATORS = [gen_real_link, gen_where_does_it_go, gen_fake_sender, gen_strongest_password,
              gen_dangerous_attachment, gen_phishy_subject, gen_raw_ip]


def _finalize(item: dict, rng: random.Random, idx: int, kind: str) -> dict:
    options = [item["correct"], *item["wrong"]]
    rng.shuffle(options)
    return {
        "id": f"gen-{kind}-{idx}-{''.join(rng.choices(string.ascii_lowercase, k=4))}",
        "topic": item["topic"],
        "question": item["question"],
        "options": options,
        "answer": options.index(item["correct"]),
        "explanation": item["explanation"],
        "generated": True,
    }


def generate_quiz(count: int = 10, seed: int | None = None) -> list[dict]:
    rng = random.Random(seed)
    count = max(4, min(count, 20))

    generated_count = round(count * 0.6)
    kinds = []
    while len(kinds) < generated_count:
        batch = GENERATORS[:]
        rng.shuffle(batch)
        kinds.extend(batch)
    questions = [_finalize(gen(rng), rng, i, gen.__name__[4:]) for i, gen in enumerate(kinds[:generated_count])]

    fixed_pool = [q for q in QUIZ_QUESTIONS if q["id"] not in COVERED_BY_GENERATORS]
    questions += rng.sample(fixed_pool, min(count - generated_count, len(fixed_pool)))
    rng.shuffle(questions)
    return questions
