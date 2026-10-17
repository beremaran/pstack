---
name: mattpocock-implement
description: Implement a piece of work based on a spec or set of tickets.
metadata:
  upstream: mattpocock/skills
  upstream-skill: implement
  stability: engineering
  invocation: explicit-request
---

Read the [portable runtime contract](../pstack-runtime/SKILL.md) before executing this workflow. Skill names here identify files to read and follow; they do not require a host-specific skill tool. Use [the shared Matt Pocock prerequisites and host fallbacks](../mattpocock-ask-matt/PORTABILITY.md) for delegation, integrations, context changes, and authorization.
Run this workflow when the user explicitly requests it; this is an intent rule, not a claim that every host hides it from automatic discovery.

Bundled companion workflows: [mattpocock-code-review](../mattpocock-code-review/SKILL.md), [mattpocock-tdd](../mattpocock-tdd/SKILL.md).

Implement the work described by the user in the spec or tickets.

If the user passes a ticket reference, fetch it from the issue tracker and state its title before starting. If the reference is ambiguous, ask.

read and follow the skill instructions for "mattpocock-tdd" where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, read and follow the skill instructions for "mattpocock-code-review" to review the work.

Commit your work to the current branch.
