# PlaudeAPI Trade: public-facts MCP server

A read-only [Model Context Protocol](https://modelcontextprotocol.io/specification/2026-07-28) server (revision 2026-07-28, official Python SDK `mcp` 2.x). It serves dates, sources and guide links from the free guides at [plaudeapi.com/trade/guides](https://plaudeapi.com/trade/guides/). It accepts no user facts and stores nothing.

General information only, not legal advice. Using it does not create an attorney-client relationship. Published by Bandi & Associates PLLC. Every answer points to the free check at <https://plaudeapi.com/trade/> or the US$495 attorney-signed diagnostic described on the public site.

## Tools

| Tool | Input | Returns |
|---|---|---|
| `list_guides` | none | The public guides with page links and the date each records as verified or updated |
| `get_rule_dates` | `guide`: `foreign-ior` or `ieepa-refund` | The dated milestones the guide publishes, each with its source citation (for example the foreign importer-of-record rule: effective 2027-01-05, FR Doc. 2026-22735) |
| `get_sources` | `guide`: `foreign-ior`, `ieepa-refund`, `cf28` or `eu` | The primary authorities the guide cites, with links, and the date they were read |

Every result carries the disclaimer, `attribution` ("Bandi & Associates PLLC"), `verified` / `updated` dates, `snapshot_generated`, and `next_step` links. Results have an `outputSchema` and a matching text copy. All tools are annotated read-only, non-destructive, idempotent, closed-world. Inputs are enums only, so a client cannot submit facts about a matter. See [SECURITY.md](SECURITY.md).

Dates are as the guides publish them; rules change. Check the primary source before relying on a date.

## Install

Requires Python 3.10+ (tested on 3.14).

```bash
cd mcp
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install .
plaudeapi-trade-mcp          # stdio
```

When published to PyPI (founder decision) the same server runs with `uvx plaudeapi-trade-mcp`.

**Claude Desktop** (`claude_desktop_config.json`):

```json
{ "mcpServers": { "plaudeapi-trade": { "command": "plaudeapi-trade-mcp" } } }
```

Use the full path to the executable in the venv if it is not on PATH.

**Claude Code:** `claude mcp add plaudeapi-trade -- plaudeapi-trade-mcp`

**Cursor, VS Code, Codex and other clients:** add a stdio server whose command is `plaudeapi-trade-mcp` (or `python -m plaudeapi_trade_mcp.server`) in that client's MCP settings.

Streamable HTTP for local testing: `plaudeapi-trade-mcp --http --port 8000` (see SECURITY.md before exposing it).

## Data

`src/plaudeapi_trade_mcp/snapshot.json` is generated from the public pages only (the guides index and each guide):

```bash
python scripts/build_snapshot.py     # reads https://plaudeapi.com/trade/guides/ and each listed guide
```

No private data, no Firm App, no credentials. `plaudeapi.com/llms.txt` does not exist (404 on 2026-11-16); if the site later publishes one, the builder can read it. Review the diff of the regenerated file before committing; bump the version when it changes.

## Tests

```bash
pip install ".[test]" && pytest
```

No network: an in-memory MCP client runs against the bundled snapshot, and the builder is tested against saved copies of public pages in `tests/fixtures/`.

## Registry metadata

[`server.json`](server.json) is a draft for the official MCP Registry (preview). The namespace `io.github.peterzhang12312/...` needs GitHub-account verification, or use a DNS-verified `com.plaudeapi/...` namespace. Publishing needs a PyPI release first. Both are founder steps; nothing has been published or registered.

## Hosting options (decision for the founder; nothing deployed, no account created)

| Option | Fit | Approx. cost (check current pricing before deciding) |
|---|---|---|
| None: local stdio only, users install from PyPI or Git | Zero server, zero logs, nothing for the firm to disclose | US$0 |
| Render web service (this Python app, `--http`) | Runs as is; free tier sleeps when idle (slow first call); paid tier stays up | free, or about US$7/month for an always-on small instance |
| Cloudflare Worker (site already on Cloudflare) | Needs a small TypeScript port using the official TypeScript SDK reading the same `snapshot.json`; edge rate limiting built in | free tier covers low volume; paid plan about US$5/month |
| Static file only (`snapshot.json` on the site) | Not an MCP endpoint; useful as a fallback source | US$0 |

Prices are from general knowledge, not re-checked today. Hosted use needs a privacy statement matching SECURITY.md, a DNS name, and a decision on logs; see SECURITY.md.

## Licence

MIT. Legal authorities cited are public law; verify them before relying on them.
