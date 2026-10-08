# Anonymous Chat & Fun parser evidence model

The `anonymousChat` artifacts parse metadata for the iOS application bundle ID
`com.anonimchat.app`. The parser reports stored values and clearly labels
derived direction, grouping, media correlation, and file-type classification.
It does not establish a device owner's identity, whether a message was viewed,
or whether a file was transmitted or received.

## Account and direction evidence

The parser reads `RCTAsyncLocalStorage_V1/manifest.json` only from the app data
container, at either:

- `Library/Application Support/com.anonimchat.app/RCTAsyncLocalStorage_V1/`
- `Documents/RCTAsyncLocalStorage_V1/`

The current location is used by newer React Native AsyncStorage versions. The
`Documents` location is a documented legacy/migration location. React Native's
source establishes the storage layout and MD5 sidecar convention; it does not
establish that this app used the legacy location on a particular device. See
[React Native 0.59.10 AsyncStorage source](https://raw.githubusercontent.com/facebook/react-native/v0.59.10/React/Modules/RCTAsyncLocalStorage.m)
and [AsyncStorage 1.17.11 source](https://raw.githubusercontent.com/react-native-async-storage/async-storage/v1.17.11/ios/RNCAsyncStorage.m).

Account evidence is accepted from explicit account keys (`signedInUsername`,
`loggedInUsername`, `currentUsername`, `accountUsername`, `localUsername`) or
username fields inside named account/session objects. Generic root-level
`username` fields, contacts, message participants, and unrelated cache objects
are ignored. When a manifest value is null, the parser checks only the sibling
whose filename is the MD5 of that explicit storage key. Manifest and sidecar
reads are each limited to 1 MiB; nested JSON traversal is depth-limited.

Identifiers are grouped by source container and extraction root. The Accounts
artifact's Evidence and Source values include the manifest path and, when used,
the hashed sidecar path. Direction is assigned only when one distinct account
identifier matches exactly one conversation endpoint and the stored sender
name agrees with the sender flag (`0` local, `1` remote). Missing, conflicting,
or ambiguous account evidence leaves direction blank and participant labels
unassigned.

## Media associations

A local file is associated only through a recorded relationship:

- A stored path or path-bearing URL matches a local path in the same app
  container and extraction root.
- An SDImageCache filename is the MD5 of the exact stored HTTP(S) URL text.
  The parser hashes URL text only, never media content, and never follows the
  URL.
- A `message_info` media token explicitly joins a message to a media-table row.
- A media-table `media_id` such as `ph://<UUID>` joins to a unique Photos
  `ZASSET.ZUUID` row in the same extraction root, with a safe stored DCIM path.
  A message is linked to that Photos asset only with a separate explicit
  message-to-media join.

A bare filename, container UUID, message ID, size, timestamp, or compatible MIME
type cannot establish a file relationship. Size and MIME metadata may reject a
contradictory stored-path relationship; they do not create one. Ambiguous
relationships stay unlinked. Unlinked filesystem candidates remain in the Media
artifact with the reason recorded. Photos originals may differ from the media
file associated with a message.

Container identity alone does not cross extraction roots. The parser includes
wrapper paths and raw-image volume prefixes in root scoping. ZIP/TAR entries,
directory paths, and iTunes AppDomain/MediaDomain paths use the same root rule;
an unknown or mismatched root fails closed. Photos databases and asset paths
are also partitioned by root.

## File types and timestamps

The exported `Detected File Type` column is retained for compatibility. Its
`Identification Method` states the basis:

- `Filename extension (not content-verified)` is based on the path suffix.
- `Stored MIME metadata` is based on a database value, not file inspection.
- `File signature (first 4096 bytes)` uses a bounded prefix read for eligible
  extensionless folder, ZIP, or TAR candidates only.

Raw-image and iTunes seekers do not provide the parser a bounded header-read
interface; unclassified extensionless candidates stay `Unknown`. No full-file
scan is used. MIME and extension classifications do not verify file contents.

Numeric app timestamps are converted as Unix seconds to UTC by the parser, but
synthetic fixtures do not establish the app's epoch for every version. Message
and media timestamp columns contain the converted value; the message artifact
does not add a separate raw numeric timestamp column. Conversations also expose
`Conversation Timestamp (raw)`. Zone-less text conversation timestamps are not
converted. Folder timestamps describe the supplied copy; ZIP/TAR, iTunes, and
raw-image timestamps retain the input format's own limitations, as described in
the Media artifact notes.

## Validation boundary

Synthetic tests validate the six artifact outputs, supported input wrappers,
correlation rules, and mocked Media Manager calls. Mocked calls do not prove
that a real media item renders correctly in an examiner's report. Real-media
rendering and app-version-specific timestamp epoch validation require separate
authorized validation material.
