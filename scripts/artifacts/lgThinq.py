__artifacts_v2__ = {
    "lgThinqDevices": {
        "name": "LG ThinQ - Devices",
        "description": "LG appliances held in the ThinQ app's Realm store, with the name, model, "
                       "serial number, SSID and room recorded for each.",
        "author": "@AlexisBrignoni, Claude, Codex",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "LG ThinQ",
        "notes": "Read from the class_Product table of the app's Realm store using the vendored "
                 "realm_parser, with the sales model and serial number joined from "
                 "class_ProductModel on the product identifier and the room name joined from "
                 "class_Room. The store's file name carries the account and environment, so the "
                 "path pattern matches on the environment suffix and every candidate is then "
                 "required to hold at least one class_Product row before it is read; a file with "
                 "no such row is skipped without a log line (a file that cannot be read is "
                 "logged), and none of the ThinQ artifacts report anything from a skipped file. "
                 "Two further Realm files sat beside this one on the tested sample: "
                 "shared-prd-op-op.realm held only interface layout and feature JSON and the tv- "
                 "prefixed file held nothing but its schema version, so neither is reported. SSID "
                 "is the network name stored against the appliance; it is not evidence of the "
                 "phone's own connection. Registered is a 17 digit packed value of the form "
                 "YYYYMMDDHHMMSSmmm; all stored digits are reported as text without assigning "
                 "a time zone. Device Type, Platform Type and Network Type are "
                 "reported as stored. Online is reported as stored. It held one value on all 3 "
                 "rows of the tested sample; what the other value looks like and what moment the "
                 "value reflects are not established. Every count recorded here comes from one "
                 "extraction, adams_iphone12mini.",
        "paths": ('*/Documents/*-op-op.realm*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "device-washing-machine",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 3 rows",
        },
    },
    "lgThinqRooms": {
        "name": "LG ThinQ - Rooms",
        "description": "Rooms defined in the ThinQ home, with the creation value stored for "
                       "each.",
        "author": "@AlexisBrignoni, Claude, Codex",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "LG ThinQ",
        "notes": "Read from the class_Room table of the app's Realm store. The created_at column "
                 "holds two different shapes in the same column on the tested sample, an 8 digit "
                 "YYYYMMDD date on one row and a 14 digit YYYYMMDDHHMMSS value on another, so it "
                 "is reported as stored text with all digits retained. No time zone is recorded for "
                 "it. Is Default is the store's flag as stored. Every count recorded here comes "
                 "from one extraction, adams_iphone12mini.",
        "paths": ('*/Documents/*-op-op.realm*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "door",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 2 rows",
        },
    },
    "lgThinqFavorites": {
        "name": "LG ThinQ - Favorites",
        "description": "Rows of the FavoritesItem class in the ThinQ app's Realm store, with the "
                       "createdAt and modifiedAt values stored for each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "LG ThinQ",
        "notes": "Read from the class_FavoritesItem table of the app's Realm store. Unlike the "
                 "other date columns in this store these two carry an explicit UTC marker in the "
                 "value itself, so they are reported as datetimes. Item Type is reported as "
                 "stored. Model ID is the row's modelID value, reported as stored. Created At and "
                 "Modified At held the same value on every row in the tested sample, and Home ID "
                 "held one value because that account had a single home. All three are reported. "
                 "What createdAt and modifiedAt each mark is not established, since they did not "
                 "differ on the tested rows, and Home ID was not tested on an account with more "
                 "than one home. Every count recorded here comes from one extraction, "
                 "adams_iphone12mini.",
        "paths": ('*/Documents/*-op-op.realm*',),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "star",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 3 rows",
        },
    },
    "lgThinqAccount": {
        "name": "LG ThinQ - Account Identifiers",
        "description": "Account identifiers the ThinQ app stored, with the identifier type "
                       "recorded for each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "LG ThinQ",
        "notes": "Read from the class_UserIdInfo table of the app's Realm store. Identifier Type "
                 "is the row's idType value and is reported as stored; what each value denotes is "
                 "not established. The access token the same store holds in class_Token is "
                 "deliberately not reported. Every count recorded here comes from one extraction, "
                 "adams_iphone12mini.",
        "paths": ('*/Documents/*-op-op.realm*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 2 rows",
        },
    },
    "lgThinqServices": {
        "name": "LG ThinQ - Services",
        "description": "Rows of the Service class in the ThinQ app's Realm store, with the "
                       "service name, code, isService flag and joinDate value stored for each.",
        "author": "@AlexisBrignoni, Claude, Codex",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "LG ThinQ",
        "notes": "Read from the class_Service table of the app's Realm store. Join Date is stored "
                 "as a text date whose field order is not stated by the store; the original text "
                 "is retained without reordering it. No time of day or zone is recorded. Service Code is reported as stored. "
                 "Every count recorded here comes from one extraction, adams_iphone12mini.",
        "paths": ('*/Documents/*-op-op.realm*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 2 rows",
        },
    },
}

import os
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.realm_parser import realm_rows

_MARKER_CLASS = 'class_Product'


def _packed_as_stored(value):
    """Report a packed date value as stored text, with no assigned time zone.

    The store records no time zone for these columns, so the original digits are retained rather than rendered as an instant.
    """
    if value in (None, ''):
        return ''
    return str(value)



def _utc_marked(value):
    """A 'YYYY-MM-DD HH:MM:SS UTC' value as an aware datetime, or '' when unusable."""
    if not value or not isinstance(value, str):
        return ''
    text = value.strip()
    if not text.endswith(' UTC'):
        return ''
    try:
        return datetime.strptime(text[:-4], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    except ValueError:
        return ''


def _month_first_date(value):
    """A date value as stored text, without assuming its field order."""
    return '' if value is None else str(value)



def _stores(files_found):
    """The ThinQ Realm files, sidecars and files without the marker class excluded."""
    stores = []
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.isdir(file_found) or not file_found.endswith('.realm'):
            continue
        try:
            rows = list(realm_rows(file_found, _MARKER_CLASS))
        except Exception as error:  # pylint: disable=broad-exception-caught
            logfunc(f'LG ThinQ: could not read {os.path.basename(file_found)}: {error}')
            continue
        if not rows:
            continue
        stores.append(file_found)
    return stores


def _rows(store, class_name):
    """Rows of a Realm class, or nothing when the class is absent or unreadable."""
    try:
        return list(realm_rows(store, class_name))
    except Exception as error:  # pylint: disable=broad-exception-caught
        logfunc(f'LG ThinQ: {class_name} not read from '
                f'{os.path.basename(store)}: {error}')
        return []


def _text(value):
    """A displayable value; a list is joined and a dictionary is not rendered."""
    if value is None:
        return ''
    if isinstance(value, bool):
        return value
    if isinstance(value, list):
        return ', '.join(str(item) for item in value)
    if isinstance(value, dict):
        return ''
    return value


@artifact_processor
def lgThinqDevices(context):
    data_headers = (
        'Registered (as stored, no zone recorded)',
        'Device Alias',
        'Model Name',
        'Sales Model',
        'Serial Number',
        'Room',
        'SSID',
        'Time Zone',
        'Online',
        'Device Type (as stored)',
        'Device Code (as stored)',
        'Platform Type (as stored)',
        'Network Type (as stored)',
        'Product ID',
        'Source File',
    )
    data_list = []
    source_files = []

    for store in _stores(context.get_files_found()):
        models = {}
        for row in _rows(store, 'class_ProductModel'):
            if row.get('deviceId'):
                models[row['deviceId']] = row
        rooms = {}
        for row in _rows(store, 'class_Room'):
            if row.get('roomId'):
                rooms[row['roomId']] = row
        count = 0
        for row in _rows(store, 'class_Product'):
            count += 1
            model = models.get(row.get('productId')) or {}
            room = rooms.get(row.get('roomId')) or {}
            data_list.append((
                _packed_as_stored(row.get('regDt')),
                _text(row.get('alias')),
                _text(row.get('name')),
                _text(model.get('salesModel')),
                _text(model.get('serialNo')),
                _text(room.get('name')),
                _text(row.get('ssid')),
                _text(row.get('timezoneCode')),
                _text(row.get('online')),
                _text(row.get('type')),
                _text(row.get('deviceCode')),
                _text(row.get('platformType')),
                _text(row.get('networkType')),
                _text(row.get('productId')),
                context.get_relative_path(store),
            ))
        if count:
            source_files.append(store)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def lgThinqRooms(context):
    data_headers = (
        'Created (as stored, no zone recorded)',
        'Room Name',
        'Is Default',
        'Room Type (as stored)',
        'Room ID',
        'Source File',
    )
    data_list = []
    source_files = []

    for store in _stores(context.get_files_found()):
        count = 0
        for row in _rows(store, 'class_Room'):
            count += 1
            data_list.append((
                _packed_as_stored(row.get('created_at')),
                _text(row.get('name')),
                _text(row.get('isDefault')),
                _text(row.get('type')),
                _text(row.get('roomId')),
                context.get_relative_path(store),
            ))
        if count:
            source_files.append(store)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def lgThinqFavorites(context):
    data_headers = (
        ('Created At', 'datetime'),
        ('Modified At', 'datetime'),
        'Item Type (as stored)',
        'Model ID',
        'Home ID',
        'Order',
        'Favorite ID',
        'Source File',
    )
    data_list = []
    source_files = []

    for store in _stores(context.get_files_found()):
        count = 0
        for row in _rows(store, 'class_FavoritesItem'):
            count += 1
            data_list.append((
                _utc_marked(row.get('createdAt')),
                _utc_marked(row.get('modifiedAt')),
                _text(row.get('itemType')),
                _text(row.get('modelID')),
                _text(row.get('homeID')),
                _text(row.get('order')),
                _text(row.get('id')),
                context.get_relative_path(store),
            ))
        if count:
            source_files.append(store)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def lgThinqAccount(context):
    data_headers = (
        'Identifier Type (as stored)',
        'User ID',
        'Source File',
    )
    data_list = []
    source_files = []

    for store in _stores(context.get_files_found()):
        count = 0
        for row in _rows(store, 'class_UserIdInfo'):
            count += 1
            data_list.append((
                _text(row.get('idType')),
                _text(row.get('userId')),
                context.get_relative_path(store),
            ))
        if count:
            source_files.append(store)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def lgThinqServices(context):
    data_headers = (
        'Join Date (as stored, no zone recorded)',
        'Service Name',
        'Service Code (as stored)',
        'Is Service',
        'Source File',
    )
    data_list = []
    source_files = []

    for store in _stores(context.get_files_found()):
        count = 0
        for row in _rows(store, 'class_Service'):
            count += 1
            data_list.append((
                _month_first_date(row.get('joinDate')),
                _text(row.get('svcName')),
                _text(row.get('svcCode')),
                _text(row.get('isService')),
                context.get_relative_path(store),
            ))
        if count:
            source_files.append(store)

    return data_headers, data_list, '\n'.join(source_files)
