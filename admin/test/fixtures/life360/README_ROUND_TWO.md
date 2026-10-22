# Life360 cache and WAL fixtures

All fixture values are fabricated. Generate a new container from the repository root:

```sh
python -m admin.test.fixtures.life360.make_synthetic_round_two /tmp/life360-synthetic-round-two
```

The generator uses ordinary SQLite transactions. Its topic databases contain a main-file record, a later WAL record (including an overflow-payload control), and a final live record. The older records are removed from the final view. The generator captures the main/WAL/SHM bytes before closing the writer, then restores that fabricated snapshot. The native drive fixture supplies a main-file record absent from the current WAL-applied view. Nothing is copied from a device extraction.

The fabricated stores include Z_PRIMARYKEY entity mappings. Decoded Z_ENT must match the selected entity; absent or ambiguous mappings suppress recovery with a diagnostic. A checkpoint/reused-page regression proves that a same-width sibling entity cannot be presented as ZENTRY history. Btree traversal can still depend on later main-file pages after a checkpoint, using current root/schema/entity metadata: this guard does not reconstruct historical schemas or guarantee historical page ownership. If btree assignment fails, eligible committed WAL leaf cells are still checked and receive the distinct btree-assignment-unavailable source state; this condition is logged.

The CFURL cache contains inline JSON, a recorded external JSON filename/body, and a missing external-body reference. The profile creation string intentionally lacks a zone and remains raw. Event/location ISO timestamps have explicit offsets; circle creation uses Unix seconds. Device locations, device ownership, issue objects, circle objects, account data and response availability have independent cases.

The cases use `casesynthetic_round2`; the two case definitions, fourteen artifact ZIPs and recorded baselines cover `life360Cache` and `life360Recovered`. Baselines include page/frame/cell/byte-offset provenance. Archive WAL bytes are fixed test input: do not regenerate expected output from a different WAL or substitute real files.

## Recovery scope

The implementation reads table cells reachable in the main-file view and intact table-leaf cells in checksum-valid committed WAL page images of the current generation. WAL leaves outside the inferred btree are also checked against the current schema/entity and labeled separately, preserving versions that later checkpointed page ownership would otherwise hide. It excludes exact live content while ignoring Core Data bookkeeping columns. It retains changed content under the same identifier and the decoded source appearances of identical recovered content. Historical overflow data must be available from preceding WAL page versions; it is never filled from the main file for a WAL record. Page images do not establish a consistent historical database snapshot or user deletion.

Recovery currently covers ZENTRY in these Life360 topic families: DeviceLocationTopic, FailedLocationTopic, drive_session, trip_session, DriveEvent, DriveCancellationTopic, TripCancellationTopic, DwellTopic, dwell_session, BreachTopic and active_modality. It also covers ZDRIVEMODEL in DriveModelStore.sqlite. Topic records retain their complete stored payload; location, movement, waypoint, incident, geofence and dwell views expose the validated fields separately. Activity-modality details remain in the complete topic payload.

Freeblocks, freelists, old-salt WAL remnants, incomplete transactions and unsupported/incomplete cells are excluded with diagnostics. Individual payloads/bodies above 32 MiB are not decoded. This is not a deleted-row or whole-image carver.

Other EventKit topics (transactiontopic, structuredLogTopic, systemEventTopic, systemErrorTopic, systemRequestTopic, observabilityDataTopic, PowerModeTopic, PowerTopic, SRTTopic, MemberWakeTopic, TakeoffTopic and FlightTopic) need their own payload/epoch assessment. Historical Messaging.sqlite (circles/members), L360CoreDataStore.sqlite (including ZPLACEMODEL Places), UberIntegration.sqlite, Recommendations.sqlite, httpstorages.sqlite and other SDK stores are not recovered by this module. Recovered Places is a follow-up gap requiring its own artifact and fixtures. Historical circle-drive relationships are not joined from a current relationship table. Saved sensor payloads, upload queues, extension-container stores and older unbracketed diagnostic logs remain outside this change.

The cache parser reads only the validated main app's API cache, including exact external-body references under that cache's fsCachedData directory. First-party response metadata is indexed; SDK asset/configuration caches and images are excluded. Cached drives-feed bodies unavailable in the acquired input cannot be decoded. Device-owner IDs are not treated as a full circle-member list. Numeric speeds and accuracy values remain as stored with no additional unit conversion.

External bodies and the fsCachedData directory cannot resolve through symlinks outside that cache. Missing receiver rows are reported as missing bodies. Device Issues Record JSON contains the complete enclosing item and the selected issue. Structural diagnostics are emitted once per distinct message per run; starting another run reports them again.

Waypoints and Incidents use Parent Record Count and Parent Records JSON headers. HTML shows a compact reference to complete parent provenance in the TSV/LAVA export, matched by the explicit Row Key; those exports retain every provenance object. This avoids repeating large parent JSON payloads in each browser row. Missing or null breach JSON timestamps stay blank and are logged; Logged Time remains the independently stored parent timestamp.

## Validation

```sh
python -m unittest admin.test.scripts.test_life360_round_two
python admin/test/scripts/run_test_cases.py --module life360Cache --module life360Recovered
```

Only use fabricated input with the fixture-generation/recording tools. Private validation reports belong outside Git. Public research-image `sample_data` counts must come from actual completed runs; private and synthetic metadata keys are not added to the artifact declarations.

Row Key is a SHA-256 digest of the grouped item and parent-version references, including relative source paths and retained appearances. It links the same output row across HTML, TSV, timeline and LAVA within this report; it is not an app identifier or a stable identifier across changed inputs. Current-schema subentities with another Z_ENT are rejected rather than inferred as the selected entity. No historical allocation status is assigned to WAL leaves outside the inferred btree.
