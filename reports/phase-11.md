# Phase 11 report — SMS (secondary transactional)

Date: 23 September 2026  
Git branch: `cursor/phase-11-sms-9d24`  
Live URL(s): https://haqqline.excellonit.net/#sms · `/sms.json` · `POST /api/v1/webhooks/twilio/sms`  
Deploy: GitHub Actions rsync + `scripts/sync_sms.py` (when Twilio SMS number is set)

## Built (complete)

- Demo `#sms` section (EN + AR): secondary fallback; no rights-check over SMS; redirect to WhatsApp/Talk.
- `public/sms.json` scaffolding + `sms.js`; STOP/HELP policy; events `filing_queued` / `escalated`.
- `HaqqLineSms.php`: outbox dry-run when not connected; opt-out; inbound STATUS/STOP/HELP; Twilio send when credentials + connected.
- Confirmed submit / escalate with `packet.phone` or `sms_to` → receipt body includes case id + `pending_human`.
- Unconfirmed submit never notifies.
- Webhook `POST /api/v1/webhooks/twilio/sms` (TwiML); authenticated `GET /api/v1/sms/outbox`.
- CI `sms-sync` skip-clean when numbers unset; health/API phase → 11; `channels.sms: true`.

## Tests

| Test | Result |
| --- | --- |
| SMS section sandbox markup | pass |
| `filing_queued` → outbox with case id / pending_human | pass |
| Unconfirmed submit → no SMS | pass |
| STOP → further SMS skipped (`opted_out`) | pass |
| Invalid inbound → help, no tool submit | pass |
| Health phase ≥ 11 | pass |
| Prior phase suites | pass (run in CI) |

## What an investor can do now

Complete a confirmed filing with a phone on the packet and see a sandbox SMS receipt (outbox until Twilio SMS is connected). STOP works. Rights-check stays on Talk/WhatsApp.

## Twilio SMS — deferred (accepted residual)

Phase 5 DID / Twilio secrets remain deferred. Live carrier send needs `TWILIO_SMS_NUMBER` (or voice number) + Account SID/Auth Token and a green `sms-sync`.

**Residual defect (accepted at sign-off):** *Twilio SMS deferred* — outbox + webhook prove behaviour without the carrier.

Clearing later: load Twilio secrets, configure Messaging webhook to `/api/v1/webhooks/twilio/sms`, green `sms-sync`, live receipt evidence. Defect return to Phase 11, not a new phase.

## Explicitly not built (next phases)

- Live carrier SMS evidence (residual)
- LLM / rights-check over SMS (forbidden by design)
- Marketing SMS
- Phase 12 hardening

## Risks / residual defects

- **Twilio SMS deferred** (accepted).
- Phase 5 *inbound DID deferred* and Phase 10 *WABA deferred* unchanged.

## Status

**Awaiting Approve Phase 11.** Phase 12 stays closed until then.
