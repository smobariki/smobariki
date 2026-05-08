import re


def parse_schedule_13(raw_text: str) -> dict:
    sections = {f"Item {i}": None for i in range(1, 8)}
    for item in sections:
        m = re.search(rf"({item}.*?)(?=Item \d|$)", raw_text, re.IGNORECASE | re.DOTALL)
        if m:
            sections[item] = m.group(1).strip()
    return {"source_parse_method": "text_fallback", "parse_confidence": None, "sections": sections}
