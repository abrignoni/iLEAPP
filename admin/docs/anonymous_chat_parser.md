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

Container identity is `(extraction root, container type, container UUID)`. A
bundle is admitted from a matching `Info.plist` bundle identifier, matching
container-manager metadata, or matching iTunes store metadata. A data container
is admitted from matching container-manager metadata, the app's preference
plist path, or the exact `AppDomain-com.anonimchat.app` iTunes domain. An app
group is admitted only from target-app group metadata or a group identifier
listed by that root's verified bundle. These checks are performed per root;
another extraction's matching UUID cannot authorize a database, manifest,
group, or media file. Account rows are also kept per data container, even when
the displayed account string repeats.

Before deriving a root or container identity, staged paths are mapped back with
iLEAPP's `Context.get_relative_path()` through the parser's `_source_label()`
helper. This removes the report's temporary data-folder prefix. Folder, ZIP,
and TAR seekers retain their evidence-relative paths; the iTunes seeker maps
AppDomain and CameraRoll/MediaDomain members to the corresponding iOS paths.
The root is the prefix before the first recognized `private/var` or `var`
system path, with container and `Media/PhotoData` anchors as fallbacks for
partial paths. An unwrapped extraction therefore has the empty prefix within
that single run. A wrapper directory (ZIP/TAR/folder) or raw-image volume
prefix is retained, so identical container UUIDs in separate roots stay
distinct. If no recognized anchor exists, the root is unknown and the
association is left unconfirmed.

Photos matching uses the same evidence-relative conversion for every staged
`Photos.sqlite` path before comparing it with app database references. The
seeker stages `Photos.sqlite` and its adjacent WAL when present; SQLite reads
are read-only and include committed WAL records where applicable. Exactly one
Photos database must be available in the matching root. A stored `ph://UUID`
must match one unique `ZASSET.ZUUID`, and its stored directory and filename
must form a safe relative `DCIM/` path. Duplicate databases, duplicate asset
UUIDs, unsafe paths, duplicate path owners, missing databases, and unknown or
mismatched roots remain unlinked. Linking a Photos original to a message still
requires a separate, unique explicit app message-to-media join. No filename,
size, or timestamp similarity creates a relationship.

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

Synthetic tests validate the six artifact outputs and LAVA conversation view
through end-to-end CLI runs for folders, ZIP, TAR, and iTunes backups (including
a Photos database). Wrapped ZIP/TAR roots and duplicate-UUID roots are also
exercised through the CLI. The available generic NTFS image completes a raw
CLI smoke run but contains no iOS/app evidence, so it emits no Anonymous Chat
artifact group. A raw-seeker staging test uses a synthetic reader/member to
exercise real raw staging and `Context.get_relative_path()` with a volume
prefix; the repository does not contain an iOS raw image with Photos metadata,
so raw-image Photos correlation has not been validated end to end. Unit tests
cover WAL-only asset records, ambiguous/missing/invalid databases, repeated
asset UUIDs, unsafe DCIM paths, and extraction-root isolation. Mocked Media
Manager calls do not prove that a real media item renders correctly in an
examiner's report.
Real-media rendering and app-version-specific timestamp epoch validation
require separate authorized validation material.
