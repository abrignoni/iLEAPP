__artifacts_v2__ = {
    "knowledgeC_NotificationUsage": {
        "name": "knowledgeC - Notification Usage",
        "description": "Notification events from the /notification/usage stream of knowledgeC.db: the usage "
                       "type, the app bundle ID and the notification identifier.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-21",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "Developed independently, working from the store's schema, its data and the metadata key "
                 "names in Apple's CoreDuet framework. Those key names were read from CoreDuet on macOS 27.2.1 "
                 "(26B131); no iOS copy of the framework was read. The Biome artifact for this stream reads a "
                 "separate store. Whether the two stores hold the same events was not compared field by field. "
                 "Tested images means the 25 images in sample_data (iOS 12.4 to 26.5.2). Device ID is "
                 "ZSOURCE.ZDEVICEID as stored, filled on 807 rows across 3 tested images; whether a filled "
                 "value means the row came from another device is not established. Timestamp is ZSTARTDATE; "
                 "ZENDDATE held the same value on every tested row, so it is not a column. Record Created is "
                 "ZCREATIONDATE, and what the gap between it and Timestamp means is not established. Usage "
                 "Type is the stored text; every value seen is a usage type name of the BMNotificationUsage "
                 "class in BiomeLibrary on macOS 27.2.1 (26B131). On the tested images only Receive rows "
                 "stored a bundle ID: 12,092 of 23,004 rows (Bundle ID Origin Recorded). On 8,496 other rows "
                 "Bundle ID comes from a Receive row in the same store with the same Notification ID (Bundle "
                 "ID Origin Same Notification ID); no tested identifier named two apps, but an identifier can "
                 "recur over time. The remaining 2,416 rows have no such Receive row and leave Bundle ID and "
                 "Bundle ID Origin blank.",
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
        "description": "App activity records from the /app/activity stream of knowledgeC.db: the app, the "
                       "activity type, its description and any related content URL.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-21",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "Developed independently, working from the store's schema, its data and the metadata key "
                 "names in Apple's CoreDuet framework. Those key names were read from CoreDuet on macOS 27.2.1 "
                 "(26B131); no iOS copy of the framework was read. The Biome artifact for this stream reads a "
                 "separate store. Whether the two stores hold the same events was not compared field by field. "
                 "Tested images means the 25 images in sample_data (iOS 12.4 to 26.5.2). Device ID is "
                 "ZSOURCE.ZDEVICEID and held no value on the tested images. Timestamp is ZSTARTDATE; ZENDDATE "
                 "held the same value on every tested row, so it is not a column. Record Created is "
                 "ZCREATIONDATE. Bundle ID is ZVALUESTRING as stored. On 84 of the 4,124 tested rows, in 4 "
                 "images, the value is a single word with no dot, and whether that value is a bundle ID is not "
                 "established. Expiration is a Cocoa date. Each other column is the metadata key its header "
                 "names, reported as stored. Related Content URL is itemRelatedContentURL and Related Unique "
                 "Identifier is itemRelatedUniqueIdentifier. What the 0 and 1 flags mean on a given row is not "
                 "established. A key the store lacks leaves its column blank. Not reported: "
                 "userActivityRequiredString, a text value that is not decoded here; shortcutAvailability, "
                 "which held only 0 or no value on the tested images; and the Calendar date and external ID "
                 "columns (19 rows on the tested images), whose date epoch is not established. The title key "
                 "held no value on any tested row.",
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
        "description": "Web usage periods from the /app/webUsage stream of knowledgeC.db: the app, the web "
                       "domain and the page URL.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-21",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "Developed independently, working from the store's schema, its data and the metadata key "
                 "names in Apple's CoreDuet framework. Those key names were read from CoreDuet on macOS 27.2.1 "
                 "(26B131); no iOS copy of the framework was read. The Biome artifact for this stream reads a "
                 "separate store. Whether the two stores hold the same events was not compared field by field. "
                 "Tested images means the 25 images in sample_data (iOS 12.4 to 26.5.2). Device ID is "
                 "ZSOURCE.ZDEVICEID as stored, filled on 22 rows across 2 tested images; whether a filled "
                 "value means the row came from another device is not established. Start Time is ZSTARTDATE, "
                 "End Time ZENDDATE and Record Created ZCREATIONDATE. Bundle ID is ZVALUESTRING. Usage Type is "
                 "stored as an integer and its meaning is not established: it held 1 on 843 and 0 on 5 of the "
                 "848 rows on the tested images. Is Usage Trusted held 1 on all 611 rows of the stores that "
                 "have the column. The iOS 12.4 and 13.3.1 stores lack the column and their 237 rows leave it "
                 "blank. The safariProfileID key held no value on any tested row and is not reported.",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard",
        "artifact_icon": "world",
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

from scripts.ilapfuncs import artifact_processor, convert_cocoa_core_data_ts_to_utc, logfunc, \
    open_sqlite_db_readonly

NOTIFICATION_KEY = 'Z_DKNOTIFICATIONUSAGEMETADATAKEY__'
ACTIVITY_KEY = 'Z_DKAPPLICATIONACTIVITYMETADATAKEY__'
WEB_KEY = 'Z_DKDIGITALHEALTHMETADATAKEY__'


def _stores(context):
    """Every staged knowledgeC.db, leaving out its -wal and -shm."""
    return [str(path) for path in context.get_files_found() if str(path).endswith('knowledgeC.db')]


def _stream_rows(store, stream, metadata_columns):
    """Rows of one stream as (start, end, created, value, *metadata, device). A missing column reads None."""
    with open_sqlite_db_readonly(store) as db:
        cursor = db.cursor()
        tables = {row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        if not {'ZOBJECT', 'ZSTRUCTUREDMETADATA'} <= tables:
            logfunc(f'knowledgeC tables not found in {store}')
            return []
        present = {row[1] for row in cursor.execute('PRAGMA table_info(ZSTRUCTUREDMETADATA)')}
        selected = ', '.join(f'm."{column}"' if column in present else 'NULL' for column in metadata_columns)
        source_columns = {row[1] for row in cursor.execute('PRAGMA table_info(ZSOURCE)')}
        device = 's.ZDEVICEID' if 'ZDEVICEID' in source_columns else 'NULL'
        source_join = 'LEFT JOIN ZSOURCE s ON o.ZSOURCE = s.Z_PK ' if device != 'NULL' else ''
        cursor.execute(
            f'SELECT o.ZSTARTDATE, o.ZENDDATE, o.ZCREATIONDATE, o.ZVALUESTRING, {selected}, {device} '
            'FROM ZOBJECT o LEFT JOIN ZSTRUCTUREDMETADATA m ON o.ZSTRUCTUREDMETADATA = m.Z_PK '
            f'{source_join}'
            'WHERE o.ZSTREAMNAME = ? ORDER BY o.ZSTARTDATE, o.Z_PK', (stream,))
        return cursor.fetchall()


def _time(value):
    return convert_cocoa_core_data_ts_to_utc(value) if value else ''


def _notification_rows(rows):
    """Add the app to rows without one, from the Receive row holding the same notification identifier."""
    apps = {}
    for row in rows:
        bundle_id, identifier = row[4], row[5]
        if bundle_id and identifier:
            apps.setdefault(identifier, set()).add(bundle_id)
    data = []
    for start, _end, created, usage_type, bundle_id, identifier, device in rows:
        origin = 'Recorded' if bundle_id else ''
        if not bundle_id and len(apps.get(identifier, ())) == 1:
            bundle_id = next(iter(apps[identifier]))
            origin = 'Same Notification ID'
        data.append((_time(start), _time(created), usage_type, bundle_id or '', origin, identifier or '',
                     device or ''))
    return data


@artifact_processor
def knowledgeC_NotificationUsage(context):
    """Parse /notification/usage from knowledgeC.db."""
    stores = _stores(context)
    columns = (NOTIFICATION_KEY + 'BUNDLEID', NOTIFICATION_KEY + 'IDENTIFIER')
    data_list = []
    for store in stores:
        data_list.extend(_notification_rows(_stream_rows(store, '/notification/usage', columns)))
    data_headers = (('Timestamp', 'datetime'), ('Record Created', 'datetime'), 'Usage Type', 'Bundle ID',
                    'Bundle ID Origin', 'Notification ID', 'Device ID')
    return data_headers, data_list, '\n'.join(stores)


@artifact_processor
def knowledgeC_AppActivity(context):
    """Parse /app/activity from knowledgeC.db."""
    stores = _stores(context)
    columns = tuple(ACTIVITY_KEY + name for name in (
        'EXPIRATIONDATE', 'ACTIVITYTYPE', 'CONTENTDESCRIPTION', 'ITEMRELATEDCONTENTURL', 'SUGGESTEDINVOCATIONPHRASE',
        'ITEMIDENTIFIER', 'ITEMRELATEDUNIQUEIDENTIFIER', 'USERACTIVITYUUID', 'ISELIGIBLEFORPREDICTION',
        'ISPUBLICLYINDEXABLE', 'BEGINNINGOFACTIVITY'))
    data_list = []
    for store in stores:
        for start, _end, created, bundle_id, expiration, *rest in _stream_rows(store, '/app/activity', columns):
            data_list.append((_time(start), _time(created), _time(expiration), bundle_id,
                              *('' if value is None else value for value in rest)))
    data_headers = (('Timestamp', 'datetime'), ('Record Created', 'datetime'), ('Expiration', 'datetime'),
                    'Bundle ID', 'Activity Type', 'Content Description', 'Related Content URL',
                    'Suggested Invocation Phrase', 'Item Identifier', 'Related Unique Identifier',
                    'User Activity UUID', 'Is Eligible For Prediction', 'Is Publicly Indexable',
                    'Beginning Of Activity', 'Device ID')
    return data_headers, data_list, '\n'.join(stores)


@artifact_processor
def knowledgeC_AppWebUsage(context):
    """Parse /app/webUsage from knowledgeC.db."""
    stores = _stores(context)
    columns = tuple(WEB_KEY + name for name in ('WEBDOMAIN', 'WEBPAGEURL', 'USAGETYPE', 'ISUSAGETRUSTED'))
    data_list = []
    for store in stores:
        for start, end, created, bundle_id, *rest in _stream_rows(store, '/app/webUsage', columns):
            data_list.append((_time(start), _time(end), _time(created), bundle_id,
                              *('' if value is None else value for value in rest)))
    data_headers = (('Start Time', 'datetime'), ('End Time', 'datetime'), ('Record Created', 'datetime'),
                    'Bundle ID', 'Web Domain', 'Web Page URL', 'Usage Type', 'Is Usage Trusted', 'Device ID')
    return data_headers, data_list, '\n'.join(stores)
