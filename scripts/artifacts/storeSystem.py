__artifacts_v2__ = {
    'storeSystemAppInstalls': {
        'name': 'Installed Apps - App Store Install Records',
        'description': 'App Store install records from storeSystem.db, including the purchasing '
                       'Apple Account and the on-disk bundle path',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-29',
        'last_update_date': '2026-07-30',
        'requirements': 'none',
        'category': 'Installed Apps',
        'notes': ('Store metadata is an NSKeyedArchiver payload recorded at install time, so the '
                  'version, genre and purchase date describe the app as it was when installed. '
                  'The phase, update type, source type, one shot bootstrap and switch '
                  'distributor columns are integer codes whose values are not documented and '
                  'are reported as stored. Bundle directory name arrived with iOS 26 and was '
                  'empty on every row of the image tested, so what it holds is unknown.'),
        'paths': ('*/containers/Data/System/*/Documents/Persistence/storeSystem.db*',),
        'output_types': 'standard',
        'artifact_icon': 'device-mobile-down',
        'sample_data': {
            'magnet_ios16': 'iOS 16.1.1 | 16 rows; no install_finished_timestamp column, '
                            'store metadata carries no storefrontCountryCode',
            'iphone11_ios17': 'iOS 17.3 | 0 rows; table present and empty',
            'hc_ios18_7': '26 rows; install_finished_timestamp empty on every row',
            'hc_ios26': '12 rows; gains bundle_directory_name (empty on every '
                                      'row), one_shot_bootstrap, switch_distributor and '
                                      'optimal_download_duration, and drops download_volume',
        },
    },
    'storeSystemAppUpdates': {
        'name': 'Installed Apps - App Store Update Records',
        'description': 'Per-app update state from storeSystem.db, with the App Store catalog '
                       'metadata cached alongside it',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-29',
        'last_update_date': '2026-07-30',
        'requirements': 'none',
        'category': 'Installed Apps',
        'notes': ('The catalog metadata is a cached copy of the App Store listing, so the latest '
                  'version and release notes describe what the store offered at the time of the '
                  'last refresh, not necessarily what is installed. Update state and package '
                  'type are integer codes whose values are not documented.'),
        'paths': ('*/containers/Data/System/*/Documents/Persistence/storeSystem.db*',),
        'output_types': 'standard',
        'artifact_icon': 'refresh',
        'sample_data': {
            'magnet_ios16': 'iOS 16.1.1 | 0 rows; no package_type column on this schema',
            'iphone11_ios17': 'iOS 17.3 | 0 rows; table present and empty',
            'hc_ios18_7': '28 rows; install_date populated on 2 of 28',
            'hc_ios26': '15 rows; gains installer_packaging_type, populated on '
                                      '11 of 15',
        },
    },
    'storeSystemAppPackages': {
        'name': 'Installed Apps - App Store Download Packages',
        'description': 'Download packages recorded in storeSystem.db, with sizes and source '
                       'URLs, joined to the install record they belong to',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-29',
        'last_update_date': '2026-07-30',
        'requirements': 'none',
        'category': 'Installed Apps',
        'notes': ('One install can own several packages, such as the app itself plus its '
                  'on-demand resources, so bundle identifiers repeat across rows.'),
        'paths': ('*/containers/Data/System/*/Documents/Persistence/storeSystem.db*',),
        'output_types': 'standard',
        'artifact_icon': 'package',
        'sample_data': {
            'magnet_ios16': 'iOS 16.1.1 | 32 rows; no delta_algorithm or '
                            'extracted_content_size columns on this schema',
            'iphone11_ios17': 'iOS 17.3 | 0 rows; table present and empty',
            'hc_ios18_7': '49 rows across 26 installs',
            'hc_ios26': '24 rows; schema unchanged',
        },
    },
}

import json
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_sqlite_db_records, does_table_exist_in_db, \
    convert_cocoa_core_data_ts_to_utc, get_plist_content


def _iso_to_utc(value):
    """Convert an App Store ISO 8601 string to an aware datetime.

    The catalog and store metadata use several widths: '2026-06-10T17:01:48Z',
    '2026-06-10' and occasionally a bare date-time without a zone. Anything that
    does not parse is returned untouched so the value still reaches the report.
    """
    if not value:
        return ''
    try:
        parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except (ValueError, TypeError):
        return value
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _store_metadata(blob):
    """Deserialize the NSKeyedArchiver store_metadata blob into a dict."""
    if not blob:
        return {}
    parsed = get_plist_content(bytes(blob))
    return parsed if isinstance(parsed, dict) else {}


def _catalog_metadata(blob):
    """Decode the mapi_app_update metadata blob, which holds a catalog JSON entry."""
    if not blob:
        return {}
    try:
        parsed = json.loads(bytes(blob).decode('utf-8', 'replace'))
    except (ValueError, TypeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _existing_columns(source_path, table):
    """Return the column names a table actually has in this database.

    The schema moves between iOS versions: app_package gained delta_algorithm and
    extracted_content_size after iOS 17, app_install gained install_volume and
    others after iOS 14, and mapi_app_update gained package_type. Selecting a
    column that is not there fails the whole query and drops every row, so the
    column list is built from the file in hand.
    """
    return {record['name']
            for record in get_sqlite_db_records(source_path, f'PRAGMA table_info({table})')}


def _get(record, column, default=''):
    """Read a column that may not exist in this schema version.

    A NULL reads back the same as an absent column so that a value missing
    because of the schema and one missing because it was never set render
    identically in the report.
    """
    if column not in record.keys():
        return default
    value = record[column]
    return default if value is None else value


def _ios_attributes(catalog):
    """Return the iOS platform attributes of a catalog entry, if present."""
    attributes = catalog.get('attributes') or {}
    platforms = attributes.get('platformAttributes') or {}
    return attributes, (platforms.get('ios') or {})


@artifact_processor
def storeSystemAppInstalls(context):
    source_path = get_file_path(context.get_files_found(), 'storeSystem.db')
    data_list = []
    data_headers = (
        ('Record Timestamp', 'datetime'), ('Install Finished', 'datetime'),
        ('Last Start Date', 'datetime'), ('Purchase Date', 'datetime'),
        ('App Release Date', 'datetime'), 'App Name', 'Bundle ID', 'Short Version',
        'Bundle Version', 'Developer', 'Genre', 'Rating', 'Apple ID', 'Account DSID',
        'altDSID', 'Item ID', 'External Version ID', 'Storefront Country', 'Storefront',
        'Source App', 'Client ID', 'Install Path', 'Bundle Directory Name', 'Transaction ID',
        'Phase', 'Update Type', 'Source Type', 'Redownload', 'One Shot Bootstrap',
        'Switch Distributor', 'Optimal Download Duration')
    if not source_path or not does_table_exist_in_db(source_path, 'app_install'):
        return data_headers, data_list, ''

    # bundle_directory_name, one_shot_bootstrap, switch_distributor and
    # optimal_download_duration arrived with iOS 26; download_volume went away in
    # the same release. Selecting against the table covers both directions.
    wanted = ('timestamp', 'install_finished_timestamp', 'last_start_date', 'bundle_id',
              'bundle_name', 'bundle_version', 'bundle_url', 'bundle_directory_name',
              'vendor_name', 'item_id', 'storefront', 'client_id', 'transaction_id',
              'phase', 'update_type', 'source_type', 'redownload', 'one_shot_bootstrap',
              'switch_distributor', 'optimal_download_duration', 'account_id',
              'store_metadata')
    available = _existing_columns(source_path, 'app_install')
    columns = ', '.join(column for column in wanted if column in available)
    query = f'''
    SELECT {columns}
    FROM app_install
    ORDER BY timestamp
    '''

    for record in get_sqlite_db_records(source_path, query):
        metadata = _store_metadata(_get(record, 'store_metadata', b''))
        data_list.append((
            convert_cocoa_core_data_ts_to_utc(_get(record, 'timestamp')),
            convert_cocoa_core_data_ts_to_utc(_get(record, 'install_finished_timestamp')),
            convert_cocoa_core_data_ts_to_utc(_get(record, 'last_start_date')),
            _iso_to_utc(metadata.get('purchaseDate')),
            _iso_to_utc(metadata.get('releaseDate')),
            metadata.get('itemName') or _get(record, 'bundle_name'),
            _get(record, 'bundle_id'),
            metadata.get('bundleShortVersionString', ''),
            _get(record, 'bundle_version'),
            metadata.get('artistName') or _get(record, 'vendor_name'),
            metadata.get('genre', ''),
            metadata.get('ratingLabel', ''),
            metadata.get('appleID', ''),
            _get(record, 'account_id'),
            metadata.get('altDSID', ''),
            _get(record, 'item_id'),
            metadata.get('softwareVersionExternalIdentifier', ''),
            metadata.get('storefrontCountryCode', ''),
            _get(record, 'storefront'),
            metadata.get('sourceApp', ''),
            _get(record, 'client_id'),
            _get(record, 'bundle_url'),
            _get(record, 'bundle_directory_name'),
            _get(record, 'transaction_id'),
            _get(record, 'phase'),
            _get(record, 'update_type'),
            _get(record, 'source_type'),
            _get(record, 'redownload'),
            _get(record, 'one_shot_bootstrap'),
            _get(record, 'switch_distributor'),
            _get(record, 'optimal_download_duration'),
        ))

    return data_headers, data_list, source_path


@artifact_processor
def storeSystemAppUpdates(context):
    source_path = get_file_path(context.get_files_found(), 'storeSystem.db')
    data_list = []
    data_headers = (
        ('Record Timestamp', 'datetime'), ('Install Date', 'datetime'),
        ('Latest Version Released', 'datetime'), ('App First Released', 'datetime'),
        'App Name', 'Bundle ID', 'Developer', 'Genre', 'Latest Version', 'Release Notes',
        'Item ID', 'Store Software Version ID', 'External Version ID', 'Update State',
        'Package Type', 'Installer Packaging Type', 'App Store URL')
    if not source_path or not does_table_exist_in_db(source_path, 'mapi_app_update'):
        return data_headers, data_list, ''

    # installer_packaging_type arrived with iOS 26.
    wanted = ('timestamp', 'install_date', 'bundle_id', 'item_id',
              'store_software_version_id', 'update_state', 'package_type',
              'installer_packaging_type', 'metadata')
    available = _existing_columns(source_path, 'mapi_app_update')
    columns = ', '.join(column for column in wanted if column in available)
    query = f'''
    SELECT {columns}
    FROM mapi_app_update
    ORDER BY timestamp
    '''

    for record in get_sqlite_db_records(source_path, query):
        catalog = _catalog_metadata(_get(record, 'metadata', b''))
        attributes, ios = _ios_attributes(catalog)
        latest = ios.get('latestVersionInfo') or {}
        data_list.append((
            convert_cocoa_core_data_ts_to_utc(_get(record, 'timestamp')),
            convert_cocoa_core_data_ts_to_utc(_get(record, 'install_date')),
            _iso_to_utc(latest.get('releaseTimestamp')),
            _iso_to_utc(ios.get('releaseDate')),
            attributes.get('name', ''),
            _get(record, 'bundle_id'),
            attributes.get('artistName', ''),
            attributes.get('genreDisplayName', ''),
            latest.get('versionDisplay', ''),
            latest.get('releaseNotes', ''),
            _get(record, 'item_id'),
            _get(record, 'store_software_version_id'),
            ios.get('externalVersionId', ''),
            _get(record, 'update_state'),
            _get(record, 'package_type'),
            _get(record, 'installer_packaging_type'),
            attributes.get('url', ''),
        ))

    return data_headers, data_list, source_path


@artifact_processor
def storeSystemAppPackages(context):
    source_path = get_file_path(context.get_files_found(), 'storeSystem.db')
    data_list = []
    data_headers = (
        ('Timestamp', 'datetime'), 'Bundle ID', 'App Name', 'Package Type', 'Bytes Total',
        'Disk Usage', 'Extracted Content Size', 'Variant ID', 'Compression',
        'Delta Algorithm', 'Archive Type', 'Request Count', 'Package URL')
    if not source_path or not does_table_exist_in_db(source_path, 'app_package'):
        return data_headers, data_list, ''

    # parent_id carries the app_install.pid this package belongs to, despite the
    # column being declared UUID.
    wanted = ('timestamp', 'package_type', 'bytes_total', 'disk_usage',
              'extracted_content_size', 'variant_id', 'compression', 'delta_algorithm',
              'archive_type', 'request_count', 'package_url')
    available = _existing_columns(source_path, 'app_package')
    columns = ', '.join(f'app_package.{column}' for column in wanted if column in available)
    join = ''
    if does_table_exist_in_db(source_path, 'app_install'):
        columns += ', app_install.bundle_id, app_install.bundle_name'
        join = 'LEFT JOIN app_install ON app_install.pid = app_package.parent_id'
    query = f'''
    SELECT {columns}
    FROM app_package
    {join}
    ORDER BY app_package.timestamp
    '''

    for record in get_sqlite_db_records(source_path, query):
        data_list.append((
            convert_cocoa_core_data_ts_to_utc(_get(record, 'timestamp')),
            _get(record, 'bundle_id'),
            _get(record, 'bundle_name'),
            _get(record, 'package_type'),
            _get(record, 'bytes_total'),
            _get(record, 'disk_usage'),
            _get(record, 'extracted_content_size'),
            _get(record, 'variant_id'),
            _get(record, 'compression'),
            _get(record, 'delta_algorithm'),
            _get(record, 'archive_type'),
            _get(record, 'request_count'),
            _get(record, 'package_url'),
        ))

    return data_headers, data_list, source_path
