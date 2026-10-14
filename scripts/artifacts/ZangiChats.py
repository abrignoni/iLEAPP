# Update line 3-13
__artifacts_v2__ = {
    "get_zangichats": {
        "name": "Zangi Chats",
        "description": "Messages from the ZZANGIMESSAGE table of zangidb.sqlite, with the name and number of the ZZNUMBER row the message's ZFROM value points to. Direction is SENT when ZISRECEIVED is 0 and RECEIVED when it is 1; no source for that reading is recorded here.",
        "author": "Matt Beers",
        "creation_date": "2024-04-16",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Chats",
        "notes": "Only a file named zangidb.sqlite is read. ZFROM First Name, ZFROM Last Name and "
                 "ZFROM Number come from the ZZNUMBER row whose ZCONTACTNUMBEROBJECT equals the "
                 "message's ZFROM value, and from the ZCONTACT row holding the same ZIDENTIFIRE "
                 "text as that ZZNUMBER row, on sent and received rows alike. The Core Data model "
                 "shipped with the app on iphone14plus_ios18 (zangidb 7.7.mom) defines ZFROM as a "
                 "to-one relationship to ContactNumber and gives a ContactNumber any number of "
                 "ZNumber rows, so a message is listed once per matching ZZNUMBER row, and a "
                 "message with no matching row is listed once with those three columns blank. "
                 "iphone14plus_ios18 holds no file named zangidb.sqlite; other images were not "
                 "checked. Measured on a scratch copy of the zangidb_<number>.sqlite store of "
                 "that image, which holds the same tables: all 19 messages, 10 with ZISRECEIVED 0 and 9 with 1, carried "
                 "one ZFROM value, so on the 10 sent rows the three ZFROM columns name the other "
                 "party and not the sender; each message matched one ZZNUMBER row, and ZCONTACT "
                 "was empty, so both name columns were blank. Source File holds the database "
                 "path.",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/zangidb.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "ZFROM Number",
                "textColumn": "Message Text",
                "directionColumn": "Direction",
                "directionSentValue": "SENT",
                "timeColumn": "Timestamp",
                "senderColumn": "ZFROM First Name",
                "sentMessageStaticLabel": "Local User"
            }
        },
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
    source_files = set()
    files_found = context.get_files_found()
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('zangidb.sqlite'):  # put the database name here
            source_files.add(file_found)
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
                LEFT JOIN ZZNUMBER ON ZZANGIMESSAGE.ZFROM = ZZNUMBER.ZCONTACTNUMBEROBJECT
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
                        row[4],
                        row[1],
                        row[3],
                        row[2],
                        row[5],
                        context.get_relative_path(file_found),
                        ))
            db.close()
        else:
            continue
    data_headers = (
        ('Timestamp', 'datetime'),
        'Direction',
        'ZFROM First Name',
        'Message Text',
        'ZFROM Last Name',
        'ZFROM Number',
        'Source File',
        )
    return data_headers, data_list, '\n'.join(sorted(source_files))
