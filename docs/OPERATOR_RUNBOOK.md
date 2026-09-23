# Operator runbook (sandbox) — Phases 9–12

**Audience:** ExcellonIT operators supporting the HaqqLine sandbox at https://haqqline.excellonit.net  
**Tone:** authority-facing clarity; this host remains an **ExcellonIT sandbox**, not a government service.  
**Budgets:** `public/sre-budgets.json` (also served at `/sre-budgets.json`).  
**Edge notes:** `docs/NGINX_SECURITY_HEADERS.md`.

## 1. Pack rollback

1. Identify the last good tag (`phase-11`, `phase-10`, …) or commit where `verify_pack_lock.py` and live `GET /api/v1/health` citation match.
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

## 3. Number / channel failover

| Condition | Operator action |
| --- | --- |
| `enabled: false` / empty `phone_number` in `/twilio.json` | Kill switch or unset secrets. Callers use **Talk**. To pause: `HAQQLINE_CALL_DID_ENABLED=0` + re-run `sync_twilio.py`. |
| Live sandbox DID (`+13159020932` when enabled) | Inbound Voice only; sandbox disclaimer. SMS off until Messaging compliance clears. |
| Twilio / carrier 5xx or DID does not ring | Instruct callers to use **Talk**. |
| WhatsApp not connected (`/whatsapp.json`) | Use **Talk**. Residual *WABA deferred*. |
| SMS not connected (`/sms.json`) | Receipts stay in outbox; callers use WhatsApp/Talk. Residual *Twilio SMS deferred* (compliance review). |

Do not invent a government hotline or WhatsApp number.

## 4. Alerts (minimal)

Append-only `public/api/data/alerts.jsonl` on the host (gitignored):

- `http_5xx` — API returned 5xx
- `tool_failure` — tool audit with 5xx or `policy_denied`

Read via authenticated `GET /api/v1/alerts` (last 20). Wipeable on sandbox reset. This is not a paging stack — act on entries during triage.

## 5. Latency / load budgets (sandbox-labelled)

See `/sre-budgets.json`. If tool p95, cited-answer, or sandbox load gate fails on a release candidate, **do not promote** the agent; capture the note in the phase report.

Load evidence: `python3 scripts/load_test.py` → `reports/phase-12-load.json`.

## 6. Case / audit backup and restore drill

1. On a workstation with the repo (or a host snapshot of `public/api/data/`):  
   `python3 scripts/backup_restore_drill.py`
2. Confirm `reports/phase-12-restore.json` has `"ok": true` and matching line counts.
3. Log elapsed_ms in the phase report. Live host wipe remains operator-controlled (git does not restore `api/data`).

## 7. Rate limit response

Burst traffic returns HTTP 429 (`rate_limited`). Check pack `rate_limit_per_minute` (default 120/IP). Do not raise the limit for a demo spike without recording it in `OPERATIONS.md`.

## 8. Phase 12 dry-run checklist (sign here)

| Step | Result | Operator (not the builder) |
| --- | --- | --- |
| Pack rollback path read and understood | ☐ | |
| Agent promote-gate refusal understood | ☐ | |
| Talk failover for empty DID / WA / SMS stated | ☐ | |
| Restore drill artifact `phase-12-restore.json` reviewed | ☐ | |
| Load artifact `phase-12-load.json` reviewed | ☐ | |
| Edge/WAF notes in `NGINX_SECURITY_HEADERS.md` acknowledged | ☐ | |

Dry-run sign-off is recorded in `reports/phase-12.md`.
