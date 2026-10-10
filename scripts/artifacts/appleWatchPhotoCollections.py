""" Apple Watch photo sync: DeviceRegistry/<id>/NanoPhotos/collectionTargetMap """
__artifacts_v2__ = {
    "appleWatchPhotoCollections": {
        "name": "Apple Watch Photo Collections",
        "description": "One row per collection entry under each target type in the NanoPhotos "
                       "collectionTargetMap under DeviceRegistry, with the target type, "
                       "identifier and title.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-10",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "Apple Watch",
        "notes": "Each row is one collection listed under one target type in "
                 "collectionTargetMap. Target Type is the number the collection is filed under, "
                 "as stored; 1, 3, 4 and 6 were seen, and what they mean is not established. "
                 "Collection ID is the UUID the entry is keyed by, stored as 16 bytes and shown "
                 "as uppercase hyphenated text. Title, Subtitle and Subtype are the entry's "
                 "title, subtitle and subtype as stored. Asset ID Count and Key Asset ID Count "
                 "are the number of items in the entry's assetUUIDs and keyAssetUUIDs lists, "
                 "which Apple Watch Photo Collection Assets reports one per row with the file "
                 "path and thumbnail found for each; they have no value when the entry has no "
                 "such list. Other Keys lists any other key of the entry as key=value and had no "
                 "value on these rows. The 3 sample_data images that have the file gave 27 rows "
                 "(cookbook_ios1751 3, hickman_ios14 5, iphone11_ios17 19): 22 of type 4, 3 of "
                 "type 1, 1 of type 3 and 1 of type 6. Compared with Photos.sqlite on the same "
                 "image, the Collection ID of all 25 type 1 and type 4 rows was equal to a "
                 "ZGENERICALBUM.ZUUID and that of the type 3 row to a ZMEMORY.ZUUID; the type 6 "
                 "row matched neither table. This artifact does not open Photos.sqlite. On each "
                 "image the type 1 Collection ID was also listed under type 4. Title had a value "
                 "on 26 rows, all but the type 6 row; Subtitle on the type 3 row only; Subtype "
                 "on the 3 cookbook_ios1751 rows only. No value in the file is stored as a date "
                 "on the 3 images; the one Subtitle is text that names a year. Device Registry "
                 "ID is the name of the folder under DeviceRegistry that holds the file. That "
                 "this store belongs to a paired Apple Watch rests on issue #1876, which "
                 "describes DeviceRegistry as Apple Watch sync data; it is not sourced from "
                 "Apple documentation. The other 20 images have no "
                 "NanoPhotos/collectionTargetMap under mobile/Library/DeviceRegistry.",
        "paths": ('*/mobile/Library/DeviceRegistry/*/NanoPhotos/collectionTargetMap',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "photo",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 5 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 19 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 3 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
    "appleWatchPhotoCollectionAssets": {
        "name": "Apple Watch Photo Collection Assets",
        "description": "One row per asset identifier listed for a collection in the NanoPhotos "
                       "collectionTargetMap under DeviceRegistry, with the file path and "
                       "thumbnail Photos.sqlite and the Photos thumbnail folder hold for it.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-10",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "Apple Watch",
        "notes": "Each row is one item of a collection's assetUUIDs or keyAssetUUIDs list in "
                 "collectionTargetMap. List says which list, Position is the item's 1-based "
                 "place in it, and Asset ID is the item's UUID, stored as 16 bytes and shown as "
                 "uppercase hyphenated text. Target Type, Collection ID and Collection Title are "
                 "those of the collection the list belongs to; Collection Title has no value "
                 "when the collection has no title. File Path is the ZDIRECTORY and ZFILENAME of "
                 "the Photos.sqlite asset row whose ZUUID equals Asset ID, joined with a slash, "
                 "as stored; on iphone11_ios17 each path named a file under mobile/Media. "
                 "Thumbnail is the file in PhotoData/Thumbnails/V2 under that directory and file "
                 "name. The link from Asset ID to both is the recorded UUID; nothing is matched "
                 "by time or size. The original at File Path is not opened by this artifact and "
                 "its presence is not checked. Of the 3 sample_data images that have the map, "
                 "only iphone11_ios17 holds such lists: 16 assetUUIDs and 1 keyAssetUUIDs item "
                 "under the type 3 collection, and 2 assetUUIDs items under the type 6 "
                 "collection, 19 rows naming 17 distinct assets. All 19 rows had a File Path and "
                 "a Thumbnail: 17 rows show a .HEIC file under DCIM and 2 show a .JPG file under "
                 "PhotoData, and each asset had exactly one thumbnail file, named 5005.JPG. When "
                 "an asset has several thumbnail files the first by path is shown, when "
                 "Photos.sqlite is absent both columns are empty, and when the thumbnail file is "
                 "absent the Thumbnail column is empty; none of these cases occurred on these "
                 "images. The asset table read is ZASSET; ZGENERICASSET is read when ZASSET is "
                 "absent, which no image with asset lists exercised. What listing an asset here "
                 "records is not established. cookbook_ios1751 and hickman_ios14 hold the map "
                 "with no asset list and give 0 rows. Device Registry ID is the name of the "
                 "folder under DeviceRegistry that holds the map. That this store belongs to a "
                 "paired Apple Watch rests on issue #1876, which describes DeviceRegistry as "
                 "Apple Watch sync data; it is not sourced from Apple documentation. The other "
                 "20 images have no NanoPhotos/collectionTargetMap under "
                 "mobile/Library/DeviceRegistry; this artifact also matches Photos.sqlite and "
                 "the thumbnail folder, so it runs there and gives 0 rows.",
        "paths": ('*/mobile/Library/DeviceRegistry/*/NanoPhotos/collectionTargetMap',
                  '*/mobile/Media/PhotoData/Photos.sqlite*',
                  '*/mobile/Media/PhotoData/Thumbnails/V2/*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "photo",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 19 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
}

import os
import plistlib
import sqlite3
import uuid

from scripts.ilapfuncs import (artifact_processor, check_in_media, logfunc,
                               open_sqlite_db_readonly)

_ASSET_LISTS = ('assetUUIDs', 'keyAssetUUIDs')
# Keys of a collection that get a column of their own.
_COLLECTION_COLUMNS = ('title', 'subtitle', 'subtype')


def _value(objects, value):
    """ An archived value as a Python value: text, number, list, dictionary or UUID text. """
    if isinstance(value, plistlib.UID):
        value = objects[value.data]
    if not isinstance(value, dict):
        return None if value == '$null' else value
    if 'NS.uuidbytes' in value:
        return str(uuid.UUID(bytes=bytes(value['NS.uuidbytes']))).upper()
    items = [_value(objects, item) for item in value.get('NS.objects', [])]
    if 'NS.keys' in value:
        return list(zip((_value(objects, key) for key in value['NS.keys']), items))
    return items


def _collections(context):
    """ (paths, [(folder under DeviceRegistry, target type, collection id, {key: value})]). """
    paths = []
    out = []
    for file_found in sorted(str(path) for path in context.get_files_found()):
        segments = file_found.replace('\\', '/').split('/')
        # The folder is read by position from the file, so a DeviceRegistry segment in the
        # examiner's own output path cannot be taken for it.
        if segments[-1] != 'collectionTargetMap' or segments[-4:-1:2] != ['DeviceRegistry',
                                                                          'NanoPhotos']:
            continue
        paths.append(file_found)
        try:
            with open(file_found, 'rb') as file:
                plist = plistlib.load(file)
            objects = plist['$objects']
            targets = _value(objects, plist['$top']['root'])
            for target_type, collections in targets:
                for collection_id, fields in collections:
                    out.append((segments[-3], target_type, collection_id, dict(fields)))
        except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError,
                plistlib.InvalidFileException) as error:
            logfunc(f'{file_found} did not read as a collection target map: {error}')
    return '\n'.join(paths), out


def _text(value):
    return '' if value is None else str(value)


def _count(fields, key):
    return len(fields[key]) if isinstance(fields.get(key), list) else ''


@artifact_processor
def appleWatchPhotoCollections(context):
    """ See artifact description """
    data_headers = ('Target Type', 'Collection ID', 'Title', 'Subtitle', 'Subtype',
                    'Asset ID Count', 'Key Asset ID Count', 'Other Keys', 'Device Registry ID')
    source_path, collections = _collections(context)
    data_list = []
    for registry_id, target_type, collection_id, fields in collections:
        other = '; '.join(f'{key}={fields[key]}' for key in sorted(fields, key=str)
                          if key not in _COLLECTION_COLUMNS and key not in _ASSET_LISTS)
        data_list.append((_text(target_type), _text(collection_id))
                         + tuple(_text(fields.get(key)) for key in _COLLECTION_COLUMNS)
                         + (_count(fields, 'assetUUIDs'), _count(fields, 'keyAssetUUIDs'),
                            other, registry_id))
    return data_headers, data_list, source_path


_PHOTOS_DB = '/mobile/Media/PhotoData/Photos.sqlite'
_THUMBNAILS = '/mobile/Media/PhotoData/Thumbnails/V2/'


def _asset_files(files):
    """ (Photos.sqlite path, {asset UUID: (directory, file name)}). ('', {}) when absent. """
    database = next((path for path in files if path.replace('\\', '/').endswith(_PHOTOS_DB)), '')
    assets = {}
    db = open_sqlite_db_readonly(database) if database else None
    if db is None:
        return '', assets
    try:
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        # The asset table is ZASSET on the sample image; older stores name it ZGENERICASSET.
        table = next((name for name in ('ZASSET', 'ZGENERICASSET') if name in tables), None)
        if table is None:
            logfunc(f'{database} has no asset table')
            return database, assets
        for asset_id, directory, filename in db.execute(
                f'SELECT ZUUID, ZDIRECTORY, ZFILENAME FROM {table}'):
            if asset_id:
                assets[asset_id] = (directory, filename)
    except sqlite3.Error as error:
        logfunc(f'{database}: assets were not read: {error}')
    finally:
        db.close()
    return database, assets


def _thumbnails(files):
    """ {(directory, file name): [thumbnail paths]} from the evidence part of each path. """
    found = {}
    for path in files:
        normal = path.replace('\\', '/')
        start = normal.rfind(_THUMBNAILS)
        if start < 0 or not os.path.isfile(path):
            continue
        parts = normal[start + len(_THUMBNAILS):].split('/')
        if len(parts) >= 3:
            found.setdefault(('/'.join(parts[:-2]), parts[-2]), []).append(path)
    return found


@artifact_processor
def appleWatchPhotoCollectionAssets(context):
    """ See artifact description """
    data_headers = ('Target Type', 'Collection ID', 'Collection Title', 'List', 'Position',
                    'Asset ID', ('Thumbnail', 'media'), 'File Path', 'Device Registry ID')
    source_path, collections = _collections(context)
    data_list = []
    if not collections:
        return data_headers, data_list, source_path

    files = sorted(str(path) for path in context.get_files_found())
    database, assets = _asset_files(files)
    thumbnails = _thumbnails(files)
    if database:
        source_path = f'{source_path}\n{database}'
    for registry_id, target_type, collection_id, fields in collections:
        for list_name in _ASSET_LISTS:
            listed = fields.get(list_name)
            for position, asset in enumerate(listed if isinstance(listed, list) else [], start=1):
                directory, filename = assets.get(asset, (None, None))
                file_path = f'{directory}/{filename}' if directory and filename else ''
                candidates = sorted(thumbnails.get((directory, filename), []))
                thumbnail = check_in_media(candidates[0], f'{_text(asset)} thumbnail') \
                    if candidates else None
                data_list.append((_text(target_type), _text(collection_id),
                                  _text(fields.get('title')), list_name, position, _text(asset),
                                  thumbnail or '', file_path, registry_id))
    return data_headers, data_list, source_path
