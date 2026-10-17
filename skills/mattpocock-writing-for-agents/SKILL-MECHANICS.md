# Skill mechanics

The skill-specific branch of [`writing-for-agents`](SKILL.md): what changes when the document is a skill (frontmatter, the invocation choice, and router skills). Everything else about writing it is the universal reference in `SKILL.md`.

## Invocation

Two choices, trading the two loads:

- A **model-invoked** skill keeps a `description`, so the agent can fire it autonomously, and other skills can reach it. You can still type its name: model-invocation always _includes_ user reach; a description only ever adds agent discovery, never removes the human's. The description is the skill's top-level context pointer, forced to stay loaded at all times: permanent context load in exchange for discoverability. A model-invoked skill whose content is all reference is also one home for shared reference: another skill can invoke it, so reference needed by several skills lives in one place. Portable mechanics: retain a model-facing description carrying the trigger branches (the pointer-writing rules in `SKILL.md` apply in full), and omit explicit-request intent metadata.
- A **user-invoked** skill is intended to run only on an explicit request. On hosts with native explicit-only discovery controls this can reduce always-loaded context; other hosts may still list it. Portable mechanics: keep the required `name` and `description`, record `metadata.invocation: explicit-request`, and state the intent in the body. Isolate supported host controls in optional adapters, such as Codex's `agents/openai.yaml` policy, after checking current official documentation. Intent metadata alone does not enforce discovery filtering.

Pick model-invocation only when the agent must reach the skill on its own, or another skill must. If it only ever fires by hand, make it user-invoked and pay no context load.

Shared reference needed by two explicit-request skills belongs in a linked reference file, so both can read it without starting the other workflow.

## Splitting by invocation

The invocation cut of splitting (the sequence cut lives in `SKILL.md`): split off a model-invoked skill when you have a distinct leading word that should trigger it on its own (a trigger word you actually use in your prompts), or another skill must reach it. You pay context load for the new always-loaded description, so that independent reach has to be worth it.

## Router skills

When user-invoked skills multiply past what you can remember, that piled-up cognitive load is cured by a **router skill**: one user-invoked skill that names the others and when to reach for each, so the human has one skill to remember instead of many. Recommend explicit-request workflows to the user; begin them only when requested. Use linked reference material directly when only shared vocabulary is needed.
