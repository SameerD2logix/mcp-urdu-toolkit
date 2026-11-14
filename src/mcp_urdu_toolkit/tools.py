"""Pure functions behind the MCP tools (no MCP imports here, so they are easy to test and reuse)."""
from __future__ import annotations

import datetime as dt
import re

URDU_DIGITS = "۰۱۲۳۴۵۶۷۸۹"  # Extended Arabic-Indic digits used in Urdu (U+06F0-U+06F9)
ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"  # Arabic-Indic digits (U+0660-U+0669), sometimes pasted from Arabic text
TO_URDU = str.maketrans("0123456789", URDU_DIGITS)
TO_LATIN = str.maketrans(URDU_DIGITS + ARABIC_DIGITS, "0123456789" * 2)

HIJRI_MONTHS = [
    ("Muharram", "محرم"), ("Safar", "صفر"), ("Rabi ul Awwal", "ربیع الاول"), ("Rabi us Sani", "ربیع الثانی"),
    ("Jumada al Ula", "جمادی الاول"), ("Jumada al Sani", "جمادی الثانی"), ("Rajab", "رجب"), ("Shaban", "شعبان"),
    ("Ramazan", "رمضان"), ("Shawwal", "شوال"), ("Zul Qadah", "ذوالقعدہ"), ("Zul Hijjah", "ذوالحجہ"),
]

# First digits after 03 → network the number was originally issued by (numbers can be ported).
MOBILE_PREFIX = {"0": "Jazz", "1": "Zong", "2": "Jazz (ex-Warid)", "3": "Ufone", "4": "Telenor"}
AREA_CODES = {"21": "Karachi", "42": "Lahore", "51": "Islamabad/Rawalpindi", "41": "Faisalabad",
              "61": "Multan", "91": "Peshawar", "81": "Quetta", "52": "Sialkot", "55": "Gujranwala", "22": "Hyderabad"}


def normalize_pk_phone(phone: str) -> dict:
    """Normalise a Pakistani phone number to E.164 and describe it."""
    digits = re.sub(r"\D", "", convert_digits(phone, "latin"))
    for prefix in ("0092", "92", "0"):
        if digits.startswith(prefix):
            digits = digits[len(prefix):]
            break
    if len(digits) == 10 and digits.startswith("3"):
        return {"valid": True, "e164": "+92" + digits, "type": "mobile",
                "local": f"0{digits[:3]}-{digits[3:]}",
                "original_network": MOBILE_PREFIX.get(digits[1], "unknown"),
                "note": "Numbers can be ported, so the current network may differ."}
    if 9 <= len(digits) <= 10:
        area = digits[:2] if digits[:2] in AREA_CODES else digits[:3]
        return {"valid": True, "e164": "+92" + digits, "type": "landline",
                "local": f"0{area}-{digits[len(area):]}", "city": AREA_CODES.get(area, "unknown")}
    return {"valid": False, "input": phone, "reason": "Expected a 10-digit mobile (3XX...) or a landline with area code."}


def convert_digits(text: str, to: str = "urdu") -> str:
    """Convert digits between Latin (0-9) and Urdu (۰-۹)."""
    if to not in ("urdu", "latin"):
        raise ValueError("to must be 'urdu' or 'latin'")
    return text.translate(TO_URDU if to == "urdu" else TO_LATIN)


def _is_urdu_char(ch: str) -> bool:
    return "؀" <= ch <= "ۿ" or "ݐ" <= ch <= "ݿ" or "ﭐ" <= ch <= "﷿" or "ﹰ" <= ch <= "﻿"


def urdu_text_stats(text: str, words_per_minute: int = 150) -> dict:
    """Word/character counts, share of Urdu script, and reading time."""
    words = text.split()
    letters = [c for c in text if c.isalpha()]
    urdu = sum(_is_urdu_char(c) for c in letters)
    return {
        "words": len(words),
        "characters": len(text),
        "characters_no_spaces": len(re.sub(r"\s", "", text)),
        "urdu_script_ratio": round(urdu / len(letters), 2) if letters else 0.0,
        "script": "urdu" if letters and urdu / len(letters) > 0.6 else "latin/roman" if letters and urdu == 0 else "mixed",
        "reading_minutes": round(len(words) / max(words_per_minute, 1), 1),
    }


def _gregorian_to_jdn(d: dt.date) -> int:
    a = (14 - d.month) // 12
    y = d.year + 4800 - a
    m = d.month + 12 * a - 3
    return d.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def hijri_date(date: str = "", offset_days: int = 0) -> dict:
    """Approximate Hijri date with the tabular (arithmetic) Islamic calendar.

    Pakistan follows moon sighting, so the real date can differ by 1-2 days: use offset_days to adjust.
    """
    g = dt.date.fromisoformat(date) if date else dt.date.today()
    jd = _gregorian_to_jdn(g) + offset_days
    l = jd - 1948440 + 10632
    n = (l - 1) // 10631
    l = l - 10631 * n + 354
    j = ((10985 - l) // 5316) * ((50 * l) // 17719) + (l // 5670) * ((43 * l) // 15238)
    l = l - ((30 - j) // 15) * ((17719 * j) // 50) - (j // 16) * ((15238 * j) // 43) + 29
    month = (24 * l) // 709
    day = l - (709 * month) // 24
    year = 30 * n + j - 30
    en, ur = HIJRI_MONTHS[month - 1]
    return {
        "gregorian": g.isoformat(), "day": day, "month": month, "year": year,
        "text": f"{day} {en} {year} AH",
        "text_urdu": f"{convert_digits(str(day))} {ur} {convert_digits(str(year))} ہجری",
        "note": "Tabular calendar: may differ by 1-2 days from the moon-sighting date in Pakistan.",
    }


def format_pkr(amount: float, words: bool = True) -> dict:
    """Format rupees with South Asian grouping (1,25,000) and lakh/crore words."""
    negative = amount < 0
    whole = int(round(abs(amount)))
    s = str(whole)
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        s = ",".join(groups + [tail])
    out = {"formatted": f"{'-' if negative else ''}Rs {s}"}
    if words:
        crore, rest = divmod(whole, 10_000_000)
        lakh, rest = divmod(rest, 100_000)
        thousand, rest = divmod(rest, 1_000)
        parts = [f"{v} {name}" for v, name in ((crore, "crore"), (lakh, "lakh"), (thousand, "hazar")) if v]
        if rest or not parts:
            parts.append(str(rest))
        out["words"] = ("minus " if negative else "") + " ".join(parts)
    return out
