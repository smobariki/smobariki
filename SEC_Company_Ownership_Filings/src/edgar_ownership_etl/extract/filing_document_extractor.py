from __future__ import annotations

from edgar_ownership_etl.sec.client import SecClient


def select_ownership_document(client: SecClient, archive_base_url: str, primary_document: str | None) -> tuple[str, str]:
    if primary_document and primary_document.lower().endswith(".xml"):
        txt = client.get(f"{archive_base_url}/{primary_document}").text
        if "ownershipDocument" in txt:
            return primary_document, txt

    index = client.get(f"{archive_base_url}/index.json").json()
    for item in index.get("directory", {}).get("item", []):
        name = item.get("name", "")
        if name.lower().endswith(".xml"):
            txt = client.get(f"{archive_base_url}/{name}").text
            if "ownershipDocument" in txt:
                return name, txt

    if primary_document:
        return primary_document, client.get(f"{archive_base_url}/{primary_document}").text
    raise ValueError("No filing document could be resolved")
