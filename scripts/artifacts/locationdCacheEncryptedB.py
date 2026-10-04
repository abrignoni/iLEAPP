__artifacts_v2__ = {
    'locationdWifiLocations': {
        'name': 'Locationd Cache - Wi-Fi Locations',
        'description': "Rows of locationd's WifiLocation cache table, with the BSSID and "
                       'coordinates each row stores',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-29',
        'last_update_date': '2026-08-21',
        'requirements': 'none',
        'category': 'Locations',
        'notes': ("Each row pairs a BSSID with coordinates in the WifiLocation table; the table "
                  "and column names are the only labels used here. Apple states that Location "
                  "Services uses crowd-sourced Wi-Fi hotspot locations (Reference: Apple, "
                  "'Location Services & Privacy', "
                  "https://www.apple.com/legal/privacy/data/en/location-services/); that page "
                  "does not name this table. A row does not show that the device was at those "
                  "coordinates or connected to that access point. Horizontal Accuracy is reported "
                  "as stored. Speed and course values of -1 are reported as stored and are not "
                  "converted; their meaning is not documented. AlsQueryTimestamp was present on "
                  "the iOS 26 tested image; what distinguishes it from Timestamp is not "
                  "documented, so both are converted the same way (seconds since 2001, shown in "
                  "UTC, with a stored value of 0 or less left blank) and neither is given a "
                  "meaning here."),
        'paths': ('*/root/Library/Caches/locationd/cache_encryptedB.db*',),
        'output_types': 'all',
        'artifact_icon': 'wifi',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 30665 rows',
            'magnet_ios16': 'iOS 16.1.1 | 0 rows; table present and empty',
            'hc_ios18_7': '90783 rows',
            'hc_ios26': '142 rows; gains AlsQueryTimestamp',
        },
    },
    'locationdWifiHarvest': {
        'name': 'Locationd Cache - Associated Wi-Fi Harvest',
        'description': "Rows from locationd's associated Wi-Fi harvest table, with the BSSID, "
                       "position, signal strength and scan time as stored",
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-29',
        'last_update_date': '2026-08-21',
        'requirements': 'none',
        'category': 'Locations',
        'notes': ('The source table is named WifiAssociatedApWifiHarvestTable. The name points to '
                  'access points the device associated with, but what causes a row to be written '
                  'is not established here, so a row is not by itself proof of a connection. '
                  'Whether the coordinates are the position of the device at that time or of the '
                  'access point is not documented. Two timestamps are kept, Timestamp and '
                  'ScanTimestamp; what each marks is not established here. Both are read as '
                  'seconds since 2001 in UTC, and a value of 0 or less in either is left blank. A '
                  'scan timestamp of -1 is reported empty rather '
                  "than converted to a real looking date in 2000; what the value means is not "
                  "documented. The LoiType column is an integer code whose values "
                  'are not documented.'),
        'paths': ('*/root/Library/Caches/locationd/cache_encryptedB.db*',),
        'output_types': 'all',
        'artifact_icon': 'router',
        'sample_data': {
            'magnet_ios16': 'iOS 16.1.1 | table absent on this schema',
            'iphone11_ios17': 'iOS 17.3 | 0 rows; case data not committed, see the case note',
            'hc_ios18_7': '122 rows',
            'hc_ios26': '148 rows; schema unchanged',
        },
    },
    'locationdCellLocations': {
        'name': 'Locationd Cache - Cell Locations',
        'description': "Cell identifiers and coordinates stored in locationd's cell location "
                       'cache, across the eight cell tables this parser reads (CellLocation, '
                       'LteCellLocation, NrCellLocation, ScdmaCellLocation, CdmaCellLocation and '
                       'the Local variants of three of them)',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-29',
        'last_update_date': '2026-08-21',
        'requirements': 'none',
        'category': 'Locations',
        'notes': ("As with the Wi-Fi table, a row pairs cell identifiers with coordinates as the "
                  "cache stores them; the table and column names are the only labels used here. "
                  "Apple states that Location Services uses crowd-sourced cell tower locations "
                  "(Reference: Apple, 'Location Services & Privacy', "
                  "https://www.apple.com/legal/privacy/data/en/location-services/); that page does "
                  "not name these tables. A row does not show that the device was at those "
                  "coordinates. Horizontal Accuracy is reported as stored. The Radio column is a "
                  "label this parser assigns from the source table's name: CellLocation is shown "
                  "as GSM/UMTS, LteCellLocation as LTE, NrCellLocation as 5G NR, ScdmaCellLocation "
                  "as TD-SCDMA and CdmaCellLocation as CDMA, with (Local) added for the tables "
                  "whose name ends in Local. Tables whose name ends in Local are reported "
                  "separately because the "
                  'difference from their counterparts is not documented. Rows are folded into '
                  'shared columns, so Area Code holds LAC or TAC depending on the radio, and '
                  'identifiers specific to CDMA are kept in Additional Identifiers.'),
        'paths': ('*/root/Library/Caches/locationd/cache_encryptedB.db*',),
        'output_types': 'all',
        'artifact_icon': 'antenna-bars-5',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 2060 rows, all LTE; case data not committed, see '
                              'the case note',
            'magnet_ios16': 'iOS 16.1.1 | 0 rows across all nine tables',
            'hc_ios18_7': '1090 rows, all LTE; the other eight tables were empty',
            'hc_ios26': '450 rows, all LTE; schema unchanged',
        },
    },
    'locationdWifiTiles': {
        'name': 'Locationd Cache - Wi-Fi Tiles',
        'description': 'Map tiles of Wi-Fi location data held by locationd, with the area each '
                       'covers and its generation and access timestamps',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-29',
        'last_update_date': '2026-08-21',
        'requirements': 'none',
        'category': 'Locations',
        'notes': ("Each row is a row of the WifiTileHeader table; the column names are the only "
                  "labels used here. Access Timestamp and Generation Timestamp are the "
                  "AccessTimestamp and GenerationTimestamp columns read as seconds since 2001 in "
                  "UTC, with a value of 0 or less left blank; what each marks is not established "
                  "here. The reported latitude and longitude are the SouthwestLatitude and "
                  "SouthwestLongitude columns, so by name the coordinates are a corner rather "
                  "than a centre; Delta Latitude and Delta Longitude are reported as stored and "
                  "by name give the extent from that corner."),
        'paths': ('*/root/Library/Caches/locationd/cache_encryptedB.db*',),
        'output_types': 'all',
        'artifact_icon': 'grid-dots',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 89 rows; case data not committed, see the case note',
            'magnet_ios16': 'iOS 16.1.1 | 0 rows',
            'hc_ios18_7': '180 rows',
            'hc_ios26': '74 rows; schema unchanged',
        },
    },
}

from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_sqlite_db_records, does_table_exist_in_db, \
    convert_cocoa_core_data_ts_to_utc

# Cell tables share a layout apart from the identifier columns. Each entry maps a
# table to the radio label and the columns that carry the area, cell, channel and
# physical identifiers for that radio.
CELL_TABLES = (
    ('CellLocation', 'GSM/UMTS', 'LAC', 'CI', 'UARFCN', 'PSC', ()),
    ('CellLocationLocal', 'GSM/UMTS (Local)', 'LAC', 'CI', 'UARFCN', 'PSC', ()),
    ('LteCellLocation', 'LTE', 'TAC', 'CI', 'UARFCN', 'PID', ()),
    ('LteCellLocationLocal', 'LTE (Local)', 'TAC', 'CI', 'UARFCN', 'PID', ()),
    ('NrCellLocation', '5G NR', 'TAC', 'CI', 'NRARFCN', 'PID', ()),
    ('ScdmaCellLocation', 'TD-SCDMA', 'LAC', 'CI', 'UARFCN', 'PSC', ()),
    ('CdmaCellLocation', 'CDMA', None, 'BSID', 'CHANNEL', 'PNOFFSET',
     ('SID', 'NID', 'ZONEID', 'BANDCLASS')),
    ('CdmaCellLocationLocal', 'CDMA (Local)', None, 'BSID', 'CHANNEL', 'PNOFFSET',
     ('SID', 'NID', 'ZONEID', 'BANDCLASS')),
)


def _timestamp(value):
    """Convert a Cocoa timestamp, treating the -1 sentinel as no value.

    locationd writes -1 where it has nothing to record, the same convention it
    uses for speed and course. Converting it yields 2000-12-31, a real looking
    date that was never a real event, so those cells are left empty instead.
    """
    if value is None or value == '' or value <= 0:
        return ''
    return convert_cocoa_core_data_ts_to_utc(value)


def _mac(value):
    """Format the integer BSSID as a colon separated MAC address."""
    if value is None or value == '':
        return ''
    try:
        number = int(value)
    except (TypeError, ValueError):
        return value
    return ':'.join(f'{(number >> shift) & 0xFF:02x}' for shift in (40, 32, 24, 16, 8, 0))


@artifact_processor
def locationdWifiLocations(context):
    source_path = get_file_path(context.get_files_found(), 'cache_encryptedB.db')
    data_list = []
    data_headers = (
        ('Timestamp', 'datetime'), ('ALS Query Timestamp', 'datetime'), 'Latitude',
        'Longitude', 'BSSID', 'Horizontal Accuracy', 'Altitude', 'Vertical Accuracy',
        'Speed', 'Course', 'Channel', 'Confidence', 'Score', 'Reach', 'Info Mask')
    if not source_path:
        return data_headers, data_list, ''
    if not does_table_exist_in_db(source_path, 'WifiLocation'):
        return data_headers, data_list, source_path

    # AlsQueryTimestamp arrived with iOS 26, so the column list is built from the
    # table rather than hardcoded.
    wanted = ('Timestamp', 'AlsQueryTimestamp', 'Latitude', 'Longitude', 'MAC',
              'HorizontalAccuracy', 'Altitude', 'VerticalAccuracy', 'Speed', 'Course',
              'Channel', 'Confidence', 'Score', 'Reach', 'InfoMask')
    available = {record['name'] for record in
                 get_sqlite_db_records(source_path, 'PRAGMA table_info(WifiLocation)')}
    columns = ', '.join(name for name in wanted if name in available)
    query = f'''
    SELECT {columns}
    FROM WifiLocation
    ORDER BY Timestamp, WifiLocation.rowid
    '''

    for record in get_sqlite_db_records(source_path, query):
        keys = record.keys()
        data_list.append((
            _timestamp(record['Timestamp']),
            _timestamp(record['AlsQueryTimestamp']) if 'AlsQueryTimestamp' in keys else '',
            record['Latitude'],
            record['Longitude'],
            _mac(record['MAC']),
            record['HorizontalAccuracy'],
            record['Altitude'],
            record['VerticalAccuracy'],
            record['Speed'],
            record['Course'],
            record['Channel'],
            record['Confidence'],
            record['Score'],
            record['Reach'],
            record['InfoMask'],
        ))

    return data_headers, data_list, source_path


@artifact_processor
def locationdWifiHarvest(context):
    source_path = get_file_path(context.get_files_found(), 'cache_encryptedB.db')
    data_list = []
    data_headers = (
        ('Timestamp', 'datetime'), ('Scan Timestamp', 'datetime'), 'Latitude', 'Longitude',
        'BSSID', 'RSSI', 'Channel', 'Horizontal Accuracy', 'Altitude', 'Vertical Accuracy',
        'LOI Type')
    table = 'WifiAssociatedApWifiHarvestTable'
    if not source_path:
        return data_headers, data_list, ''
    if not does_table_exist_in_db(source_path, table):
        return data_headers, data_list, source_path

    query = f'''
    SELECT Timestamp, ScanTimestamp, Latitude, Longitude, MAC, Rssi, Channel,
           HorizontalAccuracy, Altitude, VerticalAccuracy, LoiType
    FROM {table}
    ORDER BY Timestamp
    '''

    for record in get_sqlite_db_records(source_path, query):
        data_list.append((
            _timestamp(record['Timestamp']),
            _timestamp(record['ScanTimestamp']),
            record['Latitude'],
            record['Longitude'],
            _mac(record['MAC']),
            record['Rssi'],
            record['Channel'],
            record['HorizontalAccuracy'],
            record['Altitude'],
            record['VerticalAccuracy'],
            record['LoiType'],
        ))

    return data_headers, data_list, source_path


@artifact_processor
def locationdCellLocations(context):
    source_path = get_file_path(context.get_files_found(), 'cache_encryptedB.db')
    data_list = []
    data_headers = (
        ('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Radio', 'MCC', 'MNC',
        'Area Code', 'Cell ID', 'Channel', 'Physical Cell ID', 'Additional Identifiers',
        'Horizontal Accuracy', 'Altitude', 'Vertical Accuracy', 'Speed', 'Course',
        'Confidence')
    if not source_path:
        return data_headers, data_list, ''

    for table, radio, area, cell, channel, physical, extras in CELL_TABLES:
        if not does_table_exist_in_db(source_path, table):
            continue

        wanted = ['Timestamp', 'Latitude', 'Longitude', 'MCC', 'MNC', cell, channel,
                  physical, 'HorizontalAccuracy', 'Altitude', 'VerticalAccuracy', 'Speed',
                  'Course', 'Confidence']
        if area:
            wanted.append(area)
        wanted.extend(extras)

        # The CDMA tables have no MNC, and columns have moved before now, so ask
        # the table which of these it actually has.
        available = {record['name'] for record in
                     get_sqlite_db_records(source_path, f'PRAGMA table_info({table})')}
        columns = ', '.join(name for name in dict.fromkeys(wanted) if name in available)

        query = f'SELECT {columns} FROM {table}'
        for record in get_sqlite_db_records(source_path, query):
            keys = record.keys()

            def value(column, keys=keys, record=record):
                return record[column] if column and column in keys else ''

            additional = ', '.join(f'{name}={value(name)}' for name in extras)
            data_list.append((
                _timestamp(record['Timestamp']),
                record['Latitude'],
                record['Longitude'],
                radio,
                value('MCC'),
                value('MNC'),
                value(area),
                value(cell),
                value(channel),
                value(physical),
                additional,
                record['HorizontalAccuracy'],
                record['Altitude'],
                record['VerticalAccuracy'],
                record['Speed'],
                record['Course'],
                record['Confidence'],
            ))

    data_list.sort(key=lambda row: (row[0] is None, row[0]))
    return data_headers, data_list, source_path


@artifact_processor
def locationdWifiTiles(context):
    source_path = get_file_path(context.get_files_found(), 'cache_encryptedB.db')
    data_list = []
    data_headers = (
        ('Access Timestamp', 'datetime'), ('Generation Timestamp', 'datetime'),
        'Latitude', 'Longitude', 'Delta Latitude', 'Delta Longitude', 'Tile X', 'Tile Y',
        'Altitude', 'Minimum Altitude', 'Maximum Altitude', 'Index Entries', 'Input Points',
        'Expiration Age', 'Version', 'Flags')
    if not source_path:
        return data_headers, data_list, ''
    if not does_table_exist_in_db(source_path, 'WifiTileHeader'):
        return data_headers, data_list, source_path

    query = '''
    SELECT AccessTimestamp, GenerationTimestamp, SouthwestLatitude, SouthwestLongitude,
           DeltaLatitude, DeltaLongitude, TileX, TileY, Altitude, MinimumAltitude,
           MaximumAltitude, NumberOfIndexEntries, NumberOfInputPoints, ExpirationAge,
           Version, Flags
    FROM WifiTileHeader
    ORDER BY AccessTimestamp, WifiTileHeader.rowid
    '''

    for record in get_sqlite_db_records(source_path, query):
        data_list.append((
            _timestamp(record['AccessTimestamp']),
            _timestamp(record['GenerationTimestamp']),
            record['SouthwestLatitude'],
            record['SouthwestLongitude'],
            record['DeltaLatitude'],
            record['DeltaLongitude'],
            record['TileX'],
            record['TileY'],
            record['Altitude'],
            record['MinimumAltitude'],
            record['MaximumAltitude'],
            record['NumberOfIndexEntries'],
            record['NumberOfInputPoints'],
            record['ExpirationAge'],
            record['Version'],
            record['Flags'],
        ))

    return data_headers, data_list, source_path
