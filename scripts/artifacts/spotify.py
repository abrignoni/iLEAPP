__artifacts_v2__ = {
    "spotify_ios_recently_played": {
        "name": "Spotify - Recently Played",
        "description": "Tracks, playlists, albums and artists the Spotify app's own "
                       "store lists as recently played, with the times it records "
                       "against them.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-07",
        "last_update_date": "2026-09-07",
        "requirements": "none",
        "category": "Spotify",
        "notes": "One row per key in the recently played families of the LevelDB the "
                 "app keeps at Library/Application "
                 "Support/PersistentCache/Users/<account>-user/primary.ldb, read with "
                 "the LevelDB reader this repository already carries rather than by "
                 "scanning the bytes. The store rewrites an entry rather than editing "
                 "it, so one key can hold several records, and an older record can "
                 "carry an earlier time. Those earlier times are separate recordings "
                 "and are reported. Keeping only the newest record for each key would "
                 "have given 204 rows instead of 258, so 54 recorded times across 3 "
                 "images would have been dropped. Records that repeat a key, a time and "
                 "a state are counted once. Record State says whether the record the "
                 "row came from is a value or a deletion, and it reads Deleted on 1 of "
                 "258 rows, which is an entry the app had dropped from the list. Played "
                 "is the Unix time the record carries, reported in UTC, and is blank on "
                 "1 row, the deleted one. The app renames these families between "
                 "releases and the module reads all three it has been seen to use. On "
                 "the newest tested image, iOS 18.7, none of them is present and the "
                 "store instead holds an index of tracks against context identifiers "
                 "that carries no time at all, so that image reports nothing here. That "
                 "index is not read: what its records mean was not established, and "
                 "reporting them would be a guess. Item Type comes from the address "
                 "itself, so a row is a track, a playlist, an album or an artist as the "
                 "address says: 141 tracks, 27 artists, 75 playlists and 15 albums "
                 "across the tested images. Artist and Title are filled only where the "
                 "same container also cached the lyrics for that track, which is a link "
                 "the cache file name records rather than a match on anything else, and "
                 "that is 9 of 258 rows. The rest carry the address only, and the "
                 "address is what an examiner can look up. Account is the name of the "
                 "per-user folder the store sits in and holds one value across all 258 "
                 "rows because each tested image had one signed in account. The same "
                 "store holds a much larger cache of track, album and artist metadata "
                 "that the app downloaded, thousands of rows on one image, and none of "
                 "it is reported here because it says what a track is rather than that "
                 "anyone played it.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/PersistentCache/Users/*',
                  '*/Containers/Data/Application/*/Library/Caches/genius/*'),
        "output_types": "standard",
        "artifact_icon": "play-circle",
                         "sample_data": {
                                            "ctf2020_ios12": "iOS 12.4 | Spotify 8.5.49 | 0 rows",
                                            "hickman_ios13": "iOS 13.3.1 | Spotify 8.5.51 | 0 rows",
                                            "hickman_ios14": "iOS 14.3 | Spotify 8.5.94 | 107 rows",
                                            "hickman_ios15": "iOS 15.3.1 | Spotify 8.8.27 | 109 rows",
                                            "iphone11_ios17": "iOS 17.3 | Spotify 8.9.6 | 42 rows",
                                            "iphone12_ios18": "iOS 18.7 | Spotify 9.1.0 | 0 rows",
                                        },
    },
    "spotify_ios_saved_items": {
        "name": "Spotify - Saved and Offline Items",
        "description": "Entries the Spotify store holds for the account's saved "
                       "collection and for items that carried a marker to keep them on "
                       "the device.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-07",
        "last_update_date": "2026-09-07",
        "requirements": "none",
        "category": "Spotify",
        "notes": "One row per collection or offline key in the same LevelDB the "
                 "recently played entries come from, newest record per key. Kind "
                 "separates the two: 38 rows are collection entries and 90 are offline "
                 "markers. Record State matters here more than anywhere else. Every one "
                 "of the 90 offline markers is a deletion, so the marker is not "
                 "currently set on any of them. Whether that means a download was "
                 "removed or the app rewrote its index was not established, and the "
                 "honest reading is that these tracks carried an offline marker at some "
                 "point and do not now. All 38 collection entries are live. Saved is "
                 "the Unix time the collection record carries, reported in UTC, and is "
                 "blank on the 90 offline rows because those records hold no time. Item "
                 "Type comes from the address: 93 tracks, 31 artists, and 4 rows whose "
                 "address names the collection itself rather than an item, two of which "
                 "carry a type in the address and two of which do not, so Item Type is "
                 "blank on those two. Account is the name of the per-user folder the "
                 "store sits in and holds one value per image because each tested image "
                 "had one signed in account. The collection families the app uses "
                 "differ between releases and the module reads the plain ones rather "
                 "than the derived indexes beside them, so an item is counted once "
                 "rather than two or three times.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/PersistentCache/Users/*',),
        "output_types": "standard",
        "artifact_icon": "download",
                         "sample_data": {
                                            "ctf2020_ios12": "iOS 12.4 | Spotify 8.5.49 | 0 rows",
                                            "hickman_ios13": "iOS 13.3.1 | Spotify 8.5.51 | 0 rows",
                                            "hickman_ios14": "iOS 14.3 | Spotify 8.5.94 | 91 rows",
                                            "hickman_ios15": "iOS 15.3.1 | Spotify 8.8.27 | 17 rows",
                                            "iphone11_ios17": "iOS 17.3 | Spotify 8.9.6 | 17 rows",
                                            "iphone12_ios18": "iOS 18.7 | Spotify 9.1.0 | 3 rows",
                                        },
    },
    "spotify_ios_player_state": {
        "name": "Spotify - Player State",
        "description": "What the Spotify app was playing when it last wrote its saved "
                       "player state, with the position reached in the track.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-07",
        "last_update_date": "2026-09-07",
        "requirements": "none",
        "category": "Spotify",
        "notes": "One row per Library/Application "
                 "Support/PersistentCache/Users/<account>-user/context_player_state_restore, "
                 "which the app writes when it saves what it was playing. Every tested "
                 "image that carries the app has exactly one, so this is 6 rows across "
                 "6 images. State Saved is the millisecond time the file itself begins "
                 "with, and Playback Reported is the time inside the saved playback "
                 "block. They are close but not equal: across the 6 rows the playback "
                 "time follows the file's own stamp by up to 33 seconds. Both are "
                 "reported in UTC. The file changes format between releases. On the "
                 "three images running app version 8.5 it holds JSON and on the three "
                 "running 8.8 or later it holds a protobuf instead. Where in between "
                 "the change happened is not established. The protobuf is undocumented, "
                 "so the playing track is found by shape rather than by field numbers "
                 "written into this module: the first subtree that carries a Spotify "
                 "track address beside a block of three numbers whose first is a "
                 "millisecond time. The metadata inside names its own keys, so the "
                 "album, the artist address and the playlist come out under the names "
                 "the file uses. That format change is why some columns are thinner on "
                 "the newer images. Title is blank on 3 of 6 rows and Artist on 4, "
                 "because the newer form does not always carry them; Album, Album URI, "
                 "Artist URI, Track URI and Played From URI are filled on all 6. "
                 "Feature and Reached From are filled on 3 rows, the JSON ones. App "
                 "Version is the version string the file carries, and it is not the "
                 "same reading as the version the device has installed. On four of the "
                 "6 images the two agree to three parts and on two they do not: one "
                 "file says 8.5.47.887 against an installed 8.5.49, and another says "
                 "8.8.60.501 against an installed 8.9.6. The file records the version "
                 "that wrote it. Position and Duration are milliseconds as stored. "
                 "Playing and Paused are two separate flags and they are not opposites: "
                 "three rows read Yes to both, which is a paused track inside a playing "
                 "session. Shuffle, Repeat Context, Repeat Track and Explicit Content "
                 "Filtered each hold one value across all 6 rows, No, because no tested "
                 "image had any of them turned on. The same file also lists the tracks "
                 "of the playlist that was loaded, up to ninety of them on one image. "
                 "Those are the playlist's contents as the server sent them, not a "
                 "record of playing, and they are not reported.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/PersistentCache/Users/*',),
        "output_types": "standard",
        "artifact_icon": "music",
                         "sample_data": {
                                            "ctf2020_ios12": "iOS 12.4 | Spotify 8.5.49 | 1 row",
                                            "hickman_ios13": "iOS 13.3.1 | Spotify 8.5.51 | 1 row",
                                            "hickman_ios14": "iOS 14.3 | Spotify 8.5.94 | 1 row",
                                            "hickman_ios15": "iOS 15.3.1 | Spotify 8.8.27 | 1 row",
                                            "iphone11_ios17": "iOS 17.3 | Spotify 8.9.6 | 1 row",
                                            "iphone12_ios18": "iOS 18.7 | Spotify 9.1.0 | 1 row",
                                        },
    },
    "spotify_ios_play_history": {
        "name": "Spotify - Play History",
        "description": "The list of tracks the Spotify app's saved player state carries "
                       "as its own play history.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-07",
        "last_update_date": "2026-09-07",
        "requirements": "none",
        "category": "Spotify",
        "notes": "One row per entry of the play history list inside "
                 "context_player_state_restore, in the order the file lists them, which "
                 "Position In List reports. 15 rows across 3 images. The list carries "
                 "no time of its own, so State Saved repeats the time the file was "
                 "written and is the same value on every row from one file. It bounds "
                 "the entries rather than dating them: the list was written by then, "
                 "and how long before is not recorded. Only the JSON form of the file "
                 "carries this list. On the three images running app version 8.8 or "
                 "later the file is a protobuf holding one track, the one that was "
                 "playing, so those images report nothing here even though they carry "
                 "the file. Account is the name of the per-user folder the file sits in "
                 "and holds one value per image because each tested image had one "
                 "signed in account. Item Type comes from the address, and one row is "
                 "an advertisement rather than a track, which is what the app recorded "
                 "in the list. Artist and Title are filled where the same container "
                 "cached the lyrics for that track, which is 2 of 15 rows; the rest "
                 "carry the address only. Play ID is the identifier the app gave that "
                 "entry and is blank on 1 row, the advertisement.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/PersistentCache/Users/*',
                  '*/Containers/Data/Application/*/Library/Caches/genius/*'),
        "output_types": "standard",
        "artifact_icon": "list",
                         "sample_data": {
                                            "ctf2020_ios12": "iOS 12.4 | Spotify 8.5.49 | 1 row",
                                            "hickman_ios13": "iOS 13.3.1 | Spotify 8.5.51 | 4 rows",
                                            "hickman_ios14": "iOS 14.3 | Spotify 8.5.94 | 10 rows",
                                            "hickman_ios15": "iOS 15.3.1 | Spotify 8.8.27 | 0 rows",
                                            "iphone11_ios17": "iOS 17.3 | Spotify 8.9.6 | 0 rows",
                                            "iphone12_ios18": "iOS 18.7 | Spotify 9.1.0 | 0 rows",
                                        },
    },
    "spotify_ios_lyrics_cache": {
        "name": "Spotify - Lyrics Cache",
        "description": "Tracks the Spotify app cached lyrics for, with the artist, the "
                       "title and the time each was cached.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-07",
        "last_update_date": "2026-09-07",
        "requirements": "none",
        "category": "Spotify",
        "notes": "One row per file in Library/Caches/genius whose name is a track "
                 "identifier. Each is a binary property list holding the artist, the "
                 "title, the lyrics, the provider's own song identifier and the time "
                 "the app cached them. Everything but the lyrics is reported: the "
                 "lyrics are the provider's text and say nothing about the device. "
                 "Cached is a Core Data time, seconds since 2001, reported in UTC. The "
                 "file name is the track identifier, so each row names the track it "
                 "belongs to without any matching, and that is what lets the recently "
                 "played and play history tables show an artist and a title for the "
                 "tracks this cache covers. An entry means the app fetched the lyrics "
                 "for that track on this device and when. It is not established that a "
                 "person read them. One of the 6 tested images that carry the app has "
                 "this cache, with 9 entries spanning 2021-01-27 to 2021-02-13. The "
                 "folder is named for the lyrics provider rather than for Spotify, so "
                 "an entry is only used for a store in the same container.",
        "paths": ('*/Containers/Data/Application/*/Library/Caches/genius/*',),
        "output_types": "standard",
        "artifact_icon": "file-text",
                         "sample_data": {
                                            "ctf2020_ios12": "iOS 12.4 | Spotify 8.5.49 | 0 rows",
                                            "hickman_ios13": "iOS 13.3.1 | Spotify 8.5.51 | 0 rows",
                                            "hickman_ios14": "iOS 14.3 | Spotify 8.5.94 | 9 rows",
                                            "hickman_ios15": "iOS 15.3.1 | Spotify 8.8.27 | 0 rows",
                                            "iphone11_ios17": "iOS 17.3 | Spotify 8.9.6 | 0 rows",
                                            "iphone12_ios18": "iOS 18.7 | Spotify 9.1.0 | 0 rows",
                                        },
    },
    "spotify_ios_podcast_playback": {
        "name": "Spotify - Podcast Playback",
        "description": "Podcast episodes the Spotify app recorded a playback position "
                       "for, with the time each was last played.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-07",
        "last_update_date": "2026-09-07",
        "requirements": "none",
        "category": "Spotify",
        "notes": "One row per record in Library/Application "
                 "Support/PersistentCache/Users/<account>-user/played-state-storage, a "
                 "protobuf the app writes as it plays podcast episodes. Last Played is "
                 "the Unix time the record carries, reported in UTC. Position and "
                 "Duration are seconds as stored, and Played Through is the one divided "
                 "by the other, which is a calculation here and not a stored value. The "
                 "file is two bytes long and holds nothing on the three oldest tested "
                 "images, holds records on two of the newer ones, and is absent from "
                 "the newest, so it is worth opening on any image rather than being "
                 "judged by the older layout. Across those two images it holds the same "
                 "2 episodes with the same positions and the same times, one at 99.3% "
                 "of its length and one at 14.7%. Show URI is blank on 1 of 4 rows "
                 "because that record does not carry it. The record also holds three "
                 "flags this module does not report, because what they mean was not "
                 "established.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/PersistentCache/Users/*',),
        "output_types": "standard",
        "artifact_icon": "headphones",
                         "sample_data": {
                                            "ctf2020_ios12": "iOS 12.4 | Spotify 8.5.49 | 0 rows",
                                            "hickman_ios13": "iOS 13.3.1 | Spotify 8.5.51 | 0 rows",
                                            "hickman_ios14": "iOS 14.3 | Spotify 8.5.94 | 0 rows",
                                            "hickman_ios15": "iOS 15.3.1 | Spotify 8.8.27 | 2 rows",
                                            "iphone11_ios17": "iOS 17.3 | Spotify 8.9.6 | 2 rows",
                                            "iphone12_ios18": "iOS 18.7 | Spotify 9.1.0 | 0 rows",
                                        },
    },
    "spotify_ios_account": {
        "name": "Spotify - Account",
        "description": "The Spotify account the app is signed in to, from its settings "
                       "file and its cached profile record.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-07",
        "last_update_date": "2026-09-07",
        "requirements": "none",
        "category": "Spotify",
        "notes": "One row per settings file the app writes at Library/Application "
                 "Support/prefs. A file of that name is not on its own the app's, so "
                 "one is only read when it carries the key the app writes its signed in "
                 "account under. That guard is in the code and no tested image "
                 "exercised it: every file this path matched across the 26 tested "
                 "images belonged to Spotify. Username is that key's value. Display "
                 "Name, Profile Picture URL and Profile Picture URL (Large) come from a "
                 "cached profile record in mercury.db beside it, and only the images "
                 "that still carry that cache can fill them. Display Name is filled on "
                 "3 of 6 rows and the two picture addresses on 2, because one of those "
                 "cached records carries a name and no picture. Where the account "
                 "signed in through Facebook the picture address is on Facebook's own "
                 "servers and carries that account's identifier in the address, which "
                 "is a link between the two accounts that the app recorded. The display "
                 "name is the account's at the moment the record was cached, not a "
                 "fixed value: two of the tested images hold the same account with the "
                 "name capitalised differently. Sign In Credential Stored says only "
                 "whether the settings file holds the saved sign in blob. It does on "
                 "all 6 rows. The blob itself is not printed. Clock Offset From Server "
                 "is the value the app stores under core.clock_delta and is reported as "
                 "stored, in seconds; it reads 0 on four rows and a small negative "
                 "number on two. Language is blank on 4 rows because those settings "
                 "files do not carry it. The app also writes a second, much smaller "
                 "settings file inside the per-user folder on the newer images. It "
                 "carries a single migration flag and no account, so it is not read. "
                 "Documents/stickyCredentials.db sits beside all this and holds a login "
                 "table that was empty on the one tested image that has the file.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/prefs',
                  '*/Containers/Data/Application/*/Library/Application Support/Users/*/prefs',
                  '*/Containers/Data/Application/*/Library/Application Support/PersistentCache/mercury.db*'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "user",
                         "sample_data": {
                                            "ctf2020_ios12": "iOS 12.4 | Spotify 8.5.49 | 1 row",
                                            "hickman_ios13": "iOS 13.3.1 | Spotify 8.5.51 | 1 row",
                                            "hickman_ios14": "iOS 14.3 | Spotify 8.5.94 | 1 row",
                                            "hickman_ios15": "iOS 15.3.1 | Spotify 8.8.27 | 1 row",
                                            "iphone11_ios17": "iOS 17.3 | Spotify 8.9.6 | 1 row",
                                            "iphone12_ios18": "iOS 18.7 | Spotify 9.1.0 | 1 row",
                                        },
    },
    "spotify_ios_followed_artists": {
        "name": "Spotify - Followed Artists",
        "description": "Artists the subscription list the Spotify app cached names the "
                       "account as following, with the time recorded against each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-07",
        "last_update_date": "2026-09-07",
        "requirements": "none",
        "category": "Spotify",
        "notes": "One row per entry of the subscription list the app cached in "
                 "Library/Application Support/PersistentCache/mercury.db. The row that "
                 "holds it records the request it answered, which names the account, so "
                 "the account each entry belongs to is recorded rather than assumed. "
                 "Followed is the Unix time the entry carries, reported in UTC. That "
                 "cache is a response the server sent, so this is the list as the "
                 "service held it at the moment of the fetch, and it is the service's "
                 "record of when each artist was followed. The times cluster: on each "
                 "of the 3 images that carry the list all of its entries fall inside "
                 "four minutes of one day, which is what a first run of the app's pick "
                 "some artists step looks like, though nothing here establishes that. "
                 "On one of them the same day also carries the only collection entry "
                 "the store holds. mercury.db is a general response cache and almost "
                 "all of it is downloaded catalogue: on one tested image 2,950 of its "
                 "3,088 rows are track metadata and only one row records which request "
                 "produced it. Nothing else in it is reported here, and the file is "
                 "gone from the three newest tested images, where the app keeps its "
                 "cache a different way.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/PersistentCache/mercury.db*',),
        "output_types": "standard",
        "artifact_icon": "user-plus",
                         "sample_data": {
                                            "ctf2020_ios12": "iOS 12.4 | Spotify 8.5.49 | 12 rows",
                                            "hickman_ios13": "iOS 13.3.1 | Spotify 8.5.51 | 14 rows",
                                            "hickman_ios14": "iOS 14.3 | Spotify 8.5.94 | 14 rows",
                                            "hickman_ios15": "iOS 15.3.1 | Spotify 8.8.27 | 0 rows",
                                            "iphone11_ios17": "iOS 17.3 | Spotify 8.9.6 | 0 rows",
                                            "iphone12_ios18": "iOS 18.7 | Spotify 9.1.0 | 0 rows",
                                        },
    },
}

import json
import os
import pathlib
import plistlib
import re
from datetime import datetime, timedelta, timezone

import scripts.ccl_leveldb
from scripts.ilapfuncs import artifact_processor, does_table_exist_in_db, get_sqlite_db_records, logfunc

_CONTAINER = re.compile(r'(.*?/Containers/Data/Application/[0-9A-Fa-f-]{36})/', re.I)
_USER_DIR = re.compile(r'/PersistentCache/Users/([^/]+?)-user(?:/|$)', re.I)
_CORE_DATA_EPOCH_UTC = datetime(2001, 1, 1, tzinfo=timezone.utc)
_UNIX_EPOCH_UTC = datetime(1970, 1, 1, tzinfo=timezone.utc)
_TRACK_ID = re.compile(r'^[0-9A-Za-z]{22}$')
_SUBSCRIPTIONS = re.compile(rb'hm://socialgraph/subscriptions/artist/([0-9A-Za-z]+)\?')
_SUBSCRIPTION_ENTRY = re.compile(rb'\n\x1e\n\x16([0-9A-Za-z]{22})\x18([\x80-\xff]*[\x00-\x7f])')
_DECORATION = b'vnd.spotify/social-decoration-data'
_PREFS_MARKER = 'autologin.canonical_username'
_RECENTLY_PLAYED = (b'!rp#trk#', b'!rp#ctx#', b'!yl#rpp#')
_COLLECTION = b'!col#'
_OFFLINE = b'!xmeta#offlkeys#'


def _container(path):
    '''The app data container a file sits in, or '' when it is not under one.'''
    match = _CONTAINER.match(str(path).replace('\\', '/'))
    return match.group(1) if match else ''


def _account_of(path):
    '''The account name the per-user cache folder in a path is named for, or ''.'''
    match = _USER_DIR.search(str(path).replace('\\', '/'))
    return match.group(1) if match else ''


def _unix_to_utc(value):
    '''Unix seconds to an aware UTC datetime, or ''.'''
    if value in (None, '', 0):
        return ''
    try:
        return _UNIX_EPOCH_UTC + timedelta(seconds=float(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _core_data_to_utc(value):
    '''Core Data seconds since 2001 to an aware UTC datetime, or ''.'''
    if value in (None, '', 0):
        return ''
    try:
        return _CORE_DATA_EPOCH_UTC + timedelta(seconds=float(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _text(value):
    '''A stored value as text, with a stored null read as absent.'''
    return '' if value is None else str(value)


def _varint(data, offset):
    '''A protobuf varint read at an offset, with the offset after it.'''
    number, shift = 0, 0
    while offset < len(data):
        byte = data[offset]
        number |= (byte & 0x7f) << shift
        shift += 7
        offset += 1
        if not byte & 0x80:
            return number, offset
        if shift > 63:
            return None, offset
    return None, offset


def _fields(data, offset, end):
    '''Protobuf fields between two offsets grouped by number, or None when they do not parse.'''
    parsed = _field_list(data, offset, end)
    if parsed is None:
        return None
    out = {}
    for number, value in parsed:
        out.setdefault(number, []).append(value)
    return out

def _uri_and_time(value):
    '''The item address and the time a store record holds, whichever fields carry them.

    Releases write these records with different field numbers and some leave the address
    out of the value because the key already carries it, so the record is read by what each
    field holds rather than by a field number typed here.
    '''
    uri, stamp = '', None
    for _, item in (_field_list(value) or []):
        if isinstance(item, bytes) and item.startswith(b'spotify:') and not uri:
            uri = item.decode('utf8', 'replace')
        elif isinstance(item, int) and stamp is None and 1_200_000_000 < item < 2_100_000_000:
            stamp = item
    return uri, stamp


def _uri_from_key(key):
    '''The first Spotify address a store key names, or ''.'''
    match = re.search(rb'(spotify:[a-z]+:[0-9A-Za-z]+)', key)
    return match.group(1).decode() if match else ''

def _item_type(uri):
    '''The kind of thing a Spotify address names, or '' when it is not one.'''
    parts = uri.split(':')
    return parts[1].title() if len(parts) > 2 and parts[0] == 'spotify' else ''


def _leveldb_dirs(files_found):
    '''{(container, account): the account's LevelDB directory} for every one found.'''
    dirs = {}
    for found in files_found:
        path = str(found).replace('\\', '/')
        account = _account_of(path)
        if not account or '/primary.ldb/' not in path or os.path.isdir(path):
            continue
        dirs[(_container(path), account)] = os.path.dirname(path)
    return dirs


def _leveldb_records(directory):
    '''The newest record for each key in a LevelDB, as {key: (state, value)}.'''
    latest = {}
    try:
        database = scripts.ccl_leveldb.RawLevelDb(pathlib.Path(directory))
    except (OSError, ValueError) as error:
        logfunc(f'Spotify: could not open the LevelDB at {directory}: {error}')
        return latest
    try:
        for record in database.iterate_records_raw():
            key = bytes(record.user_key)
            if key not in latest or record.seq > latest[key][0]:
                latest[key] = (record.seq, str(record.state).rsplit('.', 1)[-1],
                               bytes(record.value))
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'Spotify: could not read the LevelDB at {directory}: {error}')
    finally:
        try:
            database.close()
        except Exception:                        # pylint: disable=broad-except
            pass
    return {key: (state, value) for key, (_, state, value) in latest.items()}


def _leveldb_all(directory):
    '''Every record in a LevelDB as [(key, state, value)], superseded ones included.

    The store rewrites an entry rather than editing it, so an older record for the same key
    can hold an earlier time. Those are separate recorded times and are kept.
    '''
    out = []
    try:
        database = scripts.ccl_leveldb.RawLevelDb(pathlib.Path(directory))
    except (OSError, ValueError) as error:
        logfunc(f'Spotify: could not open the LevelDB at {directory}: {error}')
        return out
    try:
        for record in database.iterate_records_raw():
            out.append((bytes(record.user_key), str(record.state).rsplit('.', 1)[-1],
                        bytes(record.value)))
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'Spotify: could not read the LevelDB at {directory}: {error}')
    finally:
        try:
            database.close()
        except Exception:                        # pylint: disable=broad-except
            pass
    return out

def _lyrics(files_found):
    '''{(container, track id): {artist, title, cached, song id}} from the lyrics cache.'''
    entries = {}
    for found in files_found:
        path = str(found)
        if os.path.isdir(path) or '/Caches/genius/' not in path.replace('\\', '/'):
            continue
        track = os.path.basename(path)
        if not _TRACK_ID.match(track):
            continue
        try:
            with open(path, 'rb') as handle:
                plist = plistlib.load(handle)
        except Exception as error:               # pylint: disable=broad-except
            logfunc(f'Spotify: could not read the lyrics entry {path}: {error}')
            continue
        if not isinstance(plist, dict):
            continue
        entries[(_container(path), track)] = {
            'artist': _text(plist.get('artist')),
            'title': _text(plist.get('title')),
            'cached': plist.get('cachedTimestamp'),
            'song_id': _text(plist.get('genius_song_id')),
            'path': path,
        }
    return entries


def _app_version(blob):
    '''The app version string the saved state carries, or ''.'''
    match = re.search(rb'\b(\d+\.\d+\.\d+\.\d+)\b', blob)
    return match.group(1).decode() if match else ''

def _field_list(data, start=0, end=None):
    '''Every protobuf field between two offsets, or None when the bytes do not parse.'''
    end = len(data) if end is None else end
    out, offset = [], start
    while offset < end:
        tag, offset = _varint(data, offset)
        if tag is None or tag >> 3 == 0:
            return None
        number, wire = tag >> 3, tag & 7
        if wire == 2:
            length, offset = _varint(data, offset)
            if length is None or offset + length > end:
                return None
            out.append((number, data[offset:offset + length]))
            offset += length
        elif wire == 0:
            value, offset = _varint(data, offset)
            if value is None:
                return None
            out.append((number, value))
        elif wire == 5:
            offset += 4
            out.append((number, None))
        elif wire == 1:
            offset += 8
            out.append((number, None))
        else:
            return None
    return out


def _pairs(blob):
    '''The key and value strings a repeated pair message carries, as a dictionary.

    The saved state names its own metadata keys, so the names here are the file's own
    rather than ones typed in this module.
    '''
    out = {}
    for _, item in (_field_list(blob) or []):
        if not isinstance(item, bytes):
            continue
        pair = _field_list(item) or []
        if len(pair) == 2 and all(isinstance(part, bytes) for _, part in pair):
            out[pair[0][1].decode('utf8', 'replace')] = pair[1][1].decode('utf8', 'replace')
    return out


def _protobuf_state(blob, depth=0):
    '''The playing track a protobuf saved state carries, or None.

    From a later release the file holds a protobuf rather than JSON. The message is
    undocumented, so the track is found by shape, as the first subtree carrying a Spotify
    track address beside a block of three numbers whose first is a millisecond time.
    '''
    parsed = _field_list(blob)
    if parsed is None or depth > 8:
        return None
    track, meta = '', {}
    for _, item in parsed:
        if not isinstance(item, bytes):
            continue
        inner = _field_list(item)
        if inner is None:
            continue
        for _, value in inner:
            if isinstance(value, bytes) and value.startswith(b'spotify:track:'):
                track = value.decode('utf8', 'replace')
        if track:
            meta = _pairs(item)
            break
    if track:
        playback = {}
        for _, item in parsed:
            if not isinstance(item, bytes):
                continue
            numbers = [value for _, value in (_field_list(item) or [])
                       if isinstance(value, int)]
            if len(numbers) >= 3 and 1_200_000_000_000 < numbers[0] < 2_100_000_000_000:
                playback = {'timestamp': numbers[0] * 1000, 'position': numbers[1],
                            'duration': numbers[2]}
                break
        return {'track': track, 'meta': meta, 'playback': playback}
    for _, item in parsed:
        if isinstance(item, bytes) and len(item) > 8:
            found = _protobuf_state(item, depth + 1)
            if found:
                return found
    return None

def _player_states(files_found):
    '''[(container, account, path, saved millisecond stamp, the saved state)] for each file.'''
    states = []
    for found in files_found:
        path = str(found)
        if os.path.isdir(path) or os.path.basename(path) != 'context_player_state_restore':
            continue
        try:
            with open(path, 'rb') as handle:
                raw = handle.read()
        except OSError as error:
            logfunc(f'Spotify: could not read {path}: {error}')
            continue
        stamp, _, body = raw.partition(b'#')
        saved = int(stamp) / 1000 if stamp.isdigit() else None
        if body[:1] == b'{':
            try:
                state = json.loads(body.decode('utf8', 'replace'))
            except ValueError as error:
                logfunc(f'Spotify: could not read the saved player state in {path}: {error}')
                continue
        else:
            found = _protobuf_state(body)
            if not found:
                logfunc(f'Spotify: could not read the saved player state in {path}')
                continue
            state = {'player_model': {'session_queue': {'active': {
                'track': {'uri': found['track'],
                          'metadata': {'overrides': found['meta']}},
                'playback_state': found['playback'],
                'play_origin': {'view_uri': found['meta'].get('context_uri', ''),
                                'feature_version': _app_version(body)}}}}}
        states.append((_container(path), _account_of(path), path, saved, state))
    return states


def _prefs(files_found):
    '''{(container, account): {key: value}} for every Spotify preferences file found.

    A file called prefs is not on its own the app's, so one is only used when it carries the
    key the app writes its signed in account under.
    '''
    out = {}
    for found in files_found:
        path = str(found)
        if os.path.isdir(path) or os.path.basename(path) != 'prefs':
            continue
        try:
            with open(path, 'r', encoding='utf8', errors='replace') as handle:
                raw = handle.read()
        except OSError as error:
            logfunc(f'Spotify: could not read {path}: {error}')
            continue
        if _PREFS_MARKER not in raw:
            continue
        values = {'_path': path}
        for line in raw.splitlines():
            name, _, value = line.partition('=')
            if name:
                values[name.strip()] = value.strip().strip('"')
        account = _account_of(path) or values.get(_PREFS_MARKER, '')
        out[(_container(path), account)] = values
    return out


def _mercury_records(files_found):
    '''[(container, path, value bytes)] for every row of every mercury cache found.'''
    rows = []
    for found in files_found:
        path = str(found)
        if os.path.isdir(path) or os.path.basename(path) != 'mercury.db':
            continue
        if not does_table_exist_in_db(path, 'storage'):
            continue
        try:
            for record in get_sqlite_db_records(path, 'SELECT value FROM storage'):
                if record[0]:
                    rows.append((_container(path), path, bytes(record[0])))
        except Exception as error:                   # pylint: disable=broad-except
            logfunc(f'Spotify: could not read {path}: {error}')
    return rows


def _decoration(value):
    '''The account record held in a social decoration row, or {}.

    The row carries the response headers before the record itself, and a header pair has the
    same shape as the record, so every candidate is read and the last one is the record.
    '''
    start = value.find(_DECORATION)
    if start < 0:
        return {}
    best = {}
    for offset in range(start + len(_DECORATION), len(value) - 2):
        if value[offset] != 0x0a:
            continue
        length, after = _varint(value, offset + 1)
        if not length or length > 64 or after + length > len(value):
            continue
        try:
            value[after:after + length].decode('ascii')
        except UnicodeDecodeError:
            continue
        fields = _fields(value, offset, len(value))
        if fields and 1 in fields and 2 in fields and isinstance(fields[2][0], bytes):
            best = fields
    if not best:
        return {}

    def first(number):
        item = best.get(number, [b''])[0]
        return item.decode('utf8', 'replace') if isinstance(item, bytes) else _text(item)

    return {'username': first(1), 'display': first(2), 'image': first(3), 'large': first(5)}


@artifact_processor
def spotify_ios_recently_played(context):
    '''Tracks and the places they were played from, out of the account's own store.'''
    files_found = context.get_files_found()
    lyrics = _lyrics(files_found)
    data_list, sources = [], []

    for (container, account), directory in _leveldb_dirs(files_found).items():
        sources.append(directory)
        seen = set()
        for key, state, value in _leveldb_all(directory):
            if not key.startswith(_RECENTLY_PLAYED):
                continue
            uri, stamp = _uri_and_time(value)
            uri = uri or _uri_from_key(key)
            if (key, stamp, state) in seen:
                continue
            seen.add((key, stamp, state))
            track = uri.split(':')[-1] if uri.startswith('spotify:track:') else ''
            named = lyrics.get((container, track), {})
            data_list.append((
                _unix_to_utc(stamp),
                _item_type(uri),
                named.get('artist', ''),
                named.get('title', ''),
                uri,
                account,
                state,
            ))

    data_headers = (
        ('Played', 'datetime'), 'Item Type', 'Artist', 'Title', 'Item URI', 'Account',
        'Record State')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def spotify_ios_saved_items(context):
    '''Items saved to the account's collection and items marked to keep on the device.'''
    files_found = context.get_files_found()
    data_list, sources = [], []

    for (_, account), directory in _leveldb_dirs(files_found).items():
        sources.append(directory)
        for key, (state, value) in _leveldb_records(directory).items():
            if key.startswith(_COLLECTION) and b'.' not in key.split(b'#')[1]:
                uri, stamp = _uri_and_time(value)
                uri = uri or _uri_from_key(key)
                kind = 'Saved to collection'
            elif key.startswith(_OFFLINE):
                match = re.search(rb'(spotify:[a-z]+:[0-9A-Za-z]+)', key)
                uri = match.group(1).decode() if match else ''
                stamp, kind = None, 'Marked to keep on device'
            else:
                continue
            if not uri:
                continue
            data_list.append((
                kind,
                _unix_to_utc(stamp),
                _item_type(uri),
                uri,
                account,
                state,
            ))

    data_headers = (
        'Kind', ('Saved', 'datetime'), 'Item Type', 'Item URI', 'Account', 'Record State')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def spotify_ios_player_state(context):
    '''What the app was playing when it last wrote its player state out.'''
    files_found = context.get_files_found()
    data_list, sources = [], []

    for _, account, path, saved, state in _player_states(files_found):
        sources.append(path)
        model = state.get('player_model', {}) if isinstance(state, dict) else {}
        active = model.get('session_queue', {}).get('active', {})
        track = active.get('track', {}) or {}
        meta = (track.get('metadata', {}) or {}).get('overrides', {}) or {}
        playback = active.get('playback_state', {}) or {}
        origin = active.get('play_origin', {}) or {}
        options = model.get('options', {}) or {}
        configuration = model.get('configuration', {}) or {}
        stamp = playback.get('timestamp')
        data_list.append((
            _unix_to_utc(saved),
            _unix_to_utc(stamp / 1_000_000) if isinstance(stamp, (int, float)) and stamp else '',
            _text(meta.get('title')),
            _text(meta.get('artist_name')),
            _text(meta.get('album_title')),
            _text(track.get('uri')),
            _text(meta.get('context_uri') or origin.get('view_uri')),
            _text(playback.get('position')),
            _text(playback.get('duration') or meta.get('duration')),
            'Yes' if active.get('is_playing') else 'No',
            'Yes' if active.get('is_paused') else 'No',
            'Yes' if options.get('shuffling_context') else 'No',
            'Yes' if options.get('repeating_context') else 'No',
            'Yes' if options.get('repeating_track') else 'No',
            'Yes' if configuration.get('player.filter_explicit_content') else 'No',
            _text(origin.get('feature_identifier')),
            _text(origin.get('referrer_identifier')),
            _text(origin.get('feature_version')),
            _text(meta.get('album_uri')),
            _text(meta.get('artist_uri')),
            account,
        ))

    data_headers = (
        ('State Saved', 'datetime'), ('Playback Reported', 'datetime'), 'Title', 'Artist',
        'Album', 'Track URI', 'Played From URI', 'Position (ms)', 'Duration (ms)',
        'Playing', 'Paused', 'Shuffle', 'Repeat Context', 'Repeat Track',
        'Explicit Content Filtered', 'Feature', 'Reached From', 'App Version', 'Album URI',
        'Artist URI', 'Account')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def spotify_ios_play_history(context):
    '''The list of tracks the saved player state carries as its own play history.'''
    files_found = context.get_files_found()
    lyrics = _lyrics(files_found)
    data_list, sources = [], []

    for container, account, path, saved, state in _player_states(files_found):
        history = (state.get('play_history', {}) or {}).get('tracks', []) or []
        if not history:
            continue
        sources.append(path)
        for position, entry in enumerate(history, start=1):
            uri = _text(entry.get('uri') if isinstance(entry, dict) else entry)
            track = uri.split(':')[-1] if uri.startswith('spotify:track:') else ''
            named = lyrics.get((container, track), {})
            data_list.append((
                _unix_to_utc(saved),
                position,
                _item_type(uri),
                named.get('artist', ''),
                named.get('title', ''),
                uri,
                _text(entry.get('uid') if isinstance(entry, dict) else ''),
                account,
            ))

    data_headers = (
        ('State Saved', 'datetime'), 'Position In List', 'Item Type', 'Artist', 'Title',
        'Item URI', 'Play ID', 'Account')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def spotify_ios_lyrics_cache(context):
    '''Lyrics the app kept for a track, and when it kept them.'''
    files_found = context.get_files_found()
    data_list, sources = [], []

    for (_, track), entry in _lyrics(files_found).items():
        sources.append(entry['path'])
        data_list.append((
            _core_data_to_utc(entry['cached']),
            entry['artist'],
            entry['title'],
            f'spotify:track:{track}',
            entry['song_id'],
        ))

    data_headers = (
        ('Cached', 'datetime'), 'Artist', 'Title', 'Track URI', 'Lyrics Provider Song ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def spotify_ios_podcast_playback(context):
    '''Podcast episodes the account has played, and how far into each it got.'''
    files_found = context.get_files_found()
    data_list, sources = [], []

    for found in files_found:
        path = str(found)
        if os.path.isdir(path) or os.path.basename(path) != 'played-state-storage':
            continue
        account = _account_of(path)
        try:
            with open(path, 'rb') as handle:
                raw = handle.read()
        except OSError as error:
            logfunc(f'Spotify: could not read {path}: {error}')
            continue
        parsed = _fields(raw, 0, len(raw))
        if not parsed:
            continue
        sources.append(path)
        for record in parsed.get(1, []):
            if not isinstance(record, bytes):
                continue
            entry = _fields(record, 0, len(record))
            if not entry:
                continue

            def one(number, holder=entry):
                item = holder.get(number, [None])[0]
                return item.decode('utf8', 'replace') if isinstance(item, bytes) else item

            position, duration = one(3), one(8)
            through = ''
            if isinstance(position, int) and isinstance(duration, int) and duration:
                through = f'{position / duration:.1%}'
            data_list.append((
                _unix_to_utc(one(4)),
                _text(one(2)),
                _text(one(1)),
                _text(position),
                _text(duration),
                through,
                account,
            ))

    data_headers = (
        ('Last Played', 'datetime'), 'Episode URI', 'Show URI', 'Position (Seconds)',
        'Duration (Seconds)', 'Played Through', 'Account')
    return data_headers, data_list, '\n'.join(sources)

@artifact_processor
def spotify_ios_account(context):
    '''The account the app is signed in to, from its settings and its cached profile.'''
    files_found = context.get_files_found()
    profiles = {}
    for container, path, value in _mercury_records(files_found):
        record = _decoration(value)
        if record.get('username'):
            profiles[(container, record['username'])] = (record, path)

    data_list, sources = [], []
    for (container, account), values in _prefs(files_found).items():
        username = values.get(_PREFS_MARKER, '') or account
        record, profile_path = profiles.get((container, username), ({}, ''))
        sources.append(values.get('_path', ''))
        data_list.append((
            username,
            record.get('display', ''),
            values.get('language', ''),
            values.get('core.clock_delta', ''),
            'Yes' if values.get('autologin.blob') else 'No',
            record.get('image', ''),
            record.get('large', ''),
        ))
        if profile_path:
            sources.append(profile_path)

    sources = [source for source in sources if source]
    data_headers = (
        'Username', 'Display Name', 'Language', 'Clock Offset From Server (Seconds)',
        'Sign In Credential Stored', 'Profile Picture URL', 'Profile Picture URL (Large)')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def spotify_ios_followed_artists(context):
    '''Artists the account follows, with the time each was followed.'''
    files_found = context.get_files_found()
    data_list, sources = [], []

    for _, path, value in _mercury_records(files_found):
        owner = _SUBSCRIPTIONS.search(value)
        if not owner:
            continue
        sources.append(path)
        for artist, stamp in _SUBSCRIPTION_ENTRY.findall(value):
            number, _ = _varint(stamp, 0)
            data_list.append((
                _unix_to_utc(number),
                f'spotify:artist:{artist.decode()}',
                owner.group(1).decode(),
            ))

    data_headers = (('Followed', 'datetime'), 'Artist URI', 'Account')
    return data_headers, data_list, '\n'.join(sources)
