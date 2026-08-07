__artifacts_v2__ = {
    "iOSclaudeMessages": {
        "name": "Claude Messages",
        "description": "Parses Claude Messages with some conversations info",
        "author": "Brandon Baye",
        "creation_date": "2026-07-21",
        "last_updated_date": "2026-08-06",
        "requirements": "none",
        "category": "Claude",
        "notes": "json each utilized in circumstances that background searches by AI were performed"
                 "each source utilized in final response was stored within json"
                 "final response is shown as message by assistant"
                 "path containing image files uploaded remained empty"
                 "context of conversation title joined to show when messages cannot be followed in order when user switches between stored conversations"
                 "test data created with iOS 26",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/ClaudeCache/cache_*.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation ID",
                "conversationLabelColumn": "Conversation Name",
                "textColumn": "Message",
                "directionColumn": "Message Sender",
                "directionSentValue": "human",
                "timeColumn": "Message Created Time",
                "senderColumn": "Message Sender",
            }
        }
    }
}

from scripts.ilapfuncs import (
    artifact_processor, 
    get_file_path, 
    get_sqlite_db_records, 
    convert_human_ts_to_utc
)

@artifact_processor
def iOSclaudeMessages(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "cache_*.sqlite")
    data_list = []
    
    query = '''
    SELECT
        messages.createdAT AS 'Message Created Time',
        (		
			SELECT group_concat(json_extract(je.value, '$.text'), ' ')
			FROM json_each(messages.content) je
			WHERE json_extract(je.value, '$.type') = 'text'
		) as 'Message',
        json_extract(messages.files, '$[0].fileName') AS 'Image File Name',
        sender AS 'Message Sender',
        conversations.name AS 'Conversation Name',
        conversations.id AS 'Conversation ID'
    FROM messages
    JOIN conversations ON conversations.id = messages.conversationId
    '''
            
    records = get_sqlite_db_records(source_path, query)
    for record in records:   
        createdAT = convert_human_ts_to_utc(
            record[0]
        ) if record[0] else None           
        
        data_list.append((
            createdAT, 
            record[1], 
            record[2], 
            record[3], 
            record[4],
            record[5]
        ))
        
    data_headers = (
        ('Message Created Time', 'datetime'),
        'Message',
        'Image File Name',
        'Message Sender',
        'Conversation Name',
        'Conversation ID',
    )

    return data_headers, data_list, source_path