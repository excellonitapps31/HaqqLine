#!/usr/bin/env python3
"""Fail if pack areas/ejari drift from config content_hash without a version bump."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "public/api/v1/pack"


def content_digest() -> str:
    areas = json.loads((PACK / "areas.json").read_text(encoding="utf-8"))
    ejari = json.loads((PACK / "ejari.json").read_text(encoding="utf-8"))
    canon = json.dumps({"areas": areas, "ejari": ejari}, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canon.encode("utf-8")).hexdigest()


def main() -> int:
    cfg = json.loads((PACK / "config.json").read_text(encoding="utf-8"))
    expected = str(cfg.get("content_hash") or "")
    actual = content_digest()
    version = str(cfg.get("pack_version") or "")
    citation = str(cfg.get("citation_id") or "")
    pack_id = str(cfg.get("pack_id") or "")
    if not version:
        print("pack_version missing in config.json", file=sys.stderr)
        return 1
    if citation != f"{pack_id}@{version}":
        print(
            f"citation_id {citation!r} must equal pack_id@version ({pack_id}@{version})",
            file=sys.stderr,
        )
        return 1
    if not expected.startswith("sha256:"):
        print("content_hash must be sha256:…", file=sys.stderr)
        return 1
    if actual != expected:
        print(
            "Pack content hash mismatch.\n"
            f"  locked:  {expected}\n"
            f"  actual:  {actual}\n"
            "Bump pack_version and citation_id, then set content_hash to the actual digest.",
            file=sys.stderr,
        )
        return 1
    print(json.dumps({"ok": True, "pack_version": version, "citation_id": citation, "content_hash": actual}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
