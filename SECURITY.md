# Security

HaqqLine on haqqline.excellonit.net is an ExcellonIT sandbox. It is not a government service and it does not hold live resident records.

## Reporting

Email swissknife@excellonit.net. Include the URL, the time, and the expected result. Leave out a live Ejari, a passport, or a recording of a real caller.

## What is public on purpose

- The demo API key `haqqline_sandbox_preview` in `public/api/v1/pack/config.json`. The control on that key is the per-IP rate limit.
- The agent id in `public/elevenlabs.json`.
- The sandbox pack (synthetic areas and three Ejari ids).

## What stays out of git

- `ELEVENLABS_API_KEY`
- Twilio API key or auth token
- `TWILIO_VOICE_NUMBER` until the import script writes the E.164 value into `public/twilio.json`
- The ElevenLabs webhook HMAC secret (`public/api/data/elevenlabs_webhook.secret` on the host, mode 640, readable by the deploy user and the PHP pool only)
- SSH deploy key
- Anything under `public/api/data/` except the deny-all `.htaccess`

Names and empty values are in `.env.example`. Filled values go in `.env` locally and in GitHub Actions secrets for CI.

## Call and filing controls

- The first spoken turn states that this is an AI on a sandbox, not a lawyer and not a government line.
- `submit_to_human_queue` returns 400 unless `caller_confirmed` is true. A successful filing is always `pending_human`.
- Unknown areas and unknown Ejari ids are not filled in. The Ejari miss is `found: false`, `invented: false`.
- No tool collects a PIN, password, or one-time code.
- Post-call webhooks are HMAC-SHA256, rejected when the timestamp is more than 30 minutes off.

## Host

Deploy is rsync of `public/` over SSH from GitHub Actions, as a dedicated key-only user with write access to the HaqqLine document root and nothing else. The data directory is created on the host and is not part of the sync delete set. HTTP redirects to HTTPS, and HSTS is on.
