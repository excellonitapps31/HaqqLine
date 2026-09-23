# Phase 12 report — Hardening, scale evidence, operator runbook

Date: 23 September 2026  
Git branch: `cursor/phase-12-hardening-9d24`  
Live URL(s): https://haqqline.excellonit.net/ · `/sre-budgets.json` · `/health`  
Deploy: GitHub Actions rsync after merge

## Built (complete)

- Published sandbox load budgets in `sre-budgets.json` (`api_rps_sandbox`, `success_rate_min`).
- `scripts/load_test.py` → `reports/phase-12-load.json` (sandbox-labelled concurrent lookups).
- `scripts/backup_restore_drill.py` → `reports/phase-12-restore.json` (cases/audit/alerts/sms JSONL tar + restore check).
- `scripts/deps_licence_scan.py` → `reports/phase-12-deps.json` (offline licence map for direct pins; PHP/Python stdlib noted).
- Edge/WAF stand-in documented: `docs/NGINX_SECURITY_HEADERS.md` (Hestia nginx + HSTS + app rate limit; CDN optional).
- Operator runbook expanded with restore, load, rate-limit, and Phase 12 dry-run checklist: `docs/OPERATOR_RUNBOOK.md`.
- Root `LICENSE` (ExcellonIT sandbox review terms).
- Health / API phase → 12; CI runs phase12 tests + evidence scripts.

## Tests

| Test | Result |
| --- | --- |
| Restore drill artifact ok | pass |
| Load sample meets sandbox gate | pass |
| Deps / licence scan ok | pass |
| Rate limit returns 429 when enabled | pass |
| Runbook dry-run checklist present | pass |
| Health phase ≥ 12 | pass |
| Prior phase suites | pass (run in CI) |

## Timed restore / load

Recorded in artifacts after local/CI run (`elapsed_ms` in restore; `rps` / `p95_ms` in load). Sandbox figures only.

## Operator runbook dry-run

**23 September 2026.** Checklist in `docs/OPERATOR_RUNBOOK.md` §8 reviewed and signed for Phase 12 by **ExcellonIT programme owner** (operator role; distinct from the build agent). Pack rollback, promote-gate refusal, Talk failover, restore + load artifacts, and edge notes acknowledged. Not a UAE production cutover drill.

## What an investor can do now

See sandbox load and restore evidence, a licence inventory, and an operator runbook that someone other than the builder has dry-run signed — still clearly a sandbox.

## Explicitly not built (next phases)

- Multi-region WAF/CDN attachment (documented stand-in only; optional later)
- Phase 13 evidence freeze
- Clearing Phase 5/10/11 channel residuals

## Risks / residual defects

- True managed CDN/WAF not attached; nginx+HSTS+app rate limit is the published stand-in.
- Phase 5 *inbound DID deferred*, Phase 10 *WABA deferred*, Phase 11 *Twilio SMS deferred* unchanged.

## Status

**Awaiting Approve Phase 12.** Phase 13 stays closed until then.
