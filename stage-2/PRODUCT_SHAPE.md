# What HaqqLine is (and is not)

HaqqLine is a **voice agent product**, not a consumer mobile/web app, and not a module inside JustNow.

ExcellonIT is the vendor. The authority’s existing phone line, website, or super-app is the host. JustNow is a separate government product and is not required to demo or to sell this.

## Stage 2 delivery

A live agent on a test number or on the hosted page, plus recordings, tests, and transcripts. No App Store app, no user accounts, and no new citizen portal.

## Three layers

```
Caller  →  Phone (Twilio test DID)  ─┐
        →  Web widget (ConvAI)      ─┼─→  ElevenLabs agent (HaqqLine)
                                     │         │
                                     │         ├─ TTS / Scribe / Workflows / RAG
                                     │         └─ signed webhooks
                                     │
                                     └─→  ExcellonIT sandbox APIs
                                           lookup_rera_band
                                           submit_to_human_queue
                                           escalate_human
```

That stack is the product. A separate Flutter or React app is out of scope for this build.

## What a real buyer installs

DLD / RDC already have:

- inbound numbers and IVR
- public pages (Ejari, RERA index explainers)
- a human case queue

They do not need residents to download ExcellonIT software. Production looks like:

1. Point a published information DID (or Dubai Now voice entry) at the agent.
2. Embed the same widget on the RERA/Ejari page.
3. Connect webhooks to their APIs and officer queue (same contracts as the sandbox).

Native iOS/Android SDKs exist on ElevenLabs for a later embed inside Dubai Now or a DLD app. They are out of scope for 14 October.

## What ExcellonIT still has to build

| Build | Needed? |
| --- | --- |
| ElevenLabs agent, voices, knowledge, evals | Yes |
| Sandbox tools + confirmation gate | Yes |
| Demo page with the official widget | Yes — Talk and the test number |
| Full mobile + web citizen app | No |
| JustNow as a host | No |

excellonit.net is the production portfolio. Residents do not open HaqqLine there.
