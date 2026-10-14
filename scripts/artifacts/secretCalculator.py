__artifacts_v2__ = {
    "secretCalculatorPhotoAlbum": {
        "name": "Secret Calculator Photo Album",
        "description": "Rows of the Photos table in the Secret Calculator Photo Album app's "
                       "data.sqlite (xyz.hypertornado.calculator)",
        "author": "John Hyla",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Secret Calculator Photo Album",
        "notes": (
            "Photo and album dates are read as Unix epoch seconds and shown in UTC. Path is the "
            "Photos row's path value as stored. Filename is the file found under the app "
            "container's Library/Data folder whose name is that path value, with or without an "
            "extension; it is blank when no such file is in the extraction, and File shows that "
            "file. Album and Album Date are filled only when the Photos table declares a foreign "
            "key to the Albums table, and then come from the Albums row that key names; otherwise "
            "they are blank, because no link from a photo to an album is recorded in the schema. "
            "Every image in sample_data returned 0 rows, so no row has been produced from a test "
            "image and none of these readings is confirmed; the foreign key and file lookups were "
            "exercised on a constructed database only."
        ),
        "paths": ('*mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "standard",
        "artifact_icon": "lock",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    }
}

import os
import pathlib
import plistlib
import re

from scripts.ilapfuncs import (artifact_processor, get_sqlite_db_records, check_in_media,
                               is_platform_windows, logfunc)

_BUNDLE_ID = 'xyz.hypertornado.calculator'
_QUERY = '''
    SELECT
        datetime(Photos.date, 'UNIXEPOCH'),
        NULL,
        Photos.path,
        Photos.video,
        NULL
    FROM Photos
'''
_QUERY_ALBUMS = '''
    SELECT
        datetime(Photos.date, 'UNIXEPOCH'),
        datetime(Albums.date, 'UNIXEPOCH'),
        Photos.path,
        Photos.video,
        Albums.name
    FROM Photos
    LEFT JOIN Albums ON Photos."{child}" = Albums."{parent}"
'''


def _photos_query(db_file):
    """Join Albums only through a foreign key the Photos table itself declares."""
    links = [fk for fk in get_sqlite_db_records(db_file, "PRAGMA foreign_key_list('Photos')")
             if str(fk['table']).lower() == 'albums']
    if len(links) != 1:
        return _QUERY
    child, parent = links[0]['from'], links[0]['to']
    if not parent:
        # A foreign key with no column named points at the parent's primary key.
        keys = [col['name'] for col in get_sqlite_db_records(db_file, "PRAGMA table_info('Albums')")
                if col['pk']]
        if len(keys) != 1:
            return _QUERY
        parent = keys[0]
    return _QUERY_ALBUMS.format(child=child.replace('"', '""'), parent=parent.replace('"', '""'))


def _stored_file(seeker, container, stored_path):
    """Find the file under Library/Data named by the stored path, with or without an extension."""
    if not stored_path:
        return None
    stored_path = str(stored_path)
    pattern = re.sub(r'([*?\[])', r'[\1]', f'{container}/Library/Data/{stored_path}')
    wanted = os.path.basename(stored_path.replace('\\', '/'))
    for hit in seeker.search(f'**{pattern}*'):
        hit = str(hit)
        name = os.path.basename(hit)
        if os.path.isfile(hit) and (name == wanted or os.path.splitext(name)[0] == wanted):
            return hit
    return None


@artifact_processor
def secretCalculatorPhotoAlbum(context):
    data_headers = (
        ('Date', 'datetime'), ('File', 'media', 'height: 96px;'), 'Album',
        ('Album Date', 'datetime'), 'Path', 'Filename', 'Is Video')
    data_list = []
    seeker = context.get_seeker()
    source = ''
    rows = []
    staged = []
    files_found = context.get_files_found()

    for file_found in list(files_found):
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

        for row in get_sqlite_db_records(str(db_file), _photos_query(str(db_file))):
            rows.append((row[0], row[4], row[1], row[2], row[3]))
            staged.append(_stored_file(seeker, container, row[2]))
        source = context.get_relative_path(file_found)

    # check_in_media resolves a file through the artifact's found files, so the files this
    # artifact staged itself are added before the first one is checked in.
    files_found.extend(media_file for media_file in staged if media_file)
    for (date, album, album_date, stored_path, is_video), media_file in zip(rows, staged):
        media_ref = check_in_media(media_file) if media_file else None
        filename = context.get_relative_path(media_file) if media_file else ''
        data_list.append((date, media_ref, album, album_date, stored_path, filename, is_video))

    return data_headers, data_list, source
