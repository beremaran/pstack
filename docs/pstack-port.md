# Pstack migration

The source is [cursor/plugins at 101b274dd991f694e1f7024be2157e5f3adf07de](https://github.com/cursor/plugins/tree/101b274dd991f694e1f7024be2157e5f3adf07de/pstack), fetched on 2026-10-17. The pinned source inventory and SHA-256 hashes are in [pstack-lock.json](../upstream/pstack-lock.json). This is a maintained fork; updating that lock alone does not migrate a new upstream revision.

## Included dependency closure

| Source | Port |
| --- | --- |
| pstack 0.15.25, 54 top-level skills | All 54 in canonical `skills/<name>/`, including their references, templates, tests, scripts, and 23 playbooks |
| cursor-team-kit 1.2.0 | All 18 skills, including deslop, control-cli/control-ui, CI workflows, PR review canvas assets, and code-quality rubric |
| pstack delegate profiles | `poteto-agent` and `comment-sicko` skills |
| companion delegate profiles | `ci-watcher` skill; quality-review delegate brief under its existing rubric skill's `references/` |
| companion always-applied TypeScript rules | `deslop/references/companion-rules.md`, reached from deslop and typescript-best-practices; scoped to relevant TypeScript reviews |
| Benny automation pack | setup-benny, triage-issue-reports, reproduce-and-fix-issues, operational references, configuration example, and both runner prompt templates |
| Host skill-authoring built-in | New portable create-skill workflow |
| Host visualization built-in referenced by ketchup | New portable visualize workflow |
| Host babysit built-in | Existing bundled poteto-mode Babysit playbook, which upstream already prefers |
| Host loop / scheduling / automation creation | Real local CLI supervisor with bounds, persistent state, stop/resume and artifact checks; configured runner prerequisites for Benny and bot webhooks |
| Runtime adaptation | New pstack-runtime skill read by every entrypoint |

Total: **81 skills**. The full companion plugin is included, rather than selecting only its three explicitly named dependencies. No further plugin dependencies are declared by either manifest or required by the companion workflows. `watch-pr`, `orch`, `check-plan`, and `worktree-audit` are bundled helpers, not missing slash skills. Prototype, orchestrate, shipping, and babysit are playbooks. Feature-map examples such as create-note and search are examples, not dependencies.

Benny's configuration and operational safety constraints remain intact. Setup now targets a chosen runner instead of a Cursor automation editor. The port includes a local execution supervisor, but does not provision a live Benny event runner or grant messaging rights. make-bot-ui retains the server-side secret and webhook pattern while using the chosen provider's documented contract, rather than an unavailable routine API.

## External prerequisites, not vendored agent plugins

- Bun, commander 14.0.0, bun-types, and TypeScript remain in the bundled scripts package and lockfile. Run the frozen install before using those helpers. No runtime cache or node_modules is committed.
- Git and authenticated GitHub CLI support forge workflows. Origin is optional, with GitHub fallback. Graphite is not required.
- Browser, Electron, and PTY verification reuse available harnesses, Playwright/CDP, tmux, or temporary probes. Missing tools are explicit verification gaps.
- `why`, `recall`, and `reflect` optionally search available issue tracking, chat, document, observability, error-tracking, and warehouse integrations. The source already discovers these at runtime. Their category playbooks are included; service connectors and credentials are not bundled dependencies. Local source-control investigation remains usable without them.
- Benny requires a configured Slack/tracker adapter, authorized thread writes, feature map, control harness, and runner. It fails closed without them. Tailscale is optional for bot UI exposure; Apple simulator maintenance is conditional on macOS/Xcode.

## Portability decisions

Shared instructions describe capabilities and keep one source per skill. Every entrypoint reads [pstack-runtime](../skills/pstack-runtime/SKILL.md). The Claude and Codex marketplace manifests and the Pi package metadata all load that same tree; the `skills` CLI copies it into each host's supported discovery directory. No host needs executable extension or hook code for these workflows.

Models default to the parent, and per-host role overrides live in project `.pstack/models.md`. Unsupported model controls are reported. Parallel work uses supported delegation or explicitly authorized separate CLI processes with independent checkouts, or explicitly labeled serial self-review. Shipping still requires an independent verifier. Host-specific task fields, private history paths, magic model suffixes, native loops, and cloud-agent assumptions have been removed.

The canonical frontmatter uses common fields and normal automatic discovery. Upstream explicit-only flags, UI icons/colors, background/model flags, and file-glob metadata were removed rather than claiming uniform enforcement across hosts. Direct invocation and cross-skill reads remain available. Native custom modes and automatic TypeScript rule injection are not installed; scope is expressed in descriptions and workflow routing.

Upstream's generic permission grants and destructive checkout-reset shortcuts were replaced with the current session's authorization and preservation of unrelated work. The migration does not authorize posting messages, creating tickets, enabling automations, merging, deploying, or deleting data by itself.

Source README/guide prose, logos, and the old Cursor/Claude adapter are not runtime dependencies. They are replaced by the portable help skill and repository documentation. MIT notices for both source packs are retained under `upstream/`.

## Updating

Use the [upstream update workflow](upstream-updates.md). It compares every source hash and executable mode, stages three-way merge candidates, reports unmapped changes for dependency review, requires explicit per-file decisions, validates the migrated result, and writes an update receipt. A weekly read-only GitHub job produces review artifacts when upstream changes. Neither that job nor a comparison advances the pinned baseline automatically.

The port now has executable local adapters for all four CLIs, described in [host execution](../skills/pstack-runtime/references/hosts.md), and a bounded, detachable supervisor described in [supervised runs](../skills/pstack-runtime/references/supervised-runs.md). This replaces the need for proprietary cloud workers on a user-provisioned local or remote POSIX host. Cloud provisioning, event services, and OS-service installation remain explicit external setup, not silently simulated features.
