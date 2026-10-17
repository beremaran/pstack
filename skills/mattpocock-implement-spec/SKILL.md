---
name: mattpocock-implement-spec
description: Implement the result of mattpocock-to-spec and mattpocock-to-tickets in code.
metadata:
  upstream: mattpocock/skills
  upstream-skill: implement-spec
  stability: engineering
  invocation: explicit-request
---

Read the [portable runtime contract](../pstack-runtime/SKILL.md) before executing this workflow. Skill names here identify files to read and follow; they do not require a host-specific skill tool. Use [the shared Matt Pocock prerequisites and host fallbacks](../mattpocock-ask-matt/PORTABILITY.md) for delegation, integrations, context changes, and authorization.
Run this workflow when the user explicitly requests it; this is an intent rule, not a claim that every host hides it from automatic discovery.

Bundled companion workflows: [mattpocock-code-review](../mattpocock-code-review/SKILL.md), [mattpocock-setup-matt-pocock-skills](../mattpocock-setup-matt-pocock-skills/SKILL.md), [mattpocock-tdd](../mattpocock-tdd/SKILL.md), [mattpocock-to-spec](../mattpocock-to-spec/SKILL.md), [mattpocock-to-tickets](../mattpocock-to-tickets/SKILL.md).

You have been provided a spec. This spec should have tickets associated with it, describing how to implement the spec.

The issue tracker should have been provided to you. If not, tell the user to run `mattpocock-setup-matt-pocock-skills`.

The goal is the entire spec implemented on a single **integration branch**, with every ticket resolved the way the issue tracker closes work.

The tickets are not a list of steps. They are a **task graph** with blocking relationships between them. This means there is always a **frontier** of tickets which are ready to be grabbed.

Communication to and from subagents should be sparse. Communicate primarily through **context pointers**: to the spec, tickets, research notes, and previous commits. Don't duplicate information already available via pointers.

**Implementer subagents** should be run in the background where possible for maximum concurrency.

## Steps

1. Read the spec and tickets to understand the task graph.

2. (optional) Use an **exploration subagent** to conduct any exploration required by the tickets - relevant codebase files or external documentation. Ensure the exploration subagent can save files - it should save its markdown notes in a directory outside the repo, accessible by all future subagents. This lets **implementer subagents** focus on implementation rather than exploration.

3. Create the integration branch. If the issue tracker closes work through PRs, or the user asks for one, open a draft PR after the first merge in step 5 (a branch with no commits ahead of main can't open one), marked as closing the spec and tickets.

4. Use **implementer subagents** to implement each ticket, each in its own worktree on its own branch. Each implementer subagent:
   - confirms its worktree is based on the integration branch before starting, and resets onto it if not;
   - reads and follows the skill instructions for `mattpocock-tdd` to build the ticket;
   - merges the integration branch tip into its own branch before reporting done

5. Once an **implementer subagent** completes, merge its work to the integration branch with a **merger subagent**.

6. If this changes the **frontier** of available tickets, kick off more **implementer subagents** to work on the new tickets. This allows for maximum concurrency.

7. Once all tickets are complete, read and follow the skill instructions for `mattpocock-code-review` on the integration branch. Fix all issues raised by the code review in a single **implementer subagent**.

8. If a draft PR exists, mark it ready for review. Otherwise, resolve each ticket the way the issue tracker closes work, and report the integration branch.

9. Clean up all **implementer subagent** worktrees.
