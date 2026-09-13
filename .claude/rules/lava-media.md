---
paths:
  - "scripts/artifacts/**/*.py"
---

<!-- SHARED FILE. Canonical copy lives in the LAVA repo. Do not edit in place;
     edit the canonical copy and re-run the sync script, or your change will be overwritten. -->

# Show the media, do not just name it

When an app has attachments or references media, surface the media itself in **two** places:

1. A dedicated **attachments/media artifact** with a `('...', 'media')` column, covering the
   referenced files, including files on disk the database does not point at. Give orphans
   their own row rather than dropping them.
2. The **chat or messages artifact** for that app, with the media rendered inline on the
   row it belongs to, and `mediaColumn` set in the `data_views.conversation` block so it
   also appears in LAVA's conversation view.

A file name and a size in a table are not the evidence. The examiner needs to see the
picture, and a media column is what makes a conversation readable as a conversation.

## How

- Add the on-disk media locations to the artifact `paths`, not just the database path.
- Index the files by whatever key the database uses: content id, uuid, or file name.
- Register with `check_in_media`, or `check_in_embedded_media` when the bytes were decrypted
  or carved in memory rather than read from a file.
- **Sniff the content, do not trust the extension.** Some apps store PNG bytes in a file
  named `.jpg`.
- Watch the tuple width when adding a media column. A header/value mismatch raises a binding
  error, or worse, silently shifts every column right.
