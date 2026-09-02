__artifacts_v2__ = {
    "iftttAccount": {
        "name": "IFTTT - Account",
        "description": "The IFTTT account signed in on the device, with the login name, email "
                       "address and time zone the app held for it.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-02",
        "last_update_date": "2026-09-02",
        "requirements": "none",
        "category": "IFTTT",
        "notes": "Read from class_UserRecord in the app's Realm store (Documents/default.realm) "
                 "with the vendored realm_parser. The store is Realm file format 9, which the "
                 "parser reads through its pre-Cluster path. An iOS data container is named by "
                 "a GUID, so the path pattern cannot carry the bundle identifier and matches "
                 "any Documents/default.realm; every candidate is then required to carry an "
                 "IFTTT class before it is read, and a store without one is skipped and "
                 "logged, so another app's Realm cannot be reported under IFTTT's name. Time "
                 "Zone is the zone the account holds in the IFTTT service, not a device "
                 "setting. These are values the account held in the app, which the app "
                 "received from its service; they are not verified identifiers. User Type and "
                 "Home Screen Preference are reported as stored.",
        "paths": ('*/Documents/default.realm',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | com.ifttt.ifttt | 1 row",
        },
    },
    "iftttApplets": {
        "name": "IFTTT - Applets",
        "description": "Applets the account had connected, with the name of each, the service "
                       "it runs on, who published it and when the app first recorded it.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-02",
        "last_update_date": "2026-09-02",
        "requirements": "none",
        "category": "IFTTT",
        "notes": "Read from class_LiveConnectionRecord in the app's Realm store, which is where "
                 "the connected applets are held on the tested extraction; class_AppletRecord, "
                 "which the name suggests would carry them, held no rows. The service name is "
                 "joined from class_LiveServiceRecord through the row's own primaryService "
                 "link. Author is the applet's publisher as the service supplied it, not the "
                 "account on this device: an applet published by someone else and switched on "
                 "by this account shows that publisher. Created At is when the app first "
                 "recorded the applet locally, which is not the same as when the applet last "
                 "ran; no run history was present, see the Activity note below. Status and Kind "
                 "are reported as stored. The store's installsCount is how many IFTTT accounts "
                 "had that applet and is service-supplied popularity rather than anything about "
                 "this device, so it is not reported. Activity: class_ActivityItemRecord, "
                 "class_WidgetRunRecord and class_RegionEvent were present in the schema and "
                 "held no rows on the tested extraction, so no applet run, widget run or "
                 "geofence event was recovered.",
        "paths": ('*/Documents/default.realm',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "zap",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | com.ifttt.ifttt | 2 rows",
        },
    },
    "iftttServices": {
        "name": "IFTTT - Connected Services",
        "description": "Services the account had connected in IFTTT, with whether each was "
                       "connected and whether it required the account to authenticate.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-02",
        "last_update_date": "2026-09-02",
        "requirements": "none",
        "category": "IFTTT",
        "notes": "Read from class_LiveServiceRecord in the app's Realm store. Connected is the "
                 "store's own isConnected value; on the tested extraction it was true on every "
                 "row, so the column is uniform there, and it is kept because a service the "
                 "account had disconnected is exactly what an examiner would want "
                 "distinguished. class_ServiceFragmentRecord holds the same three services with "
                 "a subset of these fields and is not reported separately for that reason. "
                 "Requires Authentication, Offline, Hidden and Auto Activated are reported as "
                 "stored. The service description the store keeps is catalogue text supplied by "
                 "IFTTT and is not reported.",
        "paths": ('*/Documents/default.realm',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "grid",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | com.ifttt.ifttt | 3 rows",
        },
    },
    "iftttDetectedApps": {
        "name": "IFTTT - Detected Apps",
        "description": "The service identifiers IFTTT recorded under its app-detector "
                       "preference key on this device.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-02",
        "last_update_date": "2026-09-02",
        "requirements": "none",
        "category": "IFTTT",
        "notes": "Read from the app-detector.my-apps key of "
                 "Library/Preferences/com.ifttt.ifttt.plist. Each entry is an IFTTT service "
                 "identifier and the numeric identifier the service carries, reported as "
                 "stored. The key name and the entries together are consistent with a list the "
                 "app built from what it found on the device, and the list is a small subset of "
                 "the services IFTTT offered, but only one extraction holding this app was "
                 "available, so it could not be compared against a second device and this "
                 "artifact does not assert that an entry means the corresponding app was "
                 "installed. Treat it as a lead to check against the device's own installed "
                 "application artifacts rather than as an inventory. Entries naming iOS "
                 "built-in functions, and IFTTT's own notification and location services, "
                 "appear alongside third-party ones.",
        "paths": ('*/Library/Preferences/com.ifttt.ifttt.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "list",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | com.ifttt.ifttt | 24 rows",
        },
    },
}

import os
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, get_plist_file_content, logfunc
from scripts.realm_parser import parse_realm_file

# Classes specific to IFTTT's data model. An iOS container is GUID-named, so the
# path pattern cannot carry the bundle id; this is what keeps another app's
# Documents/default.realm from being reported as IFTTT's. Fails closed.
_MARKER_CLASSES = ('class_LiveConnectionRecord', 'class_LiveValuePropositionRecord')


def _utc(value):
    """A 'YYYY-MM-DD HH:MM:SS UTC' value as an aware datetime, or '' when unusable."""
    text = str(value or '').strip()
    if not text.endswith(' UTC'):
        return ''
    try:
        return datetime.strptime(text[:-4], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    except ValueError:
        return ''


def _text(value):
    """A displayable scalar. A list is rendered as its members, not its length."""
    if value is None:
        return ''
    if isinstance(value, bool):
        return value
    if isinstance(value, list):
        return ', '.join(str(item) for item in value)
    return value


def _stores(files_found):
    """Each Realm store that carries an IFTTT class, as (path, tables)."""
    found = []
    for file_found in files_found:
        file_found = str(file_found)
        # Realm keeps a default.realm.management directory beside the store, and
        # open() on a directory would end the artifact. Requiring the exact file
        # name excludes it and the .lock and .note siblings as well.
        if not file_found.endswith('default.realm') or os.path.isdir(file_found):
            continue
        try:
            tables = parse_realm_file(file_found).get('active') or {}
        except Exception as error:  # pylint: disable=broad-exception-caught
            logfunc(f'IFTTT: {os.path.basename(file_found)} did not parse: {error}')
            continue
        if not any(name in tables for name in _MARKER_CLASSES):
            continue
        found.append((file_found, tables))
    return found


def _rows(tables, class_name):
    """Every row of ``class_name`` as a {column_name: value} dict."""
    table = tables.get(class_name)
    if not table:
        return []
    names = table['column_names']
    columns = table['columns']
    out = []
    for i in range(table['row_count']):
        row = {}
        for j, name in enumerate(names):
            values = columns.get(j)
            row[name] = values[i] if values is not None and i < len(values) else None
        out.append(row)
    return out


def _linked(rows, index):
    """The row a link column points at, or None. Links are positional row indexes."""
    if index is None or isinstance(index, bool):
        return None
    try:
        position = int(index)
    except (TypeError, ValueError):
        return None
    return rows[position] if 0 <= position < len(rows) else None


@artifact_processor
def iftttAccount(context):
    data_headers = (
        ('Created At', 'datetime'),
        'Login',
        'Email',
        'User ID',
        'Time Zone',
        'User Type (as stored)',
        'Home Screen Preference (as stored)',
        'Is Admin',
    )
    data_list = []
    sources = []
    for store, tables in _stores(context.get_files_found()):
        read_any = False
        for row in _rows(tables, 'class_UserRecord'):
            data_list.append((
                _utc(row.get('createdAt')),
                _text(row.get('login')),
                _text(row.get('email')),
                _text(row.get('id')),
                _text(row.get('timezone')),
                _text(row.get('userType')),
                _text(row.get('homeScreenPreference')),
                _text(row.get('isAdmin')),
            ))
            read_any = True
        if read_any:
            sources.append(store)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def iftttApplets(context):
    data_headers = (
        ('Created At', 'datetime'),
        'Applet Name',
        'Service',
        'Author',
        'Kind (as stored)',
        'Status (as stored)',
        'By Service Owner',
        'Applet ID',
        'Description',
    )
    data_list = []
    sources = []
    for store, tables in _stores(context.get_files_found()):
        services = _rows(tables, 'class_LiveServiceRecord')
        read_any = False
        for row in _rows(tables, 'class_LiveConnectionRecord'):
            service = _linked(services, row.get('primaryService'))
            data_list.append((
                _utc(row.get('createdAt')),
                _text(row.get('name')),
                _text(service.get('name')) if service else _text(row.get('serviceId')),
                _text(row.get('author')),
                _text(row.get('kind')),
                _text(row.get('status')),
                _text(row.get('byServiceOwner')),
                _text(row.get('id')),
                _text(row.get('details')),
            ))
            read_any = True
        if read_any:
            sources.append(store)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def iftttServices(context):
    data_headers = (
        ('Created At', 'datetime'),
        'Service Name',
        'Short Name',
        'Service ID',
        'Numeric ID',
        'Connected',
        'Requires Authentication',
        'Offline',
        'Hidden',
        'Auto Activated',
    )
    data_list = []
    sources = []
    for store, tables in _stores(context.get_files_found()):
        read_any = False
        for row in _rows(tables, 'class_LiveServiceRecord'):
            data_list.append((
                _utc(row.get('createdAt')),
                _text(row.get('name')),
                _text(row.get('shortName')),
                _text(row.get('id')),
                _text(row.get('numericId')),
                _text(row.get('isConnected')),
                _text(row.get('requiresUserAuthentication')),
                _text(row.get('offline')),
                _text(row.get('isHidden')),
                _text(row.get('canBeAutoActivated')),
            ))
            read_any = True
        if read_any:
            sources.append(store)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def iftttDetectedApps(context):
    data_headers = (
        'Service ID',
        'Numeric ID',
        'Source File',
    )
    data_list = []
    sources = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.isdir(file_found) or not file_found.endswith('com.ifttt.ifttt.plist'):
            continue
        try:
            content = get_plist_file_content(file_found)
        except Exception as error:  # pylint: disable=broad-exception-caught
            logfunc(f'IFTTT: {os.path.basename(file_found)} did not parse: {error}')
            continue
        entries = (content or {}).get('app-detector.my-apps')
        if not isinstance(entries, list):
            continue
        read_any = False
        for entry in entries:
            if not isinstance(entry, dict):
                logfunc('IFTTT: an app-detector entry was not a dictionary, skipped')
                continue
            data_list.append((
                _text(entry.get('id')),
                _text(entry.get('numeric_id')),
                context.get_relative_path(file_found),
            ))
            read_any = True
        if read_any:
            sources.append(file_found)
    return data_headers, data_list, '\n'.join(sources)
