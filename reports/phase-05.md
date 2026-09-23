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
| Multi-run agent suite (`repeat_count` ≥ 2) recorded pass rate | **owed** — runs on next `elevenlabs-sync` after this branch deploys (`phase/**` or `main`) |
| Inbound EN gold path on purchased DID | **blocked** — `phone_number` empty |
| Inbound AR gold path on purchased DID | **blocked** — `phone_number` empty |
| Failover copy (Twilio 5xx → Talk) | pass (on page + in `twilio.json`) |

## What an investor can do now

Open https://haqqline.excellonit.net/#call. Until a test DID is imported, the section says to use Talk (web voice still works). After secrets are set and `twilio-sync` succeeds, the Call section shows the E.164 number.

## Owner actions to close Phase 5

1. **Merge** this Phase 5 scaffolding PR (or promote the branch) so deploy + `elevenlabs-sync` land multi-run evidence.
2. **Add GitHub Actions secrets** (preferred Standard API key):
   - `TWILIO_VOICE_NUMBER` — purchased Voice DID, E.164 (`+…`), not a DLD/RERA/RDC line
   - `TWILIO_API_KEY_SID` — starts with `SK`
   - `TWILIO_API_KEY_SECRET`
   - Fallback if no API key: `TWILIO_ACCOUNT_SID` + `TWILIO_AUTH_TOKEN`
   - `ELEVENLABS_API_KEY` must already be present (prior syncs succeeded on `main`)
3. Confirm `twilio-sync` wrote a `+` number into live `/twilio.json`.
4. Log one English and one Arabic inbound (or Talk if DID still blocked by KYC — note in this report). Attach transcript links.
5. Reply **Approve Phase 5** when the table above is green, or **Reject** with defects.

Per `stage-2/BUILD_PLAN.md`: if the DID is blocked by KYC/stock/credentials, the **web path** remains the Stage 2 deployment of record, but a filled test DID is still the Phase 5 exit criterion.

## Explicitly not built (later)

- Stage 3 enterprise spine (Phases 6–9) — planned, closed until `Begin Phase N`
- WhatsApp (Phase 10), SMS (Phase 11)

## Risks / residual defects

- No purchased Voice DID in the secret store yet.
- Multi-run increases ElevenLabs agent-test wall time; job timeout remains 45 minutes.

## Status

**Scaffolding complete. Not signed off.** Waiting on owner: merge + Twilio secrets + inbound EN/AR evidence (or documented DID block). Stage 3 stays closed until Phase 5 is approved.
