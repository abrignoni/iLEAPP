# Offline linked Reddit examiner workspace

This optional companion connects the existing `reddit.py` outputs with the separate
`redditCache.py` cache/history contribution. It reads the report's LAVA database and
manifest; no raw extraction, new parser import, external service or browser download
is required.

```sh
python admin/scripts/build_reddit_reader.py /path/to/iLEAPP_report
```

Open `Reddit_Reader.html` in that report folder. Keep `reddit_reader.html` beside the
builder script: it supplies the self-contained presentation template. This is a
source-tree utility, not an addition to the packaged iLEAPP application.

## Examiner workflow

- **Posts & comments:** cached post cards, associated comments, authors, community,
  content dates, stored score/comment count, and links to history and identity records.
  ID-only posts are optional. A missing root post or missing text is stated explicitly.
- **Post history:** retained list entries open available cached content directly.
  Each source entry/position remains distinct, including duplicate IDs and info-only
  entries. The default linked-only filter can be cleared to see unmatched records.
- **Community history:** stored IDs connect to normalized-cache communities and the
  existing subscription artifact. Descriptions and source-specific states remain visible.
- **Communities:** cache and subscription observations of the same source-account
  community appear together, with related cached content and history links.
- **People & contacts:** cached Redditor profiles, existing Reddit users, Matrix chat
  users and legacy contacts. Exact-ID matches provide source observations and related
  content/chat links. Differing names and flags are not overwritten.
- **Chats:** existing Matrix and legacy conversation grouping/direction, including
  reactions, redactions, unknown direction and attachment references. **Drafts** retain
  unsent text and link to cached posts where supported; this is not a sent-comment claim.

Search, source-account filtering and direct links connect these sections. Identity
groups can retain observations from multiple source accounts. Account and date filters
select individual source rows; linked identities retain their separate observations. Long text wraps inside bounded cards. All original exported fields,
artifact/table row references, source references and relationship bases are expandable.
Where the original artifact supplies only a manifest source, its scope is labeled;
the reader does not claim a new per-row source path.

## Relationship rules

| Relationship | Required evidence and boundary |
|---|---|
| History/draft to a post discussion | Exact post ID, same `accountData` directory including its containing path. Each matching cache store remains a separate candidate. A comment's validated exported post link can support a discussion with no root post. |
| Community history to community observations | Exact community ID, same account directory; both existing subscriptions and new cached communities contribute. |
| Post to community | Exported community ID or explicit `Subreddit:` reference, within the same normalized cache or same source-account directory. |
| Comment to community | Exported validated permalink community name, only when one community ID with that name exists in the same cache. This name-based basis is labeled distinctly from ID matches. |
| Content to cached author | Exact exported author ID and same normalized cache. |
| Content/legacy sender to existing Reddit user/contact | Exact unmodified Reddit ID, same application container. Account-specific states stay in their separate observations; the identity match does not prove matching account ownership. |
| Matrix sender to Matrix user | Exact stored sender/Matrix user ID, same application container, separate from the Reddit ID namespace. |

Missing/contradictory account-directory scope, multiple manifest source paths, absent
IDs and unmatched records never become ID-only joins across unrelated sources.
Equal row IDs in different artifact tables cannot create a relationship. Multiple
matching cache stores are all shown; none is silently chosen as authoritative.
There is no fuzzy username matching, bare-ID prefix guessing or cross-container join.
Raw source field values remain unchanged; borrowed history labels are display context.

This is a partial reconstruction of retained exports. Public comments are grouped by
validated post link within one cache, displayed flat, and not presented as a recovered
reply hierarchy. Missing text/media, forests, deleted records and absent content are
not restored by joining IDs. Content dates are not view dates. History positions and
glance flags are not read receipts, and stored flags do not establish the device
owner's authorship or actions. The reader does not fetch or render external/media content.

## Optional wrapping of existing tables

```sh
python admin/scripts/build_reddit_reader.py /path/to/iLEAPP_report --wrap-tables
```

This explicitly adds idempotent CSS to the report's Reddit HTML pages, supporting both
the current flat `_HTML/Reddit_*.html` layout and nested `_HTML/Reddit/*.html` pages.
Long cells wrap at a bounded width. Wide tables still have many parallel columns;
the workspace is the reading view. By default only the new companion is written.
Neither mode changes database, manifest, TSV or original cell values. Shared iLEAPP
HTML helpers, installed applications and native LAVA conversation views are unchanged.

## Validation and separate contribution

The reader is an independent branch based on the common upstream base, with a
report-data dependency on the cache parser for its newer sections. Existing-only
reports remain usable. Tests use fabricated exports and the real LAVA writer contract.
They cover source/account boundaries, duplicate/missing IDs, multiple candidate caches,
old/new joins, conflicting state preservation, ambiguous sources, Matrix IDs, script
escaping, database immutability and optional table formatting.

The regression suite includes source-preserving joins and actual JavaScript controls.
JavaScript unit checks use Node when available and explicitly skip if it is absent;
the standalone reader itself needs no Node runtime. Browser and native LAVA checks
are separate from Python unit tests. Generated outputs and test logs remain local.

The private validation report contributes 7,072 source rows: 594 posts, 1,029 comments,
2,036 chat events/messages, 231 community observations, 869 Reddit profile observations,
271 Matrix users, 27 legacy contacts, 1,514 post-history and 501 community-history rows.
There are 597 source-separated discussion groups. Post history links 195 entries:
194 to cached root posts and one to comments with no root post. Only six matching
history entries retain a post title. Community history links 81 entries, of which 80
have a retained name; the new cache alone links 45. Existing Reddit-user observations
add exact-ID context for 22 comments. These counts describe this sample only.

Other Python versions/platforms, packaged applications, native LAVA GUI, other report
layouts and large-report performance remain unverified. No private input, generated
report, raw browser dump or case identifier is included in the contribution.

## Review controls and iLEAPP appearance

The reader uses iLEAPP's local Roboto fonts, banner, dark header, sidebar and control
colors. Font and banner data are embedded from the source tree so the reader fetches
no network assets. Chats use left/right conversation bubbles, sender/date labels and
day separators; direction/grouping still come from existing exported roles. Unknown
direction, reactions and redactions remain labeled.

Display options include Light/Dark/System themes, UTC/System/IANA timezones,
YYYY-MM-DD, MM/DD/YYYY and DD/MM/YYYY dates, and 12/24-hour clocks. Every displayed
time includes the resolved timezone and UTC offset, including repeated DST hours.
Original UTC epochs and raw fields remain available. Only theme/time/format/sort
preferences are stored locally; search, accounts, dates and evidence are not persisted.

Sort choices include stored/default order, newest/oldest, title, comment count, row
count and source/position. Undated rows stay last for date sorts; root posts stay
before comments. Date bounds are inclusive calendar days in the selected timezone,
including 23/25-hour DST days. Each record's labeled primary source date is used;
no history view date is invented. Undated records are optional. A post shown only
for context outside the date range is marked and excluded from matching-row exports.
Following an explicit related-record link clears search/account/date filters, with
a notice, so the linked source can be examined.

CSV and JSON downloads offer selected-item matching rows, filtered-list matching
rows, or all Reddit records ignoring filters. Search locates groups/conversations;
date/account filters apply to their rows. Exports record the scope, settings,
resolved timezone, source references, raw fields and relationships. JSON retains
exact raw values. CSV quotes multiline/Unicode fields and prefixes potentially
active spreadsheet text with an apostrophe; exact text remains in its raw-fields
JSON column and the JSON export. Linked references can point to other report rows
outside a selected subset. Print/PDF uses the browser's local print dialog.

## Links from iLEAPP and LAVA

```sh
python admin/scripts/build_reddit_reader.py /path/to/report --wrap-tables --add-navigation
```

`--add-navigation` explicitly extends this generated output report. It preserves the
original LAVA database/manifest under `_Reader_Originals/`, adds a separate **Report
Navigation → Reddit Reader (generated report link)** entry, registers its generated
HTML document through LAVA's existing media/file-opening contract, and adds a top-bar
Reader link to existing iLEAPP HTML pages. The HTML wrapper stays inside `_HTML` and
opens the reader one level above it. It adds no new LAVA view type or application code.

Original extracted rows and original artifact metadata remain unchanged; only
generated navigation rows/media references and their metadata are added. This row is
not evidence or a device artifact. Integration is idempotent. By default the builder
still writes only its own companion, and `--wrap-tables` alone changes only CSS.
These flags target produced report copies, never the UFDR or prepared extraction.
Final cross-platform integration and independent audit remain separate checks.
