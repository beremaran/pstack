# Pstack verification

Verified on 2026-10-17 against port.2. Discovery, automated script tests, and live model behavior are separate results. No external messages, tickets, PRs, merges, deployments, or live automations were created.

## Native host results

| Host | Version | Discovery | Live workflow |
| --- | --- | --- | --- |
| Claude Code | 2.1.301 | Native startup lists all **81** expected skill names; plugin manifest validation passes | **Deferred by user:** account usage limit prevented the live test. Discovery and manifest checks passed. |
| Codex | 0.163.0 | Native app-server `skills/list`: **81/81**, zero errors, project paths checked | **Passed TDD fixture:** two unittest tests; failing test precedes production edit in native events. |
| OpenCode | 2.0.31 | Authenticated server after activation: **81/81**, project paths checked | **Passed TDD fixture:** six tests through the new supervisor in one attempt. Also passed the smaller restatement workflow. |
| Pi | 1.3.0 | Native RPC command inventory: **81/81**; earlier SDK loader also passed | **Passed TDD fixture:** six tests; failing test precedes production edit in native events. |

Each completed TDD run read the installed workflow, added and ran a regression test before changing a small Python function, then passed its tests. The independent verifier checked **18 additional input combinations**, preserved `KEEP.txt`, and inspected native tool events for failing-before ordering. Agent prose alone was not counted as evidence. These fixtures demonstrate a representative workflow, not every playbook or integration.

Codex used its configured `gpt-6.1-sol` model. Pi's native messages report `desktop/Qwen3.8-27B`. OpenCode used its configured CLI default; the model identifier was not collected. No model override was added to these successful tests, and multi-family review behavior was not tested.

### OpenCode diagnosis

The earlier empty registry was a faulty probe, not evidence that the skills failed to load. Direct requests did not authenticate, and the probe swallowed HTTP errors. The one-shot CLI registry query could also run before plugin activation. The corrected check authenticates a private server, uses its read-only integration inventory as an activation barrier, filters the skill inventory to the staged project, and asserts the complete expected set. It now passes without a model request. Authentication failures are errors rather than empty-list successes.

The first live TDD attempt timed out after reading project material. A smaller attached-skill restatement completed. A subsequent TDD run with explicit skill inputs completed under the supervisor, passed the independent predicate, and recorded native failing-before evidence. The failed attempt was not counted as a pass.

### Codex diagnosis

The nested sandbox rejected commands before execution because the outer sandbox masks the shared daemon directory with mode `000`. A retry from the normal host environment, with the child Codex workspace-write sandbox retained, completed the fixture. The adapter does not disable the child's sandbox. This condition is also described in the [upstream nested-sandbox report](https://github.com/openai/codex/issues/53799).

### Claude diagnosis and remaining test

Initial attempts had expired OAuth credentials. The user refreshed sign-in. The inherited custom API/model route still returned `authentication_failed` outside the sandbox. An isolated, no-tools probe with the session's custom API/model environment overrides removed reached the standard provider and returned:

> You've hit your weekly limit · resets 4pm (Australia/Perth)

A fresh no-tools probe at 2026-10-17 09:53 UTC again returned HTTP 429 `usage_limit_reached`. Native rate-limit metadata identifies the seven-day window and reports reset epoch `1792310400` (2026-10-18 08:00 UTC / 16:00 Australia/Perth). This is a provider-reported reset time, not proof that a later test will succeed.

This proves the refreshed sign-in reached a different gate; it does not prove the TDD workflow passed. The user accepted deferring the live Claude TDD test on 2026-10-17 and will report issues encountered during use. This runtime test remains unverified; it is no longer a completion gate for this port. Saved user configuration was not changed. No paid fallback or quota workaround was configured. Native skill-name discovery and manifest validation remain verified.

## Automated checks

- Structural validator: **81 skills** pass frontmatter, directory/name, length, portable-field, runtime-reference, bundled-link, source-inventory, and manifest checks.
- Staged installation checks: all four project destinations pass dry-run without writes, byte-preserved resources/notices, cache exclusions, and refusal to overwrite local edits or dangling symlinks.
- Existing Bun suite: **68 passed, 0 failed**, 246 assertions. Covers orchestration stores, locks, ledgers, forge frontiers, PR state/pagination, queue cadence, CLI arguments, and plan parsing.
- New supervisor suite: **15 passed**. Covers native adapter arguments, independent completion checks, last-attempt verification, verification after an interrupted final attempt, no false pass from worker output, native terminal errors, retry/deadline bounds, stopping, timeout cleanup, large briefs that block stdin, concurrent ownership, orphan protection, private log permissions, and configuration identity.
- New updater suite: **14 passed**. Covers no-op comparison, three-way preservation of port adaptations, review gates, stale local edits/locks, multiple conflict hunks, nested skill examples as resources, validation rollback, new skills, deletions, unmapped dependency-bearing prose, executable-mode changes, and concurrent apply protection.
- TypeScript strict checking, Python compilation, Bash and JavaScript syntax checks, read-only workflow YAML parsing, native Claude manifest validation, and diff whitespace checks: passed.
- Safe existing helper invocations: orch/watch-pr help, a temporary decision-log append, and worktree audit against a temporary repository with explicit `-b HEAD`: passed.

Total automated unit cases: **97** (68 + 15 + 14), in addition to installer, loader, and live workflow checks.

## Supervisor and upstream tracking

The new supervisor completed the OpenCode fixture using its real CLI and normal permissions. Its artifact predicate passed after one worker attempt. Detached execution uses normal POSIX process supervision; stop/resume and failure cases are tested with deterministic subprocess fixtures. No OS service or hosted cloud worker was provisioned. An actual reboot or a multi-day fleet was not exercised.

The updater fetched upstream main and found **zero source changes** from the pinned commit `101b274dd991f694e1f7024be2157e5f3adf07de`. Synthetic upstream histories exercised actual staging, review, application, lock advancement, receipts, and rollback. The weekly GitHub workflow was parsed and reviewed locally; it has not been published or run on GitHub.

Benny's Slack/tracker writes, browser/PTY app verification, native cloud provisioning, remote scheduling, multi-model adversarial reviews, and shipping remain conditional project capabilities. They were not exercised against live services. They require the stated integrations, permissions, and project-specific checks; the port does not count their absence as a successful test.

## Reproduce

```sh
python scripts/validate-skills.py
python scripts/test-install-skills.py
python scripts/test-upstream.py
python -m unittest discover -s skills/pstack-runtime/scripts -p 'test_*.py'
python scripts/check-host-loading.py --agent codex
python scripts/check-host-loading.py --agent opencode
python scripts/check-host-loading.py --agent pi
python scripts/check-host-loading.py --agent claude --claude-init /path/to/private/native-startup.jsonl
```

Loader commands do not send model prompts. To prepare a live behavior test:

```sh
python scripts/smoke-host.py prepare --agent <agent> --output /tmp/pstack-smoke-<agent>
```

Review the generated configuration and native permissions, then run the installed runtime's `scripts/run.py` with that config and its suggested state directory. This step uses the host's authentication and can incur model usage. Run the supervisor from a normal terminal when nested sandboxing prevents its child from operating. Finally run `smoke-host.py verify` with the fixture project and native JSONL transcript. Raw transcripts, credentials, and test state stay outside this repository.

See [supervised execution](../skills/pstack-runtime/references/supervised-runs.md), [host adapters](../skills/pstack-runtime/references/hosts.md), and [upstream updates](upstream-updates.md). Record any future Claude live test here; it is deferred by user agreement.
