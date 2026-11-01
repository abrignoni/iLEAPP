__artifacts_v2__ = {
    "carkitConnectionEvents": {
        "name": "CarKit Connection Events",
        "description": "Connection events carkitd kept in its CARConnectionTimeEventStoreKey array, with the "
                       "event name and type as stored and any vehicle details the event carried",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-01",
        "last_update_date": "2026-11-01",
        "requirements": "none",
        "category": "CarPlay",
        "notes": ('Read from the CARConnectionTimeEventStoreKey array in '
                  'Library/Preferences/com.apple.internal.carkitd.plist, one row per stored event. Event and Event '
                  "Type (as stored) are the event's event and eventType values. Source-verified: the iOS 16 carkitd "
                  '(abe_ios16) builds these entries with eventWithName:type:date:payload:, and in the iOS 18.7 '
                  "shared cache (iphone12_ios18) every stored event name is one of CarKit's event name constants, "
                  'which that code groups by source (Bluetooth, iAP, Wi-Fi association, CarKit, accessoryd, '
                  'mediaserverd, AirPlay, mDNSResponder). No names for the type numbers were found. Across the 328 '
                  'events on the 6 tested images that held any (hc_ios18_7 and hc_ios26 hold the same 25-event '
                  "array), no event name occurred under two type numbers, and by that constant list's grouping each "
                  'type number went with one group only (1 Bluetooth, 2 Wi-Fi, 3 AirPlay, 4 CarKit, 7 iAP); that '
                  'pairing is an observation, not a source, so the number is reported as stored. Timestamp is the '
                  "event's timestamp, a plist date shown in UTC. 114 type 2 events held exactly the Cocoa reference "
                  'date (2001-01-01 00:00:00), a zero rather than a time, so Timestamp is blank for them and '
                  'Timestamp Stored As Reference Date says Yes (79 of 100 events on abe_ios16, 17 on iphone11_ios17 '
                  'and 18 on otto_ios17). Transport Type is the transportType key, on the event on the iOS 16 and '
                  '17 images and inside the payload on the iOS 18 and 26 images (USB on all 39 events that held '
                  "it); CarKit Transport Event is the payload's CARCarKitTransportEvent value. Vehicle Name, "
                  "Manufacturer, Model, Firmware Version, Hardware Version and PPID are the payload's name, "
                  'iAPManufacturer, iAPModel, firmwareVersion, hardwareVersion and ppid: they were set only on the '
                  '6 CARCarKitVehicleInformationEvent events (2 each on dexter_ios18, hc_ios18_7 and hc_ios26, the '
                  'last two the same records), empty on the other 3 images, and PPID was set on 1. Other Payload '
                  'holds any other payload keys as JSON with keys sorted; on the tested images these were '
                  'AP_SIGNPOST_ keys with numeric values on 9 of the 10 rows that had any, and what they measure '
                  "and their units are not established. Identifier is the event's identifier as stored: it took 1 "
                  'to 3 values per image, and on 2 of the 3 images that also store CARConnectionTimeSessionUUIDKey '
                  'it matched that value; what it identifies is not established. The array held exactly 100 events '
                  'on 2 images; whether older events are dropped is not established. Not reported: '
                  'CARDNDAssertionStateKey (an integer), CRCarPlayCapabilitiesPlistPathKey (a path string), and '
                  'CRInstrumentClusterSessionURLsDefaultsKey and CARPreviousSessionInfoKey, empty arrays on every '
                  'tested image that held them; none carried a time on the tested images. The tested iTunes backup '
                  'held the plist with no events.'),
        "paths": ('*/Library/Preferences/com.apple.internal.carkitd.plist',),
        "output_types": "standard",
        "artifact_icon": "car",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 100 rows",
            "iphone11_ios17": "iOS 17.3 | 100 rows",
            "otto_ios17": "iOS 17.5.1 | 58 rows",
            "hc_ios18_7": "iOS 18.7.8 | 25 rows",
            "hc_ios26": "iOS 26.5.2 | 25 rows",
            "dexter_ios18": "iOS 18.3.2 | 20 rows",
            "belkactf6_tar": "iOS 16.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "hickman_ios14_itunes_backup_decrypted": "iOS 14.3 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        },
    }
}

import json
import os
import plistlib
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, logfunc

# A stored time of exactly the Cocoa reference date is a zero, not a moment
REFERENCE_DATE = datetime(2001, 1, 1)
VEHICLE_KEYS = ('name', 'iAPManufacturer', 'iAPModel', 'firmwareVersion', 'hardwareVersion', 'ppid')
TRANSPORT_KEYS = ('transportType', 'CARCarKitTransportEvent')


def _text(value):
    return '' if value is None else str(value)


@artifact_processor
def carkitConnectionEvents(context):
    data_headers = (('Timestamp', 'datetime'), 'Event', 'Event Type (as stored)', 'Transport Type',
                    'CarKit Transport Event',
                    'Vehicle Name', 'Manufacturer', 'Model', 'Firmware Version', 'Hardware Version', 'PPID',
                    'Identifier', 'Other Payload', 'Timestamp Stored As Reference Date')
    data_list = []
    sources = []
    for file_found in sorted(str(f) for f in context.get_files_found()):
        if not os.path.isfile(file_found):
            continue
        try:
            with open(file_found, 'rb') as fp:
                prefs = plistlib.load(fp)
        except (OSError, plistlib.InvalidFileException, ValueError) as error:
            logfunc(f'CarKit Connection Events: could not read {os.path.basename(file_found)}: {error}')
            continue
        sources.append(file_found)
        events = prefs.get('CARConnectionTimeEventStoreKey') if isinstance(prefs, dict) else None
        if not isinstance(events, list):
            continue
        for event in events:
            if not isinstance(event, dict):
                continue
            payload = event.get('payload') if isinstance(event.get('payload'), dict) else {}
            stamp = event.get('timestamp')
            zero = isinstance(stamp, datetime) and stamp == REFERENCE_DATE
            timestamp = stamp.replace(tzinfo=timezone.utc) if isinstance(stamp, datetime) and not zero else ''
            # transportType sits on the event on some versions and in the payload on others
            transport = _text(event.get('transportType', payload.get('transportType')))
            other = {k: v for k, v in payload.items() if k not in VEHICLE_KEYS and k not in TRANSPORT_KEYS}
            data_list.append((
                timestamp, _text(event.get('event')), _text(event.get('eventType')), transport,
                _text(payload.get('CARCarKitTransportEvent')),
                *(_text(payload.get(k)) for k in VEHICLE_KEYS),
                _text(event.get('identifier')),
                json.dumps(other, sort_keys=True, default=str) if other else '',
                'Yes' if zero else 'No'))

    return data_headers, data_list, '\n'.join(sources)
