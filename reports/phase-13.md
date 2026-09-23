# Phase 13 report — Challenge / programme evidence freeze

Date: 23 September 2026  
Git branch: `cursor/phase-13-evidence-9d24`  
Live URL(s): https://haqqline.excellonit.net/ · `/health` · Talk `#talk`  
Deploy: GitHub Actions rsync after merge (docs + health only; no tool/prompt behaviour change)

## Built (complete)

- Architecture one-pager: `docs/ARCHITECTURE.md` (control plane + evidence anchors).
- Frozen path cards (primary EN/AR + failure/refuse): `reports/phase-13-paths.md`.
- Evidence export/verify: `scripts/freeze_evidence.py` → `reports/phase-13-evidence.json` (SHA-256 of Stage 1–3 artefacts, 13/13 pass rate, walkthrough URL).
- Health / API phase → 13; CI runs `tests/phase13` + freeze script.
- No pack, policy, prompt, workflow, or channel behaviour changes.

## Tests

| Test | Result |
| --- | --- |
| Freeze artifact ok + 13/13 pass rate | pass |
| Architecture one-pager present | pass |
| Primary + failure gold paths listed | pass |
| Pack lock unchanged by freeze | pass |
| Health phase ≥ 13 | pass |
| Prior phase suites | pass (run in CI) |

## What an investor can do now

Read one freeze pack: architecture one-pager, hashed artefact list, recorded 13/13 pass rate, primary and failure path cards, and the Stage 1 walkthrough at https://youtu.be/ci3NsthWO0o — without needing dashboard login.

## Explicitly not built (out of programme / residuals)

- Behaviour changes of any kind (defect returns to the owning phase)
- Clearing Phase 5/10/11 channel residuals (DID / WABA / Twilio SMS)
- Committing audio recordings (stay on ElevenLabs / unlisted links)

## Risks / residual defects

- Live multi-run eval JSON (`phase-05-eval.json` / `phase-09-eval.json`) still lands on green `elevenlabs-sync`; freeze cites the recorded Phase 4 13/13 and the gate wiring.
- Channel residuals unchanged.

## Status

**Awaiting Approve Phase 13.** Programme evidence freeze candidate.
