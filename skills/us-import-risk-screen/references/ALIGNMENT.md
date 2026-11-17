# Currency and production alignment (maintainer reference)

Moved out of SKILL.md in 0.5.0 so the skill body stays small when it is loaded; nothing in this file adds or changes a rule. SKILL.md frontmatter `metadata` carries the same version and review dates (checked by VERIFY.md Tier 1c and 1f), and `CHANGELOG.md` holds the version history that used to sit in the `version:` comment.

What the pin means and does not mean is stated in the `limitation` field below: byte-identical pinned files do not prove behavioural equivalence between the skill prose and the production TypeScript.

```yaml
skill: us-import-risk-screen
version: 0.5.1                            # see CHANGELOG.md for the history; bump on every rule or pin change
last_primary_source_review: 2026-11-16   # 2026-11-16 = alignment review against production (pinned at knowledge-pop 4f8c94d) and the two guide pages, read from their own front matter (verified 2026-11-13 / 2026-11-14); this date records that alignment review only, not a primary-source re-read; the statutes, regulations and the CBP Form 28 instructions under "Key facts" were last read from the primary sources on 2026-09-19 and were not re-read in this pass (the guides' own authority lists carry their 2026-11-13/14 reads)
revalidate_by: 2027-05-15                # ceiling = last_primary_source_review + 180 days; past this date treat the skill as STALE until re-reviewed
revalidate_on_event: any change to a tariff regime, IEEPA/CAPE refund rule, or CBP form referenced here (the site's regime timeline at https://plaudeapi.com/trade/timeline/ is the trigger); an event review supersedes the ceiling
aligned_with_production:                  # "aligned with production at the recorded baseline" -- a content-hash pin, NOT a claim that this prose continuously mirrors the browser code
  repo: knowledge-pop (private)
  commit: 4f8c94dc7f9600930595e9e4ec70e3e89dcedcc8
  compiled_screen_files:                  # the exact file set check-trade-eventscreen.mjs compiles (its tsconfig include list)
    src/trade/eventscreen.ts: 53eba2ad8f401484bd5f53c68e7f20ea70c303a9
    src/trade/campaign.ts: 5401547db1c8090e4e557d4f45ab423fffa4a393
    src/trade/config.ts: 70964f87b7cbd909fef1a8e436f40d482b03176e
    src/trade/windows.ts: de226f3770f25622d4ffd2409c8eab6f95593ccc
    src/trade/firmAppTariff.ts: b545d68d71e22c99530d3bdde7f8ed31df4d6687   # imported by eventscreen.ts: the earliest-possible 28 U.S.C. 2636(i) rule, the 120-day urgency rule, the CAPE 80-day path rule and their wording
  check_scripts:
    scripts/check-trade-eventscreen.mjs: c87e74237885fa16bb969e060aea6cba2f585844
    scripts/check-trade-eventscreen-matrix.mjs: 4ed1d99eb5844092b66883f117c28e6d035b7ee6
  guide:
    content/trade/articles/cf28.md: 5fe7d990929dafca91d6eab676292cb18daf6a2a   # rendered at https://plaudeapi.com/trade/cf28/
    expected_title: "Received a CBP Form 28"  # VERIFY.md Tier 1d checks the live page for this string
    content/trade/articles/ieepa-refund.md: 729e17c8e32dcbe08e7e3b7dec05d68ab12fb4c4   # rendered at https://plaudeapi.com/trade/ieepa-refund/ ; front matter verified 2026-11-14
    content/trade/articles/foreign-ior.md: 9c985646d94e05c7d25049409276e7348b1efa50   # rendered at https://plaudeapi.com/trade/foreign-ior/ ; front matter verified 2026-11-13
  storage_wording_source: "CF-28 guide section 9 / site disclosure: the browser-side check 'asks for no documents, uploads nothing, and stores nothing on any server'"
  runtime_data_bundle:
    public/data/trade/latest.json: d69b2f79cb8b984edd0481026c5db10995a9a518   # as_of 2026-11-10; regime windows come from this bundle, which is NOT covered by the compiled_screen_files hashes -- a new vintage is a revalidate_on_event trigger
  hash_method: committed blob id -- git rev-parse <commit>:<path> in knowledge-pop (equals git hash-object of an LF checkout; a CRLF-converted working copy would hash differently)
  baseline_replay: https://github.com/peterzhang12312/plaudeapi-trade-skills/blob/master/conformance/RUNS.md (run before this pin was written)
  limitation: byte-identical pinned files do not prove behavioural equivalence between this prose and the TypeScript screen; the skill does not continuously mirror the browser code; production enforces checks this prose does not restate; production shows a CF-28 reference date (form date + 30 days, the reply period stated on the form governs) that this skill deliberately does not state; production also counts the days to the CIT LIMIT date from the New York court date and routes an urgent one to the Firm's attorney first, which this skill does not restate (it says only that fewer than 120 days remain, or that the date passed); production marks a RECOVERY PATH line POTENTIAL without a date when a liquidation date is stated, this skill keeps a no-date line UNKNOWN (Output-format rule 3); the conformance fixtures are replayed by a human or model (https://github.com/peterzhang12312/plaudeapi-trade-skills/blob/master/VERIFY.md), not executed
```

## Sources and open questions (moved from SKILL.md Key facts in 0.5.0, text unchanged)

Sources for the dates and citations in SKILL.md: the primary-authority lists of the CF-28 guide (https://plaudeapi.com/trade/cf28/), the IEEPA-refund guide and the foreign-IOR guide, and the site's regime timeline (https://plaudeapi.com/trade/timeline/); the IEEPA start/end dates and the 2636(i) start date are the same constants the browser tool uses.

Two open questions for attorney re-review at the next revalidation (they are questions, not rules of the skill): (a) does the "entries before 2025-02-03" line need a carve-out for warehouse withdrawals or FTZ entries, or does it hold as written? (b) from which event does the 6-month period in 19 U.S.C. 1504(d) run? Until answered, the Key facts in SKILL.md stand as written.
