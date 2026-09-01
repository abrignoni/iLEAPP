__artifacts_v2__ = {
    "lgThinqDevices": {
        "name": "LG ThinQ - Devices",
        "description": "LG appliances registered to the ThinQ account, with the name the "
                       "account gave each one, its model and serial number, the Wi-Fi network "
                       "it reported and the room it is assigned to.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "LG ThinQ",
        "notes": "Read from the class_Product table of the app's Realm store using the vendored "
                 "realm_parser, with the sales model and serial number joined from class_ProductModel "
                 "on the product identifier and the room name joined from class_Room. The store's file "
                 "name carries the account and environment, so the path pattern matches on the "
                 "environment suffix and every candidate is then required to carry a class_Product "
                 "table before it is read; a file without one is skipped and logged. The app keeps two "
                 "further Realm files beside this one: shared-prd-op-op.realm holds only interface "
                 "layout and feature JSON, and the tv- prefixed file held nothing but its schema "
                 "version on the tested sample, so neither is reported. SSID is the wireless network "
                 "the appliance reported to the service, which places the appliance on that network "
                 "and is not evidence of the phone's own connection. Registered is a 17 digit packed "
                 "value of the form YYYYMMDDHHMMSSmmm; it is reformatted for reading but no time zone "
                 "is recorded anywhere in the store for it, so it is reported as stored in a text "
                 "column rather than rendered as UTC. Device Type, Platform Type and Network Type are "
                 "reported as stored. Online held one value on every appliance in the tested sample, "
                 "where all three were connected when the store was last written; it is kept because "
                 "an offline appliance is exactly what an examiner would want distinguished. The app's "
                 "data container was present on 1 of the 26 registered iOS corpora swept for it, so "
                 "every count recorded here comes from that one extraction.",
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
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "LG ThinQ",
        "notes": "Read from the class_Room table of the app's Realm store. The created_at column holds "
                 "two different shapes in the same column on the tested sample, an 8 digit YYYYMMDD "
                 "date on one row and a 14 digit YYYYMMDDHHMMSS value on another, so it is reformatted "
                 "from whichever shape is present and reported as stored in a text column; no time "
                 "zone is recorded for it. Is Default marks the room the app creates itself rather "
                 "than one the account added. The app's data container was present on 1 of the 26 "
                 "registered iOS corpora swept for it, so every count recorded here comes from that "
                 "one extraction.",
        "paths": ('*/Documents/*-op-op.realm*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "door",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 2 rows",
        },
    },
    "lgThinqFavorites": {
        "name": "LG ThinQ - Favorites",
        "description": "Items the account marked as favorites, with the created and modified "
                       "timestamps the service recorded.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "LG ThinQ",
        "notes": "Read from the class_FavoritesItem table of the app's Realm store. Unlike the other "
                 "date columns in this store these two carry an explicit UTC marker in the value "
                 "itself, so they are reported as datetimes. Item Type is reported as stored. Model ID "
                 "refers to the product identifier used by the Devices artifact, so the two can be "
                 "joined. Created At and Modified At held the same value on every row in the tested "
                 "sample, and Home ID held one value because that account had a single home. All three "
                 "are kept: the timestamps separate when a favorite was added from when it was last "
                 "changed, and Home ID shows which home an item belongs to on an account with more "
                 "than one. The app's data container was present on 1 of the 26 registered iOS corpora "
                 "swept for it, so every count recorded here comes from that one extraction.",
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
        "notes": "Read from the class_UserIdInfo table of the app's Realm store. Identifier Type is "
                 "the string the service uses to describe the identifier and is reported as stored. "
                 "The access token the same store holds in class_Token is deliberately not reported. "
                 "The app's data container was present on 1 of the 26 registered iOS corpora swept for "
                 "it, so every count recorded here comes from that one extraction.",
        "paths": ('*/Documents/*-op-op.realm*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 2 rows",
        },
    },
    "lgThinqServices": {
        "name": "LG ThinQ - Services",
        "description": "LG services the account is enrolled in, with the join date recorded "
                       "for each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "LG ThinQ",
        "notes": "Read from the class_Service table of the app's Realm store. Join Date is stored as a "
                 "text date whose field order is not stated by the store. It is read as month, day, "
                 "year on two grounds from the tested sample: the value resolves to the same day the "
                 "appliances in class_Product record as their registration date, and read as day first "
                 "it would fall after the date the extraction was taken. The reformatted date is "
                 "reported in a text column and no time of day or zone is recorded. Service Code is "
                 "reported as stored. The app's data container was present on 1 of the 26 registered "
                 "iOS corpora swept for it, so every count recorded here comes from that one "
                 "extraction.",
        "paths": ('*/Documents/*-op-op.realm*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 2 rows",
        },
    },
}

import os
import re
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.realm_parser import realm_rows

_MARKER_CLASS = 'class_Product'
_PACKED = re.compile(r'^(\d{4})(\d{2})(\d{2})(?:(\d{2})(\d{2})(\d{2}))?\d*$')


def _packed_as_stored(value):
    """Reformat a packed YYYYMMDD[HHMMSS[mmm]] value for reading, or '' when unusable.

    The store records no time zone for these columns, so the value is reformatted and
    reported as stored rather than rendered as an instant.
    """
    if value in (None, ''):
        return ''
    match = _PACKED.match(str(value).strip())
    if not match:
        return str(value)
    year, month, day, hour, minute, second = match.groups()
    stamp = f'{year}-{month}-{day}'
    if hour:
        stamp += f' {hour}:{minute}:{second}'
    return stamp


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
    """A month-first MM-DD-YYYY text date reformatted as YYYY-MM-DD, or the raw value."""
    if not value or not isinstance(value, str):
        return ''
    match = re.match(r'^(\d{2})-(\d{2})-(\d{4})$', value.strip())
    if not match:
        return value
    month, day, year = match.groups()
    return f'{year}-{month}-{day}'


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
