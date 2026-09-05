#!/usr/bin/env python3
"""Quick check that filing is blocked without confirmation."""

import json
import threading
import urllib.error
import urllib.request

from http.server import HTTPServer

from server import Handler


def main() -> None:
    httpd = HTTPServer(("127.0.0.1", 0), Handler)
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    url = f"http://127.0.0.1:{port}/tools/submit_to_human_queue"
    req = urllib.request.Request(
        url,
        data=json.dumps({"packet": {"area": "jlt"}}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req)
        raise SystemExit("expected 400 without caller_confirmed")
    except urllib.error.HTTPError as e:
        if e.code != 400:
            raise
    req2 = urllib.request.Request(
        url,
        data=json.dumps({"caller_confirmed": True, "packet": {"area": "jlt"}}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req2) as resp:
        body = json.load(resp)
    assert body["status"] == "pending_human"
    httpd.shutdown()
    print("ok: confirmation gate and pending_human status")


if __name__ == "__main__":
    main()
