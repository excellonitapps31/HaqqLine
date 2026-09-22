# HaqqLine — Stage 2 delivery plan

**Window:** 30 September 2026 – 14 October 2026  
**Owner:** ExcellonIT  
**Live host:** https://haqqline.excellonit.net  
**Product shape:** `PRODUCT_SHAPE.md`  
**Programme:** `IMPLEMENTATION_PLAN.md` (Phases 1–4 are on `main`. This window finishes Phase 5 and freezes evidence.)

The product is the agent, the sandbox tools, and the demo page. A separate mobile or web app is out of scope.

## 1. Done on 14 October

A reviewer, with no dashboard login, can:

1. Open the sandbox and complete a rent-band check in the browser, in English and in Gulf Arabic.
2. Dial the test DID on the same page and complete the same check. Inbound only.
3. Hear the disclosure before any figure, hear the pack named with the figure, and hear a refusal on “will I win?”.
4. See `submit_to_human_queue` rejected unless `caller_confirmed` is true, and accepted only as `pending_human`.
5. Read the evidence in this repo: a numeric multi-run pass rate, the high-stakes tool-call result, transcripts of the primary path and the failure path, this plan, `PRODUCT_SHAPE.md`, and the README.

No resident data. No live DLD, RERA, or RDC credentials. No outbound campaigns.

If the purchased DID is blocked by KYC, stock, or credentials, the web path remains the Stage 2 deployment. The DID is still the Phase 5 exit criterion.

## 2. Baseline already on main

| Piece | Where | State |
| --- | --- | --- |
| TLS sandbox shell, EN/AR, disclaimer | `public/` | Live since Phase 1 |
| Rule lookup, Ejari mock, confirm gate, audit, HMAC webhook | `public/api/v1/` | Live since Phase 2 |
| Scenario playground | `public/play/` | Live since Phase 3 |
| ConvAI widget, workflow, knowledge pack, agent tests | Talk on the host; `elevenlabs/` | Live since Phase 4. Agent `agent_5601m1xp22apfdcbwbb8h9y5zzqt` |
| Inbound DID | `public/twilio.json`, `scripts/sync_twilio.py` | Page and import script are in the tree. `phone_number` is still empty |

Phases 1–4 are out of scope for rework in this window. A defect found while recording is fixed against the phase that owns it.

## 3. Work in this window

### Telephony

One purchased Twilio Voice number is imported into ElevenLabs and assigned to the existing agent. Credentials are a Standard API key (`SK` + secret), with Account SID + auth token as the fallback. `enable_sms` is false.

Exit: `public/twilio.json` has an E.164 number, the Call section on the host shows it with the sandbox disclaimer, one English inbound and one Arabic inbound are logged, and a Twilio failure sends the caller back to Talk on the same page.

### Evaluation evidence

`elevenlabs/tests.json` defines disclosure, the JLT lookup, the unconfirmed-submit absence, and the EN/AR simulations. Every sync waits for the run to finish and records passed/total. The 22 September 2026 run passed 13 of 13, English and Arabic. Phase 5 adds a multi-run figure (`repeat_count` above 1) so the rate is not a single sample.

Exit: `reports/phase-05.md` states passed/total and quotes the unconfirmed-submit test result verbatim. A skipped disclosure fails the run.

### Recorded paths

Two calls, web or DID:

- Primary: area, current rent, proposed rent, cited band, no filing unless the caller confirms.
- Failure: “Will I win if I sue?” ends in `escalate_human`. No advice, no invented index.

Exit: transcript links in the phase report. Recordings stay on the ElevenLabs side or an unlisted link. They are not committed as audio.

### Freeze

11–14 October is reserved for evidence. Tools, channels, and the prompt change only to fix a defect.

## 4. Acceptance

| Check | Proof |
| --- | --- |
| Disclosure is the first spoken turn | Transcript |
| Figure cites `sandbox_decree_43_2013_table_v1` | Transcript |
| Unknown area escalates and does not invent an index | Tool-call log |
| Submit without `caller_confirmed: true` returns 400 | API test and agent tool-call test |
| Submit with confirmation returns `pending_human` | API test |
| No tool asks for a PIN, password, or OTP | Tool schema review |
| EN and AR each have a completed primary path | Two transcripts |
| Pass rate is a number | Phase 5 report |
| First cited answer inside 180 seconds, including the lookup | Timed note in the report |
| Host still says this is not a government service | Landing test |

## 5. Environments

| Environment | How it runs | Data |
| --- | --- | --- |
| Local | `php -S 127.0.0.1:8787 -t public public/router.php`, pytest | Pack JSON in the repo |
| CI | `.github/workflows/ci.yml` on `main` and `phase/**` | Secrets injected. Not printed. |
| Sandbox host | GitHub Actions rsync of `public/` to the HestiaCP document root | `public/api/data/` on the host only. Wipeable. Not in git. |

Promotion is the phase branch, green CI, smoke of the live URL, `reports/phase-05.md`, sign-off, merge, tag `phase-05`.

## 6. Fixed controls

- Synthetic Ejari ids only: EJ-1001, EJ-1002, EJ-1003. Any other id is `found: false` and `invented: false`.
- The demo API key in `public/api/v1/pack/config.json` is public. The control is the rate limit, not secrecy.
- Webhook signatures are HMAC, with a 30-minute clock skew. The secret file is on the host, mode 640, outside git.
- There is no `decide_case` tool.
- Rollback of the site is the previous git tag and a redeploy. A bad agent sync is corrected by running `scripts/sync_elevenlabs.py` from the last good commit. The host data directory is not rolled back by git.

## 7. Risks

| Risk | What it does to the date | Response |
| --- | --- | --- |
| Twilio number not purchased, or extra KYC on the chosen country | DID missing on 14 October | Web path is the deployment of record. A verified caller ID is not a substitute. |
| Model-graded simulations vary between runs | A single 13/13 can drop on a re-run | Multi-run pass rate in the Phase 5 report, and a re-run on the recording day |
| Arabic path never heard by a native listener | AR evidence is weaker than EN | One listen-through before the recording day |
| Scope pulled in from WhatsApp or SMS | Voice evidence slips | Those channels stay Phase 6 and Phase 7 |

## 8. After 14 October

WhatsApp (official WABA only), then SMS for receipts and status, then hardening and the runbook drill. Each starts after Phase 5 sign-off. Gaps in the evidence pack are defects in this window.
