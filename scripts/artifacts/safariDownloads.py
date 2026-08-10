__artifacts_v2__ = {
    'safariDownloads': {
        'name': 'Safari - Downloads',
        'description': 'Files downloaded through Safari, from the browser download history plist',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-31',
        'requirements': 'none',
        'category': 'Safari Browser',
        'notes': ('Every Downloads.plist in the available test corpora has an empty DownloadHistory '
                  'array, so the columns are mapped from the expected DownloadEntry* key names; no '
                  'populated sample was available to verify them. Unrecognised keys are reported in Other Fields '
                  'rather than dropped.'),
        'paths': ('*/mobile/Containers/Data/Application/*/Library/Safari/Downloads/Downloads.plist',),
        'output_types': 'standard',
        'artifact_icon': 'download',
        'sample_data': {
            'josh_ios17_ffs': 'iOS 17.3 | plist present, DownloadHistory empty (0 rows)',
            'felix_ios17': 'iOS 17.6.1 | plist present, DownloadHistory empty (0 rows)',
            'felix23_ios16': 'iOS 16.5 | plist present, DownloadHistory empty (0 rows)',
        },
    },
}

from scripts.ilapfuncs import artifact_processor, logfunc, \
    get_file_path, get_plist_file_content, convert_plist_date_to_utc

# Keys Safari writes for each entry in the DownloadHistory array, mapped to the
# column they are reported in.
_ENTRY_KEYS = (
    ('DownloadEntryURL', 'URL'),
    ('DownloadEntryPath', 'Path'),
    ('DownloadEntryProgressBytesSoFar', 'Bytes So Far'),
    ('DownloadEntryProgressTotalToLoad', 'Total Bytes'),
    ('DownloadEntryIdentifier', 'Identifier'),
    ('DownloadEntrySandboxIdentifier', 'Sandbox Identifier'),
    ('DownloadEntryRemoveWhenDoneKey', 'Remove When Done'),
)

# Reported as a datetime rather than passed through verbatim.
_DATE_KEY = 'DownloadEntryDateAddedKey'

# Large opaque blobs that add nothing readable to the report.
_SKIP_KEYS = frozenset({
    'DownloadEntryBookmarkBlob',
    'DownloadEntryPostBookmarkBlob',
    _DATE_KEY,
} | {key for key, _ in _ENTRY_KEYS})


@artifact_processor
def safariDownloads(context):
    source_path = get_file_path(context.get_files_found(), 'Downloads.plist')
    data_list = []
    data_headers = (
        ('Date Added', 'datetime'), 'URL', 'Path', 'Bytes So Far', 'Total Bytes',
        'Identifier', 'Sandbox Identifier', 'Remove When Done', 'Other Fields')
    if not source_path:
        return data_headers, data_list, ''

    plist = get_plist_file_content(source_path) or {}
    history = plist.get('DownloadHistory')
    if not isinstance(history, list):
        logfunc('Safari Downloads.plist has no DownloadHistory array.')
        return data_headers, data_list, source_path

    for entry in history:
        if not isinstance(entry, dict):
            continue

        date_added = entry.get(_DATE_KEY)
        # Anything Safari added that this module does not know about is still
        # surfaced, so a schema change shows up instead of vanishing.
        other = ', '.join(f'{key}={entry[key]}' for key in sorted(entry)
                          if key not in _SKIP_KEYS)

        data_list.append((
            convert_plist_date_to_utc(date_added) if date_added else '',
            *[entry.get(key, '') for key, _ in _ENTRY_KEYS],
            other,
        ))

    return data_headers, data_list, source_path
