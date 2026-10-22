# Reddit normalized cache, history and drafts

`redditCache.py` supplements `reddit.py`; it does not replace the Matrix/chat, user-store or subscription artifacts. It reconstructs selected cached content and retained history entries, not a functioning Reddit client or a complete account history. No network requests are made.

## Coverage

| Store | Output | Interpretation boundary |
|---|---|---|
| `Documents/release02/accountData/*/sqlNormalizedCache`, `records` | Root SubredditPost, Comment, Subreddit and Redditor objects; selected referenced content/author/subreddit objects | Cached content can be fetched without being read. Content creation/edit times are not viewing or cache receipt times. |
| `PostHistory` | Ordered `kPostIDDictionaryKey` entries and `kInfoDictionaryKey` entries absent from the list | Positions are zero-based storage positions, not timestamps or proven chronological order. `kGlanceInfoKey` is reported without a behavioral interpretation. Duplicate list entries are retained. |
| `SubredditHistory` | Ordered entries and raw entry JSON | Does not establish subscription, a visit time or deliberate reading. |
| `CommentDraftEntity.sqlite`, `ZCOMMENTDRAFTENTITY` | Draft text, IDs, parent post/comment IDs, modification date | Core Data seconds conversion is synthetic-tested; the private validation table was empty. |

Every row carries a source file. Cache/history/draft rows carry the containing `accountData` directory as Account. This is a source association, not a verified person. Identical object IDs in different account databases are not merged. Draft discovery is restricted to the observed accountData/*/commentDrafts directory; unrelated same-name stores are excluded.

Normalized-cache `$reference` links resolve inside the same database. The parser retains each root object's JSON, its cache key, and selected resolved content JSON. It does not emit child fragments as additional posts/comments. Missing and cyclic links remain reference tokens; traversal is bounded to twelve levels. Full reply-to-comment forests, media relationships and query-root graphs remain in the preserved source database; a cached permalink does not independently prove the parent-child relationship of every comment. Rendered text is ordinary escaped report text, not injected HTML.

Unknown and absent values are kept distinct from stored false/zero. Creation/edit strings are converted only when they contain an explicit timezone, including Z, +HH:MM and the observed +HHMM form on Python 3.10. HH:MM:SS fractional seconds are normalized to six microsecond digits on both runtimes: shorter fractions are padded and longer fractions are truncated, not rounded. Object JSON preserves the original string. Invalid nonempty dates are logged with source, cache key and field. The cache stores ISO timestamps, not NSKeyedArchiver dates. History files use the existing plist/NSKeyedArchiver helper. SQLite opens use the shared read-only helper and include available WAL state; this is not recovery of overwritten or deleted SQLite pages.

## Validation

Data-proven on one private reconstructed iOS 26.2.1 extraction: three normalized caches yielded 594 root posts, 1,029 root comments, 165 subreddits and 677 profiles; six PostHistory files yielded 1,514 list/info entries; three SubredditHistory files yielded 501 entries. Some roots contain only IDs or partial fields. The draft store had no rows. These are sample counts, not deduplicated persons or proof of user activity. App-version applicability beyond this input is unverified.

Synthetic tests cover account separation, reference resolution/cycles, malformed JSON, missing schema, null/false preservation, fractional ISO timestamps, WAL-only rows, source-byte preservation, history duplicate positions and info-only entries, NSKeyedArchiver arrays, and populated draft structure/epoch. Run:

```
python -m unittest admin.test.scripts.test_reddit_cache_history
ILEAPP_LOCAL_IMAGE=/path/to/reconstructed/filesystem python -m unittest admin.test.scripts.test_reddit_cache_history
```

The optional local test reports shapes only. Never commit private extraction files or private generated output. The input in the private validation was a UFDR path reconstruction, so it validates only bytes included in that report archive.

## Stores not decoded by this addition

- `Account.db`, `RoomsUsersService.db`, `RedditUsersStore.db`, `chat.sqlite` and `SubredditSubscriptions`: existing `reddit.py` coverage; this contribution does not claim those parsers cover every table/field.
- `ContentService.db`: cached service payloads require a separate field/format assessment; not assumed equivalent to the Apollo normalized cache.
- Query roots, search/autocomplete/recommendation objects, awards, media objects, comment-forest relationships, wiki/style/configuration fragments: retained in the source but not expanded as separate artifacts. Suggestions/recommendations must not be mislabeled as user searches. Author/profile/subreddit selected references may contain some of these nested values without constituting full coverage.
- Other account configuration plists, `observations.db`, authentication/configuration state and preferences: not interpreted as behavior by this addition.
- CFURL/HTTP/WebKit caches, cookies, local storage, IndexedDB and service-worker stores: separate formats; no claim that generic parsers fully cover them.
- SDK/ad/analytics databases, RemoteConfig, Google measurement, image/avatar caches and executables: excluded from these content/history artifacts. Media bytes are not downloaded, decoded or displayed.
- Notification/OS usage records: separate existing iLEAPP artifacts, not Reddit post read receipts. Runtime testing of the app's history/flag writers was not performed.

Android or other LEAPP core store formats are not covered. No shared-core helper was changed.

## Output audit

Comment output omits unvalidated direct Title, Subreddit ID, Subreddit and URL fields; raw root JSON remains available. Comments expose Post ID (from permalink), Subreddit (from permalink), Cached Post Title and Post Cache Key. A stored Reddit permalink must contain the same comment ID as the root object. Subreddit and user-profile post paths are supported; user-profile paths leave Subreddit blank. Title joins are confined to the same source database; titles are never invented from URL slugs. The comment table leads with creation/edit dates, then account, matched post context, author and text; all 1,029 private comments had creation dates. Post tables lead with account, title, text, author and subreddit because dates are sparse. Artifact notes define timestamp and field meanings and examiner caveats; sample-specific findings and validation results belong in PR or development records.

The comparison run also included unchanged `reddit.py` artifacts. Its contact Blocked and Account ID, message Account ID, subscription Subscribed/Favourite/Muted, and user Is Blocked columns were uniform. Legacy message Image URL/GIF URL and Chats Attachment columns were empty; the focused input omitted media bytes, so this does not establish absence of attachments in the full extraction. Chat Users Matrix User ID/Store Key and Users Is Verified/Is Accepting Chats were identical in the sample. Subscriptions retains Source File alongside Account. These existing-module findings are documented rather than changed by this contribution.

## Audit repairs

Local audit repairs add regression controls for the reported failures. Fabricated case metadata is labeled synthetic, not an acquired iOS version. Unit and strict fabricated regression checks pass on Python 3.10 and 3.12. Other Python runtimes, Windows, packaging, backup/other seekers and native LAVA behavior remain unverified. Module diagnostics use extraction-relative source paths; shared framework helpers may still log absolute local paths.

Display labels use “subreddit”; Reddit’s app calls these Communities. Internal artifact/table identifiers remain stable. Blank entity fields can be absent or explicitly null; Object JSON distinguishes them. Calendar ISO basic forms and hour-only offsets are normalized across Python 3.10/3.12.
