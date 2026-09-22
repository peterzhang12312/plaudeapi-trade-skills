# VERIFY — how this repository is checked (written 2026-09-21 for skill version 0.3.0)

This repository contains a prose skill and replayable fixtures. **There is no test runner, no CI, no dependency and no runtime in this repository, and nothing here detects drift automatically.** Tier 1 uses only a POSIX shell, `git`, `curl` and a Python 3 interpreter on PATH (`python3` or `python`); nothing is installed. Verification is four distinct activities; a report must say which of them were performed.

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
PY=$(command -v python3 || command -v python) || { echo "python3/python not on PATH -- Tier 1a/1c need a Python 3 interpreter"; exit 2; }
# 1a. wording: no unqualified storage claim anywhere in the repo
"$PY" - <<'EOF'
import re, pathlib, sys
bad = []
for f in [pathlib.Path('README.md'), pathlib.Path('VERIFY.md'), *pathlib.Path('skills').rglob('*.md'), *pathlib.Path('conformance').glob('*')]:
    for i, line in enumerate(f.read_text(encoding='utf-8').splitlines(), 1):
        if '(?!' in line:  # the check's own definition line
            continue
        if re.search(r'stores nothing(?! on any server)|nothing is stored', line, re.I):
            bad.append(f'{f}:{i}: {line.strip()[:100]}')
print('\n'.join(bad) or '1a clean'); sys.exit(1 if bad else 0)
EOF
# 1b. no fee/price offer, no unsupported credential wording, no 'mirrors production'
#     (user-stated duty amounts and the volume bands in the intake table are legitimate content and are NOT matched)
grep -rniE '\$[0-9][0-9,.]*[[:space:]]*(flat|fixed|fee|retainer|per hour|/h|/hour)|(fee|price|retainer|charge)[[:space:]]+(of|is|:)[[:space:]]*\$|specialist|\bexpert\b|mirrors production' README.md VERIFY.md skills/ conformance/ | grep -vE '^VERIFY\.md:[0-9]+:(# 1b|grep -rniE)' ; echo "exit $? (1 = clean)"
# 1c. metadata dates parse and the skill is not expired
"$PY" - <<'EOF'
import re, datetime as d, sys
s = open('skills/us-import-risk-screen/SKILL.md', encoding='utf-8').read()
rev = d.date.fromisoformat(re.search(r'last_primary_source_review:\s*(\S+)', s).group(1))
by  = d.date.fromisoformat(re.search(r'revalidate_by:\s*(\S+)', s).group(1))
today = d.date.today()
assert by == rev + d.timedelta(days=180), ('revalidate_by must equal review + 180 days', rev, by)
print('review', rev, 'revalidate_by', by, 'today', today, 'STATUS', 'OK' if today <= by else 'STALE -- DO NOT RELY')
sys.exit(0 if today <= by else 2)
EOF
# 1d. the guide pointer resolves to the guide (HTTP 200 AND the `expected_title` recorded next to the guide hash in SKILL.md Metadata), and the revalidate_on_event trigger page exists
TITLE=$(grep -oE 'expected_title: "[^"]+"' skills/us-import-risk-screen/SKILL.md | cut -d'"' -f2)
BODY=$(mktemp); CODE=$(curl -sS -o "$BODY" -w '%{http_code}' https://plaudeapi.com/trade/cf28/); echo "guide http $CODE, title hits $(grep -c "$TITLE" "$BODY") (expect 200 and >= 1)"; rm -f "$BODY"
curl -sS -o /dev/null -w 'timeline http %{http_code} (expect 200)\n' https://plaudeapi.com/trade/timeline/
# 1e. the version in SKILL.md Metadata equals cases.yaml skill_version
V1=$(grep -oE '^version: [0-9.]+' skills/us-import-risk-screen/SKILL.md | cut -d' ' -f2); V2=$(grep -oE '^skill_version: [0-9.]+' conformance/cases.yaml | cut -d' ' -f2); [ "$V1" = "$V2" ] && echo "1e versions match ($V1)" || echo "1e VERSION MISMATCH skill=$V1 fixtures=$V2"
```
Pass = 1a prints `1a clean`, 1b prints `exit 1`, 1c prints `STATUS OK`, 1d prints `http 200` with title hits ≥ 1 and `timeline http 200`, 1e prints `versions match`. (Path existence is proven by Tier 2: `git hash-object` fails on a missing path.)

## Tier 2 — alignment-pin verification (maintainer only; the repo is private)
```bash
KP="${KP:-../knowledge-pop}"          # path to your private knowledge-pop checkout (override with KP=...)
echo "knowledge-pop master: $(git -C "$KP" rev-parse master)   (informational; the pin is by content hash, not by commit)"
# the file list is read from the Metadata block so SKILL.md stays the only list; a missing path fails here (that is check 1e)
grep -oE '^    (src|scripts|content|public)/[^:]+' skills/us-import-risk-screen/SKILL.md | tr -d ' ' | grep . | while read -r f; do
  echo "$(git -C "$KP" rev-parse "master:$f")  $f"   # committed blob id: independent of core.autocrlf rewriting the working tree (git hash-object on a CRLF-converted checkout would differ)
done
```
Compare each hash with `aligned_with_production` in SKILL.md → Metadata. Any mismatch = **DRIFT CANDIDATE**: the skill is not wrong yet, but it is no longer aligned at a known baseline. Action: read the diff of the changed file(s), replay Tier 3, then either re-pin (update the hashes, bump `version`, add a `conformance/RUNS.md` entry) or mark the skill `STALE — DO NOT RELY` in its metadata until fixed. A new `public/data/trade/latest.json` vintage is a `revalidate_on_event` trigger even if the compiled files are unchanged.

## Tier 3 — replay protocol for `conformance/cases.yaml`
- Operator: a person, or a model. Record the model name and version (e.g. `claude-opus-5`), the sampling setting where controllable (temperature 0 preferred; if the host does not expose it, record "host default"), the date, and the skill `version`.
- Operator prompt (record it verbatim in RUNS.md): "Read SKILL.md in full and follow it exactly. Read cases.yaml but use only `as_of_date` and each case's `inputs`; do not read `expects`/`forbids`/`allows`. For each case produce the screen with today's date = as_of_date. Treat null/blank inputs as not provided." Setting today = `as_of_date` is what keeps C09/C21 (future dates) and the past-date flags stable after the replay date.
- Independence: each run reads SKILL.md and only the `inputs` + `as_of_date` of the fixtures; the `expects` / `forbids` / `allows` blocks are grading keys and are hidden from the operator (a fresh context per run).
- N = 3 independent runs per replay. A case **passes** only if every structured assertion holds in 3/3 runs. Each assertion key is graded per the vocabulary block at the top of `conformance/cases.yaml` (the single source for grading semantics, including the `allows.mentions` and `forbids.instruction_wording` carve-outs).
- Grading is done by a person (or a second, separate model context) against the structured assertions; substring matching alone is not sufficient. A replay graded by the same context that wrote the fixtures is recorded as such in RUNS.md and counts as a baseline only; the next replay must be graded independently.
- Record every replay in `conformance/RUNS.md`: date, operator, model/version, sampling, skill version, per-case result, and any deviation with the exact quoted line. The baseline replay recorded there was run BEFORE the alignment pin was written; it shows that no divergence was observed in the replayed fixtures, which is all a sampled replay can show.

## Tier 4 — Run-Q revalidation (founder / attorney)
Run-Q is the *review cadence* (every ≤ 90 days); `revalidate_by` (review + 180 days) is the *hard ceiling* after which Tier 1c marks the skill STALE even if no Run-Q happened. A skill 120 days past review is therefore "overdue for Run-Q" but not yet STALE; both statements are true and refer to different things. Every ≤ 90 days, and immediately on any `revalidate_on_event` trigger: re-read every authority under "Key facts" from the primary source; re-run Tiers 1–3; update `last_primary_source_review`, `revalidate_by` and the pin; bump `version`; record the review in `conformance/RUNS.md`. If any authority changed, mark the skill `STALE — DO NOT RELY` until the attorney re-approves the "Key facts" and the worked example.

## What this file does not claim
No automatic drift detection, no executable tests, no guarantee that a replay passing today means the law is current tomorrow; for what the pin proves, see the `limitation` field in the skill's Metadata.
