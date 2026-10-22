# Private Photo Vault ECD and diagnostic activity

`privatePhotoVaultEcd.py` adds support alongside the older `privatePhotoVault.py` Core Data artifacts. It reads plaintext SQLite or an already decrypted `PPV.ecd.decrypted`. It does not perform decryption, access credentials, fetch cloud content or decode/display media.

## Stores and fields

- `ecdPersistentAlbum`: identifiers, title, parent reference, selected flags and creation/modification/deletion dates. Passwords are excluded.
- `ecdPersistentMediaItem`: sync and album IDs, file type/extension, dimensions, selected state fields, byte size, date fields and **l_viewCount as stored**. Encryption keys are excluded. Album IDs allow a source-scoped join to the album output; equal sync IDs in different stores are not merged.
- `ecdPersistentMediaItemPart`: part/media IDs, sizes, offsets, content hashes and selected local/cloud-state values. The validation input had no rows; populated coverage is synthetic-tested only.
- `ecdPersistentTresspassRecord` (spelling as stored): date, login type, device name, coordinates and file references. The validation input had no rows; populated coverage is synthetic-tested only. A table name is not proof that every record represents a failed login. File and thumbnail references are emitted as text only; this artifact selects no media bytes and performs no decryption/rendering.
- `Library/*_MPDB.sqlite`, `mixpanel_*_events`: event names, `properties.time`, session length, `sessionParams.itemsViewed`, `albumsViewed` and gallery/thumbnail metrics. Complete event JSON, source table, row ID, source file, both bundle IDs and App Association accompany the selected fields.
- `Library/Caches/com.crashlytics.data/com.enchantedcloud.photovault/*/log_*.clsrecord`: newline-delimited JSON `log` records with hexadecimal UTF-8 `msg` and Unix-millisecond `time`. Physical line numbers, raw time, hex and decode status are retained. Malformed JSON and unsupported log shapes are logged with source/line context and skipped; an undecodable hex message keeps a row and its raw hex.

The ECD schema's dates were observed as Unix seconds, including fractions. Selected Metadata JSON retains their original values. These are not all view dates. A stored zero is displayed literally as 1970-01-01 UTC; whether the app uses zero for an unset date is unverified. Invalid or out-of-range dates display blank, with the raw value retained in Selected Metadata JSON. Missing, zero and nonzero counter values remain distinct; optional missing columns remain blank. No date/enum field is promoted into an operator attribution.

Mixpanel is not unique to PPV. The association policy is:

1. Check **both** `properties.bundleId` and `properties.sessionParams.bundleId`. Null and empty strings are absent. Any other value that differs from `com.enchantedcloud.photovault` rejects the event, even when the other field matches. Both IDs are exposed in the output.
2. A matching explicit ID accepts the event independently of an ECD store. This is a stored label, not an independent guarantee about the writer.
3. With neither ID, require a supported ECD schema or matching `MCMMetadataIdentifier` in the **same** `/Containers/Data/Application/<container>/` directory. Container metadata is read only from `.com.apple.mobile_container_manager.metadata.plist` directly under that container, not a same-name nested file.
4. A decrypted/plaintext store must contain at least one supported ECD table signature: media (`__objectid`, `syncId`, `albumSyncId`), album (`__objectid`, `syncId`, `title`), part (`__objectid`, `syncId`, `mediaItemSyncId`), or trespass (`__objectid`, `syncId`, `loginType`). An unrelated SQLite file named `PPV.ecd.decrypted` does not qualify. Non-SQLite `PPV.ecd` bytes alone do not establish encryption or app identity. Independent container metadata permits analytics association when that store cannot be decoded; no media/album rows are invented.

`App Association` records the acceptance basis. Rejected/unattributed events are logged with source file, table and row ID; unsupported tables do not suppress later valid tables. Generic SDK events sharing the app container are not thereby established as PPV UI actions. Backup layouts without the container path cannot use this fallback.

`properties.time` in the validation input uses both seconds and milliseconds. Numeric absolute values at least 100,000,000,000 are divided by 1,000; the divisor and raw value are exposed. This is a modern-event unit heuristic, not a universal date inference. Invalid/nonfinite timestamps remain blank while the raw value is retained. **The SQL queue time column is not substituted for event time.** Diagnostic log time uses its observed millisecond unit, separately.

Neither `itemsViewed` nor `l_viewCount` identifies the operator, proves deliberate/full-size rendering, counts unique images by definition, or establishes a per-file sequence of views. Session metrics must not be subtracted from individual media counters. A diagnostic message is reported text, not a verified description of human behavior.

## Validation

Data-proven on one private reconstructed iOS 26.2.1 extraction: 12 album rows, 865 media rows, 98 Mixpanel event rows and 13 diagnostic log rows. Parts and trespass tables were empty. App analytics in that input report version 23.9.2; this is not an independent binary-version verification or support claim for other versions. No private values are committed.

Synthetic tests exercise null versus zero, fractional Unix dates, optional columns, multiple containers with equal IDs, excluded passwords/keys, populated part/trespass rows, mixed event units, misleading queue timestamps, session metrics, unrelated Mixpanel rejection, explicit bundle identity without ECD, malformed JSON, non-plaintext-store refusal, verified-container identity without readable ECD, false filename markers, all outer/session identity combinations, malformed-table isolation, oversized event/diagnostic times, WAL-visible changes without source-byte modification, and hex/UTF-8 diagnostic decoding including invalid records.

```
python -m unittest admin.test.scripts.test_private_photo_vault_ecd
ILEAPP_LOCAL_IMAGE=/path/to/reconstructed/filesystem python -m unittest admin.test.scripts.test_private_photo_vault_ecd
```

The optional corpus test checks row structure without printing values and is skipped in hosted CI unless local input is explicitly supplied. Read-only SQLite access can create SHM reader state; source DB/WAL bytes are checked separately in tests. Live SQLite/WAL visibility is not recovery of overwritten pages.

## Deliberate exclusions and validation boundaries

- `PPVCoreData.sqlite`: existing older parser remains unchanged.
- Non-plaintext/encrypted `PPV.ecd` and PPV_Pics media: no cryptographic recovery, media rendering or inferred filename reconstruction. Corroborated container metadata can associate analytics without decoding ECD. The encrypted-store identity control uses fabricated non-SQLite bytes, not a verified public encrypted acquisition; genuine encrypted-store validation remains open. Plaintext/decrypted variants beyond the observed suffix are unvalidated.
- `meta` and password/encryption-key columns: excluded from reported selected metadata.
- Mixpanel people/groups: profile/analytics bookkeeping, not a chronological activity log; not exposed as events. Event payload JSON may contain device/account identifiers for local examiner review.
- Crashlytics binary_images, internal_incremental_kv, settings.json, cache-key.json and other metadata: not decoded as diagnostic messages; only the observed log JSON format is supported. Other crash SDK versions are unvalidated.
- Preferences, advertising/measurement SDK stores, `Library/Caches/com.enchantedcloud.photovault/Cache.db`/`fsCachedData`, HTTPStorages `httpstorages.sqlite`, other HTTP/WebKit caches and executables: not decoded here. No guarantee that a generic parser covers these stores.
- UI action-to-counter causation, every writer of a state flag, cross-device sync effects, and operator attribution: not established by this parser. No runtime app experiments are claimed.

These are iOS-specific additions. No shared-core helper or other LEAPP core was changed.

## Audit repairs

Local audit repairs add regression controls for the reported failures. Fabricated case metadata is labeled synthetic, not an acquired iOS version. Test/runtime results and remaining validation limits are recorded in the local review handoff; passing Python 3.10 and 3.12 checks does not establish untested runtimes, Windows, packaging or native LAVA behavior.
