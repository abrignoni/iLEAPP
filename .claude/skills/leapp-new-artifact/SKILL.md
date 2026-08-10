---
name: leapp-new-artifact
description: Write a new LEAPP artifact module, or substantially rework an existing one. Use when adding support for an app or data source in iLEAPP, ALEAPP, RLEAPP, VLEAPP or DLEAPP, when asked to "add an artifact" or "parse <app>", or when a module needs new output types, media or a conversation view.
---

<!-- SHARED SKILL. Canonical copy lives in leapps-org/leapps-parity under skills/.
     Do not edit in place; edit the canonical copy and re-run the sync script. -->

# Writing a LEAPP artifact module

`admin/docs/artifact_info_block.md` in the iLEAPP repo is the authority on every field of
the `__artifacts_v2__` block. Read it first. This skill is the order of operations around it.

## 1. Find the data before writing any code

Locate the app's files in a real extraction and confirm what is actually there. Do not start
from the app's documentation or from another tool's output.

Open the database or file read-only and look at the schema. Note which tables carry
timestamps, which carry identifiers, and which are empty in your sample. An empty table in
one image is not evidence the feature is unused.

## 2. Check the siblings first

Grep the other cores for the same app name and bundle or package identifier. If a copy
exists, read it. You may be fixing a known problem, or inheriting one. See the
`leapp-cross-core` rule.

## 3. Write the module

One file under `scripts/artifacts/`. The key in `__artifacts_v2__` must exactly match the
processing function's name, or the loader will not associate them.

Get these right, because they are the ones most often wrong:

- **`paths`** is `fnmatch`, not glob. `*` crosses `/`. Matching is case-sensitive off
  Windows. See the `leapp-artifact-paths` rule and validate before committing.
- **`author`** is unversioned: `@YourHandle`, or `@YourHandle, Claude` if an agent helped.
- **`description` and `notes`** are examiner-facing and reach the report and the LAVA
  manifest. Say only what the data proves. See the `leapp-claims` rule.
- **`output_types`**: `"standard"` for the usual fan-out, `"all"` to add KML when the
  artifact has coordinates, `"lava_only"` for a producer another module reads.
- **Column order**: most relevant event timestamp first, any other timestamps immediately
  after, then identifiers, then descriptive fields.
- **Never write to evidence.** Use `open_sqlite_db_readonly()`, and
  `attach_sqlite_db_readonly()` if you attach. See the `leapp-evidence-readonly` rule.

If the app has attachments, surface the media itself rather than its filename. See the
`lava-media` rule.

## 4. Run it against real data

A module that imports cleanly has not been tested. Run the tool against an extraction that
contains the app and confirm the row count, the column alignment, and that timestamps land
in the right column with the right epoch.

Build a focused profile containing only the artifacts you changed so the run is fast.

Record what you verified in `sample_data` as `"<corpus key>": "<OS> <ver> | <n> rows"`.
Record zero-row corpora too: that a corpus was checked and had none is useful.

## 5. Before opening the PR

- Run the full tool once. Duplicate artifact `name` values are rejected at load and nothing
  else catches it.
- Reproduce lint locally. Warnings fail the build. See the `leapp-ci` rule.
- Reread the PR body for values copied out of someone's real data.
