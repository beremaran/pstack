---
name: mattpocock-handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
metadata:
  upstream: mattpocock/skills
  upstream-skill: handoff
  stability: productivity
  invocation: explicit-request
---

Read the [portable runtime contract](../pstack-runtime/SKILL.md) before executing this workflow. Skill names here identify files to read and follow; they do not require a host-specific skill tool. Use [the shared Matt Pocock prerequisites and host fallbacks](../mattpocock-ask-matt/PORTABILITY.md) for delegation, integrations, context changes, and authorization.
Run this workflow when the user explicitly requests it; this is an intent rule, not a claim that every host hides it from automatic discovery.
Input: What will the next session be used for?

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save to the temporary directory of the user's OS (`$TMPDIR`, else `/tmp`; `%TEMP%` on Windows) - not the current workspace.

Include a "suggested skills" section in the document, naming which skills the next agent should read and follow the skill instructions for.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
