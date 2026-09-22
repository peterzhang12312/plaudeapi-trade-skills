# Replay log — conformance/cases.yaml (Tier 3 of VERIFY.md)

Append-only. One block per replay. A replay is not a test-suite run: it is a person or a model applying SKILL.md to the fixture inputs, graded by a separate reader against the structured assertions in the cases.yaml vocabulary block. A passing replay shows that no divergence was observed in the replayed fixtures — nothing more.

## 2026-09-21 — replay of skill text 0.2.0 (8 fixtures C01–C08; superseded by the 0.3.0 entry below) — PASS 8/8
- Historical record kept because this log is append-only. Skill text: version 0.2.0 as committed at 80e042a (SKILL.md blob 40fe629d…; rules unchanged from 0.1.0; wording/metadata added). Fixtures: cases.yaml as committed at 80e042a (blob 1b70a813…), 8 cases. Operator: `claude-opus-5`, three fresh contexts, host-default sampling, keys withheld. Grader: the maintainer's session (the context that wrote the fixtures — recorded as a baseline, not an independent grade). Result: every assertion then defined held in 3/3 runs (24/24). Four of those eight keys were later tightened (C01 past-date flag, C05 forbid list, C06/C08 field names); the outputs were re-graded under the tightened keys in the entry below.

## 2026-09-21 — BASELINE replay for skill version 0.3.0 (21 fixtures; before the alignment pin was written) — PASS 21/21
- Skill text replayed: version 0.3.0 with Hard rules 1–9 (rule 9 added 2026-09-21). The replayed text predates the clarifying edits made after the adversarial review (rule 0 URL allowlist; rule 3 cross-reference to rules 4/5/6/9; rule 9 'name them under What fact is missing'; KIND token list in Output 3; source note under Key facts; https scheme in the worked example). None of these changes a rule's outcome; the shipped SKILL.md blob is b47e3955… and is what the next replay must use.
- Fixtures graded: cases.yaml as of blob 631169c4… (the closed-world POTENTIAL rule, the extra LIQUIDATION expectations for C03/C07/C14–C18, the strict rule-5 suppression for C11/C21 and the instruction-wording exemption were added after the three outputs were produced; the same three outputs were re-graded against this tightened set and still pass 63/63).
- Operator prompt (verbatim): "Read SKILL.md in full. Treat it as the operating instructions you must follow exactly. Read cases.yaml. Do NOT read or use the expects, forbids, or allows sections — they are grading keys. Use only as_of_date and each case's inputs (including any user_message). For EACH of the 21 cases, produce the screen the skill prescribes, using today's date = the file's as_of_date (2026-09-21). Where an input is null/blank, treat it as not provided (ask for it under 'What fact is missing' as the skill directs; do not invent values). Follow the skill's seven headings in order."
- Fixtures: C01–C21 of cases.yaml as committed with this entry (the fixture set was expanded from 8 to 21 on 2026-09-21 after review; the earlier 8-case replay of the 0.2.0 text, also 3/3 on every assertion, is superseded by this entry and is not relied on).
- Operator: model — `claude-opus-5` in three fresh contexts (N = 3), each given only SKILL.md plus the fixtures' `inputs` and `as_of_date` (2026-09-21); grading keys withheld; sampling: host default (temperature not exposed by the host).
- Grader: the maintainer's session (the context that wrote the fixtures and spawned the operators) applying the vocabulary definitions, not substring matching. This satisfies the letter of VERIFY.md Tier 3 but not its independence intent; it is recorded as a BASELINE. The next replay (Run-Q or after any rule change) must be graded by a person or a context that did not write the fixtures.
- Result: every structured assertion held in 3/3 runs for all 21 cases (63/63 case-runs).

| Case | Run 1 | Run 2 | Run 3 | Notes |
|---|---|---|---|---|
| C01_liquidation_date_given | PASS | PASS | PASS | PROTEST WINDOW · POTENTIAL · 2026-08-28, basis 1514(c)(3), verify step, past-date flag |
| C02_entry_date_only_non_adcvd | PASS | PASS | PASS | LIQUIDATION · POTENTIAL · 2026-06-15 (1504; extended/suspended caveat); PROTEST WINDOW UNKNOWN |
| C03_no_liquidation_date_no_180 | PASS | PASS | PASS | no 180-day projection; USER-STATED money; no computed amount |
| C04_adcvd_no_one_year | PASS | PASS | PASS | LIQUIDATION UNKNOWN (suspension); scope language not HTS; no HTS code assigned |
| C05_cf28_notice_no_computed_due_date | PASS | PASS | PASS | printed-period reference; guide URL; LIQUIDATION · POTENTIAL · 2027-05-20; no computed due date |
| C06_contradictory_dates_drive_nothing | PASS | PASS | PASS | inconsistency stated; both dependent dates UNKNOWN; liquidation_date + entry_date requested |
| C07_pre_ieepa_entry | PASS | PASS | PASS | IEEPA question not raised; explanation only |
| C08_unknown_everything_safe_output | PASS | PASS | PASS | seven headings; all dates UNKNOWN; the four intake fields requested; nothing beyond the Minimal-facts table |
| C09_future_entry_date_drives_nothing | PASS | PASS | PASS | future date stated as inconsistent; no LIQUIDATION/PROTEST projection |
| C10_out_of_range_year_drives_nothing | PASS | PASS | PASS | out-of-range stated; nothing projected |
| C11_notice_before_entry_drives_nothing | PASS | PASS | PASS | notice-before-entry stated; no protest projection; notice_date + entry_date requested |
| C12_cf29_notice_protest_still_from_liquidation | PASS | PASS | PASS | PROTEST WINDOW UNKNOWN (1514, from liquidation not notice); LIQUIDATION · POTENTIAL · 2027-01-12 |
| C13_no_us_import_no_entry_timing | PASS | PASS | PASS | "no U.S. entry timing" stated; nothing projected from the stray date |
| C14_user_asks_for_attorney_conflict_check_first | PASS | PASS | PASS | conflict check before facts; no fee/price; no promise to act; https://plaudeapi.com/trade present |
| C15_entry_day_before_ieepa_start | PASS | PASS | PASS | 2025-02-03: IEEPA not raised |
| C16_entry_on_ieepa_start_day | PASS | PASS | PASS | 2025-02-04: IEEPA question raised |
| C17_entry_on_ieepa_end_day_needs_deposit_check | PASS | PASS | PASS | deposit verification requested |
| C18_entry_day_after_ieepa_end | PASS | PASS | PASS | 2026-02-25: IEEPA not raised (verify-deposit caveat allowed) |
| C19_column2_origin | PASS | PASS | PASS | column-2 / GN 3(b) mentioned; LIQUIDATION · POTENTIAL · 2027-06-01; no 8/10-digit HTS |
| C20_cf_family_without_notice_drives_nothing | PASS | PASS | PASS | Hard rule 9: nothing projected; cbp_notice + notice_date requested first |
| C21_future_notice_date_not_potential | PASS | PASS | PASS | future notice date stated as inconsistent; no CF-28 due date, no protest projection |

Observations (not failures): run 2 wrote the money line as "nothing is labeled USER-STATED or BAND" where neither was given (C02/C04 etc.) — no fixture asserts a label there, but Output 2 makes the label mandatory; the next replay should add `money_label: BAND` to cases with a volume band and treat the unlabeled form as a deviation. Run 3 used the worked example's short labels (**Money. / Dates. / Missing.**) for three headings while keeping all seven sections in order — the `headings_all_present` definition now says the short labels are accepted and the worked example is marked abridged. Runs differ in the "Measures that may apply" detail (e.g. Section 232 derivative remarks, sanctions notes on RU origin); all stayed at signal level and none assigned an HTS code, computed an amount, quoted a fee or stated a deadline for the user.

Pin written after this replay: see SKILL.md → Metadata → `aligned_with_production` (the commit recorded there; blob hashes recorded 2026-09-21).
