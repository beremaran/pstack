# Track and update upstream

The pinned source baseline is `upstream/pstack-lock.json`. It records the source commit, every tracked source file's hash and mode, skill mappings, and local additions. This covers pstack and the entire companion kit, including agents, rules, scripts, manifests, licenses, Benny, documentation, and assets. Changes to material we did not copy still appear for dependency and portability review.

The read-only GitHub workflow `.github/workflows/upstream-check.yml` runs weekly or on manual dispatch once this repository is published with Actions enabled. It compares the current upstream main branch, stages a review artifact when changes exist, and marks the job failed so updates are visible in ordinary Actions status/notifications. It does not create issues or PRs, modify files, or advance the source baseline. This workflow file was checked locally; no hosted workflow has been triggered from this session.

## Check locally

Use Python 3.9+ and git. Clone upstream into a separate directory; keep this checkout independent of upstream's working tree.

```sh
git clone --filter=blob:none --sparse https://github.com/cursor/plugins.git /tmp/pstack-upstream
git -C /tmp/pstack-upstream sparse-checkout set pstack cursor-team-kit
python scripts/upstream.py check --checkout /tmp/pstack-upstream --fetch --ref origin/main
```

`--fetch` updates only that source clone. Without it, the command compares the locally known ref, which can be stale. `--fail-if-changed` returns exit 3 for a nonempty report and can be used with a scheduler. Exit 1 means the comparison itself failed, not “no updates.” The report contains source paths, hashes, modes, additions/deletions, and canonical targets. The pinned source objects must remain available for three-way merges; fetch the recorded base commit if using a shallow clone.

## Stage without changing our skills

```sh
python scripts/upstream.py stage --checkout /tmp/pstack-upstream --ref origin/main --output /tmp/pstack-review
```

The output directory must be new. It contains:

- `plan.json`: changes, target paths, pre-update local hashes/modes, review decisions, source versions, and any declared dependencies.
- `base/` and `incoming/`: upstream evidence from the pinned and proposed commits.
- `ours/` and `merged/`: current port content and three-way merge candidates where applicable.

A clean merge preserves nonconflicting port adaptations. A conflict needs manual resolution. New skills/resources need portability review; they are not installed just because they were added upstream. Deletions are never performed automatically. Aggregated companion rules, host manifests, README/guide changes, and other unmapped files require explicit review instead of a blind text merge.

Source manifests and README changes can introduce dependencies that are only named in prose. Trace those references recursively before accepting an update. A newly required plugin outside the two tracked packs requires extending the mapping/inventory and porting it. The tool does not claim to infer an arbitrary prose dependency graph.

## Review and apply

For every `plan.json` entry:

1. Inspect the base, incoming content, current port, and merge candidate. Preserve capability-based instructions, sibling resource paths, runtime contract, user authorization, and host adapters.
2. Edit the corresponding `merged/` file into its final portable form. Resolve conflict markers. Review changed scripts, executable modes, credentials, and integration prerequisites. Do not execute incoming scripts just to inspect an update.
3. Set `decision` to `accept`, `keep`, or `delete`, and write a concrete `reason`. Even clean merges need a reason. An unmapped entry must use `keep` with the review result. Use `delete` only for an upstream deletion after checking local callers. `keep` records a deliberate local divergence while advancing the reviewed source baseline.
4. Check any new skill directory, name, resources, and dependency links. Required new upstream skills must exist in the resulting port. Retaining a removed upstream skill is permitted, but record why it remains local.

Then apply the reviewed stage:

```sh
python scripts/upstream.py apply --stage /tmp/pstack-review
```

Only one apply can run at a time; its temporary lock stays outside the repository. Inspect an interrupted update before removing a stale lock. A forced process kill or machine failure still requires inspecting the diff before retrying.

Apply refuses pending decisions, missing reasons, unresolved conflicts, changed local files/modes, a changed source lock, missing required skills, and unsupported source modes. It validates the resulting portable skill tree before advancing the lock. A validation failure restores changed file contents/modes and the previous lock. The command does not commit, push, execute imported scripts, or run agent model turns.

A successful update writes `upstream/updates/<commit>.json` with the source transition and per-file review decisions. Keep that receipt with the adapted changes. It explains what was accepted, kept, or deleted even after the baseline moves forward.

## Verify the updated port

Run the structural validator, installation checks, updater tests, supervisor tests, and affected bundled script tests. Run native inventory checks on available hosts and behavioral tests appropriate to changed workflows. Record versions and the distinction between a loader check, fixture-backed execution, and a live model workflow in `docs/pstack-verification.md`. Publish changes only through the repository's normal reviewed process.

## Additional source: Matt Pocock

The same commands support `--source mattpocock` for [the Matt Pocock vendor](mattpocock-port.md). Omit the flag for the existing pstack behavior. Use a separate source checkout and fresh staging directory for each repository:

```sh
python scripts/upstream.py check --source mattpocock --checkout /path/to/mattpocock-skills --fetch
python scripts/upstream.py stage --source mattpocock --checkout /path/to/mattpocock-skills --output /tmp/mattpocock-review
python scripts/upstream.py apply --source mattpocock --stage /tmp/mattpocock-review
```

The baseline is `upstream/mattpocock-lock.json`; it tracks the entire upstream repository. Skill paths `skills/<category>/<name>/...` map to `skills/mattpocock-<name>/...`; licenses have a distinct notice. All other changes are explicit review entries. Preserve the namespace and portability adaptations when merging. The plan records source package version/development dependency metadata as evidence, not instructions to install those packages.

Source identity is stored in each stage; applying it under another source is refused. Both sources share the same apply lock, so updates cannot write concurrently. Validation checks all source inventories for duplicate ownership. Receipts for this source live under `upstream/updates/mattpocock/`; pstack's receipt paths and commands remain unchanged. Weekly Actions uses a two-source matrix with independent failures and named artifacts. This workflow extension has been checked locally; it has not yet been published or executed on GitHub.
