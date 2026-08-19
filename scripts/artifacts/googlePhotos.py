__artifacts_v2__ = {
    "googlePhotosLibrary": {
        "name": "Google Photos - Library Items",
        "description": "Items in the Google Photos library store, with the file name, capture "
                       "and client creation timestamps, dimensions, coordinates and camera "
                       "fields recorded for each item.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Photos",
        "notes": "Rows come from ServerPhotos joined to ExtendedPhotos, whose mcMediaItem blob "
                 "is zlib compressed protobuf. File name, camera make and camera model are read "
                 "from that blob. In the tested samples every row carrying videoDurationMs had a "
                 "video file extension in the file name field and no still image row did, which "
                 "is how the field was identified. widthAndHeight packs two 16 bit values, "
                 "verified as (width << 16) | height against the same two values in the blob on "
                 "4103 of 4103 rows that carried both. latitudeLongitudeE7 packs two signed 32 "
                 "bit values, read as latitude in the high half and longitude in the low half; "
                 "both halves fall in range under either reading, so the order was taken from "
                 "the column name and corroborated against timeZoneOffsetHoursTimes4, which the "
                 "longitude agrees with on 263 of 263 and 1172 of 1176 located rows in the two "
                 "samples. Presence of a coordinate is not evidence of a person's location. "
                 "timestampMs and clientCreationTimestampMs are Unix milliseconds; no value in "
                 "either column fell on midnight, so they are read as instants rather than "
                 "dates. Device Asset ID comes from the LocalAssets table of photos-shared.db, "
                 "joined on localDedupKey, and is in the iOS local identifier form. flags, "
                 "storagePolicy, autoAwesomeType and contentVersion are reported as stored; the "
                 "app binary is not present in a data container, so no mapping was sourced. "
                 "Reference: Park, Park, Kim, Kang and Kim, 'A comprehensive artifact analysis "
                 "of Google applications on Android and iOS platforms', Forensic Science "
                 "International: Digital Investigation 55 (2025) 302029, which documents the "
                 "app's iOS cache paths but not this store.",
        "paths": ('*/Library/Application Support/store/photos-*.db*',),
        "output_types": ["html", "tsv", "lava", "timeline", "kml"],
        "artifact_icon": "image",
    },
    "googlePhotosAlbums": {
        "name": "Google Photos - Albums",
        "description": "Albums recorded in the Google Photos library store.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Photos",
        "notes": "Read from the Collections table, whose mcCollection blob is protobuf. The "
                 "title, item count, the earliest and latest item timestamps and the cover "
                 "image URL are taken from that blob. Timestamps are Unix milliseconds. Some "
                 "titles observed in the tested samples are calendar dates, which is consistent "
                 "with an album the app named rather than the account holder, but nothing in "
                 "the store distinguishes the two, so no such column is reported.",
        "paths": ('*/Library/Application Support/store/photos-*.db*',),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "folder",
    },
    "googlePhotosSharedAlbums": {
        "name": "Google Photos - Shared Albums",
        "description": "Shared albums, their recipients and the sync and activity timestamps "
                       "recorded for each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Photos",
        "notes": "Read from SharedCollections, with the recipient count taken from "
                 "SharedRecipients on envelopeMediaKey. The mcCollection blob here is zlib "
                 "compressed protobuf, unlike the uncompressed blob in the Collections table of "
                 "the same database. Timestamps are Unix milliseconds. The share link is the "
                 "album's own goo.gl address as recorded in that blob; it was present on all 11 "
                 "shared albums in the tested samples and on none of the 43 private ones. "
                 "pinState, isJoined, isLive and suggestedAddViewStatus are reported as stored, "
                 "and suggestedAddViewStatus was null on every shared album observed.",
        "paths": ('*/Library/Application Support/store/photos-*.db*',),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "share-2",
    },
    "googlePhotosSharedItems": {
        "name": "Google Photos - Shared Album Items",
        "description": "Items belonging to shared albums, with the album and contributing actor "
                       "keys recorded for each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Photos",
        "notes": "Read from SharedServerPhotos joined to SharedExtendedPhotos, whose "
                 "mcMediaItem blob is zlib compressed protobuf and supplies the file name. "
                 "actorMediaKey identifies the account credited with the item in the album; the "
                 "store records the key, not a name. Timestamps are Unix milliseconds. "
                 "widthAndHeight and latitudeLongitudeE7 are unpacked as in the library "
                 "artifact. allowedActions is reported as stored.",
        "paths": ('*/Library/Application Support/store/photos-*.db*',),
        "output_types": ["html", "tsv", "lava", "timeline", "kml"],
        "artifact_icon": "users",
    },
    "googlePhotosSearchCategories": {
        "name": "Google Photos - On-Device Search Clusters",
        "description": "Labelled clusters the app holds for on-device search over the library.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Photos",
        "notes": "Read from OnDeviceSearchClusters. A label is the text the cluster is "
                 "searchable by; the store does not record whether a given label was entered by "
                 "the account holder or produced by the app, so no such distinction is "
                 "reported. clusterType, visibleStatus and hiddenReason are reported as stored: "
                 "five distinct clusterType values were observed and no mapping was sourced, "
                 "since a data container carries no app binary to read case names from. "
                 "clusterIndexKey is the token that appears in the ServerPhotos clusterIndexKeys "
                 "column, which is how a cluster ties back to the items it covers.",
        "paths": ('*/Library/Application Support/store/photos-*.db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "tag",
    },
    "googlePhotosRecentSearches": {
        "name": "Google Photos - Recent Searches",
        "description": "Recent search entries held by the app's on-device search store.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Photos",
        "notes": "Read from the content table of the OnDeviceRecentSearchesFullTextSearch full "
                 "text index. The label is reported as stored. Each row also carries a "
                 "serialised search entry blob and a blob of local dedup keys, whose byte "
                 "lengths are reported so the presence of an associated result set is visible; "
                 "their contents are not decoded here. The store does not record who or what "
                 "originated an entry.",
        "paths": ('*/Library/Application Support/store/photos-*.db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "search",
    },
    "googlePhotosDownloadedMedia": {
        "name": "Google Photos - Downloaded Media Files",
        "description": "Video and audio files held in the app's per-extension fetch caches.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Photos",
        "notes": "Files under Library/Caches/com.google.photos/ImageFetcherCache_file_<ext>. "
                 "Each is a complete standalone file: the MP4 and MOV members read as ISO base "
                 "media with a moov atom and the M4A members as M4A, so they are checked in and "
                 "rendered. The cacheV0.index beside them is a 20 byte header followed by 32 "
                 "byte records of a 20 byte digest and three 32 bit values, the last of which "
                 "matched the member's byte length. The digest preimage was not recovered: "
                 "sha1, md5, sha256 and UTF-16 variants over the media key and over 2694 image "
                 "URLs read out of the library store's own protobufs produced no match against "
                 "13461 index digests across the two samples, so no link from these files to a "
                 "library row is reported. The file name is the cache's own sequence number and "
                 "does not carry the original name. This path is also listed in Park, Park, "
                 "Kim, Kang and Kim, 'A comprehensive artifact analysis of Google applications "
                 "on Android and iOS platforms', Forensic Science International: Digital "
                 "Investigation 55 (2025) 302029.",
        "paths": ('*/Library/Caches/com.google.photos/ImageFetcherCache_file_*/*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "film",
    },
    "googlePhotosCachedVideoStreams": {
        "name": "Google Photos - Cached Video Streams",
        "description": "Streamed video the app cached, keyed by the library item it belongs to.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Photos",
        "notes": "Under Library/Caches/Media/CacheV0/<account>/<media key>/ the directory name "
                 "is the item's media key: every one of the 9 directories in the first tested "
                 "sample matched a ServerPhotos mediaKey exactly, so the link is recorded "
                 "rather than correlated. Each holds one directory per stream, named "
                 "<stream id>_<value>, containing numbered segments, plus a cache_metadata "
                 "protobuf. The segments are fragmented streams rather than whole files: "
                 "concatenating them yields a separate audio and video track needing an "
                 "external muxer, and some caches are missing their first segment, so the "
                 "bytes are inventoried and located here rather than checked in as media. The "
                 "stream id is reported as stored. This path is not namespaced by bundle "
                 "id, unlike the app's other cache paths, so the Source File column should "
                 "be read to confirm which container a row came from. No other app was "
                 "observed using it in the tested samples.",
        "paths": ('*/Library/Caches/Media/CacheV0/*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "video",
    },
    "googlePhotosPreCheckpointRows": {
        "name": "Google Photos - Pre-Checkpoint Rows",
        "description": "Rows held in the committed part of the app's stores that the current "
                       "state of those stores no longer returns.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Photos",
        "notes": "Each store is read twice, once normally so the write-ahead log is applied and "
                 "once with the log ignored, and the two are compared row by row on the "
                 "primary key, or on the whole row where the table declares none. A row the "
                 "second read holds and the first does not is reported as absent from the "
                 "current read; a row both hold with differing content is reported as a prior "
                 "version, and the values shown are the committed ones. Comparing counts alone "
                 "would have missed most of these: in the tested samples counts flagged 2 "
                 "tables while the key comparison found rows in 8. This recovers only rows that "
                 "reached the main database file at a checkpoint and is not a substitute for "
                 "log frame parsing or freespace carving. Why a row is no longer returned is "
                 "not recorded: it may have been removed by the app, replaced by a later sync, "
                 "or rewritten, and this artifact reports the observation rather than a cause. "
                 "Full text index tables are skipped because they hold index structures rather "
                 "than records, and the external content index tables are skipped because they "
                 "duplicate the tables they index. Blob values are summarised by byte length "
                 "and by the container their leading bytes identify.",
        "paths": ('*/Library/Application Support/store/photos-*.db*',
                  '*/Library/Application Support/store/transaction-shared.db*'),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "rotate-ccw",
    },
    "googlePhotosAppState": {
        "name": "Google Photos - Application State",
        "description": "Application and operating system versions and backup state recorded in "
                       "the app's preferences.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Photos",
        "notes": "Read from Library/Preferences/com.google.photos.plist. Only keys whose "
                 "values are plain strings, numbers, booleans or dates are reported; the file "
                 "also holds serialised binary values that are not decoded here. Key names are "
                 "reported as they appear in the file and their meanings are not asserted.",
        "paths": ('*/Library/Preferences/com.google.photos.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
    },
}

import hashlib
import os
import sqlite3
import zlib
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    get_plist_file_content,
    get_sqlite_db_path,
    get_sqlite_db_records,
    logfunc,
    open_sqlite_db_readonly,
)

_UNIX_EPOCH_UTC = datetime(1970, 1, 1, tzinfo=timezone.utc)

# The library store is named after the account it belongs to, so the account database and the
# shared database sit side by side and are told apart by name rather than by pattern.
_SHARED_DB_NAMES = ('photos-shared.db', 'transaction-shared.db')


def _ms_to_utc(value):
    """A Unix millisecond value as a UTC datetime.

    Converted here rather than through the shared helper because the unit is known at this
    call site; inferring it from magnitude is only correct away from the epoch.
    """
    if not value:
        return ''
    try:
        return _UNIX_EPOCH_UTC + timedelta(milliseconds=int(value))
    except (ValueError, TypeError, OverflowError):
        return ''


def _sec_to_utc(value):
    """A Unix seconds value as a UTC datetime."""
    if not value:
        return ''
    try:
        return _UNIX_EPOCH_UTC + timedelta(seconds=int(value))
    except (ValueError, TypeError, OverflowError):
        return ''


def _unpack_dimensions(value):
    """The width and height packed into one integer as (width << 16) | height."""
    if value is None:
        return '', ''
    try:
        value = int(value)
    except (ValueError, TypeError):
        return '', ''
    return (value >> 16) & 0xFFFF, value & 0xFFFF


def _unpack_coordinates(value):
    """The latitude and longitude packed into one integer as two signed E7 halves.

    The high half is read as the latitude, which is the order the column names them and the
    order the stored timezone offset agrees with.
    """
    if not value:
        return '', ''
    try:
        value = int(value) & 0xFFFFFFFFFFFFFFFF
    except (ValueError, TypeError):
        return '', ''

    def signed(half):
        return half - (1 << 32) if half >= (1 << 31) else half

    latitude = signed((value >> 32) & 0xFFFFFFFF) / 1e7
    longitude = signed(value & 0xFFFFFFFF) / 1e7
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return '', ''
    return latitude, longitude


def _offset_to_str(quarter_hours):
    """A timezone offset stored in quarter hours, as a signed HH:MM string."""
    if quarter_hours is None:
        return ''
    try:
        minutes = int(quarter_hours) * 15
    except (ValueError, TypeError):
        return ''
    sign = '-' if minutes < 0 else '+'
    minutes = abs(minutes)
    return f'{sign}{minutes // 60:02d}:{minutes % 60:02d}'


def _read_varint(buffer, index):
    result = 0
    shift = 0
    while index < len(buffer):
        byte = buffer[index]
        index += 1
        result |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return result, index
        shift += 7
        if shift > 63:
            break
    raise ValueError('truncated varint')


def _pb_walk(buffer):
    """Every top level field of a protobuf message, as (number, wire type, value)."""
    index = 0
    length = len(buffer)
    while index < length:
        key, index = _read_varint(buffer, index)
        number, wire_type = key >> 3, key & 7
        if number == 0:
            raise ValueError('field number 0')
        if wire_type == 0:
            value, index = _read_varint(buffer, index)
            yield number, wire_type, value
        elif wire_type == 1:
            value = buffer[index:index + 8]
            index += 8
            yield number, wire_type, value
        elif wire_type == 5:
            value = buffer[index:index + 4]
            index += 4
            yield number, wire_type, value
        elif wire_type == 2:
            size, index = _read_varint(buffer, index)
            value = buffer[index:index + size]
            index += size
            yield number, wire_type, value
        else:
            raise ValueError(f'unsupported wire type {wire_type}')


def _pb_get(buffer, path):
    """The first value at a field number path, or None.

    Every element but the last is followed as a nested message; the last is returned raw.
    """
    if buffer is None:
        return None
    current = bytes(buffer)
    for wanted in path:
        found = None
        try:
            for number, _wire_type, value in _pb_walk(current):
                if number == wanted:
                    found = value
                    break
        except (ValueError, IndexError):
            return None
        if found is None:
            return None
        current = found
    return current


def _pb_text(buffer, path):
    """The value at a field number path decoded as text, or an empty string."""
    value = _pb_get(buffer, path)
    if not isinstance(value, (bytes, bytearray)):
        return ''
    try:
        return bytes(value).decode('utf-8')
    except UnicodeDecodeError:
        return ''


def _pb_int(buffer, path):
    """The value at a field number path when it is a varint, otherwise an empty string."""
    value = _pb_get(buffer, path)
    return value if isinstance(value, int) else ''


def _inflate(blob):
    """A zlib compressed blob, or the blob unchanged when it is not compressed."""
    if not blob:
        return b''
    blob = bytes(blob)
    try:
        return zlib.decompress(blob)
    except zlib.error:
        return blob


def _library_databases(files_found):
    """The per-account library databases, newest sidecars excluded."""
    databases = []
    for file_found in files_found:
        file_found = str(file_found)
        name = os.path.basename(file_found)
        if not name.startswith('photos-') or not name.endswith('.db'):
            continue
        if name in _SHARED_DB_NAMES:
            continue
        databases.append(file_found)
    return databases


def _shared_asset_index(library_db):
    """Device asset identifiers from photos-shared.db, keyed by local dedup key.

    The two databases sit in the same directory, so the shared one is located from the
    library one rather than from a second pattern.
    """
    shared_db = os.path.join(os.path.dirname(library_db), 'photos-shared.db')
    if not os.path.exists(shared_db):
        return {}
    index = {}
    query = '''
    SELECT localDedupKey, assetID, viewCount, shareCount, caption
    FROM LocalAssets
    WHERE localDedupKey IS NOT NULL
    '''
    for record in get_sqlite_db_records(shared_db, query):
        index[record[0]] = (record[1], record[2], record[3], record[4])
    return index


@artifact_processor
def googlePhotosLibrary(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        ('Client Creation Timestamp', 'datetime'),
        'Timezone Offset',
        'File Name',
        'Latitude',
        'Longitude',
        'Width',
        'Height',
        'Size (Bytes)',
        'Video Duration (ms)',
        'Camera Make',
        'Camera Model',
        'Device Asset ID',
        'View Count',
        'Media Key',
        'Local Dedup Key',
        'Album Media Key',
        'Storage Policy (as stored)',
        'Flags (as stored)',
        'Content Version (as stored)',
        'Source File',
    )
    data_list = []
    source_files = []

    query = '''
    SELECT
        S.timestampMs,
        S.clientCreationTimestampMs,
        S.timeZoneOffsetHoursTimes4,
        S.latitudeLongitudeE7,
        S.widthAndHeight,
        S.size,
        S.videoDurationMs,
        S.mediaKey,
        S.localDedupKey,
        S.collectionMediaKey,
        S.storagePolicy,
        S.flags,
        S.contentVersion,
        E.mcMediaItem
    FROM ServerPhotos AS S
    LEFT JOIN ExtendedPhotos AS E ON E.mediaKey = S.mediaKey
    ORDER BY S.timestampMs DESC
    '''

    for library_db in _library_databases(context.get_files_found()):
        assets = _shared_asset_index(library_db)
        rows = 0
        for record in get_sqlite_db_records(library_db, query):
            rows += 1
            item = _inflate(record[13])
            latitude, longitude = _unpack_coordinates(record[3])
            width, height = _unpack_dimensions(record[4])
            asset_id, view_count = '', ''
            if record[8] in assets:
                asset_id, view_count = assets[record[8]][0], assets[record[8]][1]
            data_list.append((
                _ms_to_utc(record[0]),
                _ms_to_utc(record[1]),
                _offset_to_str(record[2]),
                _pb_text(item, (2, 4)),
                latitude,
                longitude,
                width,
                height,
                record[5],
                record[6],
                _pb_text(item, (5, 2, 1, 9, 5, 1)),
                _pb_text(item, (5, 2, 1, 9, 5, 2)),
                asset_id,
                view_count,
                record[7],
                record[8],
                record[9],
                record[10],
                record[11],
                record[12],
                context.get_relative_path(library_db),
            ))
        if rows:
            source_files.append(library_db)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def googlePhotosAlbums(context):
    data_headers = (
        ('Earliest Item Timestamp', 'datetime'),
        ('Latest Item Timestamp', 'datetime'),
        ('Last Modified Timestamp', 'datetime'),
        'Title',
        'Item Count',
        'Album Media Key',
        'Owner Actor Key',
        'Cover Image URL',
        'Source File',
    )
    data_list = []
    source_files = []

    for library_db in _library_databases(context.get_files_found()):
        rows = 0
        for record in get_sqlite_db_records(
                library_db, 'SELECT mediaKey, mcCollection FROM Collections'):
            rows += 1
            album = _inflate(record[1])
            data_list.append((
                _ms_to_utc(_pb_int(album, (2, 10, 1))),
                _ms_to_utc(_pb_int(album, (2, 10, 2))),
                _ms_to_utc(_pb_int(album, (2, 10, 10))),
                _pb_text(album, (2, 5)),
                _pb_int(album, (2, 7)),
                record[0],
                _pb_text(album, (2, 3, 1)),
                _pb_text(album, (2, 15)),
                context.get_relative_path(library_db),
            ))
        if rows:
            source_files.append(library_db)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def googlePhotosSharedAlbums(context):
    data_headers = (
        ('Last Activity Timestamp', 'datetime'),
        ('Sort Timestamp', 'datetime'),
        ('Last View Timestamp', 'datetime'),
        'Title',
        'Recipients',
        'Share Link',
        'Album Media Key',
        'Owner Actor Key',
        'Cover Item Media Key',
        'Pin State (as stored)',
        'Is Joined (as stored)',
        'Is Live (as stored)',
        'Suggested Add View Status (as stored)',
        'Source File',
    )
    data_list = []
    source_files = []

    query = '''
    SELECT
        C.lastActivityTimeMs,
        C.sortTimeMs,
        C.lastViewTimeMs,
        C.envelopeMediaKey,
        C.ownerMediaKey,
        C.coverItemMediaKey,
        C.pinState,
        C.isJoined,
        C.isLive,
        C.suggestedAddViewStatus,
        C.mcCollection,
        (SELECT COUNT(*) FROM SharedRecipients AS R
          WHERE R.envelopeMediaKey = C.envelopeMediaKey)
    FROM SharedCollections AS C
    ORDER BY C.lastActivityTimeMs DESC
    '''

    for library_db in _library_databases(context.get_files_found()):
        rows = 0
        for record in get_sqlite_db_records(library_db, query):
            rows += 1
            album = _inflate(record[10])
            data_list.append((
                _ms_to_utc(record[0]),
                _ms_to_utc(record[1]),
                _ms_to_utc(record[2]),
                _pb_text(album, (2, 5)),
                record[11],
                _pb_text(album, (2, 18, 1)),
                record[3],
                record[4],
                record[5],
                record[6],
                record[7],
                record[8],
                record[9],
                context.get_relative_path(library_db),
            ))
        if rows:
            source_files.append(library_db)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def googlePhotosSharedItems(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        ('Added To Album Timestamp', 'datetime'),
        'File Name',
        'Latitude',
        'Longitude',
        'Width',
        'Height',
        'Size (Bytes)',
        'Video Duration (ms)',
        'Album Media Key',
        'Contributor Actor Key',
        'Media Key',
        'Allowed Actions (as stored)',
        'Source File',
    )
    data_list = []
    source_files = []

    query = '''
    SELECT
        P.timestampMs,
        P.creationTimestampMs,
        P.latitudeLongitudeE7,
        P.widthAndHeight,
        P.size,
        P.videoDurationMs,
        P.envelopeMediaKey,
        P.actorMediaKey,
        P.mediaKey,
        P.allowedActions,
        E.mcMediaItem
    FROM SharedServerPhotos AS P
    LEFT JOIN SharedExtendedPhotos AS E ON E.mediaKey = P.mediaKey
    ORDER BY P.timestampMs DESC
    '''

    for library_db in _library_databases(context.get_files_found()):
        rows = 0
        for record in get_sqlite_db_records(library_db, query):
            rows += 1
            item = _inflate(record[10])
            latitude, longitude = _unpack_coordinates(record[2])
            width, height = _unpack_dimensions(record[3])
            data_list.append((
                _ms_to_utc(record[0]),
                _ms_to_utc(record[1]),
                _pb_text(item, (2, 4)),
                latitude,
                longitude,
                width,
                height,
                record[4],
                record[5],
                record[6],
                record[7],
                record[8],
                record[9],
                context.get_relative_path(library_db),
            ))
        if rows:
            source_files.append(library_db)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def googlePhotosSearchCategories(context):
    data_headers = (
        'Label',
        'Cluster Type (as stored)',
        'Ranking Score',
        'Visible Status (as stored)',
        'Hidden Reason (as stored)',
        'Cluster Index Key',
        'Cluster Media Key',
        'Source File',
    )
    data_list = []
    source_files = []

    query = '''
    SELECT label, clusterType, rankingScore, visibleStatus, hiddenReason,
           clusterIndexKey, clusterMediaKey
    FROM OnDeviceSearchClusters
    ORDER BY rankingScore DESC
    '''

    for library_db in _library_databases(context.get_files_found()):
        rows = 0
        for record in get_sqlite_db_records(library_db, query):
            rows += 1
            data_list.append(tuple(record) + (context.get_relative_path(library_db),))
        if rows:
            source_files.append(library_db)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def googlePhotosRecentSearches(context):
    data_headers = (
        'Label',
        'Ranking Score',
        'Search Entry Blob (Bytes)',
        'Local Dedup Keys Blob (Bytes)',
        'Source File',
    )
    data_list = []
    source_files = []

    query = '''
    SELECT c0label, c3rankingScore, LENGTH(c1searchEntryBlob), LENGTH(c2localDedupKeysBlob)
    FROM OnDeviceRecentSearchesFullTextSearch_content
    '''

    for library_db in _library_databases(context.get_files_found()):
        rows = 0
        for record in get_sqlite_db_records(library_db, query):
            rows += 1
            data_list.append(tuple(record) + (context.get_relative_path(library_db),))
        if rows:
            source_files.append(library_db)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def googlePhotosDownloadedMedia(context):
    data_headers = (
        ('Media', 'media'),
        'Cache File Name',
        'Cache',
        'Size (Bytes)',
        'Source File',
    )
    data_list = []
    source_files = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        name = os.path.basename(file_found)
        if name == 'cacheV0.index' or not os.path.isfile(file_found):
            continue
        cache = os.path.basename(os.path.dirname(file_found))
        if not cache.startswith('ImageFetcherCache_file_'):
            continue
        # The JSON and ttf members of these caches are application resources rather than
        # library content, so only the audio and video extensions are checked in.
        extension = cache.rsplit('_', 1)[-1]
        if extension.upper() not in ('MP4', 'MOV', 'M4A', 'MP3'):
            continue
        media_ref = check_in_media(file_found, name=f'{cache}/{name}')
        data_list.append((
            media_ref,
            name,
            cache,
            os.path.getsize(file_found),
            context.get_relative_path(file_found),
        ))
        source_files.append(file_found)

    return data_headers, data_list, '\n'.join(sorted(set(
        os.path.dirname(path) for path in source_files)))


@artifact_processor
def googlePhotosCachedVideoStreams(context):
    data_headers = (
        'Media Key',
        'Account ID',
        'Stream ID (as stored)',
        'Segments',
        'Cached Bytes',
        'First Segment Present',
        'Source File',
    )
    data_list = []
    source_files = []

    # The seeker returns the files under each cache directory, so the stream directories are
    # rebuilt from those paths rather than by walking the extraction.
    streams = {}
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not os.path.isfile(file_found):
            continue
        normalised = file_found.replace('\\', '/')
        if '/Library/Caches/Media/CacheV0/' not in normalised:
            continue
        parts = normalised.split('/Library/Caches/Media/CacheV0/', 1)[1].split('/')
        # <account>/<media key>/<stream>/<segment>, with cache_metadata sitting one level up.
        if len(parts) != 4:
            continue
        account, media_key, stream, segment = parts
        key = (account, media_key, stream, os.path.dirname(file_found))
        entry = streams.setdefault(key, {'segments': 0, 'bytes': 0, 'first': False})
        entry['segments'] += 1
        entry['bytes'] += os.path.getsize(file_found)
        if segment == '0':
            entry['first'] = True
        source_files.append(file_found)

    for (account, media_key, stream, stream_dir), entry in sorted(streams.items()):
        data_list.append((
            media_key,
            account,
            stream,
            entry['segments'],
            entry['bytes'],
            'Yes' if entry['first'] else 'No',
            context.get_relative_path(stream_dir),
        ))

    return data_headers, data_list, '\n'.join(sorted(set(
        os.path.dirname(os.path.dirname(path)) for path in source_files)))


@artifact_processor
def googlePhotosAppState(context):
    data_headers = ('Key', 'Value', 'Source File')
    data_list = []
    source_files = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.basename(file_found) != 'com.google.photos.plist':
            continue
        content = get_plist_file_content(file_found)
        if not isinstance(content, dict):
            continue
        for key, value in sorted(content.items()):
            if isinstance(value, (bytes, bytearray, dict, list)):
                continue
            if isinstance(value, datetime):
                value = value.replace(tzinfo=value.tzinfo or timezone.utc)
            data_list.append((key, str(value), context.get_relative_path(file_found)))
        source_files.append(file_found)

    return data_headers, data_list, '\n'.join(source_files)


# Tables holding full text index structures rather than records. The _content table is kept
# because it holds the indexed values themselves and is what the live artifact reads.
_INDEX_TABLE_SUFFIXES = ('_segdir', '_segments', '_stat', '_docsize')

# The column naming the row's own event time, for the tables whose column name states what it
# is. Tables absent from this map report no timestamp rather than a guessed one.
_TABLE_TIMESTAMP_MS = {
    'ServerPhotos': 'timestampMs',
    'SharedServerPhotos': 'timestampMs',
    'LocalAssets': 'localDedupKeyTimeMs',
    'Stories': 'renderStartTimeMS',
    'SharedStories': 'renderStartTimeMS',
    'LifeItems': 'timestamp',
    'SharedCollections': 'lastActivityTimeMs',
    'SharedReactions': 'creationTimeMs',
    'SharedRecipients': 'inviteTimeMs',
    'SharedSync': 'lastActivityTimestampMs',
}

# Blob columns this module decodes elsewhere, so a recovered row can carry its file name
# rather than only a byte count.
_NAMED_BLOB_COLUMNS = {
    ('ExtendedPhotos', 'mcMediaItem'),
    ('SharedExtendedPhotos', 'mcMediaItem'),
}


def _blob_kind(data):
    """The container a blob's leading bytes identify."""
    if data[:8] == b'bplist00':
        return 'bplist'
    # RFC 1950: low nibble 8 is deflate and the two header bytes are a multiple of 31.
    if len(data) >= 2 and data[0] & 0x0F == 8 and (data[0] * 256 + data[1]) % 31 == 0:
        return 'zlib'
    return 'blob'


def _decode(value):
    """A stored value as text, leaving bytes that are not text as bytes."""
    if isinstance(value, (bytes, bytearray)):
        try:
            return bytes(value).decode('utf-8')
        except UnicodeDecodeError:
            return bytes(value)
    return value


def _render_value(table, column, value):
    """One column of a recovered row, with blobs summarised rather than dumped."""
    if value is None:
        return f'{column}=NULL'
    if isinstance(value, (bytes, bytearray)):
        data = bytes(value)
        summary = f'{column}=<{_blob_kind(data)} {len(data)} bytes'
        if (table, column) in _NAMED_BLOB_COLUMNS:
            name = _pb_text(_inflate(data), (2, 4))
            if name:
                summary += f', file name {name}'
        return summary + '>'
    return f'{column}={value}'


def _open_committed(path):
    """The store as committed to its main file, with any write-ahead log ignored.

    sqlite3.connect is lazy, so the query is what raises when the file cannot be read that
    way and the guard has to wrap it rather than the open.
    """
    try:
        db = sqlite3.connect(f'file:{get_sqlite_db_path(path)}?immutable=1', uri=True)
        db.execute('SELECT count(*) FROM sqlite_master')
        return db
    except sqlite3.Error as error:
        logfunc(f'Could not read the committed state of {os.path.basename(path)}: {error}')
        return None


def _comparable_tables(db):
    """The tables worth comparing, excluding index structures and external content indexes."""
    names = []
    for name, sql in db.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
        name = _decode(name)
        sql = _decode(sql) or ''
        if name.endswith(_INDEX_TABLE_SUFFIXES):
            continue
        if 'USING fts' in sql or 'using fts' in sql:
            continue
        names.append(name)
    return sorted(names)


def _table_shape(db, table):
    """The table's column names and its primary key columns."""
    columns, primary_key = [], []
    for row in db.execute(f'PRAGMA table_info("{table}")'):
        name = _decode(row[1])
        columns.append(name)
        if row[5]:
            primary_key.append(name)
    return columns, primary_key


def _table_rows(db, table, columns, primary_key):
    """Every row keyed by identity, with the row itself and a hash of its contents.

    Identity is the primary key when the table declares one. When it does not, the row's own
    contents are its identity, so a changed row reads as one row gone and one row added
    rather than as a modification.
    """
    selection = ','.join(f'"{column}"' for column in columns)
    rows = {}
    for row in db.execute(f'SELECT {selection} FROM "{table}"'):
        digest = hashlib.sha256(repr(row).encode()).hexdigest()
        if primary_key:
            identity = tuple(_decode(row[columns.index(key)]) for key in primary_key)
        else:
            identity = ('', digest)
        rows[identity] = (digest, row)
    return rows


@artifact_processor
def googlePhotosPreCheckpointRows(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Table',
        'State',
        'Row Identity',
        'Values',
        'Source File',
    )
    data_list = []
    source_files = []

    stores = sorted({
        str(file_found) for file_found in context.get_files_found()
        if str(file_found).endswith('.db') and os.path.isfile(str(file_found))
    })

    for store in stores:
        committed = _open_committed(store)
        if committed is None:
            continue
        current = open_sqlite_db_readonly(store)
        if current is None:
            committed.close()
            continue
        current.text_factory = bytes
        committed.text_factory = bytes
        recovered = 0
        try:
            for table in _comparable_tables(current):
                columns, primary_key = _table_shape(current, table)
                if not columns:
                    continue
                try:
                    live = _table_rows(current, table, columns, primary_key)
                    # The table can be newer than the last checkpoint, in which case the
                    # committed file does not carry it at all.
                    held = _table_rows(committed, table, columns, primary_key)
                except sqlite3.Error:
                    continue
                for identity, (digest, row) in held.items():
                    if identity in live and live[identity][0] == digest:
                        continue
                    state = ('Prior version of a current row' if identity in live
                             else 'Absent from current read')
                    values = ', '.join(
                        _render_value(table, column, row[index])
                        for index, column in enumerate(columns))
                    timestamp = ''
                    time_column = _TABLE_TIMESTAMP_MS.get(table)
                    if time_column in columns:
                        timestamp = _ms_to_utc(row[columns.index(time_column)])
                    label = '|'.join(str(part) for part in identity if part) or digest[:16]
                    data_list.append((
                        timestamp,
                        table,
                        state,
                        label,
                        values,
                        context.get_relative_path(store),
                    ))
                    recovered += 1
        finally:
            committed.close()
            current.close()
        if recovered:
            source_files.append(store)

    return data_headers, data_list, '\n'.join(source_files)
