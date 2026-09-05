# Phase 01 report — Platform: repo, CI, subdomain, live shell

Date: 5 September 2026  
Git SHA / tag: `6dcb0ef` on `phase/01-platform` (tag `phase-01` after merge to `main`)  
Live URL(s): https://haqqline.excellonit.net/ · https://haqqline.excellonit.net/health  
Deploy method: GitHub Actions rsync of `public/` to `/home/excegksu/public_html/haqqline`  
CI: https://github.com/excellonitapps31/HaqqLine/actions/runs/33953955662 (verify, deploy, https-home — all success)

## Built (complete)

- Dedicated public repo, `CODEOWNERS`, `main` still refuses force-push and deletion.
- cPanel subdomain `haqqline.excellonit.net` serving only `public/` (canvas and plan are not on the web root).
- Let’s Encrypt certificate for this hostname, HTTP→HTTPS (ACME challenge path excluded), HSTS.
- Bilingual EN/AR demo shell: sandbox banner above the fold, “not a government service”, DLD/RERA/RDC disclaimer, honest scope (no agent/phone/WhatsApp/SMS on this host yet).
- `/health` JSON with phase and channel flags.
- pytest suite for health schema and landing copy; CI runs it before deploy and smokes HTTPS after deploy.
- Host of record documented as **cPanel**, not Cloud Run.
- Cert renewal helper on the server (`~/bin/install_haqqline_ssl.py`) wired as acme.sh `--reloadcmd`.

## Tests

| Test | Result |
| --- | --- |
| `tests/phase1` health schema | pass (stdlib + CI pytest) |
| `tests/phase1` landing copy / bilingual / no JustNow | pass |
| CI `GET https://haqqline.excellonit.net/health` 200 + schema | pass |
| CI homepage contains EN + AR government-service disclaimer | pass |
| Manual: TLS name match `CN=haqqline.excellonit.net` | pass |
| Manual: desktop banner visible without scroll; Arabic toggle sets `dir=rtl` | pass |

## What an investor can do now

Open https://haqqline.excellonit.net, read the product in English or Arabic, hit Health, and know this is an ExcellonIT sandbox.

## Explicitly not built (next phases)

- Rule APIs, Ejari lookup, filing queue
- ElevenLabs agent / widget
- Twilio, WhatsApp, SMS
- Investor scenario player (Phase 3)
- Licence file (matches other ExcellonIT product repos)

## Risks / residual defects

- Shared-host AutoSSL is not enabled for this cPanel user; TLS is Let’s Encrypt via acme.sh. Renewals depend on acme cron + `install_haqqline_ssl.py`.
- No demo PIN on the shell (not in Phase 1 DoD).

## Request

Approve Phase 01 / Reject
