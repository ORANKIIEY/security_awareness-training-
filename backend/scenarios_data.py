SCENARIOS = [
    {
        "id": "it-password-reset",
        "title": "IT Password Reset Alert",
        "category": "Credential Harvesting",
        "sender": "Acme IT ServiceDesk <security-alert@acme-support-desk.com>",
        "subject": "ACTION REQUIRED: Mandatory Password Verification",
        "preview": "Your password will expire in 2 hours. Click below immediately to keep your account active.",
        "content": "Dear Employee,\n\nWe detected suspicious activity on your account. Your password will expire in 2 hours unless verified.\n\nPlease click the button below to verify your current password immediately:\n\n[Verify Account & Reset Password](http://192.168.1.55/auth/login?user=acme)\n\nFailure to verify will result in immediate lock of your workstation.\n\nRegards,\nAcme IT Global Security Team",
        "red_flags": [
            {
                "title": "Sender Address Mismatch",
                "explanation": "Email claims to be from Acme IT, but domain is 'acme-support-desk.com' (not official acme.com)."
            },
            {
                "title": "Artificial Urgency & Threat",
                "explanation": "Threatens 2-hour deadline and workstation lock to induce panic and force fast action."
            },
            {
                "title": "Raw IP Address Link",
                "explanation": "Link points directly to an IP address (192.168.1.55) rather than an authenticated corporate SSO domain."
            }
        ],
        "psychology_note": "Urgency short-circuits critical thinking. Panic causes targets to bypass standard security checks."
    },
    {
        "id": "hr-payroll",
        "title": "HR Direct Deposit Update Notice",
        "category": "Financial Fraud / Payroll",
        "sender": "Payroll Operations <payroll-update@acme-hr-portal.net>",
        "subject": "URGENT: Confirm Direct Deposit Details Before Payday",
        "preview": "We need you to confirm your bank account information to prevent payment delay.",
        "content": "Hello Team Member,\n\nDue to a recent banking system migration, all employees must re-submit their direct deposit banking details prior to Friday's payroll processing.\n\nPlease review your bank details now:\n\n[Update Banking Details](http://acme.payroll-portal.net/update)\n\nIf not completed, your paycheck will be held for 14 business days.\n\nThank you,\nHR & Payroll Team",
        "red_flags": [
            {
                "title": "Lookalike Subdomain Domain",
                "explanation": "Domain 'acme.payroll-portal.net' uses 'acme' as a subdomain prefix to trick targets into trusting a third-party host."
            },
            {
                "title": "Fear of Financial Loss",
                "explanation": "Threatening a 14-day pay delay exploits fear and financial stress."
            },
            {
                "title": "Out-of-Band Process Violation",
                "explanation": "HR rarely requests bank account re-verification via plain email links without 2FA or employee self-service login."
            }
        ],
        "psychology_note": "Exploits authority and fear of missing pay to force compliance without verification."
    },
    {
        "id": "invoice-payment",
        "title": "Vendor Urgent Invoice Request",
        "category": "Business Email Compromise (BEC)",
        "sender": "Accounts Receivable <billing@supplier-logistics-corp.com>",
        "subject": "OVERDUE INVOICE #98214 - Immediate Payment Required",
        "preview": "Attached is overdue invoice #98214. Please process wire transfer today.",
        "content": "Hi Accounts Payable,\n\nWe have not received payment for invoice #98214 ($14,850.00) which is now 30 days overdue. Please process payment via wire transfer to our updated bank account:\n\nAccount: 9812-4412-0987\nRouting: 122000049\n\nSee attached document: Invoice_98214_Overdue.exe\n\nThank you for your prompt payment.\n\nSupplier Logistics Corp",
        "red_flags": [
            {
                "title": "Malicious Executable Attachment",
                "explanation": "The attached invoice file ends in '.exe' instead of '.pdf'. Executing it will run malware."
            },
            {
                "title": "Unannounced Wire Account Change",
                "explanation": "Requests payment to a new/updated bank account without secondary phone confirmation."
            }
        ],
        "psychology_note": "Leverages vendor authority and fear of contract breach to bypass finance control policies."
    },
    {
        "id": "delivery-notification",
        "title": "Parcel Delivery Exception Notice",
        "category": "Consumer Phishing",
        "sender": "Express Parcel Alert <notification@express-delivery-tracking.com>",
        "subject": "Delivery Failed: Address Confirmation Required",
        "preview": "Your package could not be delivered today. Click to reschedule.",
        "content": "Notice of Undelivered Item:\n\nTracking ID: EXP-882190-US\n\nYour package delivery attempt failed due to an incomplete home address. A redelivery fee of $1.99 is required.\n\n[Reschedule Package Delivery](http://express-delivery-tracking.com/pay)\n\nPackages not claimed within 48 hours will be returned to sender.",
        "red_flags": [
            {
                "title": "Generic Unrecognized Sender",
                "explanation": "Vague delivery provider name without specifying carrier name (FedEx/UPS/DHL/USPS)."
            },
            {
                "title": "Small Fee Trap",
                "explanation": "Asks for a tiny $1.99 fee to harvest credit card numbers and full CVV credentials."
            }
        ],
        "psychology_note": "Curiosity and eagerness to receive a package lowers vigilance against low-dollar payment traps."
    },
    {
        "id": "townhall-invite",
        "title": "Quarterly Town Hall Invite",
        "category": "Internal Communication",
        "is_phishing": False,
        "sender": "Internal Communications <communications@acme.com>",
        "subject": "Q3 Town Hall - Thursday 2:00 PM",
        "preview": "Join us Thursday for the quarterly town hall.",
        "content": "Hi everyone,\n\nOur Q3 town hall is this Thursday at 2:00 PM in the main auditorium, and streamed for remote staff.\n\nWe'll cover team updates, Q3 results and the roadmap for next quarter. The calendar invite is already in your Outlook calendar, and the agenda is on the intranet:\n\n[Town hall agenda](https://intranet.acme.com/events/q3-townhall)\n\nSubmit questions in advance through the same page.\n\nBest,\nInternal Communications",
        "red_flags": [],
        "safe_signals": [
            {
                "title": "Sender matches the company domain",
                "explanation": "The email comes from @acme.com, the organisation's real domain, not a look-alike."
            },
            {
                "title": "Link stays on the company's own site",
                "explanation": "The link goes to intranet.acme.com, a subdomain of the real company domain."
            },
            {
                "title": "No pressure and no request for credentials",
                "explanation": "There's no deadline, threat or request to log in, pay or share personal details."
            }
        ],
        "psychology_note": "Not every email is an attack. Knowing what normal looks like makes the unusual stand out."
    },
    {
        "id": "github-signin",
        "title": "New Sign-in Notification",
        "category": "Account Notification",
        "is_phishing": False,
        "sender": "GitHub <noreply@github.com>",
        "subject": "[GitHub] A new sign-in to your account",
        "preview": "We noticed a new sign-in to your account from Chrome on Windows.",
        "content": "Hey there,\n\nWe noticed a new sign-in to your GitHub account.\n\nBrowser: Chrome on Windows\nLocation: Berlin, Germany\nTime: October 9, 2026, 18:42 UTC\n\nIf this was you, you don't need to do anything.\n\nIf you don't recognise this sign-in, open GitHub yourself and review your security settings:\n\n[github.com/settings/security](https://github.com/settings/security)\n\nThanks,\nThe GitHub Team",
        "red_flags": [],
        "safe_signals": [
            {
                "title": "Official sending domain",
                "explanation": "The address is @github.com exactly, with no extra words or swapped letters."
            },
            {
                "title": "Visible link matches where it goes",
                "explanation": "The link text and the real destination are both github.com/settings/security."
            },
            {
                "title": "Nothing is demanded",
                "explanation": "It tells you no action is needed if it was you, and encourages you to go to the site yourself."
            }
        ],
        "psychology_note": "Real security alerts inform rather than threaten. When in doubt, skip the link and open the site directly."
    }
]

for _scenario in SCENARIOS:
    _scenario.setdefault("is_phishing", True)
    _scenario.setdefault("safe_signals", [])

# Interleave legitimate emails so the answer isn't predictable from position.
_ORDER = ["it-password-reset", "townhall-invite", "hr-payroll", "invoice-payment", "github-signin", "delivery-notification"]
SCENARIOS.sort(key=lambda s: _ORDER.index(s["id"]) if s["id"] in _ORDER else len(_ORDER))
