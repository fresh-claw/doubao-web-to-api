#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

os.environ.setdefault("NODE_NO_WARNINGS", "1")


STATE_DIR = Path.home() / ".doubao-web-to-api"
STATE_FILE = STATE_DIR / "state.json"
DEFAULT_TIMEOUT = int(os.environ.get("DOUBAO_WEB_TO_API_TIMEOUT", "180"))
DEFAULT_CDP_ENDPOINT = os.environ.get("DOUBAO_WEB_TO_API_CDP_ENDPOINT", "http://127.0.0.1:9231")
DEFAULT_START_URL = os.environ.get("DOUBAO_WEB_TO_API_START_URL", "https://www.doubao.com/chat/")
DEFAULT_PROFILE_DIR = os.environ.get(
    "DOUBAO_WEB_TO_API_PROFILE_DIR",
    str(STATE_DIR / "browser-profile"),
)

MODE_LABELS = {
    "quick": "快速",
    "thinking": "思考",
    "expert": "专家",
    "快速": "快速",
    "思考": "思考",
    "专家": "专家",
}

MODE_ITEM_INDEX = {
    "快速": 0,
    "思考": 1,
    "专家": 3,
}


def ensure_state_dir() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def load_state() -> dict[str, Any]:
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(payload: dict[str, Any]) -> None:
    ensure_state_dir()
    merged = load_state()
    merged.update(payload)
    STATE_FILE.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")


def normalize_mode(value: str | None) -> str | None:
    if not value:
        return None
    return MODE_LABELS.get(value.strip().lower(), MODE_LABELS.get(value.strip(), value.strip()))


def parse_jsonish(text: str) -> Any:
    text = (text or "").strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        return text


def endpoint_alive(endpoint: str, timeout: float = 1.5) -> bool:
    try:
        with urllib.request.urlopen(endpoint.rstrip("/") + "/json/version", timeout=timeout):
            return True
    except Exception:
        return False


def wait_for_endpoint(endpoint: str, timeout: int) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if endpoint_alive(endpoint):
            return True
        time.sleep(0.5)
    return False


def get_port_from_endpoint(endpoint: str) -> int:
    value = endpoint.rsplit(":", 1)[-1].strip().rstrip("/")
    return int(value)


def browser_candidates() -> list[str]:
    system = platform.system()
    if system == "Darwin":
        return [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
    if system == "Windows":
        roots = [
            os.environ.get("PROGRAMFILES", r"C:\Program Files"),
            os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"),
            os.environ.get("LOCALAPPDATA", ""),
        ]
        names = [
            r"Google\Chrome\Application\chrome.exe",
            r"Microsoft\Edge\Application\msedge.exe",
            r"Chromium\Application\chrome.exe",
        ]
        out: list[str] = []
        for root in roots:
            if not root:
                continue
            for name in names:
                out.append(str(Path(root) / name))
        return out
    return ["google-chrome", "chromium", "chromium-browser", "microsoft-edge"]


def resolve_browser_path(path_value: str | None) -> str | None:
    if path_value:
        path = Path(path_value).expanduser()
        if path.exists():
            return str(path)
        return path_value
    for item in browser_candidates():
        path = Path(item)
        if path.exists():
            return str(path)
    return None


def launch_browser(browser_path: str, endpoint: str, profile_dir: str, start_url: str) -> dict[str, Any]:
    ensure_state_dir()
    profile = Path(profile_dir).expanduser()
    profile.mkdir(parents=True, exist_ok=True)
    cmd = [
        browser_path,
        f"--remote-debugging-port={get_port_from_endpoint(endpoint)}",
        f"--user-data-dir={str(profile)}",
        "--no-first-run",
        "--no-default-browser-check",
        start_url,
    ]
    subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    return {
        "browser_path": browser_path,
        "cdp_endpoint": endpoint,
        "profile_dir": str(profile),
        "start_url": start_url,
        "command": cmd,
    }


def playwright_import() -> tuple[Any | None, dict[str, Any] | None]:
    try:
        from playwright.sync_api import sync_playwright

        return sync_playwright, None
    except Exception as exc:
        return None, {
            "ok": False,
            "error": "playwright_not_found",
            "message": f"未找到可用的 Playwright：{exc}",
        }


def visible(locator: Any) -> Any:
    count = locator.count()
    for index in range(count):
        item = locator.nth(index)
        try:
            if item.is_visible():
                return item
        except Exception:
            continue
    return locator.first


def connect_chat_page(sync_playwright: Any, endpoint: str) -> tuple[Any, Any, Any]:
    playwright = sync_playwright().start()
    browser = playwright.chromium.connect_over_cdp(endpoint)
    pages: list[Any] = []
    for context in browser.contexts:
        pages.extend(context.pages)
    page = next((item for item in pages if "doubao.com/chat" in item.url), None)
    if page is None:
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()
        page.goto(DEFAULT_START_URL, wait_until="domcontentloaded")
    page.bring_to_front()
    page.wait_for_timeout(500)
    return playwright, browser, page


def current_mode(page: Any) -> str:
    text = visible(page.locator('[data-testid="mode-select-action-button"]')).inner_text().strip()
    return normalize_mode(text.split()[0]) or text.split()[0]


def is_logged_in(page: Any) -> bool:
    try:
        return visible(page.locator('textarea[placeholder="发消息..."]')).is_visible()
    except Exception:
        return False


def select_mode(page: Any, target_mode: str) -> str:
    target = normalize_mode(target_mode)
    if not target or target not in MODE_ITEM_INDEX:
        raise RuntimeError(f"不支持的模式：{target_mode}")
    if current_mode(page) == target:
        return target
    selectors = [
        f'[data-testid="deep-thinking-action-item-{MODE_ITEM_INDEX[target]}"]',
        f'[role="menuitem"]:has-text("{target}")',
        f'text="{target}"',
    ]
    for _ in range(2):
        visible(page.locator('[data-testid="mode-select-action-button"]')).click()
        page.wait_for_timeout(500)
        for selector in selectors:
            loc = page.locator(selector)
            if loc.count() == 0:
                continue
            try:
                visible(loc).click(timeout=3000)
                page.wait_for_timeout(800)
                mode = current_mode(page)
                if mode == target:
                    return mode
            except Exception:
                continue
    raise RuntimeError(f"模式切换失败：{target}")


def create_new_chat(page: Any) -> None:
    visible(page.locator('[data-testid="create_conversation_button"]')).click()
    page.wait_for_timeout(1200)
    visible(page.locator('textarea[placeholder="发消息..."]')).wait_for(state="visible", timeout=10000)


def read_messages(page: Any) -> list[dict[str, str]]:
    items = page.locator(
        '[data-testid="message-list"] [data-testid="send_message"], '
        '[data-testid="message-list"] [data-testid="receive_message"]'
    )
    messages: list[dict[str, str]] = []
    for index in range(items.count()):
        item = items.nth(index)
        try:
            text = (item.inner_text(timeout=500) or "").strip()
            if not text:
                continue
            testid = item.get_attribute("data-testid") or ""
            role = "assistant" if testid == "receive_message" else "user"
            messages.append({"role": role, "text": text})
        except Exception:
            continue
    return messages


def latest_reply(messages: list[dict[str, str]]) -> str:
    for item in reversed(messages):
        if item["role"] == "assistant":
            return item["text"]
    return ""


def send_and_wait(page: Any, prompt: str, timeout: int) -> dict[str, Any]:
    recv = page.locator('[data-testid="receive_message"]')
    before = recv.count()
    ta = visible(page.locator('textarea[placeholder="发消息..."]'))
    ta.click()
    ta.fill(prompt)
    page.keyboard.press("Enter")
    deadline = time.time() + timeout
    last_text = ""
    stable = 0
    while time.time() < deadline:
        count = recv.count()
        if count > before:
            text = (recv.nth(count - 1).inner_text(timeout=1000) or "").strip()
            if text:
                if text == last_text:
                    stable += 1
                else:
                    last_text = text
                    stable = 0
                if stable >= 2:
                    return {
                        "ok": True,
                        "answer": text,
                        "receive_count": count,
                    }
        page.wait_for_timeout(1000)
    return {
        "ok": False,
        "error": "timeout",
        "message": f"执行超时，超过 {timeout} 秒。",
        "answer": last_text,
        "receive_count": recv.count(),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Doubao Web 2 API via Playwright")
    parser.add_argument(
        "action",
        choices=["open", "login-check", "status", "new", "reset", "ask", "read", "last"],
    )
    parser.add_argument("message", nargs="?", default=None)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--mode", choices=["quick", "thinking", "expert", "快速", "思考", "专家"], default=None)
    parser.add_argument("--cdp-endpoint", default=load_state().get("cdp_endpoint", DEFAULT_CDP_ENDPOINT))
    parser.add_argument("--browser-path", default=load_state().get("browser_path"))
    parser.add_argument("--profile-dir", default=load_state().get("profile_dir", DEFAULT_PROFILE_DIR))
    parser.add_argument("--start-url", default=load_state().get("start_url", DEFAULT_START_URL))
    return parser


def connect_or_error(args: argparse.Namespace) -> tuple[Any | None, Any | None, Any | None, dict[str, Any] | None]:
    sync_playwright, import_error = playwright_import()
    if import_error:
        return None, None, None, import_error
    if not endpoint_alive(args.cdp_endpoint):
        return None, None, None, {
            "ok": False,
            "error": "cdp_not_available",
            "message": "未连接到浏览器调试端口，请先执行 open。",
            "cdp_endpoint": args.cdp_endpoint,
        }
    try:
        return (*connect_chat_page(sync_playwright, args.cdp_endpoint), None)
    except Exception as exc:
        return None, None, None, {
            "ok": False,
            "error": "connect_failed",
            "message": f"连接豆包页面失败：{exc}",
            "cdp_endpoint": args.cdp_endpoint,
        }


def close_handles(playwright: Any | None, browser: Any | None) -> None:
    try:
        if playwright:
            playwright.stop()
    except Exception:
        pass


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

    if args.action == "open":
        browser_path = resolve_browser_path(args.browser_path)
        if not browser_path:
            payload = {
                "ok": False,
                "error": "browser_not_found",
                "message": "未找到可用浏览器，请通过 --browser-path 指定 Chrome、Edge 或 Chromium。",
            }
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 1
        launched = launch_browser(
            browser_path=browser_path,
            endpoint=args.cdp_endpoint,
            profile_dir=args.profile_dir,
            start_url=args.start_url,
        )
        ok = wait_for_endpoint(args.cdp_endpoint, timeout=min(args.timeout, 30))
        payload = {
            "ok": ok,
            "action": "open",
            "browser_path": browser_path,
            "cdp_endpoint": args.cdp_endpoint,
            "profile_dir": args.profile_dir,
            "start_url": args.start_url,
            "command": launched["command"],
        }
        if not ok:
            payload["error"] = "browser_launch_timeout"
            payload["message"] = "浏览器已启动，但调试端口未在预期时间内就绪。"
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 1
        save_state(
            {
                "browser_path": browser_path,
                "cdp_endpoint": args.cdp_endpoint,
                "profile_dir": args.profile_dir,
                "start_url": args.start_url,
            }
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    playwright = None
    browser = None
    page = None
    playwright, browser, page, error = connect_or_error(args)
    if error:
        print(json.dumps(error, ensure_ascii=False, indent=2))
        return 1

    try:
        save_state(
            {
                "cdp_endpoint": args.cdp_endpoint,
                "browser_path": args.browser_path,
                "profile_dir": args.profile_dir,
                "start_url": args.start_url,
            }
        )

        action = "status" if args.action == "login-check" else "new" if args.action == "reset" else args.action

        if action == "status":
            logged_in = is_logged_in(page)
            payload = {
                "ok": logged_in,
                "action": action,
                "logged_in": logged_in,
                "title": page.title(),
                "url": page.url,
                "current_mode": current_mode(page) if logged_in else "",
                "cdp_endpoint": args.cdp_endpoint,
            }
            if not logged_in:
                payload["error"] = "not_logged_in"
                payload["message"] = "豆包网页未登录，请先在浏览器里完成登录。"
                print(json.dumps(payload, ensure_ascii=False, indent=2))
                return 1
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0

        if not is_logged_in(page):
            payload = {
                "ok": False,
                "error": "not_logged_in",
                "message": "豆包网页未登录，请先在浏览器里完成登录。",
                "action": action,
            }
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 1

        if action == "new":
            create_new_chat(page)
            if args.mode:
                mode = select_mode(page, args.mode)
            else:
                mode = current_mode(page)
            payload = {
                "ok": True,
                "action": action,
                "current_mode": mode,
                "url": page.url,
            }
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0

        if action == "read":
            messages = read_messages(page)
            payload = {
                "ok": True,
                "action": action,
                "messages": messages,
                "answer": latest_reply(messages),
                "current_mode": current_mode(page),
                "url": page.url,
            }
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0

        if action == "last":
            messages = read_messages(page)
            answer = latest_reply(messages)
            payload = {
                "ok": bool(answer),
                "action": action,
                "answer": answer,
                "current_mode": current_mode(page),
                "url": page.url,
            }
            if not answer:
                payload["error"] = "no_answer"
                payload["message"] = "当前页面没有可读取的豆包回复。"
                print(json.dumps(payload, ensure_ascii=False, indent=2))
                return 1
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0

        if action == "ask":
            if args.mode:
                mode = select_mode(page, args.mode)
                save_state({"last_mode": mode})
            else:
                mode = current_mode(page)
            result = send_and_wait(page, args.message, timeout=args.timeout)
            payload = {
                "ok": result.get("ok", False),
                "action": action,
                "question": args.message,
                "answer": result.get("answer", ""),
                "current_mode": mode,
                "url": page.url,
            }
            if payload["ok"]:
                print(json.dumps(payload, ensure_ascii=False, indent=2))
                return 0
            payload["error"] = result.get("error", "ask_failed")
            payload["message"] = result.get("message", "读取回复失败。")
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 1

        payload = {
            "ok": False,
            "error": "unsupported_action",
            "message": f"不支持的动作：{action}",
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1
    finally:
        close_handles(playwright, browser)


if __name__ == "__main__":
    sys.exit(main())
