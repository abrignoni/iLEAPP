---
name: leapp-sweep-siblings
description: After fixing an artifact in one LEAPP core, find and fix the same defect in the sibling cores. Use when a fix has just landed or is about to, when asked to "level" a change across cores, or when checking whether a defect found in one tool exists in the others.
---

<!-- SHARED SKILL. Canonical copy lives in leapps-org/leapps-parity under skills/.
     Do not edit in place; edit the canonical copy and re-run the sync script. -->

# Sweeping sibling cores after a fix

iLEAPP, ALEAPP, RLEAPP, VLEAPP and DLEAPP carry independent copies of many artifacts. A fix
in one does not reach the others, and the stale copy keeps shipping the defect to examiners.

## 1. Update every checkout first

A local clone that is days behind will tell you a fix is missing when it already shipped, or
that a file is clean when it is not. Fetch before you look, or query the remotes directly.

## 2. Find the twins

Grep each sibling for the artifact filename **and** for the app's package or bundle
identifier. The filename alone misses copies that were renamed, and the identifier alone
misses modules that handle several apps.

The `leapp-cross-core` rule lists app names already known to exist in more than one core.
Treat it as a starting point, not the full set.

## 3. Read each twin before touching it

The copies drift. Expect the same defect at different line numbers, and expect extra defects
the original never had. Do not apply the patch blind.

Check the reverse direction too. A defect you found in one core may exist unfixed in the one
you think of as canonical.

## 4. Fix each one on its own branch and PR

One PR per repo. Each core has its own CI, its own lint debt and its own reviewers.

Apply the **"Needs Cross Core Leveling"** label when a change should propagate but you are
not doing all of them now. Do the grep yourself rather than trusting the label to be
actioned later.

## 5. Verify per core, not once

Row counts differ between cores because the underlying app data differs. Confirm each fix
against data for that platform. A count that matches the other core is a coincidence worth
questioning, not a confirmation.

## Shared infrastructure counts too

The same drift applies to `scripts/lavafuncs.py`, `scripts/html_safe.py`,
`scripts/ilapfuncs.py` and the `admin/` checkers, which are meant to stay in step across
cores. When porting one of those, verify the helper you are copying **into** is not older
than the one you copied **from**, and check the helper itself rather than just the number of
findings a checker reports. A stale helper can make a checker report zero while the defect
is still live.

`leapps-org/leapps-parity` scans for exactly this class of drift and its report is a
reasonable place to start.
