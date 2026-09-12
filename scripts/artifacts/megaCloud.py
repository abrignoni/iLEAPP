__artifacts_v2__ = {
    "mega_cloud_files": {
        "name": "MEGA - Cloud Files",
        "description": 'Files, folders and root nodes in the MEGA node cache, with the folder '
                       'path rebuilt from the stored parent links',
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "MEGA",
        "notes": 'Read from the nodes table of megaclient_statecache<version>_<account>.db, '
                 'the local node cache the MEGA SDK keeps for a signed in account. The nodes '
                 'table appears from cache version 13: the SDK\'s LAST_DB_VERSION_WITHOUT_NOD '
                 'is 12 '
                 '(https://github.com/meganz/sdk/blob/b93cc672b92eb61fefe84a21719657c13a9b11c0/src/db.cpp#L137), '
                 'and the version 12 store on fsfull002_ios17 holds only the statecache blob '
                 'table, whose rows DbTable::put writes through PaddedCBC::encrypt '
                 '(https://github.com/meganz/sdk/blob/b93cc672b92eb61fefe84a21719657c13a9b11c0/src/db.cpp#L68), '
                 'and it produces no rows here. Cache versions 13 and 14 were read across the '
                 'tested images. The name column is the value Node::displayname returns '
                 '(https://github.com/meganz/sdk/blob/b93cc672b92eb61fefe84a21719657c13a9b11c0/src/db/sqlite.cpp#L1619), '
                 'so it is the decrypted file or folder name rather than ciphertext. '
                 'displayname returns the literal CRYPTO_ERROR when a node carries no name '
                 'attribute '
                 '(https://github.com/meganz/sdk/blob/b93cc672b92eb61fefe84a21719657c13a9b11c0/src/node.cpp#L1013); '
                 'that was the case on 12 rows across the tested images, and all 12 of them '
                 'are the root, vault and rubbish nodes, which have no name attribute of '
                 'their own. Item Type is the SDK\'s nodetype_t '
                 '(https://github.com/meganz/sdk/blob/b93cc672b92eb61fefe84a21719657c13a9b11c0/include/mega/types.h#L421), '
                 'Share Type decodes the ShareType_t bits the SDK writes from getShareType '
                 '(https://github.com/meganz/sdk/blob/b93cc672b92eb61fefe84a21719657c13a9b11c0/include/mega/types.h#L434), '
                 'Label is nodelabel_t '
                 '(https://github.com/meganz/sdk/blob/b93cc672b92eb61fefe84a21719657c13a9b11c0/include/mega/types.h#L456), '
                 'and In Rubbish, Is Version and Marked Sensitive are the three bits of '
                 'Node::Flags '
                 '(https://github.com/meganz/sdk/blob/b93cc672b92eb61fefe84a21719657c13a9b11c0/include/mega/node.h#L474). '
                 'Values outside those vocabularies are reported as stored. Folder Path is '
                 'built by walking each node\'s parenthandle to the root. The root, vault and '
                 'rubbish nodes carry no name of their own, so a path starts at the first '
                 'named folder below them; 3 rows per image have no path on that basis, and '
                 'on every tested image those are exactly the rows whose Item Type is one of '
                 'those three. Created and Modified are the ctime and mtime columns, which '
                 'the SDK binds from the node\'s own ctime and mtime; the SDK documents both '
                 'as seconds since the epoch '
                 '(https://github.com/meganz/sdk/blob/b93cc672b92eb61fefe84a21719657c13a9b11c0/include/megaapi.h#L1333 '
                 'and '
                 'https://github.com/meganz/sdk/blob/b93cc672b92eb61fefe84a21719657c13a9b11c0/include/megaapi.h#L1342). '
                 'The stored schema differs between images that report the same cache version '
                 'in their file name, so every column is resolved per file and a column the '
                 'store lacks is reported blank. Measured on the tested images: Modified is '
                 'blank on every row of hickman_ios15, whose store has no mtime column; the '
                 'stores on hc_ios18_7 and hc_ios26 have no size column, so their Size is '
                 'taken from the counter blob instead, which NodeCounter::serialize writes as '
                 'files, folders, storage, versions and version storage '
                 '(https://github.com/meganz/sdk/blob/b93cc672b92eb61fefe84a21719657c13a9b11c0/src/node.cpp#L4018); '
                 'Label is filled on hc_ios18_7 and hc_ios26 and blank elsewhere; Description '
                 'and Tags were empty on every row of every tested image, including the '
                 'images whose store has those columns. Files in Folder, Folders in Folder '
                 'and Folder Size come from that same counter blob on folder rows. Measured '
                 'on every one of the 664 folder rows in the three stores read directly, '
                 'Files in Folder equals the number of files below the folder, Folder Size '
                 'equals the sum of their sizes, and Folders in Folder equals the number of '
                 'folders below it plus the folder itself, with 664 agreeing and 0 differing. '
                 'Share Type was LINK on 4 rows and NO_SHARES on the rest, Favourite was Yes '
                 'on 0 rows and none of the three flag columns was Yes on any row. The same '
                 'node cache is written to more than one container on a device, and the '
                 'copies can differ: on hc_ios18_7 the app\'s own container held 8 nodes the '
                 'shared group container did not, while on iphone11_ios17 all three copies '
                 'held the identical 1,301 nodes. Rows are therefore unioned on the node '
                 'handle within an account, so hc_ios18_7 reports 20 rows rather than the 44 '
                 'a per file reading would give, and every copy read is named on the located '
                 'at line. Cached Copy is the file MEGA kept on the device for that node, '
                 'matched on the handle in the cache file name; 62 of the 2627 rows reported '
                 'across the tested images carried one, and Cache Holding the Copy names '
                 'which cache it came from. Three columns hold one value per image and are '
                 'kept for that reason: Account Handle and Node Cache Version, because each '
                 'tested image held one account\'s cache at one version, and Share Value (as '
                 'stored), the integer behind Share Type. Cached Copy and Cache Holding the '
                 'Copy are blank on every row of an image whose MEGA container has no '
                 'thumbnailsV3, previewsV3 or originalV3 directory, which is the case on '
                 'hc_ios26.',
        "paths": ('*/megaclient_statecache*.db*',
                  '*/Library/Caches/thumbnailsV3/*',
                  '*/Library/Caches/previewsV3/*',
                  '*/Library/Caches/originalV3/*'),
        "output_types": "standard",
        "artifact_icon": "cloud",
        "sample_data": {
            'abe_ios16': 'iOS 16.5 | MEGA | 0 rows',
            'dexter_ios18': 'iOS 18.3.2 | MEGA | 0 rows',
            'fsfull002_ios17': 'iOS 17.1 | MEGA | 0 rows',
            'hc_ios18_7': 'iOS 18.7.8 | MEGA | 20 rows',
            'hc_ios26': 'iOS 26.5.2 | MEGA | 20 rows',
            'hickman_ios15': 'iOS 15.3.1 | MEGA | 1286 rows',
            'iphone11_ios17': 'iOS 17.3 | MEGA | 1301 rows',
        },
    },
    "mega_cached_media": {
        "name": "MEGA - Cached Media",
        "description": 'Thumbnails, previews and original files MEGA kept on the device, '
                       'keyed by the handle in the cache file name',
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "MEGA",
        "notes": 'One row per file staged from MEGA\'s thumbnailsV3, previewsV3 and originalV3 '
                 'caches. thumbnailsV3 and previewsV3 name the file after the handle; '
                 'originalV3 uses a folder named for the handle and keeps the file\'s own name '
                 'inside it. 118 rows across the tested images: thumbnailsV3 71, previewsV3 '
                 '32, originalV3 15. 94 resolved to a node in the same extraction\'s node '
                 'cache and 24 did not, so the cache holds files the node listing alone does '
                 'not account for. Where an originalV3 file could be compared, the name on '
                 'disk equalled the name in the node cache on 10 of 10 and differed on 0. The '
                 'thumbnailsV3 cache also holds contact avatars, which are named after the 11 '
                 'character user handle rather than the 8 character node handle; 7 such rows '
                 'are reported by the App Users artifact and every one of them appears here '
                 'with the node cache lookup answering No. Size on Disk is the size of the '
                 'staged file, not a size the store recorded.',
        "paths": ('*/megaclient_statecache*.db*',
                  '*/Library/Caches/thumbnailsV3/*',
                  '*/Library/Caches/previewsV3/*',
                  '*/Library/Caches/originalV3/*'),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
            'abe_ios16': 'iOS 16.5 | MEGA | 0 rows',
            'dexter_ios18': 'iOS 18.3.2 | MEGA | 0 rows',
            'fsfull002_ios17': 'iOS 17.1 | MEGA | 0 rows',
            'hc_ios18_7': 'iOS 18.7.8 | MEGA | 37 rows',
            'hc_ios26': 'iOS 26.5.2 | MEGA | 0 rows',
            'hickman_ios15': 'iOS 15.3.1 | MEGA | 50 rows',
            'iphone11_ios17': 'iOS 17.3 | MEGA | 31 rows',
        },
    },
    "mega_recent_items": {
        "name": "MEGA - Recent and Favourite Items",
        "description": 'Entries in the MEGA widget lists of recently used and favourite cloud '
                       'items',
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "MEGA",
        "notes": 'Read from the ZQUICKACCESSWIDGETRECENTITEM and '
                 'ZQUICKACCESSWIDGETFAVOURITEITEM tables of the app\'s own Core Data file, '
                 'MEGACD.sqlite. The List column says which table a row came from. 20 rows '
                 'across the tested images, all of them from the Recents table; the '
                 'Favourites table was present and empty on every tested image, so 0 rows '
                 'came from it. Timestamp is ZTIMESTAMP read as Cocoa Core Data time. It does '
                 'not date the individual item: on each of the 4 images that produced rows, '
                 'every row carried the same value, including the two images that produced '
                 'eight rows each. On those two the single value is later than the newest '
                 'date any row\'s own name carries, so what the value records is not '
                 'established and it must not be read as when that item was used. Is Update '
                 'is reported as stored; its meaning is not established. Cached Copy is the '
                 'file MEGA kept for that node handle, matched on the handle; 12 of the 20 '
                 'rows carried one, and Cache Holding the Copy names which cache it came '
                 'from. Both are blank on every row of an image whose MEGA container has no '
                 'such cache, which is the case on hc_ios26.',
        "paths": ('*/MEGACD.sqlite*',
                  '*/Library/Caches/thumbnailsV3/*',
                  '*/Library/Caches/previewsV3/*',
                  '*/Library/Caches/originalV3/*'),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            'abe_ios16': 'iOS 16.5 | MEGA | 0 rows',
            'dexter_ios18': 'iOS 18.3.2 | MEGA | 0 rows',
            'fsfull002_ios17': 'iOS 17.1 | MEGA | 0 rows',
            'hc_ios18_7': 'iOS 18.7.8 | MEGA | 8 rows',
            'hc_ios26': 'iOS 26.5.2 | MEGA | 8 rows',
            'hickman_ios15': 'iOS 15.3.1 | MEGA | 2 rows',
            'iphone11_ios17': 'iOS 17.3 | MEGA | 2 rows',
        },
    },
    "mega_offline_files": {
        "name": "MEGA - Offline Files",
        "description": 'Rows in the MEGA offline node table, each giving a node handle, a '
                       'stored path and a recorded download time',
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "MEGA",
        "notes": 'Read from the ZOFFLINENODE table of MEGACD.sqlite. The reported columns are '
                 'ZDOWNLOADEDDATE, ZLOCALPATH, ZBASE64HANDLE, ZPARENTBASE64HANDLE and '
                 'ZFINGERPRINT, reported under those readings of their names; no source for '
                 'the column meanings was found and the table held no rows to check them '
                 'against. The table was present and empty on every tested image, so this '
                 'artifact produced 0 rows and none of its columns has been exercised against '
                 'real data. Downloaded is ZDOWNLOADEDDATE read as Cocoa Core Data time, on '
                 'the same basis as the other MEGACD.sqlite dates; that reading is '
                 'unexercised here.',
        "paths": ('*/MEGACD.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "download",
        "sample_data": {
            'abe_ios16': 'iOS 16.5 | MEGA | 0 rows',
            'dexter_ios18': 'iOS 18.3.2 | MEGA | 0 rows',
            'fsfull002_ios17': 'iOS 17.1 | MEGA | 0 rows',
            'hc_ios18_7': 'iOS 18.7.8 | MEGA | 0 rows',
            'hc_ios26': 'iOS 26.5.2 | MEGA | 0 rows',
            'hickman_ios15': 'iOS 15.3.1 | MEGA | 0 rows',
            'iphone11_ios17': 'iOS 17.3 | MEGA | 0 rows',
        },
    },
    "mega_app_users": {
        "name": "MEGA - App Users",
        "description": 'Users held in the MEGA app\'s own Core Data file, with the email and '
                       'name it recorded for them',
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "MEGA",
        "notes": 'Read from the ZUSER table of MEGACD.sqlite, which is the app\'s own store '
                 'and separate from the contacts table in the karere chat database that the '
                 'MEGA - Contacts artifact reports. 12 rows across the tested images, with an '
                 'email on 11 of them and a nickname on 0. Interacted With is reported as '
                 'stored; its meaning is not established. Avatar is the file in MEGA\'s '
                 'thumbnailsV3 cache named after the user handle, which is 11 characters '
                 'where a node handle is 8; 7 of the 12 rows carried one. First Name and Last '
                 'Name hold one value across every row of fsfull002_ios17, which is what that '
                 'image stores rather than a column that failed to fill.',
        "paths": ('*/MEGACD.sqlite*',
                  '*/Library/Caches/thumbnailsV3/*'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            'abe_ios16': 'iOS 16.5 | MEGA | 0 rows',
            'dexter_ios18': 'iOS 18.3.2 | MEGA | 0 rows',
            'fsfull002_ios17': 'iOS 17.1 | MEGA | 3 rows',
            'hc_ios18_7': 'iOS 18.7.8 | MEGA | 2 rows',
            'hc_ios26': 'iOS 26.5.2 | MEGA | 2 rows',
            'hickman_ios15': 'iOS 15.3.1 | MEGA | 2 rows',
            'iphone11_ios17': 'iOS 17.3 | MEGA | 3 rows',
        },
    },
}

import base64
import os
import re
import struct

from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    convert_cocoa_core_data_ts_to_utc,
    convert_unix_ts_to_utc,
    does_column_exist_in_db,
    does_table_exist_in_db,
    get_sqlite_db_records,
    logfunc,
)

# Node types, from the SDK's nodetype_t.
# https://github.com/meganz/sdk/blob/master/include/mega/types.h
_NODE_TYPES = {-5: 'TYPE_NESTED_MOUNT', -4: 'TYPE_SYMLINK', -3: 'TYPE_DONOTSYNC',
               -2: 'TYPE_SPECIAL', -1: 'TYPE_UNKNOWN', 0: 'FILENODE', 1: 'FOLDERNODE',
               2: 'ROOTNODE', 3: 'VAULTNODE', 4: 'RUBBISHNODE'}

# Share bits, from ShareType_t in the same header. The column holds getShareType(), which
# sets IN_SHARES for a node shared in, OUT_SHARES for one shared with a named user,
# PENDING_OUTSHARES for an invitation not yet accepted and LINK for a public link.
_SHARE_BITS = ((0x01, 'IN_SHARES'), (0x02, 'OUT_SHARES'),
               (0x04, 'PENDING_OUTSHARES'), (0x08, 'LINK'))

# Colour labels, from the SDK's nodelabel_t in the same header.
_LABELS = {0: 'LBL_UNKNOWN', 1: 'LBL_RED', 2: 'LBL_ORANGE', 3: 'LBL_YELLOW',
           4: 'LBL_GREEN', 5: 'LBL_BLUE', 6: 'LBL_PURPLE', 7: 'LBL_GREY'}

# Bit positions of the node flags bitset, from Node::Flags in the SDK's node.h.
_FLAG_IS_VERSION = 0
_FLAG_IS_IN_RUBBISH = 1
_FLAG_IS_MARKED_SENSITIVE = 2

# The account's own user handle is the tail of the node cache file name.
_STATECACHE = re.compile(
    r'megaclient_statecache(\d+)_(?!status_|transfers_)([A-Za-z0-9_-]+)\.db$')
_CACHE_DIRS = ('thumbnailsV3', 'previewsV3', 'originalV3')


def _handle_to_base64(handle):
    """MEGA prints a node handle as the URL-safe base64 of its low six bytes, which is the
    form used for the media cache file names and for the handles the app stores elsewhere."""
    if handle is None:
        return ''
    return base64.urlsafe_b64encode(
        (int(handle) & ((1 << 48) - 1)).to_bytes(6, 'little')).decode().rstrip('=')


def _counter(blob):
    """NodeCounter::serialize writes files, folders, storage, versions and version storage.
    https://github.com/meganz/sdk/blob/master/src/node.cpp"""
    if not isinstance(blob, (bytes, bytearray)) or len(blob) != 28:
        return None
    files, folders, storage, versions, version_storage = struct.unpack('<IIqIq', blob)
    return {'files': files, 'folders': folders, 'storage': storage,
            'versions': versions, 'version_storage': version_storage}


def _share_type(value):
    if value is None:
        return ''
    value = int(value)
    names = [name for bit, name in _SHARE_BITS if value & bit]
    if names:
        return '|'.join(names)
    return 'NO_SHARES' if value == 0 else str(value)


def _flag(flags, bit):
    if flags is None:
        return ''
    return 'Yes' if int(flags) >> bit & 1 else 'No'


def _stored(value, names):
    if value is None:
        return ''
    name = names.get(value)
    return name if name else str(value)


def _sort_files(files_found):
    """Split the staged files into the node caches, the Core Data file and the media cache."""
    node_dbs, coredata, media = [], [], []
    for file_found in files_found:
        path = str(file_found)
        if os.path.isdir(path):
            continue
        normalised = path.replace('\\', '/')
        if _STATECACHE.search(normalised):
            node_dbs.append(path)
        elif normalised.endswith('MEGACD.sqlite'):
            coredata.append(path)
        elif any('/%s/' % name in normalised for name in _CACHE_DIRS):
            media.append(path)
    return node_dbs, coredata, media


def _media_entries(media_files):
    """List every staged cache file as (cache name, handle, path). An original is stored in a
    folder named for the handle and keeps its own file name, the other two caches name the
    file after the handle itself."""
    entries = []
    for path in media_files:
        parts = path.replace('\\', '/').split('/')
        for name in _CACHE_DIRS:
            if name not in parts:
                continue
            rest = parts[parts.index(name) + 1:]
            if not rest:
                continue
            if name == 'originalV3':
                if len(rest) < 2:
                    continue
            elif len(rest) != 1:
                continue
            entries.append((name, rest[0], path))
    return entries


def _media_index(media_files):
    """Map (cache name, handle) to one staged file. The match is on the handle alone because
    both path families this module reads are named by MEGA and by nothing else, and because
    the app keeps its caches in its group container while the node cache is also written to
    the app's own container."""
    index = {}
    for name, handle, path in _media_entries(media_files):
        index.setdefault((name, handle), path)
    return index


def _pick_media(index, handle):
    """Prefer the original the app kept, then the preview, then the thumbnail."""
    for name in ('originalV3', 'previewsV3', 'thumbnailsV3'):
        path = index.get((name, handle))
        if path:
            return path, name
    return '', ''


def _node_rows(path):
    """Read one node cache, resolving the columns that differ between releases."""
    if not does_table_exist_in_db(path, 'nodes'):
        return []
    present = {name: does_column_exist_in_db(path, 'nodes', name)
               for name in ('size', 'mtime', 'label', 'description', 'tags', 'share', 'fav',
                            'flags', 'counter', 'ctime', 'origFingerprint')}
    columns = ['nodehandle', 'parenthandle', 'name', 'type']
    columns += [name if present[name] else 'NULL AS %s' % name
                for name in ('size', 'ctime', 'mtime', 'share', 'fav', 'flags',
                             'label', 'description', 'tags', 'counter')]
    return list(get_sqlite_db_records(path, 'SELECT %s FROM nodes' % ', '.join(columns)))


def _paths_for(nodes):
    """Rebuild each node's folder path by walking its parent links. The three root nodes carry
    no name attribute of their own, so the path starts below them."""
    resolved = {}

    def walk(handle, seen):
        if handle in resolved:
            return resolved[handle]
        node = nodes.get(handle)
        if node is None or handle in seen:
            return None
        seen.add(handle)
        parent = (walk(node['parent'], seen) or '') if node['parent'] in nodes else ''
        if node['type'] in (2, 3, 4):
            value = ''
        elif parent:
            value = '%s/%s' % (parent, node['name'])
        else:
            value = node['name']
        resolved[handle] = value
        return value

    for handle in nodes:
        walk(handle, set())
    return resolved


@artifact_processor
def mega_cloud_files(context):
    node_dbs, _, media_files = _sort_files(context.get_files_found())
    index = _media_index(media_files)
    data_list = []
    sources = []
    seen = set()

    for path in sorted(node_dbs):
        match = _STATECACHE.search(path.replace('\\', '/'))
        version, account = match.group(1), match.group(2)
        rows = _node_rows(path)
        if not rows:
            continue
        sources.append(path)
        nodes = {}
        for row in rows:
            nodes[row[0]] = {'parent': row[1], 'name': row[2] or '', 'type': row[3]}
        folders = _paths_for(nodes)
        for row in rows:
            key = (account, row[0])
            if key in seen:
                continue
            seen.add(key)
            handle = _handle_to_base64(row[0])
            counter = _counter(row[13])
            size = row[4]
            if size is None and counter and row[3] == 0:
                size = counter['storage']
            media_path, cache = _pick_media(index, handle)
            media_ref = check_in_media(media_path, row[2] or handle) if media_path else ''
            data_list.append((
                convert_unix_ts_to_utc(row[5]) if row[5] else '',
                convert_unix_ts_to_utc(row[6]) if row[6] else '',
                folders.get(row[0], ''),
                row[2] or '',
                _stored(row[3], _NODE_TYPES),
                size,
                counter['files'] if counter and row[3] == 1 else '',
                counter['folders'] if counter and row[3] == 1 else '',
                counter['storage'] if counter and row[3] == 1 else '',
                _flag(row[9], _FLAG_IS_IN_RUBBISH),
                _flag(row[9], _FLAG_IS_VERSION),
                _flag(row[9], _FLAG_IS_MARKED_SENSITIVE),
                'Yes' if row[8] else 'No',
                _share_type(row[7]),
                _stored(row[10], _LABELS),
                row[11] or '',
                row[12] or '',
                row[7],
                handle,
                _handle_to_base64(row[1]) if row[1] not in (None, -1) else '',
                account,
                version,
                media_ref,
                cache,
                context.get_relative_path(path)))

    data_headers = (
        ('Created', 'datetime'), ('Modified', 'datetime'), 'Folder Path', 'Name', 'Item Type',
        'Size', 'Files in Folder', 'Folders in Folder', 'Folder Size', 'In Rubbish',
        'Is Version', 'Marked Sensitive', 'Favourite', 'Share Type', 'Label (as stored)',
        'Description', 'Tags', 'Share Value (as stored)', 'Node Handle', 'Parent Handle', 'Account Handle',
        'Node Cache Version', ('Cached Copy', 'media'), 'Cache Holding the Copy', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def mega_cached_media(context):
    node_dbs, _, media_files = _sort_files(context.get_files_found())
    names = {}
    sources = []

    for path in sorted(node_dbs):
        rows = _node_rows(path)
        if not rows:
            continue
        sources.append(path)
        for row in rows:
            names[_handle_to_base64(row[0])] = row[2] or ''

    data_list = []
    for cache, handle, path in sorted(_media_entries(media_files)):
        try:
            size = os.path.getsize(path)
        except OSError as error:
            logfunc('MEGA cached media could not be sized: %s' % type(error).__name__)
            size = ''
        on_disk = os.path.basename(path.replace('\\', '/')) if cache == 'originalV3' else ''
        in_cloud = names.get(handle, '')
        data_list.append((
            cache,
            handle,
            'Yes' if handle in names else 'No',
            in_cloud,
            on_disk,
            size,
            check_in_media(path, in_cloud or on_disk or handle),
            context.get_relative_path(path)))
        sources.append(os.path.dirname(path.replace('\\', '/')))

    data_headers = (
        'Cache', 'Handle', 'Handle in the Node Cache', 'Name in the Node Cache',
        'Name on Disk', 'Size on Disk', ('File', 'media'), 'Source File')
    return data_headers, data_list, '\n'.join(sorted(set(sources)))


@artifact_processor
def mega_recent_items(context):
    _, coredata, media_files = _sort_files(context.get_files_found())
    index = _media_index(media_files)
    data_list = []
    sources = []

    for path in sorted(coredata):
        for table, listing in (('ZQUICKACCESSWIDGETRECENTITEM', 'Recents'),
                               ('ZQUICKACCESSWIDGETFAVOURITEITEM', 'Favourites')):
            if not does_table_exist_in_db(path, table):
                continue
            update = does_column_exist_in_db(path, table, 'ZISUPDATE')
            query = 'SELECT ZTIMESTAMP, ZHANDLE, ZNAME, %s FROM %s' % (
                'ZISUPDATE' if update else 'NULL AS ZISUPDATE', table)
            rows = list(get_sqlite_db_records(path, query))
            if rows:
                sources.append(path)
            for row in rows:
                handle = row[1] or ''
                media_path, cache = _pick_media(index, handle)
                data_list.append((
                    convert_cocoa_core_data_ts_to_utc(row[0]) if row[0] else '',
                    listing,
                    row[2] or '',
                    handle,
                    row[3],
                    check_in_media(media_path, row[2] or handle) if media_path else '',
                    cache,
                    context.get_relative_path(path)))

    data_headers = (
        ('Timestamp', 'datetime'), 'List', 'Name', 'Node Handle', 'Is Update (as stored)',
        ('Cached Copy', 'media'), 'Cache Holding the Copy', 'Source File')
    return data_headers, data_list, '\n'.join(sorted(set(sources)))


@artifact_processor
def mega_offline_files(context):
    _, coredata, _ = _sort_files(context.get_files_found())
    data_list = []
    sources = []

    for path in sorted(coredata):
        if not does_table_exist_in_db(path, 'ZOFFLINENODE'):
            continue
        rows = list(get_sqlite_db_records(
            path,
            'SELECT ZDOWNLOADEDDATE, ZLOCALPATH, ZBASE64HANDLE, ZPARENTBASE64HANDLE, '
            'ZFINGERPRINT FROM ZOFFLINENODE'))
        if rows:
            sources.append(path)
        for row in rows:
            data_list.append((
                convert_cocoa_core_data_ts_to_utc(row[0]) if row[0] else '',
                row[1] or '',
                row[2] or '',
                row[3] or '',
                row[4] or '',
                context.get_relative_path(path)))

    data_headers = (
        ('Downloaded', 'datetime'), 'Stored Path', 'Node Handle', 'Parent Handle',
        'Fingerprint', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def mega_app_users(context):
    _, coredata, media_files = _sort_files(context.get_files_found())
    index = _media_index(media_files)
    data_list = []
    sources = []

    for path in sorted(coredata):
        if not does_table_exist_in_db(path, 'ZUSER'):
            continue
        columns = ['ZBASE64USERHANDLE', 'ZEMAIL', 'ZFIRSTNAME', 'ZLASTNAME']
        columns += [name if does_column_exist_in_db(path, 'ZUSER', name) else 'NULL AS %s' % name
                    for name in ('ZNICKNAME', 'ZINTERACTEDWITH')]
        rows = list(get_sqlite_db_records(path, 'SELECT %s FROM ZUSER' % ', '.join(columns)))
        if rows:
            sources.append(path)
        for row in rows:
            handle = row[0] or ''
            avatar = index.get(('thumbnailsV3', handle), '')
            data_list.append((
                row[1] or '',
                row[2] or '',
                row[3] or '',
                row[4] or '',
                handle,
                row[5],
                check_in_media(avatar, handle) if avatar else '',
                context.get_relative_path(path)))

    data_headers = (
        'Email', 'First Name', 'Last Name', 'Nickname', 'User Handle',
        'Interacted With (as stored)', ('Avatar', 'media'), 'Source File')
    return data_headers, data_list, '\n'.join(sources)
