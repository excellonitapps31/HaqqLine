# Phase 07 report — Policy engine

Date: 23 September 2026  
Git branch: `cursor/phase-07-policy-engine-9d24`  
Live URL(s): https://haqqline.excellonit.net/api/v1/ · OpenAPI deny schema  
Deploy: GitHub Actions rsync after merge

## Built (complete)

- `HaqqLinePolicy.php`: workflow-node allowlists (Intake / RuleMatch / Filing / Escalate), credential-field ban, no `decide_case`, confirm gate, invent-index ban on filings.
- Optional header `X-HaqqLine-Workflow-Node`. When absent, tools still run subject to confirm + credential rules (backward compatible).
- Denies return `policy_denied: true` with `reason` codes; audited.
- OpenAPI `PolicyDenied` schema + `decide_case` documented as always denied.
- Unconfirmed submit remains HTTP 400 with `error: confirmation_required` (compat) plus policy fields.

## Tests

| Test | Result |
| --- | --- |
| Unconfirmed submit → policy deny | pass |
| Intake cannot submit | pass |
| Filing may submit when confirmed | pass |
| PIN/password/OTP fields denied | pass |
| decide_case denied | pass |
| Deny audited | pass |
| Prior phase suites | pass (run in CI) |

## What an investor can do now

Trust that a prompt regression cannot quietly file without confirmation or invent credentials: the API policy layer blocks it.

## Explicitly not built (next phases)

- Case spine (Phase 8)
- Voice SRE (Phase 9)
- Forcing ElevenLabs to send workflow-node headers on every call (optional; allowlist applies when present)

## Risks / residual defects

- Without `X-HaqqLine-Workflow-Node`, node allowlists are not applied (confirm + credential gates still are).
- Phase 5 residual *inbound DID deferred* unchanged.

## Status

**Signed off 23 September 2026 — Approve Phase 7.** Phase closed. Merge this branch to `main` and tag `phase-07` after merge. Phase 8 stays closed until owner `Begin Phase N` / **Next**.
