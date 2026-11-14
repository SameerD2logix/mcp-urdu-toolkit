import asyncio

import pytest

from mcp_urdu_toolkit import tools
from mcp_urdu_toolkit.server import server


def test_phone_mobile_and_landline():
    m = tools.normalize_pk_phone("0333-1234567")
    assert m["e164"] == "+923331234567" and m["type"] == "mobile" and m["original_network"] == "Ufone"
    assert tools.normalize_pk_phone("۰۳۰۰۱۲۳۴۵۶۷")["e164"] == "+923001234567"  # Urdu digits
    l = tools.normalize_pk_phone("042-35761234")
    assert l["type"] == "landline" and l["city"] == "Lahore" and l["local"] == "042-35761234"
    assert tools.normalize_pk_phone("123")["valid"] is False


def test_digits_round_trip():
    assert tools.convert_digits("Rs 2026") == "Rs ۲۰۲۶"
    assert tools.convert_digits("۲۰۲۶ اور ٢٠", "latin") == "2026 اور 20"
    with pytest.raises(ValueError):
        tools.convert_digits("1", "roman")


def test_text_stats():
    s = tools.urdu_text_stats("یہ ایک ٹیسٹ ہے")
    assert s["words"] == 4 and s["script"] == "urdu"
    assert tools.urdu_text_stats("Aap kaise hain")["script"] == "latin/roman"


def test_hijri_known_dates():
    # 1 Jan 2000 was 24/25 Ramadan 1420 depending on sighting
    h = tools.hijri_date("2000-01-01")
    assert (h["year"], h["month"]) == (1420, 9) and h["day"] in (24, 25)
    # offset moves the day
    assert tools.hijri_date("2000-01-01", offset_days=1)["day"] == h["day"] + 1
    assert "ہجری" in h["text_urdu"]


def test_pkr_grouping_and_words():
    assert tools.format_pkr(1250000) == {"formatted": "Rs 12,50,000", "words": "12 lakh 50 hazar"}
    assert tools.format_pkr(25_00_00_000)["formatted"] == "Rs 25,00,00,000"
    assert tools.format_pkr(999)["formatted"] == "Rs 999"
    assert tools.format_pkr(-1500)["words"] == "minus 1 hazar 500"


def test_server_exposes_all_tools():
    names = {t.name for t in asyncio.run(server.list_tools())}
    assert names == {"normalize_pk_phone", "convert_digits", "urdu_text_stats", "hijri_date", "format_pkr"}
