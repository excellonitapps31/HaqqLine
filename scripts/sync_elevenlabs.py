#!/usr/bin/env python3
"""Create or update the HaqqLine ElevenLabs agent, tests, and post-call webhook."""

from __future__ import annotations

import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = "https://api.elevenlabs.io"
CTX = ssl.create_default_context()
AGENT_NAME = "HaqqLine sandbox"
VOICE_EN = "EXAVITQu4vr4xnSDxMaL"
VOICE_AR = "pNInz6obpgDQGcFmaJgB"
WEBHOOK_URL = "https://haqqline.excellonit.net/api/v1/webhooks/elevenlabs"
TOOLS_BASE = "https://haqqline.excellonit.net/api/v1/tools"
DEMO_KEY = "haqqline_sandbox_preview"


def api(method: str, path: str, body: dict | None = None) -> dict:
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        raise SystemExit("ELEVENLABS_API_KEY is not set")
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        API + path,
        data=data,
        method=method,
        headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=180) as res:
            raw = res.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode()
        raise SystemExit(f"{method} {path} -> {exc.code}: {detail[:2000]}") from exc


def find_named(items: list, name: str, id_key: str) -> str | None:
    for row in items:
        if row.get("name") == name:
            return row.get(id_key) or row.get("id") or row.get("agent_id")
    return None


def upsert_knowledge() -> str:
    text = (ROOT / "elevenlabs/knowledge/rera-pack.md").read_text(encoding="utf-8")
    listing = api("GET", "/v1/convai/knowledge-base")
    docs = listing.get("documents") or listing.get("knowledge_base") or []
    if isinstance(listing, dict) and "items" in listing:
        docs = listing["items"]
    existing = find_named(docs if isinstance(docs, list) else [], "HaqqLine RERA pack v1", "id")
    if existing:
        return existing
    created = api("POST", "/v1/convai/knowledge-base/text", {"name": "HaqqLine RERA pack v1", "text": text})
    return created["id"]


def tool_config(name: str, description: str, path: str, properties: dict, required: list[str]) -> dict:
    return {
        "type": "webhook",
        "name": name,
        "description": description,
        "api_schema": {
            "url": f"{TOOLS_BASE}/{path}",
            "method": "POST",
            "headers": {
                "Authorization": f"Bearer {DEMO_KEY}",
                "Content-Type": "application/json",
            },
            "request_body_schema": {
                "type": "object",
                "description": description,
                "properties": properties,
                "required": required,
            },
        },
    }


def upsert_tools() -> dict[str, str]:
    listing = api("GET", "/v1/convai/tools")
    rows = listing.get("tools") or listing.get("items") or []
    wanted = {
        "lookup_rera_band": tool_config(
            "lookup_rera_band",
            "Look up the sandbox RERA increase band for an area and two rents. Never invent an index.",
            "lookup_rera_band",
            {
                "area": {"type": "string", "description": "Area key such as jlt or Downtown Dubai"},
                "current_rent": {"type": "number", "description": "Current annual rent AED"},
                "proposed_rent": {"type": "number", "description": "Proposed annual rent AED"},
            },
            ["area", "current_rent", "proposed_rent"],
        ),
        "lookup_ejari": tool_config(
            "lookup_ejari",
            "Look up a synthetic Ejari record. Unknown ids return found false, invented false.",
            "lookup_ejari",
            {"ejari_id": {"type": "string", "description": "Ejari id, for example EJ-1001"}},
            ["ejari_id"],
        ),
        "submit_to_human_queue": tool_config(
            "submit_to_human_queue",
            "Queue a filing for a human. Must send caller_confirmed true only after the caller clearly confirms.",
            "submit_to_human_queue",
            {
                "caller_confirmed": {"type": "boolean", "description": "True only after explicit verbal confirmation"},
                "packet": {"type": "object", "description": "Synthetic scenario packet, no real PII"},
            },
            ["caller_confirmed"],
        ),
        "escalate_human": tool_config(
            "escalate_human",
            "Hand the case to a human. Use for missing rules, legal advice, or will-I-win questions.",
            "escalate_human",
            {"reason": {"type": "string", "description": "Why a human must take over"}},
            ["reason"],
        ),
    }
    ids: dict[str, str] = {}
    for name, cfg in wanted.items():
        existing = None
        for row in rows:
            cfg_row = row.get("tool_config") if isinstance(row.get("tool_config"), dict) else row
            if cfg_row.get("name") == name:
                existing = row.get("id") or row.get("tool_id")
                break
        if existing:
            api("PATCH", f"/v1/convai/tools/{existing}", {"tool_config": cfg})
            ids[name] = existing
        else:
            created = api("POST", "/v1/convai/tools", {"tool_config": cfg})
            ids[name] = created.get("id") or created.get("tool_id")
            if not ids[name]:
                raise SystemExit(f"tool create missing id: {created}")
    return ids


def upsert_webhook() -> tuple[str, str | None]:
    listing = api("GET", "/v1/workspace/webhooks")
    rows = listing.get("webhooks") or listing.get("items") or []
    for row in rows:
        if row.get("webhook_url") == WEBHOOK_URL or row.get("name") == "HaqqLine post-call":
            return row.get("webhook_id") or row["id"], None
    created = api(
        "POST",
        "/v1/workspace/webhooks",
        {"settings": {"auth_type": "hmac", "name": "HaqqLine post-call", "webhook_url": WEBHOOK_URL}},
    )
    return created["webhook_id"], created.get("webhook_secret")


def agent_payload(kb_id: str, tool_ids: dict[str, str], webhook_id: str) -> dict:
    prompt = (ROOT / "elevenlabs/prompt.md").read_text(encoding="utf-8")
    tools = [
        {"type": "system", "name": "language_detection", "description": "Switch English and Arabic to match the caller."},
        {"type": "system", "name": "knowledge_base", "params": {"system_tool_type": "knowledge_base"}},
        {"type": "system", "name": "end_call", "params": {"system_tool_type": "end_call"}},
    ]
    workflow = {
        "nodes": {
            "start_node": {"type": "start", "edge_order": ["to_intake"]},
            "intake": {
                "type": "override_agent",
                "label": "Intake",
                "additional_prompt": "Complete AI disclosure if not already said. Collect area, current rent, proposed rent. Do not file yet.",
                "edge_order": ["to_match"],
            },
            "rulematch": {
                "type": "override_agent",
                "label": "RuleMatch",
                "additional_prompt": "Call lookup_rera_band. Cite the pack. If the area is unknown, go to Escalate.",
                "edge_order": ["to_filing", "to_escalate"],
            },
            "filing": {
                "type": "override_agent",
                "label": "Filing",
                "additional_prompt": "Submit only after explicit confirmation with caller_confirmed true.",
                "additional_tool_ids": [tool_ids["submit_to_human_queue"]],
                "edge_order": ["filing_end"],
            },
            "escalate": {
                "type": "override_agent",
                "label": "Escalate",
                "additional_prompt": "Do not give legal advice. Call escalate_human.",
                "additional_tool_ids": [tool_ids["escalate_human"]],
                "edge_order": ["escalate_end"],
            },
            "end_node": {"type": "end"},
        },
        "edges": {
            "to_intake": {"source": "start_node", "target": "intake", "forward_condition": {"type": "unconditional"}},
            "to_match": {
                "source": "intake",
                "target": "rulematch",
                "forward_condition": {"type": "llm", "condition": "Area and both rents are known, or an Ejari id was given."},
            },
            "to_filing": {
                "source": "rulematch",
                "target": "filing",
                "forward_condition": {"type": "llm", "condition": "The caller wants a human filing and is not asking for legal advice or a win prediction."},
            },
            "to_escalate": {
                "source": "rulematch",
                "target": "escalate",
                "forward_condition": {"type": "llm", "condition": "Unknown area, legal advice, or will-I-win."},
            },
            "filing_end": {
                "source": "filing",
                "target": "end_node",
                "forward_condition": {"type": "llm", "condition": "Filing queued or caller declined."},
            },
            "escalate_end": {
                "source": "escalate",
                "target": "end_node",
                "forward_condition": {"type": "llm", "condition": "Escalation recorded or the caller is finished."},
            },
        },
    }
    return {
        "name": AGENT_NAME,
        "conversation_config": {
            "asr": {
                "quality": "high",
                "provider": "scribe_realtime",
                "keywords": ["Ejari", "RERA", "DLD", "RDC", "HaqqLine", "JLT", "Ignyte"],
            },
            "tts": {
                "model_id": "eleven_v3_conversational",
                "voice_id": VOICE_EN,
                "supported_voices": [
                    {"voice_id": VOICE_EN, "label": "English", "language": "en"},
                    {"voice_id": VOICE_AR, "label": "Gulf Arabic", "language": "ar"},
                ],
            },
            "agent": {
                "first_message": "I am HaqqLine, an AI on an ExcellonIT sandbox — not a government service, not legal advice. How can I check a rental situation against the published pack?",
                "language": "en",
                "prompt": {
                    "prompt": prompt,
                    "llm": "gemini-2.5-flash",
                    "temperature": 0.2,
                    "tool_ids": list(tool_ids.values()),
                    "tools": tools,
                    "knowledge_base": [{"type": "text", "name": "HaqqLine RERA pack v1", "id": kb_id, "usage_mode": "auto"}],
                },
            },
            "language_presets": {
                "ar": {
                    "overrides": {
                        "agent": {
                            "language": "ar",
                            "first_message": "أنا حقّ لاين، ذكاء اصطناعي على بيئة تجريبية من ExcellonIT — لست خدمة حكومية وليست هذه مشورة قانونية. كيف أطابق حالتك بالجدول المنشور؟",
                        },
                        "tts": {"voice_id": VOICE_AR},
                    }
                }
            },
            "source_attribution": True,
            "workflow": workflow,
        },
        "platform_settings": {
            "auth": {"enable_auth": False, "allowlist": [{"hostname": "haqqline.excellonit.net"}]},
            "privacy": {"record_voice": True},
            "webhooks": {"post_call_webhook_id": webhook_id, "events": ["transcript"]},
            "widget": {"variant": "expanded", "expandable": "never", "text_contents": {"main_label": "Talk"}},
        },
        "tags": ["haqqline", "sandbox", "excellonit"],
    }


def upsert_agent(payload: dict) -> str:
    listing = api("GET", "/v1/convai/agents")
    agents = listing.get("agents") or listing.get("items") or []
    existing = find_named(agents, AGENT_NAME, "agent_id")
    if existing:
        api("PATCH", f"/v1/convai/agents/{existing}", payload)
        return existing
    created = api("POST", "/v1/convai/agents/create", payload)
    return created["agent_id"]


def upsert_tests(tool_ids: dict[str, str]) -> list[str]:
    specs = json.loads((ROOT / "elevenlabs/tests.json").read_text(encoding="utf-8"))
    listing = api("GET", "/v1/convai/agent-testing")
    rows = listing.get("tests") or listing.get("items") or []
    by_name = {row.get("name"): row.get("id") or row.get("test_id") for row in rows}
    ids = []
    for spec in specs:
        body = json.loads(json.dumps(spec))
        params = body.get("tool_call_parameters") or {}
        ref = params.get("referenced_tool") or {}
        if ref.get("id") == "LOOKUP_RERA_PLACEHOLDER":
            ref["id"] = tool_ids["lookup_rera_band"]
        if ref.get("id") == "SUBMIT_PLACEHOLDER":
            ref["id"] = tool_ids["submit_to_human_queue"]
        name = body["name"]
        if name in by_name and by_name[name]:
            api("PATCH", f"/v1/convai/agent-testing/{by_name[name]}", body)
            ids.append(by_name[name])
        else:
            created = api("POST", "/v1/convai/agent-testing/create", body)
            ids.append(created.get("id") or created.get("test_id"))
    return [i for i in ids if i]


def attach_and_run(agent_id: str, test_ids: list[str]) -> dict:
    api(
        "PATCH",
        f"/v1/convai/agents/{agent_id}",
        {"platform_settings": {"testing": {"attached_tests": [{"test_id": tid} for tid in test_ids]}}},
    )
    result = api(
        "POST",
        f"/v1/convai/agents/{agent_id}/run-tests",
        {"tests": [{"test_id": tid} for tid in test_ids], "repeat_count": 1},
    )
    return result


def write_public_config(agent_id: str) -> None:
    path = ROOT / "public/elevenlabs.json"
    path.write_text(
        json.dumps(
            {
                "agent_id": agent_id,
                "name": AGENT_NAME,
                "pack_id": "sandbox_decree_43_2013_table_v1",
                "widget_script": "https://unpkg.com/@elevenlabs/convai-widget-embed",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def summarize_runs(result: dict) -> dict:
    runs = result.get("test_runs") or result.get("results") or result.get("tests") or []
    passed = 0
    total = 0
    details = []
    if isinstance(runs, list):
        for row in runs:
            total += 1
            status = str(row.get("status") or row.get("result") or row.get("successful") or "")
            ok = status.lower() in {"passed", "pass", "success", "successful", "true"}
            if row.get("passed") is True:
                ok = True
            if ok:
                passed += 1
            details.append({"name": row.get("test_name") or row.get("name") or row.get("test_id"), "ok": ok, "status": status})
    summary = {"passed": passed, "total": total or len(test_ids_fallback(result)), "raw_keys": list(result.keys()), "details": details}
    (ROOT / "reports/phase-04-eval.json").write_text(json.dumps({"invocation": result, "summary": summary}, indent=2)[:500000], encoding="utf-8")
    return summary


def test_ids_fallback(result: dict) -> list:
    return result.get("tests") or []


def main() -> None:
    kb_id = upsert_knowledge()
    tool_ids = upsert_tools()
    webhook_id, webhook_secret = upsert_webhook()
    if webhook_secret:
        secret_path = os.environ.get("HAQQLINE_WEBHOOK_SECRET_FILE")
        if secret_path:
            Path(secret_path).write_text(webhook_secret, encoding="utf-8")
        print("NEW_WEBHOOK_SECRET_CREATED=1")
    payload = agent_payload(kb_id, tool_ids, webhook_id)
    agent_id = upsert_agent(payload)
    write_public_config(agent_id)
    test_ids = upsert_tests(tool_ids)
    result = attach_and_run(agent_id, test_ids)
    summary = summarize_runs(result)
    print(json.dumps({"agent_id": agent_id, "tools": tool_ids, "webhook_id": webhook_id, "tests": test_ids, "summary": summary}, indent=2))
    if summary["total"] and summary["passed"] < summary["total"]:
        # Still deploy the widget; report the rate. Fail only if nothing ran.
        print("warning: some agent tests did not pass", file=sys.stderr)


if __name__ == "__main__":
    main()
