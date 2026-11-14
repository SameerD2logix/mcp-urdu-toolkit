# MCP Urdu Toolkit

> An **MCP server** that gives Claude (and any MCP client) reliable Pakistan/Urdu helpers: phone numbers, Urdu digits, Hijri dates and lakh/crore rupee formatting.

![mcp](https://img.shields.io/badge/MCP-server-6E56CF) ![python](https://img.shields.io/badge/python-3.10%2B-3776AB) ![license](https://img.shields.io/badge/license-MIT-green)

LLMs often get these small local details wrong (`Rs 1,250,000` instead of `Rs 12,50,000`, mixed digit
scripts, invalid phone formats). This server makes them deterministic.

## Tools

| Tool | Example |
|---|---|
| `normalize_pk_phone` | `0333-1234567` → `+923331234567`, mobile, originally Ufone · `042-35761234` → landline, Lahore |
| `convert_digits` | `Rs 2026` ↔ `Rs ۲۰۲۶` |
| `urdu_text_stats` | words, characters, Urdu vs Roman script, reading time |
| `hijri_date` | `2000-01-01` → `24 Ramazan 1420 AH` / `۲۴ رمضان ۱۴۲۰ ہجری` (tabular, with `offset_days` for moon sighting) |
| `format_pkr` | `1250000` → `Rs 12,50,000` · `12 lakh 50 hazar` |

## Install

```bash
pip install git+https://github.com/SameerD2logix/mcp-urdu-toolkit
```

### Claude Code
```bash
claude mcp add urdu-toolkit -- mcp-urdu-toolkit
```

### Claude Desktop (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "urdu-toolkit": { "command": "mcp-urdu-toolkit" }
  }
}
```

Then ask: *"Format 2.5 crore in rupees and convert the year to Urdu digits"* or *"Clean these phone numbers"*.

## Design

- `tools.py`: pure functions, no MCP imports, easy to test and reuse in other Python code.
- `server.py`: thin MCP layer (official `mcp` Python SDK v2, stdio transport).
- No network access, no data stored. Everything runs locally.

## Development

```bash
pip install -e . pytest
pytest -q
```

## Author

**Sameer Hussain** · [LinkedIn](https://www.linkedin.com/in/sameer-hussain-87368a164) · [D2Logix](https://d2logix.com)
