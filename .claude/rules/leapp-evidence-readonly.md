---
paths:
  - "scripts/artifacts/**/*.py"
---

<!-- SHARED FILE. Canonical copy lives in leapps-org/leapps-parity. Do not edit in place;
     edit the canonical copy and re-run the sync script, or your change will be overwritten. -->

# An artifact must never write to evidence

The file an artifact receives is the extracted copy the report preserves in its `data/`
folder and records timestamps for. Writing to it corrupts what the report presents as the
source. This is not a style rule.

**Three** patterns count as violations, and the third is the one audits miss:

1. `open(path, 'w')` (or `'a'`, `'x'`) on a source file, including to "repair" malformed
   input before parsing.
2. `sqlite3.connect(path)` instead of `open_sqlite_db_readonly()` from `ilapfuncs`.
3. A hand-built `ATTACH DATABASE "<path>"` statement. **SQLite opens an attached database
   read-write no matter what mode the primary connection used**, so
   `open_sqlite_db_readonly()` on the main database does not protect the attachment. Use
   `attach_sqlite_db_readonly()` from `ilapfuncs`, which builds the statement with a
   `file:<path>?mode=ro` URI and percent-encodes spaces, `#` and `%` in the path.

## Instead

- To handle malformed XML, read the text and fix it **in memory**, then parse. A sweep that
  rewrote a first line changed the file's bytes and mtime and produced the exact same rows,
  so the write bought nothing.
- For SQLite always use `open_sqlite_db_readonly()`, and handle a `None` return.
- Writing into `report_folder` is fine. That is output, not evidence.

## Auditing for it

Grep for all three, not the obvious two. A sweep that checked only `sqlite3.connect(` and
write-mode `open()` reported a directory clean and missed four `ATTACH` call sites:

```
sqlite3.connect(
open\([^)]*, *['"][wax]
attach database          (case-insensitive)
os.remove|rename|replace|chmod|truncate|shutil.move
```

Expect false positives worth knowing rather than re-flagging: connecting read-write to a
module's *own* `tempfile.mkstemp()` cache or its own decrypted temp copy is correct, and
`:memory:` is not evidence.

A read-only WAL open still creates a `-shm` file, because SQLite requires one for readers.
Claim only that no evidence file is altered, never "no side effects".
