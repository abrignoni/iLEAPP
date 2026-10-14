__artifacts_v2__ = {
    "netusage_appdata": {
        "name": "App Data",
        "description": "Parses app data from netusage.sqlite",
        "author": "@stark4n6, @snoop168",
        "creation_date": "2023-02-13",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Network Usage",
        "notes": "ZKIND is reported as stored; its values are not documented. The three timestamps "
                 "are ZLIVEUSAGE.ZTIMESTAMP, ZPROCESS.ZFIRSTTIMESTAMP and ZPROCESS.ZTIMESTAMP read "
                 "as seconds from 2001-01-01 UTC; what each marks is not sourced. Only the first "
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
        "name": "Connections",
        "description": "Network attachments and their route performance counters from netusage.sqlite",
        "author": "@stark4n6, @snoop168",
        "creation_date": "2023-02-13",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Network Usage",
        "notes": "One row per ZLIVEROUTEPERF row linked to a network. The byte, packet and connection "
                 "columns are joined to their network through ZLIVEROUTEPERF.ZHASNETWORKATTACHMENT = "
                 "ZNETWORKATTACHMENT.Z_PK, the join the reference below uses. The Core Data model "
                 "cached in the dexter_ios18 store (Z_MODELCACHE) defines hasNetworkAttachment as a "
                 "to-one relationship from LiveRoutePerf to NetworkAttachment. A network with more "
                 "than one linked ZLIVEROUTEPERF row is listed once per linked row, with the network "
                 "columns repeated; a network with none would be listed once with those columns empty. "
                 "Measured on the 14 listed images that hold the tables: all 9,266 ZLIVEROUTEPERF "
                 "rows carried a link, each link named an existing network, and each of the 8,722 "
                 "networks had one to three linked rows (531 had more than one). Before 2026-10-04 "
                 "this artifact paired the two tables by their own row numbers (Z_PK of both), which "
                 "filled the counters on 3,234 of 8,722 rows on those images, 152 of them from a "
                 "linked row. Route Performance Timestamp is ZLIVEROUTEPERF.ZTIMESTAMP read as seconds "
                 "from 2001-01-01 UTC; what it marks is not sourced. Network Type is mapped from "
                 "ZNETWORKATTACHMENT.ZKIND (1 Wifi, 2 Cellular); the reference maps "
                 "ZLIVEROUTEPERF.ZKIND, and the two held the same value on all 9,266 linked pairs. "
                 "The first two timestamp columns are ZNETWORKATTACHMENT.ZFIRSTTIMESTAMP and "
                 "ZTIMESTAMP; the reference labels them first network attachment and network "
                 "attachment timestamp. Only the first netusage.sqlite that holds both tables is "
                 "read. Reference: Sarah Edwards, APOLLO netusage_zliverouteperf module, "
                 "https://github.com/mac4n6/APOLLO/blob/bd725461fbd22c8ceadd04f0c4ded49b66147439/modules/netusage_zliverouteperf.txt",
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
            "felix23_ios16": "iOS 16.5 | 366 rows",
            "hickman_ios13": "iOS 13.3.1 | 52 rows",
            "hickman_ios14": "iOS 14.3 | 49 rows",
            "jess_ios15": "iOS 15.0.2 | 240 rows",
            "magnet_ios16": "iOS 16.1.1 | 17 rows",
        },
    }
}

from scripts.ilapfuncs import (artifact_processor, get_sqlite_db_records, does_table_exist_in_db,
                               convert_cocoa_core_data_ts_to_utc, logfunc)

def pad_mac_adr(adr):
    return ':'.join([i.zfill(2) for i in adr.split(':')]).upper()

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
    data_headers = (('First Connection Timestamp', 'datetime'), ('Last Connection Timestamp', 'datetime'),
                    ('Route Performance Timestamp', 'datetime'), 'Network Name', 'Network Identifier',
                    'Network Type', 'Bytes In', 'Bytes Out', 'Connection Attempts', 'Connection Successes',
                    'Packets In',
                    'Packets Out')
    data_list = []

    data_source = _find_netusage_db(context, ('ZNETWORKATTACHMENT', 'ZLIVEROUTEPERF'))
    if data_source:
        all_rows = get_sqlite_db_records(data_source, '''
                select
                ZNETWORKATTACHMENT.ZFIRSTTIMESTAMP,
                ZNETWORKATTACHMENT.ZTIMESTAMP,
                ZNETWORKATTACHMENT.ZIDENTIFIER,
                case ZNETWORKATTACHMENT.ZKIND
                    when 1 then 'Wifi'
                    when 2 then 'Cellular'
                    else ZNETWORKATTACHMENT.ZKIND
                end,
                ZLIVEROUTEPERF.ZBYTESIN,
                ZLIVEROUTEPERF.ZBYTESOUT,
                ZLIVEROUTEPERF.ZCONNATTEMPTS,
                ZLIVEROUTEPERF.ZCONNSUCCESSES,
                ZLIVEROUTEPERF.ZPACKETSIN,
                ZLIVEROUTEPERF.ZPACKETSOUT,
                ZLIVEROUTEPERF.ZTIMESTAMP
                from ZNETWORKATTACHMENT
                left join ZLIVEROUTEPERF on ZLIVEROUTEPERF.ZHASNETWORKATTACHMENT = ZNETWORKATTACHMENT.Z_PK
                ''')

        for row in all_rows:
            first_connected = convert_cocoa_core_data_ts_to_utc(row[0])
            last_connected = convert_cocoa_core_data_ts_to_utc(row[1])
            perf_timestamp = convert_cocoa_core_data_ts_to_utc(row[10])

            if row[2] is None:
                data_list.append((first_connected, last_connected, perf_timestamp, '', '', row[3], row[4], row[5], row[6], row[7],
                                  row[8], row[9]))
            else:
                if '-' not in row[2]:
                    data_list.append((first_connected, last_connected, perf_timestamp, row[2], '', row[3], row[4], row[5], row[6],
                                      row[7],row[8],row[9]))
                else:
                    id_split = row[2].rsplit('-',1)
                    netname = id_split[0]
                    id_mac = pad_mac_adr(id_split[1])

                    data_list.append((first_connected, last_connected, perf_timestamp, netname, id_mac, row[3], row[4], row[5], row[6],
                                      row[7], row[8], row[9]))

    return data_headers, data_list, data_source
