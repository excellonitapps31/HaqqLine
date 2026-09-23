# Nginx / edge security notes (sandbox) — Phase 12

**Host:** https://haqqline.excellonit.net  
**Compute:** Ubuntu 24.04, HestiaCP, nginx, PHP 8.5-FPM  
**Label:** Sandbox hardening notes — not a multi-region WAF design.

## What this VPS already does

| Control | Where |
| --- | --- |
| TLS + HTTP→HTTPS | HestiaCP / Let’s Encrypt; forced HTTPS |
| HSTS | Host nginx + `public/.htaccess` (`max-age=31536000; includeSubDomains`) |
| `X-Content-Type-Options: nosniff` | `.htaccess` / should be mirrored in nginx |
| `Referrer-Policy` | `.htaccess` |
| `X-Robots-Tag: noindex` | `.htaccess` + API `send()` |
| API routing | Hestia include `nginx.ssl.conf_haqqline_api` (nginx ignores `.htaccess` for PHP routes) |
| App rate limit | `rate_limit_per_minute` in pack config (default 120/IP) → HTTP 429 |

## WAF / CDN

A dedicated CDN or managed WAF in front of the subdomain is **optional for the sandbox**. If added later:

1. Terminate TLS at the edge or pass-through to Hestia.
2. Preserve `X-Forwarded-For` so the PHP rate limiter still keys on client IP (or move limiting to the edge).
3. Do not cache `/api/v1/*` or `/api/data` paths.
4. Keep ACME HTTP-01 working for Let’s Encrypt (or switch to DNS-01).

Until a CDN/WAF is attached, the published stand-in is: **Hestia nginx + HSTS + app rate limit + noindex**. That is sufficient for the investor sandbox; it is not a UAE production edge posture.

## Operator checklist

- [ ] HTTPS forced; HSTS present on home and API responses  
- [ ] `/api/v1/` routes through the HaqqLine API include  
- [ ] 429 observed under burst when rate limit is enabled  
- [ ] Document any future CDN/WAF change in `OPERATIONS.md`
