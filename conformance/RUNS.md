# Replay log — conformance/cases.yaml (Tier 3 of VERIFY.md)

Append-only. One block per replay. A replay is not a test-suite run: it is a person or a model applying SKILL.md to the fixture inputs, graded by a separate reader against the structured assertions.

## 2026-09-21 — BASELINE replay (before the alignment pin was written) — PASS 8/8
- Skill version replayed: 0.2.0 (the S1 text; rules unchanged from 0.1.0, wording/metadata added)
- Operator: model — `claude-opus-5` via Claude Code subagents; 3 independent fresh contexts (N = 3); sampling: host default (temperature not exposed by the host); each context read SKILL.md and only the fixtures' `inputs` + `as_of_date` (2026-09-21); grading keys withheld from the operator.
- Grader: a separate Claude context (the S1 session) against `expects` / `forbids` / `allows`, not substring matching.
- Result: every structured assertion held in 3/3 runs for all 8 cases (24/24).

| Case | Run 1 | Run 2 | Run 3 | Notes |
|---|---|---|---|---|
| C01_liquidation_date_given | PASS | PASS | PASS | PROTEST WINDOW · POTENTIAL · 2026-08-28, basis 1514(c)(3), verify step present, past-date flag shown; no instruction wording |
| C02_entry_date_only_non_adcvd | PASS | PASS | PASS | LIQUIDATION · POTENTIAL · 2026-06-15, basis 1504(a), "extended … or suspended" caveat; PROTEST WINDOW UNKNOWN |
| C03_no_liquidation_date_no_180 | PASS | PASS | PASS | no 180-day projection; PROTEST WINDOW UNKNOWN; money USER-STATED; no computed amount |
| C04_adcvd_no_one_year | PASS | PASS | PASS | LIQUIDATION UNKNOWN ("may not apply", suspension); scope language, not HTS, controls; no HTS assigned |
| C05_cf28_notice_no_computed_due_date | PASS | PASS | PASS | CF-28 REPLY PERIOD UNKNOWN, "printed on the form", 163.6(a) named, guide URL given; LIQUIDATION · POTENTIAL · 2027-05-20; "30 days" never asserted as a due date |
| C06_contradictory_dates_drive_nothing | PASS | PASS | PASS | inconsistency stated; LIQUIDATION and PROTEST WINDOW both UNKNOWN; correct liquidation date requested |
| C07_pre_ieepa_entry | PASS | PASS | PASS | IEEPA/CAPE stated as not applicable (allowed explanation), no recovery question raised from IEEPA |
| C08_unknown_everything_safe_output | PASS | PASS | PASS | seven headings present; all dates UNKNOWN; the four minimal facts requested; "no entry numbers, invoices or narrative" |

Observations (not failures): runs differ in phrasing and in the "Measures that may apply" detail (e.g., Section 232 derivative-annex remarks); all stayed at "signal only" and none assigned an HTS code or computed an amount. Run 2 wrote the money line as "nothing is labeled USER-STATED or BAND" when neither was given — acceptable under the skill's output format.

Pin written after this replay: see SKILL.md → Metadata → `aligned_with_production` (knowledge-pop commit 5f87b5e9…; blob hashes recorded 2026-09-21).
