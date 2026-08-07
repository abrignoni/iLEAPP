__artifacts_v2__ = {
    "what3words_saved_places": {
        "name": "what3words - Saved Places",
        "description": "Places the user saved in what3words, with the three word address, the label "
                       "given to it, the nearest place and the coordinates",
        "author": "",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "what3words",
        "notes": "Read from the class_DataPlace table of the app's Realm store (Documents/default.realm) "
                 "using the vendored realm_parser. Each three word address maps to a fixed 3m square; "
                 "the latitude and longitude are the square's coordinates as the app stored them.",
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
        "author": "",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "what3words",
        "notes": "Read from the class_DataSearchItem table of the app's Realm store.",
        "paths": ('*/Documents/default.realm*',),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | what3words | 2 rows",
        },
    },
    "what3words_account": {
        "name": "what3words - Account",
        "description": "The signed-in what3words account from the app's Realm store, with the email, "
                       "name, country and the provider the account signed in with",
        "author": "",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "what3words",
        "notes": "Read from the class_DataProfile table of the app's Realm store.",
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


def _realm_path(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('default.realm') and _is_what3words_realm(file_found):
            return file_found
    return ''


@artifact_processor
def what3words_saved_places(context):
    source_path = _realm_path(context.get_files_found())
    data_list = []

    for row in realm_rows(source_path, 'class_DataPlace'):
        data_list.append((
            _realm_ts(row.get('createdAt')),
            row.get('address'),
            row.get('label'),
            row.get('nearestPlace'),
            row.get('lat'),
            row.get('lng'),
            row.get('countryCode'),
            row.get('language'),
            'Yes' if row.get('isShared') else 'No',
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
    return data_headers, data_list, source_path


@artifact_processor
def what3words_search_history(context):
    source_path = _realm_path(context.get_files_found())
    data_list = []

    for row in realm_rows(source_path, 'class_DataSearchItem'):
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
    return data_headers, data_list, source_path


@artifact_processor
def what3words_account(context):
    source_path = _realm_path(context.get_files_found())
    data_list = []

    for row in realm_rows(source_path, 'class_DataProfile'):
        data_list.append((
            _realm_ts(row.get('created')),
            _realm_ts(row.get('updated')),
            row.get('email'),
            row.get('firstName'),
            row.get('lastName'),
            row.get('country'),
            row.get('oauthProvider'),
            'Yes' if row.get('verified') else 'No',
            'Yes' if row.get('suspended') else 'No',
            'Yes' if row.get('searchHistoryOptout') else 'No',
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
    return data_headers, data_list, source_path
