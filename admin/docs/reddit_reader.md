# Reddit Reader

An offline companion that combines existing iLEAPP Reddit results with the separate
cache/history parser's outputs. It needs the report's `_lava_data.lava` and
`_lava_artifacts.db`; older-only reports remain usable.

```sh
python admin/scripts/build_reddit_reader.py /path/to/report --wrap-tables --add-navigation
```

Open `Reddit_Reader.html`. Keep `reddit_reader.html` and
`reddit_reader_controls.js` beside the builder. Run from an iLEAPP source tree;
this utility is not part of the packaged application.

## Reading the results

- **Posts & comments:** retained text, author/community, source dates and stored
  states. Comments link to a post through the exported validated permalink.
  Missing root posts/text stay explicit; reply nesting is not reconstructed.
- **Post/community history:** each stored entry keeps its source and position.
  Exact IDs link to retained content or community records in the same account
  directory. Multiple cache candidates stay separate. Uncheck “Only linked
  history” to see unmatched entries.
- **Communities/people:** cached and older-parser observations are shown together
  when explicit IDs and source scope support the relationship. Each card retains
  its own names, flags and provenance; conflicting values are not overwritten.
- **Chats:** existing iLEAPP conversation grouping and direction, with sender,
  timestamp and day separators. Unknown direction, reactions and redactions are
  labeled. Attachment references do not cause media downloads.
- **Drafts:** retained unsent text, parent/post context and modification dates.

“All exported fields and source references” shows the original fields, source
reference scope and the basis of each link. Account identifies a source account
directory, not a verified person. A manifest-only source is labeled accordingly.
Cached content/history does not establish reading, intent or device-owner authorship.

## Dates, filters and exports

Choose Light/Dark/System theme, UTC/System/IANA timezone, YYYY-MM-DD/MM-DD/DD-MM
date order, and a 12/24-hour clock. Displayed times include the timezone and UTC
offset; raw UTC epochs remain available. Theme/time/format/sort preferences are
stored locally. Evidence, search/account selections and date bounds are not saved.

The date label identifies the source field used for each record: content creation
for posts/comments, server/message time for chats, profile/community creation,
Matrix-user update, or draft modification. History has no inferred view date.
Blank/invalid dates remain undated. Bounds include each whole selected calendar
day in the chosen timezone, including daylight-saving changes. The undated option
controls whether those rows remain visible.

Search finds groups/conversations; account/date filters select their source rows.
A root post outside the date range may appear as marked context and is excluded
from matching-row exports. Following a related-record link clears search/account/
date filters with a notice. Sorts include stored/default order, source/position,
newest/oldest, title, comment count and row count. Date sorts put undated items last.

CSV/JSON export scopes are selected item, filtered list, or all Reddit records
ignoring filters. Exports include scope/settings, resolved timezone, raw fields
and source references. JSON preserves raw values. CSV prefixes potentially active
spreadsheet text with an apostrophe; exact text remains in Raw fields JSON and the
JSON export. Links may refer to rows outside an exported subset. Print/PDF uses
the browser's print dialog for the current view.

## Relationship boundaries

History/post/community links require exact IDs and the complete source-account
directory. Discussions stay separate by source cache. Content-author links use
exact IDs in the same cache; older Reddit-user/contact matches require the same
application container. Account-specific states remain separate observations.
Matrix IDs use their own namespace. Comment-community name matches are permitted
only for the exported validated permalink and a unique same-cache community ID.
Each basis is labeled. No fuzzy username, guessed ID prefix or cross-container join
is made. Missing IDs cannot group unrelated table-local row numbers.

## Report integration

By default only the companion is written. `--wrap-tables` adds bounded wrapping CSS
to existing Reddit HTML pages; it leaves cell text, TSV, database and manifest intact.

`--add-navigation` explicitly extends a generated report copy: it retains the
original database/manifest under `_Reader_Originals`, adds a **Report Navigation →
Reddit Reader** document link in LAVA, and adds a Reader link to iLEAPP HTML headers.
Original extracted rows and artifact metadata stay unchanged. Added navigation
rows/media references are generated report content, not device evidence. The HTML
wrapper resolves inside the report, so the directory can be moved intact. Repeated
integration is idempotent; incomplete backups/name collisions are rejected.

The reader uses iLEAPP's local fonts/banner and conversation styling. No network
content is fetched. Neither installed iLEAPP/LAVA nor their shared renderers change.
Parser and reader are separate contributions; the newer sections need the parser's
report tables. Validation, sample counts and platform gaps belong in the PR and
development records rather than examiner-facing notes.
