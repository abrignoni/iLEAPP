<!-- SHARED FILE. Canonical copy lives in leapps-org/leapps-parity. Do not edit in place;
     edit the canonical copy and re-run the sync script, or your change will be overwritten. -->

# Fixes do not propagate between cores

iLEAPP, ALEAPP, RLEAPP, VLEAPP and DLEAPP carry independent copies of many artifacts. A fix
in one does not reach the others. The stale copy keeps shipping the defect, and an examiner
running that tool gets output the fixed tool no longer produces.

**After fixing an artifact in one core, check the others for the same app.** Grep the
sibling repos for the filename and for the app's package or bundle identifier.

The twin is rarely identical. Same defect, different line numbers, sometimes extra defects
the first copy never had. Read it; do not blind-copy the patch. Check the reverse direction
too: a defect found in one core may exist unfixed in the one you consider canonical.

Apps known to exist in more than one core: swissmeteo, waze, sbbmobile, tikTok, chatgpt,
c2paProvenance, dmss, hikvision, discord\*, cashApp, googleDuo, googleChat, gmail, chrome\*,
firefox\*, torrent\*, teams, viber, whatsApp, signal\*, mastodon, groupMe, bumble, burner\*,
walStrings, kijiji, kleinanzeigen, protonmail, meWe/mewe, line, imo, life360/L360\*.

The **"Needs Cross Core Leveling"** label exists for this. Apply it when a change should
propagate, but do the grep yourself rather than relying on the label being actioned later.

The same applies to shared infrastructure, not just artifacts: `scripts/lavafuncs.py`,
`scripts/html_safe.py`, `scripts/ilapfuncs.py` and the `admin/` checkers are meant to stay
in step across cores. `leapps-org/leapps-parity` scans for exactly this kind of drift.

## Verify against the remote, not your checkout

Never read cross-core status off a local working copy. Clones go stale, and a filesystem
check on a three-day-old tree will report a helper missing from three repos when it shipped
to all five. Fetch first, or query the remote directly.

Likewise, a branch that no longer exists is not lost work. Merged branches are deleted here.
Check `git log --oneline -- <path>` and `gh pr list --state all` before concluding anything
vanished.
