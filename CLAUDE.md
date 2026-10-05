# plaudeapi-trade-skills — PlaudeAPI Trade skills constraints (added 2026-09-21)

Authority: current founder DEC records and EXP-90 (in the private `trade-counsel-os` governance repository) outrank this file; this file outranks the PlaudeAPI operating manual, which it applies. Skills here represent reviewed methodology and issue-spotting behaviour. They are not primary legal authority.

## Existing asset
Do not replace the current skill (`skills/us-import-risk-screen`) merely because another plan proposes a new CF-28 skill. Reconcile before rebuilding.

## Authority
Every legal rule implemented in a first-party skill must have a verified primary source (statute, regulation, court decision, official CBP form/instruction). GitHub repositories and commentary may be methodology sources only.

## Production relationship
Do not claim `mirrors production` unless executable continuous equivalence exists. Preferred wording: `aligned with production at recorded baseline`. Maintain the production-alignment metadata/pins in SKILL.md → Metadata.

## Drift
When pinned production files change: `DRIFT_DETECTED`. Then inspect the actual change; re-verify sources; replay the conformance fixtures; update the skill if needed; obtain attorney review where required (VERIFY.md Tiers 2–4).

## Tests
Do not call `conformance/cases.yaml` an automated regression suite unless executable code actually runs it. Distinguish conformance fixtures, the replay protocol, and automated tests (none exist here).

## Revalidation
Each skill tracks `last_primary_source_review`, `revalidate_by`, and material legal-change triggers (`revalidate_on_event`). Past revalidation: `STALE — DO NOT RELY` until reviewed.

## Storage claims
Any statement such as "nothing is stored" must be narrowly scoped to the actual PlaudeAPI browser tool behaviour being described ("stores nothing on any server"). Do not generalize that claim to all agent environments; a host running this skill may log prompts.

## Identity
The firm-identity and disclosure paragraph in README.md follows the current approved copy; do not edit it, embellish credentials, add prices or fees, or use "specialist"/"expert".

## Licensing
No NC material. Preserve attribution and methodology provenance. This repository is MIT.

## Third-party execution
Never run code or installers from methodology/vendor repositories without an explicit separate audit and authorization. This repository must stay free of dependencies, runtimes and CI unless a founder DEC changes that.

## Git
Develop on a feature branch (`s1/...`, `fix/...`); never directly on `master`. Push the feature branch; open a PR; do not auto-merge; do not push `master`. Pushing to this public repository is publication — founder action.
