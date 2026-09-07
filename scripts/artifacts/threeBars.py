__artifacts_v2__ = {
    'threeBarsNetworks': {
        'name': 'Wi-Fi ThreeBars - Networks',
        'description': 'Wi-Fi networks held in the Wi-Fi daemon ThreeBars cache, with the '
                       'centroid coordinates the location service reported for each one',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-29',
        'last_update_date': '2026-08-21',
        'requirements': 'none',
        'category': 'Locations',
        'notes': ("ThreeBars holds Wi-Fi network records with coordinates stored against each "
                  "network. A row does not establish that this device connected to or observed "
                  "the network, and the coordinates are stored against the network rather than "
                  "as a device position; how the cache is populated is not sourced here. "
                  'The venue, type, authentication mask and score columns are integer codes '
                  'whose values are not documented and are reported as stored. A row whose '
                  'latitude and longitude are both exactly zero holds no position and is '
                  'reported with empty coordinates rather than plotted at 0/0.'),
        'paths': ('*/root/Library/Caches/com.apple.wifid/ThreeBars.sqlite*',),
        'output_types': 'all',
        'artifact_icon': 'wifi',
        'sample_data': {
            'magnet_ios16': 'iOS 16.1.1 | 430 rows',
            'iphone11_ios17': 'iOS 17.3 | 195 rows',
            'hc_ios18_7': '2092 rows spanning about six weeks; ZNAME empty on '
                                      'every row in all three images tested',
        },
    },
    'threeBarsAccessPoints': {
        'name': 'Wi-Fi ThreeBars - Access Points',
        'description': 'Individual access points in the Wi-Fi daemon ThreeBars cache, with '
                       'their BSSID and reported coordinates',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-29',
        'last_update_date': '2026-08-21',
        'requirements': 'none',
        'category': 'Locations',
        'notes': ("Same caveat as the networks artifact: a row does not establish that this "
                  "device connected to the access point, and how the cache is populated is not "
                  "sourced here. "
                  'Each row is joined to its parent network through ZNETWORK. A row whose '
                  'latitude and longitude are both exactly zero holds no position and is '
                  'reported with empty coordinates rather than plotted at 0/0.'),
        'paths': ('*/root/Library/Caches/com.apple.wifid/ThreeBars.sqlite*',),
        'output_types': 'all',
        'artifact_icon': 'router',
        'sample_data': {
            'magnet_ios16': 'iOS 16.1.1 | 16713 rows',
            'iphone11_ios17': 'iOS 17.3 | 8927 rows',
            'hc_ios18_7': '52096 rows across 2092 networks',
        },
    },
    'threeBarsTiles': {
        'name': 'Wi-Fi ThreeBars - Downloaded Tiles',
        'description': "Tile records in the Wi-Fi daemon ThreeBars cache, with the timestamp "
                       "stored against each",
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-29',
        'last_update_date': '2026-08-21',
        'requirements': 'none',
        'category': 'Locations',
        'notes': ("A tile row carries a key and a timestamp, both reported as stored; what event "
                  "writes a tile row is not sourced here. The tile key is not decoded here "
                  "because its "
                  'mapping to a geographic area is not documented; the networks and access '
                  'points belonging to a tile carry the coordinates.'),
        'paths': ('*/root/Library/Caches/com.apple.wifid/ThreeBars.sqlite*',),
        'output_types': 'standard',
        'artifact_icon': 'grid-dots',
        'sample_data': {
            'magnet_ios16': 'iOS 16.1.1 | 168 rows',
            'iphone11_ios17': 'iOS 17.3 | 5 rows',
            'hc_ios18_7': '51 rows',
        },
    },
}

from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_sqlite_db_records, null_absent_columns, does_table_exist_in_db, \
    convert_cocoa_core_data_ts_to_utc


def _coordinates(latitude, longitude):
    """Return a coordinate pair, blanking the 0/0 placeholder.

    A handful of rows per image carry latitude and longitude both exactly zero,
    which is the absence of a position rather than a point in the Gulf of
    Guinea. They are reported empty so the KML output does not gain pins there;
    the rest of the row is reported as normal.
    """
    if not latitude and not longitude:
        return '', ''
    return latitude, longitude


def _yes_no(value):
    """Render a 0/1 flag, leaving anything unexpected as stored."""
    if value == 1:
        return 'Yes'
    if value == 0:
        return 'No'
    return value


@artifact_processor
def threeBarsNetworks(context):
    source_path = get_file_path(context.get_files_found(), 'ThreeBars.sqlite')
    data_list = []
    data_headers = (
        ('Created', 'datetime'), 'Latitude', 'Longitude', 'Network Name', 'Identifier',
        'Access Point Count', 'Captive', 'Public', 'Moving', 'Suspicious', 'Low Quality',
        'Quality Score', 'Popularity Score', 'Auth Mask', 'Type', 'Venue Group', 'Venue Type',
        'Tile Key', 'Record ID')
    if not source_path or not does_table_exist_in_db(source_path, 'ZNETWORK'):
        return data_headers, data_list, source_path or ''

    query = '''
    SELECT ZCREATED, ZCENTROIDLAT, ZCENTROIDLNG, ZNAME, ZIDENTIFIER, ZACCESSPOINTCOUNT,
           ZCAPTIVE, ZPUBLIC, ZMOVING, ZSUSPICIOUS, ZLOWQUALITY, ZQUALITYSCOREVALUE,
           ZPOPULARITYSCOREVALUE, ZAUTHMASK, ZTYPE, ZVENUEGROUP, ZVENUETYPE, ZTILEKEY, Z_PK
    FROM ZNETWORK
    ORDER BY ZCREATED
    '''

    for record in get_sqlite_db_records(source_path, null_absent_columns(source_path, query)):
        latitude, longitude = _coordinates(record['ZCENTROIDLAT'], record['ZCENTROIDLNG'])
        data_list.append((
            convert_cocoa_core_data_ts_to_utc(record['ZCREATED']),
            latitude,
            longitude,
            record['ZNAME'],
            record['ZIDENTIFIER'],
            record['ZACCESSPOINTCOUNT'],
            _yes_no(record['ZCAPTIVE']),
            _yes_no(record['ZPUBLIC']),
            _yes_no(record['ZMOVING']),
            _yes_no(record['ZSUSPICIOUS']),
            _yes_no(record['ZLOWQUALITY']),
            record['ZQUALITYSCOREVALUE'],
            record['ZPOPULARITYSCOREVALUE'],
            record['ZAUTHMASK'],
            record['ZTYPE'],
            record['ZVENUEGROUP'],
            record['ZVENUETYPE'],
            record['ZTILEKEY'],
            record['Z_PK'],
        ))

    return data_headers, data_list, source_path


@artifact_processor
def threeBarsAccessPoints(context):
    source_path = get_file_path(context.get_files_found(), 'ThreeBars.sqlite')
    data_list = []
    data_headers = (
        ('Created', 'datetime'), 'Latitude', 'Longitude', 'BSSID', 'Network Name',
        'Network Identifier', 'Edge', 'TCP Good', 'Quality Score', 'Popularity Score',
        'Record ID')
    if not source_path or not does_table_exist_in_db(source_path, 'ZACCESSPOINT'):
        return data_headers, data_list, source_path or ''

    join = ''
    columns = ''
    if does_table_exist_in_db(source_path, 'ZNETWORK'):
        columns = ', ZNETWORK.ZNAME, ZNETWORK.ZIDENTIFIER'
        join = 'LEFT JOIN ZNETWORK ON ZNETWORK.Z_PK = ZACCESSPOINT.ZNETWORK'

    query = f'''
    SELECT ZACCESSPOINT.ZCREATED, ZACCESSPOINT.ZLAT, ZACCESSPOINT.ZLNG,
           ZACCESSPOINT.ZBSSID, ZACCESSPOINT.ZEDGE, ZACCESSPOINT.ZTCPGOOD,
           ZACCESSPOINT.ZQUALITYSCOREVALUE, ZACCESSPOINT.ZPOPULARITYSCOREVALUE,
           ZACCESSPOINT.Z_PK{columns}
    FROM ZACCESSPOINT
    {join}
    ORDER BY ZACCESSPOINT.ZCREATED
    '''

    for record in get_sqlite_db_records(source_path, null_absent_columns(source_path, query)):
        keys = record.keys()
        latitude, longitude = _coordinates(record['ZLAT'], record['ZLNG'])
        data_list.append((
            convert_cocoa_core_data_ts_to_utc(record['ZCREATED']),
            latitude,
            longitude,
            record['ZBSSID'],
            record['ZNAME'] if 'ZNAME' in keys else '',
            record['ZIDENTIFIER'] if 'ZIDENTIFIER' in keys else '',
            record['ZEDGE'],
            _yes_no(record['ZTCPGOOD']),
            record['ZQUALITYSCOREVALUE'],
            record['ZPOPULARITYSCOREVALUE'],
            record['Z_PK'],
        ))

    return data_headers, data_list, source_path


@artifact_processor
def threeBarsTiles(context):
    source_path = get_file_path(context.get_files_found(), 'ThreeBars.sqlite')
    data_list = []
    data_headers = (
        ('Created', 'datetime'), 'Tile Key', 'Network Count', 'ETag', 'Record ID')
    if not source_path or not does_table_exist_in_db(source_path, 'ZTILE'):
        return data_headers, data_list, source_path or ''

    query = '''
    SELECT ZCREATED, ZKEY, ZNETWORKCOUNT, ZETAG, Z_PK
    FROM ZTILE
    ORDER BY ZCREATED
    '''

    for record in get_sqlite_db_records(source_path, null_absent_columns(source_path, query)):
        data_list.append((
            convert_cocoa_core_data_ts_to_utc(record['ZCREATED']),
            record['ZKEY'],
            record['ZNETWORKCOUNT'],
            record['ZETAG'],
            record['Z_PK'],
        ))

    return data_headers, data_list, source_path
