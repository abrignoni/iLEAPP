---
name: leapp-new-artifact
description: Write, rework, review or audit a LEAPP artifact module. Use when adding support for an app or data source in iLEAPP, ALEAPP, RLEAPP, VLEAPP or DLEAPP, when asked to "add an artifact" or "parse <app>", when a module needs new output types, media or a conversation view, and equally when fixing, validating or checking the forensic value of a module that already exists, including one already merged.
---

<!-- SHARED SKILL. Canonical copy lives in leapps-org/leapps-parity under skills/.
     Do not edit in place; edit the canonical copy and re-run the sync script. -->

# Writing a LEAPP artifact module

`admin/docs/artifact_info_block.md` in the iLEAPP repo is the authority on every field of
the `__artifacts_v2__` block. Read it first. This skill is the order of operations around it.

## 1. Find the data before writing any code

Locate the app's files in a real extraction and confirm what is actually there. Do not start
from the app's documentation or from another tool's output.

**Inventory the stores by content, not by file name.** The commonest Android SQLite files
have no extension at all, so a scan keyed on `.db`/`.sqlite` misses them. Read the first
sixteen bytes of every candidate and test for `SQLite format 3\x00`. The same test works in
reverse: a file named `.db` need not be SQLite. Do this before writing any inventory down,
because an early inventory becomes the summary you hand over.

Open the database read-only and dump the **full `.schema`**, not just `PRAGMA table_info`.
SQLite keeps the original `CREATE TABLE` text including the developers' own inline comments,
and a `CHECK (x IN (...))` constraint is an enum definition for free. Note which tables carry
timestamps, which carry identifiers, and which are empty in your sample. An empty table in
one image is not evidence the feature is unused.

**Read the file twice, with and without its write-ahead log**, and compare. `file:db?mode=ro`
applies the log; `file:db?immutable=1` ignores it. Compare **primary keys, not row counts**:
a table can hold the same number of rows in both reads with different rows in them. If they
differ the sidecars are load-bearing and must be in your `paths` glob.

## 2. Decide what is worth reporting

**The `leapp-artifact-value` rule is the bar. Read it before deciding anything here.** This
section is only the order of operations for clearing that bar with the extraction open.

1. **Enumerate every store in the extraction, across all file types**, not just the ones
   that enumerate themselves. Inventory by extension with sizes alongside the magic-byte
   scan from step 1, so a format class you have not considered is visible.
2. **List every table with its row count and its full schema.** Both, because the ranking
   that matters is what the columns promise and the counts rank it backwards.
3. **Sort the candidates by what a row would let an examiner do**, then draw the line.
4. **Write down which side each table fell on, the excluded ones included**, in the notes
   and in the PR body. Nothing else in the diff records that a table was considered, so an
   omission and a reasoned exclusion are indistinguishable without it.
5. Turn every zero-row table you kept into a checked absence in `sample_data`.

## 3. Check the siblings first

Grep the other cores for the same app name and bundle or package identifier. If a copy
exists, read it. You may be fixing a known problem, or inheriting one. See the
`leapp-cross-core` rule.

## 4. Write the module

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
`lava-media` rule. Link media by something the extraction **records** — a content hash, a
foreign key, a cache index mapping address to file — not by correlating size and timestamp.
An exact match can fail, and a failure is a real result; a ranked guess always returns
something. When no recorded link exists, say so and say what you checked, so the next person
does not re-derive the same dead ends.

### The framework shortens one path and no others

Every seeker copies matched evidence into `<report folder>/data/`, so each `files_found`
entry is an absolute path on the machine running the tool. `artifact_processor` splits the
**third element** of your return tuple on `\n` and passes each piece through
`Context.get_relative_path`. Nothing else is touched. A staged path placed in a data row goes
verbatim into the HTML, the TSV, the timeline, the KML and the LAVA database, publishing the
examiner's home directory, case folder and report layout to everyone who reads the report.

Shorten the path where it enters the row, not centrally afterwards:

```python
data_list.append((timestamp, name, context.get_relative_path(file_found)))
```

Two things stop this showing up on its own:

- `get_relative_path` returns its input unchanged when the data folder is unset, so wherever
  that state is missing a leaking artifact and a correct one produce byte-identical output.
  The committed test harness is one such place, which is why a fixture comparison cannot tell
  them apart. Read a report from a real run instead.
- A module that builds its own `ArtifactHtmlReport` rather than returning to the wrapper skips
  the normalization entirely, including its own "located at" line.

The third element itself has to be real paths, newline joined, because that is what the
wrapper splits. Placeholder prose (`'see the Source File column'`), several paths joined with
`'; '` or `', '`, and an empty string on a run that parsed data are all silent defects: the
report's "located at" line then points nowhere. Return `''` only from a branch where no file
was found. A file that exists but lacks the expected table still reports its path.

`admin/scripts/check_report_local_paths.py` and `admin/scripts/check_source_path.py` gate both
halves in CI. Run them before opening the PR.

### Three failure modes that are silent by construction

**An index keyed on a bare name merges two app data directories.** The moment you write
`index[name] = path` over `files_found`, where `name` is a cache entry, a basename, a media
id or a store label, two containers holding that name collide and the second silently
overwrites the first. It drops rows, and worse, it can join one container's record to another
container's bytes. Key on `(container, name)`, where the container is resolved by matching a
path **segment** equal to the package name, never a substring. The harness dedupe collapses
the duplicate storage views of one file; it says nothing about a dict you build yourself.

**A decoder that returns nothing on unrecognised input makes the table short, not loud.**
`if value is None: continue` is correct defensive code and it is silent: N sources become
N-1 rows with no error. Prefer a decoder that degrades to the raw value over one that
abstains, and log every skip. Count the inputs independently and assert the row count matches
before recording that number anywhere.

**A guard conditioned on the emptiness of the set it validates against is inverted.**
`if roots and not in_container(path, roots)` admits everything when `roots` is empty, which is
precisely the case the guard exists for. Fail closed, and prove the branch by running the
function with an empty set rather than by reading it.

Tolerate schema drift rather than relocating to it: resolve every spelling you have seen
instead of replacing the old one, and let a missing table log and yield nothing rather than
costing the artifact every row it would have returned.

## 5. Run it against real data

A module that imports cleanly has not been tested. Run the tool against an extraction that
contains the app and confirm the row count, the column alignment, and that timestamps land
in the right column with the right epoch.

Build a focused profile containing only the artifacts you changed so the run is fast.

Record what you verified in `sample_data` as `"<corpus key>": "<OS> <ver> | <n> rows"`.
Record zero-row corpora too: that a corpus was checked and had none is useful.

`python3 admin/scripts/validate_sample_data.py --emit <image> --key <corpus key>` prints
these values for you: it runs the tool on a zip, tar, gz or extraction directory, asserts
the completion marker and greps the error vocabulary itself, and emits paste-ready blocks
for the modules changed on the branch (or `--modules`), with every zero flagged as
unverified. Add the app name and version yourself, and confirm a zero against the source
store before recording it. The two checks below still apply to any run you scrape by hand.

**Assert the run finished.** Scrape counts only from a log containing the tool's own
end-of-work marker, and record a sentinel rather than zero when it is absent. A default of
zero in an error path asserts a measurement that was never taken, and a zero is
indistinguishable from a real empty result. Note that the log prints `record` singular at one
row and prints **nothing at all** at zero.

**Grep the raw output for the layer beneath the framework banner.** Artifacts catch their own
database errors and log them in their own format, so a clean banner is a statement about the
reporting, not about the run. Search for `no such column`, `no such table`, `malformed` and
`file is not a database`, and read how the artifact handled each: an error string inside a
deliberate explanatory skip is the code working.

### Run the multi-container tree. It is the check that finds real defects.

A single-container sample cannot detect the commonest scoping bug, because the count it
produces looks entirely reasonable. Build **one** tree containing all three of:

1. the same container under two spellings, `/data/data/<pkg>` and `/data/user/0/<pkg>`,
   which must **collapse to one**;
2. a genuinely different tenant, `/data/user/10/<pkg>` or a second account directory, with a
   known row delta, which must **add its own rows**;
3. a decoy with an identical internal layout under a different package name, which must add
   **nothing**.

Then read the arithmetic per artifact. It needs no knowledge of the module:

| result | meaning |
| --- | --- |
| exactly `2x` plus the known delta | correct |
| `1x` | a second tenant's rows are being dropped or merged |
| `3x` | the duplicate storage spellings are not collapsing |
| `>2x` | a decoy or foreign container is leaking in |

Assert **exact multiplication**. "More rows than before" passes a version that double counts,
and "no crash" passes the broken version. Then check row **contents** per container, not just
the count: a lost row is visible in arithmetic, but a surviving row wearing another
container's data is not.

This is also the cheapest audit that exists for code already merged, and it finds defects the
authoring session missed. Run it over a batch of new modules as routine.

### Let the output checker read the report you cannot fully read yourself

`admin/scripts/check_artifact_output.py REPORT_DIR` reads the generated report and reports the
column defects that source review and lint cannot see, because they are properties of a run
against real data:

- **empty-column**: no value on any row. The query never fills it, or the field is not what it
  was taken for.
- **constant-column**: one value across every row. Sometimes the data is uniform; sometimes a
  derivation never ran.
- **identical-columns**: two columns equal on every row where the values vary, which is what a
  derived column that equals its input looks like (a basename split on the wrong separator is
  the classic case).
- **sparse-lead**: the table leads with a timestamp that is mostly blank.

Pass `--compare MULTI_REPORT_DIR` to add the multi-container arithmetic above as a check rather
than a manual diff.

It is not a gate. A finding is a prompt, and the answer is usually one of two things: fix the
column, or, when the blank or the constant is a real result, **name that column in the notes**.
A column the notes name is not reported, so the documented way to keep a uniform column, saying
it was uniform and why it still earns its place, is exactly what clears the finding. An empty
column on a messages or location artifact is frequently a forensic negative worth stating (no
group chats, no disappearing timers, coarse location denied), not a column to delete.

## 6. Before opening the PR

- **Re-derive every number in `description`, `notes` and `sample_data` from the finished
  run.** Rereading your own prose does not find these; recomputing each claim does. A count
  written while building is a claim about the code as it was then, and any later change to
  what the module sees invalidates it. Check the arithmetic of joins especially: a count of
  matches is not a count of items when one item can match more than once, so print the
  distribution rather than the total.
- **State which tier each claim is**: proven against real data, verified against the vendor's
  published source but unexercised here, or code-present and never run. Never let the second
  or third read as the first.
- **Say what the module does not do**, in the same place you say what it does, and name the
  sample that would close the gap.
- Run the full tool once. Duplicate artifact `name` values are rejected at load and nothing
  else catches it.
- Reproduce lint locally. Warnings fail the build. See the `leapp-ci` rule.
- Reread the PR body for values copied out of someone's real data.

## When you change a merged module

Making a guard stricter creates false negatives in the same edit that removes false
positives, and the two need opposite inputs. Run **both** controls: an extraction where the
app is absent, proving the guard fires, and one where it is present, proving it does not
over-fire. Diff the **full row-count list**, because the tell is often an artifact vanishing
rather than reporting a smaller number.

Re-keying an index is not done when the write is patched: every read of that key has to move
with it. Grep the module for remaining bare-key uses, then re-run the single-container case
as well as the multi-container one. The single-container run is the control that must still
pass, and it is the one that catches a half-applied fix.
