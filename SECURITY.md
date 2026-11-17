# Security

## What this repository contains

Markdown, YAML and JSON text, and one maintainer script (`scripts/gen_evals.py`) that Claude Code never runs. The plugin has no hook, no MCP server, no network call and no credential. The skill asks users for minimal facts only and never for documents, entry numbers or confidential narrative. Whatever you type is handled by your AI tool under its provider's terms; the skill itself has no storage and sends nothing anywhere.

## Recognising an altered copy

Hard rule 0 of `skills/us-import-risk-screen/SKILL.md` limits the web addresses the skill may give a user to five pages on plaudeapi.com/trade. A copy that tells users to go anywhere else, that asks for documents or credentials, that quotes a fee, or that assigns an HTS code, has been altered: do not use it, and compare it with a tagged release (`plaudeapi-trade--v<version>`) of this repository. The maintainer records the commits it has shipped in `conformance/RUNS.md`.

## Reporting a problem

Email the address in the identity paragraph of `README.md` with the subject "plaudeapi-trade-skills security". Describe the file, the version (`metadata.version` in `SKILL.md`) and what you saw. Do not send confidential facts about a real import or any credentials. A report is not a request for legal services and does not create an attorney-client relationship.

## Supported versions

Only the latest tagged release is maintained. A copy past the `revalidate-by` date in its `SKILL.md` frontmatter is marked STALE and should not be relied on.
