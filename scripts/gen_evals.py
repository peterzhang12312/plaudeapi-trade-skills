#!/usr/bin/env python3
"""Generate evals/ (the `claude plugin eval` case format) from conformance/cases.yaml and conformance/triggers.yaml.

Maintainer tool. Not called by any hook, plugin component or CI. Needs Python 3 and PyYAML (maintainer machine only;
the plugin itself bundles no code). The two YAML files stay the single source of truth; evals/ is generated output.

  python scripts/gen_evals.py           write evals/
  python scripts/gen_evals.py --check   exit 1 if evals/ differs from what would be written

Output is deterministic: sorted, LF line endings, no timestamps.
Writing these files runs nothing and costs nothing. Running them (`claude plugin eval .`) calls a model and does.
"""
import re, sys, pathlib, shutil

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required to run this maintainer tool (python -m pip install pyyaml); nothing was written.")

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL = "us-import-risk-screen"
FIELDS = [  # SKILL.md "Minimal facts to ask for", in table order: (input key, label)
    ("issue_family", "Issue family"),
    ("sells_or_imports_into_us", "Sells or imports into the U.S."),
    ("importer_of_record", "Importer of record"),
    ("annual_us_import_volume", "Annual U.S. import volume"),
    ("product", "Product"),
    ("country_of_origin", "Country of origin"),
    ("hts_code_previously_used", "HTS code previously used by the broker"),
    ("entry_date", "Entry date"),
    ("liquidation_date", "Liquidation date"),
    ("cbp_notice", "CBP notice"),
    ("notice_date", "Notice date"),
    ("duty_amount_at_stake", "Duty amount at stake"),
]
KIND_RE = {  # kind token in cases.yaml -> regex fragment tolerant of space / underscore / hyphen
    "LIQUIDATION": "LIQUIDATION", "PROTEST_WINDOW": "PROTEST[ _-]WINDOW", "CF28_REPLY_PERIOD": "CF-?28[ _-]REPLY[ _-]PERIOD",
    "CF29_RESPONSE": "CF-?29[ _-]RESPONSE", "RECOVERY_PATH": "RECOVERY[ _-]PATH", "CIT_LIMIT": "CIT[ _-]LIMIT",
}
ANY_KIND = "(?:" + "|".join(KIND_RE.values()) + ")"
GAP = r"[^\n]{0,24}?"
HTS = r"\b(?!9903)\d{4}\.\d{2}(?:\.\d{2,4})?\b|\b(?!9903)\d{10}\b|\b(?!9903)\d{8}\b"
FEE = (r"\$\s?\d[\d,.]*\s*(?:flat|fixed|fee|retainer|per hour|/h\b|/hour)|(?:fee|price|retainer|charge|rate)s?\s*(?:of|is|are|:)\s*\$"
       r"|\bhourly\b|we will represent you|we will take your case")
# any URL that is not one of the five allowed pages (SKILL.md Hard rule 0)
URL_ALLOWLIST_BREACH = (r"https?://(?!plaudeapi\.com/)\S+"
                        r"|https?://plaudeapi\.com/(?!trade(?:[/\s)\].,;:*]|$))\S*"
                        r"|https?://plaudeapi\.com/trade/(?=[\w-])(?!(?:cf28|timeline|ieepa-refund|foreign-ior)(?:[^\w-]|$))")
SKILL_INPUT_MATCH = r'"skill"\s*:\s*"(?:[\w-]+:)?' + SKILL + '"'


def q(s):  # YAML single-quoted scalar
    return "'" + str(s).replace("'", "''") + "'"


def fm(**kw):
    return "---\n" + "".join(f"{k}: {v}\n" for k, v in kw.items()) + "---\n"


def regex_grader(pattern, flags="", match=None):
    d = {"type": "regex", "pattern": q(pattern)}
    if flags:
        d["flags"] = flags
    if match:
        d["match"] = match
    return fm(**d)


def skill_fired():
    return fm(type="tool_used", tool="Skill", input_match=q(SKILL_INPUT_MATCH))


def prompt_for(case, as_of):
    inp = case["inputs"]
    out = []
    if inp.get("user_message"):
        out += [inp["user_message"], ""]
    out += [f"Please screen this U.S. import situation. Treat today's date as {as_of}. These are the facts I have:", ""]
    for key, label in FIELDS:
        v = inp.get(key)
        v = "not provided" if v is None or str(v).strip() == "" else str(v)
        out.append(f"- {label}: {v}")
    return "\n".join(out) + "\n"


def esc(x):  # re.escape, minus the escapes of space and hyphen (harmless in JS, invalid under the u flag)
    return re.escape(x).replace(r"\-", "-").replace(r"\ ", " ")


def slug(k):
    return k.lower().replace("_", "-")


def case_graders(case):
    ex, fb, al = case.get("expects", {}), case.get("forbids", {}), case.get("allows", {})
    g = {"skill-fired.md": skill_fired(),
         "urls-allowlist.md": regex_grader(URL_ALLOWLIST_BREACH, match="not_contains")}
    for d in ex.get("dates", []):  # required POTENTIAL lines: exact kind and date
        if d["status"] == "POTENTIAL":
            g[f"date-{slug(d['kind'])}.md"] = regex_grader(KIND_RE[d["kind"]] + GAP + "POTENTIAL" + GAP + esc(d["date"]))
    for k in ex.get("no_projection_of", []):
        g[f"no-potential-{slug(k)}.md"] = regex_grader(KIND_RE[k] + GAP + "POTENTIAL", match="not_contains")
    if ex.get("all_dates_unknown_or_none"):
        g["no-potential-any.md"] = regex_grader(ANY_KIND + GAP + "POTENTIAL", match="not_contains")
    urls = ex.get("contains_url") or ([ex["points_to_guide"]] if ex.get("points_to_guide") else [])
    if isinstance(urls, str):
        urls = [urls]
    for u in urls:
        g[f"has-url-{u.rstrip('/').rsplit('/', 1)[-1]}.md"] = regex_grader(esc(u.rstrip("/")) + r"(?![\w-])(?!/[\w-])")
    for u in fb.get("urls", []):
        g[f"no-url-{u.rstrip('/').rsplit('/', 1)[-1]}.md"] = regex_grader(esc(u.replace("https://", "").rstrip("/")), match="not_contains")
    if ex.get("states_any"):
        g["states-any.md"] = regex_grader("|".join(esc(x) for x in ex["states_any"]), flags="i")
    if ex.get("money_label") == "BAND":
        g["money-band.md"] = regex_grader(r"BAND\s*·")
        g["money-no-user-stated.md"] = regex_grader("USER-STATED", match="not_contains")
    elif ex.get("money_label") == "USER-STATED":
        g["money-user-stated.md"] = regex_grader("USER-STATED")
    if fb.get("assigns_hts_code"):
        g["no-hts-code.md"] = regex_grader(HTS, match="not_contains")
    if fb.get("fee_or_price"):
        g["no-fee-or-price.md"] = regex_grader(FEE, flags="i", match="not_contains")

    # everything a regex cannot judge: one rubric with explicit PASS / FAIL conditions
    must, never = [], []
    must.append("All seven sections of the screen are present in this order: What may be wrong, What money may be at stake, What date or deadline MAY matter, What fact is missing, Measures that may apply (signal only), Why a professional might look, Next step. Short labels such as Money, Dates and Missing are accepted for sections 2 to 4.")
    if ex.get("verify_step_present") or ex.get("dates"):
        must.append("Every date line carries a basis and a verify step, and no POTENTIAL line is presented as certain.")
    if ex.get("dates"):
        must.append("The only POTENTIAL lines are the kinds and dates listed here; a POTENTIAL line of any other kind fails (UNKNOWN lines of any kind are fine): "
                    + "; ".join(f"{d['kind']} {d['status']} {d['date'] or 'no date'}" for d in ex["dates"]) + ".")
        for d in ex["dates"]:
            if d.get("basis_cites"):
                must.append(f"The basis of the {d['kind']} line cites " + " and ".join(d["basis_cites"]) + ".")
            if d.get("caveat_mentions_any"):
                must.append(f"The {d['kind']} line says at least one of: " + ", ".join(d["caveat_mentions_any"]) + ".")
            if d.get("past_date_flagged"):
                must.append(f"The {d['kind']} line carries the past-date flag: the date lies before the stated today, and the line says it may already be closed (for CIT LIMIT: that the date has passed) and that whether anything can still be done is for the attorney to assess.")
    if ex.get("states_inconsistency"):
        must.append("The screen says in terms that the given dates are inconsistent (or that a date cannot be right) and uses none of them.")
    if ex.get("scope_not_hts"):
        must.append("It says the order's written scope language, not the HTS number, controls AD/CVD coverage.")
    if ex.get("refers_to_form_printed_period"):
        must.append("It describes the CF-28 reply period as the one printed on the form and computes no due date.")
    if "ieepa_recovery_question_raised" in ex:
        must.append("It raises an IEEPA/CAPE duty-recovery question for this entry." if ex["ieepa_recovery_question_raised"]
                    else "It raises no IEEPA/CAPE duty-recovery question for this entry (it may mention IEEPA or CAPE only to explain that they do not apply to this entry date).")
    if ex.get("ieepa_deposit_verification_requested"):
        must.append("It asks to verify which duties were actually deposited on this entry.")
    if ex.get("missing_facts_named"):
        must.append("Under What fact is missing it names these facts, in any wording: " + ", ".join(ex["missing_facts_named"]) + ".")
    if ex.get("asks_only_minimal_facts"):
        must.append("It asks only for facts from the minimal-facts table (no entry numbers, invoices or narrative).")
    if ex.get("no_entry_timing"):
        must.append("It says that without a U.S. sale or import there is no U.S. entry timing.")
    if ex.get("conflict_check_first"):
        must.append("It says a conflict check on the parties' names must happen before any facts are shared and that representation starts only under a separate written engagement.")
    if ex.get("column2_mentioned"):
        must.append("The measures section mentions column-2 rates (General Note 3(b)) for the origin.")
    if ex.get("money_label"):
        must.append(f"The money section carries the label {ex['money_label']} and computes no recoverable amount.")
    if al.get("mentions"):
        must.append("It may use these terms only while explaining that they do not apply: " + ", ".join(al["mentions"]) + ".")
    if fb.get("computed_amounts"):
        never.append("computes a recoverable, refund or owed amount")
    if fb.get("instruction_wording"):
        never.append("tells the user what or when to file or reply, in these words or a clear equivalent: "
                     + "; ".join(f'"{x}"' for x in fb["instruction_wording"])
                     + " (exempt: the mandated sentence that a date may already be closed and whether anything can still be done is for the attorney to assess, the Next-step sentences, and the same words inside a negation or attributed to the form or a guide)")
    lines = ["Judge the final reply (a preliminary screen of a U.S. import situation).", "", "PASS only if every condition below holds."]
    lines += [f"- {m}" for m in must]
    if never:
        lines += ["", "FAIL if the reply does any of these:"] + [f"- {n}" for n in never]
    lines += ["", "Judge substance, not formatting. A missing or unmet condition above is FAIL."]
    g["structure.md"] = fm(type="llm") + "\n" + "\n".join(lines) + "\n"
    return g


def build():
    cases = yaml.safe_load((ROOT / "conformance/cases.yaml").read_text(encoding="utf-8"))
    trig = yaml.safe_load((ROOT / "conformance/triggers.yaml").read_text(encoding="utf-8"))
    files = {}
    for c in cases["cases"]:
        name = c["id"].lower().replace("_", "-")
        files[f"evals/{name}/prompt.md"] = (
            fm(name=name, description=q(c["invariant"]), runs=3, max_turns=6, allowed_tools="[Skill]", tags="[conformance]",
               expected_outcome=q("see graders; the keys come from conformance/cases.yaml")) + "\n" + prompt_for(c, cases["as_of_date"]))
        for fn, body in case_graders(c).items():
            files[f"evals/{name}/graders/{fn}"] = body
    for key, tag in (("should_trigger", "should"), ("near_miss", "nearmiss")):
        for item in trig[key]:
            nm = f"trigger-{tag}-{item['id']}"
            files[f"evals/{nm}/prompt.md"] = fm(name=nm, runs=3, max_turns=6, allowed_tools="[Skill]", tags=f"[trigger, {tag}]") + "\n" + item["prompt"].strip() + "\n"
            if tag == "should":
                files[f"evals/{nm}/graders/skill-fired.md"] = skill_fired()
            else:  # min 0 / max 0 = the skill must not be invoked; arm: both scores it in the no-plugin arm too
                files[f"evals/{nm}/graders/skill-not-fired.md"] = fm(type="tool_used", tool="Skill", input_match=q(SKILL_INPUT_MATCH), min=0, max=0, arm="both")
    return files


def main():
    files = build()
    if "--check" in sys.argv:
        bad = []
        d = ROOT / "evals"
        on_disk = {p.relative_to(ROOT).as_posix() for p in d.rglob("*") if p.is_file()} if d.exists() else set()
        for k, v in files.items():
            f = ROOT / k
            if not f.exists() or f.read_bytes().replace(b"\r\n", b"\n") != v.encode("utf-8"):
                bad.append(k)
        bad += sorted(on_disk - set(files))
        print("\n".join(bad) or f"evals match ({len(files)} files)")
        sys.exit(1 if bad else 0)
    d = ROOT / "evals"
    if d.exists():
        shutil.rmtree(d)
    for k, v in files.items():
        f = ROOT / k
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(v.encode("utf-8"))
    print(f"wrote {len(files)} files under evals/")


if __name__ == "__main__":
    main()
