__artifacts_v2__ = {
    "iOSclaudeConversations": {
        "name": "Claude Conversations",
        "description": "Parses Claude Conversations",
        "author": "Brandon Baye",
        "creation_date": "2026-07-23",
        "last_updated_date": "2026-08-06",
        "requirements": "none",
        "category": "Claude",
        "notes": "Data marked as incognito conversation will not reference a conversation name, will remain blank"
                 "test data created with iOS 26",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/ClaudeCache/cache_*.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
    }
}

from scripts.ilapfuncs import (
    artifact_processor,
    get_file_path,
    get_sqlite_db_records,
    convert_human_ts_to_utc
)

@artifact_processor
def iOSclaudeConversations(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "cache_*.sqlite")
    data_list = []
    
    query = '''
    SELECT
        conversations.createdAT AS 'Conversation Start Time',
        conversations.updatedAT AS 'Conversation Updated Time',
        conversations.id AS 'Conversation ID',
        conversations.name AS 'Conversation Name',
        conversations.model AS 'Model',
        CASE conversations.isTemporary
            WHEN 0 THEN 'False'
            WHEN 1 THEN 'True'
            ELSE 'Unknown'
            END AS 'Incognito Conversation',
        CASE conversations.isStarred
            WHEN 0 THEN 'False'
            WHEN 1 THEN 'True'
            ELSE 'Unknown'
            END AS 'Conversation Starred'
    FROM conversations
    '''
            
    records = get_sqlite_db_records(source_path, query)
    for record in records:
        createdAT = convert_human_ts_to_utc(
            record[0]
        ) if record[0] else None
            
        updatedAT = convert_human_ts_to_utc(
            record[1]
        ) if record[1] else None
                
        data_list.append((
            createdAT,
            updatedAT,
            record[2],
            record[3],
            record[4],
            record[5],
            record[6]
        ))
        
    data_headers = (
        ('Conversation Start Time', 'datetime'),
        ('Conversation Updated Time', 'datetime'),
        'Conversation ID',
        'Conversation Name',
        'Model',
        'Incognito Conversation',
        'Conversation Starred'
    )

    return data_headers, data_list, source_path