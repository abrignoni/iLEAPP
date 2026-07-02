__artifacts_v2__ = {
    "secretCalculatorPhotoAlbum": {
        "name": "Secret Calculator Photo Album",
        "description": "Photos/videos hidden in the Secret Calculator Photo Album "
                       "(xyz.hypertornado.calculator) and their albums",
        "author": "John Hyla",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Secret Calculator Photo Album",
        "notes": "Photo/Album dates are Unix epoch seconds (UTC).",
        "paths": ('*mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "standard",
        "artifact_icon": "lock"
    }
}

import pathlib
import plistlib

from scripts.ilapfuncs import (artifact_processor, get_sqlite_db_records, check_in_media,
                               is_platform_windows, logfunc)

_BUNDLE_ID = 'xyz.hypertornado.calculator'
_QUERY = '''
    SELECT
        datetime(Photos.date, 'UNIXEPOCH'),
        datetime(Albums.date, 'UNIXEPOCH'),
        Photos.path,
        Photos.video,
        Albums.name
    FROM Photos
    LEFT JOIN Albums ON Photos.id = Albums.id
'''


@artifact_processor
def secretCalculatorPhotoAlbum(context):
    data_headers = (
        ('Date', 'datetime'), ('File', 'media', 'height: 96px;'), 'Album',
        ('Album Date', 'datetime'), 'Filename', 'Is Video')
    data_list = []
    seeker = context.get_seeker()
    source = ''

    for file_found in context.get_files_found():
        file_found = str(file_found)
        try:
            with open(file_found, 'rb') as fp:
                plist = plistlib.load(fp)
        except (plistlib.InvalidFileException, OSError, ValueError):
            continue
        if plist.get('MCMMetadataIdentifier') != _BUNDLE_ID:
            continue

        split_on = '\\private\\' if is_platform_windows() else '/private/'
        parts = str(pathlib.Path(file_found).parent).split(split_on, 1)
        if len(parts) < 2:
            continue
        container = parts[1].replace('\\', '/')

        db_file = seeker.search(f'**{container}/Library/data.sqlite', return_on_first_hit=True)
        if not db_file:
            logfunc(f'Secret Calculator: data.sqlite not found for {container}')
            continue

        for row in get_sqlite_db_records(str(db_file), _QUERY):
            filename = f'/private/{container}/Library/Data/{row[2]}.mov'
            media_ref = check_in_media(filename)
            data_list.append((row[0], media_ref, row[4], row[1], filename, row[3]))
        source = context.get_relative_path(file_found)

    return data_headers, data_list, source
