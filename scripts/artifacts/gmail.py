__artifacts_v2__ = {
    "gmailOfflineSearch": {
        "name": "Gmail - Offline Search",
        "description": "Parses Gmail offline search content",
        "author": "@KevinPagano3",
        "version": "0.0.2",
        "date": "2024-03-20",
        "requirements": "none",
        "category": "Gmail",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/data/*/searchsqlitedb*',),
        "output_types": ["html", "tsv", "lava", "timeline"]
    },
    "gmailLabelDetails": {
        "name": "Gmail - Label Details",
        "description": "Parses Gmail label details",
        "author": "@KevinPagano3",
        "version": "0.0.2",
        "date": "2024-03-20",
        "requirements": "none",
        "category": "Gmail",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/data/*/sqlitedb*',),
        "output_types": ["html", "tsv", "lava"]
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, logfunc, convert_ts_human_to_timezone_offset

@artifact_processor
def gmailOfflineSearch(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    data_headers = ()
    source_path = ''
    
    for file_found in files_found:
        source_path = str(file_found)
        if file_found.endswith('searchsqlitedb'):
            break

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()

    cursor.execute('''
    SELECT
        datetime(c0/1000,'unixepoch'),
        c3 AS 'Sender',
        c4 AS 'Receiver',
        c5 AS 'CC',
        c6 AS 'BCC',
        c7 AS 'Subject',
        c8 AS 'Body',
        c1 AS 'Thread ID',
        c2 AS 'Message ID'
    FROM offline_search_content
    ''')
    
    all_rows = cursor.fetchall()
        
    for row in all_rows:
        timestamp = convert_ts_human_to_timezone_offset(row[0], timezone_offset)

        sender = row[1]
        sender_split = [sender_split.strip() for sender_split in sender.split(',')]
        
        if len(sender_split) < 2:
            sender_title = sender_split[0]
            sender_email = ''
        else:
            sender_title = sender_split[0]
            sender_email = sender_split[1]

        data_list.append((timestamp, sender_title, sender_email, row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
        
    db.close()
    
    data_headers = (
        ('Timestamp', 'datetime'), 
        'Sender Name', 
        'Sender Email', 
        'Receiver', 
        'CC', 
        'BCC', 
        'Subject', 
        'Body', 
        'Thread ID', 
        'Message ID'
    )
    
    return data_headers, data_list, source_path

@artifact_processor
def gmailLabelDetails(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    data_headers = ()
    source_path = ''
    
    for file_found in files_found:
        source_path = str(file_found)
        if file_found.endswith('sqlitedb'):
            break

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    
    cursor.execute('''
    SELECT
        label_server_perm_id,
        unread_count,
        total_count,
        unseen_count
    FROM label_counts
    ORDER BY label_server_perm_id
    ''')
    
    all_rows = cursor.fetchall()
    
    for row in all_rows:
        data_list.append((row[0], row[1], row[2], row[3]))
    
    db.close()
    
    data_headers = ('Label', 'Unread Count', 'Total Count', 'Unseen Count')
    
    return data_headers, data_list, source_path
