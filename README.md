# PlaudeAPI Trade — agent skills

Skills that teach an AI coding/chat agent to run a **fail-closed preliminary screen of a U.S. import situation** the way the free tool at **[plaudeapi.com/trade](https://plaudeapi.com/trade)** does: minimal facts in, observations out, every date labelled POTENTIAL or UNKNOWN with its legal basis and a verification step, and no legal advice, no refund math, no entry classification.

| Skill | What it does |
|---|---|
| [`skills/us-import-risk-screen`](skills/us-import-risk-screen/SKILL.md) | Screens duty-recovery questions, CBP Form 28/29 notices, AD/CVD exposure and general U.S. import risk from minimal facts; enforces the deadline-safety rules (never "liquidation + 180 days" without a liquidation date; AD/CVD never gets a 1-year projection; contradictory or future dates drive nothing); routes to the free tool, to the CF-28 guide at [plaudeapi.com/trade/cf28](https://plaudeapi.com/trade/cf28/) for a Form 28, and, if the user asks, to a conflict-check-first attorney review path. |

The skill is **aligned with production at a recorded baseline** (content hashes of the compiled screen files, the check scripts and the guide, in its Metadata block) — it does not continuously mirror the browser code. `conformance/cases.yaml` holds replayable fixtures and `VERIFY.md` the verification protocol; neither is an automated test runner.

## Install

**Claude Code** — copy the folder into your project's `.claude/skills/` (or your user-level `~/.claude/skills/`):

```bash
git clone https://github.com/peterzhang12312/plaudeapi-trade-skills.git
cp -r plaudeapi-trade-skills/skills/us-import-risk-screen ~/.claude/skills/
```

Then ask, for example: *"We got a CF-29 dated 2026-09-02 on an entry from January — what may matter?"*

Other agent frameworks: the skill is a single Markdown file with YAML frontmatter (`name`, `description`); load it as a system instruction or tool description.

Wording source for storage and identity statements: the site's own disclosure and the CF-28 guide §9 ("asks for no documents, uploads nothing, and stores nothing on any server"); this README repeats them and never widens them.

## Why the rules are strict

Trade deadlines are entry-specific. The most common mistake by tools and people alike is to compute "liquidation + 180 days" from an entry date. The protest clock (19 U.S.C. 1514(c)(3)) runs from the *liquidation* date, which is usually about a year after entry but may be extended or suspended (19 U.S.C. 1504). A screen that projects a confident date it cannot know is worse than no screen. The skill states the same fail-closed rules that the browser tool at plaudeapi.com/trade enforces (source of the rules: the `eventscreen` module and its regression checks in the PlaudeAPI codebase), aligned at the baseline recorded in the skill's Metadata block; it is prose, so equivalence is checked by replaying `conformance/cases.yaml` (VERIFY.md), not guaranteed by construction.

## What this is not

Not legal advice, not customs brokerage, not classification. Any HTS information is general and for planning; the classification used on a specific entry is determined by the importer's licensed customs broker. If legal services are requested, they are provided only by **Bandi & Associates PLLC**, a New York law firm, after a conflicts check and a separate written engagement; its responsible attorney, Di Ban, Esq. (eclbk_legal@ahs.us.com), also founded and operates PlaudeAPI. PlaudeAPI receives no share of legal fees.

## Licence

MIT for the skill text. Legal authorities cited are public law; verify them before relying on them.
