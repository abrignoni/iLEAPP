"""
Extracts and processes device synchronization information from the
    Biome Device Sync database.
"""

__artifacts_v2__ = {
    "biome_sync": {
        "name": "Biome - Device Syncs",
        "description": "Device records from the DevicePeer table of Biome's sync.db, with platform, OS build and last sync time where recorded",
        "author": "@JohnHyla",
        'creation_date': '2023-03-22',
        'last_update_date': '2026-09-26',
        "requirements": "none",
        "category": "Biome",
        "notes": (
            "Reads the DevicePeer table of Biome's sync.db, one row per device record. Local "
            "Device is Yes where the me column is 1. On the 19 registered iOS images carrying the "
            "database, Name held an empty string on all 38 rows, and Last Sync Timestamp was "
            "empty on the Local Device row of each image (last_sync_date is NULL there) and "
            "filled on every other row. Platform (as stored) is the integer in the platform "
            "column. Device Type is the name Apple's BMDevicePlatformToString returns for that "
            "integer: 0 Unknown, 1 iPad, 2 iPhone, 3 MacDesktop, 4 MacPortable, 5 TV, 6 Watch, 7 "
            "HomePod, 8 Vision, measured by calling the function in the BiomeSync framework on "
            "macOS 26.6.2 (build 25G83). Any other value leaves Device Type blank. On the same "
            "system BiomeFoundation's BMDevicePlatformFromModelString returned 7 for "
            "AudioAccessory model identifiers, 5 for AppleTV ones and 8 for RealityDevice ones. "
            "That DevicePeer stores this enumeration is inferred rather than sourced: BiomeSync's "
            "BMDevice class carries five of the table's fields (device identifier, IDS device "
            "identifier, name, model and platform), with model a string and platform an integer, "
            "and on the tested images the text builds on platform 2 rows resolved to iOS "
            "versions, on platform 1 to iPadOS, on 3 and 4 to macOS and on 6 to watchOS. The "
            "table declares model as STRING, which SQLite gives NUMERIC affinity (Reference: "
            "SQLite, 'Datatypes In SQLite', sections 3.1 and 3.1.1, "
            "https://www.sqlite.org/datatype3.html), so a build made of digits, the letter E and "
            "digits is stored as a number. OS Build reports model when it is stored as text. A "
            "numeric model is reported in Model Stored as Number, as the shortest decimal that "
            "reads back to the stored value, with OS Build and OS Version blank. The build is not "
            "rebuilt from the number, because the conversion loses information: inserted into a "
            "test table's STRING column, 20E247 is stored as 2.0e+248 and 23E5 as the integer "
            "2300000. On those images 3 of the 38 rows, on 3 images, held a number. OS Version is "
            "looked up from OS Build for iPhone, iPad, Mac, TV, Watch and Vision rows. It is left "
            "blank for HomePod rows: the lookup table has no HomePod group, and the builds on the "
            "3 tested HomePod rows are listed in it as tvOS builds, a name not applied to a "
            "HomePod. OS Build is the build this table holds for the device, not necessarily the "
            "build installed at acquisition: on the Local Device row it matched the build the iOS "
            "Information artifact reported for the image on 14 of the 19 tested images and "
            "differed on 5, one of them the numeric row."),
        "paths": ('*/Biome/sync/sync.db*'),
        "output_types": "standard",
        'artifact_icon': 'eye',
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 2 rows",
            "felix_ios17": "iOS 17.6.1 | 6 rows",
            "fsfull002_ios17": "iOS 17.1 | 1 row",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 5 rows",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
            "otto_ios17": "iOS 17.5.1 | 2 rows",
            "abe_ios16": "iOS 16.5 | 1 row",
            "felix23_ios16": "iOS 16.5 | 2 rows",
            "jess_ios15": "iOS 15.0.2 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 1 row",
            "adams_iphone12mini": "iOS 17.1.1 | 4 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 3 rows",
            "falken_ios26": "iOS 26.2.1 | 2 rows",
            "hc_ios26": "iOS 26.5.2 | 2 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 1 row",
            "hickman_ios15": "iOS 15.3.1 | 1 row",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 1 row",
        }
    },
    "biome_sync_merged_events": {
        "name": "Biome - Sync Merged Events",
        "description": "Merge results Biome's sync service logged for stream records, with each record's owning device",
        "author": "@AlexisBrignoni, Claude",
        'creation_date': '2026-09-26',
        'last_update_date': '2026-09-26',
        "requirements": "none",
        "category": "Biome",
        "notes": (
            "Reads AtomMergedLog in Biome's sync.db. Each row is a merge result for one Biome "
            "stream record, with the device that owns the record; biomesyncd carries a method "
            "named "
            "recordAtomMergeResult:inStream:sessionID:messageID:ownerSite:originatingSite:eventCreatedAt:, "
            "whose parameters match the table's columns. No column identifies the stored record "
            "itself (an identifier or a storage location), so the record's content, such as which "
            "app an AppLaunch record names, is not reported. Synced At and Event Created At are "
            "read as seconds since 2001-01-01 (Cocoa), unlike DevicePeer's last_sync_date, which "
            "is Unix seconds: on falken_ios26 the latest synced_at read as Cocoa seconds equals, "
            "to the second, the latest last_sync_date read as Unix seconds, and on all 369 rows "
            "carrying both, Event Created At is at or before Synced At. Event Created At is left "
            "blank where it is stored as 0. Merge Result is the name biomesyncd's own naming "
            "function, the one behind its 'Merge result: %@' log line, gives the value in Merge "
            "Result (as stored): 1 DroppedDuplicate, 2 CausalityViolation, 3 Merged, read from "
            "the x86_64 slice of /usr/libexec/biomesyncd on macOS 26.6.2 (build 25G83). Other "
            "values leave Merge Result blank. That this function names the merge_result column is "
            "inferred from that log line and from the data: on the 9 registered iOS images with "
            "rows, all 533 rows with Owned by Local Device Yes were DroppedDuplicate with Event "
            "Created At empty, all 369 Merged rows were owned by another device and carried an "
            "Event Created At, and 230 more rows owned by another device were DroppedDuplicate. "
            "Owning Device ID is owning_site_identifier, which matched a DevicePeer row on all "
            "1,132 rows. Owning Device Type and Owning Device OS Build come from that row as "
            "Biome - Device Syncs reports them, so Owning Device OS Build is blank where "
            "DevicePeer stores model as a number (all 26 rows of one image). Relayed By Device ID "
            "is reported as stored: it equalled Owning Device ID on 349 rows and named no "
            "DevicePeer device on the other 783. Session Transport (as stored) and Session Reason "
            "(as stored) come from the SyncSessionLog row with the same session id, which existed "
            "for all 1,132 rows. biomesyncd was checked for names for either code, in its string "
            "constants and its name tables, and holds none, so both are reported as stored. "
            "Stream is the Biome stream name as stored: AppLaunch on 1,037 rows, NowPlaying on "
            "86, and two identifiers written as UUIDs on 9. Within one image the values were "
            "often uniform: Stream, Merge Result, Owning Device ID, Owning Device Type, Session "
            "Transport (as stored) and Message ID each held one value on all rows of 7 of the 9 "
            "images, Session Reason (as stored) on 8, Owning Device OS Build and Owned by Local "
            "Device on 6, Relayed By Device ID on 5, and Synced At and Session ID on 3. Event "
            "Created At was empty on all rows of 6 images, and Owned by Local Device and Owning "
            "Device OS Build were each empty on all rows of 1 other image. DevicePeer and "
            "SyncSessionLog held no repeated identifier on any tested image, so the joins added "
            "no rows; neither table declares a unique constraint that guarantees this."),
        "paths": ('*/Biome/sync/sync.db*'),
        "output_types": "standard",
        'artifact_icon': 'refresh',
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 149 rows",
            "felix_ios17": "iOS 17.6.1 | 9 rows",
            "fsfull002_ios17": "iOS 17.1 | 19 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 63 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 88 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 540 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 6 rows",
            "falken_ios26": "iOS 26.2.1 | 232 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 26 rows",
        }
    },
    "biome_sync_messages": {
        "name": "Biome - Sync Messages",
        "description": "Sync messages Biome logged with peer devices, with the peer's platform and the session codes as stored",
        "author": "@AlexisBrignoni, Claude",
        'creation_date': '2026-09-26',
        'last_update_date': '2026-09-26',
        "requirements": "none",
        "category": "Biome",
        "notes": (
            "Reads SyncMessageLog in Biome's sync.db: one row per entry, each naming a peer "
            "device. Timestamp is read as seconds since 2001-01-01 (Cocoa), the epoch of the sync "
            "log tables described in Biome - Sync Merged Events. Peer Device ID matched a "
            "DevicePeer row on all 21 rows of the 6 registered iOS images with rows. Peer Device "
            "Type and Peer OS Build come from that row as Biome - Device Syncs reports them. "
            "Reachable (as stored), Reciprocal (as stored) and Atom Batch Bytes are the "
            "reachable, is_reciprocal and atom_batch_bytes columns as stored; their meaning "
            "beyond the column names is not established. Reachable (as stored) held 1 on all 21 "
            "rows. Session Transport (as stored) and Session Reason (as stored) come from the "
            "SyncSessionLog row with the same session id, which existed for 16 of the 21 rows. "
            "Session Transport (as stored) and Session Reason (as stored) are empty on the other "
            "5, and on all rows of 3 images. Session Transport (as stored) held 2 on all 16 rows "
            "where it was filled. biomesyncd holds no names for either code, so both are reported "
            "as stored. Within one image the rows came from one peer: Peer Device ID, Peer Device "
            "Type, Peer OS Build, Reachable (as stored) and Message ID held one value on all rows "
            "of each of the 6 images."),
        "paths": ('*/Biome/sync/sync.db*'),
        "output_types": "standard",
        'artifact_icon': 'link',
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 12 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 1 row",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 3 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 3 rows",
            "hc_ios26": "iOS 26.5.2 | 1 row",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, \
    get_sqlite_db_records, convert_unix_ts_to_utc, \
    convert_cocoa_core_data_ts_to_utc


# Names returned by Apple's BMDevicePlatformToString for each value.
PLATFORM_NAMES = {
    0: 'Unknown',
    1: 'iPad',
    2: 'iPhone',
    3: 'MacDesktop',
    4: 'MacPortable',
    5: 'TV',
    6: 'Watch',
    7: 'HomePod',
    8: 'Vision',
}

# Names returned for a merge result by biomesyncd's own naming function, the
# one behind its "Merge result: %@" log line. Other values it names Unknown.
MERGE_RESULT_NAMES = {
    1: 'DroppedDuplicate',
    2: 'CausalityViolation',
    3: 'Merged',
}

# Device family passed to the build lookup. HomePod and unnamed values are
# left out, so no OS version is looked up for them.
BUILD_LOOKUP_FAMILY = {
    1: 'iPad',
    2: 'iPhone',
    3: 'Mac',
    4: 'Mac',
    5: 'AppleTV',
    6: 'Watch',
    8: 'RealityDevice',
}


@artifact_processor
def biome_sync(context):
    """
    Extracts and processes device synchronization information from the
    'sync.db' SQLite database.
    """

    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'sync.db')
    data_list = []

    query = '''
        SELECT
            last_sync_date,
            device_identifier,
            name,
            platform,
            model,
            typeof(model),
            CASE me
                WHEN 0 THEN ''
                WHEN 1 THEN 'Yes'
            END AS 'Local Device'
        FROM DevicePeer
    '''

    data_headers = (('Last Sync Timestamp', 'datetime'), 'Device ID', 'Name',
                    'Device Type', 'Platform (as stored)', 'OS Build',
                    'OS Version', 'Model Stored as Number', 'Local Device')

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        timestamp = convert_unix_ts_to_utc(record[0])
        platform = record[3]
        device_type = PLATFORM_NAMES.get(platform, '')
        os_build = ''
        os_version = ''
        model_number = ''
        if record[5] == 'text':
            os_build = record[4]
            family = BUILD_LOOKUP_FAMILY.get(platform)
            if family:
                os_version = context.get_apple_os_version(os_build, family)
        elif record[5] in ('real', 'integer'):
            # The column's NUMERIC affinity turned a build such as 22E240
            # into a number. The build is not rebuilt from it.
            model_number = repr(record[4])

        data_list.append((timestamp, record[1], record[2], device_type,
                          platform, os_build, os_version, model_number,
                          record[6]))

    return data_headers, data_list, source_path


def _cocoa_or_blank(value):
    """A Cocoa timestamp as UTC, with a zero or empty value left blank."""
    if not value:
        return None
    return convert_cocoa_core_data_ts_to_utc(value)


def _peer_build(model, model_type):
    """The peer's build when model is stored as text, otherwise blank."""
    return model if model_type == 'text' else ''


@artifact_processor
def biome_sync_merged_events(context):
    """
    Reports AtomMergedLog: Biome stream records merged into this device's
    store during a sync, with the device that owns each record.
    """

    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'sync.db')
    data_list = []

    query = '''
        SELECT
            a.synced_at,
            a.event_created_at,
            a.stream,
            a.merge_result,
            a.owning_site_identifier,
            p.platform,
            p.model,
            typeof(p.model),
            p.me,
            a.relayed_by_site_identifier,
            s.transport,
            s.reason,
            hex(a.session_id),
            a.message_id
        FROM AtomMergedLog a
        LEFT JOIN DevicePeer p
            ON p.device_identifier = a.owning_site_identifier
        LEFT JOIN SyncSessionLog s
            ON s.session_id = a.session_id
        ORDER BY a.synced_at
    '''

    data_headers = (('Synced At', 'datetime'), ('Event Created At', 'datetime'),
                    'Stream', 'Merge Result', 'Merge Result (as stored)',
                    'Owning Device ID', 'Owning Device Type',
                    'Owning Device OS Build', 'Owned by Local Device',
                    'Relayed By Device ID', 'Session Transport (as stored)',
                    'Session Reason (as stored)', 'Session ID', 'Message ID')

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        data_list.append((
            _cocoa_or_blank(record[0]), _cocoa_or_blank(record[1]), record[2],
            MERGE_RESULT_NAMES.get(record[3], ''), record[3], record[4],
            PLATFORM_NAMES.get(record[5], ''), _peer_build(record[6], record[7]),
            'Yes' if record[8] == 1 else '', record[9], record[10], record[11],
            record[12], record[13]))

    return data_headers, data_list, source_path


@artifact_processor
def biome_sync_messages(context):
    """
    Reports SyncMessageLog: sync messages exchanged with a peer device, with
    the peer's platform and the transport and reason of the session.
    """

    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'sync.db')
    data_list = []

    query = '''
        SELECT
            m.timestamp,
            m.device_identifier,
            p.platform,
            p.model,
            typeof(p.model),
            m.reachable,
            m.is_reciprocal,
            m.atom_batch_bytes,
            s.transport,
            s.reason,
            hex(m.session_id),
            m.message_id
        FROM SyncMessageLog m
        LEFT JOIN DevicePeer p
            ON p.device_identifier = m.device_identifier
        LEFT JOIN SyncSessionLog s
            ON s.session_id = m.session_id
        ORDER BY m.timestamp
    '''

    data_headers = (('Timestamp', 'datetime'), 'Peer Device ID',
                    'Peer Device Type', 'Peer OS Build', 'Reachable (as stored)',
                    'Reciprocal (as stored)', 'Atom Batch Bytes',
                    'Session Transport (as stored)', 'Session Reason (as stored)',
                    'Session ID', 'Message ID')

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        data_list.append((
            _cocoa_or_blank(record[0]), record[1],
            PLATFORM_NAMES.get(record[2], ''), _peer_build(record[3], record[4]),
            record[5], record[6], record[7], record[8], record[9], record[10],
            record[11]))

    return data_headers, data_list, source_path
