__artifacts_v2__ = {
    "queryPredictions": {
        "name": "Query Predictions",
        "description": "Message query predictions from query_predictions.db",
        "author": "",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-07-03",
        "requirements": "none",
        "category": "SMS & iMessage",
        "notes": "",
        "paths": ('**/query_predictions.db',),
        "output_types": "standard",
        "artifact_icon": "message",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation ID",
                "textColumn": "Content",
                "directionColumn": "Is Sent?",
                "directionSentValue": 1,
                "timeColumn": "Timestamp"
            }
        },
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records


@artifact_processor
def queryPredictions(context):
    data_headers = (('Timestamp', 'datetime'), 'Content', 'Is Sent?', 'Conversation ID', 'ID', 'UUID')
    data_list = []

    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('query_predictions.db'):
            source_path = file_found
            break
    if not source_path:
        return data_headers, data_list, ''

    query = '''
    SELECT datetime(creationTimestamp, 'unixepoch'), content, isSent, conversationId, id, uuid
    FROM messages
    '''
    for row in get_sqlite_db_records(source_path, query):
        data_list.append(tuple(row))

    return data_headers, data_list, context.get_relative_path(source_path)
