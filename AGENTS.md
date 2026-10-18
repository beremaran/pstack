# Repository guidance

This repository packages the pstack bundle for general use. Every shared skill must work with Codex, Claude Code, OpenCode, and Pi.

## Structure

- Keep each skill's canonical source in `skills/<name>/SKILL.md`, directly under `skills/`.
- Use lowercase kebab-case names. Match the directory name to the frontmatter `name`.
- Give every skill YAML frontmatter with `name` and `description`. Describe the situations that should trigger it.
- Keep optional scripts, references, and assets inside the skill directory. Resolve their paths relative to that directory.
- Keep shared repository instructions here. `CLAUDE.md` directs Claude Code to this file.

## Portability

- Write the shared workflow in ordinary Markdown using the common Agent Skills format.
- Describe required capabilities by purpose rather than assuming a particular agent's tool names, slash commands, hooks, plugins, or subagent APIs.
- When a workflow needs a specific CLI, integration, runtime, or credential, state the prerequisite and how to proceed when it is unavailable.
- Isolate optional agent-specific metadata and adapters from the shared workflow. Document their scope and preserve a usable path for all four agents.
- Maintain one source per skill; hosts load the canonical `skills/` tree through their native package mechanisms, or receive a copy in their discovery directory.
- Verify current official documentation before changing discovery paths or claiming support for an agent-specific feature.

## Authoring and verification

- Make instructions actionable, with clear inputs, steps, and completion criteria. Keep lengthy or conditional reference material in linked files.
- Use relative links for bundled resources and placeholders for user-specific paths. Keep secrets and machine-local state outside the repository.
- For a skill change, check frontmatter, directory/name agreement, bundled links, and every affected portability assumption.
- For scripts, run appropriate syntax checks and a representative safe invocation when the required runtime is available.
- Report which agents were actually exercised. Distinguish format review from runtime verification; compatibility is a requirement, not evidence that all four agents were tested.
