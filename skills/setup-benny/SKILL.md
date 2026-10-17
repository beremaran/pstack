---
name: setup-benny
description: Configure Benny issue-report triage and bounded reproduce-and-fix workflows with a chosen automation runner, Slack integration, tracker, and real-app harness.
---

# Setup Benny

Read [pstack runtime](../pstack-runtime/SKILL.md). Benny is two workflows: [triage](../triage-issue-reports/SKILL.md) and [reproduce and fix](../reproduce-and-fix-issues/SKILL.md). They may run manually or under a user-selected scheduler/event runner. No host-specific automation service is assumed.

## Install and configure

1. Identify the target repository and runner. Install the entire portable bundle in project scope using the repository installer or committed canonical skills with discovery links. Verify that a fresh runner checkout can resolve the operational skill files, `how`, `why`, `tdd`, `unslop`, and required `principle-*` skills. User-scoped caches do not prove project readiness.
2. Preserve local edits on refresh. Review conflicts at source-managed paths and preserve destination-only files. Store user-owned configuration, feature maps, and routing maps outside skill directories, for example `.pstack/benny/`. Keep secrets in environment variables or a secret manager.
3. Copy [configuration.example.yaml](templates/configuration.example.yaml), [feature-map.example.md](../reproduce-and-fix-issues/references/feature-map.example.md), and, if needed, [routing.example.md](../triage-issue-reports/references/routing.example.md) to user-owned paths. Replace every relevant placeholder. Commit only secret-free configuration when a fresh automation checkout needs it.
4. Establish source Slack channel ID, optional operations channel, repository/default branch, triage identity, tracker adapter/team/project/labels/status, control skill, feature-map path, status markers, PR URL format, time/retry/fix budgets, and supported models. Use only confirmed models or inherit the runner's model. Fail setup if channel, identity, repository, tracker, control adapter, or feature map is ambiguous.
5. Check actual integration capabilities. Triage needs scoped thread reads/replies, attachment access, and tracker search/read/create/update. Repro needs thread reads/replies, optional operations message edits, repository/history access, draft PR creation, tracker access, and the control adapter. The optional `BENNY_SLACK_BOT_TOKEN` may fill a narrow configured capability gap; never expose it to workers.
6. Fill the feature map for every supported user journey. Read [control-adapter.md](../reproduce-and-fix-issues/references/control-adapter.md). Verify real app launch, navigation, actions, read-only inspection, screenshots, recordings, and cleanup. Leave repro disabled when evidence capabilities are missing.
7. Configure routing only from explicit entries; leave owner pings off by default. A configured owner or confirmed regression author may be pinged only within the authorized workflow. Without routing, classify without guessing a destination.

## Prepare the runner

Ask whether the user wants first-time creation or edits to existing jobs. Drafts alone do not authorize activation. Do not create duplicate automations.

Adapt [triage prompt](templates/triage-automation-prompt.md) and [repro prompt](templates/reproduce-automation-prompt.md). Use stable committed paths verified in the runner's actual checkout. The templates' `skills/...` paths assume the canonical tree is committed at that location; replace them with actual project-relative installed paths when it is not. Avoid user home directories and plugin cache paths. Apply `unslop` to names, descriptions, and prompts.

Configure two jobs, one at a time:

- Triage triggers on a new top-level report in the configured channel. Keep source channel and root thread coordinates immutable. Search for duplicates, update a confident duplicate, create only clear net-new bug tickets, and post exactly one thread verdict with `[benny:bug]`, `[benny:performance]`, or `[benny:other]`. Never post a root source-channel message.
- Repro receives the same report, waits within budget for a marker from the trusted triage identity, checks existing ownership/fixes, reproduces the exact symptom twice with evidence, and attempts at most one bounded root-cause fix. Verify existing PRs rather than competing with them. Open a draft PR only after before/after proof. Never merge or deploy.

Workers may assist but receive no Slack credentials or write capability. Utility bots provide evidence, not ownership. Missing coordinates, tracker, control adapter, or feature map must fail closed.

If the runner lacks event triggers, provide manual invocation instructions and leave scheduling unconfigured. If it cannot enforce thread-only messaging or credential isolation, leave the jobs disabled. Use only its documented configuration interface. Creating, editing, posting, or activating a job requires explicit user authorization; this setup workflow does not supply it.

## Verify before activation

Confirm the runner revision contains the installed skills, discovery configuration if needed, and all referenced secret-free files. Run the following only in an authorized test channel with a harmless report:

1. Triage stores the root `thread_ts` and posts exactly one reply with a configured marker.
2. Repro accepts only the configured triage identity's marker and retains immutable source coordinates.
3. No root message appears in the source channel.
4. Delegated workers cannot use Slack writes or access its credentials.
5. Missing coordinates, a deleted parent, or preflight failure produces no post or tracker issue.
6. Existing ownership/fixes prevent a competing change, and failed evidence prevents a draft PR.

Enable normal traffic only after all checks pass and activation is authorized. Report configured files, runner capabilities, tests actually performed, and outstanding blockers. Do not claim a live automation exists from prompt preparation alone.
