---
name: leapp-corpus-run
description: Run a LEAPP tool end to end against a real extraction to validate artifact changes and produce a handoff. Use when verifying new or changed artifacts before a PR, when asked to "run it against a real image" or "check the report", or when confirming recorded sample_data row counts.
---

<!-- SHARED SKILL. Canonical copy lives in leapps-org/leapps-parity under skills/.
     Do not edit in place; edit the canonical copy and re-run the sync script. -->

# Validating against a real extraction

Unit tests and a clean import prove the module loads. They do not prove it parses. An
end-to-end run against a real extraction is the validation that counts, and it is what
should back any claim in the PR.

## 1. Build a focused profile

Create a tool profile containing only the artifacts you changed or added. A profile naming
a handful of modules turns a full-image run from tens of minutes into seconds, which is what
makes iterating on real data practical.

Plugin names in a profile are the artifact function names.

## 2. Pick an extraction that actually exercises the change

One that contains the app, at an OS version where the data shape matches what you parsed.
When no single image covers everything, assemble a compact composite from the relevant
files plus their SQLite sidecars. A `-wal` or `-shm` left behind changes what a reader sees,
so carry them or knowingly drop them.

**Keep source images read-only.** Do extraction and any permission changes on a temporary
copy. Never point the tool at your only copy of an image.

## 3. Run it and read the output

Generate output somewhere you will actually look at it, then check:

- **Row counts** per artifact, against what you expected. Both zero and implausibly large
  are findings.
- **Column alignment.** A tuple-width mismatch shifts every column right and is easy to miss
  when the values are plausible.
- **Timestamps** in the first column, in the right epoch, in the right zone.
- **Export formats** the artifact declares. If `output_types` includes KML, open it.
- **Parser errors** in the log. A caught exception per artifact does not fail the run, so a
  green exit code is not evidence of a clean parse.
- **The LAVA output**, if the artifact writes one. Open the case in LAVA rather than
  assuming the manifest is right. Record counts come from the manifest, not a live query,
  so an artifact that writes rows without updating the count shows as empty.

## 4. Record what you verified

Add the confirmed counts to `sample_data` as `"<corpus key>": "<OS> <ver> | <n> rows"`,
including zero-row corpora.

Reference corpora by **key only**. A key plus a row count is a pointer back to the data
behind it, so do not name files, paths or values.

## 5. Hand off

State what was run, against which extraction, what the counts were, and what you did **not**
cover: OS versions untested, app versions unseen, code paths present but never exercised.
The gaps are the most useful part of the report, and leaving them out turns a bounded result
into an implied general claim.

Give clickable paths to the profile, the report entry point and the output folder.
