from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_zangichats(files_found, report_folder, seeker, wrap_text, time_offset):
    data_list = []

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('zangidb.sqlite'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            select
            datetime(ZZANGIMESSAGE.ZMESSAGETIME+978307200, 'unixepoch') AS 'MESSAGE DATE/TIME',
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
            if len(all_rows) > 0:
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))
            db.close()

        else:
            continue

    data_headers = ('Timestamp', 'First Name', 'Last Name', 'Message Text', 'Direction', 'Number')
    return data_headers, data_list, str(files_found[0])

__artifacts_v2__ = {
    "get_zangichats": {
        "name": "Zangi Chats",
        "description": "Parses Zangi Chat database",
        "author": "Matt Beers",
        "version": "0.0.1",
        "date": "2024-04-16",
        "requirements": "none",
        "category": "Chats",
        "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/zangidb.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "message-square"
    }
}
