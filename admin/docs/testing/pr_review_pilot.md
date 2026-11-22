# iLEAPP PR review on a Mac

GitHub Actions adds the `mac-review` label when a contributor PR opens ready, reopens, becomes
ready, or receives commits while ready. The label means the PR is enrolled. It
stays on the PR after review so a push during delivery cannot lose a signal.
The label contains no findings. The workflow uses base-branch code, never checks
out the PR, and needs only pull-request write access to set the label. Create the label once in
the repository. The fixture bot continues to own fixture requests and labels.

The signed-in user's LaunchAgent checks enrolled open PRs every five minutes and
at login. While the Mac is asleep or offline GitHub retains enrollment. Pickup
reviews the latest ready revision. The worker reads the revision’s workflow path filters
and waits for each applicable PR workflow run to finish, including its matrix jobs.
If an expected workflow is still missing after 15 minutes of polling, the Mac
requests a notification. Local revision tracking skips duplicates. The flag job
runs for every ready contributor PR, including a documentation change with no other checks. Idle checks use the GitHub CLI and Python. Codex starts
only for a revision that needs a review. An interrupted delivery reuses the
saved result. The worker retries failures with backoff.

## Installation

Sign in to GitHub CLI and Codex CLI on the Mac. From a trusted checkout run:

    python3 admin/scripts/install_mac_review.py
    launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/org.ileapp.mac-review.plist"

To stop pickup, run:

    launchctl bootout "gui/$(id -u)/org.ileapp.mac-review"

Rerun the installer after updating the trusted scripts. Reload the LaunchAgent
if its definition changes. Its output goes to the local `pickup.log`.

## Delivery

The Mac requests a notification when it discovers a revision and when the report
is ready. PRs authored by abrignoni skip automated review, including previously
labeled PRs. Contributor review summaries are saved under
`~/Library/Application Support/iLEAPP/PR Review/reports/`. For contributor PRs,
the helper can post verified, new inline findings on the reviewed commit. A
closed, draft, or superseded PR cannot receive a new delivery.

For an optional private Codex inbox, run the installed worker once with
`--inbox-thread <chat UUID>`. It starts with future completed reviews.
The worker records each send attempt before launching Codex. If the worker
restarts after Codex writes its queue receipt, it records the receipt and
continues. A failure to start Codex is retried on a later pass. Other reports
can be delivered while one revision is pending.

If Codex might have accepted a report and the receipt is missing, the Mac
requests a notification and writes the PR number and full SHA to `pickup.log`.
Check the inbox and its pending messages for that revision. If it is present, run

    python3 "$HOME/Library/Application Support/iLEAPP/PR Review/bin/mac_review_worker.py" --resolve-inbox <PR> <FULL_SHA> received

If you confirm the report is absent from both places, use `retry` in place of
`received`. The next worker pass sends it. If you cannot verify the outcome,
leave the revision pending. The local Markdown report remains available.

The reviewer reads the diff, CI outcomes, existing inline feedback, fixture bot
comment and per-module fixture classification. For artifact PRs it includes the
base branch's artifact guidance. The model runs in a temporary directory. The
trusted parent handles GitHub delivery. A touched case or cited image alone
does not establish coverage. Findings requiring an extraction stay in the
private report for local verification.

Treat contributor files as untrusted data. Run contributor code only in an
isolated test environment without access to the signed-in user's credentials,
private corpus, or reports. Keep extraction data and local-only reproduction
details off GitHub even after a finding has been verified. Use a shareable
fixture or public code to explain a confirmed issue to the contributor.
