"""
Extracts and processes device synchronization information from the
    Biome Device Sync database.
"""

__artifacts_v2__ = {
    "biome_sync": {
        "name": "Biome - Device Syncs",
        "description": "Device records from the DevicePeer table of Biome's sync.db, with platform, OS build and last sync time where recorded",
        "author": "@JohnHyla",
        'creation_date': '2023-03-22',
        'last_update_date': '2026-09-26',
        "requirements": "none",
        "category": "Biome",
        "notes": (
            "Reads the DevicePeer table of Biome's sync.db, one row per device record. Local "
            "Device is Yes where the me column is 1. On the 19 registered iOS images carrying the "
            "database, Name held an empty string on all 38 rows, and Last Sync Timestamp was "
            "empty on the Local Device row of each image (last_sync_date is NULL there) and "
            "filled on every other row. Platform (as stored) is the integer in the platform "
            "column. Device Type is the name Apple's BMDevicePlatformToString returns for that "
            "integer: 0 Unknown, 1 iPad, 2 iPhone, 3 MacDesktop, 4 MacPortable, 5 TV, 6 Watch, 7 "
            "HomePod, 8 Vision, measured by calling the function in the BiomeSync framework on "
            "macOS 26.6.2 (build 25G83). Any other value leaves Device Type blank. On the same "
            "system BiomeFoundation's BMDevicePlatformFromModelString returned 7 for "
            "AudioAccessory model identifiers, 5 for AppleTV ones and 8 for RealityDevice ones. "
            "That DevicePeer stores this enumeration is inferred rather than sourced: BiomeSync's "
            "BMDevice class carries five of the table's fields (device identifier, IDS device "
            "identifier, name, model and platform), with model a string and platform an integer, "
            "and on the tested images the text builds on platform 2 rows resolved to iOS "
            "versions, on platform 1 to iPadOS, on 3 and 4 to macOS and on 6 to watchOS. The "
            "table declares model as STRING, which SQLite gives NUMERIC affinity (Reference: "
            "SQLite, 'Datatypes In SQLite', sections 3.1 and 3.1.1, "
            "https://www.sqlite.org/datatype3.html), so a build made of digits, the letter E and "
            "digits is stored as a number. OS Build reports model when it is stored as text. A "
            "numeric model is reported in Model Stored as Number, as the shortest decimal that "
            "reads back to the stored value, with OS Build and OS Version blank. The build is not "
            "rebuilt from the number, because the conversion loses information: inserted into a "
            "test table's STRING column, 20E247 is stored as 2.0e+248 and 23E5 as the integer "
            "2300000. On those images 3 of the 38 rows, on 3 images, held a number. OS Version is "
            "looked up from OS Build for iPhone, iPad, Mac, TV, Watch and Vision rows. It is left "
            "blank for HomePod rows: the lookup table has no HomePod group, and the builds on the "
            "3 tested HomePod rows are listed in it as tvOS builds, a name not applied to a "
            "HomePod. OS Build is the build this table holds for the device, not necessarily the "
            "build installed at acquisition: on the Local Device row it matched the build the iOS "
            "Information artifact reported for the image on 14 of the 19 tested images and "
            "differed on 5, one of them the numeric row."),
        "paths": ('*/Biome/sync/sync.db*'),
        "output_types": "standard",
        'artifact_icon': 'eye',
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 2 rows",
            "felix_ios17": "iOS 17.6.1 | 6 rows",
            "fsfull002_ios17": "iOS 17.1 | 1 row",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 5 rows",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
            "otto_ios17": "iOS 17.5.1 | 2 rows",
            "abe_ios16": "iOS 16.5 | 1 row",
            "felix23_ios16": "iOS 16.5 | 2 rows",
            "jess_ios15": "iOS 15.0.2 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 1 row",
            "adams_iphone12mini": "iOS 17.1.1 | 4 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 3 rows",
            "falken_ios26": "iOS 26.2.1 | 2 rows",
            "hc_ios26": "iOS 26.5.2 | 2 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 1 row",
            "hickman_ios15": "iOS 15.3.1 | 1 row",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 1 row",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, \
    get_sqlite_db_records, convert_unix_ts_to_utc


# Names returned by Apple's BMDevicePlatformToString for each value.
PLATFORM_NAMES = {
    0: 'Unknown',
    1: 'iPad',
    2: 'iPhone',
    3: 'MacDesktop',
    4: 'MacPortable',
    5: 'TV',
    6: 'Watch',
    7: 'HomePod',
    8: 'Vision',
}

# Device family passed to the build lookup. HomePod and unnamed values are
# left out, so no OS version is looked up for them.
BUILD_LOOKUP_FAMILY = {
    1: 'iPad',
    2: 'iPhone',
    3: 'Mac',
    4: 'Mac',
    5: 'AppleTV',
    6: 'Watch',
    8: 'RealityDevice',
}


@artifact_processor
def biome_sync(context):
    """
    Extracts and processes device synchronization information from the
    'sync.db' SQLite database.
    """

    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'sync.db')
    data_list = []

    query = '''
        SELECT
            last_sync_date,
            device_identifier,
            name,
            platform,
            model,
            typeof(model),
            CASE me
                WHEN 0 THEN ''
                WHEN 1 THEN 'Yes'
            END AS 'Local Device'
        FROM DevicePeer
    '''

    data_headers = (('Last Sync Timestamp', 'datetime'), 'Device ID', 'Name',
                    'Device Type', 'Platform (as stored)', 'OS Build',
                    'OS Version', 'Model Stored as Number', 'Local Device')

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        timestamp = convert_unix_ts_to_utc(record[0])
        platform = record[3]
        device_type = PLATFORM_NAMES.get(platform, '')
        os_build = ''
        os_version = ''
        model_number = ''
        if record[5] == 'text':
            os_build = record[4]
            family = BUILD_LOOKUP_FAMILY.get(platform)
            if family:
                os_version = context.get_apple_os_version(os_build, family)
        elif record[5] in ('real', 'integer'):
            # The column's NUMERIC affinity turned a build such as 22E240
            # into a number. The build is not rebuilt from it.
            model_number = repr(record[4])

        data_list.append((timestamp, record[1], record[2], device_type,
                          platform, os_build, os_version, model_number,
                          record[6]))

    return data_headers, data_list, source_path
