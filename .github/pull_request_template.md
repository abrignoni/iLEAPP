## What this changes

<!-- One or two sentences. What does this add, fix or change? -->

## For a new or changed artifact

<!-- Delete this section if the PR does not touch scripts/artifacts. -->

- [ ] Ran the tool against a real extraction and confirmed the row counts, not just that it imports.
- [ ] Ran `python admin/scripts/check_artifact_output.py <report folder>` on that report and **fixed or documented every finding**. An empty or constant column is often a real result (no group chats, coarse location denied); the fix for those is to say so in the artifact's `notes`, which is also what stops the checker reporting them.
- [ ] Checked it against a second app data directory where the platform provides one (a second user, account, or container). `--compare <multi-container report>` reads the scaling for you: it should be exactly double.
- [ ] `notes`, `description` and `sample_data` say only what the data shows, and the numbers were re-derived from the finished run.

## Anything reviewers should know

<!-- Undocumented codes reported as stored, a store that could not be decrypted, a validation gap, etc. -->
