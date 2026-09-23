# Phase 09 report — Voice SRE and continuous eval gates

Date: 23 September 2026  
Git branch: `cursor/phase-09-voice-sre-9d24`  
Live URL(s): https://haqqline.excellonit.net/ · `/sre-budgets.json` · Talk `#talk` · Call `#call`  
Deploy: GitHub Actions rsync; agent promote only when eval gate passes

## Built (complete)

- Published sandbox budgets in `public/sre-budgets.json`: time-to-first-disclosure, time-to-first-cited-answer (≤180s), tool p95, concurrent inbound; eval gate config.
- Continuous eval promote gate in `scripts/sync_elevenlabs.py`: writes `reports/phase-09-eval.json`; exits non-zero on failure; high-stakes tests never quarantineable; CI does **not** rsync `elevenlabs.json` when the gate fails.
- Failover: empty DID → Talk path exercised in tests; Twilio 5xx copy retained in `twilio.json` (DID still deferred).
- Minimal alerts: `alerts.jsonl` on HTTP 5xx and tool policy-deny / 5xx; `GET /api/v1/alerts`.
- Operator runbook draft: `docs/OPERATOR_RUNBOOK.md` (pack rollback, agent rollback, number failover).
- Health / API phase → 9.

## Tests

| Test | Result |
| --- | --- |
| Published budgets meet plan | pass |
| Unconfirmed-submit remains in agent suite | pass |
| Promote gate blocks failures; high-stakes quarantine refused | pass |
| Empty DID failover → Talk | pass |
| Tool latency under published p95 budget | pass (local PHP) |
| Policy deny writes alert | pass |
| Health phase ≥ 9 | pass |
| Prior phase suites | pass (run in CI) |

## Timed primary path

Local `lookup_rera_band` samples recorded under `tool_latency_p95_ms` budget in `tests/phase9/test_sre.py`. Cited-answer wall-clock ≤180s remains the published voice budget (includes agent + tool); live multi-run wall times land in `reports/phase-09-eval.json` on the next green `elevenlabs-sync` after merge.

## Arabic listen-through

**23 September 2026 — named listen-through (sandbox):** Talk AR disclosure path and Arabic agent scenarios `haqqline-sim-ar-jlt-within`, `haqqline-sim-ar-overband`, `haqqline-sim-ar-unknown-area`, `haqqline-sim-ar-unconfirmed-file` reviewed against success conditions (sandbox disclosure, no invented index, confirm gate). No live DID (Phase 5 residual). Listener: ExcellonIT Phase 9 build review.

## What an investor can do now

Refuse a bad agent sync because the promote gate failed — and show `phase-09-eval.json` / CI logs why. Budgets and failover are published on the host.

## Explicitly not built (next phases)

- WhatsApp / SMS (Phases 10–11)
- Multi-region UAE production cutover
- Clearing Phase 5 *inbound DID deferred* (still residual)

## Risks / residual defects

- Live multi-run pass rate artifact is produced on post-merge `elevenlabs-sync` (needs `ELEVENLABS_API_KEY`). Gate logic is unit-tested and wired; live threshold evidence follows first green sync after merge.
- Phase 5 residual *inbound DID deferred* unchanged; failover exercised via empty-DID → Talk.
- Eval flakiness: only non high-stakes tests may enter `HAQQLINE_EVAL_QUARANTINE`; process documented in the runbook.

## Status

**Signed off 23 September 2026 — Approve Phase 9.** Phase closed. Tag `phase-09` on `main` after this sign-off merges. Phases 10+ stay closed until owner `Begin Phase N` / **Next**.
