# Phase 10 report — WhatsApp (primary automated messaging)

Date: 23 September 2026  
Git branch: `cursor/phase-10-whatsapp-9d24`  
Live URL(s): https://haqqline.excellonit.net/#whatsapp · `/whatsapp.json`  
Deploy: GitHub Actions rsync + `scripts/sync_whatsapp.py` (when WABA secrets are set)

## Built (complete)

- Demo `#whatsapp` section (EN + AR), sandbox-labelled, same agent / tools / policy as Talk.
- `public/whatsapp.json` scaffolding: empty until connect; `wa_me`, STOP/HELP policy, failover → Talk; `voice_calls: false`, `outbound_templates: false`.
- `public/whatsapp.js` loads number + wa.me link, or empty → Talk.
- `scripts/sync_whatsapp.py`: after Meta Embedded Signup in ElevenLabs dashboard, lists `/v1/convai/whatsapp-accounts`, PATCHes `assigned_agent_id` to the HaqqLine agent, writes live `whatsapp.json`.
- CI `whatsapp-sync`: skip-clean when `WHATSAPP_PHONE_NUMBER_ID` / `WHATSAPP_E164` unset; assign + rsync when set.
- Case spine: webhook detects WhatsApp channel and stamps `channel` on conversation + case link.
- Health / API phase → 10; `channels.whatsapp: true` (surface live; number may be empty).

## Tests

| Test | Result |
| --- | --- |
| WhatsApp section sandbox markup | pass |
| Empty number → Talk failover | pass |
| Gold EN/AR + unconfirmed-submit still in agent suite | pass |
| STOP / HELP opt-out policy documented | pass |
| Sync scaffold + wa.me helper | pass |
| Prior phase suites | pass (run in CI) |

## What an investor can do now

Open `#whatsapp`: see sandbox WhatsApp section and Talk failover until a WABA number is connected. Same agent brain and policy as voice.

## WhatsApp WABA — deferred (accepted residual)

Entry criteria (Meta WABA approved, number not elsewhere, payment if templates, session-start template approved) and live ElevenLabs import are **not** loaded yet.

**Residual defect (accepted at sign-off):** *WABA deferred* — same pattern as Phase 5 inbound DID.

Clearing the residual later requires: Meta Embedded Signup into ElevenLabs, GitHub secrets `WHATSAPP_PHONE_NUMBER_ID` or `WHATSAPP_E164`, green `whatsapp-sync`, inbound EN+AR gold WhatsApp transcripts, and an update to this report. That is a defect return to Phase 10, not a new phase.

## Explicitly not built (next phases)

- Live inbound WhatsApp evidence (residual)
- SMS (Phase 11)
- WhatsApp voice calls (out of Phase 10 scope)
- Marketing blasts / outbound templates (gated off)

## Risks / residual defects

- **WABA deferred** (accepted until owner loads Meta / ElevenLabs WhatsApp).
- Unofficial WhatsApp gateways remain forbidden.

## Status

**Signed off 23 September 2026 — Approve Phase 10 with residual “WABA deferred”.** Phase closed. Merge this branch to `main` and tag `phase-10` after merge. Phase 11 stays closed until owner `Begin Phase N` / **Next**.
