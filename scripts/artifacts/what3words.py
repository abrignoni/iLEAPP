__artifacts_v2__ = {
    "what3words_saved_places": {
        "name": "what3words - Saved Places",
        "description": "Rows of the what3words class_DataPlace table, with the three word "
                       "address, label, nearest place and coordinates as stored",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "what3words",
        "notes": "Read from the class_DataPlace table of the app's Realm store "
                 "(Documents/default.realm) using the vendored realm_parser. Every matched "
                 "default.realm that carries a what3words class is read. Saved Time is the "
                 "createdAt attribute. Shared shows Yes or No for a stored isShared value and is "
                 "blank when the attribute is not present. The latitude "
                 "and longitude are reported as the app stored them.",
        "paths": ('*/Documents/default.realm*',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | what3words | 1 row",
        },
    },
    "what3words_search_history": {
        "name": "what3words - Search History",
        "description": "Three word address entries in the what3words search history table, with the "
                       "nearest place, coordinates and the time recorded for each entry",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "what3words",
        "notes": "Read from the class_DataSearchItem table of the app's Realm store. Every "
                 "matched default.realm that carries a what3words class is read. Search Time is the "
                 "created attribute. Three Word Address is threeWordAddress, or the result "
                 "attribute when that is empty.",
        "paths": ('*/Documents/default.realm*',),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | what3words | 2 rows",
        },
    },
    "what3words_account": {
        "name": "what3words - Account",
        "description": "The what3words account profile from the app's Realm store "
                       "class_DataProfile table, with the email, name, country and the stored "
                       "sign-in provider",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "what3words",
        "notes": "Read from the class_DataProfile table of the app's Realm store. Every matched "
                 "default.realm that carries a what3words class is read. Verified, Suspended and "
                 "Search History Opt-out show Yes or No for a stored value and are blank when the "
                 "attribute is not present.",
        "paths": ('*/Documents/default.realm*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | what3words | 1 row",
        },
    },
}

from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor
from scripts.realm_parser import parse_realm_file, realm_rows


def _realm_ts(value):
    """The vendored realm_parser renders Realm timestamps as 'YYYY-MM-DD HH:MM:SS UTC';
    turn that into a timezone-aware datetime so it sorts and timelines correctly."""
    if not value or not isinstance(value, str):
        return value
    try:
        return datetime.strptime(value.replace(' UTC', ''), '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    except ValueError:
        return value


def _is_what3words_realm(path):
    """Guard: the default.realm glob is shared by several apps, so confirm this
    Realm actually carries what3words classes before reporting rows."""
    tables = parse_realm_file(path).get("active", {})
    return 'class_DataPlace' in tables or 'class_DataProfile' in tables or 'class_DataSearchItem' in tables


def _realm_paths(files_found):
    paths = []
    for file_found in files_found:
        file_found = str(file_found)
        if file_found in paths:
            continue
        if file_found.endswith('default.realm') and _is_what3words_realm(file_found):
            paths.append(file_found)
    return paths


def _all_rows(source_paths, table):
    for source_path in source_paths:
        yield from realm_rows(source_path, table)


def _yes_no(value):
    if value is None or value == '':
        return ''
    return 'Yes' if value else 'No'


@artifact_processor
def what3words_saved_places(context):
    source_paths = _realm_paths(context.get_files_found())
    data_list = []

    for row in _all_rows(source_paths, 'class_DataPlace'):
        data_list.append((
            _realm_ts(row.get('createdAt')),
            row.get('address'),
            row.get('label'),
            row.get('nearestPlace'),
            row.get('lat'),
            row.get('lng'),
            row.get('countryCode'),
            row.get('language'),
            _yes_no(row.get('isShared')),
        ))

    data_headers = (
        ('Saved Time', 'datetime'),
        'Three Word Address',
        'Label',
        'Nearest Place',
        'Latitude',
        'Longitude',
        'Country Code',
        'Language',
        'Shared',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def what3words_search_history(context):
    source_paths = _realm_paths(context.get_files_found())
    data_list = []

    for row in _all_rows(source_paths, 'class_DataSearchItem'):
        data_list.append((
            _realm_ts(row.get('created')),
            row.get('threeWordAddress') or row.get('result'),
            row.get('nearestPlace'),
            row.get('lat'),
            row.get('lng'),
            row.get('countryCode'),
            row.get('languageCode'),
        ))

    data_headers = (
        ('Search Time', 'datetime'),
        'Three Word Address',
        'Nearest Place',
        'Latitude',
        'Longitude',
        'Country Code',
        'Language',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def what3words_account(context):
    source_paths = _realm_paths(context.get_files_found())
    data_list = []

    for row in _all_rows(source_paths, 'class_DataProfile'):
        data_list.append((
            _realm_ts(row.get('created')),
            _realm_ts(row.get('updated')),
            row.get('email'),
            row.get('firstName'),
            row.get('lastName'),
            row.get('country'),
            row.get('oauthProvider'),
            _yes_no(row.get('verified')),
            _yes_no(row.get('suspended')),
            _yes_no(row.get('searchHistoryOptout')),
            row.get('userId'),
        ))

    data_headers = (
        ('Account Created', 'datetime'),
        ('Account Updated', 'datetime'),
        'Email',
        'First Name',
        'Last Name',
        'Country',
        'Sign-in Provider',
        'Verified',
        'Suspended',
        'Search History Opt-out',
        'User ID',
    )
    return data_headers, data_list, '\n'.join(source_paths)
