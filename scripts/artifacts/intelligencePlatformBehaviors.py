__artifacts_v2__ = {
    "intelligencePlatformBehaviors": {
        "name": "Intelligence Platform Knowledge Graph - Behaviors",
        "description": "A timestamped log of device behaviors the on-device knowledge "
                       "graph recorded: app launches, connections, location visits, "
                       "person interactions and device state changes.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-23",
        "last_update_date": "2026-09-23",
        "requirements": "none",
        "category": "Knowledge Graph",
        "notes": "Reads behaviors.db under IntelligencePlatform (the 'knowledged' graph). "
                 "The behaviorEventsExtended table is a running log of device behaviors, "
                 "each with a behaviorType code, a behaviorIdentifier and a timestamp. The "
                 "behaviorType code is resolved to a category from the histogramKey_<name> "
                 "tables shipped in the same database, by matching each category table's "
                 "identifiers back to the events, so the resolution is exact for the device "
                 "that produced the store. Categories seen include app launch, app intent, "
                 "point-of-interest category, focus mode, CarPlay, device locked, "
                 "micro-location visit, airplane mode, Wi-Fi event, charging event, "
                 "location-of-interest visit and person interaction. The identifier is "
                 "reported as stored: for an app launch it is a bundle id, for a Wi-Fi "
                 "event a connect or disconnect with a network name, for a person "
                 "interaction a handle reference. Some behaviorType codes (seen as 19, 20 "
                 "and 21) are not named by any histogramKey table and are the bulk of the "
                 "rows; they are location-cluster entry events whose identifier is an "
                 "opaque cluster id, and their code is reported as stored. This store was "
                 "seen on iOS 17 and is not present on the tested iOS 18.3 and later "
                 "images, so it is a source specific to that window. The behaviors are "
                 "recorded by the system, so a row is not evidence a person performed the "
                 "action. The store was described by 0x11 Forensics and Consulting, 'That "
                 "is one smart Apple', 0x11forensicssc.com, 2026-07-21.",
        "paths": (
            '*/mobile/Library/IntelligencePlatform/behaviors.db*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | 25186 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
        },
    },
}

from scripts.ilapfuncs import artifact_processor, get_file_path, \
    open_sqlite_db_readonly, convert_cocoa_core_data_ts_to_utc, does_table_exist_in_db


def _category_map(cur):
    """Derive {behaviorType: category label} by matching each histogramKey_<name>
    table's identifiers back to behaviorEventsExtended, so a code resolves to the
    category whose identifiers carry it. Codes no table names are left unmapped."""
    mapping = {}
    tables = [row[0] for row in cur.execute(
        "select name from sqlite_master where type='table' "
        "and name like 'histogramKey\\_%' escape '\\'")]
    for table in tables:
        label = table[len("histogramKey_"):]
        for (behavior_type,) in cur.execute(
                f'select distinct b.behaviorType from behaviorEventsExtended b '
                f'join "{table}" k on b.behaviorIdentifier = k.behaviorIdentifier'):
            mapping[behavior_type] = label
    return mapping


@artifact_processor
def intelligencePlatformBehaviors(context):
    files_found = context.get_files_found()
    db_path = get_file_path(files_found, "behaviors.db")
    data_list = []
    source_path = context.get_relative_path(db_path) if db_path else ''
    if db_path and does_table_exist_in_db(db_path, "behaviorEventsExtended"):
        db = open_sqlite_db_readonly(db_path)
        if db is not None:
            cur = db.cursor()
            mapping = _category_map(cur)
            for behavior_type, identifier, timestamp, gap in cur.execute(
                    "select behaviorType, behaviorIdentifier, timestamp, "
                    "timeSincePreviousEvent from behaviorEventsExtended order by timestamp"):
                category = mapping.get(behavior_type, f'behaviorType {behavior_type}')
                data_list.append((
                    convert_cocoa_core_data_ts_to_utc(timestamp) if timestamp else '',
                    category,
                    identifier,
                    round(gap, 3) if gap is not None else ''))
            db.close()

    data_headers = (
        ('Timestamp', 'datetime'),
        'Category',
        'Identifier (as stored)',
        'Seconds Since Previous Event')
    return data_headers, data_list, source_path
