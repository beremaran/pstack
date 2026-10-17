---
name: mattpocock-git-guardrails-claude-code
description: Set up Claude Code hooks to block dangerous git commands (push, reset --hard, clean, branch -D, etc.) before they execute. Use when user wants to prevent destructive git operations, add git safety hooks, or block git push/reset in Claude Code.
metadata:
  upstream: mattpocock/skills
  upstream-skill: git-guardrails-claude-code
  stability: misc
---

Read the [portable runtime contract](../pstack-runtime/SKILL.md) before executing this workflow. Skill names here identify files to read and follow; they do not require a host-specific skill tool. Use [the shared Matt Pocock prerequisites and host fallbacks](../mattpocock-ask-matt/PORTABILITY.md) for delegation, integrations, context changes, and authorization.

# Git guardrails

Set up a command review rule for pushes and destructive Git operations. First establish the commands the user wants blocked and the project or user scope. Read existing permission settings before making changes.

The bundled [command filter](scripts/block-dangerous-git.sh) accepts JSON on stdin with `tool_input.command`. It needs Bash, `jq`, and standard text tools. It exits 2 for its blocked text patterns and 0 otherwise; it never executes the command. Test with a synthetic `git push origin main` payload (expect 2), and `git status` (expect 0).

On Claude Code, follow the optional [native hook adapter](references/claude-hook.md), merging rather than replacing existing settings. On Codex, OpenCode, or Pi, use the active host's existing permission controls and run this preflight before candidate commands when requested. Without a verified native hook adapter, describe this as an advisory workflow; do not claim automatic interception or equivalent enforcement.

This is a simple text filter, not a comprehensive shell security boundary. Keep ordinary host permission checks active. Complete when the chosen scope and policy are documented, both synthetic checks pass, and any configured native interception has been tested in its actual host. Missing native integration is an explicit limitation.
