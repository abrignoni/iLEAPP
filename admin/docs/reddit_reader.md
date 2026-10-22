# Offline Reddit report reader



Existing `reddit.py` artifacts keep their native LAVA `data_views.conversation` settings: Matrix rooms use Room ID, and legacy chat messages use Channel URL. Time, sender, direction and media settings survive the report manifest. This addition does not alter those chat parsers or declare public content to be sent/received messages.

An optional local reader supplies separate Chats and Cached discussions tabs from the report's existing LAVA database:

```
python admin/scripts/build_reddit_reader.py /path/to/iLEAPP_report
```

Open `Reddit_Reader.html` in that report folder. It supports search, account filters, author/date display, explicit reaction/redaction labels, unknown chat direction, and artifact/table-row/source references. It uses the exported chat configuration for grouping and direction. Missing chat IDs remain separate rather than merging unrelated messages. Public discussions group by source file, account and validated post ID. ID-only post records are hidden by default and can be included. Unlinked comments remain individual records. This flat display does not claim reply nesting, complete threads, reading, or authorship by the device owner. Own flags remain labeled as stored. The underlying HTML/TSV/LAVA tables remain available.

The reader embeds text safely, fetches no external content, and writes only its own HTML file. It is an optional report companion, not a change to LAVA or iLEAPP's general HTML renderer. The public normalized-cache tables preserve records even when no post link can be established. Chat presentation is checked against the installed LAVA reader contract; no hosted CI or runtime app experiments are implied.

Presentation validation on the private sample: the existing chat views retain 2,027 Matrix events and 9 legacy messages; the reader presents 594 cached post rows and 1,029 comment rows across 597 source/account/post groups. All 1,029 comments have a matching stored permalink; three discussion groups lack a corresponding cached post row. A post title was available for only 28 comment rows in the same cache, so missing titles remain explicit. Browser checks exercised tab navigation, card display, search and the ID-only filter.

## Separate contribution

This optional report presentation has no artifact module changes. Chats use the existing Reddit artifacts. Cached discussions are available only when the separate normalized-cache parser contribution has supplied those tables; a chat-only report remains usable. Missing discussion links use artifact-table plus row identifiers, so equal table-local row IDs cannot imply a post/comment relationship.

The reader is a local HTML companion, not a modification of LAVA's native conversation view. Tests create fabricated LAVA tables and use the real LAVA writer contract; none requires private case files or the new parser module to import.
