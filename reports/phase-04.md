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
| ElevenLabs agent test suite, re-run 22 September 2026 (invocation `suite_8301m35dwvwhe6q8qc0190mh279w`, agent version `agtvrsn_2501m35dwvkxedqv18zhtq4f9rj6`) | 13/13 passed |

## What an investor can do now

Open https://haqqline.excellonit.net/, allow the microphone, click Talk, complete a rights-check in the browser.

## Explicitly not built (next phases)

- Twilio inbound DID (Phase 5)
- WhatsApp, SMS

## Risks / residual defects

- Demo API key remains public (intentional).
- The 7 September sync read test results before they finished and recorded 0. `scripts/sync_elevenlabs.py` now waits for the invocation to finish and writes passed/total to the job summary and the `phase-04-eval` artifact.
- 22 September 2026: agent tool calls reached the API without the demo key (HTTP 401), because ElevenLabs now reads `request_headers`, not `headers`. Fixed the same day. The suite went from 6/13 to 11/13.
- The two Arabic failures were fixed the same day. The prompt and workflow now call `lookup_rera_band` before any band statement, treat an over-band result as information rather than an escalation, and reply in the caller's language. The Arabic unknown-area scenario now states that the simulated caller speaks only Arabic; before that, the simulated caller spoke English. Result: 13/13.
- Simulation tests are model-graded. A single run is evidence, not a guarantee. Phase 5 scaffolding sets `repeat_count` default 3; the recorded multi-run rate lands in `reports/phase-05-eval.json` on the next sync.
- Webhook HMAC secret lives only on the host (`api/data/elevenlabs_webhook.secret`), not in git.

## Status

Signed off 7 September 2026. Phase closed.
