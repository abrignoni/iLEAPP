"""Report three event streams from the CoreDuet knowledge store (knowledgeC.db)."""

__artifacts_v2__ = {
    "knowledgeC_NotificationUsage": {
        "name": "knowledgeC - Notification Usage",
        "description": "Rows of the /notification/usage stream in knowledgeC.db, with the event "
                       "name, notification identifier and bundle ID as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-21",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "Developed independently, working from the store's schema, its data and Apple's frameworks "
                 "(CoreDuet key names read on macOS 27.2.1, 26B131; no iOS copy of the framework was read). "
                 "Tested images means the 25 images in sample_data (iOS 12.4 to 26.5.2). The Biome artifact "
                 "for this stream reads a separate store, and whether the two hold the same events was not "
                 "compared field by field. Times are Core Data TIMESTAMP columns converted from Cocoa seconds "
                 "to UTC and cut to the whole second. Creation Time is ZCREATIONDATE and Local Creation Time "
                 "is ZLOCALCREATIONDATE, both shown in UTC. What sets either is not established. Seconds From "
                 "GMT is ZSECONDSFROMGMT as stored. Whether it is the offset in force at the event is not "
                 "established. End Time equals Start Time on all 23,004 rows of the tested images. Event is "
                 "ZVALUESTRING as stored. All 13 names stored on the tested images are among those returned by "
                 "BMNotificationUsageTypeAsString in Apple's BiomeLibrary (macOS 27.2.1, 26B131). The function "
                 "gives names and no definitions, so what each name means is not established. On the tested "
                 "images Bundle ID is stored only on Receive rows (12,092 rows). Bundle ID (Same Identifier) "
                 "is derived. For a row with no stored bundle ID, it is the bundle ID stored on rows of the "
                 "same store with the same identifier and the same device ID, or no device ID on both. It is "
                 "left blank when those rows hold more than one bundle ID, which did not occur on the tested "
                 "images, where all such rows are Receive rows. It fills 8,496 rows, and 2,416 rows have no "
                 "such Receive row and leave both columns blank. Source Device ID is ZSOURCE.ZDEVICEID. It is "
                 "filled on 807 rows in 3 tested images, and every such ID matches a ZSYNCPEER row. Whether a "
                 "row with one describes an event on this device is not established. Peer Model is "
                 "ZSYNCPEER.ZMODEL for that ID. When a -wal is beside the store it is applied, so rows the "
                 "-wal has superseded are not reported. One tested image had no -wal and was read from the "
                 "database file alone.",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard",
        "artifact_icon": "bell",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 4062 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 401 rows",
            "belkactf6_tar": "iOS 16.3 | 4 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 106 rows",
            "ctf2020_ios12": "iOS 12.4 | 1167 rows",
            "dexter_ios18": "iOS 18.3.2 | 1061 rows",
            "falken_ios26": "iOS 26.2.1 | 118 rows",
            "felix23_ios16": "iOS 16.5 | 229 rows",
            "felix_ios17": "iOS 17.6.1 | 680 rows",
            "fsfull002_ios17": "iOS 17.1 | 46 rows",
            "hc_ios17_2": "iOS 17.2.1 | 476 rows",
            "hc_ios18_7": "iOS 18.7.8 | 119 rows",
            "hc_ios26": "iOS 26.5.2 | 110 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 520 rows",
            "hickman_ios13": "iOS 13.3.1 | 1075 rows",
            "hickman_ios14": "iOS 14.3 | 821 rows",
            "hickman_ios15": "iOS 15.3.1 | 1738 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 203 rows",
            "iphone11_ios17": "iOS 17.3 | 3906 rows",
            "iphone14plus_ios18": "iOS 18.0 | 63 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 171 rows",
            "jess_ios15": "iOS 15.0.2 | 294 rows",
            "magnet_ios16": "iOS 16.1.1 | 516 rows",
            "otto_ios17": "iOS 17.5.1 | 4300 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 818 rows",
        },
    },
    "knowledgeC_AppActivity": {
        "name": "knowledgeC - App Activity",
        "description": "Rows of the /app/activity stream in knowledgeC.db, with the activity metadata stored on each "
                       "row.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-21",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "Developed independently, working from the store's schema, its data and Apple's frameworks "
                 "(CoreDuet key names read on macOS 27.2.1, 26B131; no iOS copy of the framework was read). "
                 "Tested images means the 25 images in sample_data (iOS 12.4 to 26.5.2). The Biome artifact "
                 "for this stream reads a separate store, and whether the two hold the same events was not "
                 "compared field by field. Times are Core Data TIMESTAMP columns converted from Cocoa seconds "
                 "to UTC and cut to the whole second. Creation Time is ZCREATIONDATE and Local Creation Time "
                 "is ZLOCALCREATIONDATE, both shown in UTC. What sets either is not established. Seconds From "
                 "GMT is ZSECONDSFROMGMT as stored. Whether it is the offset in force at the event is not "
                 "established. End Time equals Start Time on all 4,124 rows of the tested images. Expiration "
                 "Time is the expirationDate metadata key. On 3,760 of its 3,764 filled rows it falls 29 to 31 "
                 "days after Start Time. What it marks is not established. Bundle ID is ZVALUESTRING as "
                 "stored; on 84 rows, in 4 images, it is a single word with no dot, and whether that value is "
                 "a bundle ID is not established. Calendar Date Value and Calendar End Date Value are declared "
                 "INTEGER, not TIMESTAMP. They are reported as stored and their epoch is not established. "
                 "Required String and Beginning Of Activity are as stored and their meaning is not "
                 "established. Beginning Of Activity is absent from 2 tested stores. Title, Source Device ID "
                 "and Peer Model held no value on all 4,124 rows of the tested images and are kept for stores "
                 "that fill them. When a -wal is beside the store it is applied, so rows the -wal has "
                 "superseded are not reported. One tested image had no -wal and was read from the database "
                 "file alone.",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 384 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 193 rows",
            "belkactf6_tar": "iOS 16.3 | 46 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 30 rows",
            "ctf2020_ios12": "iOS 12.4 | 217 rows",
            "dexter_ios18": "iOS 18.3.2 | 624 rows",
            "falken_ios26": "iOS 26.2.1 | 330 rows",
            "felix23_ios16": "iOS 16.5 | 86 rows",
            "felix_ios17": "iOS 17.6.1 | 90 rows",
            "fsfull002_ios17": "iOS 17.1 | 8 rows",
            "hc_ios17_2": "iOS 17.2.1 | 17 rows",
            "hc_ios18_7": "iOS 18.7.8 | 31 rows",
            "hc_ios26": "iOS 26.5.2 | 35 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 115 rows",
            "hickman_ios13": "iOS 13.3.1 | 300 rows",
            "hickman_ios14": "iOS 14.3 | 12 rows",
            "hickman_ios15": "iOS 15.3.1 | 336 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 129 rows",
            "iphone11_ios17": "iOS 17.3 | 201 rows",
            "iphone14plus_ios18": "iOS 18.0 | 59 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 171 rows",
            "jess_ios15": "iOS 15.0.2 | 135 rows",
            "magnet_ios16": "iOS 16.1.1 | 129 rows",
            "otto_ios17": "iOS 17.5.1 | 137 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 309 rows",
        },
    },
    "knowledgeC_AppWebUsage": {
        "name": "knowledgeC - App Web Usage",
        "description": "Rows of the /app/webUsage stream in knowledgeC.db, with the bundle ID, web domain and page "
                       "URL as stored, and the start and end times.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-21",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "Developed independently, working from the store's schema, its data and Apple's frameworks "
                 "(CoreDuet key names read on macOS 27.2.1, 26B131; no iOS copy of the framework was read). "
                 "Tested images means the 25 images in sample_data (iOS 12.4 to 26.5.2). The Biome artifact "
                 "for this stream reads a separate store, and whether the two hold the same events was not "
                 "compared field by field. Times are Core Data TIMESTAMP columns converted from Cocoa seconds "
                 "to UTC and cut to the whole second. Creation Time is ZCREATIONDATE and Local Creation Time "
                 "is ZLOCALCREATIONDATE, both shown in UTC. What sets either is not established. Seconds From "
                 "GMT is ZSECONDSFROMGMT as stored. Whether it is the offset in force at the event is not "
                 "established. Bundle ID is ZVALUESTRING as stored. Duration is End Time minus Start Time. "
                 "Usage Type and Is Usage Trusted are integers as stored and their meaning is not established. "
                 "Usage Type held 1 on 843 and 0 on 5 of the 848 rows of the tested images. Is Usage Trusted "
                 "held 1 on all 611 rows of the stores that have the column. The iOS 12.4 and 13.3.1 stores "
                 "lack the column and their 237 rows are blank. Safari Profile ID is absent from 10 of the 25 "
                 "tested stores and held no value on the 349 rows of the others. It is kept for stores that "
                 "fill it. Source Device ID is ZSOURCE.ZDEVICEID. It is filled on 22 rows in 2 tested images, "
                 "and every such ID matches a ZSYNCPEER row. Whether a row with one describes an event on this "
                 "device is not established. Peer Model is ZSYNCPEER.ZMODEL for that ID. When a -wal is beside "
                 "the store it is applied, so rows the -wal has superseded are not reported. One tested image "
                 "had no -wal and was read from the database file alone.",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard",
        "artifact_icon": "world-www",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 71 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 36 rows",
            "belkactf6_tar": "iOS 16.3 | 8 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 43 rows",
            "ctf2020_ios12": "iOS 12.4 | 220 rows",
            "dexter_ios18": "iOS 18.3.2 | 16 rows",
            "falken_ios26": "iOS 26.2.1 | 71 rows",
            "felix23_ios16": "iOS 16.5 | 9 rows",
            "felix_ios17": "iOS 17.6.1 | 10 rows",
            "fsfull002_ios17": "iOS 17.1 | 7 rows",
            "hc_ios17_2": "iOS 17.2.1 | 3 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 16 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 84 rows",
            "hickman_ios13": "iOS 13.3.1 | 17 rows",
            "hickman_ios14": "iOS 14.3 | 37 rows",
            "hickman_ios15": "iOS 15.3.1 | 23 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 70 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 21 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 11 rows",
            "jess_ios15": "iOS 15.0.2 | 27 rows",
            "magnet_ios16": "iOS 16.1.1 | 3 rows",
            "otto_ios17": "iOS 17.5.1 | 44 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 1 rows",
        },
    },
}

import os

from scripts.ilapfuncs import (
    artifact_processor,
    convert_cocoa_core_data_ts_to_utc,
    convert_unix_ts_to_utc,
    does_table_exist_in_db,
    get_sqlite_db_records,
    null_absent_columns,
    sqlite_databases,
)

COCOA_EPOCH_UNIX = 978307200
ACTIVITY = 'm.Z_DKAPPLICATIONACTIVITYMETADATAKEY__'
CALENDAR = 'm.ZCOM_APPLE_CALENDARUIKIT_USERACTIVITY_'
NOTIFICATION = 'm.Z_DKNOTIFICATIONUSAGEMETADATAKEY__'
WEB = 'm.Z_DKDIGITALHEALTHMETADATAKEY__'

COMMON_SELECT = """
    o.Z_PK AS object_pk, o.ZUUID AS object_uuid,
    o.ZSTARTDATE AS start_time, o.ZENDDATE AS end_time,
    o.ZCREATIONDATE AS creation_time, o.ZLOCALCREATIONDATE AS local_creation_time,
    o.ZSECONDSFROMGMT AS seconds_from_gmt, o.ZVALUESTRING AS value_string,
    s.ZDEVICEID AS source_device_id"""


def _cocoa(value):
    """Convert stored Cocoa seconds to UTC, keeping NULL blank and 0 as a real time."""
    if value is None:
        return ''
    if value == 0:
        return convert_unix_ts_to_utc(COCOA_EPOCH_UNIX)
    return convert_cocoa_core_data_ts_to_utc(value)


def _stores(context):
    """The distinct knowledgeC.db files found, without their sidecars."""
    found = sqlite_databases(context.get_files_found())
    return list(dict.fromkeys(f for f in found if os.path.basename(f) == 'knowledgeC.db'))


def _query(db_path, stream, select):
    """Rows of one stream. Every join is a LEFT JOIN so no stream row can be dropped."""
    if does_table_exist_in_db(db_path, 'ZSYNCPEER'):
        peer = '(SELECT MAX(p.ZMODEL) FROM ZSYNCPEER p WHERE p.ZDEVICEID = s.ZDEVICEID)'
    else:
        peer = 'NULL'
    query = f"""
        SELECT {COMMON_SELECT}, {peer} AS peer_model, {select}
        FROM ZOBJECT o
        LEFT JOIN ZSOURCE s ON s.Z_PK = o.ZSOURCE
        LEFT JOIN ZSTRUCTUREDMETADATA m ON m.Z_PK = o.ZSTRUCTUREDMETADATA
        WHERE o.ZSTREAMNAME = '{stream}'
        ORDER BY o.ZSTARTDATE, o.Z_PK
    """
    return list(get_sqlite_db_records(db_path, null_absent_columns(db_path, query)))


@artifact_processor
def knowledgeC_NotificationUsage(context):
    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), ('Creation Time', 'datetime'),
        ('Local Creation Time', 'datetime'), 'Event', 'Seconds From GMT', 'Bundle ID',
        'Bundle ID (Same Identifier)', 'Notification Identifier', 'Source Device ID',
        'Peer Model', 'Object UUID', 'Object Z_PK',
    )
    select = f"{NOTIFICATION}BUNDLEID AS bundle_id, {NOTIFICATION}IDENTIFIER AS identifier"
    stores = _stores(context)
    data_list = []
    for db_path in stores:
        records = _query(db_path, '/notification/usage', select)
        linked = {}
        for rec in records:
            if rec['bundle_id']:
                linked.setdefault((rec['identifier'], rec['source_device_id']), set()).add(
                    rec['bundle_id'])
        rows = []
        for rec in records:
            same_identifier = ''
            if not rec['bundle_id']:
                matches = linked.get((rec['identifier'], rec['source_device_id']), ())
                if len(matches) == 1:
                    same_identifier = next(iter(matches))
            rows.append((
                _cocoa(rec['start_time']), _cocoa(rec['end_time']), _cocoa(rec['creation_time']),
                _cocoa(rec['local_creation_time']), rec['value_string'], rec['seconds_from_gmt'],
                rec['bundle_id'], same_identifier, rec['identifier'], rec['source_device_id'],
                rec['peer_model'], rec['object_uuid'], rec['object_pk'],
            ))
        data_list.extend(rows)
    return data_headers, data_list, '\n'.join(stores)


@artifact_processor
def knowledgeC_AppActivity(context):
    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), ('Creation Time', 'datetime'),
        ('Local Creation Time', 'datetime'), ('Expiration Time', 'datetime'),
        'Seconds From GMT', 'Bundle ID', 'Activity Type', 'Item Identifier',
        'Item Related Unique Identifier', 'User Activity UUID', 'Source Device ID', 'Peer Model',
        'Object UUID', 'Object Z_PK', 'Title', 'Content Description', 'Item Related Content URL',
        'Suggested Invocation Phrase', 'Required String', 'Beginning Of Activity',
        'Calendar Date Value', 'Calendar End Date Value', 'Calendar External ID',
    )
    select = f"""{ACTIVITY}EXPIRATIONDATE AS expiration, {ACTIVITY}ACTIVITYTYPE AS activity_type,
        {ACTIVITY}ITEMIDENTIFIER AS item_identifier,
        {ACTIVITY}ITEMRELATEDUNIQUEIDENTIFIER AS related_unique,
        {ACTIVITY}USERACTIVITYUUID AS activity_uuid, {ACTIVITY}TITLE AS title,
        {ACTIVITY}CONTENTDESCRIPTION AS content_description,
        {ACTIVITY}ITEMRELATEDCONTENTURL AS related_url,
        {ACTIVITY}SUGGESTEDINVOCATIONPHRASE AS invocation_phrase,
        {ACTIVITY}USERACTIVITYREQUIREDSTRING AS required_string,
        {ACTIVITY}BEGINNINGOFACTIVITY AS beginning,
        {CALENDAR}DATE AS calendar_date, {CALENDAR}ENDDATE AS calendar_end,
        {CALENDAR}EXTERNALID AS calendar_external_id"""
    stores = _stores(context)
    data_list = []
    for db_path in stores:
        rows = [(
            _cocoa(rec['start_time']), _cocoa(rec['end_time']), _cocoa(rec['creation_time']),
            _cocoa(rec['local_creation_time']), _cocoa(rec['expiration']),
            rec['seconds_from_gmt'], rec['value_string'], rec['activity_type'],
            rec['item_identifier'], rec['related_unique'], rec['activity_uuid'],
            rec['source_device_id'], rec['peer_model'], rec['object_uuid'], rec['object_pk'],
            rec['title'], rec['content_description'], rec['related_url'],
            rec['invocation_phrase'], rec['required_string'], rec['beginning'],
            rec['calendar_date'], rec['calendar_end'], rec['calendar_external_id'],
        ) for rec in _query(db_path, '/app/activity', select)]
        data_list.extend(rows)
    return data_headers, data_list, '\n'.join(stores)


@artifact_processor
def knowledgeC_AppWebUsage(context):
    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), ('Creation Time', 'datetime'),
        ('Local Creation Time', 'datetime'), 'Duration (Seconds)', 'Seconds From GMT',
        'Bundle ID', 'Web Domain', 'Web Page URL', 'Safari Profile ID', 'Source Device ID',
        'Peer Model', 'Object UUID', 'Object Z_PK', 'Usage Type', 'Is Usage Trusted',
    )
    select = f"""{WEB}WEBDOMAIN AS web_domain, {WEB}WEBPAGEURL AS web_url,
        {WEB}SAFARIPROFILEID AS safari_profile, {WEB}USAGETYPE AS usage_type,
        {WEB}ISUSAGETRUSTED AS usage_trusted"""
    stores = _stores(context)
    data_list = []
    for db_path in stores:
        rows = []
        for rec in _query(db_path, '/app/webUsage', select):
            start, end = rec['start_time'], rec['end_time']
            duration = end - start if start is not None and end is not None else ''
            rows.append((
                _cocoa(start), _cocoa(end), _cocoa(rec['creation_time']),
                _cocoa(rec['local_creation_time']), duration, rec['seconds_from_gmt'],
                rec['value_string'], rec['web_domain'], rec['web_url'], rec['safari_profile'],
                rec['source_device_id'], rec['peer_model'], rec['object_uuid'], rec['object_pk'],
                rec['usage_type'], rec['usage_trusted'],
            ))
        data_list.extend(rows)
    return data_headers, data_list, '\n'.join(stores)
