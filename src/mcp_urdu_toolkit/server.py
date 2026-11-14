"""MCP server entry point. Exposes the functions in tools.py as MCP tools (stdio transport)."""
from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from . import tools

server = MCPServer(
    "urdu-toolkit",
    instructions=(
        "Helpers for Pakistani and Urdu content: phone numbers, Urdu digits, text stats, "
        "approximate Hijri dates and rupee formatting. Hijri dates are arithmetic approximations."
    ),
)


@server.tool()
def normalize_pk_phone(phone: str) -> dict:
    """Normalise a Pakistani phone number (any format, Latin or Urdu digits) to +92 E.164,
    and say if it is a mobile (with its original network) or a landline (with its city)."""
    return tools.normalize_pk_phone(phone)


@server.tool()
def convert_digits(text: str, to: str = "urdu") -> str:
    """Convert the digits in text to Urdu digits (to="urdu") or back to 0-9 (to="latin")."""
    return tools.convert_digits(text, to)


@server.tool()
def urdu_text_stats(text: str, words_per_minute: int = 150) -> dict:
    """Count words and characters, detect Urdu vs Roman/Latin script, and estimate reading time."""
    return tools.urdu_text_stats(text, words_per_minute)


@server.tool()
def hijri_date(date: str = "", offset_days: int = 0) -> dict:
    """Approximate Hijri (Islamic) date for an ISO date (YYYY-MM-DD, default today), in English and Urdu.
    Use offset_days (e.g. -1) to match the local moon-sighting calendar."""
    return tools.hijri_date(date, offset_days)


@server.tool()
def format_pkr(amount: float, words: bool = True) -> dict:
    """Format a rupee amount with lakh/crore grouping, e.g. 1250000 -> "Rs 12,50,000" / "12 lakh 50 hazar"."""
    return tools.format_pkr(amount, words)


def main() -> None:
    server.run()  # stdio


if __name__ == "__main__":
    main()
