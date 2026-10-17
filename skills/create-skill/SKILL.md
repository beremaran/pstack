---
name: create-skill
description: Create or revise a portable Agent Skills workflow with clear triggers, bundled resources, and verification. Use when pstack routes to skill authoring or the user asks to create or improve a skill.
---

# Create a skill

Read [pstack runtime](../pstack-runtime/SKILL.md). This replaces the upstream host's built-in authoring capability.

1. Identify the task, inputs, decisions the skill changes, and observable completion criteria. Use repository instructions and real examples. Ask only for missing intent that affects the result.
2. Keep one canonical directory `skills/<name>/` with `SKILL.md`. Use lowercase kebab-case of at most 64 characters matching the directory. In a destination project, preserve its canonical convention and install or link into the active host's discovery directory.
3. Start with YAML `name` and a scalar `description` of at most 1024 characters stating when to use it. Quote punctuation safely. Use common Agent Skills fields; isolate optional host metadata. Keep automatic discovery unless the user requests explicit-only use; document host differences.
4. Write actionable steps and decision criteria adding task-specific knowledge. State runtime, CLI, credential, integration, and delegation prerequisites with fallbacks. Avoid hardcoded host APIs and machine-local paths. Preserve user scope and authorization.
5. Bundle scripts, references, and assets when they improve execution. Link relative to the skill directory and say when to read them. Put substantial conditional detail behind references. Maintain one source per instruction.
6. Check YAML parsing, name/directory agreement, local links, portability, secrets, and unfinished scaffolds. Run script syntax checks and a safe representative invocation where runtimes exist. Exercise realistic tasks in isolation when authorized. Distinguish format review from host execution.
7. Deliver the skill with checks, limitations, and agents actually exercised. Publishing, installing outside scope, and opening PRs follow user authorization.
