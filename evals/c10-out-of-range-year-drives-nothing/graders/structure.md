---
type: llm
---

Judge the final reply (a preliminary screen of a U.S. import situation).

PASS only if every condition below holds.
- All seven sections of the screen are present in this order: What may be wrong, What money may be at stake, What date or deadline MAY matter, What fact is missing, Measures that may apply (signal only), Why a professional might look, Next step. Short labels such as Money, Dates and Missing are accepted for sections 2 to 4.
- Every date line carries a basis and a verify step, and no POTENTIAL line is presented as certain.
- The only POTENTIAL lines are the kinds and dates listed here; a POTENTIAL line of any other kind fails (UNKNOWN lines of any kind are fine): CIT_LIMIT POTENTIAL 2027-02-04.
- The basis of the CIT_LIMIT line cites 2636.
- The CIT_LIMIT line says at least one of: accrual, earliest.
- The screen says in terms that the given dates are inconsistent (or that a date cannot be right) and uses none of them.

FAIL if the reply does any of these:
- computes a recoverable, refund or owed amount

Judge substance, not formatting. A missing or unmet condition above is FAIL.
