# Shared prerequisites and host fallbacks

These adaptations apply to every `mattpocock-*` workflow and take precedence over upstream host assumptions in the remaining text. Follow the [runtime contract](../pstack-runtime/SKILL.md) for concrete worker adapters and bounded supervision.

## Skills and context

Read a named companion's linked `SKILL.md` and follow its instructions. Names are portable identifiers, not literal slash commands. Use the `mattpocock-*` variants inside this collection; similarly named pstack or user-installed workflows have different sources and semantics.

`metadata.invocation: explicit-request` preserves upstream's intent: wait for a user request before starting that workflow. Codex's optional `agents/openai.yaml` retains its native invocation policy. The shared format does not claim equivalent automatic-discovery filtering on Claude Code, OpenCode, or Pi. All workflows remain readable directly on all four hosts. Argument hints are recorded as input prose instead of host-specific frontmatter.

Context reset, compaction, background execution, and scheduling depend on the host. Use a supported native operation when available. Otherwise save a scoped handoff file and give the user the file path for a fresh session; do not pretend the current session was reset or that a scheduler exists. Decide using the actual host context budget; upstream's approximate 150k-token “smart zone” is a heuristic, not a supported limit for every model.

## Delegation

Parallel and background roles require an available, authorized delegation capability. When available, use separate contexts, narrow briefs, distinct worktrees for writers, and the same evidence and completion checks described by the workflow. Use the [host adapters](../pstack-runtime/references/hosts.md) or [supervisor](../pstack-runtime/references/supervised-runs.md) when separate CLI workers are appropriate.

When unavailable, perform roles sequentially, keeping each role's inputs and report separate. Code review still reports Standards and Spec separately; state that independent contexts were unavailable. Implement-spec still respects blocking edges, uses an integration branch, and validates every ticket, but processes ready tickets serially. Chief-of-staff keeps its durable goal notes and performs bounded work in the current session. Research still produces a cited file. Sequential execution does not provide independent reviewer isolation or simultaneous progress; disclose that limit. If the user specifically requires concurrency or unattended operation, report the missing prerequisite instead of substituting a serial run silently.

## Integrations and authorization

Use the project's existing tracker configuration. GitHub needs authenticated `gh`, GitLab needs authenticated `glab`, and custom trackers need their configured connector or CLI. Without a working remote integration, prepare local Markdown drafts using the bundled local-tracker template; do not claim they were published or that remote labels/dependencies were changed. Preserve the user's chosen tracker and explain missing access. Browsing/research needs source access; if unavailable, record which claims remain unverified and request the missing source rather than inventing citations.

Tracker comments, issues, notifications, branch pushes, PRs, merges, credentials, and infrastructure changes require authorization from the user's request or existing session. A workflow's example is not authorization for an unrelated external action. Prepare concrete local artifacts before asking for any missing authorization. Never put secrets in skill files, handoffs, logs, or committed examples.

Code and repository workflows need the relevant language/runtime, package manager, Git, and project checks. Install dependencies in the target project only when authorized by the task. Detect existing configuration and merge changes; preserve unrelated user settings. If the required runtime or check is unavailable, report the unverified step. HTML output can be opened with the platform's file opener when available; otherwise give the absolute artifact path. Bash helpers require Bash; the Git command filter additionally requires `jq` and standard text tools.

## Shared repository instructions

Prefer the project's established shared instruction source. If `CLAUDE.md` points to `AGENTS.md`, edit `AGENTS.md`; keep the pointer. Otherwise put shared workflow guidance in `AGENTS.md` and, when necessary, add a small Claude pointer with the user's agreement. Do not create competing copies of the same instructions. Check that the active host can discover the shared file; provide its path explicitly when automatic loading is not verified.

## Optional Claude Git hook

The [Git guardrail workflow](../mattpocock-git-guardrails-claude-code/SKILL.md) includes a Claude-only adapter. Other hosts can use the bundled JSON command preflight manually and their existing permission controls. This is an advisory textual pattern filter, not a shell parser or comprehensive security boundary: aliases, wrappers, alternate spellings, and other tools may evade it. A passing preflight does not authorize a command. No hook is installed merely by vendoring or installing these skills.
