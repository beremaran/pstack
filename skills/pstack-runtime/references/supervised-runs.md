# Supervised runs

Use this when the user authorizes separate agent processes, repeat-until work, or an unattended run. It provides a local alternative to native loops and cloud workers. It does not provision cloud machines, publish anything, or replace a service's credentials and event triggers.

## Prerequisites and scope

Use Python 3.9+ on a POSIX host, the selected agent CLI on PATH, its normal authentication, and a project with this skill bundle installed. Unix process groups and `fcntl` provide cancellation and single-owner locking. On Windows, use a POSIX environment such as WSL or native host execution without this supervisor. Run from a terminal or runner that permits the selected child's own sandbox; see [host adapters](hosts.md).

One writer owns each checkout. Give parallel writers separate worktrees and separate state directories. A verifier receives the implementation commit and evidence, not permission to edit it. Separate sessions provide context separation; model diversity requires explicitly confirmed different models. Do not call self-review independent verification.

## Prepare the run

Write a task brief naming goal, role SKILL.md path, exclusive checkout, allowed files and actions, constraints, verification commands, and expected report. Preserve the original brief through all retries. Secrets stay in the host's normal credential store or environment, never the brief or configuration.

Write a JSON configuration, using actual project-relative paths and an independent done check. Example, with the config at `<project>/.pstack/run.json` and brief beside it:

```json
{
  "agent": "codex",
  "project": "..",
  "brief": "brief.md",
  "check": ["python", "-m", "unittest", "discover", "-v"],
  "maxAttempts": 3,
  "maxSeconds": 1800,
  "iterationSeconds": 300,
  "intervalSeconds": 10
}
```

Paths in `project` and `brief` are relative to the config file. Put state under the target checkout, such as `<project>/.pstack/runs/<id>/state/`, so workers can read the failing-check pointer without gaining unrelated filesystem access. A config under `.pstack/runs/<id>/` needs `project: "../../.."`; calculate it from the actual location rather than copying this example blindly.

`model`, `executable`, and `extraArgs` are optional native adapter choices. Confirm model availability and review extra arguments. No model override means the CLI's own configured default, not guaranteed inheritance from the parent. Resolve a role's `inherit-parent` choice to a confirmed actual model ID before supplying it, or omit the override and disclose the CLI default; the runner rejects literal parent aliases. The adapter does not disable permissions or sandboxes. Claude denies unresolved permissions; configure narrow authorized operations before expecting writes. The operator remains responsible for the chosen CLI's own settings, hooks, extensions, credentials, and security boundary.

## Run, observe, stop, resume

Run by absolute installed script path:

```sh
python <installed-runtime>/scripts/run.py run --config <config.json> --state <state-dir>
python <installed-runtime>/scripts/run.py status --state <state-dir>
python <installed-runtime>/scripts/run.py stop --state <state-dir>
```

The supervisor runs the done check first. If it fails, it starts a fresh worker with the original brief plus the previous check's log path. It checks the artifact after each successful worker exit, including the last permitted attempt. Only an actual zero exit from the check means passed. A worker's claim or zero exit alone is insufficient. Authentication failures, denied permissions, CLI errors, check timeouts, and worker timeouts stop the run instead of consuming unbounded retries.

State and logs are local with restrictive permissions. Inspect `status` rather than reading raw transcripts into a coordinator. They can contain private project evidence; keep them out of source control and shared reports. Exit 0 means passed; exit 1 is a bounded non-pass; exit 2 is invalid configuration or an execution prerequisite failure.

For an authorized detached run, launch that same command from a normal terminal under `nohup` or an existing OS service, redirecting its output into a private local log. The process can then outlive the parent terminal. No service is installed automatically. A reboot or forced process kill needs an explicit restart of the same command, or a separately approved OS service policy.

Resume with the same config and state directory. Deadlines and attempt counts do not reset, and changed configuration or brief requires a fresh state directory. An interrupted attempt remains in the record. A live orphan worker blocks resume; inspect it before restarting rather than creating a second writer. After a requested stop, inspect the project and remove the local `stop` marker only when intentionally resuming. A previously passed run is a historical result; use a fresh run for a new verification claim.

For multi-day programs, keep standing orders, briefs, units, and verdicts in the existing `orch` store. The coordinator can launch one supervised process per authorized unit and collect its state and artifact pointers. The supervisor supplies execution and bounds; it does not merge branches, approve shipping, or impersonate a missing independent verifier. Remote execution uses a user-provisioned host with the same checkout and prerequisites; no proprietary cloud API is assumed.
