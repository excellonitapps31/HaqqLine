# HaqqLine — architecture one-pager

**Owner:** ExcellonIT · **Host:** https://haqqline.excellonit.net · **Environment:** sandbox  
**Freeze:** Phase 13 evidence pack (`reports/phase-13-evidence.json`)

This is the programme architecture snapshot for the Ignyte × ElevenLabs Future of Voice AI Challenge and Stage 2–3 review. It does not change product behaviour.

## Surfaces

| Surface | Role |
| --- | --- |
| Static EN/AR site + playground | Investor demo shell; sandbox disclaimer on every path |
| HTTPS tools API (PHP) | Rule lookup, Ejari mock, confirm-gated filing, audit, cases, alerts, SMS outbox |
| ElevenLabs Conversational agent | Voice brain: disclosure → lookup → cite pack → file or escalate |
| Web Talk widget | Primary Stage 2 deployment of record while DID is deferred |
| Twilio Voice / WhatsApp / SMS | Channel adapters; residuals may leave numbers empty until secrets are intentional |

## Control plane

```
Caller (Talk / Call / WA / SMS)
        ↓
ElevenLabs agent (prompt + workflow + Agent Testing)
        ↓ server tools (HMAC / demo key)
PHP API  →  HaqqLinePolicy (allow / deny)
         →  signed pack (pack_version + citation_id)
         →  HaqqLineCaseStore (append-only JSONL)
         →  audit / alerts / SMS outbox
```

Policy is the enforce layer. The prompt stays UX. Pack hash/signature is verified in CI (`scripts/verify_pack_lock.py`). Eval promote gate refuses a bad agent sync (`scripts/sync_elevenlabs.py` + `sre-budgets.json`).

## Evidence anchors (already live)

| Artefact | Where |
| --- | --- |
| Idea Canvas + walkthrough | `stage-1/ElevenLabs_Idea_Canvas.docx` · https://youtu.be/ci3NsthWO0o |
| Architecture banner | `stage-1/haqqline-architecture-banner.png` |
| Sources / analysis | `stage-1/SOURCES.md` |
| Stage 2 / 3 plans | `stage-2/BUILD_PLAN.md`, `PRODUCT_SHAPE.md`, `stage-3/BUILD_PLAN.md` |
| Pass rate (recorded) | `reports/phase-04.md` — 13/13 on 22 September 2026 |
| Gold paths (primary + failure) | `elevenlabs/tests.json` · summarised in `reports/phase-13-paths.md` |
| Programme README | `README.md` |

Banner art for walkthrough framing lives beside the Idea Canvas; this page is the textual one-pager reviewers read without opening Office files.

## Explicitly not architecture (out of programme)

JustNow, live Ejari/DLD credentials, deciding case outcomes, PIN/OTP tools, App Store apps, unofficial WhatsApp libraries, labour/RTA packs before a new Gate 0.
