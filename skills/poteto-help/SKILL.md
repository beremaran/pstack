---
name: poteto-help
description: Explain pstack setup and select the appropriate skill, playbook, or principle. Use for poteto-help or questions about using the portable pstack bundle.
---

# Poteto help

Read [pstack runtime](../pstack-runtime/SKILL.md). Answer help questions without starting the described work. A request to perform work routes to the relevant skill instead.

For installation, use the repository's installation documentation. This port supports common skill discovery in Claude Code, Codex, OpenCode, and Pi, plus optional Claude plugin and Pi package metadata. It does not require custom modes or a native loop command. Say “use the poteto-mode skill” when host command syntax is unknown.

For model setup or cost questions, read [setup-pstack](../setup-pstack/SKILL.md). Defaults inherit the current session model. Model diversity, background work, and delegation depend on the current host and authorization. Without delegation, serial self-review is available, but cannot satisfy independent shipping verification.

Read [poteto-mode](../poteto-mode/SKILL.md) for its playbook index. It covers investigation, bugs, performance, runtime/trace forensics, features, refactoring, prototypes, visual parity, skill authoring/evaluation, PR babysitting, shipping, autonomous work, orchestration, autopilot, pickup, pausing, plans, and worktree cleanup. Ask for that mode explicitly at the start of a new task; do not promise persistence after host context loss.

Choose a direct skill when a narrower task fits:

| Need | Skill |
| --- | --- |
| Explain current behavior or reasons | [how](../how/SKILL.md), [why](../why/SKILL.md), [teach](../teach/SKILL.md) |
| Rebuild recent context | [recall](../recall/SKILL.md), [ketchup](../ketchup/SKILL.md) |
| Sharpen intent | [sharpen](../sharpen/SKILL.md), [in-your-own-words](../in-your-own-words/SKILL.md) |
| Explore design or alternatives | [architect](../architect/SKILL.md), [arena](../arena/SKILL.md) |
| Partition checks or adversarial review | [swarm](../swarm/SKILL.md), [interrogate](../interrogate/SKILL.md), [blast-radius](../blast-radius/SKILL.md) |
| Verify behavior | [tdd](../tdd/SKILL.md), [control-ui](../control-ui/SKILL.md), [control-cli](../control-cli/SKILL.md), [benchmark-checklist](../benchmark-checklist/SKILL.md) |
| Build or maintain app verification | [create-verification-skill](../create-verification-skill/SKILL.md), [maintain-verification-skill](../maintain-verification-skill/SKILL.md) |
| Improve code or prose | [deslop](../deslop/SKILL.md), [no-comments](../no-comments/SKILL.md), [unslop](../unslop/SKILL.md), [technical-writing](../technical-writing/SKILL.md) |
| Record or improve workflows | [show-me-your-work](../show-me-your-work/SKILL.md), [reflect](../reflect/SKILL.md), [correct](../correct/SKILL.md), [automate-me](../automate-me/SKILL.md), [create-skill](../create-skill/SKILL.md) |
| Configure issue automations | [setup-benny](../setup-benny/SKILL.md) |
| Build bot controls | [make-bot-ui](../make-bot-ui/SKILL.md) |

For other skills, inspect sibling frontmatter. `principle-*` skills are read when their rule applies, not all at once. Use [prompting](references/prompting.md) and [recipes](references/recipes.md) for examples; `/name` there denotes skill loading through the active host.

If a run drifts, check which skill was actually loaded, the done predicate, host capability gaps, checkout isolation, and real verification evidence. Give one concrete steer. Keep the answer short, with a path to the relevant skill and at most one example prompt.
