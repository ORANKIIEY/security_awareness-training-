import random


ORGANIZATIONS = [
    ("Northstar", "northstar.example"),
    ("Cedar", "cedar.example"),
    ("Harbor", "harbor.example"),
    ("Nimbus", "nimbus.example"),
    ("Acme", "acme.example"),
    ("Summit", "summit.example"),
]


def generate_scenarios(seed: int) -> list[dict]:
    rng = random.Random(seed)
    company, domain = rng.choice(ORGANIZATIONS)
    deadline = rng.choice(["two hours", "the end of today", "before your next sign-in"])
    payroll_day = rng.choice(["Friday", "the next pay cycle", "the end of this week"])
    invoice = rng.randint(1200, 9800)
    tracking_id = f"TRAIN-{rng.randint(100000, 999999)}"
    meeting_day = rng.choice(["Tuesday", "Wednesday", "Thursday"])
    meeting_time = rng.choice(["10:00 AM", "1:30 PM", "2:00 PM"])
    sign_in_location = rng.choice(["Berlin", "Dublin", "Toronto"])

    scenarios = [
        {
            "id": f"generated-{seed}-password-reset",
            "title": f"{company} Password Verification Request",
            "category": "Credential Harvesting",
            "is_phishing": True,
            "sender": f"{company} IT Support <security@{company.lower()}-help.example.com>",
            "subject": rng.choice([
                "ACTION REQUIRED: Verify your account",
                "Your password needs immediate attention",
                "Security notice: confirm your sign-in",
            ]),
            "preview": f"Verify your account {deadline} to avoid interruption.",
            "content": (
                f"Hello {company} employee,\n\nOur security system detected an issue with your account. "
                f"You must verify your password {deadline} or your access will be suspended.\n\n"
                f"[Verify your account](https://example.com/account/verify)\n\n"
                f"Do not ignore this notice.\n\n{company} IT Support"
            ),
            "red_flags": [
                {"title": "Lookalike sender domain", "explanation": f"The sender uses {company.lower()}-help.example.com rather than the organization's {domain} domain."},
                {"title": "Urgency and threat", "explanation": f"The short {deadline} deadline and threat of suspension pressure the reader to act without checking."},
                {"title": "Unexpected password link", "explanation": "The message asks you to verify a password through a link on example.com. Open the official service directly instead."},
            ],
            "safe_signals": [],
            "psychology_note": "Urgency and fear of losing access are used to short-circuit careful verification.",
        },
        {
            "id": f"generated-{seed}-payroll-update",
            "title": f"{company} Payroll Details Update",
            "category": "Financial Fraud / Payroll",
            "is_phishing": True,
            "sender": f"Payroll Team <payroll-update@{company.lower()}-people.example.com>",
            "subject": f"Confirm your pay details before {payroll_day}",
            "preview": "Confirm your bank details to avoid a delay to your pay.",
            "content": (
                f"Hello team,\n\nWe are updating our payroll records. Please confirm your direct deposit details "
                f"before {payroll_day} so your next payment is not delayed.\n\n"
                f"[Review payroll details](https://example.com/payroll/review)\n\n"
                f"Thank you,\n{company} Payroll"
            ),
            "red_flags": [
                {"title": "Sensitive financial information", "explanation": "The email directs employees to a link to review bank details, which should be handled through a known payroll portal."},
                {"title": "Pressure tied to payday", "explanation": f"The warning about delayed pay before {payroll_day} pressures the recipient to act quickly."},
                {"title": "Unverified sender and link", "explanation": f"The sender domain does not match {domain}; the link goes to example.com rather than an official payroll portal."},
            ],
            "safe_signals": [],
            "psychology_note": "Fear of missing a paycheck can make an unexpected request feel urgent and legitimate.",
        },
        {
            "id": f"generated-{seed}-invoice",
            "title": f"Supplier Invoice {invoice}",
            "category": "Business Email Compromise (BEC)",
            "is_phishing": True,
            "sender": "Accounts Payable <billing@vendor-payments.example.com>",
            "subject": f"Overdue invoice {invoice}: payment details changed",
            "preview": "Please pay today using the revised account information.",
            "content": (
                f"Hello Accounts Payable,\n\nInvoice {invoice} is overdue. Please arrange payment today using the "
                f"updated bank details in the attached file: Invoice_{invoice}.pdf.exe\n\n"
                "Please do not call the usual contact, as they are unavailable.\n\n"
                "Regards,\nSupplier Accounts"
            ),
            "red_flags": [
                {"title": "Executable disguised as an invoice", "explanation": "The filename ends in .exe, so it is a program, not a PDF. Do not open it."},
                {"title": "Changed payment details", "explanation": "Payment-account changes should be verified with a known contact using a separate trusted channel."},
                {"title": "Discourages verification", "explanation": "Asking you not to call the usual contact is a warning sign designed to bypass normal controls."},
            ],
            "safe_signals": [],
            "psychology_note": "A plausible invoice and payment deadline exploit routine business processes and pressure.",
        },
        {
            "id": f"generated-{seed}-delivery",
            "title": "Parcel Delivery Fee Notice",
            "category": "Consumer Phishing",
            "is_phishing": True,
            "sender": "Parcel Updates <notice@delivery-status.example.com>",
            "subject": "Delivery on hold: small fee required",
            "preview": "Pay a small redelivery fee to release your parcel.",
            "content": (
                f"Delivery reference: {tracking_id}\n\nYour parcel could not be delivered. A small redelivery fee "
                "is required within 24 hours or the parcel will be returned.\n\n"
                "[Pay redelivery fee](https://example.com/delivery/fee)\n\n"
                "Parcel Updates"
            ),
            "red_flags": [
                {"title": "Generic delivery sender", "explanation": "The message does not identify a carrier or connect the tracking reference to an order you expect."},
                {"title": "Unexpected payment request", "explanation": "A small fee request can be used to collect payment-card details."},
                {"title": "Urgent deadline and unfamiliar link", "explanation": "The 24-hour threat and example.com link are reasons to check directly with the carrier instead."},
            ],
            "safe_signals": [],
            "psychology_note": "A small fee and the anticipation of a delivery can lower suspicion.",
        },
        {
            "id": f"generated-{seed}-town-hall",
            "title": f"{company} Team Town Hall",
            "category": "Internal Communication",
            "is_phishing": False,
            "sender": f"Internal Communications <communications@{domain}>",
            "subject": f"Team town hall: {meeting_day} at {meeting_time}",
            "preview": "Join the team for updates and a question-and-answer session.",
            "content": (
                f"Hello everyone,\n\nOur team town hall is {meeting_day} at {meeting_time}. "
                "We will share project updates and leave time for questions. The calendar invitation is in your "
                "work calendar, and the agenda is on the company intranet:\n\n"
                f"[Town hall agenda](https://intranet.{domain}/events/town-hall)\n\n"
                "Best,\nInternal Communications"
            ),
            "red_flags": [],
            "safe_signals": [
                {"title": "Expected internal sender", "explanation": f"The sender uses the organization's {domain} domain."},
                {"title": "Link stays on the company domain", "explanation": f"The agenda link is on the intranet subdomain of {domain}."},
                {"title": "No pressure or sensitive request", "explanation": "The message is informational and does not request credentials, payment, or personal data."},
            ],
            "psychology_note": "Recognizing normal, low-pressure communication helps make unusual requests stand out.",
        },
        {
            "id": f"generated-{seed}-sign-in",
            "title": f"{company} Sign-in Notification",
            "category": "Account Notification",
            "is_phishing": False,
            "sender": f"{company} Account Security <no-reply@{domain}>",
            "subject": "A new sign-in to your work account",
            "preview": f"A sign-in was recorded from {sign_in_location}.",
            "content": (
                f"Hello,\n\nA new sign-in to your {company} work account was recorded from {sign_in_location}. "
                "If this was you, no action is needed. If you do not recognize it, open the company account portal "
                "using your usual bookmark and review your recent activity.\n\n"
                f"[Account security](https://accounts.{domain}/security)\n\n"
                f"{company} Account Security"
            ),
            "red_flags": [],
            "safe_signals": [
                {"title": "Official sender domain", "explanation": f"The sender address uses the organization's {domain} domain."},
                {"title": "No immediate demand", "explanation": "The message says no action is needed if the sign-in was yours and does not threaten account loss."},
                {"title": "Advises independent verification", "explanation": "It recommends opening the known account portal directly rather than urgently entering credentials through an email link."},
            ],
            "psychology_note": "A trustworthy security notification informs the reader and encourages independent verification.",
        },
    ]
    rng.shuffle(scenarios)
    return scenarios
