# HaqqLine — Phased DevOps implementation plan

**Status:** Phases 1–13 signed off. Voice sandbox DID **active** (`+13159020932`) with kill switch `HAQQLINE_CALL_DID_ENABLED`. Remaining residuals: Phase 10 *WABA deferred*; Phase 11 *Twilio SMS deferred* (Messaging compliance review ongoing). Programme Gate 0 sequence complete.  
**Owner:** ExcellonIT  
**Product:** HaqqLine  
**Investor demo host:** `https://haqqline.excellonit.net`  
**Rule:** one phase in flight. A phase is built, deployed, tested, reported, and signed off in writing before the next phase starts. Two phases never share a change set, branch, or deploy.

This plan is the delivery sequence. `stage-2/BUILD_PLAN.md` covers the 30 September – 14 October window. `stage-3/BUILD_PLAN.md` covers the enterprise spine (Phases 6–9) after Phase 5.

---

## 0. Operating rules

1. **One phase at a time.** Phase N+1 stays closed while Phase N is open. Later-phase features stay in their own phase.
2. **Complete increments.** A phase is releasable on its own: versioned, deployed to `haqqline.excellonit.net` (or a path it already serves), documented, and reversible by git tag. Hardening owed by a phase ships in that phase.
3. **Tests gate merge.** CI must be green. Phase-specific tests listed below must pass. If a test cannot be automated, a signed manual test log is attached to the phase report. A failure blocks deploy and sign-off.
4. **Sign-off, then the next phase.** Each phase ends with `reports/phase-NN.md`. Sign-off is **Approve Phase N** or **Reject** with defects. A reject stays on that phase. **Stage 3 and later phases also require an explicit owner start instruction (`Begin Phase N`) before any code.** Planning alone is not permission to build.
5. **Git is the system of record.** No production changes from a laptop outside CI. No `--no-verify`. No force-push to `main`.
6. **Demo is not government production.** Every page, call, WhatsApp thread, and SMS states this is an ExcellonIT **sandbox**. Synthetic data only. No live DLD/RERA credentials.
7. **Enterprise spine before message channels.** Pack governance, policy engine, case spine, and voice SRE (Phases 6–9) land before WhatsApp and SMS so every channel shares one brain and one enforce layer.
8. **WhatsApp is the primary message channel; SMS is secondary.** They are **separate phases** (10 and 11). Voice (web, then Twilio) lands first so the agent exists before any message channel is wired.
9. **Twilio.** The account is ExcellonIT’s. Twilio voice starts only after a **Standard API Key** (SID starting `SK` + secret) is in the secret store, a **purchased** number has Voice (SMS when that phase starts), and 2FA is on in the Twilio console. Account SID + Auth Token is a fallback only.
10. **No extra demo infrastructure in Stage 3+.** No second playground, no citizen App Store app, no JustNow module. The product stays agent + tools + channel embeds.

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
| Signed rule packs | Pack version, hash/signature, citation fields, band fixtures | 6 |
| Policy engine | Server-side tool allowlists and deny codes | 7 |
| Case spine | Case status machine, immutable audit, conversation linkage | 8 |
| Voice SRE + eval gates | Latency budgets, continuous multi-run gates, failover, operator runbook draft | 9 |
| WhatsApp Business via ElevenLabs | **Primary** automated messaging (text / voice notes) | 10 |
| Twilio SMS | Automated fallback and transactional notices | 11 |

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
- [ ] Meta WhatsApp Business / WABA not required until Phase 10 — Meta verification can run as paperwork only, with no code
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
- Load smoke: documented RPS for demo (not UAE production scale yet — that is Phase 12)  

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

### Phase 6 — Pack governance (signed citations)

**Intent:** the rule pack is the product of record. Every figure is attributable to a signed pack version.

**Owner start:** **in flight** after `Begin Phase N` (23 September 2026). Detail: `stage-3/BUILD_PLAN.md`.

**In scope**

- Pack manifest: version, effective dates, content hash, optional signature  
- API citation fields the agent must speak  
- CI hash lock + band regression fixtures  
- Documented pack rollback via git tag  

**Out of scope**

- Live DLD/RERA feeds, WhatsApp, SMS, new demo playgrounds  

**Tests**

- Lookup returns pack version / citation  
- Hash mismatch fails verify  
- Band fixtures; unknown area still `invented: false`  

**Live-ready means:** a spoken figure maps to a named signed pack version.

**Report:** `reports/phase-06.md`

---

### Phase 7 — Policy engine

**Intent:** LLM proposes; server-side policy decides what is executable.

**Owner start:** **signed off 23 September 2026** (`reports/phase-07.md`). Was in flight on `cursor/phase-07-policy-engine-9d24`.

**In scope**

- Tool / workflow allowlists  
- Deny reason codes in OpenAPI and audit  
- Hard backstop for confirm gate, no PIN/OTP, no `decide_case`  

**Out of scope**

- New channels, officer UI, replacing ElevenLabs workflows  

**Tests**

- Illegal tool use → policy deny + audit  
- Unconfirmed submit still blocked  
- Schema rejects credential-collection fields  

**Live-ready means:** a prompt regression cannot quietly file or invent an index.

**Report:** `reports/phase-07.md`

---

### Phase 8 — Case spine and immutable audit

**Intent:** filings and escalations are trackable cases, not only demo JSONL tails.

**Owner start:** **signed off 23 September 2026** (`reports/phase-08.md`). Was in flight on `cursor/phase-08-case-spine-9d24`.

**In scope**

- Case id + status machine (`pending_human` → `in_review` → `closed` | `returned`)  
- Durable store behind existing tool URLs  
- Immutable audit; webhook conversation linkage  
- Authenticated case/audit read APIs  

**Out of scope**

- Full officer CRM product UI, live authority queue credentials, WhatsApp, SMS  

**Tests**

- Confirmed submit creates `pending_human` case  
- Illegal status transitions rejected  
- Concurrent append-only audit holds  
- Webhook links conversation to case  

**Live-ready means:** case id → audit → conversation without ElevenLabs dashboards.

**Report:** `reports/phase-08.md`

---

### Phase 9 — Voice SRE and continuous eval gates

**Intent:** voice quality and reliability are release gates.

**Owner start:** **signed off 23 September 2026** (`reports/phase-09.md`). Was in flight on `cursor/phase-09-voice-sre-9d24`.

**In scope**

- Latency / concurrency budgets (sandbox-labelled)  
- Multi-run eval as promote gate; high-stakes tool tests never quarantined  
- Twilio failure → Talk (or documented human path)  
- Minimal actionable alerts; Arabic listen-through; operator runbook draft  

**Out of scope**

- UAE multi-region production cutover, new packs, WhatsApp, SMS  

**Tests**

- Published multi-run threshold met  
- Unconfirmed-submit tool test green  
- Timed primary path; failover exercised or signed manual log  

**Live-ready means:** a bad agent sync can be refused with evidence.

**Report:** `reports/phase-09.md`

---

### Phase 10 — WhatsApp (primary automated messaging)

**Intent:** same agent, WhatsApp Business as the **primary** digital message channel (text, voice notes per ElevenLabs WhatsApp). Official ElevenLabs WhatsApp import — not an unofficial gateway. Reuses Phases 6–9 pack, policy, and case spine.

**Owner start:** **signed off 23 September 2026** (`reports/phase-10.md`) with residual *WABA deferred*. Was in flight on `cursor/phase-10-whatsapp-9d24`.

**Entry criteria (before any code):**

- Meta WABA approved  
- Number **not** already tied to another WhatsApp provider / personal WA Business app  
- Payment method on the WhatsApp / Meta side if outbound templates will be used later in this phase  
- Template for **session-start / sandbox disclaimer** submitted and **approved** before any outbound message  

**In scope**

- Connect WABA to the **same** HaqqLine agent  
- Inbound WhatsApp conversations: disclosure, rule check via existing tools, filing confirm gate, policy denies still hold  
- Demo page: “Message the sandbox on WhatsApp” with QR / wa.me (sandbox labelled)  
- Human handoff path already in the agent (`escalate_human`)  
- Logging of WhatsApp conversation ids into the case / audit spine  

**Out of scope**

- SMS  
- Marketing blasts  
- Voice-on-WhatsApp calls. Inbound messages are the acceptance test. Messages only, unless a later Phase 10b is signed off on its own.

**Tests**

- Inbound EN and AR WhatsApp: gold rent-increase + blocked unconfirmed filing  
- Disclosure present in the first agent turn  
- Tool-call confirm gate and policy engine still hold on this channel  
- Opt-out / stop handling per Meta + ElevenLabs policy (documented test)  

**Live-ready means:** an investor can WhatsApp the sandbox number from the demo page and finish a scenario.

**Report:** `reports/phase-10.md`

WhatsApp is Phase 10. It is outside the Stage 1 canvas scope.

---

### Phase 11 — SMS (automated, secondary)

**Intent:** Twilio SMS for transactional automation: reference numbers, queue acknowledgements, “continue on WhatsApp” when SMS is all the device has. **Not** a second agent brain. WhatsApp stays primary. Same case ids as Phase 8.

**Owner start:** **signed off 23 September 2026** (`reports/phase-11.md`) with residual *Twilio SMS deferred*. Was in flight on `cursor/phase-11-sms-9d24`.

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

**Report:** `reports/phase-11.md`

---

### Phase 12 — Hardening, scale evidence, operator runbook

**Intent:** production-shaped sandbox: rate limits, backups, error budgets, load, operator runbook drill. Still synthetic data unless a separate production Gate exists.

**Owner start:** **open** — `Begin Phase 12` 23 September 2026.

**In scope**

- Rate limits and WAF/CDN in front of the subdomain  
- Structured logs, traces, alerts on 5xx and tool failures  
- Backup/restore drill of the case / audit store  
- Load test numbers for concurrent widget and API calls, labelled as sandbox figures  
- Operator runbook dry-run (pack rollback, agent rollback, number failover) by someone other than the builder  
- Dependency list and licence scan  

**Out of scope**

- New channels, new use cases (labour pack, RTA fines)  

**Tests**

- Load test meets the published number  
- Restore drill timed and logged  
- Runbook dry-run signed in the phase report  

**Report:** `reports/phase-12.md`

---

### Phase 13 — Challenge / programme evidence freeze (if applicable)

**Intent:** Stage 2–3 artefacts from **already live** phases: recordings, transcripts, analysis, architecture one-pager, README, pass rates. **No new features.**

**Owner start:** `Begin Phase 13` received 23 September 2026.

**In scope:** export and freeze evidence.  
**Out of scope:** any behaviour change. If a test fails, that is a **defect return to the phase that owns it**, not a Phase 13 patch.

**Report:** `reports/phase-13.md`

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

Sign-off that starts the next phase: `Approve Phase NN`. Stage 3+ also needs `Begin Phase NN` before coding. Anything else keeps work on the current phase.

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
Phase 5  Twilio Voice                    ← Stage 2 window
   ↓
Phase 6  Pack governance                 ┐
Phase 7  Policy engine                   │ Stage 3 enterprise spine
Phase 8  Case spine + immutable audit    │ (owner Begin Phase N only)
Phase 9  Voice SRE + continuous eval     ┘
   ↓
Phase 10 WhatsApp (primary messaging)
   ↓
Phase 11 SMS (secondary automation)
   ↓
Phase 12 Hardening + operator runbook
   ↓
Phase 13 Evidence freeze (if applicable)
```

WhatsApp and SMS stay last among **channels** so Meta approval and Twilio SMS can lag without blocking the spine. Paperwork for WABA may start after Gate 0; **code** for WhatsApp starts only at Phase 10.

---

## 9. Where this plan sits against the competition

| Constraint | Programme |
| --- | --- |
| Stage 1 is the Idea Canvas | `stage-1/ElevenLabs_Idea_Canvas.docx` |
| Stage 2 is the hosted page or a test number | Phase 4, then Phase 5. Both stay gated. |
| Stage 3 is the enterprise spine | Phases 6–9 in `stage-3/BUILD_PLAN.md`. Owner `Begin Phase N` only. |
| Not a live government deployment | Sandbox banner and synthetic data on `haqqline.excellonit.net` |
| WhatsApp is a later channel | Phase 10, after the spine |

---

## 10. Where the programme is

Gate 0 is closed. Phases 1–13 signed off. Voice DID active with `HAQQLINE_CALL_DID_ENABLED` kill switch. Residuals: WABA deferred; Twilio SMS deferred (compliance review). Further feature work needs a new Gate 0.
