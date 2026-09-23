# Phase 08 report — Case spine and immutable audit

Date: 23 September 2026  
Git branch: `cursor/phase-08-case-spine-9d24`  
Live URL(s): https://haqqline.excellonit.net/api/v1/ · `GET/PATCH /api/v1/cases/{id}` · `GET /api/v1/cases/{id}/audit`  
Deploy: GitHub Actions rsync after merge

## Built (complete)

- `HaqqLineCaseStore.php`: append-only `cases.jsonl` with flock; case ids `CASE-F-*` / `CASE-E-*`; status machine `pending_human` → `in_review` → `closed` | `returned` (returned → in_review).
- Confirmed `submit_to_human_queue` and `escalate_human` create cases (pack version + citation_id stamped); legacy `queue.jsonl` / `escalations.jsonl` still appended for compatibility.
- Authenticated `GET /api/v1/cases/{id}`, `PATCH` status transitions (409 `illegal_transition`), `GET …/audit` (tool audit entries + case events).
- Post-call webhook links `conversation_id` to the newest pending case without a conversation (or creates an escalation case); response includes `case_id`.
- `SECURITY.md`: retention note — append-only JSONL; wipeable on sandbox reset; ≥30 days audit for any later production cutover.

## Tests

| Test | Result |
| --- | --- |
| Confirmed submit → pending_human case | pass |
| Illegal transition rejected (409) | pass |
| Legal transitions in_review → closed | pass |
| Case audit entries + events | pass |
| Concurrent submits → distinct ids + audit | pass |
| Webhook links conversation to case | pass |
| Health phase ≥ 8 | pass |
| Prior phase suites | pass (52 total with phase8) |

## What an investor can do now

Follow case id → audit → conversation without opening ElevenLabs dashboards.

## Explicitly not built (next phases)

- Officer CRM / dashboard UI (Phase 8 out of scope)
- Voice SRE budgets and continuous eval gates (Phase 9)
- WhatsApp / SMS (Phases 10–11)

## Risks / residual defects

- Case store is host-local JSONL (sandbox); not multi-host replicated.
- Webhook auto-link attaches to the newest pending case without a conversation when no explicit case id is sent — callers should pass `conversation_id` on submit when known.
- Phase 5 residual *inbound DID deferred* unchanged.

## Status

**Awaiting Approve Phase 8.** Phase 9 stays closed until then.
