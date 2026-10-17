---
name: mattpocock-claude-handoff
description: Hand the current conversation off to a fresh background agent that picks up the work immediately.
metadata:
  upstream: mattpocock/skills
  upstream-skill: claude-handoff
  stability: in-progress
  invocation: explicit-request
---

Read the [portable runtime contract](../pstack-runtime/SKILL.md) before executing this workflow. Skill names here identify files to read and follow; they do not require a host-specific skill tool. Use [the shared Matt Pocock prerequisites and host fallbacks](../mattpocock-ask-matt/PORTABILITY.md) for delegation, integrations, context changes, and authorization.
Run this workflow when the user explicitly requests it; this is an intent rule, not a claim that every host hides it from automatic discovery.
Input: What will the next session be used for?
Upstream marks this workflow experimental; its interface may change or disappear.

Write a handoff summary to a private, uniquely named file in the OS temporary directory. Start a fresh worker in the current project only when background execution is available and authorized. Use the [portable worker adapters](../pstack-runtime/references/hosts.md) and [bounded supervisor](../pstack-runtime/references/supervised-runs.md) with an explicit completion check, time budget, logs, and stop path. Feed the file as input without evaluating its contents as shell code. Give the worker a descriptive label where supported.

When the host cannot launch or supervise a worker, give the user the handoff path and instructions to seed a fresh session with it. State that no background job was started. The upstream name is retained for traceability; this workflow is usable from all four hosts and does not require Claude's background-agent CLI.

Include a "suggested skills" section in the summary, naming which skills the next agent should read and follow the skill instructions for.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information, since the summary becomes the agent's prompt.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the summary accordingly.
