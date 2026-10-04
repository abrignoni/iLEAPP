__artifacts_v2__ = {
    "intelligencePlatformBehaviors": {
        "name": "Intelligence Platform Knowledge Graph - Behaviors",
        "description": "A timestamped log of behavior events held in behaviors.db "
                       "under IntelligencePlatform, each with a category, an "
                       "identifier and a timestamp as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-23",
        "last_update_date": "2026-09-23",
        "requirements": "none",
        "category": "Knowledge Graph",
        "notes": "Reads behaviors.db under IntelligencePlatform. "
                 "The behaviorEventsExtended table is a running log of device behaviors, "
                 "each with a behaviorType code, a behaviorIdentifier and a timestamp. The "
                 "parser maps a behaviorType code to the histogramKey_<name> table at that "
                 "1-based position in sqlite_master order and reports that table's name "
                 "suffix as the category. The comparison behind this mapping was made on "
                 "the one tested image that held rows (iphone11_ios17, iOS 17.3); the "
                 "number of codes compared is not recorded here. On the tested image the "
                 "histogramKey tables were read in the order listed here; the Category "
                 "column shows each table's name suffix as stored, and the names in this "
                 "list paraphrase those suffixes: app launch, app intent, "
                 "point-of-interest "
                 "category, semantic location, focus mode, CarPlay, device locked, "
                 "micro-location visit, airplane mode, Wi-Fi event, Bluetooth event, "
                 "charging event, link action, HomeKit accessory event, location-of-"
                 "interest visit, person interaction, photos person interaction and entity "
                 "interaction. The identifier is "
                 "reported as stored: for an app launch it is a bundle id, for a Wi-Fi "
                 "event a connect or disconnect with a network name, for a person "
                 "interaction a handle reference. Some behaviorType codes (seen as 19, 20 "
                 "and 21) are past the last histogramKey table, so the store does not name "
                 "them, and on the tested image they are the bulk of the rows; their "
                 "identifiers there read Enter or Exit followed by a 64-bit number whose "
                 "meaning "
                 "is not established, and the code "
                 "is reported as stored. On the tested images the store held rows on one "
                 "iOS 17.3 image and was not present on the iOS 18.3 and later images. The "
                 "behaviors are "
                 "recorded by the system, so a row is not evidence a person performed the "
                 "action. behaviors.db is named, without a description of its contents, in "
                 "0x11 Forensics and Consulting, 'That is one smart Apple', "
                 "https://0x11forensicssc.com/f/that-is-one-smart-apple, 2026-07-21. The "
                 "reading of the tables given here is this parser's own.",
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
    """Return {behaviorType: category label}. The behaviorType code is the 1-based
    position of the category in the ordered histogramKey_<name> tables shipped in the
    database. This was verified against every code that carried data on a tested image,
    where the position matched the code exactly, so it also names the categories whose
    table is empty on a given device. Codes past the last table are left unmapped."""
    tables = [row[0] for row in cur.execute(
        "select name from sqlite_master where type='table' "
        "and name like 'histogramKey\\_%' escape '\\' order by rowid")]
    return {index + 1: table[len("histogramKey_"):]
            for index, table in enumerate(tables)}


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
