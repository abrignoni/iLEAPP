__artifacts_v2__ = {
    "netusage_appdata": {
        "name": "App Data",
        "description": "Parses app data from netusage.sqlite",
        "author": "@stark4n6, @snoop168",
        "creation_date": "2023-02-13",
        "last_update_date": "2026-01-17",
        "requirements": "none",
        "category": "Network Usage",
        "notes": "",
        "paths": ('*/netusage.sqlite*'),
        "output_types": "standard",
    },
    "netusage_connections": {
        "name": "Connections",
        "description": "Parses connections from netusage.sqlite",
        "author": "@stark4n6, @snoop168",
        "creation_date": "2023-02-13",
        "last_update_date": "2026-01-17",
        "requirements": "none",
        "category": "Network Usage",
        "notes": "",
        "paths": ('*/netusage.sqlite*'),
        "output_types": "standard",
    }
}

from scripts.ilapfuncs import open_sqlite_db_readonly, artifact_processor, convert_cocoa_core_data_ts_to_utc

def pad_mac_adr(adr):
    return ':'.join([i.zfill(2) for i in adr.split(':')]).upper()

@artifact_processor
def netusage_appdata(context):
    data_source = context.get_source_file_path('netusage.sqlite')
    db = open_sqlite_db_readonly(data_source)
    cursor = db.cursor()
    cursor.execute('''
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

    all_rows = cursor.fetchall()
    data_headers = (('Live Usage Timestamp', 'datetime'), ('Process First Usage Timestamp', 'datetime'), ('Process Timestamp', 'datetime'), 'Bundle Name',
                    'Process Name', 'Type', 'Wifi In (Bytes)', 'Wifi Out (Bytes)', 'Mobile/WWAN In (Bytes)',
                    'Mobile/WWAN Out (Bytes)', 'Wired In (Bytes)',
                    'Wired Out (Bytes)')

    if len(all_rows) > 0:
        data_list = []
        for row in all_rows:
            lastconnected = convert_cocoa_core_data_ts_to_utc(row[0])
            firstused = convert_cocoa_core_data_ts_to_utc(row[1])
            lastused = convert_cocoa_core_data_ts_to_utc(row[2])

            data_list.append((lastconnected,firstused,lastused,row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]))

        db.close()

        return data_headers, data_list, data_source



@artifact_processor
def netusage_connections(context):
    data_source = context.get_source_file_path('netusage.sqlite')
    db = open_sqlite_db_readonly(data_source)
    cursor = db.cursor()
    cursor.execute('''
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

    all_rows = cursor.fetchall()
    data_headers = (('First Connection Timestamp', 'datetime'), ('Last Connection Timestamp', 'datetime'), 'Network Name', 'Cell Tower ID/Wifi MAC',
                    'Network Type', 'Bytes In', 'Bytes Out', 'Connection Attempts', 'Connection Successes',
                    'Packets In',
                    'Packets Out')
    if len(all_rows) > 0:
        data_list = []
        for row in all_rows:
            first_connected = convert_cocoa_core_data_ts_to_utc(row[0])
            last_connected = convert_cocoa_core_data_ts_to_utc(row[1])

            if row[2] == None:
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

        db.close()

        return data_headers, data_list, data_source
