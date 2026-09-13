<!-- SHARED FILE. Canonical copy lives in the LAVA repo. Do not edit in place;
     edit the canonical copy and re-run the sync script, or your change will be overwritten. -->

# The LEAPP to LAVA output contract

The five LEAPP extractors write a case; LAVA (an Electron app) reads it. Both sides have to
agree, and a change to either half can break the other.

## What a LEAPP run produces

Alongside `_HTML/`, `_TSV Exports/`, `_Timeline/`, `data/` and `media/`:

- **`_lava_data.lava`**: a JSON manifest. Top-level keys include `parser_info`,
  `lava_db_name`, `modules`, `artifacts` and `meta`. `artifacts` is keyed by category, and
  each entry carries `name`, `tablename`, `module`, `column_map`, `artifact_icon`,
  `record_count`, `source_path` and `object_columns`.
- **`_lava_artifacts.db`**: SQLite, one table per artifact, named from the sanitized
  artifact function name. Column names are sanitized snake_case of the headers, so
  `Kind (as stored)` becomes `kind_as_stored`. A header typed `('X', 'datetime')` becomes
  an INTEGER epoch column; everything else is TEXT. The database also carries bookkeeping
  tables recording which glob matched which file.

Writing is done by `scripts/lavafuncs.py`, which is meant to stay identical across the five
extractors. `output_types` in the artifact block selects the fan-out: `"standard"` is
HTML + TSV + LAVA + timeline, `"all"` adds KML, `"lava_only"` writes only the database, and
`"none"` suits device-info collectors.

## Gotchas that are not visible from the code

- **LAVA validates the manifest filename**, so a renamed manifest is rejected even though
  its contents are fine. The older `_lava_data.json` name is still accepted.
- Paths inside the manifest are absolute, but LAVA resolves the database **relative to the
  manifest**, so moving the whole output folder is safe.
- Record counts shown in LAVA come from `record_count` in the manifest, not a live
  `COUNT(*)`. An artifact that writes rows without updating the count displays as empty.

## SQL identifiers must be quoted on both sides

Artifact headers that sanitize to SQL reserved words (`From`, `To`, `Order`) broke the
writer with `near "from": syntax error`. The fix is `quote_sql_name()` in `lavafuncs.py`
plus `sanitize_report_name()` in `ilapfuncs.py` for `/` in artifact names and categories,
and matching quoting on LAVA's read path.

**Both halves are required.** The extractor-side fix makes reserved-word columns reach LAVA
for the first time (before it, the artifact died and no table was created), so an unquoted
read path just moves the failure downstream. Quoting changes the statement, not the stored
identifier, so ordering does not matter, and columns already shipped keep working.

## Cross-module chaining

A module can write its own table into the LAVA database and later artifacts can query it.
The pattern is a producer with `output_types: "lava_only"`, and dependents that declare
`"paths": None` plus a `requirements` string naming the producer, then read the table back
out of the LAVA database rather than re-parsing the source.
