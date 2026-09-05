"""Mock RERA band lookup and human filing queue. Sandbox only. Not legal advice."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

# Illustrative bands for demo. Replace with a signed-off table before any institutional pilot.
# Decree 43/2013 style steps: 0 / 5 / 10 / 15 / 20 percent depending on gap to index.
AREAS = {
    "downtown_dubai": {"index_aed": 120000},
    "jlt": {"index_aed": 85000},
    "international_city": {"index_aed": 42000},
    "dubai_marina": {"index_aed": 110000},
    "al_barsha": {"index_aed": 90000},
}

QUEUE: list[dict] = []


def permitted_increase_pct(current: float, index: float) -> int:
    if current <= 0:
        raise ValueError("current_rent must be positive")
    gap = (index - current) / current
    if gap < 0.10:
        return 0
    if gap < 0.20:
        return 5
    if gap < 0.30:
        return 10
    if gap < 0.40:
        return 15
    return 20


class Handler(BaseHTTPRequestHandler):
    def _json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        data = json.loads(raw or b"{}")
        path = urlparse(self.path).path

        if path == "/tools/lookup_rera_band":
            area = data.get("area", "")
            current = float(data["current_rent"])
            proposed = float(data["proposed_rent"])
            row = AREAS.get(area)
            if not row:
                self._json(404, {"error": "unknown_area", "escalate": True})
                return
            pct = permitted_increase_pct(current, row["index_aed"])
            cap = current * (1 + pct / 100)
            self._json(
                200,
                {
                    "source": "sandbox_decree_43_2013_table_v0",
                    "index_aed": row["index_aed"],
                    "permitted_increase_pct": pct,
                    "permitted_new_rent_aed": round(cap, 2),
                    "proposed_is_within_band": proposed <= cap + 0.005,
                    "disclaimer": "Information from a signed-off published rule pack. Not legal advice. Not a determination.",
                },
            )
            return

        if path == "/tools/submit_to_human_queue":
            if data.get("caller_confirmed") is not True:
                self._json(400, {"error": "confirmation_required"})
                return
            item = {
                "id": f"RDC-SANDBOX-{len(QUEUE) + 1:04d}",
                "status": "pending_human",
                "packet": data.get("packet", {}),
            }
            QUEUE.append(item)
            self._json(200, item)
            return

        self._json(404, {"error": "not_found"})

    def log_message(self, fmt: str, *args) -> None:
        return


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8787), Handler).serve_forever()
