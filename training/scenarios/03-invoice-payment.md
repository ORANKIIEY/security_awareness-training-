# Scenario 3: Fake invoice / payment request (BEC-style)

**TRAINING EXAMPLE — DO NOT SEND.** Generic company only. Links are dead placeholders.

## 1. The scenario

A business-email-compromise style message impersonates a manager or vendor finance contact and asks for urgent payment or a “updated” invoice wire — using authority and secrecy.

## 2. The email (spot the phish)

Try to list the red flags before scrolling to the annotated section.

```
From:    Jordan Lee (CFO) <j.lee@acme-corp-finance.co>
Reply-To: j.lee.payments@acmecorp-vendors.net
To:      ap@acmecorp.example
Subject: Urgent — Process vendor invoice #44821 today (do not loop email thread)

Hi,

I’m in back-to-back meetings and need Accounts Payable to process
the attached invoice for Northwind Supplies before close of business.
New banking details are on the invoice — use those, not the old ones
on file.

Please confirm once the wire is sent. Keep this between us for now;
I’ll update the full thread tomorrow.

Thanks,
Jordan
CFO, Acme Corp
Sent from my iPhone

[ View Invoice PDF ]
→ https://link-disabled-for-training-purposes.example/invoice-44821
```

Interactive quiz version: [web/scenarios/invoice-payment.html](../../web/scenarios/invoice-payment.html)

---

## 3. Annotated breakdown (answer key)

| # | Red flag | Why it’s suspicious |
| --- | --- | --- |
| 1 | **Lookalike domain** `acme-corp-finance.co` | Not the real company domain; finance-themed add-on domains are common in BEC. |
| 2 | **Reply-To** on `acmecorp-vendors.net` | Payment conversation steered off-corporate infrastructure. |
| 3 | **Executive impersonation** “CFO” + casual mobile sign-off | Authority + “busy executive” realism. |
| 4 | **Urgency** “today” / before close of business | Compresses time for dual-control checks. |
| 5 | **Process bypass** “new banking details” / “not the ones on file” | Classic fraud move — change payee details outside verified channels. |
| 6 | **Secrecy** “keep this between us” / “do not loop email thread” | Blocks the very controls (CC finance, call-back) that would catch the scam. |
| 7 | **Unexpected attachment / invoice link** | Unsolicited payment artifacts deserve verification before opening or paying. |
| 8 | **Tone mismatch** Informal “Sent from my iPhone” for a wire change | Can feel authentic — and that authenticity is the point. |

---

## 4. Psychology — why each technique works

| Technique in this email | Principle | Why it works |
| --- | --- | --- |
| CFO / senior title | **Authority** | Employees are trained not to slow down executives; pushback feels risky. |
| Same-day wire | **Urgency / time pressure** | Dual approval and call-backs get skipped “just this once.” |
| “Keep this between us” | **Fear / social pressure** | Implies career or relational cost to escalating. |
| New bank details on “invoice” | **Familiarity / trust cues** | Invoice PDFs and AP workflows are routine — routine feels safe. |
| Mobile sign-off, short sentences | **Familiarity** | Mimics how busy leaders actually email. |
| Out-of-band domain details | **Cognitive load** | AP staff juggling queues may not parse From vs Reply-To carefully. |

---

## 5. Checklist

Apply the shared list: [How to catch a phish](../checklist.md)

Especially for this pretext: **never** change vendor bank details from email alone. Use the known call-back number on file, dual control, and your real AP policy — ignore “don’t tell anyone” instructions.

## Related

- [Risk overview](../overview.md)
- Previous: [HR / payroll](02-hr-payroll.md) · Next: [Delivery notification](04-delivery-notification.md)
