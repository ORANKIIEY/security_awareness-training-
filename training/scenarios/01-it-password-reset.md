# Scenario 1: Fake IT / password-reset alert

**TRAINING EXAMPLE — DO NOT SEND.** Generic company only. Links are dead placeholders.

## 1. The scenario

A fake IT desk warns that your corporate account will be suspended in 24 hours unless you “verify” your credentials via a lookalike domain.

## 2. The email (spot the phish)

Try to list the red flags before scrolling to the annotated section.

```
From:    IT Support Desk <it-support@acmecorp-secure.net>
Reply-To: helpdesk@mail-acmecorp-login.com
To:      you@acmecorp.example
Subject: Action Required: Your Account Will Be Suspended in 24 Hours

Dear User,

We detected unusual activity on your Acme Corp account from an
unrecognised device. To avoid permanent suspension, you must verify
your identity immediately.

[ Verify My Account ]
→ https://link-disabled-for-training-purposes.example/verify-now

Failure to verify within 24 hours will result in permanent account
suspension and loss of email access.

Thank you for your immediate attention,
IT Support Team
Acme Corp Information Security
Ext. 0000 | it-support@acmecorp-secure.net
```

Interactive quiz version: [web/scenarios/it-password-reset.html](../../web/scenarios/it-password-reset.html)

---

## 3. Annotated breakdown (answer key)

| # | Red flag | Why it’s suspicious |
| --- | --- | --- |
| 1 | **Sender domain** `acmecorp-secure.net` | Lookalike / typosquat pattern. Real mail would come from the organisation’s real domain (e.g. `acmecorp.example`), not a `-secure` add-on domain. |
| 2 | **Reply-To** differs (`mail-acmecorp-login.com`) | Replies (and “help” threads) can be steered to an attacker-controlled address even if the From line looks official. |
| 3 | **Generic greeting** “Dear User” | Internal IT that knows your account almost always uses your name. |
| 4 | **Urgency + threat** “24 hours” / “permanent suspension” | Designed to short-circuit careful checking. |
| 5 | **CTA link destination** | Hover shows a training-disabled / non-corporate host — not the real SSO or helpdesk URL. |
| 6 | **Unsolicited “unusual activity”** | You didn’t start a reset; cold “verify or lose access” mail is a classic pretext. |
| 7 | **Authority costume** “Information Security” signature | Borrows trust from IT’s real role without proving identity. |

---

## 4. Psychology — why each technique works

| Technique in this email | Principle | Why it works |
| --- | --- | --- |
| 24-hour suspension threat | **Urgency / time pressure** | Shrinks the window for slow, rational evaluation; people act reactively. |
| “IT Support” / “Information Security” | **Authority** | We are conditioned to comply with IT security requests without pushback. |
| Loss of email / permanent suspension | **Fear / loss aversion** | Threats of loss hit harder than neutral “please update your password” language. |
| Official-looking signature + department title | **Familiarity / trust cues** | Formatting that “looks like IT” borrows existing trust in the real team. |
| Subtle domain change (`-secure.net`) | **Cognitive load** | People scan From names, not domains — small mismatches slip past. |
| “Unusual activity” story | **Authority + fear** | Implies the organisation already knows something is wrong; verifying feels like the safe path. |

---

## 5. Checklist

Apply the shared list: [How to catch a phish](../checklist.md)

Especially for this pretext: open your real password portal or call the IT number you already have — never the link or extension in the email.

## Related

- [Risk overview](../overview.md)
- Next: [HR / payroll](02-hr-payroll.md)
