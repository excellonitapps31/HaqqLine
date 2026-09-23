# Operator runbook (sandbox) — Phase 9 draft

**Audience:** ExcellonIT operators supporting the HaqqLine sandbox at https://haqqline.excellonit.net  
**Tone:** authority-facing clarity; this host remains an **ExcellonIT sandbox**, not a government service.  
**Budgets:** `public/sre-budgets.json` (also served at `/sre-budgets.json`).

## 1. Pack rollback

1. Identify the last good tag (`phase-08`, `phase-07`, …) or commit where `verify_pack_lock.py` and live `GET /api/v1/health` citation match.
2. Redeploy that tree via the normal Actions rsync (revert on a phase branch, or checkout tag and push).
3. Confirm `pack_version` / `citation_id` on `/api/v1/health` and run `python3 scripts/verify_pack_lock.py`.
4. Re-run `scripts/sync_elevenlabs.py` from that commit so the agent prompt matches the pack.

Do not edit `areas.json` / `ejari.json` without bumping `pack_version`, `citation_id`, and `content_hash`. Detail: `OPERATIONS.md` § Pack rollback.

## 2. Agent rollback (promote gate)

Phase 9 makes multi-run eval a **promote gate**:

- `scripts/sync_elevenlabs.py` writes `reports/phase-09-eval.json` and exits **2** when the gate fails.
- CI `elevenlabs-sync` **does not rsync** `elevenlabs.json` when the gate fails — the live widget keeps the prior agent.
- High-stakes tests listed in `sre-budgets.json` → `eval_gate.high_stakes_never_quarantined` cannot be skipped via `HAQQLINE_EVAL_QUARANTINE`.

**To roll back a bad agent that already promoted:**

1. Check out the last good commit that produced a green `phase-09-eval` artifact.
2. Run sync (or re-run the Actions `elevenlabs-sync` job on that commit).
3. Confirm live `/elevenlabs.json` `agent_id` / step summary.

**Quarantine (non high-stakes only):** set `HAQQLINE_EVAL_QUARANTINE=test-name-a,test-name-b`. If any name is high-stakes, sync refuses.

## 3. Number failover (Twilio → Talk)

| Condition | Operator action |
| --- | --- |
| Empty `phone_number` in `/twilio.json` | Expected while DID is deferred. Callers use **Talk**. |
| Twilio / carrier 5xx or DID does not ring | Instruct callers to use **Talk** on the home page. Failover string is in `twilio.json`. |
| Secrets unavailable | `twilio-sync` skips import; page keeps Talk failover. Do not invent a government hotline. |

Inbound DID remains a Phase 5 residual until Twilio secrets are intentionally loaded.

## 4. Alerts (minimal)

Append-only `public/api/data/alerts.jsonl` on the host (gitignored):

- `http_5xx` — API returned 5xx
- `tool_failure` — tool audit with 5xx or `policy_denied`

Read via authenticated `GET /api/v1/alerts` (last 20). Wipeable on sandbox reset. This is not a paging stack — act on entries during triage.

## 5. Latency budgets (sandbox-labelled)

See `/sre-budgets.json`. If tool p95 or cited-answer times blow the published targets on a release candidate, **do not promote** the agent; capture the note in the phase report.
