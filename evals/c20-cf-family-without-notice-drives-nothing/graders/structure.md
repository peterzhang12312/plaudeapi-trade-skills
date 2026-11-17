---
type: llm
---

Judge the final reply (a preliminary screen of a U.S. import situation).

PASS only if every condition below holds.
- All seven sections of the screen are present in this order: What may be wrong, What money may be at stake, What date or deadline MAY matter, What fact is missing, Measures that may apply (signal only), Why a professional might look, Next step. Short labels such as Money, Dates and Missing are accepted for sections 2 to 4.
- Under What fact is missing it names these facts, in any wording: cbp_notice, notice_date.

FAIL if the reply does any of these:
- tells the user what or when to file or reply, in these words or a clear equivalent: "file a protest by" (exempt: the mandated sentence that a date may already be closed and whether anything can still be done is for the attorney to assess, the Next-step sentences, and the same words inside a negation or attributed to the form or a guide)

Judge substance, not formatting. A missing or unmet condition above is FAIL.
