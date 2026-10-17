# Matt Pocock vendor verification

Verified on 2026-10-17 for bundle `0.15.25-port.3`, against upstream `49dd158d1076134a641b33efb035946536778336` (1.3.1). This record covers the new vendor and changes to shared tooling. The [pstack verification record](pstack-verification.md) remains the historical evidence for the earlier port.

## Coverage and structure

All **38** upstream skills are present in canonical `skills/mattpocock-*/SKILL.md` directories. Every source file within a skill directory has a corresponding local file; additional portability references are bundled locally. MIT notice, copied PR credit, resource links, optional Codex metadata, source categories, and experimental labels are retained. Full-repository provenance covers **190** tracked source files with hashes and modes. No runtime skill dependency was dropped; current upstream explicitly identifies show-me as attributed copied material rather than an installed dependency.

The structural validator passes **119** total canonical skills, checking names/frontmatter, bundled Markdown links, runtime references, source ownership, and manifests. Installation tests pass for all four project discovery destinations, including byte-preserved resources and all source notices/locks, dry-run behavior, overwrite refusal, and dangling symlink handling.

## Native discovery

| Host | Check performed for this vendor | Result |
| --- | --- | --- |
| Codex | Native app-server inventory with project paths | **119/119**, no loader errors |
| OpenCode | Authenticated native inventory after activation | **119/119** |
| Pi | Native RPC command inventory | **119/119** |
| Claude Code | Native plugin manifest validation plus common-format review and installer checks | **Passed with advisory warnings.** New 119-skill native startup inventory and live workflow were not run. The user deferred Claude live testing during the earlier port. |

Claude's validator warns that plugin-root `CLAUDE.md` is not project context, and suggests a marketplace installation line. Runtime behavior is carried in skills; no marketplace is declared or advertised as published. The existing plugin identity `pstack` is retained to avoid breaking installations; the plugin and Pi package descriptions now include both vendors.

Discovery is not execution. No claim is made that all 38 workflows, all playbooks, remote integrations, or every host-specific optional feature were run.

## Live imported workflow

A fresh Pi fixture explicitly loaded **mattpocock-tdd** and fixed a small Python clamp function using standard-library unittest. The bounded supervisor completed in one worker attempt with exit 0 and an independent artifact check. Native JSONL events record the failed test before the production edit (**1126 < 1200**) and an explicit read of the imported skill. The independent verifier passed **18 input cases**, confirmed a test file exists and unittest passes, and confirmed `KEEP.txt` was unchanged.

The first invocation failed before model work because the outer filesystem sandbox prevented Pi's normal trust-file lock. A new bounded invocation outside that outer sandbox completed using the normal host configuration and CLI-default model (native events report `desktop/Qwen3.8-27B`), without adding a permission-bypass flag. The failed attempt is not counted as a pass. Fixture artifacts, raw transcripts, and supervisor state remain outside the repository under `/tmp`; no credentials were copied into the repository. No commits, pushes, tracker writes, delegated agents, or infrastructure actions were performed by the fixture.

This single fixture verifies a representative imported workflow on Pi. New live imported-workflow behavior on Codex and OpenCode was not exercised; their earlier pstack fixtures do not establish this vendor's behavior. Claude live testing remains deferred by agreement.

## Upstream/update tooling

**22 updater tests pass**: the existing 14 pstack cases plus eight new Matt Pocock cases. New coverage exercises namespace-preserving three-way updates, whole-repository docs/manifest tracking, required new-skill adaptation and rollback, wrong-source apply refusal, duplicate names across categories, merge conflicts, retained deletions, review gates, independent source baselines, and source-specific receipts. pstack's default commands and receipt layout remain compatible. The shared exclusive apply lock prevents concurrent cross-source writes.

A real upstream fetch followed by comparison reports **zero changes** from the recorded baseline. No-op staging against that checkout succeeds with zero review entries. The weekly Actions matrix was parsed and reviewed locally; it checks both sources independently and uploads separately named review artifacts. The extension has not yet been published or executed on GitHub. No automatic application, issue posting, PR creation, or baseline advancement is enabled.

The **15 supervisor regression tests** also pass after the shared tooling changes. Python compilation, Bash syntax checks for both imported helpers, Node syntax/loading of the dependency-cruiser configuration, and diff whitespace checks pass. The Git filter rejected synthetic `git push origin main` input with exit 2 and accepted synthetic `git status` with exit 0; neither command was executed. The HITL template captured synthetic observations from piped input without contacting an app. The dependency-cruiser CLI's actual import-boundary enforcement was not exercised, and no project dependency was installed for it.

## Reproduce

```sh
python scripts/validate-skills.py
python scripts/test-install-skills.py
python scripts/test-upstream.py
python -m unittest discover -s skills/pstack-runtime/scripts -p 'test_*.py'
python scripts/check-host-loading.py --agent codex
python scripts/check-host-loading.py --agent opencode
python scripts/check-host-loading.py --agent pi
claude plugin validate .
python scripts/upstream.py check --source mattpocock --checkout /path/to/mattpocock-skills --fetch --fail-if-changed
```

To prepare the representative imported TDD fixture, without starting a model:

```sh
python scripts/smoke-host.py prepare --agent pi --skill mattpocock-tdd --output /tmp/mattpocock-smoke-new
```

Review its generated config, then use the existing supervisor and independent `smoke-host.py verify` command as described in [supervised execution](../skills/pstack-runtime/references/supervised-runs.md). Native runtime credentials and permissions are prerequisites; reports must distinguish failed, deferred, discovery-only, and executed checks.
