# HaqqLine — Stage 3 enterprise build plan

**Status:** Phases 6–7 signed off. **Phase 8 (case spine) closed** until owner `Begin Phase N`. Phase 9 stays closed until Phase 8 is approved.  
**Owner:** ExcellonIT  
**Live host:** https://haqqline.excellonit.net (sandbox until an authority production cutover is separately signed)  
**Product shape:** `stage-2/PRODUCT_SHAPE.md`  
**Programme:** `IMPLEMENTATION_PLAN.md`  
**Prerequisite:** Phase 5 signed off (residual *inbound DID deferred*).

This plan raises HaqqLine from an excellent sandbox proof to an **authority-shaped capability**: signed rule packs, a hard policy layer, a case spine officers can trust, and voice SRE with continuous eval gates. Message channels (WhatsApp, SMS) stay **after** that spine.

It does **not** add more demo playgrounds, citizen apps, or marketing surfaces.

---

## 0. Operating rules (Stage 3)

These rules sit on top of `IMPLEMENTATION_PLAN.md` §0.

1. **Owner start only.** A Stage 3 phase does **not** begin until the owner gives a written instruction to start that phase (for example: `Begin Phase 6`). Planning this file is not permission to code.
2. **One phase in flight.** Phase N+1 stays closed while Phase N is open. No shared branch, change set, or deploy across two phases.
3. **Build → deploy → test → report → approve.** Exit is `reports/phase-NN.md` plus written **Approve Phase N**. Reject keeps work on that phase.
4. **No extra demo infrastructure.** No new investor collages, no second playground, no App Store app, no JustNow integration. Surfaces stay the agent, tools, and existing host embeds.
5. **Synthetic data until a production cutover plan.** Still not a government service on this host. Live DLD / RERA / RDC credentials need a separate Gate.
6. **Channels after the spine.** WhatsApp and SMS (Phases 10–11) do not start until Phases 6–9 are signed off.
7. **Git is the system of record.** Phase branch `phase/NN-<slug>` → green CI → deploy/smoke → report → sign-off → merge → tag `phase-NN`.

---

## 1. Done when Stage 3 closes

A reviewer (and later an authority technical counterpart) can show:

1. Every spoken or tool-returned figure cites a **signed pack version** with effective dates.
2. High-stakes actions are blocked by a **server-side policy engine**, not only by the prompt.
3. Filings and escalations land in a **case spine** with stable ids, status machine, and immutable audit; conversation webhooks link to cases.
4. Voice quality is gated by **continuous multi-run evals**, latency budgets, and a documented failover path — not a one-off challenge sample.
5. WhatsApp / SMS (if later approved) reuse the same tools and policy; they do not become a second brain.

No resident PII in the sandbox. No `decide_case`. No PIN / password / OTP tools.

---

## 2. Baseline entering Stage 3

| Piece | State |
| --- | --- |
| Phases 1–4 on `main` | Live sandbox shell, APIs, playground, web voice |
| Phase 5 | Twilio Call scaffolding; DID import when secrets exist; Stage 2 evidence window |
| Storage | JSONL + `flock` under `public/api/data/` |
| Auth | Public demo API key + per-IP rate limit |
| Pack | Static `sandbox_decree_43_2013_table_v1` in git |
| Evals | Agent Testing suite; multi-run default in sync script |

Stages 1–2 stay frozen except for defects owned by their phases.

---

## 3. Phase catalogue (Stage 3)

### Phase 6 — Pack governance (signed citations)

**Intent:** the rule pack is the product of record. Every figure is attributable to a signed pack version.

**Owner start phrase:** `Begin Phase 6`

**In scope**

- Pack manifest: `pack_id`, version, `effective_from` / `effective_to`, content hash, optional signature file
- API responses include pack version + citation id the agent must speak
- CI fails if pack JSON drifts from the locked hash without a version bump
- Regression fixtures: known areas → known band answers for the signed version
- Rollback: redeploy previous pack version by git tag; document the procedure in `OPERATIONS.md`

**Out of scope**

- Live DLD/RERA data feeds  
- New demo UI beyond citing the version on existing surfaces if already shown  
- WhatsApp / SMS  

**Tests**

- Lookup returns pack version and citation fields  
- Hash/signature mismatch fails verify job  
- Band fixtures pass for the signed pack; unknown area still escalates with `invented: false`  

**Live-ready means:** an investor (or auditor) can name the pack version behind a spoken figure from the API response and the transcript.

**Report:** `reports/phase-06.md`

---

### Phase 7 — Policy engine (LLM proposes; policy executes)

**Intent:** hard server-side policy between the agent and tools. Prompt rules are mirrored in code.

**Owner start phrase:** `Begin Phase 7`

**Entry criteria:** Phase 6 signed off.

**In scope**

- Policy module: workflow node / tool allowlists (e.g. Intake cannot submit; Filing cannot invent bands)
- Enforce existing gates in one place: `caller_confirmed`, no PIN/OTP fields, no `decide_case`, escalate-only paths for advice questions at the tool boundary where applicable
- Structured deny responses (`policy_denied` with reason codes) written to audit
- OpenAPI documents deny codes

**Out of scope**

- New channels  
- Replacing ElevenLabs workflows (they stay; policy is the backstop)  
- Officer UI  

**Tests**

- Unconfirmed submit → 400 / policy deny (unchanged contract or stricter)  
- Disallowed tool from a simulated node context → deny + audit entry  
- Schema rejects PIN/password/OTP property names if present  
- Contract tests for deny reason codes  

**Live-ready means:** a prompt regression cannot quietly file or invent an index; the API still blocks it.

**Report:** `reports/phase-07.md`

---

### Phase 8 — Case spine and immutable audit

**Intent:** filings and escalations are cases officers can track, not only JSONL tails for a demo.

**Owner start phrase:** `Begin Phase 8`

**Entry criteria:** Phase 7 signed off.

**In scope**

- Case model: id, type (`filing` | `escalation`), status (`pending_human` → `in_review` → `closed` | `returned`), timestamps, pack version, conversation id when known
- Durable store behind the same tool URLs (migration path from JSONL; no citizen app)
- Immutable audit stream (append-only, retention note in `SECURITY.md`)
- Webhook linkage: post-call / conversation ids attach to the case
- Read APIs for case by id and audit by case id (authenticated; still sandbox credentials until a later cutover)

**Out of scope**

- Full officer CRM UI or dashboard product  
- Live authority queue integration (adapter interface may be sketched; no live credentials)  
- WhatsApp / SMS  

**Tests**

- Confirmed submit creates a case in `pending_human`  
- Status transitions are validated; illegal transitions rejected  
- Audit entries for a case are complete and append-only under concurrent writes  
- Webhook with conversation id links to an existing or new case record  

**Live-ready means:** a reviewer can follow case id → audit → conversation without opening ElevenLabs dashboards.

**Report:** `reports/phase-08.md`

---

### Phase 9 — Voice SRE and continuous eval gates

**Intent:** voice quality and reliability are release gates, not challenge souvenirs.

**Owner start phrase:** `Begin Phase 9`

**Entry criteria:** Phase 8 signed off.

**In scope**

- Published budgets: time-to-first-disclosure, time-to-first-cited-answer (≤180s including lookup), tool p95, concurrent inbound target (sandbox-labelled numbers)
- Continuous eval: multi-run suite is a CI/release gate; failed high-stakes tool-call tests block agent promote
- Failover note and tested behaviour: Twilio 5xx → Talk (or human IVR stub documented)
- Structured logs / alerts on 5xx and tool failures (minimal: actionable, not a vanity observability stack)
- Named Arabic listen-through logged in the phase report before sign-off
- Operator runbook draft: pack rollback, agent rollback, number failover (authority-facing tone; still sandbox host)

**Out of scope**

- Multi-region UAE production cutover (separate Gate)  
- New features or packs  
- WhatsApp / SMS  

**Tests**

- Multi-run pass rate meets the published threshold in `reports/phase-09-eval.json`  
- Unconfirmed-submit tool test remains green  
- Timed primary path note in the report  
- Failover path exercised or signed manual log  

**Live-ready means:** ExcellonIT can refuse a bad agent sync because the gate failed — and show why.

**Report:** `reports/phase-09.md`

---

## 4. After Stage 3 (programme Phases 10–13)

Only after Phases 6–9 are approved:

| Phase | Name | Note |
| --- | --- | --- |
| 10 | WhatsApp (primary messaging) | Same agent, tools, and policy. Official WABA only. |
| 11 | SMS (secondary automation) | Receipts / status; not a second brain. |
| 12 | Hardening + operator runbook drill | WAF/CDN, load evidence, restore drill — still synthetic data unless a production Gate exists. |
| 13 | Evidence freeze | Export and freeze; no behaviour change. |

Detail for 10–13 remains in `IMPLEMENTATION_PLAN.md`. Stage 3 does not start them.

---

## 5. Acceptance across Stage 3

| Check | Owning phase | Proof |
| --- | --- | --- |
| Spoken figure cites signed pack version | 6 | Transcript + API field |
| Policy deny on illegal tool use | 7 | Automated test + audit |
| Case id with status machine + immutable audit | 8 | API + report |
| Multi-run eval gate + latency note | 9 | Eval artifact + report |
| Host still not a government service | all | Landing / disclosure tests |
| No PIN/OTP/`decide_case` | 7 (+ earlier) | Schema + policy tests |

---

## 6. Environments

| Environment | Role in Stage 3 |
| --- | --- |
| Local | PHP server + pytest; pack fixtures |
| CI | verify, phase tests, hash/policy gates as each phase adds them |
| Sandbox host | Still `haqqline.excellonit.net`. Synthetic data. |

UAE-region production residency and live authority credentials are **out of Stage 3** until a separate Gate 0-style production plan is signed.

---

## 7. Risks

| Risk | Response |
| --- | --- |
| Pressure to open WhatsApp before the spine | Refuse; Phases 10+ stay closed until 6–9 approve |
| Pack signing becomes theatre without fixtures | Phase 6 exit requires band regression fixtures |
| Policy engine duplicates prompt forever | Prompt stays UX; policy is the enforce layer — both tested |
| Case spine turns into a dashboard build | Read APIs + audit only; no officer product UI in Phase 8 |
| Eval flakiness blocks all deploys | Threshold + quarantine process documented in Phase 9 report; high-stakes tool tests never quarantined |

---

## 8. How work starts

```
Owner: "Begin Phase N"
        ↓
phase/NN-<slug> branch → implement → CI green → deploy/smoke
        ↓
reports/phase-NN.md → Owner: "Approve Phase N" | "Reject"
        ↓
merge + tag phase-NN → wait for next Begin instruction
```

**Current instruction state:** Phase 7 is **signed off**. Phase 8 stays closed until the owner says `Begin Phase N` (or **Next**).
