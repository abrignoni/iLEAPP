__artifacts_v2__ = {
    "netusage_appdata": {
        "name": "App Data",
        "description": "Parses app data from netusage.sqlite",
        "author": "@stark4n6, @snoop168",
        "creation_date": "2023-02-13",
        "last_update_date": "2026-07-10",
        "requirements": "none",
        "category": "Network Usage",
        "notes": "",
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
        },
    },
    "netusage_connections": {
        "name": "Connections",
        "description": "Parses connections from netusage.sqlite",
        "author": "@stark4n6, @snoop168",
        "creation_date": "2023-02-13",
        "last_update_date": "2026-07-10",
        "requirements": "none",
        "category": "Network Usage",
        "notes": "",
        "paths": ('*/netusage.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "network",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 518 rows",
            "dexter_ios18": "iOS 18.3.2 | 1457 rows",
            "felix_ios17": "iOS 17.6.1 | 974 rows",
            "fsfull002_ios17": "iOS 17.1 | 4 rows",
            "hc_ios18_7": "iOS 18.7.8 | 430 rows",
            "iphone11_ios17": "iOS 17.3 | 1232 rows",
            "iphone12_ios18": "iOS 18.7 | 287 rows",
            "iphone14plus_ios18": "iOS 18.0 | 16 rows",
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
                    'Process Name', 'Type', 'Wifi In (Bytes)', 'Wifi Out (Bytes)', 'Mobile/WWAN In (Bytes)',
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
                case ZLIVEUSAGE.ZKIND
                    when 0 then 'Process'
                    when 1 then 'App'
                end,
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
            lastused = convert_cocoa_core_data_ts_to_utc(row[2])

            data_list.append((lastconnected,firstused,lastused,row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]))

    return data_headers, data_list, data_source



@artifact_processor
def netusage_connections(context):
    data_headers = (('First Connection Timestamp', 'datetime'), ('Last Connection Timestamp', 'datetime'), 'Network Name', 'Cell Tower ID/Wifi MAC',
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
                end,
                ZLIVEROUTEPERF.ZBYTESIN,
                ZLIVEROUTEPERF.ZBYTESOUT,
                ZLIVEROUTEPERF.ZCONNATTEMPTS,
                ZLIVEROUTEPERF.ZCONNSUCCESSES,
                ZLIVEROUTEPERF.ZPACKETSIN,
                ZLIVEROUTEPERF.ZPACKETSOUT
                from ZNETWORKATTACHMENT
                left join ZLIVEROUTEPERF on ZLIVEROUTEPERF.Z_PK = ZNETWORKATTACHMENT.Z_PK
                ''')

        for row in all_rows:
            first_connected = convert_cocoa_core_data_ts_to_utc(row[0])
            last_connected = convert_cocoa_core_data_ts_to_utc(row[1])

            if row[2] is None:
                data_list.append((first_connected, last_connected, '', '', row[3], row[4], row[5], row[6], row[7],
                                  row[8], row[9]))
            else:
                if '-' not in row[2]:
                    data_list.append((first_connected, last_connected, row[2], '', row[3], row[4], row[5], row[6],
                                      row[7],row[8],row[9]))
                else:
                    id_split = row[2].rsplit('-',1)
                    netname = id_split[0]
                    id_mac = pad_mac_adr(id_split[1])

                    data_list.append((first_connected, last_connected , netname, id_mac, row[3], row[4], row[5], row[6],
                                      row[7], row[8], row[9]))

    return data_headers, data_list, data_source
