# HaqqLine — Phased DevOps implementation plan

**Status:** Phase 4 complete (`phase-04`). Phase 5 scaffolding complete on the Call page, sync scripts, CI, and multi-run evals; sign-off waits on a purchased Twilio Voice DID and inbound EN/AR evidence (`reports/phase-05.md`).  
**Owner:** ExcellonIT  
**Product:** HaqqLine  
**Investor demo host:** `https://haqqline.excellonit.net`  
**Rule:** one phase in flight. A phase is built, deployed, tested, reported, and signed off in writing before the next phase starts. Two phases never share a change set, branch, or deploy.

This plan is the delivery sequence. `stage-2/BUILD_PLAN.md` covers the 30 September – 14 October window inside it, under the same gates.

---

## 0. Operating rules

1. **One phase at a time.** Phase N+1 stays closed while Phase N is open. Later-phase features stay in their own phase.
2. **Complete increments.** A phase is releasable on its own: versioned, deployed to `haqqline.excellonit.net` (or a path it already serves), documented, and reversible by git tag. Hardening owed by a phase ships in that phase.
3. **Tests gate merge.** CI must be green. Phase-specific tests listed below must pass. If a test cannot be automated, a signed manual test log is attached to the phase report. A failure blocks deploy and sign-off.
4. **Sign-off, then the next phase.** Each phase ends with `reports/phase-NN.md`. Sign-off is **Approve Phase N** or **Reject** with defects. A reject stays on that phase.
5. **Git is the system of record.** No production changes from a laptop outside CI. No `--no-verify`. No force-push to `main`.
6. **Demo is not government production.** Every page, call, WhatsApp thread, and SMS states this is an ExcellonIT **sandbox**. Synthetic data only. No live DLD/RERA credentials.
7. **WhatsApp is the primary message channel; SMS is secondary.** They are **separate phases**. Voice (web, then Twilio) lands first so the agent exists before any message channel is wired.
8. **Twilio.** The account is ExcellonIT’s. Twilio voice starts only after a **Standard API Key** (SID starting `SK` + secret) is in the secret store, a **purchased** number has Voice (SMS when that phase starts), and 2FA is on in the Twilio console. Account SID + Auth Token is a fallback only.

---

## 1. What this builds

HaqqLine remains an **institutional voice-and-message agent**, not a citizen App Store product.

| Surface | Role | Phase |
| --- | --- | --- |
| `haqqline.excellonit.net` | Investor demo (disclaimer, scenarios, widget, queue view, health) | 1 then 3 |
| HTTPS APIs | Rule lookup, Ejari mock, confirmation-gated filing queue, audit | 2 |
| ElevenLabs agent | Workflows, EN+AR voice, RAG, evals | 4 |
| Web voice widget | Playable on the subdomain | 4 |
| Twilio Voice | Inbound test DID | 5 |
| WhatsApp Business via ElevenLabs | **Primary** automated messaging (text / voice notes) | 6 |
| Twilio SMS | Automated fallback and transactional notices | 7 |

JustNow is out of scope for every phase.

---

## 2. Git and promotion

**Repository:** dedicated public HaqqLine repo. JustNow and other ExcellonIT sites live elsewhere.

| Branch | Purpose |
| --- | --- |
| `main` | Only approved, deployed phase tips. Protected. |
| `phase/NN-<slug>` | The **single** active phase. Deleted after merge. |
| Tags `phase-NN` | Immutable snapshot of the signed-off phase. |

**Pipeline (every phase):**

```
phase branch → CI (lint, unit, contract, phase tests) → deploy to haqqline.excellonit.net
            → smoke against the live URL → report → sign-off → merge to main → tag
```

**Commit policy:** conventional commits, one concern, no “WIP” on `main`. Phase branch may iterate; `main` only receives a complete phase.

**Secrets:** never in git. Twilio, ElevenLabs, WhatsApp, and the webhook HMAC live in GitHub Actions secrets or on the host. The sandbox demo API key in `public/api/v1/pack/config.json` is public on purpose.

---

## 3. Target environment

| Item | Decision |
| --- | --- |
| Public URL | `https://haqqline.excellonit.net` (subdomain on the excellonit.net VPS; deploy writes into its document root) |
| TLS | Valid certificate; HTTP → HTTPS |
| Compute | Ubuntu 24.04 VPS managed by HestiaCP (nginx, PHP 8.5-FPM). Phases 1–4 ran on cPanel; the site moved to this VPS on 21 September 2026. GitHub Actions rsyncs `public/` to the subdomain document root. |
| Regions | Sandbox only. A production deployment for a UAE authority runs in a UAE region. |
| Data | Demo database only; wipeable; no real resident PII |
| Identity | Demo PIN or magic-link for investors; separate from excellonit.net marketing site |

The apex `excellonit.net` site is **not** modified in any HaqqLine phase except DNS for the subdomain.

---

## 4. Entry criteria for the whole programme (before Phase 1)

In place before Phase 1:

- [x] Gate 0 sign-off of this file
- [x] GitHub repo for HaqqLine
- [x] DNS: `haqqline.excellonit.net` on the excellonit.net host
- [x] Compute: cPanel for Phases 1–4, HestiaCP VPS from 21 September 2026
- [x] ElevenLabs workspace
- [ ] Twilio account: API Key SID + secret (preferred), purchased Voice number; SMS on that number or a second number, documented
- [ ] Meta WhatsApp Business / WABA not required until Phase 6 — Meta verification can run as paperwork only, with no code
- [ ] Arabic listen-through by a named person before any later voice sign-off that adds copy

---

## 5. Phase catalogue

### Gate 0 — Approve this plan

**Done when:** this plan is signed off. Closed; Phases 1–4 shipped from it.  
**Was out of scope at Gate 0:** application code, DNS, and CI.

---

### Phase 1 — Platform: repo, CI, subdomain, live shell

**Intent:** investors can open `https://haqqline.excellonit.net` and see a real, TLS-secured HaqqLine demo shell. No agent. No Twilio. No WhatsApp. No SMS.

**In scope**

- Repo layout, `README`, `CODEOWNERS`, branch protection  
- CI: install, lint, test job, deploy job  
- Static site (subdomain document root) that serves a **complete** demo landing: product name, sandbox banner, “not a government service”, English + Arabic chrome, `/health` JSON  
- Deploy to `haqqline.excellonit.net`  
- Uptime/health check in CI against the live host after deploy  

**Out of scope**

- Rule APIs, ElevenLabs, Twilio, WhatsApp, SMS, filing queue, investor scenario player  

**Tests (all must pass)**

- Unit: health payload schema  
- CI deploy smoke: `GET https://haqqline.excellonit.net/health` → 200  
- Manual: browser TLS padlock, disclaimer visible without scrolling on desktop  

**Live-ready means:** the subdomain is a professional sandbox shell on its own, not a 404 and not the excellonit.net marketing theme.

**Report:** `reports/phase-01.md`

---

### Phase 2 — Rule and case APIs (production-shaped sandbox)

**Intent:** a versioned HTTPS API the agent (and later WhatsApp tools) will call. Fully tested, authenticated, deployed under the same host (e.g. `/api/v1`).

**In scope**

- `lookup_rera_band`  
- `lookup_ejari` (registered or not, synthetic contract dates)  
- `submit_to_human_queue` (reject unless `caller_confirmed=true`; status always `pending_human`)  
- `escalate_human`  
- OpenAPI 3.1 served at `/api/v1/openapi.json` and a **read-only** docs UI  
- Structured audit log per request (id, tool, result, timestamp)  
- Demo API key for investors (rate-limited)  

**Out of scope**

- Voice widget, Twilio, WhatsApp, SMS, ElevenLabs, visual scenario player beyond OpenAPI  

**Tests**

- Contract tests from OpenAPI  
- Confirmation gate: unconfirmed submit → 4xx; confirmed → `pending_human`  
- Unknown area → escalate flag, **no invented index**  
- Auth: no key → 401  
- Load smoke: documented RPS for demo (not UAE production scale yet — that is Phase 8)  

**Live-ready means:** `/api/v1/docs` on the subdomain works for an investor with the demo key. No local-only Python script.

**Report:** `reports/phase-02.md`

---

### Phase 3 — Investor playground (no voice)

**Intent:** non-technical investors can **play** the gold paths in a browser: pick a scenario, see the citation, try an unconfirmed filing (blocked), confirm a filing (queued), see the queue.

**In scope**

- Scenario cards (within-band increase, over-band, missing area, “will I win?” → escalate copy)  
- Forms bound **only** to Phase 2 APIs  
- Queue / audit viewer for demo cases  
- EN/AR UI strings for this shell  
- Same sandbox banner  

**Out of scope**

- Microphone, ElevenLabs widget, phone, WhatsApp, SMS  

**Tests**

- Playwright (or equivalent) against **production URL**: three gold scenarios + blocked submit  
- A11y smoke on the two languages  
- No PII fields beyond synthetic labels  

**Live-ready means:** a rights-check completes in the browser, with no call.

**Report:** `reports/phase-03.md`

---

### Phase 4 — ElevenLabs agent + web voice on the subdomain

**Intent:** web voice on the sandbox. Agent behaviour, voice, knowledge, and evaluation run on ElevenLabs and are callable from `haqqline.excellonit.net`.

**In scope**

- Agent Workflows: Intake → RuleMatch → Filing | Escalate  
- Scripted AI disclosure (eval fails if skipped)  
- Eleven v3 + Voice Library: English + Gulf Arabic  
- Scribe v2 + keyterms (Ejari, RERA, DLD, RDC)  
- Knowledge pack version-pinned; source attribution in replies  
- Server tools pointed at **live** Phase 2 APIs  
- Official web widget (or React SDK) **on the demo site**  
- Agent Testing: multi-run pass rate + tool-call test (unconfirmed filing must not submit)  
- Conversation recording + post-call webhook into the audit store  

**Out of scope**

- Twilio numbers, WhatsApp, SMS, native iOS/Android apps, batch outbound  

**Tests**

- ElevenLabs tool-call tests: high-stakes confirm gate  
- Multi-run suite ≥10 gold dialogues EN and AR; pass rate reported  
- Live widget: one EN and one AR session from the subdomain (manual log + transcript attached)  
- Webhook 2xx on those sessions  

**Live-ready means:** investor clicks Talk on `haqqline.excellonit.net` and completes the primary flow. No dashboard-only agent.

**Report:** `reports/phase-04.md` (include pass rates and transcript links)

---

### Phase 5 — Twilio Voice

**Intent:** inbound test calls to a purchased Twilio number, native ElevenLabs Twilio integration, same agent as Phase 4.

**Entry criteria:** Twilio account ready; number purchased with Voice; credentials in the secret store; the number is a **test** DID (not published as DLD).

**In scope**

- Import number into ElevenLabs; assign HaqqLine agent  
- Inbound only for this phase (outbound calling is not required for the use case)  
- Recording on; transcripts in audit  
- Demo page lists the test number and calling hours/disclaimer  
- Failover note if Twilio returns 5xx (same agent; Talk on the page is the fallback)  

**Out of scope**

- WhatsApp, SMS, outbound campaigns, SIP trunks besides this number  

**Tests**

- Inbound EN and AR: disclosure heard, citation spoken, confirm-gate on filing  
- Failure path: advice question → escalate  
- The test number appears only on the sandbox page, with the disclaimer  

**Live-ready means:** an inbound call to the test DID completes the gold path.

**Report:** `reports/phase-05.md`

---

### Phase 6 — WhatsApp (primary automated messaging)

**Intent:** same agent, WhatsApp Business as the **primary** digital message channel (text, voice notes per ElevenLabs WhatsApp). Official ElevenLabs WhatsApp import — not an unofficial gateway.

**Entry criteria (before any code):**

- Meta WABA approved  
- Number **not** already tied to another WhatsApp provider / personal WA Business app  
- Payment method on the WhatsApp / Meta side if outbound templates will be used later in this phase  
- Template for **session-start / sandbox disclaimer** submitted and **approved** before any outbound message  

**In scope**

- Connect WABA to the **same** HaqqLine agent  
- Inbound WhatsApp conversations: disclosure, rule check via existing tools, filing confirm gate  
- Demo page: “Message the sandbox on WhatsApp” with QR / wa.me (sandbox labelled)  
- Human handoff path already in the agent (`escalate_human`)  
- Logging of WhatsApp conversation ids into audit  

**Out of scope**

- SMS  
- Marketing blasts  
- Voice-on-WhatsApp calls. Inbound messages are the acceptance test. Messages only, unless a later Phase 6b is signed off on its own.

**Tests**

- Inbound EN and AR WhatsApp: gold rent-increase + blocked unconfirmed filing  
- Disclosure present in the first agent turn  
- Tool-call confirm gate still holds on this channel  
- Opt-out / stop handling per Meta + ElevenLabs policy (documented test)  

**Live-ready means:** an investor can WhatsApp the sandbox number from the demo page and finish a scenario.

**Report:** `reports/phase-06.md`

WhatsApp is Phase 6. It is outside the Stage 1 canvas scope.

---

### Phase 7 — SMS (automated, secondary)

**Intent:** Twilio SMS for transactional automation: reference numbers, queue acknowledgements, “continue on WhatsApp” when SMS is all the device has. **Not** a second agent brain. WhatsApp stays primary.

**In scope**

- SMS send from documented events only (filing queued, escalated, reference id)  
- Inbound SMS: short commands (`STATUS <id>`) or a one-line redirect to WhatsApp/web — **no** full rights-check over SMS (too lossy for citations)  
- STOP / HELP compliance  
- Same case ids as APIs and WhatsApp  
- Demo page documents SMS as fallback  

**Out of scope**

- New LLM over SMS  
- Changing WhatsApp flows  
- Marketing SMS  

**Tests**

- Event `filing_queued` → SMS received with `pending_human` id  
- STOP → no further SMS  
- Invalid inbound → help text, no tool submit  
- No SMS on unconfirmed filing attempt  

**Live-ready means:** completing a web or WhatsApp filing produces an SMS receipt in the demo.

**Report:** `reports/phase-07.md`

---

### Phase 8 — Hardening, scale evidence, investor runbook

**Intent:** production-shaped demo: rate limits, backups, error budgets, load, runbook. Still sandbox data.

**In scope**

- Rate limits and WAF/CDN in front of the subdomain  
- Structured logs, traces, alerts on 5xx and tool failures  
- Backup/restore drill of demo DB  
- Load test numbers for concurrent widget and API calls, labelled as sandbox figures  
- Investor runbook: 15-minute script (web, voice, WhatsApp, SMS)  
- Dependency list and licence scan  

**Out of scope**

- New channels, new use cases (labour pack, RTA fines)  

**Tests**

- Load test meets the published number
- Restore drill timed and logged
- Runbook dry-run by someone other than the person who built the phase  

**Report:** `reports/phase-08.md`

---

### Phase 9 — Challenge evidence pack (only if still in the Ignyte window)

**Intent:** Stage 2 artefacts from **already live** Phases 4–5 (and 6 if approved): recordings, transcripts, analysis, architecture one-pager, README, pass rates. **No new features.**

**In scope:** export and freeze evidence.  
**Out of scope:** any behaviour change. If a test fails, that is a **defect return to the phase that owns it**, not a Phase 9 patch.

**Report:** `reports/phase-09.md`

---

## 6. Out of this programme (needs a new plan)

- JustNow integration  
- Live Ejari/DLD credentials  
- Deciding case outcomes  
- Asking for PIN/password/OTP  
- App Store / Play Store HaqqLine app  
- Mixing labour-law or RTA packs into the rental agent before a new gated plan  
- Unofficial WhatsApp libraries  

---

## 7. Phase summary report (mandatory)

After CI is green and the live URL is smoked, write `reports/phase-NN.md` in this form:

```markdown
# Phase NN report — <name>
Date:
Git SHA / tag:
Live URL(s):
Deploy method:

## Built (complete)
- …

## Tests
| Test | Result |
| --- | --- |
| … | pass / fail |

## What an investor can do now
- …

## Explicitly not built (next phases)
- …

## Risks / residual defects
- none | …

## Status
Signed off / returned with defects
```

Sign-off that starts the next phase: `Approve Phase NN`. Anything else keeps work on Phase NN.

---

## 8. Sequence

Reordering needs a new Gate 0.

```
Gate 0  this plan
   ↓
Phase 1  subdomain live shell + CI
   ↓
Phase 2  APIs
   ↓
Phase 3  investor playground (forms)
   ↓
Phase 4  ElevenLabs + web voice
   ↓
Phase 5  Twilio Voice
   ↓
Phase 6  WhatsApp (primary messaging)
   ↓
Phase 7  SMS (secondary automation)
   ↓
Phase 8  hardening + runbook
   ↓
Phase 9  challenge evidence freeze (if applicable)
```

WhatsApp and SMS are last among **channels** so Meta approval and Twilio SMS can lag without blocking voice. Paperwork for WABA may start after Gate 0; **code** for WhatsApp starts only at Phase 6.

---

## 9. Where this plan sits against the competition

| Constraint | Programme |
| --- | --- |
| Stage 1 is the Idea Canvas | `stage-1/ElevenLabs_Idea_Canvas.docx` |
| Stage 2 is the hosted page or a test number | Phase 4, then Phase 5. Both stay gated. |
| Not a live government deployment | Sandbox banner and synthetic data on `haqqline.excellonit.net` |
| WhatsApp is a later channel | Phase 6, after voice |

---

## 10. Where the programme is

Gate 0 is closed. Phases 1–4 are on `main`. Phase 5 is Twilio Voice. WhatsApp and SMS code wait for Phases 6 and 7.
