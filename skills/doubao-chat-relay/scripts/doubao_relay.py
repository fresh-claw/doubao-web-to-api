#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


STATE_FILE = Path.home() / ".openclaw" / "state" / "doubao-chat-relay.json"
DEFAULT_TIMEOUT = int(os.environ.get("DOUBAO_RELAY_TIMEOUT", "180"))

ADAPTERS = {
    "web": {"cli_name": "doubao", "kind": "web"},
    "app": {"cli_name": "doubao-app", "kind": "app"},
}

ACTION_ALIASES = {
    "login-check": "status",
    "reset": "new",
    "last": "read",
}


def ensure_state_parent() -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_state() -> dict[str, Any]:
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(payload: dict[str, Any]) -> None:
    ensure_state_parent()
    STATE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def get_opencli_bin() -> str | None:
    return shutil.which("opencli")


def parse_jsonish(text: str) -> Any:
    text = (text or "").strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        return text


def flatten_text(value: Any) -> list[str]:
    out: list[str] = []
    if value is None:
        return out
    if isinstance(value, str):
        item = value.strip()
        if item:
            out.append(item)
        return out
    if isinstance(value, list):
        for item in value:
            out.extend(flatten_text(item))
        return out
    if isinstance(value, dict):
        for key in (
            "answer",
            "reply",
            "content",
            "text",
            "message",
            "output",
            "body",
            "markdown",
        ):
            if key in value:
                out.extend(flatten_text(value[key]))
        for key in ("items", "messages", "data", "result"):
            if key in value:
                out.extend(flatten_text(value[key]))
        return out
    return out


def guess_answer(payload: Any) -> str:
    parts = flatten_text(payload)
    if not parts:
        return ""
    seen: set[str] = set()
    ordered: list[str] = []
    for item in parts:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return "\n".join(ordered).strip()


def build_cmd(opencli_bin: str, cli_name: str, action: str, message: str | None) -> list[str]:
    cmd = [opencli_bin, cli_name, action]
    if message:
        cmd.append(message)
    cmd.extend(["-f", "json"])
    return cmd


def run_cmd(cmd: list[str], timeout: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        timeout=timeout,
    )


def normalize_action(action: str) -> str:
    return ACTION_ALIASES.get(action, action)


def candidate_order(adapter: str) -> list[str]:
    adapter = adapter.lower()
    state = load_state()
    last = state.get("last_adapter")
    if adapter in ADAPTERS:
        return [adapter]
    if last in ADAPTERS:
        others = [name for name in ADAPTERS if name != last]
        return [last] + others
    return ["web", "app"]


def run_opencli_action(adapter: str, action: str, message: str | None, timeout: int) -> dict[str, Any]:
    opencli_bin = get_opencli_bin()
    if not opencli_bin:
        return {
            "ok": False,
            "error": "opencli_not_found",
            "message": "未找到 opencli，请先安装并加入 PATH。",
            "action": action,
        }

    action = normalize_action(action)
    attempts: list[dict[str, Any]] = []
    for name in candidate_order(adapter):
        info = ADAPTERS[name]
        cmd = build_cmd(opencli_bin, info["cli_name"], action, message)
        try:
            proc = run_cmd(cmd, timeout)
        except subprocess.TimeoutExpired:
            attempts.append(
                {
                    "adapter": name,
                    "kind": info["kind"],
                    "command": cmd,
                    "ok": False,
                    "error": "timeout",
                    "message": f"执行超时，超过 {timeout} 秒。",
                }
            )
            continue
        payload = parse_jsonish(proc.stdout)
        result = {
            "adapter": name,
            "kind": info["kind"],
            "command": cmd,
            "ok": proc.returncode == 0,
            "exit_code": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
            "payload": payload,
            "answer": guess_answer(payload) if action in {"ask", "read"} else "",
        }
        attempts.append(result)
        if proc.returncode == 0:
            save_state({"last_adapter": name})
            return {
                "ok": True,
                "adapter": name,
                "adapter_kind": info["kind"],
                "action": action,
                "result": payload,
                "answer": result["answer"],
                "command": cmd,
            }

    return {
        "ok": False,
        "action": action,
        "error": "all_adapters_failed",
        "attempts": attempts,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Doubao chat relay via OpenCLI")
    parser.add_argument("action", choices=["login-check", "status", "new", "reset", "ask", "read", "last"])
    parser.add_argument("message", nargs="?", default=None)
    parser.add_argument("--adapter", choices=["auto", "web", "app"], default=os.environ.get("DOUBAO_RELAY_TARGET", "auto"))
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.action == "ask" and not args.message:
        payload = {
            "ok": False,
            "error": "missing_message",
            "message": "ask 需要问题文本。",
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2

    result = run_opencli_action(
        adapter=args.adapter,
        action=args.action,
        message=args.message,
        timeout=args.timeout,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
