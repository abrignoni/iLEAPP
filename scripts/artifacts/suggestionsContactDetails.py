__artifacts_v2__ = {
    "suggestionsContactDetails": {
        "name": "Suggestions Store - Contact Details",
        "description": "Rows of the contactDetails table in mobile/Library/Suggestions/entities.db: each "
                       "phone number, email address or other detail with its type, the title, type and "
                       "times of the entity it belongs to, and the apps that entity's references name.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-30",
        "last_update_date": "2026-10-30",
        "requirements": "none",
        "category": "Suggestions",
        "notes": "Reads the contactDetails table of mobile/Library/Suggestions/entities.db, with its "
                 "-wal, one row per table row, joined to the entity table by entityId and to "
                 "entityReferences for the bundle IDs that entity's references name; the contactDetails "
                 "table was absent from ctf2020_ios12 and hickman_ios13. Detail Type is "
                 "contactDetails.type and Entity Type is entity.entityType, each shown as a name with the "
                 "stored number. The names are the values returned by the SGContactDetailTypeDescription "
                 "and SGEntityTypeDescription functions of Apple's CoreSuggestionsInternals framework, "
                 "called on macOS 27.0.1 (26A434), with the SGContactDetail or SGEntityType prefix "
                 "removed and the words spaced; the iOS builds of the framework were not called, and a "
                 "number outside those lists is shown alone. On the tested rows every Phone value had the "
                 "shape of a phone number (54 rows) and every Email Address value the shape of an email "
                 "address (231); the other 36 were Social Profile. On every tested row the entity was a "
                 "Pseudo Contact (295 rows) or a Detected Phone (26). Entity Created, Entity Updated and "
                 "Entity Last Seen are entity.creationTimestamp, updateTimestamp and lastSeenTimestamp "
                 "read as Unix seconds: read from 2001-01-01 the tested values would fall in 2051 to "
                 "2057, and read as Unix seconds they fall in the same years as the same store's "
                 "emailMetadata times, within a month of that span on every tested store. Entity Updated "
                 "is blank where updateTimestamp is 0. What sets each time is not established. Entity "
                 "Title is entity.title as stored; it was blank on 5 of the 321 tested rows. Label held "
                 "no value on any of the 321 tested rows. Referenced Apps (bundle ID) lists the "
                 "bundleIdentifier of the entity's entityReferences rows; it named com.apple.mobilemail "
                 "on 182 rows and com.apple.MobileSMS on 6, and was blank on 133, where the entity had no "
                 "reference. A reference row names an app the store recorded for the entity. Its "
                 "uniqueIdentifier and domainIdentifier are not read here, and what the reference points "
                 "at is not established. Source Key (as stored) is contactDetails.sourceKey, and "
                 "Extraction Type (as stored) is the extractionType of its extractionInfos row (0, 16 or "
                 "2 on the tested rows); neither is resolved. The confidence of that extractionInfos row, "
                 "the entity's content and structured data, and the identity and email tables are not "
                 "read here.",
        "paths": ('*/mobile/Library/Suggestions/entities.db*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 16 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 42 rows",
            "belkactf6_tar": "iOS 16.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 3 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 58 rows",
            "falken_ios26": "iOS 26.2.1 | 10 rows",
            "felix23_ios16": "iOS 16.5 | 11 rows",
            "felix_ios17": "iOS 17.6.1 | 3 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 6 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 41 rows",
            "hickman_ios15": "iOS 15.3.1 | 16 rows",
            "iphone11_ios17": "iOS 17.3 | 22 rows",
            "iphone12_ios18": "iOS 18.7 | 11 rows",
            "iphone14plus_ios18": "iOS 18.0 | 3 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 5 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 74 rows",
        },
    }
}

import os

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, does_table_exist_in_db, \
    get_sqlite_db_records

# Names derived from the return values of CoreSuggestionsInternals' SGContactDetailTypeDescription
# and SGEntityTypeDescription, called on macOS 27.0.1 (26A434): prefix removed, words spaced.
_DETAIL_TYPES = {0: 'Phone', 1: 'Address', 2: 'Email Address', 3: 'Instant Message Address',
                 4: 'Social Profile', 5: 'Photo', 6: 'Birthday'}
_ENTITY_TYPES = {
    0: 'Unknown', 1: 'Curated Event', 2: 'Pseudo Event', 3: 'Curated Contact', 4: 'Pseudo Contact', 5: 'Email',
    6: 'Detected Phone', 7: 'Detected Address', 8: 'Detected Email Address', 9: 'Curated Phone',
    10: 'Curated Address', 11: 'Curated Email Address', 12: 'Unrecognized Contact', 13: 'Text Message',
    14: 'Curated Instant Message Address', 15: 'Detected Instant Message Address', 16: 'Interaction',
    17: 'Schema.org', 18: 'Web Page', 19: 'Detected Social Profile', 20: 'Detected Birthday',
    21: 'Curated Birthday', 22: 'Pseudo Reminder', 23: 'Curated Photo Path', 24: 'Delivery',
    25: 'Wallet Order', 26: 'Wallet Pass'}


def _named(code, names):
    """'Name (code)' for a known code, the code alone otherwise, blank for none."""
    if code is None:
        return ''
    return f'{names[code]} ({code})' if code in names else str(code)


def _time(value):
    """Unix seconds as a UTC datetime; blank for no value or 0."""
    if not value or isinstance(value, bool) or not isinstance(value, (int, float)):
        return ''
    return convert_unix_ts_to_utc(value)


def _text(value):
    return '' if value is None else value


@artifact_processor
def suggestionsContactDetails(context):
    data_headers = (
        ('Entity Created', 'datetime'), ('Entity Updated', 'datetime'), ('Entity Last Seen', 'datetime'),
        'Detail Type', 'Value', 'Label', 'Entity Title', 'Entity Type', 'Referenced Apps (bundle ID)',
        'Source Key (as stored)', 'Extraction Type (as stored)')
    data_list, read = [], []
    paths = sorted({str(p) for p in context.get_files_found() if os.path.basename(str(p)) == 'entities.db'})
    for path in paths:
        if not (does_table_exist_in_db(path, 'contactDetails') and does_table_exist_in_db(path, 'entity')):
            continue
        read.append(path)
        apps = {}
        if does_table_exist_in_db(path, 'entityReferences'):
            for row in get_sqlite_db_records(path, 'SELECT entityId, bundleIdentifier FROM entityReferences '
                                                   'ORDER BY id'):
                names = apps.setdefault(row['entityId'], [])
                if row['bundleIdentifier'] and row['bundleIdentifier'] not in names:
                    names.append(row['bundleIdentifier'])
        extraction = ''
        joins = ''
        if does_table_exist_in_db(path, 'extractionInfos'):
            extraction, joins = ', x.extractionType', ' LEFT JOIN extractionInfos x ON x.id = d.extractionInfoId'
        rows = get_sqlite_db_records(
            path, 'SELECT e.creationTimestamp, e.updateTimestamp, e.lastSeenTimestamp, d.type, d.value, d.label, '
                  f'e.title, e.entityType, d.entityId, d.sourceKey{extraction or ", NULL AS extractionType"} '
                  f'FROM contactDetails d LEFT JOIN entity e ON e.id = d.entityId{joins} '
                  'ORDER BY e.creationTimestamp, d.id')
        for row in rows:
            data_list.append((
                _time(row['creationTimestamp']), _time(row['updateTimestamp']), _time(row['lastSeenTimestamp']),
                _named(row['type'], _DETAIL_TYPES), _text(row['value']), _text(row['label']), _text(row['title']),
                _named(row['entityType'], _ENTITY_TYPES), ', '.join(apps.get(row['entityId'], [])),
                _text(row['sourceKey']), _text(row['extractionType'])))
    return data_headers, data_list, '\n'.join(read)
