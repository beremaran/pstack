### Autonomous run

**You own the exit condition. Define done, then drive to it without stopping.**

1. State the exit condition as a checkable predicate before the first iteration (tests green, repro fixed, all N PRs merged, pixel-diff zero).
2. Pick a supported wake mechanism. In a live session, use a bounded repeat-until loop and a native watcher when available. To continue beyond the parent terminal, read [supervised runs](../../pstack-runtime/references/supervised-runs.md) and configure the bundled supervisor with a real done check, explicit attempt/deadline bounds, a brief, and a dedicated checkout. Native cloud or scheduled execution is optional. If no persistent runner is available, state that execution ends with this session. Never promise a wakeup mechanism that was not started and verified.
3. Each iteration makes the smallest change the evidence justifies, verifies it against the predicate, commits if it advanced, discards changes that didn't help. Belt-and-suspenders that "might help" gets reverted, not left to ride.
   Sequence the work via the **sequence-verifiable-units** principle skill, verifying each unit before the next instead of batching checks at the end.
4. Mid-run discoveries are yours. Address broken skills, related bugs, flaky verifiers, review noise, tooling failures, orphaned follow-ups, and fixable drift yourself via poteto-mode. Put out-of-band fixes in their own PR. Do not park reversible work for the human or use a structured question, or plain text if unavailable. Surface only irreversible actions, genuine product or preference calls no experiment can settle, or a real dead end. Keep the predicate as the main drive, and return to it after each side fix.
5. Checkpoint every iteration via the **show-me-your-work** skill, a row for what changed and whether the predicate moved.
6. Stop when the predicate is met. Within the declared attempt and time bounds, pivot when progress plateaus. On budget exhaustion, record the unmet predicate and stop. Surface a genuine dead end rather than spinning, and never relax the predicate to declare victory.

**Reply:** the exit condition, iterations run, what landed, what was discarded, final predicate state.
