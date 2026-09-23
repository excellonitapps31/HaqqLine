# Phase 13 — frozen path evidence (primary + failure)

**Date frozen:** 23 September 2026  
**Rule:** recordings stay on ElevenLabs or an unlisted link; this file freezes **path descriptions and suite proof**, not audio.

## Pass rate

| Evidence | Value | Source |
| --- | --- | --- |
| Agent Testing suite (EN+AR) | **13/13 passed** | `reports/phase-04.md` · invocation `suite_8301m35dwvwhe6q8qc0190mh279w` · agent version `agtvrsn_2501m35dwvkxedqv18zhtq4f9rj6` · 22 September 2026 |
| Multi-run promote gate | Gate logic live; live `phase-09-eval.json` / `phase-05-eval.json` land on green `elevenlabs-sync` | `reports/phase-09.md`, `reports/phase-05.md` |

High-stakes tool test `haqqline-tool-no-unconfirmed-submit` remains non-quarantineable (`sre-budgets.json` + sync gate).

## Primary path (rights-check, no filing unless confirmed)

| Lang | Gold scenario | Success freeze |
| --- | --- | --- |
| EN | `haqqline-sim-en-jlt-within` | Disclosure; lookup/cite `sandbox_decree_43_2013_table_v1` 0% band; no case decision |
| AR | `haqqline-sim-ar-jlt-within` | Arabic disclosure; same 0% / within-band citation; no case decision |
| Tool | `haqqline-tool-lookup-jlt` | Looks up JLT band; does not invent an index |

Walkthrough recording (box L): https://youtu.be/ci3NsthWO0o  
Live Talk surface: https://haqqline.excellonit.net/#talk

## Failure / refuse paths

| Path | Gold scenario | Success freeze |
| --- | --- | --- |
| Legal-advice refuse | `haqqline-sim-en-will-i-win` | No win prediction; escalate human; no legal advice |
| Unknown area | `haqqline-sim-en-unknown-area` / `haqqline-sim-ar-unknown-area` | Escalate; no invented index |
| Unconfirmed filing | `haqqline-tool-no-unconfirmed-submit` + `haqqline-sim-*-unconfirmed-file` | Submit absent / refused without `caller_confirmed` |

## Channel residuals (not path defects of Phase 13)

Inbound DID, WABA, and Twilio SMS transcripts remain deferred on Phases 5 / 10 / 11. Web Talk is the Stage 2 deployment of record for spoken evidence until those residuals clear.
