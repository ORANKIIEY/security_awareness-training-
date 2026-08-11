# Why phishing awareness matters (organisational risk)

**TRAINING EXAMPLE — DO NOT SEND.**

Phishing is not just an individual “be careful” problem. It is one of the most reliable ways attackers enter organisations — and training the human layer is a deliberate risk control, not a soft optional extra.

## Risk = Likelihood × Impact

| Factor | Why it scores high for phishing |
| --- | --- |
| **Likelihood** | Phishing volume is enormous. Lookalike domains, business email compromise (BEC), and credential theft campaigns are routine. Filters catch many messages; enough still reach inboxes. |
| **Impact** | A single successful click can lead to credential theft, account takeover, fraudulent payments, ransomware footholds, or lateral movement inside the network. |

High likelihood × high impact = a priority risk. That is why phishing consistently ranks among top initial access vectors in breach reports and why boards and GRC teams track awareness programmes.

## Technical controls are necessary — and incomplete

Organisations typically deploy:

- Spam / phishing filters and secure email gateways
- Multi-factor authentication (MFA)
- URL rewriting / sandboxing
- Endpoint detection and response

These **reduce** risk. They do **not** eliminate it. Attackers adapt (new domains, MFA fatigue, vendor impersonation, urgent internal-looking requests). Someone will still receive a message that looks “close enough” under time pressure.

## Awareness training as a complementary control

Security awareness and simulated phishing campaigns treat people as a control layer:

- Teach recognition of common pretexts and red flags
- Build the habit of **reporting** instead of clicking or quietly deleting
- Measure whether the control is working

Training does not replace filters or MFA. It covers residual risk those tools leave behind.

## How organisations measure effectiveness

| Metric | What it tells you |
| --- | --- |
| **Click rate** | How often users engage with simulated (or real) phishing links — lower is better over time. |
| **Report rate** | How often users report suspicious mail — higher (and rising) shows a healthy reporting culture. |
| **Time-to-report** | How quickly suspicious mail is flagged — faster reporting shrinks the attacker’s window. |

Trend these over repeated simulations. A one-off “phishing day” is less useful than a programme that reduces clicks and increases timely reports.

## How this package fits

The scenarios in this repo are sample awareness material of the kind a security awareness or GRC role might produce:

1. Show a realistic pretext.
2. Let learners spot red flags.
3. Explain the psychology (why the trick works).
4. Hand them a reusable checklist.
5. Connect back to organisational risk — not just “don’t get fooled.”

Continue with the [reusable checklist](checklist.md) or jump into a scenario:

- [IT password-reset](scenarios/01-it-password-reset.md)
- [HR / payroll](scenarios/02-hr-payroll.md)
- [Invoice / payment](scenarios/03-invoice-payment.md)
- [Delivery notification](scenarios/04-delivery-notification.md)

Interactive versions: [web/index.html](../web/index.html)
