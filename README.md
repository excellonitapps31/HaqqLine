# HaqqLine

**ExcellonIT** · multilingual rights-check voice agent for published Dubai rental rules.

Live sandbox: **[https://haqqline.excellonit.net](https://haqqline.excellonit.net)** · **[Try a case](https://haqqline.excellonit.net/play/)**  
This host is a demonstration, **not a government service**. It is not affiliated with DLD, RERA, or the Rental Disputes Center.

## What this is

HaqqLine checks a caller’s situation against signed-off published rules, answers in their language, and queues filings for a human. It does not decide cases and does not give legal advice.

This repository is ExcellonIT’s HaqqLine sandbox: the public host, the sandbox APIs, and the ElevenLabs agent behind Talk. The Stage 1 Idea Canvas for the Ignyte × ElevenLabs Future of Voice AI Challenge is `stage-1/ElevenLabs_Idea_Canvas.docx`.

## Stack

| Layer | Technology |
| --- | --- |
| Web client | Static HTML, CSS, and vanilla JavaScript. English and Arabic (RTL) in one page. IBM Plex Sans, IBM Plex Sans Arabic, and Newsreader from Google Fonts. |
| Voice agent | ElevenLabs Agents: `eleven_v3_conversational` voices for English and Gulf Arabic, Scribe realtime transcription, a Workflow graph (Intake → RuleMatch → Filing or Escalate), knowledge base, server tools, and Agent Testing. LLM is `gemini-2.5-flash`, configured on the agent. |
| Web voice | ElevenLabs ConvAI widget (`@elevenlabs/convai-widget-embed`) |
| Telephony | Twilio Voice number imported into ElevenLabs through `POST /v1/convai/phone-numbers` |
| API | PHP with `strict_types`, no framework, no Composer. OpenAPI 3.1 contract at `public/api/v1/openapi.json`. |
| Storage | Append-only JSONL files under `public/api/data/` with `flock`. No database. |
| Webhooks | ElevenLabs post-call webhook, HMAC-SHA256 signed, 30-minute clock skew |
| Sync scripts | Python 3.12, standard library only (`urllib`, `ssl`, `json`) |
| Tests | pytest, Playwright (Chromium), PHP built-in server for local runs |
| CI/CD | GitHub Actions: verify, rsync over SSH, live smoke, agent sync, number sync |
| Host | Ubuntu 24.04 VPS managed by HestiaCP: nginx and PHP 8.5-FPM. Let’s Encrypt TLS issued by HestiaCP, HTTPS forced, HSTS on. |

## Phase 1–5 and Stage 3

HTTPS shell, sandbox APIs, playground, voice, Call/WhatsApp/SMS (channel residuals deferred), Phase 12 hardening signed off, and Phase 13 evidence freeze in flight. Detail: `IMPLEMENTATION_PLAN.md`.

```bash
python3 -m pip install -r requirements-dev.txt
php -S 127.0.0.1:8787 -t public public/router.php
# other terminal:
HAQQLINE_API_BASE=http://127.0.0.1:8787 HAQQLINE_DISABLE_RATE_LIMIT=1 python3 -m pytest -q tests/phase1 tests/phase2 tests/phase3/test_play_markup.py tests/phase4 tests/phase5 tests/phase6 tests/phase7 tests/phase8 tests/phase9 tests/phase10 tests/phase11 tests/phase12 tests/phase13
python3 scripts/verify_pack_lock.py
python3 scripts/backup_restore_drill.py
python3 scripts/deps_licence_scan.py
HAQQLINE_API_BASE=http://127.0.0.1:8787 HAQQLINE_DISABLE_RATE_LIMIT=1 python3 scripts/load_test.py
python3 scripts/freeze_evidence.py
```

## Layout

| Path | Purpose |
| --- | --- |
| `public/` | Files served at haqqline.excellonit.net |
| `public/play/` | Scenario playground |
| `public/api/v1/pack/` | Signed pack (`config.json` manifest + areas/ejari); lock via `scripts/verify_pack_lock.py` |
| `tests/` | Phase tests, including Playwright for the playground |
| `IMPLEMENTATION_PLAN.md` | Delivery sequence |
| `stage-2/BUILD_PLAN.md` | 30 September – 14 October window |
| `stage-2/PRODUCT_SHAPE.md` | What is in the product, and what is not |
| `stage-3/BUILD_PLAN.md` | Enterprise spine (Phases 6–9); owner start only |
| `stage-1/` | Idea Canvas (`ElevenLabs_Idea_Canvas.docx`), `SOURCES.md`, and the architecture banner for the walkthrough video |
| `OPERATIONS.md` | Deploy, smoke, and failure checks |
| `SECURITY.md` | Sandbox limits and where secrets live |
| `.env.example` | Variable names for local sync. No values. |
| `sandbox/` | Local API sketch from before Phase 2 |
| `docs/` | Operator runbook, nginx headers, architecture one-pager |
| `reports/` | Phase completion reports + evidence freeze pack |

## Conventions

- One phase at a time. Each phase is built on `phase/NN-…` and merged to `main` after sign-off. Stage 3+ also needs a written `Begin Phase N` before coding.
- No secrets in git. Deploy uses GitHub Actions secrets over SSH.
- Host of record: the HestiaCP VPS behind `haqqline.excellonit.net`. Deploys run as a dedicated SSH user that can write only the HaqqLine document root.
