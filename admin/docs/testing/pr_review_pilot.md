# iLEAPP PR review on a Mac

GitHub Actions adds the `mac-review` label when a PR opens ready, reopens, becomes
ready, or receives commits while ready. The label means the PR is enrolled. It
stays on the PR after review so a push during delivery cannot lose a signal.
The label contains no findings. The workflow uses base-branch code, never checks
out the PR, and needs only pull-request write access to set the label. Create the label once in
the repository. The fixture bot continues to own fixture requests and labels.

The signed-in user's LaunchAgent checks enrolled open PRs every five minutes and
at login. While the Mac is asleep or offline GitHub retains enrollment. Pickup
reviews the latest ready revision. Local revision tracking skips duplicates and
waits for running CI. Idle checks use the GitHub CLI and Python. Codex starts
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
is ready. Findings on owner-authored PRs stay in private Markdown files under
`~/Library/Application Support/iLEAPP/PR Review/reports/`. For contributor PRs,
the helper can post verified, new inline findings on the reviewed commit. A
closed, draft, or superseded PR cannot receive a new delivery.

The reviewer reads the diff, CI outcomes, existing inline feedback, fixture bot
comment and per-module fixture classification. For artifact PRs it includes the
base branch's artifact guidance. The model runs in a temporary directory. The
trusted parent handles GitHub delivery. A touched case or cited image alone
does not establish coverage. Findings requiring an extraction stay in the
private report for local verification.
