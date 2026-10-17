# Host execution adapters

Use the current session's native tools first. This reference is only needed when configuring a host or supervising separate CLI workers. Check the installed CLI's `--help` before using optional fields; host interfaces change independently of these skills.

## Claude Code

Load the repository as a plugin with `claude --plugin-dir <checkout>`, or copy skills into `.claude/skills/`. Plugin commands use `/pstack:<name>`; copied skills use `/<name>`. Read sibling SKILL.md files directly when a workflow routes to them. A general native delegate can read `poteto-agent` or another role file; custom agent registration is optional.

For a separate worker, the bundled adapter uses `claude -p --output-format stream-json --verbose --no-session-persistence --permission-mode dontAsk` and sends the brief on stdin. `dontAsk` denies unresolved permission requests; it does not grant them. Preconfigure narrow project permissions or supply reviewed `extraArgs` such as `--allowedTools Read,Edit,Write,Bash(python*)`. It will stop or fail rather than silently bypass permissions. `--model` is only added for a confirmed configured choice. Set a native API budget through `extraArgs` when wanted.

Native background sessions and cloud sessions are optional Claude features, not required by shared skills. Their availability, credentials, costs, and operational approval must be checked separately. [Official CLI reference](https://code.claude.com/docs/en/cli-reference).

## Codex

Copy skills into `.agents/skills/` and invoke `$<name>`, or read the skill path. Native delegation depends on the session's exposed tools and policy. Worker briefs include the role file and checkout; do not assume a particular tool schema or supported model catalog.

The CLI adapter runs `codex exec --ephemeral --sandbox workspace-write --skip-git-repo-check --json -`, with the brief on stdin. It preserves the child's sandbox. A configured model is passed with `--model`; otherwise the CLI uses its configured default, which can differ from the parent session model.

On Linux, launching a sandboxed Codex CLI from inside another Codex sandbox can fail before any command runs because the outer sandbox masks the shared daemon directory. This is a host prerequisite failure, not a reason to disable the child's sandbox. Run the supervisor from a normal terminal or an appropriately authorized outer execution context; report the gap if unavailable. [Official non-interactive documentation](https://developers.openai.com/codex/noninteractive), [reported nested-sandbox issue](https://github.com/openai/codex/issues/53799).

## OpenCode

Copy skills into `.opencode/skills/` and request the skill by name. Native delegation and permissions follow the installed version. Do not add a JavaScript plugin merely to expose ordinary skills.

The CLI adapter uses `opencode run --standalone --format json --file <brief> <instruction>`. No `--auto` permission grant is added. Configure the target project's allowed operations explicitly when an unattended worker needs them. Keep task/agent creation disabled for workers that should not delegate. Confirm model identifiers from this host before supplying `--model`.

For a v2 HTTP loader check, authenticate requests to the private server and wait for plugin activation before reading `/api/skill`. A cold one-shot inventory query can return an empty registry. The repository check script uses the read-only integration inventory as an activation barrier; it does not connect any integration. [Official CLI reference](https://opencode.ai/docs/cli/), [skill discovery](https://opencode.ai/docs/skills/).

## Pi

Copy skills into `.pi/skills/`, or install the root Pi package. Invoke `/skill:<name>`. Base Pi installations need not have a native delegation extension. In that case use serial passes, or explicitly authorized separate CLI workers through the supervisor; separate sessions are not simulated subagents.

The adapter uses `pi --print --mode json --no-session @<brief>`. A configured model uses `--model`; an omitted one uses Pi's configured default. Extensions, MCP servers, trust rules, and tools remain the operator's configuration. Use a controlled project and explicitly reviewed options such as `--no-extensions --no-mcp` for isolated tests. Do not copy credentials into a repository or pretend Pi has a sandbox it does not expose. An OS/container boundary is appropriate for untrusted workers.

Pi's RPC `get_commands` can inspect skill discovery without a model turn. [Official CLI documentation](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/cli.md), [RPC protocol](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/rpc.md).
