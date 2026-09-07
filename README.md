# HaqqLine

**ExcellonIT** · multilingual rights-check voice agent for published Dubai rental rules.

Live sandbox: **[https://haqqline.excellonit.net](https://haqqline.excellonit.net)** · **[Try a case](https://haqqline.excellonit.net/play/)**  
This host is a demonstration, **not a government service**. It is not affiliated with DLD, RERA, or the Rental Disputes Center.

[Repository](https://github.com/excellonitapps31/HaqqLine) · Applicant: ExcellonIT · Product: HaqqLine

## What this is

HaqqLine checks a caller’s situation against signed-off published rules, answers in their language, and queues filings for a human. It does not decide cases and does not give legal advice.

The Ignyte × ElevenLabs Future of Voice AI Challenge Stage 1 submission is the official Idea Canvas only (`stage-1/IDEA_CANVAS.md` is the draft to paste). [Apply on Ignyte](https://app.ignyte.ae/public/challenges/C1607A40-2F9A-F111-9B33-6045BD14DEC9) by 23 September 2026.

## Phase 1–5

HTTPS shell, sandbox APIs, playground, ElevenLabs web voice, and an inbound Twilio test DID (secrets required). WhatsApp and SMS are later phases.

The widget is created by `scripts/sync_elevenlabs.py` (`ELEVENLABS_API_KEY`). The test number is imported by `scripts/sync_twilio.py` (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_VOICE_NUMBER`). Do not put secrets in git.

```bash
python3 -m pip install -r requirements-dev.txt
php -S 127.0.0.1:8787 -t public public/router.php
# other terminal:
HAQQLINE_API_BASE=http://127.0.0.1:8787 python3 -m pytest -q tests/phase1 tests/phase2 tests/phase3/test_play_markup.py tests/phase4 tests/phase5
```

## Layout

| Path | Purpose |
| --- | --- |
| `public/` | Files served at haqqline.excellonit.net |
| `public/play/` | Investor scenario playground |
| `tests/phase1/` | Health schema and landing tests |
| `tests/phase3/` | Playground markup and Playwright tests |
| `IMPLEMENTATION_PLAN.md` | Gated phases |
| `stage-1/` | Idea Canvas draft |
| `stage-2/` | Product shape (agent, not an app) |
| `sandbox/` | Local API sketch — replaced in Phase 2 |
| `reports/` | Phase completion reports |

## Conventions

- One phase at a time. Branch `phase/NN-…`, then merge to `main` after written approval.
- No secrets in git. Deploy uses GitHub Actions secrets over SSH.
- Host of record: cPanel at `haqqline.excellonit.net` (not Cloud Run).
