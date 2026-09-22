# VERIFY — how this repository is checked (S1, 2026-09-21)

This repository contains a prose skill and replayable fixtures. **There is no test runner, no CI, no dependency and no runtime in this repository, and nothing here detects drift automatically.** Verification is four distinct activities; a report must say which of them were performed.

| Tier | What it proves | Who / how | Automatic? |
|---|---|---|---|
| 1. Static metadata checks | the skill's own metadata is well-formed and not expired | shell commands below | no (commands are run by a person or an agent) |
| 2. Source / alignment-pin verification | the production files the skill was aligned against are byte-identical to the pinned baseline | `git hash-object` in the private `knowledge-pop` working tree (founder / maintainer only) | no |
| 3. Human / model replay of `conformance/cases.yaml` | the prose, when followed, still produces the expected screens | a person, or a model applying SKILL.md, N = 3 independent runs | no |
| 4. Run-Q revalidation (every ≤ 90 days, or on a trigger event) | law, guide and production are still what the skill says | founder + attorney review of primary sources; re-pin; re-replay | no |

A pin that matches proves nothing about behaviour; a replay that passes proves nothing about law currency. Report each tier separately.

## Tier 1 — static metadata checks
Run from the repository root.
```bash
# 1a. wording: no unqualified storage claim anywhere in the repo
python - <<'EOF'
import re, pathlib, sys
bad = []
for f in [pathlib.Path('README.md'), *pathlib.Path('skills').rglob('*.md')]:
    for i, line in enumerate(f.read_text(encoding='utf-8').splitlines(), 1):
        if re.search(r'stores nothing(?! on any server)|nothing is stored', line, re.I):
            bad.append(f'{f}:{i}: {line.strip()[:100]}')
print('
'.join(bad) or '1a clean'); sys.exit(1 if bad else 0)
EOF
# 1b. no price, no unsupported credential wording, no 'mirrors production'
grep -rniE "\\\$[0-9]|specialist|expert in|mirrors production" README.md skills/ conformance/ ; echo "exit $? (1 = clean)"
# 1c. metadata dates parse and the skill is not expired
python - <<'EOF'
import re, datetime as d, sys
s = open('skills/us-import-risk-screen/SKILL.md', encoding='utf-8').read()
rev = d.date.fromisoformat(re.search(r'last_primary_source_review:\s*(\S+)', s).group(1))
by  = d.date.fromisoformat(re.search(r'revalidate_by:\s*(\S+)', s).group(1))
today = d.date.today()
assert by == rev + d.timedelta(days=180), ('revalidate_by must equal review + 180 days', rev, by)
print('review', rev, 'revalidate_by', by, 'today', today, 'STATUS', 'OK' if today <= by else 'STALE -- DO NOT RELY')
sys.exit(0 if today <= by else 2)
EOF
# 1d. the guide pointer resolves to the guide (title string, not just HTTP 200)
curl -sS https://plaudeapi.com/trade/cf28/ | grep -c "Received a CBP Form 28" ; echo "(expect >= 1)"
# 1e. every path named in the metadata block is a real path in knowledge-pop (maintainer only; see Tier 2)
```
Pass = 1a prints `1a clean`, 1b prints `exit 1`, 1c prints `STATUS OK`, 1d prints a count ≥ 1.

## Tier 2 — alignment-pin verification (maintainer only; the repo is private)
```bash
KP=C:/Users/Admin/knowledge-pop      # adjust to your checkout
git -C "$KP" rev-parse HEAD           # informational; the pin is by content hash, not by commit
for f in src/trade/eventscreen.ts src/trade/campaign.ts src/trade/config.ts src/trade/windows.ts \
         scripts/check-trade-eventscreen.mjs scripts/check-trade-eventscreen-matrix.mjs \
         content/trade/articles/cf28.md public/data/trade/latest.json; do
  echo "$(git -C "$KP" hash-object "$f")  $f"
done
```
Compare each hash with `aligned_with_production` in SKILL.md → Metadata. Any mismatch = **DRIFT CANDIDATE**: the skill is not wrong yet, but it is no longer aligned at a known baseline. Action: read the diff of the changed file(s), replay Tier 3, then either re-pin (update the hashes, bump `version`, add a `conformance/RUNS.md` entry) or mark the skill `STALE — DO NOT RELY` in its metadata until fixed. A new `public/data/trade/latest.json` vintage is a `revalidate_on_event` trigger even if the compiled files are unchanged.

## Tier 3 — replay protocol for `conformance/cases.yaml`
- Operator: a person, or a model. Record the model name and version (e.g. `claude-opus-5`), the sampling setting where controllable (temperature 0 preferred; if the host does not expose it, record "host default"), the date, and the skill `version`.
- Independence: each run reads SKILL.md and only the `inputs` + `as_of_date` of the fixtures; the `expects` / `forbids` / `allows` blocks are grading keys and are hidden from the operator (a fresh context per run).
- N = 3 independent runs per replay. A case **passes** only if every structured assertion holds in 3/3 runs. `allows.mentions` terms do not fail a case when they appear inside an explanation that the term does not apply.
- Grading is done by a person (or a second, separate model context) against the structured assertions; substring matching alone is not sufficient.
- Record every replay in `conformance/RUNS.md`: date, operator, model/version, sampling, skill version, per-case result, and any deviation with the exact quoted line. The baseline replay recorded there was run BEFORE the alignment pin was written, so a divergent skill was never pinned.

## Tier 4 — Run-Q revalidation (founder / attorney)
Every ≤ 90 days, and immediately on any `revalidate_on_event` trigger: re-read every authority under "Key facts" from the primary source; re-run Tiers 1–3; update `last_primary_source_review`, `revalidate_by` and the pin; bump `version`; record the review in `conformance/RUNS.md`. If any authority changed, mark the skill `STALE — DO NOT RELY` until the attorney re-approves the "Key facts" and the worked example.

## What this file does not claim
No continuous mirroring of production, no automatic drift detection, no executable tests, no guarantee that a replay passing today means the law is current tomorrow.
