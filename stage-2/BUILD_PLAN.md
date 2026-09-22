# HaqqLine — Stage 2 delivery plan

**Window:** 30 September 2026 – 14 October 2026  
**Owner:** ExcellonIT  
**Live host:** https://haqqline.excellonit.net  
**Product shape:** `PRODUCT_SHAPE.md`  
**Programme:** `IMPLEMENTATION_PLAN.md` (Phases 1–4 are on `main`. This window finishes Phase 5 and freezes evidence.)

The product is the agent, the sandbox tools, and the demo page. A separate mobile or web app is out of scope.

## 1. Done on 14 October

A reviewer, with no dashboard login, can:

1. Open the sandbox and complete a rent-band check in the browser, in English and in Gulf Arabic.
2. Dial the test DID on the same page and complete the same check. Inbound only.
3. Hear the disclosure before any figure, hear the pack named with the figure, and hear a refusal on “will I win?”.
4. See `submit_to_human_queue` rejected unless `caller_confirmed` is true, and accepted only as `pending_human`.
5. Read the evidence in this repo: a numeric multi-run pass rate, the high-stakes tool-call result, transcripts of the primary path and the failure path, this plan, `PRODUCT_SHAPE.md`, and the README.

No resident data. No live DLD, RERA, or RDC credentials. No outbound campaigns.

If the purchased DID is blocked (KYC, stock, or credentials), the web path still stands. The DID is the stronger proof and stays the Phase 5 exit. It does not become a reason to invent a second product.

## 2. Baseline already on main

| Piece | Where | State |
| --- | --- | --- |
| TLS sandbox shell, EN/AR, disclaimer | `public/` | Live since Phase 1 |
| Rule lookup, Ejari mock, confirm gate, audit, HMAC webhook | `public/api/v1/` | Live since Phase 2 |
| Scenario playground | `public/play/` | Live since Phase 3 |
| ConvAI widget, workflow, knowledge pack, agent tests | Talk on the host; `elevenlabs/` | Live since Phase 4. Agent `agent_5601m1xp22apfdcbwbb8h9y5zzqt` |
| Inbound DID | `public/twilio.json`, `scripts/sync_twilio.py` | Page and import script are in the tree. `phone_number` is still empty |

Do not rebuild Phases 1–4 inside this window. Defects found while recording go back to the phase that owns them.

## 3. Work in this window

### Telephony

Import one purchased Twilio Voice number into ElevenLabs and assign the existing agent. Prefer a Standard API key (`SK` + secret). Account SID + auth token is the fallback. `enable_sms` stays false.

Exit: `public/twilio.json` has an E.164 number, the Call section on the host shows it with the sandbox disclaimer, one English inbound and one Arabic inbound are logged, and a Twilio failure sends the caller back to Talk on the same page.

### Evaluation evidence

`elevenlabs/tests.json` already defines disclosure, the JLT lookup, the unconfirmed-submit absence, and the EN/AR simulations. Phase 4 invoked the suite. The sync summary did not parse a pass rate (reported as 0). The dashboard remains the source of truth until `scripts/sync_elevenlabs.py` writes a real fraction.

Exit: `reports/phase-05.md` states passed/total. The unconfirmed-submit test is quoted, not described from memory. A skipped disclosure fails the run.

### Recorded paths

Two calls, web or DID:

- Primary: area, current rent, proposed rent, cited band, no filing unless the caller confirms.
- Failure: “Will I win if I sue?” ends in `escalate_human`. No advice, no invented index.

Exit: transcript links in the phase report. Recordings stay on the ElevenLabs side or an unlisted link. They are not committed as audio.

### Freeze

11–14 October is evidence only. No new tools, no new channel, no prompt experiments that are not a defect fix.

## 4. Acceptance

| Check | Proof |
| --- | --- |
| Disclosure is the first spoken turn | Transcript |
| Figure cites `sandbox_decree_43_2013_table_v1` | Transcript |
| Unknown area escalates and does not invent an index | Tool-call log |
| Submit without `caller_confirmed: true` returns 400 | API test and agent tool-call test |
| Submit with confirmation returns `pending_human` | API test |
| No tool asks for a PIN, password, or OTP | Tool schema review |
| EN and AR each have a completed primary path | Two transcripts |
| Pass rate is a number | Phase 5 report |
| First cited answer inside 180 seconds, including the lookup | Timed note in the report |
| Host still says this is not a government service | Landing test |

## 5. Environments

| Environment | How it runs | Data |
| --- | --- | --- |
| Local | `php -S 127.0.0.1:8787 -t public public/router.php`, pytest | Pack JSON in the repo |
| CI | `.github/workflows/ci.yml` on `main` and `phase/**` | Secrets injected. Not printed. |
| Sandbox host | GitHub Actions rsync of `public/` to the cPanel document root | `public/api/data/` on the host only. Wipeable. Not in git. |

Promotion is the phase branch, green CI, smoke of the live URL, `reports/phase-05.md`, sign-off, merge, tag `phase-05`.

## 6. Controls that do not move

- Synthetic Ejari ids only: EJ-1001, EJ-1002, EJ-1003. Any other id is `found: false` and `invented: false`.
- The demo API key in `public/api/v1/pack/config.json` is public. The control is the rate limit, not secrecy.
- Webhook signatures are HMAC, with a 30-minute clock skew. The secret file is on the host, mode 600.
- There is no `decide_case` tool.
- Rollback of the site is the previous git tag and a redeploy. A bad agent sync is corrected by running `scripts/sync_elevenlabs.py` from the last good commit. The host data directory is not rolled back by git.

## 7. Risks

| Risk | What it does to the date | Response |
| --- | --- | --- |
| Twilio number not purchased, or extra KYC on the chosen country | DID missing on 14 October | Keep the web path. Do not substitute a verified caller id. |
| Eval payload shape still unparsed | Pass rate cannot be quoted | Use the ElevenLabs dashboard count and fix the parser only if the payload is stable |
| Arabic path never heard by a native listener | AR evidence is weaker than EN | One listen-through before the recording day |
| Scope pulled in from WhatsApp or SMS | Voice evidence slips | Those channels stay Phase 6 and Phase 7 |

## 8. After 14 October

WhatsApp (official WABA only), then SMS for receipts and status, then hardening and the runbook drill. None of that starts because the evidence pack feels thin. A thin pack is a defect in this window, not a reason to open the next channel.
