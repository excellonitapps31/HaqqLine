# Phase 05 report — Twilio Voice

Date: 23 September 2026 (residual clear 23 September 2026)  
Git branch: `cursor/wire-twilio-did-9d24`  
Live URL(s): https://haqqline.excellonit.net/ · https://haqqline.excellonit.net/#call  
Agent id: `agent_5601m1xp22apfdcbwbb8h9y5zzqt`  
Deploy: GitHub Actions rsync + `scripts/sync_elevenlabs.py` + `scripts/sync_twilio.py`

## Built (complete)

- Call section on the sandbox home page (`#call`), EN + AR, labelled as a sandbox test DID (not DLD / RERA / RDC).
- **Active sandbox DID:** `+13159020932` published via `public/twilio.json` (`enabled: true`, `enable_sms: false`).
- Abuse kill switch: `HAQQLINE_CALL_DID_ENABLED` (default on). Set `0` and re-run `scripts/sync_twilio.py` to unpublish the number and clear the Twilio Voice webhook.
- `public/call.js` loads the number, or Talk / paused copy, without exposing Twilio secrets.
- `scripts/sync_twilio.py`: imports the DID into ElevenLabs with `enable_sms: false`, assigns the HaqqLine agent; respects the kill switch.
- CI `twilio-sync` job: imports and rsyncs when `TWILIO_VOICE_NUMBER` is set; honours `HAQQLINE_CALL_DID_ENABLED`.
- Phase 5 multi-run agent evals: `HAQQLINE_TEST_REPEAT_COUNT` defaults to **3**. Sync writes `reports/phase-05-eval.json`.

## Tests

| Test | Result |
| --- | --- |
| `tests/phase5` markup + sync_twilio + kill-switch unit tests | pass |
| Live Call section shows DID when enabled | owed after merge + green `twilio-sync` |
| Multi-run agent suite (`repeat_count` ≥ 2) recorded pass rate | owed on green `elevenlabs-sync` |
| Inbound EN/AR gold path on DID | owed after ElevenLabs import confirms Voice webhook |
| Failover / pause copy (kill switch / Twilio 5xx → Talk) | pass (unit) |

## What an investor can do now

Open https://haqqline.excellonit.net/#talk for web voice (EN/AR). Open `#call` for the sandbox test DID (`+13159020932`) when `enabled: true`. Still an ExcellonIT sandbox — not a DLD / RERA / RDC line.

## Residual clear — inbound DID

**Cleared 23 September 2026.** Twilio account lists `+13159020932` in-use with Voice. Secrets + kill switch are intentional. ElevenLabs import runs via `twilio-sync` when `ELEVENLABS_API_KEY` and Twilio secrets are present in Actions.

## Still deferred

- **SMS on this DID:** Twilio number capability includes SMS, but **Messaging compliance review is ongoing**. `enable_sms` stays `false`; Phase 11 residual remains until compliance clears and `sms-sync` is intentional.
- WABA (Phase 10) unchanged.

## Status

**Phase 5 residual *inbound DID deferred* cleared.** Voice Call path is active with abuse kill switch. Tag / report update ships on this branch after CI green.
