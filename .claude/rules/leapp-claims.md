---
paths:
  - "scripts/artifacts/**/*.py"
---

<!-- SHARED FILE. Canonical copy lives in leapps-org/leapps-parity. Do not edit in place;
     edit the canonical copy and re-run the sync script, or your change will be overwritten. -->

# Say only what the data proves

These tools produce evidence used in casework. A parser that asserts what a record *means*
about a person is making the examiner's finding for them, and an overstated claim baked
into tool metadata is what gets challenged in court.

Never state what something means unless the data itself proves it, or a source that
documents it is cited after checking that the source supports the **specific** claim.

Scope is every string a reader can take as fact: artifact `description` and `notes`, column
headers, enum mappings, report-emitted strings, KML and timeline labels, commit messages
and PR bodies.

## Name the evidence tier

1. **Data-proven**: decoded from a real image, ideally cross-checked by a second
   independent path. Give numbers.
2. **Source-verified**: the format comes from the vendor's published code and is confirmed
   by a round-trip test, but no image exercises it. Legitimate, but **say so**.
3. **Code-present but unexercised**: implemented and derived identically to a proven path,
   never run against real data. Name it as a validation boundary.

Never let tier 2 or 3 read as tier 1. Naming the tier costs one clause.

## Absence is not a negative finding

A missing key, row or file is not evidence a feature was off or unused. Many apps write no
record until a default changes, so a missing key means *factory default in effect*. Report
absence as absence and state what the default is. An empty artifact is not evidence of
absence either.

## Publish the gaps

Say what the artifact does **not** cover, in the same place you say what it does. List
unvalidated capabilities explicitly and ask for the corpus that would close them.

## Violations to check for

- Behavioural meaning as fact: "shows the user was at the location", "records every app
  launch", "the user selected/typed/saw X".
- Purpose attributed to a vendor with no source: "Apple uses this to...".
- Blanket assurances: "reliable", "proves", "always", "complete history", "full list".
- Unverified version-range or negative claims: "on all versions since X", "does not store
  message bodies".
- Bare database or protobuf fields given meaning-laden names, and enum mappings with no
  derivation stated. A column header and an enum branch are claims.
- Sample observations stated as general properties. This is the commonest slip.

## What passes

Neutral parser statements; claims evidenced by decoded content in the same file; labelled
observations ("in tested samples", "observed on iOS 18.7"); cautionary limits ("presence
does not establish connection"); cross-validation notes with numbers; an "(as stored)"
column plus a note for undocumented integers; "TBD" in place of an invented name.

## Citations

Cite the defining line, not the file. **Pin permalinks to a commit SHA, never to `main`**.
Line numbers move, so a `main` link keeps resolving while pointing at the wrong line, which
is worse than a broken link. Fetch the pinned link back and confirm it says what you claim.
Grep the relevant class body rather than the whole file; a file-wide grep can return a
same-named field from an unrelated struct.

`admin/scripts/check_claim_language.py` runs in CI and catches part of this, but it only
scans `description` and `name` for claim vocabulary. Passing the check is not the standard.
