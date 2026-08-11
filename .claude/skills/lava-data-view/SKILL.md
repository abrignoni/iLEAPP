---
name: lava-data-view
description: Wire up how an artifact renders in LAVA, end to end across the producer and the viewer. Use when adding a conversation view to an artifact, when a view renders wrong or not at all, when adding a field to the LAVA schema or manifest, or when asked to "add a module to the LAVA schema".
---

<!-- SHARED SKILL. Canonical copy lives in the LAVA repo under .claude/skills/.
     Do not edit in place; edit the canonical copy and re-run the sync script. -->

# Adding or changing a LAVA data view

`LAVA/docs/schema/` is the authority and is more current than any summary:

| doc | covers |
| --- | --- |
| `docs/schema/data-views.md` | every view type and every config field, with a required/optional table |
| `docs/schema/output-data-v1.md` | the `_lava_data` manifest structure |
| `docs/schema/sqlite-data-v1.md` | the artifact database layout |

Read `data-views.md` before writing a `data_views` block. This skill is the order of
operations and the traps around it.

## The change is always two-sided

The extractor declares the view; LAVA renders it. A change to one half without the other
either does nothing or breaks the case. Decide up front which halves you are touching, and
say so in the PR.

**Producer side** (any of the five extractors): the `data_views` block in
`__artifacts_v2__`, plus whatever columns the view references.

**Viewer side** (LAVA): only needed for a genuinely new view type or a new config field.
An existing view type with a new artifact needs no LAVA change at all.

## 1. Producer: declare the view

Column values in the config are the **display names as they appear in the artifact module**,
not the sanitized SQL names. LAVA resolves them, and also accepts an exact match on the
sanitized form, so use the display name and stay consistent.

Every required field in `data-views.md` must be present. A conversation view missing
`directionColumn` or `timeColumn` does not degrade gracefully, it fails to group.

`directionSentValue` is the value meaning "sent", and it is type-sensitive: `1` and `"1"`
are not interchangeable. Confirm what your parser actually writes into that column.

## 2. Make sure the columns survive the trip

The table is created from the artifact's headers, and column names are sanitized to
snake_case, so `Chat_Contact_ID` becomes `chat_contact_id`. A header typed
`('X', 'datetime')` becomes an INTEGER epoch column.

Headers that sanitize to SQL reserved words are handled by `quote_sql_name()`, but a header
that sanitizes to the *same* name as another column silently collides. Check for that when
adding columns to an artifact that already has a view.

If the view references media, see the `lava-media` rule: register with `check_in_media` and
set `mediaColumn`.

## 3. Viewer: only if the type or a field is new

`data_views` is consumed in `src/renderer/components/` by `ArtifactView.jsx`, which decides
whether the view is offered, and `ConversationPanel.jsx` / `ConversationExportView.jsx`,
which render it. A new field means touching the panel and the export view together, or the
on-screen view and the exported one disagree.

Note the legacy alias: the code reads `data_views.conversation || data_views.chat` and has
a separate branch for `chat`. New artifacts use `conversation`. Do not add `chat`, and do
not remove support for it.

## 4. Verify by opening a real case

**LAVA has no automated test runner.** A passing harness is necessary and not sufficient,
because the harness cannot exercise the GUI, which is where view bugs live.

Run an actual extractor against real data, then open the resulting `_lava_data.lava` in the
running app and check: the view is offered at all, conversations group on the right column,
direction is right for both sent and received, ordering follows `timeColumn`, labels resolve
rather than showing raw identifiers, and media renders in the bubble.

Confirm the plain table view still works. It is the default for every artifact and is easy
to break while adding a second view.

## Known stale documentation

`docs/schema/sqlite-data-v1.md` says the artifact table is named from the artifact's `name`
value. It is not. `lava_process_artifact` derives it from `func_name`, and falls back to
`artifact_name` only for modules that predate that parameter. Trust the code.
