# Phase 04 report — ElevenLabs agent + web voice

Date: 7 September 2026  
Git SHA: `57c3fe3` on `phase/04-elevenlabs`  
Live URL(s): https://haqqline.excellonit.net/ · https://haqqline.excellonit.net/#talk  
Agent id: `agent_5601m1xp22apfdcbwbb8h9y5zzqt`  
Deploy: GitHub Actions rsync + `scripts/sync_elevenlabs.py`  
CI: https://github.com/excellonitapps31/HaqqLine/actions/runs/34110709328 (verify, deploy, https-home, playwright-live, elevenlabs-sync — success)

## Built (complete)

- Official ConvAI widget on the sandbox home page (Talk).
- Same agent tools pointed at live `/api/v1` lookup, Ejari, confirmation-gated filing, escalate.
- Prompt with scripted AI/sandbox/not-legal-advice disclosure; EN + Arabic language preset; Scribe realtime keyterms; signed-off pack as knowledge.
- Workflow nodes Intake → RuleMatch → Filing | Escalate.
- Post-call HMAC webhook `/api/v1/webhooks/elevenlabs` into host conversation/audit logs.
- Agent Testing suite defined in `elevenlabs/tests.json` (disclosure, JLT lookup, unconfirmed submit absence, ≥10 EN/AR simulations).

## Tests

| Test | Result |
| --- | --- |
| Widget markup + HMAC webhook unit tests | pass |
| CI verify, deploy, live playground | pass |
| Live `elevenlabs.json` agent_id | pass |
| Parsed multi-run pass rate from sync JSON | 0 (result shape not mapped; suite was still invoked) |

## What an investor can do now

Open https://haqqline.excellonit.net/, allow the microphone, click Talk, complete a rights-check in the browser.

## Explicitly not built (next phases)

- Twilio inbound DID (Phase 5)
- WhatsApp, SMS

## Risks / residual defects

- Demo API key remains public (intentional).
- ElevenLabs eval JSON summary was not parsed into a numeric pass rate; treat dashboard runs as the source of truth until the parser is tightened.
- Webhook HMAC secret lives only on the host (`api/data/elevenlabs_webhook.secret`), not in git.

## Request

Approve Phase 04 / Reject — **approved 7 September 2026**.
