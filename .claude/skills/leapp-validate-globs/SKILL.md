---
name: leapp-validate-globs
description: Validate LEAPP artifact path globs against real extraction file listings before committing them. Use when adding or changing a "paths" pattern in __artifacts_v2__, when an artifact returns no rows and the pattern is suspect, or when a vendor has moved a file between OS versions.
---

<!-- SHARED SKILL. Canonical copy lives in leapps-org/leapps-parity under skills/.
     Do not edit in place; edit the canonical copy and re-run the sync script. -->

# Validating a path glob

A pattern that matches nothing fails silently. The artifact simply reports no data, which is
indistinguishable from the app not being present. Never commit a pattern you have not run.

## What you are testing against

The matcher is Python `fnmatch`, so reproduce it exactly rather than approximating with
`glob` or a regex:

- `*` and `**` both span `/`. They are interchangeable.
- Matching goes through `os.path.normcase`, so it is **case-sensitive on macOS and Linux**
  and case-insensitive on Windows. Test the case-sensitive behaviour; it is the stricter one.
- The directory, zip and tar seekers prepend a synthetic `root/`. iLEAPP's iOS-backup seeker
  does not, and does not normcase either.

## Method 1: against recorded path listings (fastest)

iLEAPP carries real file listings from published research images at
`admin/data/filepath-lists/*.csv.zip`, covering several iOS generations.

Unzip to a scratch directory, then run each candidate pattern over the path column with
`fnmatch.fnmatchcase` and count hits per generation. Run the **old and new** patterns both,
and compare. A change that reduces the count on an older image is a regression, not a
tightening, unless you meant it.

## Method 2: against a real extraction (authoritative)

Instantiate the matching seeker from `scripts/search_files.py` directly so the semantics are
exact by construction, then call `search()` with the pattern. This is the only way to catch
a mismatch between what you think the seeker does and what it does.

To confirm the artifact then produces the rows you expect, call the artifact function's
`.__wrapped__`, exposed by `@artifact_processor`'s `@wraps`, with a mock context providing
`get_files_found()` and `get_relative_path()`. `len(data_list)` is the count to record in
`sample_data`.

## Patterns that need extra care

**Case variants.** Use one bracket class, `*/[Bb]iome/*`, never a tuple of two patterns. A
tuple double-counts on Windows, where `normcase` folds both to the same string and the
entry point extends `files_found` once per pattern with no dedup.

**Vendor moves.** When a file changes location between OS versions, keep the old pattern
alongside the new one. Examiners run these tools against extractions going back years.

**Over-generic components.** A pattern whose filename component is bare `*`, `**` or `*.*`
matches every file at that level and is rejected. Anchor on something real.

## Hygiene

Print counts and value shapes from test images, never actual values, and delete anything
you extracted when you are done.
