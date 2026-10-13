__artifacts_v2__ = {
    "queryPredictions": {
        "name": "Query Predictions",
        "description": "Rows of the messages table in query_predictions.db",
        "author": "@abrignoni; @AlexisBrignoni, Codex",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "SMS & iMessage",
        "notes": (
            "No sample data is recorded for this artifact, and its query has not been run against "
            "a real query_predictions.db. creationTimestamp is read as Unix seconds; this reading "
            "has not been checked against a real database. isSent (as stored) carries the selected "
            "database value without a sent or received interpretation. No conversation direction "
            "mapping is declared because the meaning of isSent has not been established. Only the "
            "first query_predictions.db found is read."
        ),
        "paths": ('**/query_predictions.db*',),
        "output_types": "standard",
        "artifact_icon": "message",
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records


@artifact_processor
def queryPredictions(context):
    data_headers = (('Timestamp', 'datetime'), 'isSent (as stored)', 'Content', 'Conversation ID', 'ID', 'UUID')
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
    SELECT datetime(creationTimestamp, 'unixepoch'), isSent, content, conversationId, id, uuid
    FROM messages
    '''
    for row in get_sqlite_db_records(source_path, query):
        data_list.append(tuple(row))

    return data_headers, data_list, context.get_relative_path(source_path)
