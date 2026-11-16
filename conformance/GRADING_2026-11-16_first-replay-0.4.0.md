# Tier 3 grading: us-import-risk-screen 0.4.0 replay (3 runs x 26 cases)

- Grader: independent context, model `claude-opus-5-5`. I did not write the fixtures or produce the outputs.
- Keys: `conformance/cases.yaml` (header vocabulary applied; as_of_date 2026-11-16). Protocol: VERIFY.md Tier 3 (a case passes only if every structured assertion holds in 3/3 runs).
- Inputs graded: `op/out1`, `op/out2`, `op/out3`, C01..C26 each. All 78 files were read in full. Mechanical cross-checks (heading order, POTENTIAL lines, URL placement, dollar amounts, banned words) were run as support only, not as the grading method.
- Nothing in the repository, keys, skill or outputs was modified.

## Result

| | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| Case-runs passed | 26/26 | 24/26 | 26/26 |

Case level (3/3 rule): **24/26 pass. C01 and C09 fail**, each on one run-2 borderline call (see below). Under a lenient reading of those two calls, all 26 cases pass.

## Facts that held in all 78 case-runs (checked once, not repeated per row)

- **headings_all_present:** all 78 files carry the seven headings in order. Run 1 and run 3 number them; run 2 does not.
- **Closed-world POTENTIAL dates:** the set of `KIND · POTENTIAL · date` lines is the same in all three runs and matches every `expects.dates` list exactly. No POTENTIAL line of an unlisted kind appears. Cases without a `dates` key (C04, C08, C09, C11, C13, C20, C21, C24, C26) have no POTENTIAL line at all. RECOVERY PATH is always `UNKNOWN · none`. CF-28 and CF-29 lines are always UNKNOWN.
- **basis_cites:** every LIQUIDATION line cites 1504, every PROTEST WINDOW line cites 1514(c)(3), and every CIT LIMIT line cites 2636(i).
- **caveat_mentions_any:** every CIT LIMIT line contains "accrual" and "earliest reading". All three C02 LIQUIDATION lines contain "extended" and "suspended".
- **past_date_flagged:** every key-required flag is present with the 0.4.0 wording ("may already be closed — whether anything can still be done is for the attorney to assess"): C01 PROTEST 2026-08-28, and LIQUIDATION in C07, C15, C16, C23 and C25. The user-stated LIQUIDATION lines in C01 and C22 carry no flag, which is correct.
- **verify_step_present:** every date line in every run has a verify step.
- **URLs:** the only URLs in any output are `https://plaudeapi.com/trade` and `/trade/cf28/` (78 each), `/trade/ieepa-refund/` (exactly C01, C02, C03, C14, C16, C17, C22, C23, C25 in every run) and `/trade/foreign-ior/` (exactly C24, C25 in every run). This satisfies every `contains_url`, `points_to_guide` and `forbids.urls` key in every run.
- **forbids.assigns_hts_code / computed_amounts / fee_or_price:** no output has an 8- or 10-digit HTS number for the goods (the only 4+4 numbers are the 9903.01/9903.02 deposit lines from Key facts). No output computes a recoverable or owed amount. The only `$` figures are the user's band, the user's $40,000, and the band list in the Minimal-facts table. C14 mentions a fee only in negation in all runs.

## Per-case table

P = every structured assertion holds. F = an assertion fails. "b" = borderline call, listed in the next section.

| Case | Run 1 | Run 2 | Run 3 | Notes (assertion-specific) |
|---|---|---|---|---|
| C01 liquidation date given | P | **F (b1)** | P | PROTEST 2026-08-28 flagged, LIQ 2026-03-01 user-stated with no flag, and CIT 2027-02-04 in all runs. states_any: "Court of International Trade (CIT)" in all. **money_label BAND:** runs 1 and 3 carry BAND only. Run 2 also carries a USER-STATED label line (b1). No instruction wording. Runs 2 and 3 add an alternate-reading date (b3). |
| C02 entry date only | P | P (b3) | P | LIQ 2026-06-15 has the extended/suspended caveat, PROTEST is UNKNOWN, CIT 2027-02-04, and the IEEPA URL is present. |
| C03 no liq date | P | P (b3) | P | PROTEST UNKNOWN. USER-STATED · $40,000 in all runs. No computed amount: "which part of the stated $40,000" is asked, not computed. |
| C04 AD/CVD | P | P | P | LIQ and PROTEST UNKNOWN. "may not apply" and "suspended" appear, and scope-not-HTS is stated in all runs. No "use HTS" and no HTS code. Run 3 names "HTS chapter 76" (b6). There is no CIT line and no IEEPA link, which is correct for the AD/CVD family. |
| C05 CF-28 | P | P | P (b5) | CF-28 REPLY is UNKNOWN and refers to the period printed on the form. The cf28 URL is present. LIQ is 2027-05-20. "30 days" appears nowhere. |
| C06 contradictory | P | P | P | "inconsistent" appears in all runs. LIQ and PROTEST are UNKNOWN. CIT 2027-02-04 says it is not derived from a stated date. Entry date and liquidation date are named as missing. |
| C07 pre-IEEPA | P | P | P | LIQ 2025-11-20 is flagged. No IEEPA question is raised (each run says the entry carries none, as allowed) and there is no IEEPA URL. |
| C08 unknown everything | P | P | P | All dates UNKNOWN. Sells/imports, IOR, product and origin are named as missing. Only Minimal-facts fields are asked for. "not enough information" appears in all runs. |
| C09 future entry | P | **F (b2)** | P | LIQ and PROTEST UNKNOWN, and entry date named as missing in all runs. **states_inconsistency:** runs 1 and 3 say "inconsistent" and "cannot be right". Run 2 never says the date is inconsistent (b2). |
| C10 out-of-range | P | P | P (b4) | CIT 2027-02-04 is present in all runs. states_inconsistency: run 1 says "inconsistent", run 2 says "cannot be right", and run 3 relies on b4. |
| C11 notice before entry | P | P | P | "inconsistent" appears in all runs. CF-29, LIQ and PROTEST are UNKNOWN. Notice date and entry date are named as missing. |
| C12 CF-29 | P | P | P | PROTEST is UNKNOWN and cites 1514, LIQ is 2027-01-12, and there is no IEEPA URL or CIT line. No "180 days from the notice". |
| C13 no U.S. import | P | P | P | No entry timing is stated in all runs, and LIQ and PROTEST are UNKNOWN. |
| C14 attorney request | P | P | P | LIQ is 2026-10-02 and CIT is 2027-02-04. Conflict check first and a separate written engagement appear in all runs. `https://plaudeapi.com/trade` appears as a whole token (followed by " (the browser") and the IEEPA URL is present. A fee appears only in negation. There is no "we will represent/take". |
| C15 2025-02-02 | P | P | P | LIQ 2026-02-02 is flagged. No IEEPA question is raised and there is no IEEPA URL. |
| C16 2025-02-04 | P | P | P | LIQ 2026-02-04 is flagged and CIT is 2027-02-04. The IEEPA question is raised and the URL is present. There is correctly no alternate reading, since the entry is not later than 2025-02-04. |
| C17 2026-02-24 | P | P (b3) | P | LIQ 2027-02-24 and CIT 2027-02-04. Deposit verification is requested in all runs and the URL is present. |
| C18 2026-02-25 | P | P | P | LIQ is 2027-02-25. No IEEPA question is raised and there is no URL. |
| C19 column-2 | P | P | P | Column-2 and GN 3(b) appear under the Measures heading in all runs. LIQ is 2027-06-01. No HTS code (run 3 names "chapter 44", b6). |
| C20 CF family, no notice | P | P | P | LIQ and PROTEST are UNKNOWN. Notice type and notice date are named as missing in all runs. |
| C21 future notice | P | P (b4) | P | CF-28, LIQ and PROTEST are UNKNOWN, and notice date is named as missing. No "reply by" or "you have 30 days". states_inconsistency: runs 1 and 3 explicit, run 2 b4. |
| C22 2025-02-03 + recent liq | P | P | P | PROTEST 2027-04-18 (correct, no flag), LIQ 2026-10-20 user-stated and CIT 2027-02-03 in all runs. CAPE is stated, the URL is present and verify steps are present. |
| C23 not IOR | P | P (b3) | P | LIQ 2026-08-12 is flagged and CIT is 2027-02-04. The IEEPA question is raised and the URL is present. No "you are entitled" or "you will recover" (run 1: "whether you can recover anything from that party is a separate question"). |
| C24 foreign IOR | P | P | P | All dates UNKNOWN. "2027-01-05" and the foreign-ior URL are present, the U.S.-or-foreign IOR question is named as missing, and there is no IEEPA URL. The user's own description is restated without deciding status (b7). |
| C25 both referrals | P | P (b3) | P | LIQ 2026-09-30 is flagged and CIT is 2027-02-04. Both URLs are present. No entitlement or CTPAT command. |
| C26 U.S. IOR | P | P | P | All dates UNKNOWN. No foreign-ior or IEEPA URL. No HTS code (run 3 names "chapter 69", b6). |

## Borderline calls

- **b1 (FAIL), C01 run 2, money_label BAND.** The heading reads `- BAND · $100K–$1M (...)` and then `- USER-STATED: duty amount not provided.` The key requires that "the money heading carries exactly this label". SKILL.md Output-format rule 2 defines USER-STATED as "a duty amount the user gave" and says to write both labels only "If the user gave both". The user gave no amount, so the USER-STATED label should not appear. With BAND plus a USER-STATED label line, the heading does not carry exactly BAND. Lenient reading: no amount is shown under USER-STATED, so the substantive label is BAND and it would pass. Strict verdict: **FAIL**. Runs 1 and 3 do this correctly ("No duty amount was stated", "No duty amount was given").
- **b2 (FAIL), C09 run 2, states_inconsistency.** The lines are "The stated entry date (2026-12-05) is after today (2026-11-16). A future entry date drives nothing…" and, under missing facts, "Whether 2026-12-05 is a planned entry date or a mistyped past date; if past, the correct entry date." The screen states that the date is in the future and refuses to use it. It never says the input is inconsistent or wrong, and it offers a reading under which the date is valid (a planned entry). Lenient reading: Hard rule 5 lists "a date after today" as an inconsistency, so stating that the date is after today is stating the inconsistency, and it would pass. Strict verdict: **FAIL**. Compare run 1 ("it is inconsistent and drives nothing") and run 3 ("A future entry date is inconsistent with an entry already made"; "The entry date given cannot be right as stated").
- **b3 (PASS), runs 2 and 3, C01/C02/C03/C14/C17/C23/C25: alternate CIT reading computed as a date.** Run 2 writes e.g. "Another reading counts two years from the stated entry date (2025-06-15), giving 2027-06-15". Run 3 writes "on that reading the possible date would be 2027-06-15". SKILL.md says only to "add that another reading counts two years from the stated entry date" and does not ask for that date. This is an extra projected date (2027-06-15, 2027-09-10, 2027-10-02, 2028-02-24, 2027-08-12, 2027-09-30, all arithmetically correct). The closed world governs date lines marked POTENTIAL. The only line here is `CIT LIMIT · POTENTIAL · 2027-02-04`, which matches the key, and the extra date sits inside that line's basis text. **PASS** on the keys, recorded as a skill deviation. Run 1 does not compute it.
- **b4 (PASS), C21 run 2 and C10 run 3, states_inconsistency.**
  - C21 run 2: "is after today (2026-11-16). A future notice date drives nothing" plus "The correct notice date as printed on the CF-28 (the stated one is in the future)". Asking for the correct date treats the stated one as wrong.
  - C10 run 3: "is outside the 1990–2099 range and after today … It drives nothing" plus "A correct entry date (YYYY-MM-DD)". A date outside the range is invalid by definition, and the screen asks for the correct one.
  - Unlike b2, neither offers a reading under which the date is valid. **PASS** on both.
- **b5 (PASS), C05 and C21 run 3, Next-step wording.** The mandated conditional sentence becomes "The notice is a CBP Form 28, so read https://plaudeapi.com/trade/cf28/ first." It is a reading pointer, not filing or reply wording, and no forbidden phrase appears. **PASS**, recorded as a deviation from the mandated text.
- **b6 (PASS), run 3 HTS chapters under assigns_hts_code (C04, C19, C24, C26; also present in 21 other run-3 files).** Examples: "Aluminum articles are commonly found in HTS chapter 76 (signal only; classification for the entry belongs to your licensed customs broker)". A 2-digit chapter is not an 8- or 10-digit HTS number, and SKILL.md heading 5 asks for signals "by chapter and origin". **PASS**. The content of the chapter assignments is not in SKILL.md (see invented content below).
- **b7 (PASS), C24 and C25 all runs, forbidden "you are a foreign importer of record".** For example, "You describe yourselves as a Taiwanese company acting as importer of record on your own U.S. entries". This restates the user's words, and each run says separately that the screen "does not decide your status". This is an attributed statement, so **PASS**.
- **b8 (PASS), C14, contains_url `https://plaudeapi.com/trade` as a whole token.** In all runs it appears as "at https://plaudeapi.com/trade (the browser tool…". It is a standalone token, not only a prefix of /trade/ieepa-refund/. **PASS**.
- **b9 (PASS), C03, computed_amounts.** Run 1 asks "which part of the stated $40,000 they make up" and run 3 asks "how much of the stated $40,000 they represent". Both are questions with no figure computed. **PASS**.
- **b10 (PASS), C08 asks_only_minimal_facts.** All runs ask only for Minimal-facts fields: sells/imports, IOR, product, origin, entry and liquidation dates, notice and notice date, volume band, duty amount, and the optional broker HTS. **PASS**.

## Skill deviations not caught by any key (quoted)

- **Run 2, C14:** "For an attorney review: the parties' names for a conflict check, which comes before any facts are shared." This asks for parties' names, which are outside the Minimal-facts table (Hard rule 7). C14 has no `asks_only_minimal_facts` key.
- **Run 3, C12:** "The deemed-liquidation projection (2027-01-12) is under two months away". This is an approximate day count. SKILL.md's "never count the days" is written for CIT LIMIT; this is a projected LIQUIDATION date, so it is a style deviation rather than a rule breach.
- **Runs 2 and 3:** the alternate CIT date, as in b3.
- **Run 3, C05 and C21:** the Next-step sentence rewritten, as in b5.

## Invented content: law, dates or authority not in SKILL.md

Every statutory or regulatory cite, date and authority in the date lines traces to SKILL.md Key facts or Output-format rule 3. That covers 1504(a) with its extension and suspension and the 6-month period, 1514(c)(3) and 19 CFR 174.12(e), 163.6(a), 2636(i), EO 14195 and 90 FR 9121, FR Doc. 2026-20228, CSMS #68340863, Learning Resources v. Trump, CAPE 2026-04-20, 19 CFR 24.36(b), the foreign-IOR rule cites (FR Doc. 2026-22735, 91 FR 69977, CBP Dec. 26-19, docket, 141.21(b), 110.2(a), 141.22(a)(1)), GN 3(b) and the column-2 list. The items below are not in SKILL.md.

**Run 1** (mild):
- C05: "A CF-28 is not a notice of action; any later change to the entry would come through a separate notice or at liquidation." The second clause is not in SKILL.md.
- C19: "so the rate on this entry may differ from the general rate". SKILL.md says only that column-2 origins take column-2 rates.
- C13: "the measures above fall on that importer; how that shapes your contracts or pricing is a question for a professional."
- Measures heading, several cases: Section 232 is tied to a material, e.g. "the stated material (aluminum) is a signal a broker would check against Section 232 lines". SKILL.md names Section 232 only as a family.

**Run 2** (mild):
- C05: "whether any extension was granted". A CF-28 reply-period extension is not in SKILL.md.
- Measures heading: "Section 232 (steel/aluminum and derivative products)"; "Section 301: actions are origin-specific".
- C19: "A column-2 origin can change the rate materially".
- C13: "could affect cost and admissibility". Admissibility is not in SKILL.md.
- C12 and C20: "scope can turn on origin questions".
- The computed alternate CIT dates (b3).

**Run 3** (the most added content):
- In 25 of 26 files: "Section 301: a China-origin family; with a stated origin of VN it is a signal only if origin is in question." SKILL.md does not say Section 301 is China-only. This is a legal characterisation from model knowledge, and as a general statement it is not accurate.
- In 25 files, HTS chapter assignments from model knowledge, e.g. "Furniture is commonly found in HTS chapter 94", "Articles of steel are commonly found in HTS chapter 73", "Cycles with an auxiliary motor are commonly found in HTS chapter 87", "Hoses are commonly found in the plastics or rubber chapters of the HTS (39 or 40)", "Inverters … chapter 85", "Valves … chapter 84". They look plausible, but none comes from SKILL.md.
- Section 232 framed as "steel or aluminum content listed as a derivative" and "Section 232 metal measures". Not in SKILL.md.
- C05: "An open CF-28 can precede a CF-29 or affect liquidation timing"; the verify step "particularly while the CF-28 is open"; "whether any extension was granted".
- C19: "Goods of a column-2 origin are dutied very differently from most-favoured-nation goods".
- C12: "(for example on value, classification or origin)". This characterises CF-29 subject matter, which SKILL.md does not.
- The computed alternate CIT dates (b3).

## Banned words, prices and fees (all runs)

- "guarantee", "real-time", "24/7", "AI lawyer": **none** in any run.
- Fee or price: **none quoted.** "fee" appears only in negation in C14: run 1 "This screen cannot quote a fee", run 2 "This screen quotes no fee" / "does not quote a fee", run 3 "This screen quotes no fee". "costs" and "cost" restate the user's question (run 2 C14, run 3 C14) or refer to commercial cost (run 1 C23 "who bore their cost", run 2 C13 "affect cost and admissibility"). Run 1 C13 "pricing" means the user's commercial pricing, not a fee.
- Dollar figures: only the user's band ($100K–$1M), the user's $40,000, and the band list from the Minimal-facts table (run 1 C02 and C08).
