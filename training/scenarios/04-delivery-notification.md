# Scenario 4: Fake delivery notification

**TRAINING EXAMPLE — DO NOT SEND.** Generic courier branding only — not a real delivery company. Links are dead placeholders.

## 1. The scenario

A fake parcel notification says a package could not be delivered and asks you to “reschedule” or pay a small customs fee via a lookalike tracking site.

## 2. The email (spot the phish)

Try to list the red flags before scrolling to the annotated section.

```
From:    ParcelLink Delivery <alerts@parcel-link-delivery-secure.com>
Reply-To: support@parcelink-tracking.net
To:      you@email.example
Subject: Your package is on hold — confirm delivery within 12 hours

Dear Customer,

We attempted to deliver your parcel (Tracking #PL-9284410) but the
address could not be verified.

Your item will be returned to the sender unless you confirm delivery
preferences within 12 hours. A small redelivery fee may apply.

[ Reschedule Delivery ]
→ https://link-disabled-for-training-purposes.example/reschedule

Track status anytime on our secure portal.

ParcelLink Automated Notifications
Do not reply to this message.
```

Interactive quiz version: [web/scenarios/delivery-notification.html](../../web/scenarios/delivery-notification.html)

---

## 3. Annotated breakdown (answer key)

| # | Red flag | Why it’s suspicious |
| --- | --- | --- |
| 1 | **Sender domain** `parcel-link-delivery-secure.com` | Long, hyphenated, “secure”-stuffed domain — lookalike pattern, not a known courier. |
| 2 | **Reply-To** `parcelink-tracking.net` | Slight misspelling (`parcelink` vs `parcel-link`) — typosquat flavour. |
| 3 | **Generic greeting** “Dear Customer” | No name, no order number you recognise from a real retailer. |
| 4 | **12-hour hold / return threat** | Artificial deadline to force a click. |
| 5 | **Unexpected parcel** | You didn’t order anything (or the tracking ID is meaningless to you). |
| 6 | **Fee / “secure portal” CTA** | Credential or card harvest pretext disguised as logistics. |
| 7 | **Hover URL ≠ courier** | Destination is a training placeholder, not a real carrier tracking host. |
| 8 | **“Do not reply”** | Discourages questions; funnels you only to the link. |

---

## 4. Psychology — why each technique works

| Technique in this email | Principle | Why it works |
| --- | --- | --- |
| Package on hold / returned to sender | **Fear / loss aversion** | People hate losing a package they believe is theirs. |
| 12-hour window | **Urgency / time pressure** | Encourages immediate tapping on mobile. |
| Tracking number + delivery jargon | **Familiarity / trust cues** | Logistics language feels mundane and therefore trustworthy. |
| “Reschedule” / small fee | **Curiosity / reward** (solve the problem) + mild **loss aversion** | Fixing delivery feels like the helpful, responsible action. |
| Automated notification tone | **Authority** (systemic) | “Systems” feel impersonal and official — less likely to be questioned. |
| Busy inbox / phone notification skim | **Cognitive load** | Users tap CTAs without reading domains. |

---

## 5. Checklist

Apply the shared list: [How to catch a phish](../checklist.md)

Especially for this pretext: open the courier or retailer’s app/site from a bookmark or store listing you trust, and enter the tracking number there — or ignore mail about parcels you never ordered.

## Related

- [Risk overview](../overview.md)
- Previous: [Invoice / payment](03-invoice-payment.md)
- Shared: [Checklist](../checklist.md) · [Overview](../overview.md)
