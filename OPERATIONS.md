# Operations

Sandbox host: https://haqqline.excellonit.net  
Compute: cPanel + LiteSpeed. Document root is the deploy path in the `DEPLOY_PATH` secret.  
TLS: Let’s Encrypt via acme.sh. Reload helper on the server is `scripts/install_haqqline_ssl.py`.

## Deploy

Push to `main` or `phase/**`. `.github/workflows/ci.yml` runs tests, rsyncs `public/` (it does not delete `api/data` or `.well-known`), then smokes `/health` and the API.

Agent and number updates are separate jobs in the same workflow:

- `scripts/sync_elevenlabs.py` needs `ELEVENLABS_API_KEY`. It writes `public/elevenlabs.json` and rsyncs that file.
- `scripts/sync_twilio.py` needs the ElevenLabs key, Twilio credentials, and `TWILIO_VOICE_NUMBER`. It writes `public/twilio.json`.

Local equivalents are in `.env.example`.

## Smoke after a deploy

- `GET /health` returns `status: ok`
- `GET /api/v1/health` returns the current phase and pack id
- Home page still contains the English and Arabic “not a government service” lines
- `public/elevenlabs.json` on the host has an `agent_` id

## Data on the host

`public/api/data/` holds the queue, escalations, audit tail, rate-limit buckets, conversation log, and the webhook secret. It is gitignored and denied by `.htaccess`. Wiping the JSONL files resets the sandbox. Do not wipe the webhook secret unless a new one is installed in the same step.

## When something fails

| Symptom | Look at |
| --- | --- |
| Site is the old tree | Actions run for that commit. rsync only follows a green verify job. |
| Talk widget missing | `public/elevenlabs.json` and the elevenlabs-sync job. Key unset fails that job before sync. |
| Call section has no number | `TWILIO_VOICE_NUMBER` and the twilio-sync job. Empty `phone_number` means import has not succeeded. |
| Webhook 401 | Host secret vs the ElevenLabs webhook signing secret. Clock skew over 30 minutes also fails. |
| Webhook 503 | Secret file missing on the host. |
| Lookup 429 | Rate limit in `public/api/v1/pack/config.json` (120/minute/IP). |

Rollback of the site is a redeploy of the previous tag. Rollback of the agent is a sync from the last good commit. Git does not restore `api/data`.

## Not operated from this repo

WhatsApp, SMS, live DLD or RERA credentials, and outbound dialling. Those are later phases in `IMPLEMENTATION_PLAN.md`.
