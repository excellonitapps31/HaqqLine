# HaqqLine — Phased DevOps implementation plan

**Status:** Phase 2 in flight (`phase/02-apis`).  
**Applicant:** ExcellonIT  
**Product:** HaqqLine  
**Investor demo host:** `https://haqqline.excellonit.net`  
**Rule:** one phase in flight. That phase is built, deployed, tested, reported, and **approved by you in writing** before the next phase is touched. Two phases must never be implemented in the same change set, branch, or deploy.

This plan supersedes `stage-2/BUILD_PLAN.md` as the delivery sequence. The 14-day challenge sprint is a **subset** of Phases 1–5, not a licence to skip gates.

---

## 0. Operating rules (non-negotiable)

1. **One phase at a time.** No “while we wait” work on Phase N+1. No drive-by features from later phases.
2. **No patches.** A phase is a complete, releasable increment: versioned, deployed to `haqqline.excellonit.net` (or a path it already serves), documented, and reversible by git tag. Incomplete “we’ll harden later” work is a failed phase.
3. **Tests gate merge.** CI must be green. Phase-specific tests listed below must pass. If a test cannot be automated, a signed manual test log is attached to the phase report. Fail = no deploy, no approval request.
4. **You approve; then we proceed.** After each phase the agent publishes a summary report under `reports/`. You reply **Approve Phase N** or **Reject** with defects. Reject returns to the **same** phase. No silent continue.
5. **Git is the system of record.** No production changes from a laptop outside CI. No `--no-verify`. No force-push to `main`.
6. **Demo is not government production.** Every page, call, WhatsApp thread, and SMS states this is an ExcellonIT **sandbox**. Synthetic data only. No live DLD/RERA credentials. Aligns with the challenge rule: not deployed in real production settings.
7. **WhatsApp is the primary message channel; SMS is secondary.** They are **separate phases**. Voice (web, then Twilio) lands first so the agent exists before any message channel is wired.
8. **Twilio.** You provision and confirm the account. We do not start the Twilio voice phase until you have: Account SID, Auth Token in the secret store, a **purchased** number with Voice (+ SMS when we reach that phase), and 2FA on the Twilio console.

---

## 1. What we are building

HaqqLine remains an **institutional voice-and-message agent**, not a citizen App Store product.

| Surface | Role | Phase |
| --- | --- | --- |
| `haqqline.excellonit.net` | Investor / judge playground (disclaimer, scenarios, widget, queue view, health) | 1 then 3 |
| HTTPS APIs | Rule lookup, Ejari mock, confirmation-gated filing queue, audit | 2 |
| ElevenLabs agent | Workflows, EN+AR voice, RAG, evals | 4 |
| Web voice widget | Playable on the subdomain | 4 |
| Twilio Voice | Inbound test DID | 5 |
| WhatsApp Business via ElevenLabs | **Primary** automated messaging (text / voice notes) | 6 |
| Twilio SMS | Automated fallback and transactional notices | 7 |

JustNow is out of scope for every phase.

---

## 2. Git and promotion

**Repository:** dedicated public (or investor-visible) HaqqLine repo. Do not mix JustNow or unrelated ExcellonIT sites in this tree.

| Branch | Purpose |
| --- | --- |
| `main` | Only approved, deployed phase tips. Protected. |
| `phase/NN-<slug>` | The **single** active phase. Deleted after merge. |
| Tags `phase-NN` | Immutable snapshot of what you approved. |

**Pipeline (every phase):**

```
phase branch → CI (lint, unit, contract, phase tests) → deploy to haqqline.excellonit.net
            → smoke against the live URL → report → your approval → merge to main → tag
```

**Commit policy:** conventional commits, one concern, no “WIP” on `main`. Phase branch may iterate; `main` only receives a complete phase.

**Secrets:** never in git. Twilio, ElevenLabs, WhatsApp, and demo auth live in the host secret store. CI uses OIDC or injected secrets.

---

## 3. Target environment

| Item | Decision |
| --- | --- |
| Public URL | `https://haqqline.excellonit.net` (you create DNS + folder/host; we deploy into it) |
| TLS | Valid certificate; HTTP → HTTPS |
| Compute | **cPanel + LiteSpeed** on excellonit.net (decided Phase 1). GitHub Actions rsyncs `public/` to the subdomain document root. |
| Regions | Hosting region is the excellonit.net cPanel cluster (US-east as observed on the server). Keep it. |
| Data | Demo database only; wipeable; no real resident PII |
| Identity | Demo PIN or magic-link for investors; separate from excellonit.net marketing site |

The apex `excellonit.net` site is **not** modified in any HaqqLine phase except DNS for the subdomain (your ops).

---

## 4. Entry criteria for the whole programme (before Phase 1)

You supply or confirm:

- [ ] Gate 0 approval of **this** file  
- [ ] GitHub org/repo ownership for HaqqLine  
- [ ] DNS: `haqqline.excellonit.net` CNAME/A ready for our deploy target  
- [ ] Cloud billing / Cloud Run (or named alternative)  
- [ ] ElevenLabs workspace (commercial account; challenge credits later if shortlisted)  
- [ ] Twilio account **ready** (you own this): SID, token, purchased number planned for Voice; SMS capability on that number or a second number documented  
- [ ] Meta WhatsApp Business / WABA **not** required until Phase 6 — start Meta verification in parallel **as paperwork only**, no code  
- [ ] Contact for Arabic listen-through (named person) before Phase 4 sign-off  

---

## 5. Phase catalogue

### Gate 0 — Approve this plan

**Done when:** you write **Approve Gate 0**.  
**Not done:** any application code, DNS, or CI beyond this document.

---

### Phase 1 — Platform: repo, CI, subdomain, live shell

**Intent:** investors can open `https://haqqline.excellonit.net` and see a real, TLS-secured HaqqLine demo shell. No agent. No Twilio. No WhatsApp. No SMS.

**In scope**

- Repo layout, `README`, licence, `CODEOWNERS`, branch protection  
- CI: install, lint, test job, deploy job  
- Static site (cPanel document root) that serves a **complete** demo landing: product name, sandbox banner, “not a government service”, English + Arabic chrome, `/health` JSON  
- Deploy to `haqqline.excellonit.net`  
- Uptime/health check in CI against the live host after deploy  

**Out of scope**

- Rule APIs, ElevenLabs, Twilio, WhatsApp, SMS, filing queue, investor scenario player  

**Tests (all must pass)**

- Unit: health payload schema  
- CI deploy smoke: `GET https://haqqline.excellonit.net/health` → 200  
- Manual: browser TLS padlock, disclaimer visible without scrolling on desktop  

**Live-ready means:** if we stopped the programme here, the subdomain is a professional sandbox placeholder, not a 404 or mixed excellonit.net theme.

**Report:** `reports/phase-01.md`

---

### Phase 2 — Rule and case APIs (production-shaped sandbox)

**Intent:** a versioned HTTPS API the agent (and later WhatsApp tools) will call. Fully tested, authenticated, deployed under the same host (e.g. `/api/v1`).

**In scope**

- `lookup_rera_band`  
- `lookup_ejari` (registered / not, synthetic contract dates — matches the brief’s Ejari check)  
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

**Live-ready means:** a judge can complete a rights-check without a call.

**Report:** `reports/phase-03.md`

---

### Phase 4 — ElevenLabs agent + web voice on the subdomain

**Intent:** the scored challenge web deployment: agent behaviour, voice, knowledge, evaluation **on ElevenLabs**, callable from `haqqline.excellonit.net`.

**In scope**

- Agent Workflows: Intake → RuleMatch → Filing | Escalate  
- Scripted AI disclosure (eval fails if skipped)  
- Eleven v3 + Voice Library: English + Gulf Arabic  
- Scribe v2 + keyterms (Ejari, RERA, DLD, RDC)  
- Knowledge pack version-pinned; source attribution in replies  
- Server tools pointed at **live** Phase 2 APIs  
- Official web widget (or React SDK) **on the demo site**  
- Agent Testing: multi-run pass rate + tool-call test (unconfirmed filing must not submit)  
- Conversation recording + post-call webhook into our audit store  

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

**Entry criteria (you):** Twilio account ready; number purchased with Voice; credentials in secret store; you confirm the number is a **test** DID (not published as DLD).

**In scope**

- Import number into ElevenLabs; assign HaqqLine agent  
- Inbound only for this phase (outbound calling is not required for the use case)  
- Recording on; transcripts in audit  
- Demo page lists the test number and calling hours/disclaimer  
- Failover note if Twilio 5xx (documented, not a second product)  

**Out of scope**

- WhatsApp, SMS, outbound campaigns, SIP trunks besides this number  

**Tests**

- Inbound EN and AR: disclosure heard, citation spoken, confirm-gate on filing  
- Failure path: advice question → escalate  
- Number **not** reachable without disclaimer page listing it (avoid surprise production)  

**Live-ready means:** you can dial the test DID from your phone and complete the gold path.

**Report:** `reports/phase-05.md`

---

### Phase 6 — WhatsApp (primary automated messaging)

**Intent:** same agent, WhatsApp Business as the **primary** digital message channel (text, voice notes per ElevenLabs WhatsApp). Official ElevenLabs WhatsApp import — not an unofficial gateway.

**Entry criteria (you, before any code):**

- Meta WABA approved  
- Number **not** already tied to another WhatsApp provider / personal WA Business app  
- Payment method on the WhatsApp / Meta side if outbound templates will be used later in this phase  
- Template for **session-start / sandbox disclaimer** submitted and **approved** if we send the first outbound  

**In scope**

- Connect WABA to the **same** HaqqLine agent  
- Inbound WhatsApp conversations: disclosure, rule check via existing tools, filing confirm gate  
- Demo page: “Message the sandbox on WhatsApp” with QR / wa.me (sandbox labelled)  
- Human handoff path already in the agent (`escalate_human`)  
- Logging of WhatsApp conversation ids into audit  

**Out of scope**

- SMS  
- Marketing blasts  
- Voice-on-WhatsApp **calls** unless inbound message path is already green (if both are enabled in dashboard, inbound **messages** are the acceptance test; voice-on-WA is a stretch only if tests still pass without extra scope creep — **default: messages only** unless you approve a Phase 6b later)

**Tests**

- Inbound EN and AR WhatsApp: gold rent-increase + blocked unconfirmed filing  
- Disclosure present in the first agent turn  
- Tool-call confirm gate still holds on this channel  
- Opt-out / stop handling per Meta + ElevenLabs policy (documented test)  

**Live-ready means:** an investor can WhatsApp the sandbox number from the demo page and finish a scenario.

**Report:** `reports/phase-06.md`

**Canvas note:** Stage 1 box G currently omits WhatsApp (selection, not coverage). If the canvas is **not** yet submitted, we can add one justified line after this phase exists. If it **is** submitted, do not file a second canvas. WhatsApp remains product scope.

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
- Load test numbers written (concurrent widget + API) — honest, not “UAE population” fiction  
- Investor runbook: 15-minute script (web, voice, WhatsApp, SMS)  
- Dependency list and licence scan  

**Out of scope**

- New channels, new use cases (labour pack, RTA fines)  

**Tests**

- Load test meets the number we published  
- Restore drill timed and logged  
- Runbook dry-run by someone other than the implementer (you or a named person)  

**Report:** `reports/phase-08.md`

---

### Phase 9 — Challenge evidence pack (only if still in the Ignyte window)

**Intent:** Stage 2 artefacts from **already live** Phases 4–5 (and 6 if approved): recordings, transcripts, analysis, architecture one-pager, README, pass rates. **No new features.**

**In scope:** export and freeze evidence.  
**Out of scope:** any behaviour change. If a test fails, that is a **defect return to the phase that owns it**, not a Phase 9 patch.

**Report:** `reports/phase-09.md`

---

## 6. Explicitly never in this programme (unless you open a new plan)

- JustNow integration  
- Live Ejari/DLD credentials  
- Deciding case outcomes  
- Asking for PIN/password/OTP  
- App Store / Play Store HaqqLine app  
- Mixing labour-law or RTA packs into the rental agent before a new gated plan  
- Unofficial WhatsApp libraries  

---

## 7. Phase summary report (mandatory)

After CI is green and the live URL is smoked, the agent writes `reports/phase-NN.md` using this skeleton:

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

## Request
Approve Phase NN / Reject
```

**Your reply that unlocks the next phase:** `Approve Phase NN`  
Anything else keeps work on Phase NN.

---

## 8. Sequence (do not reorder without a new Gate 0)

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

## 9. Challenge vs this plan

| Challenge page | This plan |
| --- | --- |
| Official Idea Canvas is Stage 1 | Unchanged; still paste `stage-1/IDEA_CANVAS.md` into their template |
| Web **or** test number for Stage 2 | Phase 4 then 5 — both live-ready, still gated |
| Not live government production | Sandbox banner + synthetic data on `haqqline.excellonit.net` |
| WhatsApp listed as a platform option | Phase 6, after voice, WhatsApp-primary as you instructed |
| Box G “don’t tick everything” | Canvas can stay lean; WhatsApp is earned in Phase 6 |

---

## 10. Gate 0 request

This file is the only deliverable of Gate 0.

Reply **Approve Gate 0** to start **Phase 1 only** (repo protection, CI, `haqqline.excellonit.net` live shell). Until then: no DNS cutover work in this repo, no Twilio wiring, no WhatsApp, no SMS, no ElevenLabs agent, no Phase 2 APIs.
