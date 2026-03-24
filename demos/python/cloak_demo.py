"""
Cloak 本地 HTTP API 最小示例（POST + JSON）。
完整接口与指纹字段请参考主仓库 docs/ApiDemo/cloak_api_example.py
"""
from __future__ import annotations

import json
import os
import sys
import time
from typing import Any, Dict, Optional

import requests

BASE = os.environ.get("CLOAK_BASE_URL", "http://127.0.0.1:54381").rstrip("/")
CLEANUP = bool(os.environ.get("CLOAK_CLEANUP"))


def post(path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    url = f"{BASE}{path}"
    r = requests.post(url, json=body or {}, headers={"Content-Type": "application/json"}, timeout=60)
    r.raise_for_status()
    return r.json()


def main() -> None:
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

    print("Cloak API demo | base =", BASE)

    print_result("group_list", post("/group/list", {}))

    group_name = f"demo-py-{int(time.time())}"
    gr = post("/group/add", {"groupName": group_name})
    print_result("group_add", gr)
    group_id = None
    if gr.get("success") and gr.get("data"):
        group_id = gr["data"].get("id")
    if not group_id:
        gl = post("/group/list", {})
        lst = (gl.get("data") or {}).get("list") or []
        if lst:
            group_id = lst[0].get("id")
    if not group_id:
        print("无法取得 groupId，退出")
        return

    suffix = str(int(time.time()))
    br = post(
        "/browser/update",
        {
            "name": f"demo-browser-py-{suffix}",
            "groupId": group_id,
            "randomFingerprint": True,
            "homepageUrl": "https://www.example.com",
        },
    )
    print_result("browser_update (create)", br)
    browser_id = None
    if br.get("success") and br.get("data"):
        browser_id = br["data"].get("id")

    print_result("browser_list", post("/browser/list", {"page": 0, "pageSize": 10}))

    if browser_id:
        print_result("browser_open", post("/browser/open", {"id": browser_id}))
        print_result("browser_close", post("/browser/close", {"id": browser_id}))

    if CLEANUP and browser_id:
        print_result("browser_delete", post("/browser/delete", {"id": browser_id}))
    if CLEANUP and group_id:
        print_result("group_delete", post("/group/delete", {"id": group_id}))


def print_result(title: str, data: Dict[str, Any]) -> None:
    print("\n===", title, "===")
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
