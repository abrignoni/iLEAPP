__artifacts_v2__ = {
    "photo_vault_ios_albums": {
        "name": "Private Photo Vault - Albums",
        "description": "Albums held in the Private Photo Vault app, with the title and settings "
                       "stored against each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Private Photo Vault",
        "notes": "One row per row of ZALBUM in Library/Application Support/PPVCoreData.sqlite. "
                 "Created and Last Modified are Core Data times, seconds since 2001, reported in "
                 "UTC, and read that way they fall in the period each image covers. Two of the 26 "
                 "registered iOS corpora carry the store, with 2 and 3 rows. On both, two rows "
                 "are titled Main Album and exactly one of that pair has Decoy Album set to Yes, "
                 "which is the album the app shows when the decoy entry is used; the third row on "
                 "the second image is a separate album with its own title. Password Stored says "
                 "only whether the row carries a stored password value, and it was Yes on one row "
                 "of five across both images. **The password bytes themselves are read by nothing "
                 "here.** Album Type, Cover Type and Sort Position are reported as stored. "
                 "Biometric Login Allowed read No on every row of both images, and Marked Deleted "
                 "read No on every row, so no album row on either image records one having been "
                 "removed.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/PPVCoreData.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "folder",
        "sample_data": {
                           "ctf2020_ios12": "iOS 12.4 | Private Photo Vault | 2 rows",
                           "hickman_ios14": "iOS 14.3 | Private Photo Vault | 3 rows",
                       },
    },
    "photo_vault_ios_media": {
        "name": "Private Photo Vault - Stored Media",
        "description": "Records of the pictures and videos the Private Photo Vault app holds, with "
                       "the album and the file names it stored them under.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Private Photo Vault",
        "notes": "One row per row of ZMEDIAITEM in Library/Application "
                 "Support/PPVCoreData.sqlite, joined to ZALBUM for the album title. Created, Last "
                 "Modified and Trashed are Core Data times, seconds since 2001, reported in UTC. "
                 "The row names the files the app stored under Library/PPV_Pics, a full size file "
                 "and a thumbnail, and a medium file for a live photo. Each name is looked for in "
                 "that folder inside the same app container, and all four rows across the two "
                 "images that carry the store resolved both their full size file and their "
                 "thumbnail, so the byte sizes reported are of the files themselves. **No picture "
                 "is shown, because the stored files are encrypted.** Every file staged from that "
                 "folder begins with the bytes 03 00 and none carries the signature of the format "
                 "its name claims, which agrees with the Encrypted column reading Yes on all four "
                 "rows. The app's own preferences were checked for key material and hold none, so "
                 "the files are reported by name, presence and size and are not decoded. Trashed "
                 "was empty on every row, so no row here records an item sent to the app's trash. "
                 "File Type held photo on three rows and livePhoto on one. Downloaded, Thumbnail "
                 "Downloaded, Uploaded and Marked Deleted are the app's own flags and are "
                 "reported as stored; Uploaded read No on one image and was empty on the other.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/PPVCoreData.sqlite*',
                  '*/Containers/Data/Application/*/Library/PPV_Pics/*'),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
                           "ctf2020_ios12": "iOS 12.4 | Private Photo Vault | 2 rows",
                           "hickman_ios14": "iOS 14.3 | Private Photo Vault | 2 rows",
                       },
    },
    "photo_vault_ios_break_in_attempts": {
        "name": "Private Photo Vault - Break In Attempts",
        "description": "Rows of the Private Photo Vault app's trespass table, with the login type, "
                       "coordinates and photo file each names.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Private Photo Vault",
        "notes": "One row per row of ZTRESSPASSRECORD in Library/Application "
                 "Support/PPVCoreData.sqlite. The table's columns are a date, a login type, a "
                 "device name, a latitude, a longitude and two file names, which is the shape of "
                 "the record the app keeps when an unlock is refused. **It was empty on both "
                 "images that carry the store, so this reader is code present and was not "
                 "exercised**, and its columns are the ones the table declares rather than ones "
                 "observed carrying values. Date is read as a Core Data time, seconds since 2001, "
                 "in UTC, with no row to confirm it. An empty table is not evidence that no "
                 "failed unlock ever happened, only that none is recorded here. Latitude and "
                 "Longitude are reported as stored and are what the KML output is built from when "
                 "rows exist. Login Type is reported as stored.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/PPVCoreData.sqlite*',),
        "output_types": "all",
        "artifact_icon": "alert-triangle",
        "sample_data": {
                           "ctf2020_ios12": "iOS 12.4 | Private Photo Vault | 0 rows",
                           "hickman_ios14": "iOS 14.3 | Private Photo Vault | 0 rows",
                       },
    },
}

import os
import re
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import (artifact_processor, does_table_exist_in_db,
                               get_sqlite_db_records, logfunc)

_CORE_DATA_EPOCH_UTC = datetime(2001, 1, 1, tzinfo=timezone.utc)
_CONTAINER = re.compile(r'(.*/Containers/Data/Application/[^/]+)/', re.I)


def _stores(files_found):
    '''Every PPVCoreData.sqlite among the matches, directories and sidecars skipped.'''
    seen = []
    for found in files_found:
        path = str(found)
        if os.path.isdir(path) or path.endswith(('-wal', '-shm')):
            continue
        if os.path.basename(path) == 'PPVCoreData.sqlite' and path not in seen:
            seen.append(path)
    return seen


def _container(path):
    '''The app data container a file sits in, or '' when it is not under one.'''
    match = _CONTAINER.match(str(path).replace('\\', '/'))
    return match.group(1) if match else ''


def _vault_files(files_found):
    '''{(container, file name): path} for every file staged from a vault picture folder.'''
    index = {}
    for found in files_found:
        path = str(found)
        if os.path.isdir(path):
            continue
        if '/PPV_Pics/' in path.replace('\\', '/'):
            index.setdefault((_container(path), os.path.basename(path)), path)
    return index


def _rows(path, table, columns):
    '''Rows of a table, or nothing when the store does not have it.'''
    if not does_table_exist_in_db(path, table):
        return []
    try:
        return list(get_sqlite_db_records(path, f'SELECT {columns} FROM {table}'))
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'Private Photo Vault: could not read {table}: {error}')
        return []


def _text(value):
    '''A stored value as text, with a stored null read as absent.'''
    return '' if value is None else str(value)


def _core_data_to_utc(value):
    '''Core Data seconds since 2001 to an aware UTC datetime, or ''.'''
    if value in (None, '', 0):
        return ''
    try:
        return _CORE_DATA_EPOCH_UTC + timedelta(seconds=float(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _flag(value):
    '''A stored boolean as Yes, No or blank, reported as the store holds it.'''
    if value in (None, ''):
        return ''
    return 'Yes' if str(value) not in ('0', '0.0', 'False') else 'No'


def _file_state(index, container, name):
    '''(present, size) for a named vault file, without reading its contents.'''
    if not name:
        return '', ''
    path = index.get((container, name))
    if not path:
        return 'No', ''
    try:
        return 'Yes', str(os.path.getsize(path))
    except OSError:
        return 'Yes', ''


@artifact_processor
def photo_vault_ios_albums(context):
    data_list = []
    sources = []
    for source_path in _stores(context.get_files_found()):
        sources.append(source_path)
        for (created, modified, title, album_type, cover_type, decoy, biometric,
             deleted, sort_position, udid, password) in _rows(
                source_path, 'ZALBUM',
                'ZCREATIONDATE, ZLASTMODIFICATIONDATE, ZTITLE, ZALBUMTYPE, ZCOVERTYPE, '
                'ZISDECOY, ZALLOWBIOMETRICLOGIN, ZDIDDELETE, ZSORTPOSITION, ZUDID, '
                'ZPASSWORDDATA'):
            data_list.append((
                _core_data_to_utc(created), _core_data_to_utc(modified), _text(title),
                _text(album_type), _text(cover_type), _flag(decoy), _flag(biometric),
                _flag(deleted), _text(sort_position),
                'Yes' if password else 'No', _text(udid),
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)
    data_headers = (
        ('Created', 'datetime'), ('Last Modified', 'datetime'), 'Title',
        'Album Type (as stored)', 'Cover Type (as stored)', 'Decoy Album',
        'Biometric Login Allowed', 'Marked Deleted', 'Sort Position (as stored)',
        'Password Stored', 'Album UDID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def photo_vault_ios_media(context):
    data_list = []
    sources = []
    files_found = context.get_files_found()
    on_disk = _vault_files(files_found)
    for source_path in _stores(files_found):
        sources.append(source_path)
        container = _container(source_path)
        albums = {}
        for (pk, title) in _rows(source_path, 'ZALBUM', 'Z_PK, ZTITLE'):
            albums[pk] = _text(title)
        for (created, modified, trashed, file_type, large, medium, thumb, album,
             encrypted, downloaded, thumb_downloaded, uploaded, deleted, udid) in _rows(
                source_path, 'ZMEDIAITEM',
                'ZCREATIONDATE, ZLASTMODIFICATIONDATE, ZTRASHEDDATE, ZFILETYPE, ZLARGEFILE, '
                'ZMEDIUMFILE, ZTHUMBFILE, ZALBUM, ZISENCRYPTED, ZISDOWNLOADED, '
                'ZISTHUMBDOWNLOADED, ZUPLOADED, ZDIDDELETE, ZUDID'):
            present, size = _file_state(on_disk, container, _text(large))
            thumb_present, thumb_size = _file_state(on_disk, container, _text(thumb))
            data_list.append((
                _core_data_to_utc(created), _core_data_to_utc(modified),
                _core_data_to_utc(trashed), albums.get(album, ''), _text(file_type),
                _text(large), present, size, _text(medium), _text(thumb), thumb_present,
                thumb_size, _flag(encrypted), _flag(downloaded), _flag(thumb_downloaded),
                _flag(uploaded), _flag(deleted), _text(udid),
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)
    data_headers = (
        ('Created', 'datetime'), ('Last Modified', 'datetime'), ('Trashed', 'datetime'),
        'Album', 'File Type (as stored)', 'Full Size File', 'Full Size File Present',
        'Full Size File Bytes', 'Medium File', 'Thumbnail File', 'Thumbnail Present',
        'Thumbnail Bytes', 'Encrypted', 'Downloaded', 'Thumbnail Downloaded', 'Uploaded',
        'Marked Deleted', 'Media UDID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def photo_vault_ios_break_in_attempts(context):
    data_list = []
    sources = []
    for source_path in _stores(context.get_files_found()):
        sources.append(source_path)
        for (date, login_type, device, latitude, longitude, photo, thumb,
             encrypted, sync_id, udid) in _rows(
                source_path, 'ZTRESSPASSRECORD',
                'ZDATE, ZLOGINTYPE, ZDEVICENAME, ZLATITUDE, ZLONGITUDE, ZFILENAME, '
                'ZTHUMBFILENAME, ZISENCRYPTED, ZSYNCID, ZUDID'):
            data_list.append((
                _core_data_to_utc(date), _text(login_type), _text(device),
                _text(latitude), _text(longitude), _text(photo), _text(thumb),
                _flag(encrypted), _text(sync_id), _text(udid),
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)
    data_headers = (
        ('Date', 'datetime'), 'Login Type (as stored)', 'Device Name', 'Latitude', 'Longitude',
        'Photo File', 'Thumbnail File', 'Encrypted', 'Sync ID', 'Record UDID',
    )
    return data_headers, data_list, '\n'.join(sources)
