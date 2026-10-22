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
groups can retain observations from multiple source accounts; the filter selects
groups containing that account and their headers/details still identify every retained
observation. Long text wraps inside bounded cards. All original exported fields,
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

Python 3.10/3.12 focused and full suites pass. Desktop/mobile browser checks cover
real-data navigation, combined observations, filters, source details and wrapping;
fabricated long words and script-closing text remain inert. Twelve real table pages
retain byte-identical cell content after removing only the added CSS. Real LAVA
database/manifest bytes and reader records match across both runtimes.

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
