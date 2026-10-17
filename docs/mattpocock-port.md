# Matt Pocock skills vendor

Vendored from [mattpocock/skills](https://github.com/mattpocock/skills) at `49dd158d1076134a641b33efb035946536778336`, upstream package version **1.3.1**. The source is MIT-licensed; its notice is retained in `upstream/mattpocock-LICENSE`. The lock records SHA256 hashes and Git modes for **all 190 tracked source files**, including docs, changelogs, manifests, development tooling, and assets outside the copied skill trees.

## Coverage and naming

All **38** source skills and all their bundled resources are included: 20 engineering, seven productivity, four misc, and seven in-progress. Every canonical directory is directly under `skills/`, with the prefix `mattpocock-`. This keeps pstack's `tdd`, `teach`, and other overlapping names unchanged, and gives each upstream independent ownership. Internal skill references use the imported names and relative links; start with [mattpocock-ask-matt](../skills/mattpocock-ask-matt/SKILL.md).

The inventory below records the initial source category. The seven in-progress skills are experimental upstream, excluded from its default plugin, and can change or disappear without warning; they are deliberately included here and labelled in their metadata and instructions.

| Source category | Canonical skill |
| --- | --- |
| engineering | [mattpocock-ask-matt](../skills/mattpocock-ask-matt/SKILL.md) |
| engineering | [mattpocock-code-review](../skills/mattpocock-code-review/SKILL.md) |
| engineering | [mattpocock-codebase-design](../skills/mattpocock-codebase-design/SKILL.md) |
| engineering | [mattpocock-diagnosing-bugs](../skills/mattpocock-diagnosing-bugs/SKILL.md) |
| engineering | [mattpocock-domain-modeling](../skills/mattpocock-domain-modeling/SKILL.md) |
| engineering | [mattpocock-grill-with-docs](../skills/mattpocock-grill-with-docs/SKILL.md) |
| engineering | [mattpocock-implement](../skills/mattpocock-implement/SKILL.md) |
| engineering | [mattpocock-implement-spec](../skills/mattpocock-implement-spec/SKILL.md) |
| engineering | [mattpocock-improve-codebase-architecture](../skills/mattpocock-improve-codebase-architecture/SKILL.md) |
| engineering | [mattpocock-pr](../skills/mattpocock-pr/SKILL.md) |
| engineering | [mattpocock-prototype](../skills/mattpocock-prototype/SKILL.md) |
| engineering | [mattpocock-research](../skills/mattpocock-research/SKILL.md) |
| engineering | [mattpocock-retro](../skills/mattpocock-retro/SKILL.md) |
| engineering | [mattpocock-setup-matt-pocock-skills](../skills/mattpocock-setup-matt-pocock-skills/SKILL.md) |
| engineering | [mattpocock-tdd](../skills/mattpocock-tdd/SKILL.md) |
| engineering | [mattpocock-to-spec](../skills/mattpocock-to-spec/SKILL.md) |
| engineering | [mattpocock-to-tickets](../skills/mattpocock-to-tickets/SKILL.md) |
| engineering | [mattpocock-triage](../skills/mattpocock-triage/SKILL.md) |
| engineering | [mattpocock-wayfinder](../skills/mattpocock-wayfinder/SKILL.md) |
| engineering | [mattpocock-wizard](../skills/mattpocock-wizard/SKILL.md) |
| in-progress | [mattpocock-chief-of-staff](../skills/mattpocock-chief-of-staff/SKILL.md) |
| in-progress | [mattpocock-claude-handoff](../skills/mattpocock-claude-handoff/SKILL.md) |
| in-progress | [mattpocock-loop-me](../skills/mattpocock-loop-me/SKILL.md) |
| in-progress | [mattpocock-setup-ts-deep-modules](../skills/mattpocock-setup-ts-deep-modules/SKILL.md) |
| in-progress | [mattpocock-writing-beats](../skills/mattpocock-writing-beats/SKILL.md) |
| in-progress | [mattpocock-writing-fragments](../skills/mattpocock-writing-fragments/SKILL.md) |
| in-progress | [mattpocock-writing-shape](../skills/mattpocock-writing-shape/SKILL.md) |
| misc | [mattpocock-git-guardrails-claude-code](../skills/mattpocock-git-guardrails-claude-code/SKILL.md) |
| misc | [mattpocock-migrate-to-shoehorn](../skills/mattpocock-migrate-to-shoehorn/SKILL.md) |
| misc | [mattpocock-scaffold-exercises](../skills/mattpocock-scaffold-exercises/SKILL.md) |
| misc | [mattpocock-setup-pre-commit](../skills/mattpocock-setup-pre-commit/SKILL.md) |
| productivity | [mattpocock-grill-me](../skills/mattpocock-grill-me/SKILL.md) |
| productivity | [mattpocock-grilling](../skills/mattpocock-grilling/SKILL.md) |
| productivity | [mattpocock-handoff](../skills/mattpocock-handoff/SKILL.md) |
| productivity | [mattpocock-teach](../skills/mattpocock-teach/SKILL.md) |
| productivity | [mattpocock-to-questionnaire](../skills/mattpocock-to-questionnaire/SKILL.md) |
| productivity | [mattpocock-wait-what](../skills/mattpocock-wait-what/SKILL.md) |
| productivity | [mattpocock-writing-for-agents](../skills/mattpocock-writing-for-agents/SKILL.md) |

## Adaptations and limits

The workflows retain their substantive steps, reference material, scripts, templates, credits, and optional Codex metadata. Source category READMEs and repository packaging are not copied into discovery directories; they are tracked for review in the lock. This repository's existing installer, Claude plugin, and Pi package expose the canonical collection instead. No second upstream plugin is installed, and no machine-local skill configuration is changed by vendoring.

Shared frontmatter uses the common format. Upstream argument hints become input prose. Explicit-only intent is preserved as `metadata.invocation: explicit-request` and an instruction in the workflow; existing Codex `agents/openai.yaml` policies are retained. This does not claim equivalent discovery filtering on every host. Skill calls become named instructions with bundled links. Reset/compaction references describe capabilities rather than universal slash commands. The writing-for-agents mechanics reference is adapted to teach these same portable conventions.

[Shared portability guidance](../skills/mattpocock-ask-matt/PORTABILITY.md) specifies integration prerequisites, authorization, context handling, and serial fallbacks. Parallel reviews use independent contexts when available; serial reviews disclose the loss of isolation. Integration-branch implementation still follows the ticket graph when only serial workers are available. Background handoff uses the existing bounded supervisor or returns a handoff file; it never claims a job was launched when unavailable. Runtime permissions remain those of the native host.

The Git guardrail's Claude hook configuration is isolated in an optional reference, checked against the official [hooks](https://code.claude.com/docs/en/hooks) and [settings](https://code.claude.com/docs/en/settings) documentation. All four agents can run the bundled JSON command filter as a preflight, but automatic interception is only described for Claude. This simple textual filter is advisory, not a shell parser or comprehensive security boundary. Installing the collection installs no hook.

GitHub/GitLab tracker operations require their authenticated CLI or connector; the upstream local-Markdown tracker template remains available. User authorization still governs external writes. Prerequisites for code checks, browser access, Bash helpers, dependency-cruiser, and package managers are conditional on the selected workflow; none were globally installed for this vendor operation.

The PR workflow includes attributed material from Humanlayer's show-me skill. Upstream explicitly states in its bundled `CREDITS.md` that this is copied content, not a runtime skill dependency. That credit and its links are preserved. No additional plugin is required by the current workflows; future manifest or prose dependency changes require explicit review.

## Updates

Use [the shared reviewed update process](upstream-updates.md) with `--source mattpocock`. Its baseline and receipts are separate from pstack:

```sh
git clone https://github.com/mattpocock/skills.git /tmp/mattpocock-skills-upstream
python scripts/upstream.py check --source mattpocock --checkout /tmp/mattpocock-skills-upstream --fetch
python scripts/upstream.py stage --source mattpocock --checkout /tmp/mattpocock-skills-upstream --output /tmp/mattpocock-review
# Review every entry in plan.json and every merged candidate first.
python scripts/upstream.py apply --source mattpocock --stage /tmp/mattpocock-review
```

New skills map to `mattpocock-<upstream-directory>`, including new category directories. Raw new skills must be adapted before acceptance; validation rejects an unported name, frontmatter, or missing runtime reference. Category moves, duplicate skill names, upstream renames, and deleted-but-retained skills require deliberate review. A move appears as deletion/addition, not an inferred rename. New runtime/plugin dependencies require extending the vendor inventory and port; arbitrary dependencies in prose are not automatically inferred.

No automatic apply is configured. Weekly Actions checks both sources independently and provides one review artifact per source. Applying an update creates `upstream/updates/mattpocock/<commit>.json` and changes only the selected baseline after validation. Intentional `keep` decisions record local divergence while advancing the reviewed source baseline. Keep these receipts with the adapted files.

## Verification

See [the verification record](mattpocock-verification.md) for actual native discovery, test coverage, and deferred behavior checks. Format compatibility alone is not evidence that every workflow was exercised.
