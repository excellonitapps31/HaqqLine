# What HaqqLine is (and is not)

HaqqLine is a **voice agent product**, not a consumer mobile/web app, and not a module inside JustNow.

ExcellonIT is the vendor. The authority’s existing phone line, website, or super-app is the host. JustNow is a separate government product and not a dependency.

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
                                           lookup_ejari
                                           submit_to_human_queue
                                           escalate_human
```

That stack is the product. A separate mobile or web app is out of scope for this build.

## Production deployment

DLD and RDC already run:

- inbound numbers and IVR
- public pages (Ejari, RERA index explainers)
- a human case queue

Residents install nothing from ExcellonIT. A production rollout is:

1. A published information DID (or a Dubai Now voice entry) routed to the agent.
2. The same widget embedded on the RERA/Ejari page.
3. Webhooks connected to the authority’s APIs and officer queue, on the sandbox contracts.

ElevenLabs native iOS/Android SDKs cover a later embed inside Dubai Now or a DLD app. That embed is outside the 14 October scope.

## Build scope

| Build | Needed? |
| --- | --- |
| ElevenLabs agent, voices, knowledge, evals | Yes |
| Sandbox tools + confirmation gate | Yes |
| Demo page with the official widget | Yes — Talk and the test number |
| Full mobile + web citizen app | No |


