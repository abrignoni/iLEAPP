# Helper functions for artifact modules

`scripts/ilapfuncs.py` holds the helpers an artifact module calls to find files, read
SQLite and other stores, check in media, convert timestamps and log. ALEAPP, iLEAPP, RLEAPP,
VLEAPP and DLEAPP each carry their own copy. Most helpers are the same in all five. Where a
core differs, the [table at the end](#where-the-five-cores-differ) says how.

This page is the same file in all five repositories. If you change it, change it in all five.

For the `__artifacts_v2__` block itself, see the Contributing section of the README. For
test cases, see `testing/create_module_test_cases.md` in this folder.

## The shape of a module

Modules in the five cores use the same pattern: an `@artifact_processor` function
that takes one argument, `context`, and returns headers, rows and the source path. The
processor writes the HTML, TSV, timeline, KML and LAVA output from what you return.

```python
__artifacts_v2__ = {
    "get_example_photos": {             # must match the function name
        "name": "Example App Photos",
        "description": "Photos sent in Example App chats",
        "author": "@YourHandle",
        "creation_date": "2026-10-14",
        "last_update_date": "2026-10-14",
        "requirements": "none",
        "category": "Example App",
        "notes": "",
        "paths": (
            '*/com.example.app/databases/chat.db*',
            '*/com.example.app/files/photos/*',
        ),
        "output_types": "standard",
        "artifact_icon": "photo",
    }
}

from scripts.ilapfuncs import (
    artifact_processor, check_in_media, convert_unix_ts_to_utc,
    get_sqlite_db_records, logfunc)


@artifact_processor
def get_example_photos(context):
    db_path = ''
    for file_found in context.get_files_found():
        if file_found.endswith('chat.db'):
            db_path = file_found
            break
    if not db_path:
        return (), [], ''

    query = 'SELECT sent_at, sender, photo_name FROM messages WHERE photo_name IS NOT NULL'
    data_list = []
    for row in get_sqlite_db_records(db_path, query):
        sent_at, sender, photo_name = row[0], row[1], row[2]
        photo = check_in_media(f'files/photos/{photo_name}', name=photo_name)
        if photo is None:
            logfunc(f'Photo {photo_name} is referenced but was not found')
        data_list.append((convert_unix_ts_to_utc(sent_at), sender, photo_name, photo))

    data_headers = (('Sent', 'datetime'), 'Sender', 'File Name', ('Photo', 'media'))
    return data_headers, data_list, db_path
```

The decorator reads the artifact block whose key matches the function name, sets up
`context`, calls your function and writes the output. If `data_list` is empty it logs
`No data found for <artifact name>` and writes no table.

Column types go in the header as a tuple: `('Sent', 'datetime')`, `('Day', 'date')`,
`('Number', 'phonenumber')` and `('Photo', 'media')`. Plain strings are text columns.

## What `context` gives you

`context` is the `Context` class in `scripts/context.py`. The decorator fills it in for
your artifact before calling your function. These are the methods a module uses:

| Method | Returns |
| --- | --- |
| `context.get_files_found()` | The staged paths that this artifact's `paths` globs matched. Raises `ValueError` if the list is empty. |
| `context.get_source_file_path(partial_path)` | The path in this artifact's files found with the same file name as `partial_path`, or `None`. |
| `context.get_relative_path(full_path)` | The path with the examiner's data and report folders removed. |
| `context.get_report_folder()` | This artifact's report folder. |
| `context.get_artifact_info()` | This artifact's `__artifacts_v2__` entry. |
| `context.create_artifact_result(...)` | A result object for row sets too large to hold in memory. See its docstring in `scripts/context.py`. |

`get_source_file_path` looks only in this artifact's files found, never in the whole
extraction. It matches on the file name. When only one found file has that name, that file
is returned even if the folders you gave do not match. When several do, it returns the one
whose path ends in `partial_path`, or `None` if none does.

## Finding files

`get_file_path(files_found, filename, skip=False)` returns the first path in
`files_found` that matches `filename` with `pathlib.Path.match`, or `None`. Pass a string as
`skip` to pass over any path that contains it.

```python
db_path = get_file_path(context.get_files_found(), 'chat.db')
```

`Path.match` matches from the right, so `'chat.db'` and `'databases/chat.db'` both match
`.../databases/chat.db`.

## Reading SQLite

Open evidence databases read-only. These helpers do that for you.

| Helper | What it does |
| --- | --- |
| `get_sqlite_db_records(path, query, attach_query=None)` | Runs `query` and returns its rows. Returns `[]` and logs the error if the query fails. |
| `open_sqlite_db_readonly(path)` | Returns a read-only `sqlite3` connection, or `None`. Close it when you are done. |
| `attach_sqlite_db_readonly(path, db_name)` | Returns an `ATTACH DATABASE ... AS db_name` statement that attaches `path` read-only. Pass it as `attach_query`. |
| `does_table_exist_in_db(path, table_name)` | `True` if the table exists. |
| `does_view_exist_in_db(path, table_name)` | `True` if a view named `table_name` exists. |
| `does_column_exist_in_db(path, table_name, col_name)` | `True` if the column exists. The column name is compared case-insensitively. |
| `null_absent_columns(path, query)` | Returns `query` with every column the database lacks replaced by `NULL`. Use it when an app added columns between versions. |

The rows `get_sqlite_db_records` returns are not the same in every core:

- **iLEAPP, RLEAPP, VLEAPP:** a one-pass iterator of `sqlite3.Row`. Read a value by
  position (`row[0]`) or by column name (`row['sender']`). It has no `len()`, and a second
  loop over it gets nothing.
- **DLEAPP:** a list of `sqlite3.Row`.
- **ALEAPP:** a one-pass iterator of plain tuples. Read values by position only. It logs
  and returns `[]` for an `OperationalError` or `ProgrammingError`. Any other
  `sqlite3.DatabaseError`, such as a file that is not a database, reaches your module.

Code that has to run the same in every core reads values by position and wraps the result
in `list()` when it needs a count or a second pass:

```python
rows = list(get_sqlite_db_records(db_path, query))
if not rows:
    return (), [], db_path
```

For an app whose schema changed between versions:

```python
query = null_absent_columns(db_path, 'SELECT sent_at, sender, edited_at FROM messages')
```

A column missing from this copy of the database comes back as `NULL`, and the helper logs
which columns it replaced.

## Reading other files

`get_txt_file_content(file_path)` reads the file as UTF-8 and returns a list of its lines,
each ending in a newline except possibly the last. It returns `[]` and logs the error if
the file cannot be read, including when it is not valid UTF-8.

`get_plist_file_content(file_path)` and `get_plist_content(data)` are iLEAPP helpers. They
read a plist file or plist bytes and decode an NSKeyedArchiver plist. They return `{}` and
log on failure. RLEAPP, VLEAPP and DLEAPP define both names, but they raise
`NotImplementedError`, and ALEAPP has neither. In those cores use `plistlib` directly.

`get_binary_file_content(file_path)` is ALEAPP only. It returns the file's bytes, or empty
bytes on failure.

## Checking in media

Media goes into the report through two helpers. Both return a media reference id, a string
you put in a column typed `media`. Both return `None` when nothing was checked in.

### `check_in_media` for a file in the extraction

```python
check_in_media(file_path, name="", converted_file_path=False, force_type=None,
               force_extension=None, force_creation_date=None, force_modification_date=None)
```

- `file_path` is the media file: either a staged path the seeker returned, from this
  artifact's files found or from its own `context.get_seeker().search()`, or a path or
  partial path of one of this artifact's files found, looked up the same way as
  `context.get_source_file_path`. If nothing matches, the helper logs
  `No matching file found for "<file_path>"` and returns `None`.
- `name` is the label stored with the reference. The copy in the report takes its
  extension from `force_extension`, else from `name` when the text after its last dot is
  four characters or fewer, else from the source file's name by the same rule, else from
  the type guessed from the bytes.
- `force_type` sets the MIME type. Without it, the type is guessed from the first 8,192
  bytes of the file. Set it when you know the type and the guess could miss, for example a
  cache file with no extension.
- `force_extension` sets the extension of the copy, with or without the dot.
- `force_creation_date` and `force_modification_date` replace the file system dates the
  seeker recorded for the file. The modules that use them pass Unix seconds.
- `converted_file_path` is a file your module wrote, copied into the report in place of
  the original. The source path and dates recorded are still the original file's, and the
  type is still guessed from the original's bytes, so pass `force_type` and
  `force_extension` with it. No module in the five cores uses this option yet.

### `check_in_embedded_media` for bytes inside another file

```python
check_in_embedded_media(source_file, data, name="", force_type=None, force_extension=None,
                        force_creation_date=None, force_modification_date=None)
```

- `source_file` is the file the bytes came from, usually the database. It is recorded as
  the media's source.
- `data` is the media bytes. Empty or `None` data returns `None`.
- The other options work as they do for `check_in_media`. There are no file system dates
  for embedded media, so the dates are empty unless you pass them.

```python
for row in get_sqlite_db_records(db_path, 'SELECT sent_at, thumbnail FROM messages'):
    thumb = check_in_embedded_media(db_path, row[1], name='thumbnail.jpg')
    data_list.append((convert_unix_ts_to_utc(row[0]), thumb))
```

### How it fits together

- Both helpers read the context `@artifact_processor` sets up. A module without the
  decorator sees whatever context the artifact before it left behind, so `check_in_media`
  looks in that artifact's files found and records media under that artifact's name.
- The same file is copied into the report once, however many rows or artifacts refer to
  it. A file in the extraction is identified by its evidence path. Embedded media is
  identified by the SHA-1 of its bytes, so identical blobs are stored once.
- The first check-in of a file or blob decides its copy, type, extension and dates. A later
  check-in of the same file, with any `name` or options, adds a reference and changes
  nothing else.
- The copy goes to `media/` in the report, with a second copy or hard link under
  `_HTML/media/` for the HTML pages.
- A media cell can hold one reference id or a list of them. The HTML report shows each
  item. The TSV and timeline exports show the copy's path in the report, joined with
  ` | ` for a list. LAVA stores a list as a JSON array of ids.
- An empty or `None` cell shows as blank.
- A third element in the header sets the CSS style of images in the HTML report:
  `('Photo', 'media', 'max-height:100px;')`.
- In the HTML report, `image/*` types show as images, `video/*` and `audio/*` as players,
  and anything else as a link.

## Converting timestamps

Return timestamps as timezone-aware `datetime` objects in UTC, in a column typed
`datetime`. These helpers produce them.

| Helper | Input | Notes |
| --- | --- | --- |
| `convert_unix_ts_to_utc(ts)` | Unix time in seconds, milliseconds, microseconds or nanoseconds | The unit is taken from the size of the number. Values within about four months of 1 January 1970 are read as the next coarser unit, so convert those yourself if you know the unit. A falsy value is returned as given. |
| `convert_ts_int_to_utc(ts)` | Unix seconds only | No unit detection. |
| `convert_cocoa_core_data_ts_to_utc(ts)` | Seconds since 1 January 2001 (Cocoa, Core Data, Mac absolute time) | Not in ALEAPP. |
| `webkit_timestampsconv(ts)` | Seconds since 1 January 2001 | Despite the name, it adds the 2001 offset. It does not handle WebKit or Chrome time, which counts microseconds from 1601. ALEAPP has the same function as `timestampsconv`. |
| `convert_human_ts_to_utc(ts)` and `convert_ts_human_to_utc(ts)` | Text `YYYY-MM-DD HH:MM:SS` | Drops any fraction of a second and labels the result UTC. It does not convert from local time, so the text must already be UTC. |
| `convert_plist_date_to_utc(dt)` | A `datetime` read from a plist | Labels it UTC and drops the fraction of a second. Not in ALEAPP. |
| `convert_time_obj_to_utc(dt)` | A naive `datetime` that is already UTC | Labels it UTC. It does not convert. |

In ALEAPP, `convert_unix_ts_to_utc` raises an error for text that is not a whole number.
In the other four cores it returns that text unchanged.

## Logging and device information

`logfunc(message)` writes a line to the console, the GUI log and the run's screen log. Use
it for anything an examiner should see in the log, such as a referenced file that is
missing. Do not use `print`.

`device_info(category, label, value, source_file="")` records a device value, such as an
IMEI or account name, for the report's device information page:

```python
device_info('Device Information', 'IMEI', imei, db_path)
```

It works in iLEAPP, ALEAPP and VLEAPP. iLEAPP stores the source path relative to the
extraction. ALEAPP and VLEAPP store it as given, which for a found file includes the
examiner's own folders, so pass `context.get_relative_path(path)` there. In RLEAPP and
DLEAPP it raises `NotImplementedError`.

## Where the five cores differ

As of the commit that added this page.

| | ALEAPP | iLEAPP | RLEAPP | VLEAPP | DLEAPP |
| --- | --- | --- | --- | --- | --- |
| `get_sqlite_db_records` rows | iterator of tuples | iterator of `Row` | iterator of `Row` | iterator of `Row` | list of `Row` |
| `get_plist_file_content`, `get_plist_content` | absent | work | raise `NotImplementedError` | raise `NotImplementedError` | raise `NotImplementedError` |
| `device_info` | source as given | source made relative | raises `NotImplementedError` | source as given | raises `NotImplementedError` |
| `convert_cocoa_core_data_ts_to_utc`, `convert_plist_date_to_utc` | absent | present | present | present | present |
| 2001-epoch converter | `timestampsconv` | `webkit_timestampsconv` | `webkit_timestampsconv` | `webkit_timestampsconv` | `webkit_timestampsconv` |
| `get_binary_file_content` | present | absent | absent | absent | absent |

`check_in_media`, `check_in_embedded_media`, `get_file_path`, `get_txt_file_content`,
`open_sqlite_db_readonly`, `attach_sqlite_db_readonly`, the `does_*_exist_in_db` helpers,
`null_absent_columns` and `logfunc` are the same in all five.
