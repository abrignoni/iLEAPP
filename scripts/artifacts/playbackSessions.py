""" MediaPlaybackCore session archives (Documents/PlaybackSessions) """
__artifacts_v2__ = {
    "playbackSessions": {
        "name": "Playback Session Archives",
        "description": "One row per playback session archive that holds a "
                       "contentItem.protobuf.gz under an app's Documents/PlaybackSessions "
                       "folder, with the content item saved in it: "
                       "title, artist, album, duration, elapsed time and the time field 74 "
                       "holds.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-01",
        "last_update_date": "2026-11-01",
        "requirements": "none",
        "category": "Media Playback",
        "notes": (
            "Reads contentItem.protobuf.gz in each <id>.playbackSessionArchive folder. Field "
            "numbers and types come from pyatv's reverse-engineered MediaRemote protos, not "
            "from Apple: https://github.com/postlund/pyatv/blob/"
            "b277a4c8222ecdcbaab8a24e3e713ca44765adb4/pyatv/protocols/mrp/protobuf/"
            "ContentItemMetadata.proto (title 1, albumName 6, trackArtistName 7, "
            "albumArtistName 8, duration 14, elapsedTime 35, mediaSubType 65 and its enum, "
            "nowPlayingInfoData 67, collectionInfoData 73, elapsedTimeTimestamp 74, "
            "albumYear 88) and ContentItem.proto in the same folder (identifier 1, metadata "
            "2). pyatv reads field 74 as a Cocoa time and, while playing, adds the time since "
            "it to the elapsed time to get the current position (pyatv/protocols/mrp/"
            "__init__.py, lines 152 and 208 to 226 at the same commit), so it is read here as "
            "the time the "
            "elapsed time was taken. When the archive was written, and whether a session "
            "records a queued, playing or last played item, is not established. Queue Index, "
            "Queue Count, Collection Type and Collection Title are read from the "
            "NSKeyedArchiver dictionaries in fields 67 and 73 and shown as stored. App is the "
            "container's MCMMetadataIdentifier, or in an iTunes backup the container folder "
            "name, which iLEAPP's backup reader builds from the app's domain. Artwork is the "
            "archive's artwork file, present in the archives on the iOS 13 to 15 images and in "
            "none on the iOS 17, 18 and 26 images; the content items checked carry no artwork "
            "bytes of their own. Not reported: the archive's Info.plist, the "
            "metadata, behavior, dataSources and queueStructures .opackCoder.gz files (their "
            "format is not sourced), fields 68 and 72 (pyatv names them userInfoData and "
            "deviceSpecificUserInfoData, with no layout), and the other content item fields."
        ),
        "paths": ('*/Documents/PlaybackSessions/*.playbackSessionArchive/*',
                  '*/mobile/Containers/Data/Application/*/'
                  '.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": "standard",
        "artifact_icon": "music",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 20 rows (10 Music, 10 Podcasts)",
            "hc_ios18_7": "iOS 18.7.8 | 1 row (Podcasts)",
            "hc_ios26": "iOS 26.5.2 | 1 row (Podcasts)",
            "hickman_ios13": "iOS 13.3.1 | 3 rows (Music)",
            "hickman_ios14": "iOS 14.3 | 2 rows (Music)",
            "hickman_ios14_itunes_backup_decrypted": "iOS 14.3 backup | 2 rows (Music)",
            "hickman_ios15": "iOS 15.3.1 | 2 rows (Music)",
            "iphone11_ios17": "iOS 17.3 | 6 rows (Music)",
            "iphone12_ios18": "iOS 18.7 | 0 rows (no PlaybackSessions folder)",
            "magnet_ios16": "iOS 16.1.1 | 0 rows (no PlaybackSessions folder)",
            "otto_ios17": "iOS 17.5.1 | 6 rows (Music)",
        },
    },
}

import gzip
import os
import plistlib
import re
import struct
import zlib

import nska_deserialize
from google.protobuf.message import DecodeError

from scripts import blackboxprotobuf
from scripts.ilapfuncs import (artifact_processor, check_in_media,
                               convert_cocoa_core_data_ts_to_utc, logfunc)

_SESSIONS_DIR = '/Documents/PlaybackSessions/'
_METADATA_NAME = '.com.apple.mobile_container_manager.metadata.plist'
_UUID = re.compile(r'[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}')

# Field numbers and types of the content item message as given in pyatv's
# ContentItem.proto and ContentItemMetadata.proto (see notes). Only the fields reported
# are typed; blackboxprotobuf still decodes the rest by guessing and they are ignored.
_METADATA_TYPEDEF = {
    '1': {'type': 'str', 'name': ''},     # title
    '6': {'type': 'str', 'name': ''},     # albumName
    '7': {'type': 'str', 'name': ''},     # trackArtistName
    '8': {'type': 'str', 'name': ''},     # albumArtistName
    '14': {'type': 'double', 'name': ''},    # duration
    '35': {'type': 'double', 'name': ''},    # elapsedTime
    '65': {'type': 'int', 'name': ''},       # mediaSubType
    '67': {'type': 'bytes', 'name': ''},     # nowPlayingInfoData
    '73': {'type': 'bytes', 'name': ''},     # collectionInfoData
    '74': {'type': 'double', 'name': ''},    # elapsedTimeTimestamp
    '88': {'type': 'str', 'name': ''},    # albumYear
}
_CONTENT_ITEM_TYPEDEF = {
    '1': {'type': 'str', 'name': ''},     # identifier
    '2': {'type': 'message', 'message_typedef': _METADATA_TYPEDEF, 'name': ''},  # metadata
}
# ContentItemMetadata.MediaSubType in pyatv's ContentItemMetadata.proto.
_MEDIA_SUB_TYPES = {0: 'Unknown', 1: 'Music', 4: 'Podcast', 5: 'AudioBook', 6: 'ITunesU'}

_DECODE_ERRORS = (DecodeError, OSError, EOFError, zlib.error, struct.error, KeyError,
                  ValueError, TypeError, IndexError)
_NSKA_ERRORS = (nska_deserialize.DeserializeError, plistlib.InvalidFileException, ValueError,
                TypeError, KeyError, IndexError, AttributeError, EOFError, OverflowError,
                struct.error)

_NOW_PLAYING = 'kMRMediaRemoteNowPlayingInfo'
_COLLECTION = 'kMRMediaRemoteNowPlayingCollectionInfoKey'


def _text(value):
    return '' if value is None else str(value)


def _seconds(value):
    return '' if value is None else round(value, 3)


def _keyed_archive(data, label, source):
    """A dictionary from an embedded NSKeyedArchiver plist, or {} when it does not read."""
    if not data:
        return {}
    try:
        value = nska_deserialize.deserialize_plist_from_string(data)
    except _NSKA_ERRORS as ex:
        logfunc(f'{label} in {source} did not deserialize: {ex}')
        return {}
    return value if isinstance(value, dict) else {}


def _container_bundles(files_found):
    """Container folder -> MCMMetadataIdentifier, keyed on the container's full path."""
    bundles = {}
    for file_found in files_found:
        if os.path.basename(file_found) != _METADATA_NAME:
            continue
        try:
            with open(file_found, 'rb') as handle:
                metadata = plistlib.load(handle)
        except (plistlib.InvalidFileException, ValueError, OSError):
            continue
        if isinstance(metadata, dict) and metadata.get('MCMMetadataIdentifier'):
            bundles[os.path.dirname(file_found)] = str(metadata['MCMMetadataIdentifier'])
    return bundles


def _backup_bundle(container):
    """The container folder name when it is not a UUID.

    The iTunes backup seeker builds AppDomain-<bundle id> paths as
    Containers/Data/Application/<bundle id> (scripts/search_files.py), so a backup's
    container folder is named for the app; a full file system's is a UUID.
    """
    name = os.path.basename(container)
    return '' if _UUID.fullmatch(name) else name


@artifact_processor
def playbackSessions(context):
    """ See artifact description """
    data_headers = (('Elapsed Time Timestamp', 'datetime'), 'App', 'Title', 'Artist', 'Album',
                    'Album Artist', 'Album Year', 'Media Sub Type', 'Duration (s)',
                    'Elapsed Time (s)', 'Collection Type', 'Collection Title', 'Queue Index',
                    'Queue Count', ('Artwork', 'media'), 'Content Item Identifier',
                    'Session Archive')
    data_list = []
    files_found = [str(f) for f in context.get_files_found()]
    bundles = _container_bundles(files_found)

    archives = {}
    for file_found in files_found:
        if _SESSIONS_DIR not in file_found.replace('\\', '/'):
            continue
        archives.setdefault(os.path.dirname(file_found), set()).add(os.path.basename(file_found))

    source_paths = []
    for archive in sorted(archives):
        names = archives[archive]
        if 'contentItem.protobuf.gz' not in names:
            logfunc(f'{context.get_relative_path(archive)} holds no contentItem.protobuf.gz and was not reported')
            continue
        content_path = os.path.join(archive, 'contentItem.protobuf.gz')
        source_paths.append(content_path)
        try:
            with gzip.open(content_path, 'rb') as handle:
                content = handle.read()
            message, _ = blackboxprotobuf.decode_message(content, _CONTENT_ITEM_TYPEDEF)
        except _DECODE_ERRORS as ex:
            logfunc(f'{context.get_relative_path(content_path)} did not decode as a content item: {ex}')
            continue

        metadata = message.get('2') or {}
        if not isinstance(metadata, dict):
            metadata = {}
        timestamp = metadata.get('74')
        shown_path = context.get_relative_path(content_path)
        now_playing = _keyed_archive(metadata.get('67'), 'nowPlayingInfoData', shown_path)
        collection = _keyed_archive(metadata.get('73'), 'collectionInfoData', shown_path)
        sub_type = metadata.get('65')

        container = archive.replace('\\', '/').split(_SESSIONS_DIR)[0]
        container = os.path.normpath(container)

        artwork = ''
        if 'artwork' in names:
            artwork = check_in_media(os.path.join(archive, 'artwork'),
                                     _text(metadata.get('1')) or 'artwork') or ''

        data_list.append((
            convert_cocoa_core_data_ts_to_utc(timestamp) if timestamp else '',
            bundles.get(container) or _backup_bundle(container),
            _text(metadata.get('1')),
            _text(metadata.get('7')),
            _text(metadata.get('6')),
            _text(metadata.get('8')),
            _text(metadata.get('88')),
            '' if sub_type is None else f'{_MEDIA_SUB_TYPES.get(sub_type, "Unmapped")} ({sub_type})',
            _seconds(metadata.get('14')),
            _seconds(metadata.get('35')),
            _text(collection.get(f'{_COLLECTION}CollectionType')),
            _text(collection.get(f'{_COLLECTION}Title')),
            _text(now_playing.get(f'{_NOW_PLAYING}QueueIndex')),
            _text(now_playing.get(f'{_NOW_PLAYING}TotalQueueCount')),
            artwork,
            _text(message.get('1')),
            context.get_relative_path(archive),
        ))

    return data_headers, data_list, '\n'.join(source_paths)
