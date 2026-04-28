from __future__ import annotations

import re

EIGHTK_EVENT_RULES = {
    "earnings_release": ["results of operations", "earnings release"],
    "guidance_update": ["guidance", "outlook"],
    "acquisition_or_merger": ["acquisition", "merger"],
    "material_agreement": ["material definitive agreement"],
    "bankruptcy_or_restructuring": ["bankruptcy", "restructuring"],
    "executive_change": ["departure of directors", "appointment of officers"],
    "auditor_change": ["changes in registrant's certifying accountant"],
    "dividend_or_capital_allocation": ["dividend", "share repurchase"],
    "litigation_or_regulatory": ["legal proceedings", "investigation"],
    "debt_or_financing": ["entry into a material definitive agreement", "debt"],
    "delisting_or_listing_issue": ["delisting", "listing standards"],
}


def parse_eightk_sections(raw_text: str | None) -> list[dict]:
    if not raw_text:
        return []
    items = []
    pattern = re.compile(r"Item\s+(\d+\.\d+)", flags=re.IGNORECASE)
    matches = list(pattern.finditer(raw_text))
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw_text)
        item_number = match.group(1)
        section_text = raw_text[start:end].strip()[:15000]
        items.append(
            {
                "item_number": item_number,
                "item_description": f"Item {item_number}",
                "section_text": section_text,
            }
        )
    return items


def classify_eightk_events(raw_text: str | None) -> list[dict]:
    if not raw_text:
        return []
    lower = raw_text.lower()
    tags = []
    for category, keywords in EIGHTK_EVENT_RULES.items():
        for keyword in keywords:
            if keyword in lower:
                tags.append(
                    {
                        "event_category": category,
                        "event_keyword": keyword,
                        "confidence_method": "rule_based_keyword",
                        "matched_text": keyword,
                    }
                )
    if not tags:
        tags.append(
            {
                "event_category": "other_material_event",
                "event_keyword": "fallback",
                "confidence_method": "fallback",
                "matched_text": "no rule matched",
            }
        )
    return tags
