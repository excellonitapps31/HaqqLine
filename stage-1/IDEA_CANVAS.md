# ElevenLabs Idea Canvas — paste into the official template only

Word counts below are Python `split()` counts. If the official box is tighter, cut from the end; text past the printed limit is not marked.

Replace every `[BRACKET]` before paste.

---

## A · Submission details

**Track:** Government Services  
**Use case:** Rights Checks & Dispute Prevention  
**Product:** HaqqLine  
**Applicant / team:** ExcellonIT  
**Lead:** Jeremiah Idakabor, Founder & Principal Software Engineer  
**Email:** swissknife@excellonit.net  
**Org site:** https://excellonit.net  
**Phone:** [PHONE]  
**Country:** [COUNTRY]  
**Ignyte profile:** [URL]

*(Fill the template’s form fields. Do not exceed its character limits.)*

---

## B · The idea in one line

HaqqLine is the authority’s recorded voice line that checks a caller’s situation against signed-off published rules, answers in their language, and queues filings for humans.

**Words:** 28

---

## C · What breaks today

Dubai already publishes the RERA rental index, Ejari records, and tenancy notice rules. The resident still has to find, interpret, and apply them. Government and bank-style phone lines are staffed in English and Arabic. That leaves Hindi, Urdu, Malayalam and other large expatriate languages without a factual voice answer. Rumour and typing centres fill the gap. Cases that a same-call index check would close still reach the Rental Disputes Center — which already runs on the order of 25,000 cases a year. Officers then spend settlement capacity (six days on average in Q2 2025) on disputes that were knowable at first contact. The break is not missing law. It is missing a governed, multilingual, auditable voice check that states published fact and never decides the case.

**Words:** 126

---

## D · Today’s baseline

(Figures J will move. Sources in `SOURCES.md`.)

1. Staffed voice languages for this class of query: **2** (English, Arabic). Caller base includes large Hindi–Urdu and Malayalam communities; UAE population ~10.33m, ~89% expatriate.
2. Automated, source-attributed rule-check on that voice channel: **0 per 100 contacts** (not a productised service today).
3. Institutional load the buyer already publishes: **~25,000 RDC cases in 2024**; **443 reconciliations in Q2 2025**; **6-day** average settlement.
4. Time-to-factual-answer in the caller’s language for a rent-increase band: **not available on the voice channel** (hours or a typing-centre visit).
5. Top dispute types officers already name: eviction for non-payment, rent renewal, compensation — the second is exactly an index-check problem.

**Words:** 112

---

## E · Who buys this

**Economic / operational buyer:** Senior Director, rental regulation and disputes (DLD / RDC). They own preventable caseload and citizen contact quality.  
**Sponsor:** Director of Digital Services (city digital authority) against happiness and first-contact resolution KPIs.  
**Adjacent expansion (same agent, new signed-off pack):** Director of Labour Relations (end-of-service arithmetic against Federal Decree-Law 33/2021); Director of Customer Service, transport authority (fine contestability against published schedules).  
**Budget line:** existing contact-centre and digital-services opex, not a new court.  
**Pilot:** one inbound test DID plus a widget on the public RERA/Ejari explainer page.  
**Commercial:** ExcellonIT licenses HaqqLine as a product (session capacity + signed-off rule-pack implementation), not a staff-augmentation contract. Ignyte/DIFC intro to the named roles. No consumer revenue.

**Words:** 118

---

## F · The call flow in five steps

1. **Disclose.** Answer in detected language. Scripted node: “I am this authority’s AI information line, not a lawyer. I apply published rules. This call is recorded.” Continue only on consent.
2. **Slot.** Party, area, current rent, proposed rent, renewal date, notice given. Optional Ejari id. Scribe keyterms: Ejari, RERA, DLD, RDC.
3. **Match.** Server tool `lookup_rera_band` plus RAG over the signed-off pack (Decree 43/2013 bands; Law 26/2007 notice facts). Speak the band and **cite the document**. If the tool errors, escalate — never invent an index.
4. **File or close.** If the increase is within band, close with the citation. If the caller still wants to file, read back the packet, require an explicit yes, then `submit_to_human_queue` with status `pending_human` only.
5. **Escalate.** Advice, hardship, silence in the pack, or “will I win?” → `escalate_human` with transcript and sources. Issue a reference number.

**Words:** 155

---

## G · ElevenLabs components (selection, not coverage)

**Using, and why**

- **Workflows + system prompt + two sub-agents** (Intake, RuleMatch/Filing): branching with per-node tool scope.
- **Eleven v3 + Voice Library:** Gulf Arabic and English now; Urdu/Hindi voices next. Natural disclosure and numbers.
- **Scribe v2 Realtime + keyterm biasing:** Ejari, RERA, policy numbers.
- **Knowledge base RAG + source attribution:** judges require “which document”; this is the product.
- **Webhook/server tools:** sandbox index and human queue; privileged actions not on the untrusted node.
- **Twilio or web widget:** inbound demo without batch campaigns.
- **Agent Testing, Simulate Conversations, conversation analysis, post-call webhooks:** Stage 2 evidence.

**Not using in the sprint:** batch outbound (this use case is inbound); WhatsApp (phase 2); native mobile SDKs (widget is enough); live DLD MCP (sandbox REST). Ticking every box would score lower.

**Words:** 148

---

## H · How it integrates

Callers hit an ElevenLabs Twilio test number or React widget. The agent sends signed HTTPS tool calls to our sandbox (`lookup_rera_band`, `prepare_filing`, `submit_to_human_queue`, `escalate_human`). Dynamic variables carry language and consent id. Post-call webhook writes recording URL, transcript, `sources_cited[]`, tool payloads, and outcome `answered | filing_queued | escalated`. The untrusted-caller agent has no credentials that can change a live government record. Production path is the same contract against DLD/RERA APIs behind a bank-grade gateway, UAE-region storage, and the authority’s SSO for the human queue. 100% of actions are API/webhook.

**Words:** 98

---

## I · Guardrail table (mechanisms, not intent)

| # | Requirement | Enforcement mechanism |
| --- | --- | --- |
| 1 | Identifies as the institution’s AI; not a lawyer | Workflow node 1 is a **fixed script**. Agent Testing fails any run that omits the disclosure before the first question. |
| 2 | Information, not legal advice; no case outcome | Prompt ban-list (“you should sue”, “you will win”). RAG **only** the signed-off pack. No `decide_case` tool exists. Eval suite of interpretation prompts must escalate. |
| 3 | Rule-matching logic signed off before launch | Knowledge and band table are **version-pinned**. Change requires a human sign-off artefact in git. Runtime refuses unsigned pack ids. |
| 4 | Filing is confirmation-gated and human-reviewed | `submit_to_human_queue` is scoped to the Filing node and **rejects** unless `caller_confirmed=true`. Always writes `pending_human`. Tool-call test covers the reject path. |
| 5 | Never requests PIN, password, or OTP | Those tools are absent. Transcript regex + eval fail the run if they appear. |
| 6 | 100% recorded and attributable | Platform recording + Scribe transcript + post-call webhook are mandatory. Demo fails if webhook 4xx. Retention set to challenge/test policy only. |

---

## J · Success metrics

Measured against box D.

| D baseline | J target (pilot / Stage 2 demo) |
| --- | --- |
| 2 staffed voice languages | EN + AR live on 14 Oct; Urdu scripted path documented |
| 0 source-attributed automated checks / 100 contacts | ≥80 / 100 in-scope rent-increase **test** dialogues cite the pack (multi-run pass rate) |
| Factual answer not available on the voice channel | Spoken band + citation in **<180 seconds** on the happy path (latency log) |
| ~25,000 RDC cases/year; 6-day settlement | Of sandbox calls where proposed rent is **within** band: ≥70% end **without** a filing, with citation (prevention proxy — not a claim we already cut 25,000) |
| Filing quality | 100% of submits have required fields; 0 submits without confirmation (tool-call tests) |
| Advice-seeking | 100% of gold “will I win?” runs escalate |

**Words:** 118

---

## K · Risks

**Wrong band quoted.** Version-pinned table; gold-case evals; tool failure escalates; no free-form arithmetic in the LLM.  
**Heard as legal advice.** Disclosure eval + ban-list + human sign-off of matching logic, not a footer.  
**Invented Ejari.** Agent may not state a registration that the tool did not return.  
**PII / live systems.** Challenge rule: test numbers and synthetic records only.  
**Arabic quality.** Native review of 20 utterances; Voice Library swap if evals fail.  
**ElevenLabs terms / impersonation.** Always AI-identified; not production government telephony.  
**Index lag.** Pack states the publication date; if caller’s area is missing, escalate.

**Words:** 96

---

## L · Working by 14 October

- Live widget + Twilio **test** number.
- End-to-end EN and AR: rent-increase check with spoken citation.
- Failure recording: advice question → human queue, no recommendation.
- Tool-call tests: submit blocked without confirmation; PIN never collected.
- ≥10 simulated scenarios; reported multi-run pass rate.
- Transcripts, analysis, architecture page, README.
- Sandbox covering five Dubai areas.
- Not in scope for 14 Oct: live Ejari, labour pack, WhatsApp, real residents.

**Words:** 78

---

## M · Team

**Jeremiah Idakabor, Founder & Principal Engineer, ExcellonIT** — decade shipping Flutter/Laravel/React production systems for fintech, healthcare, logistics, legal-tech and public-health clients; architecture audits, Cloud Run/AWS, fractional CTO.

Sprint: agent config, sandbox APIs, evals and demo owned in-house. Arabic listen-through and decree pack sign-off are named advisors, not the runtime. ExcellonIT is the vendor a DLD/RDC buyer already knows how to contract; HaqqLine is the product they would pilot.

**Words:** 92

---

## N · Proof of build

**Working link (required):** https://excellonit.net  

Live company site: production consultancy portfolio, analytics case studies, and contact. Challenge build: [PUBLIC GITHUB URL for this HaqqLine repo]. Box N is scored on a working link; excellonit.net is already live. Add the public GitHub URL before submit. Private unpublished apps are not used here.

**Words:** 58 + URLs
