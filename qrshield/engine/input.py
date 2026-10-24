from __future__ import annotations
import re
from .lexical import extract_urls, normalized

_TRIM = " \t\r\n\u00a0\u200b\u200c\u200d\ufeff'\"`<>()[]{}"

def clean_link(value: str) -> tuple[str | None, list[str], str | None]:
    text = value.strip(_TRIM).replace("\u00a0", " ").replace("\u200b", "").replace("\u200c", "").replace("\u200d", "")
    text = text.replace("(dot)", ".").replace("(DOT)", ".").replace("[.]", ".")
    candidates = extract_urls(text)
    if not candidates and text:
        first = text.split()[0].rstrip(".,;:!?")
        if re.fullmatch(r"(?:[\w-]+\.)+[a-z]{2,}(?:[/?#].*)?", first, re.I): candidates = [normalized(first)]
    if not candidates: return None, [], "Enter a valid web link to analyze."
    return candidates[0], candidates[1:], None
