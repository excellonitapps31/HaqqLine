# Stage 2 build sprint (30 September – 14 October)

Submit: live agent (test number or web), demo recording of primary + one failure path, Agent Testing results (multi-run pass rate + one high-stakes tool-call test), transcripts and post-call analysis, one-page architecture, short README.

Do **not** build a standalone HaqqLine mobile/web app. Host = ElevenLabs widget + Twilio test DID + `sandbox/` APIs. See `PRODUCT_SHAPE.md`.

## Days 1–3 — Agent core

- Conversational agent + Workflows: Intake → RuleMatch → Filing | Escalate
- Scripted AI disclosure node (eval must fail if skipped)
- Eleven v3 voices: Gulf Arabic + English
- Scribe v2 Realtime; keyterms: Ejari, RERA, DLD, RDC, contract number
- Knowledge: signed-off pack (Decree 43/2013 bands, Law 26/2007 notice facts only)

## Days 4–7 — Tools and sandbox

- `lookup_rera_band(area, current_rent, proposed_rent)` — this repo’s `/sandbox`
- `prepare_filing` / `submit_to_human_queue` (status always `pending_human`)
- `escalate_human`
- Per-node tool scoping: filing tools only on Filing node
- Post-call webhook: transcript, recording, sources[], outcome

## Days 8–11 — Tests and languages

- Tool-call test: `submit_to_human_queue` **must not** fire without `caller_confirmed=true`
- Tool-call test: no PIN/password collection
- Multi-run: 10 gold rent-increase dialogues, EN + AR
- Failure demo: “Will I win if I sue?” → escalate, no advice
- Conversation analysis criteria: disclosure, citation, no-advice, confirmation

## Days 12–14 — Evidence pack

- Record primary call and escalation call
- Export pass rates
- Architecture PNG + README
- Latency note (target: first spoken rule answer < 180s including lookup)

Do not dial real residents or connect live DLD systems. Test numbers and synthetic Ejari records only.
