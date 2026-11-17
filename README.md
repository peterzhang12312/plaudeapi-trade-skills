# PlaudeAPI Trade — agent skills

Skills that teach an AI coding/chat agent to run a **fail-closed preliminary screen of a U.S. import situation** the way the free tool at **[plaudeapi.com/trade](https://plaudeapi.com/trade)** does: minimal facts in, observations out, every date labelled POTENTIAL or UNKNOWN with its legal basis and a verification step, and no legal advice, no refund math, no entry classification.

| Skill | What it does |
|---|---|
| [`skills/us-import-risk-screen`](skills/us-import-risk-screen/SKILL.md) | Screens duty-recovery questions, CBP Form 28/29 notices, AD/CVD exposure and general U.S. import risk from minimal facts; enforces the deadline-safety rules (never "liquidation + 180 days" without a liquidation date; AD/CVD never gets a 1-year projection; contradictory or future dates drive nothing); routes to the free tool, to the CF-28 guide at [plaudeapi.com/trade/cf28](https://plaudeapi.com/trade/cf28/) for a Form 28, to the guide at [plaudeapi.com/trade/ieepa-refund](https://plaudeapi.com/trade/ieepa-refund/) when an IEEPA duty-refund question is raised, to the guide at [plaudeapi.com/trade/foreign-ior](https://plaudeapi.com/trade/foreign-ior/) when the user's own words raise CBP's foreign importer-of-record rule, and, if the user asks, to a conflict-check-first attorney review path. It names the earliest possible court time limit for an IEEPA refund suit as POTENTIAL with its basis and the caveat that accrual is disputed; it never computes a refund. |

The skill is **aligned with production at a recorded baseline** for the invariants listed in its Hard rules (content hashes in `skills/us-import-risk-screen/references/ALIGNMENT.md`; see the `limitation` field there for what that does and does not prove). `conformance/cases.yaml` holds replayable fixtures and `VERIFY.md` the verification protocol; neither is an automated test runner. `evals/` holds the same cases and about twenty trigger tests in the format `claude plugin eval` reads; it is generated from `conformance/` by `scripts/gen_evals.py` and, as of 0.5.0, has been structure-checked but not yet run through that tool. See `CHANGELOG.md` for versions and `SECURITY.md` for how to report a problem or recognise an altered copy of the skill.

## Example prompts

- *We got a CF-29 dated 2026-09-02 on an entry from January. What may matter here?*
- *I paid IEEPA tariffs on my imports in 2025 and I hear refunds are possible. Where do I start figuring out whether this applies to us?*
- *Our company is in Vietnam and we are our own importer of record in the U.S. Does the new CBP rule for foreign importers of record affect us?*

## Install

**Claude Code, by name** — add this repository as a marketplace, then install the plugin:

```bash
claude plugin marketplace add peterzhang12312/plaudeapi-trade-skills
claude plugin install plaudeapi-trade@plaudeapi-trade-skills
```

Release tags are named `plaudeapi-trade--v<version>` (for example `plaudeapi-trade--v0.5.0`; the version is the one in `.claude-plugin/plugin.json`). To pin what you install, clone the repository, check out a tag or a commit the maintainer recorded in `conformance/RUNS.md`, and add that local folder as the marketplace instead (`claude plugin marketplace add ./plaudeapi-trade-skills`).

**Claude Code, as a copied skill** — copy the folder into your project's `.claude/skills/` (or your user-level `~/.claude/skills/`):

```bash
git clone https://github.com/peterzhang12312/plaudeapi-trade-skills.git
git -C plaudeapi-trade-skills checkout <release tag or commit>
cp -r plaudeapi-trade-skills/skills/us-import-risk-screen ~/.claude/skills/
```

**Claude plugin, local trial** — `claude --plugin-dir ./plaudeapi-trade-skills`. The plugin (`.claude-plugin/plugin.json`, name `plaudeapi-trade`, MIT) loads no code, no MCP server and no hook, and collects nothing itself (your AI tool's provider handles what you type there under its own terms). `scripts/gen_evals.py` is a maintainer tool that Claude Code never runs.

**Codex and other agents that read Agent Skills** — the skill is a standard Agent Skills folder (`SKILL.md` with `name` and `description`, optional `references/`); copy `skills/us-import-risk-screen` into `.agents/skills/` (project) or `$HOME/.agents/skills/` (user). `skills/us-import-risk-screen/agents/openai.yaml` is optional display metadata for Codex. For any other framework, load `SKILL.md` as a system instruction or tool description.

Then ask one of the example prompts above.

Wording source for storage and identity statements: the site's own disclosure and the CF-28 guide §9, which say of the **browser-side PlaudeAPI Trade check only** that it "asks for no documents, uploads nothing, and stores nothing on any server"; this README repeats that scope and never widens it — an agent host running this skill may retain your prompts under its own terms.

## Why the rules are strict

Trade deadlines are entry-specific. The most common mistake by tools and people alike is to compute "liquidation + 180 days" from an entry date. The protest clock (19 U.S.C. 1514(c)(3)) runs from the *liquidation* date, which is usually about a year after entry but may be extended or suspended (19 U.S.C. 1504). A screen that projects a confident date it cannot know is worse than no screen. The skill states the deadline-safety rules listed in its Hard rules, which the browser tool at plaudeapi.com/trade also enforces (source of the rules: the `eventscreen` module and its regression checks in the PlaudeAPI codebase), aligned at the baseline recorded in `references/ALIGNMENT.md` (`limitation` field); it is prose, so equivalence is checked by replaying `conformance/cases.yaml` (VERIFY.md), not assumed by construction.

## What this is not

This is a free tool and general information, not legal advice and not customs brokerage. Using it does not create an attorney-client relationship. Its output is a screen, not advice; a person must review it before relying on it.

Not legal advice, not customs brokerage, not classification. Any HTS information is general and for planning; the classification used on a specific entry is determined by the importer's licensed customs broker. If legal services are requested, they are provided only by **Bandi & Associates PLLC**, a New York law firm, after a conflicts check and a separate written engagement; its responsible attorney, Di Ban, Esq. (eclbk_legal@ahs.us.com), also founded and operates PlaudeAPI. PlaudeAPI receives no share of legal fees.

## Licence

MIT for the skill text. Legal authorities cited are public law; verify them before relying on them.
