# Scenario 2: Fake HR / payroll notice

**TRAINING EXAMPLE — DO NOT SEND.** Generic company only. Links are dead placeholders.

## 1. The scenario

A fake HR / payroll message claims your direct-deposit details must be “confirmed” to receive a bonus or the next payday — pushing you to a lookalike form.

## 2. The email (spot the phish)

Try to list the red flags before scrolling to the annotated section.

```
From:    Acme Corp Payroll <payroll@acme-hr-portal.net>
Reply-To: payroll-updates@secure-acmebenefits.com
To:      you@acmecorp.example
Subject: ACTION NEEDED TODAY: Confirm Direct Deposit for Bonus Payout

Dear Employee,

Good news — you have been selected for a Q3 performance bonus.
To release payment on this Friday’s payroll run, you must confirm
your direct deposit details before 5:00 PM.

If we do not receive confirmation, your bonus will be deferred
and may be forfeited under policy 4.2.

[ Confirm Direct Deposit ]
→ https://link-disabled-for-training-purposes.example/deposit-confirm

Please treat this as confidential.

Regards,
Acme Corp People Operations — Payroll
payroll@acme-hr-portal.net
```

Interactive quiz version: [web/scenarios/hr-payroll.html](../../web/scenarios/hr-payroll.html)

---

## 3. Annotated breakdown (answer key)

| # | Red flag | Why it’s suspicious |
| --- | --- | --- |
| 1 | **Sender domain** `acme-hr-portal.net` | Not the real corporate domain. “HR portal” wording is a common lookalike pattern. |
| 2 | **Mismatched Reply-To** (`secure-acmebenefits.com`) | Another domain entirely — classic steering trick. |
| 3 | **Generic greeting** “Dear Employee” | Real payroll mail about *your* bonus usually uses your name and employee ID context. |
| 4 | **Reward + deadline** bonus + “TODAY” / 5:00 PM | Combines greed/curiosity with time pressure. |
| 5 | **Loss framing** “may be forfeited” | Threatens losing something you “already have.” |
| 6 | **Unexpected process** confirm deposit via email link | Real bank/payroll changes usually go through known HRIS portals, not cold email CTAs. |
| 7 | **“Confidential”** closing | Social pressure not to ask a colleague or manager — isolates the victim. |

---

## 4. Psychology — why each technique works

| Technique in this email | Principle | Why it works |
| --- | --- | --- |
| Bonus / payout language | **Curiosity / reward** | Positive outcomes pull clicks as strongly as threats push them. |
| “ACTION NEEDED TODAY” / 5 PM cutoff | **Urgency / time pressure** | Payday timing makes delay feel costly. |
| Forfeiture threat | **Fear / loss aversion** | People fight harder to keep a promised gain than to earn a new one. |
| “People Operations — Payroll” | **Authority** | HR/payroll controls money; employees comply with process requests. |
| Portal-looking domain & tone | **Familiarity / trust cues** | Mimics benefits-portal language people already trust. |
| “Treat as confidential” | **Social isolation** | Discourages verifying with a peer — reduces the chance someone spots the scam. |
| Scanning under busy workday load | **Cognitive load** | Subject-line skimming misses the wrong domain. |

---

## 5. Checklist

Apply the shared list: [How to catch a phish](../checklist.md)

Especially for this pretext: open your real HR/payroll system from a bookmark or SSO app launcher — never from an email button — or ask HR via a known channel.

## Related

- [Risk overview](../overview.md)
- Previous: [IT password-reset](01-it-password-reset.md) · Next: [Invoice / payment](03-invoice-payment.md)
