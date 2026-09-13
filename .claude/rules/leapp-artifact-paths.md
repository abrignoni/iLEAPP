---
paths:
  - "scripts/artifacts/**/*.py"
---

<!-- SHARED FILE. Canonical copy lives in leapps-org/leapps-parity. Do not edit in place;
     edit the canonical copy and re-run the sync script, or your change will be overwritten. -->

# Artifact `paths` matching

`admin/docs/artifact_info_block.md` is the authority on the `__artifacts_v2__` block,
including the `paths` glob semantics. Read it before writing or changing a pattern. The
short version, because it is the single most common source of silently-wrong artifacts:

- Matching is Python **`fnmatch`**, not `glob` and not `pathlib`. `*` and `**` are
  interchangeable and **both span `/`**. A single `*` can cross several directory levels.
- Case sensitivity follows `os.path.normcase`: **case-sensitive on macOS and Linux**,
  case-insensitive on Windows.
- The directory, zip and tar seekers prepend a synthetic `root/` before matching, which is
  why leading `*/` and `**/` patterns work.

## Never use a two-pattern tuple for a case variant

When a path differs only by case, use one bracket class, not two patterns:

```python
"paths": ('*/[Bb]iome/*/StreamName/local/*',)     # correct
"paths": ('*/Biome/...', '*/biome/...')           # WRONG - double-counts on Windows
```

On Windows `normcase` folds both patterns to the same string, and the entry point extends
`files_found` once per pattern with no dedup, so every row appears twice. Off Windows the
capital-only pattern silently misses the lowercase directory entirely.

## Validate a pattern before committing it

Do not eyeball a glob. Run it with `fnmatch.fnmatchcase` against the real path listings
and confirm the hit count per OS generation, then check the counts still match after the
change. A pattern that matches nothing fails silently: the artifact simply reports no data.

Prefer a wildcarded anchor over a hardcoded directory level when a vendor moves things
between OS versions, and keep the older pattern alongside the new one rather than
replacing it, so existing extractions keep parsing.
