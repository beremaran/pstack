---
name: setup-pstack
description: Configure pstack role models and reasoning budget for the current agent and project. Use for setup-pstack, configure pstack models, pstack budget, or changing model choices.
---

# Setup pstack

Read [pstack runtime](../pstack-runtime/SKILL.md).

1. Identify the host and its supported worker model choices from the current session or its documented model listing. Do not infer access from a provider's public model catalog. If no enumeration is available, use `inherit-parent`; the user can supply confirmed identifiers later. Do not install a provider or change the session model.
2. Read `<project>/.pstack/models.md` if present. Preserve existing role choices unless the user asks to change them. This is explicit workflow configuration, not an automatically applied host rule. Every bundled skill reads it through the runtime contract.
3. Ask for a budget if unspecified: unlimited (highest supported reasoning), large, medium, or small. Explain which reasoning controls the current host actually supports. Treat a missing control as unavailable, not as an invented model suffix.
4. Present the role table, models, panel seat counts, supported reasoning options, and any unavailable configured models. Confirm any unresolved preference. Defaults use the parent session model; panel defaults have two seats, which gives distinct attempts without promising model diversity. Keep user-approved model families when adjusting reasoning. Do not silently replace an unavailable configured model with another family.
5. Write the reviewed table to `<project>/.pstack/models.md`, scoped to this host. Preserve other hosts' sections if the file contains them. Use this shape with confirmed choices replacing aliases only where supported:

```text
# pstack models
# host: <current agent>
# budget: large; reasoning: <supported value or unavailable>
feature, refactoring: inherit-parent
bug-fix: inherit-parent
perf-issue: inherit-parent
hillclimb: inherit-parent
judgment and prose: inherit-parent
hardest tasks: inherit-parent
how explorer: inherit-parent
how explainer: inherit-parent
why investigators: inherit-parent
why synthesizer: inherit-parent
reflect tooling: inherit-parent
reflect judgment, divergent, synthesizer: inherit-parent
arena runners: inherit-parent, inherit-parent
arena cross-judge pool: inherit-parent, inherit-parent
swarm workers: inherit-parent
architect runners: inherit-parent, inherit-parent
interrogate reviewers: inherit-parent, inherit-parent
```

6. Verify every real model identifier against the host's available choices. Report the file and any controls that could not be mapped. Changes apply the next time a workflow reads this configuration, including the current session.
7. If the project lacks a real-app harness, mention [create-verification-skill](../create-verification-skill/SKILL.md) once. Generate it only when requested.
