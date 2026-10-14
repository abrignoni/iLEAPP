""" Media Remote daemon preferences: com.apple.mediaremote.plist """
__artifacts_v2__ = {
    "mediaRemoteSystemEndpoint": {
        "name": "Media Remote System Endpoint",
        "description": "One row per entry under SystemEndpoint in com.apple.mediaremote.plist, "
                       "with the date, event and reason text stored for it.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-10",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "Media Remote",
        "notes": "Date is the date stored in the entry. Time Since is the stored timesince "
                 "number, as stored; its unit is not established. Date Plus Time Since is "
                 "computed by this module as Date plus Time Since read as seconds: on the 20 "
                 "sample_data images that hold the file the two entries give the same Date Plus "
                 "Time Since to within a millisecond, and what that moment records is not "
                 "established. Dates are shown to the second. Entry is the key under "
                 "SystemEndpoint; on all 20 images the entries were Proactive (Type 1) and "
                 "UserSelected (Type 0). Event and Event Description are stored together, and "
                 "the pairs seen were 0 StartUp, 1 UserSelected, 5 Playback and 7 "
                 "NowPlayingAppRemoved. Event Reason and Selection Reason are text stored in "
                 "the entry, shown as stored. Change Type and Change Type Description have no "
                 "value on ctf2020_ios12 and hickman_ios13, where the entries do not hold those "
                 "keys. Other Keys lists every key of the entry that has no column of its own, "
                 "as key=value, and has no value when there is none: supportsIdleReset was seen "
                 "on 9 images and demoteWhenSyncingToCompanion on 2. No key seen in an entry "
                 "names an output device. The 3 images recorded with 0 rows have no "
                 "com.apple.mediaremote.plist under mobile/Library/Preferences. Suggested in "
                 "issue #1876.",
        "paths": ('*/mobile/Library/Preferences/com.apple.mediaremote.plist',),
        "output_types": "standard",
        "artifact_icon": "cast",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 2 rows",
            "hickman_ios13": "iOS 13.3.1 | 2 rows",
            "hickman_ios14": "iOS 14.3 | 2 rows",
            "jess_ios15": "iOS 15.0.2 | 2 rows",
            "hickman_ios15": "iOS 15.3.1 | 2 rows",
            "magnet_ios16": "iOS 16.1.1 | 2 rows",
            "abe_ios16": "iOS 16.5 | 2 rows",
            "felix23_ios16": "iOS 16.5 | 2 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 2 rows",
            "fsfull002_ios17": "iOS 17.1 | 2 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 2 rows",
            "hc_ios17_2": "iOS 17.2.1 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | 2 rows",
            "felix_ios17": "iOS 17.6.1 | 2 rows",
            "iphone14plus_ios18": "iOS 18.0 | 2 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 2 rows",
            "dexter_ios18": "iOS 18.3.2 | 2 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 2 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
    "mediaRemoteDates": {
        "name": "Media Remote Stored Dates",
        "description": "One row per date stored in com.apple.mediaremote.plist outside "
                       "SystemEndpoint, with the key it is stored under.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-10",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "Media Remote",
        "notes": "Every date value in the file outside SystemEndpoint, which Media Remote System "
                 "Endpoint reports. Key is the top-level key the date sits under and Sub Key is "
                 "the rest of its key path; Sub Key has no value for a date stored directly "
                 "under a top-level key. Dates are shown to the second. Keys seen on the 20 "
                 "sample_data images that hold the file: PersonalDeviceState with Sub Key "
                 "kMRDPersonalDeviceControllerPersonalDeviceStateDateKey (18 images), "
                 "LastPlayingDate (15), MRDPQPDS.PED (7) and RecentlySelectedDevices (2 images: "
                 "abe_ios16 with 1 entry and otto_ios17 with 3), where Sub Key is the name the "
                 "date is stored under. What each date records is not established beyond its key "
                 "name. The binary plists embedded in the file (DefaultSupportedCommands, "
                 "IRServiceToken, MRDPQPDS.RPS) are not opened by this artifact; opened "
                 "separately on these images, they held no date. Not reported: "
                 "ConnectedClientAuditTokens, ExpectedClientAuditTokens, "
                 "kMRSettingsConnectedClientPIDS, LastBootUUID, LocalPlaybackState, "
                 "MinorUserState, MRDPQPDS.PPR, SystemEndpointRecentlyDismissedRecommendations, "
                 "the MRUserSettings flags, and the device list under PersonalDeviceState, which "
                 "was empty on all 18 images that have it. Of the 4 images recorded with 0 rows, "
                 "3 have no com.apple.mediaremote.plist under mobile/Library/Preferences and "
                 "ctf2020_ios12 has it with no date outside SystemEndpoint. Suggested in issue "
                 "#1876.",
        "paths": ('*/mobile/Library/Preferences/com.apple.mediaremote.plist',),
        "output_types": "standard",
        "artifact_icon": "cast",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 1 rows",
            "hickman_ios14": "iOS 14.3 | 2 rows",
            "jess_ios15": "iOS 15.0.2 | 2 rows",
            "hickman_ios15": "iOS 15.3.1 | 2 rows",
            "magnet_ios16": "iOS 16.1.1 | 2 rows",
            "abe_ios16": "iOS 16.5 | 3 rows",
            "felix23_ios16": "iOS 16.5 | 1 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 2 rows",
            "fsfull002_ios17": "iOS 17.1 | 1 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 3 rows",
            "hc_ios17_2": "iOS 17.2.1 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 3 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | 6 rows",
            "felix_ios17": "iOS 17.6.1 | 3 rows",
            "iphone14plus_ios18": "iOS 18.0 | 1 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 2 rows",
            "dexter_ios18": "iOS 18.3.2 | 3 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 3 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
}

from datetime import datetime, timedelta

from scripts.ilapfuncs import (artifact_processor, convert_plist_date_to_utc, get_file_path,
                               get_plist_file_content, logfunc)

_SYSTEM_ENDPOINT_KEY = 'SystemEndpoint'
# Keys of a SystemEndpoint entry that get a column of their own, in column order.
_ENDPOINT_COLUMNS = ('type', 'event', 'eventdescription', 'eventreason', 'selectionreason',
                     'changeType', 'changeTypeDescription', 'timesince')


def _load(context):
    source_path = get_file_path(context.get_files_found(), 'com.apple.mediaremote.plist')
    if not source_path:
        return '', {}
    plist = get_plist_file_content(source_path)
    if not isinstance(plist, dict):
        logfunc(f'{source_path} did not read as a plist dictionary')
        return source_path, {}
    return source_path, plist


def _text(value):
    return '' if value is None else str(value)


def _stored_dates(value, key_path, rows):
    """Collect every date under value. Embedded binary plists are not opened."""
    if isinstance(value, datetime):
        rows.append((convert_plist_date_to_utc(value), key_path[0], '/'.join(key_path[1:])))
    elif isinstance(value, dict):
        for key in sorted(value, key=str):
            _stored_dates(value[key], key_path + [str(key)], rows)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _stored_dates(item, key_path + [f'[{index}]'], rows)


@artifact_processor
def mediaRemoteSystemEndpoint(context):
    """ See artifact description """
    data_headers = (('Date', 'datetime'), ('Date Plus Time Since', 'datetime'), 'Entry', 'Type',
                    'Event', 'Event Description', 'Event Reason', 'Selection Reason',
                    'Change Type', 'Change Type Description', 'Time Since', 'Other Keys')
    data_list = []
    source_path, plist = _load(context)
    if not source_path:
        return data_headers, data_list, ''

    endpoints = plist.get(_SYSTEM_ENDPOINT_KEY)
    if not isinstance(endpoints, dict):
        logfunc(f'{source_path} holds no {_SYSTEM_ENDPOINT_KEY} dictionary')
        return data_headers, data_list, source_path

    for name in sorted(endpoints, key=str):
        entry = endpoints[name]
        if not isinstance(entry, dict):
            logfunc(f'{_SYSTEM_ENDPOINT_KEY} entry {name} is not a dictionary and was not reported')
            continue
        date = entry.get('date')
        time_since = entry.get('timesince')
        shown = set(_ENDPOINT_COLUMNS)
        stored_date = date_plus = ''
        if isinstance(date, datetime):
            shown.add('date')
            stored_date = convert_plist_date_to_utc(date)
            if isinstance(time_since, (int, float)) and not isinstance(time_since, bool):
                try:
                    date_plus = convert_plist_date_to_utc(date + timedelta(seconds=time_since))
                except OverflowError:
                    logfunc(f'{_SYSTEM_ENDPOINT_KEY} entry {name}: timesince is out of range')
        other = '; '.join(f'{key}={entry[key]}' for key in sorted(entry, key=str)
                          if key not in shown)
        data_list.append((stored_date, date_plus, str(name))
                         + tuple(_text(entry.get(key)) for key in _ENDPOINT_COLUMNS)
                         + (other,))
    return data_headers, data_list, source_path


@artifact_processor
def mediaRemoteDates(context):
    """ See artifact description """
    data_headers = (('Timestamp', 'datetime'), 'Key', 'Sub Key')
    data_list = []
    source_path, plist = _load(context)
    if not source_path:
        return data_headers, data_list, ''

    for key in sorted(plist, key=str):
        if key != _SYSTEM_ENDPOINT_KEY:
            _stored_dates(plist[key], [str(key)], data_list)
    return data_headers, data_list, source_path
