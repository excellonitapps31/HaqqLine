# Operations

Sandbox host: https://haqqline.excellonit.net  
Compute: Ubuntu 24.04 VPS, HestiaCP, nginx, PHP 8.5-FPM. The PHP pool runs as `admin`. Document root is the `DEPLOY_PATH` secret.  
Deploy user: `haqqdeploy`, key-only SSH (`restrict`), owns the document root. `api/data` is `haqqdeploy:admin` mode 770 with an ACL (`u:admin:rwX`, default on new files) so PHP can read the webhook secret and write the logs.  
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
- `GET /twilio.json` returns `inbound_only: true`, `enable_sms: false`, and a failover string. Empty `phone_number` is expected until Twilio secrets are set.
- `GET /whatsapp.json` returns sandbox WhatsApp status (`connected`, STOP policy, failover → Talk). Empty number is expected until WABA is imported in ElevenLabs and `whatsapp-sync` runs.
- `python3 scripts/verify_pack_lock.py` exits 0 (pack areas/ejari match `content_hash` in `public/api/v1/pack/config.json`)
- `GET /sre-budgets.json` returns sandbox-labelled latency / concurrency / eval-gate budgets (Phase 9)

## Pack rollback (Phase 6)

The signed pack is `pack_id` + `pack_version` + `content_hash` in `public/api/v1/pack/config.json`. Data files are `areas.json` and `ejari.json`.

1. Check out the previous git tag (for example `phase-05` or the last good `phase-06` tip).
2. Redeploy that tree via the normal Actions rsync (or push a revert on a phase branch).
3. Confirm `GET /api/v1/health` shows the prior `pack_version` / `citation_id`, and `verify_pack_lock.py` passes.
4. Re-run `scripts/sync_elevenlabs.py` from that commit so the agent prompt matches the pack citation.

Do not edit `areas.json` / `ejari.json` without bumping `pack_version`, updating `citation_id` (`pack_id@version`), and refreshing `content_hash` via:

```bash
python3 - <<'PY'
import hashlib, json
from pathlib import Path
p = Path('public/api/v1/pack')
canon = json.dumps(
    {'areas': json.loads((p/'areas.json').read_text()), 'ejari': json.loads((p/'ejari.json').read_text())},
    sort_keys=True, separators=(',', ':'),
)
print('sha256:' + hashlib.sha256(canon.encode()).hexdigest())
PY
```

Then run `python3 scripts/verify_pack_lock.py`.

## Data on the host

`public/api/data/` holds the queue, escalations, audit tail, rate-limit buckets, conversation log, and the webhook secret. It is gitignored and denied by `.htaccess`. Wiping the JSONL files resets the sandbox. The webhook secret is replaced, never just removed; a missing secret returns 503 on every webhook.

## When something fails

| Symptom | Look at |
| --- | --- |
| Site is the old tree | Actions run for that commit. rsync only follows a green verify job. |
| Deploy `Permission denied (publickey)` | `SSH_HOST`, `SSH_USER`, and `SSH_PRIVATE_KEY` against `/home/haqqdeploy/.ssh/authorized_keys` on the VPS |
| Deploy cannot write files after a HestiaCP rebuild | A domain rebuild can return the document root to `admin`. Re-own it to `haqqdeploy:www-data`, `api/data` to `haqqdeploy:admin` 770, and re-apply `setfacl -R -m u:admin:rwX` plus `setfacl -d -m u:admin:rwX,u:haqqdeploy:rwX` on `api/data`. |
| Webhook 503 after a sync | `getfacl api/data/elevenlabs_webhook.secret` shows `user:admin` with read |
| Talk widget missing | `public/elevenlabs.json` and the elevenlabs-sync job. Key unset fails that job before sync. |
| Call section has no number | `TWILIO_VOICE_NUMBER` and the twilio-sync job. Empty `phone_number` means import has not succeeded. |
| Webhook 401 | Host secret vs the ElevenLabs webhook signing secret. Clock skew over 30 minutes also fails. |
| Webhook 503 | Secret file missing on the host. |
| Lookup 429 | Rate limit in `public/api/v1/pack/config.json` (120/minute/IP). |

Rollback of the site is a redeploy of the previous tag. Rollback of the agent is a sync from the last good commit **only after** the Phase 9 promote gate passes (`reports/phase-09-eval.json`). Git does not restore `api/data`.

Operator runbook (pack / agent / number failover, alerts): `docs/OPERATOR_RUNBOOK.md`.

## Not operated from this repo

Live DLD or RERA credentials, and outbound dialling. WhatsApp WABA import is Meta Embedded Signup in the ElevenLabs dashboard, then `scripts/sync_whatsapp.py` (see Phase 10). SMS is Phase 11.
