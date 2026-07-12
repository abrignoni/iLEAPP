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
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "search",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | Gmail - Email by Google 6.0.250915 | 176 rows",
            "iphone11_ios17": "iOS 17.3 | Gmail - Email by Google 6.0.231127 | 321 rows",
            "iphone14plus_ios18": "iOS 18.0 | Gmail - Email by Google 6.0.251201 | 18 rows",
            "otto_ios17": "iOS 17.5.1 | Gmail - Email by Google 6.0.240729 | 305 rows",
            "abe_ios16": "iOS 16.5 | Gmail - Email by Google 6.0.230528 | 430 rows",
            "jess_ios15": "iOS 15.0.2 | Gmail - Email by Google 6.0.211226 | 81 rows",
            "magnet_ios16": "iOS 16.1.1 | Gmail - Email by Google 6.0.221127 | 21 rows",
        }
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
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "tag",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | com.google.Gmail | 30 rows",
            "dexter_ios18": "iOS 18.3.2 | Gmail - Email by Google 6.0.250915 | 35 rows",
            "iphone11_ios17": "iOS 17.3 | Gmail - Email by Google 6.0.231127 | 31 rows",
            "iphone14plus_ios18": "iOS 18.0 | Gmail - Email by Google 6.0.251201 | 33 rows",
            "otto_ios17": "iOS 17.5.1 | Gmail - Email by Google 6.0.240729 | 33 rows",
            "abe_ios16": "iOS 16.5 | Gmail - Email by Google 6.0.230528 | 31 rows",
            "jess_ios15": "iOS 15.0.2 | Gmail - Email by Google 6.0.211226 | 30 rows",
            "magnet_ios16": "iOS 16.1.1 | Gmail - Email by Google 6.0.221127 | 28 rows",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_ts_human_to_timezone_offset

@artifact_processor
def gmailOfflineSearch(files_found, _report_folder, _seeker, _wrap_text, timezone_offset):
    data_list = []
    data_headers = ()
    source_path = ''
    
    file_found = ''
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
def gmailLabelDetails(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    data_list = []
    data_headers = ()
    source_path = ''
    
    file_found = ''
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
