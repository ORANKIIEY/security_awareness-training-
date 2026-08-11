# Security Awareness Training — Phishing Breakdown

**TRAINING EXAMPLE — DO NOT SEND.** This repository is a security awareness training artifact. It contains fictional phishing emails used only for education. No real organisations are impersonated, and every link is a dead placeholder.

## What this is

A Project 2–style phishing awareness package: realistic (but generic) fake emails, annotated red flags, the psychology behind each trick, a reusable catch-it checklist, and organisational risk framing.

## How to use it

### Markdown (read / interview walkthrough)

1. Start with [training/overview.md](training/overview.md) — why phishing matters at org level.
2. Skim [training/checklist.md](training/checklist.md) — reusable “how to catch it” list.
3. Work through each scenario (spot the phish first, then read the annotations):
   - [IT password-reset alert](training/scenarios/01-it-password-reset.md)
   - [HR / payroll notice](training/scenarios/02-hr-payroll.md)
   - [Invoice / payment request](training/scenarios/03-invoice-payment.md)
   - [Delivery notification](training/scenarios/04-delivery-notification.md)

### Interactive HTML (quiz + reveal)

Open [web/index.html](web/index.html) in a browser. Pick a scenario, try to spot the red flags, then click **Reveal red flags**.

```bash
# From the repo root (so /web and /training links both work)
python3 -m http.server 8080
# Then visit http://localhost:8080/web/
```

## Package structure

```
training/
  overview.md          # Risk = Likelihood × Impact; why training exists
  checklist.md         # Reusable detection checklist
  scenarios/           # Four pretexts with email + psychology
web/
  index.html           # Hub
  css/ styles.css
  js/  app.js
  scenarios/           # Interactive email mockups
```

## Ethical boundaries

- Generic company names only (e.g. Acme Corp) — no real logos or trademarks.
- Links point to `example.com` or `link-disabled-for-training-purposes` only.
- Clearly labelled as training on every page and scenario.
- This is not a phishing kit: do not send these emails or host credential forms.

## Suggested 2-minute interview walkthrough

1. Show the clean email (“What would you check?”).
2. Reveal annotations and name the techniques.
3. Tie one technique to psychology (e.g. urgency → short-circuits scrutiny).
4. Close with Risk = Likelihood × Impact and why awareness training complements MFA/filters.
