from __future__ import annotations

import requests


def trigger_qlik_reload(tenant_url: str, api_key: str, app_id: str) -> tuple[str, str]:
    if not (tenant_url and api_key and app_id):
        return "skipped", "missing_config"
    url = f"{tenant_url.rstrip('/')}/api/v1/reloads"
    payload = {"appId": app_id, "partial": False}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    body = response.json()
    return body.get("id", "unknown"), body.get("status", "requested")
