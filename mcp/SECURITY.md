# Security note: PlaudeAPI Trade public-facts MCP server

Scope: this server serves public facts only. It is general information, not legal advice, and using it creates no attorney-client relationship. Published by Bandi & Associates PLLC.

## What it cannot do, by construction
- No free-text input. Every tool parameter is a JSON Schema `enum` (a guide slug) or absent, and each input schema declares `additionalProperties: false`, so a conforming client has no field in which to send facts about a matter. The server does not itself reject undeclared extra arguments; it ignores them and never reads or stores them. A test (`test_inputs_are_enums_only_no_free_text`) fails the build if a free-text parameter is added.
- No state. No session, no handle, no database, no files written, no cookies, no accounts, no authentication. The 2026-07-28 MCP revision has no protocol session.
- No outbound calls. It reads one bundled `snapshot.json` and makes no network request at run time. It never calls a model, the Firm App, or any private system.
- No write tools. All tools carry `readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true`, `openWorldHint: false`. No resources, no prompts, no sampling, no elicitation.
- No selling action. Tool descriptions contain no price and no checkout wording. Each result's `next_step` names the published US$495 Trade diagnostic and links to the free check and to the public page that describes it; there is no checkout, payment or engagement action.

## Logging
- The server code logs nothing about requests and installs no middleware. SDK log level is set to WARNING. A test asserts that a tool argument is not present in captured logs.
- Known behaviour: when a client sends an invalid value, the SDK returns a validation error to that client that echoes the rejected value back to the same caller. It is not stored. If a host adds access logs in front of the server, configure them to drop request bodies and query strings.

## If hosted over HTTP (maintainer decision; nothing is hosted today)
- Terminate TLS at the host; bind the app to localhost or a private port.
- Rate-limit at the edge (suggested start: 60 requests per minute per IP, burst 20) and cap request body size (for example 4 KiB; legitimate calls are under 200 bytes).
- Validate the `Origin` header and keep the SDK's DNS-rebinding protection enabled when binding to anything other than localhost.
- Disable platform request-body logging; keep only status, path, time and a truncated IP (or none). Say so on the privacy page before launch.
- Publish a privacy statement for the endpoint that matches this note; the browser tool's "stores nothing on any server" wording covers the browser tool only and must not be reused for a hosted endpoint without checking the host's own logs.
- Data freshness: rebuild and redeploy the snapshot whenever a guide changes (`python scripts/build_snapshot.py`, review the diff, bump version). Each result shows `verified`, `updated` and `snapshot_generated` `age_days` and `stale` (older than 14 days, against the server's local date), and a stale result starts with a notice line, so a stale snapshot is visible to the reader. The builder refuses to run when a dated guide's verified date is over 14 days old unless `MCP_FRESHNESS_ACK=<reason>` is set; the override is recorded in the snapshot.

## Reporting
Use the firm's responsible-disclosure page: https://plaudeapi.com/legal/responsible-disclosure/
