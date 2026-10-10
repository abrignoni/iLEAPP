""" Media Experience preferences: com.apple.mediaexperience.plist """
__artifacts_v2__ = {
    "mediaExperienceEndpoints": {
        "name": "Media Experience Endpoints",
        "description": "One row per endpoint named under volumes or endpointTypeInfo in "
                       "com.apple.mediaexperience.plist, with the endpoint type and the volume "
                       "values stored for it.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-10",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "Media Experience",
        "notes": "Endpoint is the key as stored under volumes or endpointTypeInfo, and Endpoint "
                 "Type is the endpointTypeInfo value stored for it. The 18 sample_data images "
                 "that hold the file gave 51 rows. 16 of them, on 7 images, are named "
                 "HeadphonesBT~ followed by six colon-separated hex pairs, with Endpoint Type "
                 "Headphones (7), Vehicle (5) or Unspecified (4). The Endpoint Type values seen "
                 "were Unspecified, Headphones and Vehicle. Each volume column holds the number "
                 "stored for that category under the endpoint, as stored; the values seen ran "
                 "from 0.0 to 1.0 and their scale is not established. Audio/Video Volume was "
                 "seen on 17 images, PhoneCall Volume on 10, VoiceCommand Volume on 9, Alarm "
                 "Volume on 2 (abe_ios16, otto_ios17) and Ringtone Volume on 1 (dexter_ios18); a "
                 "volume column has no value where the endpoint holds none for that category. 15 "
                 "rows have a type and no volumes, and 1 row (on dexter_ios18) has a volume and "
                 "no type. Other Volumes lists any category without a column of its own as "
                 "key=value and has no value on these images. No value in the file is a date on "
                 "these images. The 5 images recorded with 0 rows have no "
                 "com.apple.mediaexperience.plist under mobile/Library/Preferences. Suggested in "
                 "issue #1876.",
        "paths": ('*/mobile/Library/Preferences/com.apple.mediaexperience.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "volume-2",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 1 rows",
            "abe_ios16": "iOS 16.5 | 7 rows",
            "felix23_ios16": "iOS 16.5 | 3 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 2 rows",
            "fsfull002_ios17": "iOS 17.1 | 2 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 2 rows",
            "hc_ios17_2": "iOS 17.2.1 | 3 rows",
            "iphone11_ios17": "iOS 17.3 | 4 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | 5 rows",
            "felix_ios17": "iOS 17.6.1 | 3 rows",
            "iphone14plus_ios18": "iOS 18.0 | 1 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 1 rows",
            "dexter_ios18": "iOS 18.3.2 | 8 rows",
            "iphone12_ios18": "iOS 18.7 | 2 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1 rows",
            "falken_ios26": "iOS 26.2.1 | 2 rows",
            "hc_ios26": "iOS 26.5.2 | 2 rows",
        },
    },
    "mediaExperienceState": {
        "name": "Media Experience State",
        "description": "The keys of com.apple.mediaexperience.plist other than the per-endpoint "
                       "volumes and types and six boolean flags listed in the notes, flattened "
                       "to one row per stored value with its key path, rendered as text.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-10",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "Media Experience",
        "notes": "Every key of the file other than volumes and endpointTypeInfo, which Media "
                 "Experience Endpoints reports, and six boolean flags that are not reported: "
                 "AirPlayLowLatencyEntriesDeleted, AirTunesEntriesDeleted, "
                 "BluetoothA2DPAndHFPVolumesCombined, "
                 "celestialToMediaExperienceDomainMigrationFullyCompleted, "
                 "endpointTypeInfoEntriesDeleted and "
                 "ringerMutePreferenceToMediaExperienceDomainMigrationComplete. Nested "
                 "dictionaries are flattened as parent.key and lists as parent[index]. Values "
                 "are rendered as text: booleans as True or False, binary data as hex. An empty "
                 "dictionary or list gives no row. Keys seen on the 18 sample_data images that "
                 "hold the file: volumeMultiplier (17 images), silentModeEnabled, "
                 "silentModeReason and silentModeClientType (14 each), nowPlayingAppDisplayID "
                 "(13), nowPlayingAppDisplayIDStack (7), "
                 "nowPlayingAppHostProcessAttributionBundleID (7, empty on 5), "
                 "nowPlayingAppWasPlayingUponCarPlayDisconnect (6), volumeLimits (3), "
                 "mediaEndowments (3, empty on 2), mutedSessionBundleIDs (3, empty on all 3) and "
                 "nowPlayingAppDisplayIDUponCarPlayDisconnect (2). What each key records is not "
                 "established beyond its name. No value in the file is a date on these images. "
                 "The 5 images recorded with 0 rows have no com.apple.mediaexperience.plist "
                 "under mobile/Library/Preferences. Suggested in issue #1876.",
        "paths": ('*/mobile/Library/Preferences/com.apple.mediaexperience.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "volume-2",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 2 rows",
            "abe_ios16": "iOS 16.5 | 3 rows",
            "felix23_ios16": "iOS 16.5 | 1 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 2 rows",
            "fsfull002_ios17": "iOS 17.1 | 5 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 5 rows",
            "hc_ios17_2": "iOS 17.2.1 | 5 rows",
            "iphone11_ios17": "iOS 17.3 | 6 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 4 rows",
            "otto_ios17": "iOS 17.5.1 | 7 rows",
            "felix_ios17": "iOS 17.6.1 | 5 rows",
            "iphone14plus_ios18": "iOS 18.0 | 4 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 6 rows",
            "dexter_ios18": "iOS 18.3.2 | 12 rows",
            "iphone12_ios18": "iOS 18.7 | 10 rows",
            "hc_ios18_7": "iOS 18.7.8 | 7 rows",
            "falken_ios26": "iOS 26.2.1 | 8 rows",
            "hc_ios26": "iOS 26.5.2 | 8 rows",
        },
    },
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_plist_file_content, logfunc

_VOLUMES_KEY = 'volumes'
_ENDPOINT_TYPE_KEY = 'endpointTypeInfo'
# Volume categories that get a column of their own, in column order.
_VOLUME_COLUMNS = ('Audio/Video', 'PhoneCall', 'VoiceCommand', 'Alarm', 'Ringtone')
# Boolean flags left out of Media Experience State.
_HOUSEKEEPING_KEYS = frozenset((
    'AirPlayLowLatencyEntriesDeleted',
    'AirTunesEntriesDeleted',
    'BluetoothA2DPAndHFPVolumesCombined',
    'celestialToMediaExperienceDomainMigrationFullyCompleted',
    'endpointTypeInfoEntriesDeleted',
    'ringerMutePreferenceToMediaExperienceDomainMigrationComplete',
))


def _load(context):
    source_path = get_file_path(context.get_files_found(), 'com.apple.mediaexperience.plist')
    if not source_path:
        return '', {}
    plist = get_plist_file_content(source_path)
    if not isinstance(plist, dict):
        logfunc(f'{source_path} did not read as a plist dictionary')
        return source_path, {}
    return source_path, plist


def _dict(plist, key):
    value = plist.get(key)
    return value if isinstance(value, dict) else {}


def _flatten(value, key_path, rows):
    if isinstance(value, dict):
        for key in sorted(value, key=str):
            _flatten(value[key], f'{key_path}.{key}' if key_path else str(key), rows)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _flatten(item, f'{key_path}[{index}]', rows)
    elif isinstance(value, bytes):
        rows.append((key_path, value.hex()))
    else:
        rows.append((key_path, str(value)))


@artifact_processor
def mediaExperienceEndpoints(context):
    """ See artifact description """
    data_headers = ('Endpoint', 'Endpoint Type') + tuple(
        f'{category} Volume' for category in _VOLUME_COLUMNS) + ('Other Volumes',)
    data_list = []
    source_path, plist = _load(context)
    if not source_path:
        return data_headers, data_list, ''

    volumes = _dict(plist, _VOLUMES_KEY)
    types = _dict(plist, _ENDPOINT_TYPE_KEY)
    for endpoint in sorted(set(volumes) | set(types), key=str):
        stored = volumes.get(endpoint)
        shown = ()
        other = ''
        if isinstance(stored, dict):
            shown = tuple(str(stored[category]) if category in stored else ''
                          for category in _VOLUME_COLUMNS)
            other = '; '.join(f'{key}={stored[key]}' for key in sorted(stored, key=str)
                              if key not in _VOLUME_COLUMNS)
        elif stored is not None:
            other = str(stored)
        data_list.append((str(endpoint), str(types.get(endpoint, '')))
                         + (shown or ('',) * len(_VOLUME_COLUMNS)) + (other,))
    return data_headers, data_list, source_path


@artifact_processor
def mediaExperienceState(context):
    """ See artifact description """
    data_headers = ('Key', 'Value')
    data_list = []
    source_path, plist = _load(context)
    if not source_path:
        return data_headers, data_list, ''

    remaining = {key: value for key, value in plist.items()
                 if key not in _HOUSEKEEPING_KEYS and key not in (_VOLUMES_KEY, _ENDPOINT_TYPE_KEY)}
    _flatten(remaining, '', data_list)
    return data_headers, data_list, source_path
