---
paths:
  - "scripts/artifacts/**/*.py"
---

<!-- SHARED FILE. Canonical copy lives in leapps-org/leapps-parity. Do not edit in place;
     edit the canonical copy and re-run the sync script, or your change will be overwritten. -->

# Surface only what an examiner can act on

Ask of every candidate store, table and column: **what question does this let an examiner
answer, and what would they do with a row?** If the honest answer is nothing, it does not
ship. Having decoded something is not a reason to report it.

The failure this prevents is not a wrong row. It is a correct row that buries the useful
ones, in a report an examiner has to read under time pressure.

## Four things that look like user activity and are not

- **A server-supplied catalogue.** Suggestion dictionaries, trending feeds, rate tables,
  help articles, device lists, effect libraries. Ask "could this row exist if the user had
  never touched the feature?" Tells: the app's own preferences name the fetch, ids are
  contiguous with no gaps, there is a relevance or score column, or a sibling table records
  when it was downloaded. Report the fetch time and the row count, never the contents.
- **A shipped candidate list.** A table of paths or names the app *looks for*, which reads
  as a list of what the device *has*. Directory names in a language the device does not
  use, or paths belonging to apps that need not be installed, are the tell.
- **Prefetched content.** A feed row whose own column says it arrived by background
  prefetch records that the app fetched it, not that anyone saw it.
- **A constant column.** Uniformly null or uniformly identical across every row is noise,
  and it is also a bug tell: a derivation that never ran looks exactly like this. Drop it,
  or keep it and say in the notes that it was uniform and why it still earns its place.

## The populated tables are often the least interesting ones

A module built against one extraction naturally covers the tables that had rows in it. On a
device where the user never used the feature, that selection is inverted: the populated
tables are the app's own service telemetry and configuration, which fill on every device
whether or not anyone used it, and the empty tables are the user-data ones, empty
*because* the feature was unused.

So enumerate every table with its row count **and** its schema, then rank by what the
columns promise rather than by what the counts show. A table named for an event, carrying a
timestamp and a name column, outranks a populated table of debug strings whatever the counts
say. A zero-row table is a reason to record a checked absence in `sample_data`, never a
reason to omit it.

## Name every store, including the ones you left out

The excluded set needs the same written reasoning as the included set. An honest limitation
and a missing artifact read identically to a reader, and only one of them is acceptable.

Saying in the notes that a log "is not evidence of what ran" while the table that answers
that question sits unparsed and unnamed in the same file is the shape to avoid. Name each
store and say which side of the line it falls on and why.

Survey the whole extraction, not one format class. Databases attract the survey because
they enumerate themselves and can be ranked; a rolling text log is frequently the only
record of when a device was actually used, and no database in the same tree will answer it.

## Aggregate what should be aggregated

A cache of 800 files belonging to 70 titles is 70 rows with a file count, not 800 rows.
When you summarise rather than enumerate, say so in the notes and name the path, so the next
examiner who needs the detail knows where it is.

## Nothing in CI checks this

`check_claim_language.py` gates the claims rule. There is no equivalent here, because value
is a judgement and not a lint. `admin/scripts/check_artifact_output.py` is the nearest thing
and it reads only the columns that shipped, never the tables that were skipped.

That makes the artifact's own `notes` the enforcement surface. Write the reasoning down and
it can be reviewed; leave it out and nobody can tell a considered exclusion from an
oversight.

The ordered procedure for doing this while building sits in the `leapp-new-artifact` skill.
This rule is the bar it has to clear. See also `leapp-claims.md`, which is the sibling
question: that rule asks whether what you said is true, this one asks whether the row earns
its place.
