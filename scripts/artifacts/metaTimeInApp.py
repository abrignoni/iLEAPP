__artifacts_v2__ = {
    "metaTimeInApp": {
        "name": "Meta Apps - Time In App",
        "description": "Rows from the intervals table of the time_in_app_<number>.db stores that "
                       "Instagram, Facebook and Threads keep in their data containers, with the start "
                       "and end times, the duration, the app and the stored event codes.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-30",
        "last_update_date": "2026-10-30",
        "requirements": "none",
        "category": "Social Media",
        "notes": "Reads the intervals table of each Documents/time_in_app_<number>.db, with its -wal, in "
                 "an app data container (on 26 of the 31 tested filesystem stores the table was present "
                 "only in the -wal), and names the app from the container's "
                 ".com.apple.mobile_container_manager.metadata.plist (MCMMetadataIdentifier) or, in an "
                 "iTunes backup, from the container folder's name. On the tested images the stores were "
                 "in com.burbn.instagram, com.facebook.Facebook and com.burbn.barcelona containers. "
                 "ALEAPP reads the same table in its Instagram, Facebook and Threads modules. Start Time "
                 "and End Time are start_walltime and end_walltime read as Unix seconds: on all 268 rows "
                 "of the 16 tested filesystem images the difference between them was within 2 seconds of "
                 "the difference between start_uptime and end_uptime, a second pair of columns that are "
                 "not reported. Duration (seconds) is End Time minus Start Time, and was 0 on 21 rows. "
                 "What an interval measures is taken from the database and table names and is not "
                 "sourced; this artifact does not interpret what activity occurred within it. Start Event "
                 "and End Event are start_event and end_event as stored; no source for their meaning was "
                 "found. On those rows the pairs were 1 and 2 (189 rows), 7 and 2 (66), 3 and 2 (9), and "
                 "four other pairs once each. The Account ID column holds the number in the database file "
                 "name. Reading it as an account ID rests on the other paths that number names in the "
                 "same container (such as a folder named by it under Documents/cask, and on Instagram its "
                 "direct messages store); no field in the extraction was found that states it. In all 31 "
                 "stores on those images the number named at least one other folder or file in that "
                 "container, and four containers held two stores with different numbers. On 16 of the 31 "
                 "stores the table's AUTOINCREMENT counter (sqlite_sequence) was higher than the row "
                 "count, so earlier rows had been removed, and the metadata table (key and value) held "
                 "last_eviction_timestamp and last_logging_timestamp on 30 of the 31 stores; they are not "
                 "reported. Rows are ordered by Start Time. In the iTunes backups "
                 "hickman_ios13_itunes_backup_decrypted and hickman_ios14_itunes_backup_decrypted the app "
                 "was named from the container folder's name, which iLEAPP's backup reader sets to the "
                 "bundle ID, and the rows numbered 10 and 16, the same counts as hickman_ios13 and "
                 "hickman_ios14.",
        "paths": ('*/Containers/Data/Application/*/Documents/time_in_app_*.db*',
                  '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 22 rows",
            "ctf2020_ios12": "iOS 12.4 | 25 rows",
            "dexter_ios18": "iOS 18.3.2 | 12 rows",
            "fsfull002_ios17": "iOS 17.1 | 19 rows",
            "hc_ios17_2": "iOS 17.2.1 | 11 rows",
            "hc_ios18_7": "iOS 18.7.8 | 33 rows",
            "hc_ios26": "iOS 26.5.2 | 7 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 33 rows",
            "hickman_ios13": "iOS 13.3.1 | 10 rows",
            "hickman_ios13_itunes_backup_decrypted": "iOS 13.3.1 | 10 rows",
            "hickman_ios14": "iOS 14.3 | 16 rows",
            "hickman_ios14_itunes_backup_decrypted": "iOS 14.3 | 16 rows",
            "hickman_ios15": "iOS 15.3.1 | 16 rows",
            "iphone11_ios17": "iOS 17.3 | 20 rows",
            "iphone12_ios18": "iOS 18.7 | 18 rows",
            "iphone14plus_ios18": "iOS 18.0 | 8 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 4 rows",
            "otto_ios17": "iOS 17.5.1 | 14 rows",
        },
    }
}

import posixpath
import re

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, does_table_exist_in_db, \
    get_plist_file_content, get_sqlite_db_records

_MCM_PLIST = '.com.apple.mobile_container_manager.metadata.plist'
_CONTAINER_RE = re.compile(r'^(.*?/containers/data/application/([^/]+))/', re.IGNORECASE)
_STORE_RE = re.compile(r'time_in_app_(\d+)\.db')
_UUID_RE = re.compile(r'[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}')


def _source(context, path):
    """Evidence-relative path of a staged file."""
    return context.get_relative_path(str(path)).replace('\\', '/').lstrip('/')


def _time(value):
    """Unix seconds as a UTC datetime; blank for no value."""
    if value is None or isinstance(value, bool) or not isinstance(value, (int, float)):
        return ''
    return convert_unix_ts_to_utc(value)


@artifact_processor
def metaTimeInApp(context):
    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), 'Duration (seconds)', 'App (bundle ID)',
        'Account ID (from file name)', 'Start Event (as stored)', 'End Event (as stored)', 'Sequence Number')
    bundles, stores = {}, []
    for path in sorted(str(p) for p in context.get_files_found()):
        source = _source(context, path)
        match = _CONTAINER_RE.match('/' + source)
        if not match:
            continue
        folder, name = match.group(1).lower(), posixpath.basename(source)
        if name == _MCM_PLIST:
            content = get_plist_file_content(path)
            if isinstance(content, dict) and isinstance(content.get('MCMMetadataIdentifier'), str):
                bundles[folder] = content['MCMMetadataIdentifier']
        elif _STORE_RE.fullmatch(name):
            # An iTunes backup names the container folder by the app's bundle ID.
            if not _UUID_RE.fullmatch(match.group(2)):
                bundles.setdefault(folder, match.group(2))
            stores.append((path, source, folder, _STORE_RE.fullmatch(name).group(1)))

    data_list, read = [], []
    for path, source, folder, account in stores:
        if not does_table_exist_in_db(path, 'intervals'):
            continue
        read.append(path)
        rows = get_sqlite_db_records(path, 'SELECT seq_num, start_walltime, start_event, end_walltime, end_event '
                                           'FROM intervals ORDER BY start_walltime, seq_num')
        for row in rows:
            start, end = row['start_walltime'], row['end_walltime']
            duration = end - start if isinstance(start, int) and isinstance(end, int) else ''
            data_list.append((
                _time(start), _time(end), duration, bundles.get(folder, ''), account,
                '' if row['start_event'] is None else row['start_event'],
                '' if row['end_event'] is None else row['end_event'], row['seq_num']))
    data_list.sort(key=lambda r: (str(r[0]), r[3], r[4], r[7]))
    return data_headers, data_list, '\n'.join(read)
