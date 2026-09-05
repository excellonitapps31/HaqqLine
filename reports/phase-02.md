# Phase 02 report — Rule and case APIs

Date: 5 September 2026  
Git SHA: `13b6db8` on `phase/02-apis`  
Live URL(s): https://haqqline.excellonit.net/api/v1/docs · https://haqqline.excellonit.net/api/v1/openapi.json  
Deploy: GitHub Actions rsync (`phase/02-apis`)  
CI: https://github.com/excellonitapps31/HaqqLine/actions/runs/33954921384 (success)

## Built (complete)

- Versioned HTTPS API on the same host as the shell (`/api/v1`).
- Tools: `lookup_rera_band`, `lookup_ejari`, `submit_to_human_queue`, `escalate_human`.
- OpenAPI 3.1 + read-only docs UI with a live try against JLT.
- Bearer demo key `haqqline_sandbox_preview` (sandbox, documented) and 120 req/min rate limit.
- Audit JSONL on the host (not in git). Confirmation gate: unconfirmed submit → 400; confirmed → `pending_human`.
- Unknown area → 404 `escalate: true`, no `index_aed`. Missing Ejari → `found: false`, `invented: false`.
- Documented demo throughput: 2 r/s (not UAE production scale).

## Tests

| Test | Result |
| --- | --- |
| OpenAPI lists all four tools | pass |
| 401 without key | pass (local + live) |
| Unknown area / no invented index | pass |
| Ejari found and missing | pass |
| Confirmation gate | pass (local + live) |
| Load smoke 20 sequential lookups | pass |
| CI verify + deploy + live JLT lookup | pass |

## What an investor can do now

Open https://haqqline.excellonit.net/api/v1/docs, run the JLT example, read the disclaimer. Call Ejari `EJ-1001` or a fake id. Attempt a filing without confirmation and see it refused.

## Explicitly not built (next phases)

- Scenario cards / queue viewer UI (Phase 3)
- ElevenLabs, Twilio, WhatsApp, SMS

## Risks / residual defects

- Demo API key is public. That is intentional for a sandbox.
- PHP on LiteSpeed; data dir is `public/api/data` with deny-all, created on deploy.

## Request

Approve Phase 02 / Reject
