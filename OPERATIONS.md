# Operations

Sandbox host: https://haqqline.excellonit.net  
Compute: Ubuntu 24.04 VPS, HestiaCP, nginx, PHP 8.5-FPM. The PHP pool runs as `admin`. Document root is the `DEPLOY_PATH` secret.  
Deploy user: `haqqdeploy`, key-only SSH (`restrict`), owns the document root. `api/data` is `haqqdeploy:admin` mode 2770 so PHP can write it.  
TLS: Let’s Encrypt issued and renewed by HestiaCP. HTTPS is forced and HSTS is on for this domain.  
nginx ignores `.htaccess`. `/api/v1/` routing lives in the HestiaCP custom include `nginx.ssl.conf_haqqline_api` for the domain.

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

`public/api/data/` holds the queue, escalations, audit tail, rate-limit buckets, conversation log, and the webhook secret. It is gitignored and denied by `.htaccess`. Wiping the JSONL files resets the sandbox. The webhook secret is replaced, never just removed; a missing secret returns 503 on every webhook.

## When something fails

| Symptom | Look at |
| --- | --- |
| Site is the old tree | Actions run for that commit. rsync only follows a green verify job. |
| Deploy `Permission denied (publickey)` | `SSH_HOST`, `SSH_USER`, and `SSH_PRIVATE_KEY` against `/home/haqqdeploy/.ssh/authorized_keys` on the VPS |
| Deploy cannot write files after a HestiaCP rebuild | A domain rebuild can return the document root to `admin`. Re-own it to `haqqdeploy:www-data`, and `api/data` to `haqqdeploy:admin` 2770. |
| Talk widget missing | `public/elevenlabs.json` and the elevenlabs-sync job. Key unset fails that job before sync. |
| Call section has no number | `TWILIO_VOICE_NUMBER` and the twilio-sync job. Empty `phone_number` means import has not succeeded. |
| Webhook 401 | Host secret vs the ElevenLabs webhook signing secret. Clock skew over 30 minutes also fails. |
| Webhook 503 | Secret file missing on the host. |
| Lookup 429 | Rate limit in `public/api/v1/pack/config.json` (120/minute/IP). |

Rollback of the site is a redeploy of the previous tag. Rollback of the agent is a sync from the last good commit. Git does not restore `api/data`.

## Not operated from this repo

WhatsApp, SMS, live DLD or RERA credentials, and outbound dialling. Those are later phases in `IMPLEMENTATION_PLAN.md`.
