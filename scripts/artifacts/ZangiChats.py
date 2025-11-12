# Update line 3-13
__artifacts_v2__ = {
    "get_zangichats": {
        "name": "Zangi Chats",
        "description": "Parses Zangi Chat database",
        "author": "Matt Beers",
        "creation_date": "2024-04-16",
        "last_update_date": "2025-11-12",
        "requirements": "none",
        "category": "Chats",
        "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/zangidb.sqlite*'),
        "output_types": "standard",
        "artifact_icon": ""
    }
}

from scripts.ilapfuncs import (
    open_sqlite_db_readonly,
    artifact_processor,
    convert_cocoa_core_data_ts_to_utc
    )


@artifact_processor
def get_zangichats(context):  # your def variable should match what you have after function on line 13.
    data_list = []
    files_found = context.get_files_found()
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('zangidb.sqlite'):  # put the database name here
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            select
                ZZANGIMESSAGE.ZMESSAGETIME,
                ZCONTACT.ZFIRSTNAME,
                ZCONTACT.ZLASTNAME,
                ZZANGIMESSAGE.ZMESSAGE,
                CASE ZZANGIMESSAGE.ZISRECEIVED
                WHEN '0' THEN 'SENT'
                WHEN '1' THEN 'RECEIVED'
                ELSE 'unknown'
                END AS DIRECTION,
                ZZNUMBER.ZNUMBER
                FROM ZZANGIMESSAGE
                JOIN ZZNUMBER ON ZZANGIMESSAGE.ZFROM = ZZNUMBER.ZCONTACTNUMBEROBJECT
                left JOIN ZCONTACT ON ZZNUMBER.ZIDENTIFIRE = ZCONTACT.ZIDENTIFIRE
                order by ZZANGIMESSAGE.ZMESSAGETIME DESC;--
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                   # last_mod_date = row[0]
                   # if last_mod_date is None:
                   # pass
                   # else:
                   # last_mod_date = convert_utc_human_to_timezone(convert_ts_human_to_utc(last_mod_date),time_offset)
                    timestamp = convert_cocoa_core_data_ts_to_utc(row[0])
                    data_list.append((
                        timestamp,
                        row[1],
                        row[2],
                        row[3],
                        row[4],
                        row[5],
                        file_found
                        ))
            db.close()
        else:
            continue
    data_headers = (
        ('Timestamp', 'datetime'),
        'First Name',
        'Last Name',
        'Message Text',
        'Direction',
        'Number',
        'Filename',
        )
    return data_headers, data_list, 'See filename column for source database'
