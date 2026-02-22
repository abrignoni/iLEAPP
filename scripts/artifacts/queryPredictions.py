from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_queryPredictions(files_found, report_folder, seeker, wrap_text, timezone_offset):
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select
    datetime(creationTimestamp, "UNIXEPOCH") as START,
    content,
    isSent,
    conversationId,
    id,
    uuid
    from messages
    ''')
    all_rows = cursor.fetchall()
    data_list = []
    for row in all_rows:
        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))

    db.close()

    data_headers = ('Timestamp', 'Content', 'Is Sent?', 'Conversation ID', 'ID', 'UUID')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_queryPredictions": {
        "name": "SMS & iMessage",
        "description": "",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "SMS & iMessage",
        "notes": "",
        "paths": ('**/query_predictions.db',),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}
