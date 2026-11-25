__artifacts_v2__ = {
    "netusage_appdata": {
        "name": "Network Usage - App Data",
        "description": "Parses app data from netusage.sqlite",
        "author": "@stark4n6, @snoop168",
        "creation_date": "2023-02-13",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "Network & Connectivity",
        "notes": "ZKIND is reported as stored; its values are not documented. The three timestamps "
                 "are ZLIVEUSAGE.ZTIMESTAMP, ZPROCESS.ZFIRSTTIMESTAMP and ZPROCESS.ZTIMESTAMP read "
                 "as seconds from 2001-01-01 UTC; what each marks is not sourced. On iOS 18.7 (22H20) "
                 "the writer in SymptomEvaluator stores AWDL traffic in the Wired columns, so they are "
                 "not cabled traffic on that build; other builds were not read. Only the first "
                 "netusage.sqlite that holds both tables is read.",
        "paths": ('*/netusage.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "chart-pie",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 282 rows",
            "dexter_ios18": "iOS 18.3.2 | 534 rows",
            "felix_ios17": "iOS 17.6.1 | 290 rows",
            "fsfull002_ios17": "iOS 17.1 | 232 rows",
            "hc_ios18_7": "iOS 18.7.8 | 397 rows",
            "iphone11_ios17": "iOS 17.3 | 595 rows",
            "iphone12_ios18": "iOS 18.7 | 287 rows",
            "iphone14plus_ios18": "iOS 18.0 | 313 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 408 rows",
            "felix23_ios16": "iOS 16.5 | 261 rows",
            "hickman_ios13": "iOS 13.3.1 | 232 rows",
            "hickman_ios14": "iOS 14.3 | 335 rows",
            "jess_ios15": "iOS 15.0.2 | 169 rows",
            "magnet_ios16": "iOS 16.1.1 | 229 rows",
        },
    },
    "netusage_connections": {
        "name": "Network Usage - Connections",
        "description": "Network attachments and their route performance counters from netusage.sqlite",
        "author": "@stark4n6, @snoop168, @AlexisBrignoni, Claude",
        "creation_date": "2023-02-13",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "Network & Connectivity",
        "notes": "The field meanings and joins below were derived independently from each store's Core"
                 " Data model, measured data and Apple's code. Code statements were read in "
                 "SymptomEvaluator on iOS 18.7 (22H20); other builds were not read. Measured on 12 iOS"
                 " images from 12.4 to 26.5.2 (ctf2020_ios12, hickman_ios13, hickman_ios14, "
                 "jess_ios15, magnet_ios16, hexordia_ios1651, cookbook_ios1751, felix_ios17, "
                 "iphone12_ios18, hc_ios18_7, hill_iphone15pro_ios26, wilkerson_iphone16_ios26). One "
                 "row per ZLIVEROUTEPERF row, joined through the hasNetworkAttachment relationship "
                 "defined in the cached model of each measured store "
                 "(ZLIVEROUTEPERF.ZHASNETWORKATTACHMENT = ZNETWORKATTACHMENT.Z_PK). A network with "
                 "more than one linked row is listed once per linked row, and a network with none is "
                 "listed once with the route columns empty. On the 12 images all 5,220 route rows "
                 "carried a link to one of the 5,123 networks, and one network had no route row. "
                 "Versions of this artifact from before the 2026-10-04 change paired the two tables by"
                 " their own row numbers, so reports made with them can show counters on the wrong "
                 "network. Attachment First Timestamp and Attachment Timestamp are "
                 "ZNETWORKATTACHMENT.ZFIRSTTIMESTAMP and ZTIMESTAMP, seconds from 2001-01-01 UTC. On "
                 "iOS 18.7 the writer sets both from the current date rounded to the day in the "
                 "device's calendar. Both fall on a whole hour on all 5,123 networks and none on UTC "
                 "midnight. Read them as dates, not as the time of a connection. The UTC date shown "
                 "can be the day before or after the day the device recorded. Attachment First "
                 "Timestamp was later than Attachment Timestamp on 2 networks. Route Performance "
                 "Timestamp is ZLIVEROUTEPERF.ZTIMESTAMP, also on a whole hour on all 5,220 rows; what"
                 " it marks is not sourced. Network Type maps ZKIND: the writer stores 2 for a "
                 "cellular attachment and 1 on its only other path, a Wi-Fi network change. On the "
                 "other builds the label rests on the identifier form: all 237 kind 1 identifiers end "
                 "in a BSSID and all 4,886 kind 2 identifiers fit a cellular form. Identifier (as "
                 "stored) is ZIDENTIFIER. The writer composes it as network name, a hyphen and BSSID "
                 "for Wi-Fi, and carrier name, a hyphen and decimal cell identifier for cellular, or "
                 "the literal CollapsedNR. For CollapsedNR both Network Name and BSSID or Cell ID are "
                 "left blank. All 5,123 identifiers fit one of these forms. The value is split at the "
                 "last hyphen because a name can hold a hyphen. The stored BSSID is zero-padded on "
                 "some images and not on others, and is lower case. BSSID or Cell ID shows a BSSID as "
                 "six upper-case two-digit bytes so one BSSID reads the same on every image. Byte, "
                 "packet and connection columns are reported as stored and their units were not "
                 "traced. Only the first netusage.sqlite that holds both tables is read.",
        "paths": ('*/netusage.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "network",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 522 rows",
            "dexter_ios18": "iOS 18.3.2 | 1534 rows",
            "felix_ios17": "iOS 17.6.1 | 980 rows",
            "fsfull002_ios17": "iOS 17.1 | 5 rows",
            "hc_ios18_7": "iOS 18.7.8 | 431 rows",
            "iphone11_ios17": "iOS 17.3 | 1334 rows",
            "iphone12_ios18": "iOS 18.7 | 287 rows",
            "iphone14plus_ios18": "iOS 18.0 | 20 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 3429 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 4 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 475 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 662 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 1502 rows",
            "felix23_ios16": "iOS 16.5 | 366 rows",
            "hickman_ios13": "iOS 13.3.1 | 52 rows",
            "hickman_ios14": "iOS 14.3 | 49 rows",
            "jess_ios15": "iOS 15.0.2 | 240 rows",
            "magnet_ios16": "iOS 16.1.1 | 17 rows",
        },
    }
}

import re

from scripts.ilapfuncs import (artifact_processor, get_sqlite_db_records, does_table_exist_in_db,
                               convert_cocoa_core_data_ts_to_utc, logfunc)

_BSSID = re.compile(r'[0-9A-Fa-f]{1,2}(?::[0-9A-Fa-f]{1,2}){5}')


def _split_identifier(identifier, kind):
    '''(network name, BSSID or cell id) from ZIDENTIFIER, both blank when it fits no known form.'''
    if not isinstance(identifier, str) or '-' not in identifier:
        return '', ''
    name, tail = identifier.rsplit('-', 1)
    if kind == 1 and _BSSID.fullmatch(tail):
        return name, ':'.join(octet.zfill(2) for octet in tail.split(':')).upper()
    if kind == 2 and tail.isascii() and tail.isdigit():
        return name, tail
    return '', ''

def _find_netusage_db(context, required_tables):
    '''Returns the first netusage.sqlite that contains all required tables.
    Some extractions hold additional netusage.sqlite copies (e.g. an empty
    stub under /private/var/tmp) that must not be picked over the real one.'''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('netusage.sqlite'):
            continue
        if all(does_table_exist_in_db(file_found, table) for table in required_tables):
            return file_found
        logfunc(f'Skipping {file_found}: missing one of the tables {", ".join(required_tables)}')
    return ''

@artifact_processor
def netusage_appdata(context):
    data_headers = (('Live Usage Timestamp', 'datetime'), ('Process First Usage Timestamp', 'datetime'), ('Process Timestamp', 'datetime'), 'Bundle Name',
                    'Process Name', 'ZKIND (as stored)', 'Wifi In (Bytes)', 'Wifi Out (Bytes)', 'Mobile/WWAN In (Bytes)',
                    'Mobile/WWAN Out (Bytes)', 'Wired In (Bytes)',
                    'Wired Out (Bytes)')
    data_list = []

    data_source = _find_netusage_db(context, ('ZLIVEUSAGE', 'ZPROCESS'))
    if data_source:
        all_rows = get_sqlite_db_records(data_source, '''
                select
                ZLIVEUSAGE.ZTIMESTAMP,
                ZPROCESS.ZFIRSTTIMESTAMP,
                ZPROCESS.ZTIMESTAMP,
                ZPROCESS.ZBUNDLENAME,
                ZPROCESS.ZPROCNAME,
                ZLIVEUSAGE.ZKIND,
                ZLIVEUSAGE.ZWIFIIN,
                ZLIVEUSAGE.ZWIFIOUT,
                ZLIVEUSAGE.ZWWANIN,
                ZLIVEUSAGE.ZWWANOUT,
                ZLIVEUSAGE.ZWIREDIN,
                ZLIVEUSAGE.ZWIREDOUT
                from ZLIVEUSAGE
                left join ZPROCESS on ZPROCESS.Z_PK = ZLIVEUSAGE.ZHASPROCESS
            ''')

        for row in all_rows:
            lastconnected = convert_cocoa_core_data_ts_to_utc(row[0])
            firstused = convert_cocoa_core_data_ts_to_utc(row[1])
            try:
                lastused = convert_cocoa_core_data_ts_to_utc(row[2])
            except (OSError):
                lastused = None

            data_list.append((lastconnected,firstused,lastused,row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]))

    return data_headers, data_list, data_source



@artifact_processor
def netusage_connections(context):
    data_headers = (('Attachment First Timestamp', 'datetime'), ('Attachment Timestamp', 'datetime'),
                    ('Route Performance Timestamp', 'datetime'), 'Network Name', 'BSSID or Cell ID',
                    'Network Type', 'Identifier (as stored)', 'Bytes In', 'Bytes Out', 'Connection Attempts',
                    'Connection Successes', 'Packets In', 'Packets Out')
    data_list = []
    network_types = {1: 'Wi-Fi', 2: 'Cellular'}

    data_source = _find_netusage_db(context, ('ZNETWORKATTACHMENT', 'ZLIVEROUTEPERF'))
    if data_source:
        all_rows = get_sqlite_db_records(data_source, '''
                select
                ZNETWORKATTACHMENT.ZFIRSTTIMESTAMP,
                ZNETWORKATTACHMENT.ZTIMESTAMP,
                ZLIVEROUTEPERF.ZTIMESTAMP,
                ZNETWORKATTACHMENT.ZIDENTIFIER,
                ZNETWORKATTACHMENT.ZKIND,
                ZLIVEROUTEPERF.ZBYTESIN,
                ZLIVEROUTEPERF.ZBYTESOUT,
                ZLIVEROUTEPERF.ZCONNATTEMPTS,
                ZLIVEROUTEPERF.ZCONNSUCCESSES,
                ZLIVEROUTEPERF.ZPACKETSIN,
                ZLIVEROUTEPERF.ZPACKETSOUT
                from ZNETWORKATTACHMENT
                left join ZLIVEROUTEPERF on ZLIVEROUTEPERF.ZHASNETWORKATTACHMENT = ZNETWORKATTACHMENT.Z_PK
                ''')

        for row in all_rows:
            name, address = _split_identifier(row[3], row[4])
            data_list.append((convert_cocoa_core_data_ts_to_utc(row[0]),
                              convert_cocoa_core_data_ts_to_utc(row[1]),
                              convert_cocoa_core_data_ts_to_utc(row[2]),
                              name, address, network_types.get(row[4], row[4]),
                              row[3] if row[3] is not None else '',
                              row[5], row[6], row[7], row[8], row[9], row[10]))

    return data_headers, data_list, data_source
