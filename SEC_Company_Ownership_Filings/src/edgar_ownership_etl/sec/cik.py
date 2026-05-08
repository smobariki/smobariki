def normalize_cik(value: str) -> str:
    digits = "".join(ch for ch in value if ch.isdigit())
    if not digits:
        raise ValueError("CIK must contain digits")
    if len(digits) > 10:
        raise ValueError("CIK longer than 10 digits")
    return digits.zfill(10)


def cik_for_archive(value: str) -> str:
    return str(int(normalize_cik(value)))
