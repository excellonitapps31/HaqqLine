# What HaqqLine is (and is not)

HaqqLine is a **voice agent product**, not a consumer mobile/web app, and not a module inside JustNow.

ExcellonIT is the vendor. The authority’s existing phone line, website, or super-app is the host. JustNow is a separate government product and is not required to demo or to sell this.

## What Stage 2 actually requires

The brief asks for a live agent on **test numbers** or a **hosted web or chat** deployment, plus recordings, tests, and transcripts. It does not ask for App Store apps, user accounts, or a new citizen portal.

## Three layers

```
Caller  →  Phone (Twilio test DID)  ─┐
        →  Web widget (React)       ─┼─→  ElevenLabs agent (HaqqLine)
                                     │         │
                                     │         ├─ TTS / Scribe / Workflows / RAG
                                     │         └─ signed webhooks
                                     │
                                     └─→  ExcellonIT sandbox APIs
                                           lookup_rera_band
                                           submit_to_human_queue
                                           escalate_human
```

That stack **is** the product for the challenge. A Flutter/React “HaqqLine app” would not raise Stage 2 scores and would dilute the 14-day sprint.

## What a real buyer installs

DLD / RDC already have:

- inbound numbers and IVR
- public pages (Ejari, RERA index explainers)
- a human case queue

They do not need residents to download ExcellonIT software. Production looks like:

1. Point a published information DID (or Dubai Now voice entry) at the agent.
2. Embed the same widget on the RERA/Ejari page.
3. Connect webhooks to their APIs and officer queue (same contracts as the sandbox).

Native iOS/Android SDKs exist on ElevenLabs for a **later** embed inside Dubai Now or a DLD app. They are out of scope for 14 October (already stated in canvas box G).

## What ExcellonIT still has to build

| Build | Needed? |
| --- | --- |
| ElevenLabs agent, voices, knowledge, evals | Yes — this is the scored work |
| Sandbox tools + confirmation gate | Yes |
| Thin demo page with the official widget | Yes — so judges can click/call |
| Full mobile + web citizen app | No |
| JustNow as a host | No |

Box N’s live site (excellonit.net) proves you ship production software. It is not the place residents will “open HaqqLine.”
