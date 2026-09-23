# Phase 05 report — Twilio Voice

Date: 23 September 2026  
Git branch: `cursor/phase-05-scaffolding-9d24`  
Live URL(s): https://haqqline.excellonit.net/ · https://haqqline.excellonit.net/#call  
Agent id: `agent_5601m1xp22apfdcbwbb8h9y5zzqt`  
Deploy: GitHub Actions rsync + `scripts/sync_elevenlabs.py` + `scripts/sync_twilio.py` (when credentials are set)

## Built (complete)

- Call section on the sandbox home page (`#call`), EN + AR, labelled as a sandbox test DID (not DLD / RERA / RDC).
- `public/twilio.json` schema: empty `phone_number` until import; `inbound_only`, `enable_sms: false`, hours, failover to Talk.
- `public/call.js` loads the number (or the Talk fallback) without exposing Twilio secrets.
- `scripts/sync_twilio.py`: Standard API key preferred, Account SID + auth token fallback; imports the DID into ElevenLabs with `enable_sms: false` and assigns the HaqqLine agent.
- CI `twilio-sync` job: skips cleanly when `TWILIO_VOICE_NUMBER` is unset; imports and rsyncs when set.
- Phase 5 multi-run agent evals: `HAQQLINE_TEST_REPEAT_COUNT` defaults to **3**. Sync writes `reports/phase-05-eval.json`.
- Phase 5 unit tests: markup, empty DID → Talk, Twilio credential preference, E.164 gate, SMS off.

## Tests

| Test | Result |
| --- | --- |
| `tests/phase5` markup + sync_twilio + multi-run unit tests | pass (CI verify green on this branch) |
| Live Call section markup on host | pass (empty DID + failover copy) |
| Multi-run agent suite (`repeat_count` ≥ 2) recorded pass rate | **owed** on next `elevenlabs-sync` after this branch deploys |
| Inbound EN gold path on purchased DID | **deferred** — Twilio secrets not loaded by owner decision |
| Inbound AR gold path on purchased DID | **deferred** — same |
| Failover copy (Twilio 5xx → Talk) | pass (on page + in `twilio.json`) |

## What an investor can do now

Open https://haqqline.excellonit.net/#talk for web voice (EN/AR). Open `#call`: the page states there is no test number yet and to use Talk. That is intentional while Twilio credentials stay out of the agent/CI secret surface.

## Twilio secrets — deferred (owner decision, 23 September 2026)

Twilio API credentials and a live Voice DID grant powerful control of the demo telephony path. The owner has **held off** adding them for now to limit abuse risk on the public sandbox. Import and inbound DID evidence are **not** requested in this iteration.

When the owner later chooses to enable telephony:

1. Add GitHub Actions secrets only (not agent chat): `TWILIO_VOICE_NUMBER`, plus `TWILIO_API_KEY_SID` + `TWILIO_API_KEY_SECRET` (preferred) or Account SID + Auth Token.
2. Let `twilio-sync` on `main` / `phase/**` write the E.164 into `public/twilio.json`.
3. Log one EN and one AR inbound; attach transcript links here; then clear this residual.

Until then, `twilio-sync` must keep skipping when `TWILIO_VOICE_NUMBER` is unset (already the behaviour).

Per `stage-2/BUILD_PLAN.md`: the **web path** is the Stage 2 deployment of record while the DID is unavailable; a filled test DID remains the full Phase 5 exit criterion and is recorded as a residual defect if Phase 5 is approved without it.

## Owner actions now

1. **Merge** this Phase 5 scaffolding PR so the Call empty-state, tests, and multi-run defaults land on `main`.
2. Reply either:
   - **Approve Phase 5** with residual defect *“inbound DID deferred — Twilio secrets not loaded”*, or
   - **Keep Phase 5 open** until DID import is intentional later.
3. Do **not** begin Stage 3 until that reply is written.

## Explicitly not built (later)

- Live Twilio DID import and inbound EN/AR evidence (deferred)
- Stage 3 enterprise spine — planned, closed until `Begin Phase N` after Phase 5 disposition
- WhatsApp / SMS

## Risks / residual defects

- **Inbound test DID not live.** Empty `phone_number` by design until secrets are added later.
- Multi-run eval artifact lands after merge deploy + `elevenlabs-sync`.

## Status

**Scaffolding complete. Twilio secrets deferred by owner.** Awaiting merge + written **Approve Phase 5** (with residual) or **Keep Phase 5 open**.
