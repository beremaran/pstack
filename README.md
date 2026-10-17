# Personal skills

Reusable agent skills for Codex, Claude Code, OpenCode, and Pi.

Each skill lives in `skills/<name>/SKILL.md` with YAML `name` and `description` fields. Supporting scripts, references, and assets stay inside its directory. This repository is the canonical source; install individual skill directories into the discovery location supported by your agent.

See [AGENTS.md](AGENTS.md) for authoring and compatibility requirements.

Agent documentation: [Codex](https://developers.openai.com/codex/skills), [Claude Code](https://code.claude.com/docs/en/skills), [OpenCode](https://opencode.ai/docs/skills/), and [Pi](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/skills.md).

## Pstack bundle

This repository ports pstack 0.15.25 and its complete cursor-team-kit 1.2.0 companion into 81 canonical skills. Start with `poteto-mode` for engineering work, `poteto-help` for routing, and `setup-pstack` for optional per-role model configuration. See [migration scope and dependencies](docs/pstack-port.md) and [verification results](docs/pstack-verification.md).

### Install skills

Python 3.9+ is required for the installer. From this checkout, choose your agent:

```sh
python scripts/install-skills.py --agent claude --project /path/to/project
python scripts/install-skills.py --agent codex --project /path/to/project
python scripts/install-skills.py --agent opencode --project /path/to/project
python scripts/install-skills.py --agent pi --project /path/to/project
```

Use `--dry-run` to preview, or `--user` instead of `--project` for a personal install. The installer copies the whole bundle, supporting resources, attribution, and source inventory. It refuses existing skill paths before copying anything. For updates, stage with `--dest /path/to/staging`, review differences, and merge deliberately. No credentials, host settings, integrations, or dependencies are installed by this command.

| Agent | Project discovery | User discovery | Invocation |
| --- | --- | --- | --- |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` | `/poteto-mode` |
| Codex | `.agents/skills/` | `~/.agents/skills/` | `$poteto-mode` |
| OpenCode | `.opencode/skills/` | `~/.config/opencode/skills/` | Ask to use `poteto-mode` |
| Pi | `.pi/skills/` | `~/.pi/agent/skills/` | `/skill:poteto-mode` |

Restart or reload the host after installation. Avoid installing duplicate copies into discovery locations the same host also scans. Pi's user path above assumes its default agent directory; use `--dest` if `PI_CODING_AGENT_DIR` differs. OpenCode's user path assumes the default XDG config root; use `--dest` for a custom one. Paths were checked against current [Claude](https://code.claude.com/docs/en/skills), [Codex](https://developers.openai.com/codex/skills), [OpenCode](https://opencode.ai/docs/skills/), and [Pi](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/configuration.md) documentation.

### Native packaging

Claude Code can load this checkout as a local plugin:

```sh
claude --plugin-dir /absolute/path/to/beremaran-skills
```

Its skills use the plugin namespace, for example `/pstack:poteto-mode`. The root `.claude-plugin/plugin.json` uses the canonical `skills/` tree. Repository `CLAUDE.md` is contributor guidance; plugin behavior is carried by the skills themselves. See the [Claude plugin reference](https://code.claude.com/docs/en/plugins-reference).

Pi can install this checkout as a [local Pi package](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/packages.md):

```sh
pi install /absolute/path/to/beremaran-skills -l
```

The root `package.json` exposes only `skills/`, with no extensions or hooks. Choose either package/plugin loading or a copied skills install for each host. Codex and OpenCode use their documented skill directories here; no executable plugin is needed.

### Runtime requirements

All workflows read the shared [runtime contract](skills/pstack-runtime/SKILL.md). Models inherit the current session unless configured in `<project>/.pstack/models.md`. Delegation and integrations are optional capabilities; serial self-review is labeled and cannot satisfy independent shipping gates. History mining uses only explicitly scoped history. Native loops, cloud agents, schedulers, and Cursor APIs are replaced by capability-based workflows.

Bun is needed for `poteto-mode`'s orchestration and PR-watcher scripts. Install their locked dependencies before running them:

```sh
cd skills/poteto-mode/scripts
bun install --frozen-lockfile
bun test orch watch-pr check-plan.test.ts
bun run typecheck
```

GitHub workflows need authenticated `gh` or a supported forge integration. Browser and terminal verification reuse existing harnesses. Benny needs a separately configured and authorized runner, Slack/tracker integrations, and an app control adapter. Missing integrations remain explicit evidence gaps.

### Validate changes

Install PyYAML in your development environment, then run:

```sh
python scripts/validate-skills.py
python scripts/test-install-skills.py
claude plugin validate .
```

The port retains upstream MIT notices under [upstream/](upstream/), with the pinned commit and source file hashes in [pstack-lock.json](upstream/pstack-lock.json).

### Supervised execution and host checks

The bundle now includes a local supervisor for separate CLI workers, repeat-until tasks, detached runs, stop requests, and bounded resume. It saves state and checks the actual artifact instead of accepting an agent's success claim. It does not require a native loop command or provision cloud infrastructure. See [supervised runs](skills/pstack-runtime/references/supervised-runs.md) and [host adapters](skills/pstack-runtime/references/hosts.md) for prerequisites, permissions, and configuration.

Native inventory checks send no model prompts:

```sh
python scripts/check-host-loading.py --agent codex
python scripts/check-host-loading.py --agent opencode
python scripts/check-host-loading.py --agent pi
python scripts/check-host-loading.py --agent claude --claude-init /path/to/private/startup-transcript.jsonl
```

For repeatable behavioral testing, `python scripts/smoke-host.py prepare --agent <agent> --output /tmp/pstack-smoke-<agent>` creates an isolated TDD fixture and supervisor configuration. Preparation uses no model. Review the native host's permissions and configuration before running it; live execution uses that host's authentication and can incur model usage. Verify the artifact with `smoke-host.py verify --project <fixture-project> --transcript <native-jsonl-log>` to check behavior, preserved user files, and failing-before evidence from native tool events.

The supervisor requires Python 3.9+ on a POSIX host. Claude and Codex CLI workers can need launch from a normal terminal rather than an enclosing sandbox. Missing authentication, unsupported host capabilities, and execution limits are explicit non-passes. No permission bypass is added by the adapters.

### Upstream updates

[Track and update upstream](docs/upstream-updates.md) describes the pinned baseline, source comparison, staged three-way merges, mandatory review decisions, validation, and update receipts. `.github/workflows/upstream-check.yml` supplies a weekly read-only check and downloadable review artifacts once Actions is enabled in the published repository. It never applies or publishes updates.

```sh
python scripts/upstream.py check --checkout /path/to/cursor-plugins --fetch --ref origin/main
python scripts/upstream.py stage --checkout /path/to/cursor-plugins --ref origin/main --output /tmp/pstack-review
```

After reviewing every entry and merge candidate, use `upstream.py apply --stage /tmp/pstack-review`. It refuses stale local files and unresolved decisions, preserves intentional divergences, and rolls back validation failures. Run `python scripts/test-upstream.py` and `python -m unittest discover -s skills/pstack-runtime/scripts -p 'test_*.py'` when changing this tooling.
