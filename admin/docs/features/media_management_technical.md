# Media Management System: Technical Specification

This page describes how media check-in works in `scripts/ilapfuncs.py` and
`scripts/lavafuncs.py`. For how a module calls it, see
[Helper functions for artifact modules](../helper_functions.md#checking-in-media).

The first version of this page was a design written before the code. It described a
`check_in_media(file_path, module_name, artifact_name)` that returned a `MediaReference`
object and raised on missing files. The code does not work that way. What follows is what
it does.

## 1. Entry points

```python
check_in_media(file_path, name="", converted_file_path=False, force_type=None,
               force_extension=None, force_creation_date=None, force_modification_date=None)

check_in_embedded_media(source_file, data, name="", force_type=None, force_extension=None,
                        force_creation_date=None, force_modification_date=None)
```

Both return a media reference id (a string), or `None` when nothing was checked in. Neither
raises for a missing file. Both read the module name, artifact name, seeker and output
folders from `Context`, which `@artifact_processor` sets, so they work only inside a
decorated artifact function.

## 2. Identifiers

- **Media item id.** For a file in the extraction, the SHA-1 of the file's evidence path
  (the seeker's `source_path` for it). For embedded media, the SHA-1 of the bytes.
- **Media reference id.** The SHA-1 of `"<media item id>-<artifact name>-<name>"`.

So one file referenced by many rows of an artifact under the same `name` gets one
reference id, and one file referenced by several artifacts gets one media item with one
reference per artifact.

## 3. Check-in process

1. `check_in_media` resolves `file_path` against the artifact's files found
   (`Context.get_source_file_path`). If nothing matches, it logs
   `No matching file found for "<file_path>"` and returns `None`. If the match has no
   seeker file record, it returns `None`.
2. If the reference id already exists, it is returned and nothing else happens.
3. If the media item does not exist yet:
   - The MIME type is `force_type`, or is guessed from the first 8,192 bytes of the file
     (or from the embedded bytes) by `scripts/filetype.py`.
   - The extension is `force_extension`, else the extension of `name` if it is four
     characters or fewer, else that of the source path by the same rule (files only), else
     one guessed from the bytes.
   - The dates are the `force_*` values, else the seeker's recorded creation and
     modification dates for a file, else empty.
   - The file (or `converted_file_path` when given) is hard-linked, or copied if a link
     fails, to `<report>/media/<media item id>.<ext>`. Embedded bytes are written there.
     A second link or copy goes to `_HTML/media/` for the HTML report.
   - A row is written to `_lava_media_items`.
4. A row is written to `_lava_media_references` and the reference id is returned.

## 4. Database tables

In `_lava_artifacts.db`, created by `lavafuncs.py`.

### 4.1 `_lava_media_items`

| Column | Type | Contents |
| --- | --- | --- |
| id | TEXT | Media item id |
| source_path | TEXT | Path of the file in the evidence, or of the file the bytes came from |
| extraction_path | TEXT | Path of the copy, relative to the report: `media/<id>.<ext>` |
| type | TEXT | MIME type |
| metadata | TEXT | Currently always `not parsed yet` |
| created_at | INTEGER | Creation date, or NULL |
| updated_at | INTEGER | Modification date, or NULL |
| is_embedded | INTEGER | 1 for embedded media, 0 for a file |

### 4.2 `_lava_media_references`

| Column | Type | Contents |
| --- | --- | --- |
| id | TEXT | Media reference id |
| media_item_id | TEXT | Foreign key to `_lava_media_items.id` |
| module_name | TEXT | Module that checked it in |
| artifact_name | TEXT | Artifact that checked it in |
| name | TEXT | The `name` passed at check-in |

### 4.3 `_lava_media_info`

A view joining each reference to its item. The report writers read media through it
(`lava_get_full_media_info`).

## 5. Output

A column whose header is `('Name', 'media')`, optionally with a CSS style as a third
element, holds reference ids. A cell may hold one id or a list of ids.

- **HTML:** an `<img>`, `<video>` or `<audio>` tag by MIME type, or a link for anything
  else, pointing at `_HTML/media/`.
- **TSV, timeline and KML:** the copy's `extraction_path`; for a list, the paths joined
  with ` | `.
- **LAVA:** the reference id, or a JSON array of ids for a list.
