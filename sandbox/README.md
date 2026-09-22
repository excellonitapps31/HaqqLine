# Sandbox sketch

Local stand-in used before the Phase 2 API. The live tools are `public/api/v1/`, not this process.

```bash
python3 server.py
```

Listens on 127.0.0.1:8787.

- `POST /tools/lookup_rera_band` with `area`, `current_rent`, `proposed_rent`
- `POST /tools/submit_to_human_queue` with `caller_confirmed: true`

Bands are the same Decree 43/2013 steps as the deployed pack. Unknown areas return 404. A filing without confirmation returns 400.
