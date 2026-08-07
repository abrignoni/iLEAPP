__artifacts_v2__ = {
    "iOSclaudeAccountInfo": {
        "name": "Claude Account Information",
        "description": "Parses the account information for the Claude app",
        "author": "Brandon Baye",
        "creation_date": "2026-07-24",
        "last_updated_date": "2026-08-06",
        "requirements": "none",
        "category": "Claude",
        "notes": "timestamp stored ISO 8601 combined date-time format"
                 "update time accurate with name changes tested"
                 "test data created with iOS 26",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/bootstrap/*.json'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
    },

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
    },

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
    },

    "iOSclaudeProjects": {
        "name": "Claude Projects",
        "description": "Parses projects made within Claude",
        "author": "Brandon Baye",
        "creation_date": "2026-07-28",
        "last_updated_date": "2026-08-06",
        "requirements": "none",
        "category": "Claude",
        "notes": "user can add previous chats to project to further store their work"
                 "documents added to project will store file name"
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
    json,
    convert_human_ts_to_utc
)

@artifact_processor
def iOSclaudeAccountInfo(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, '*.json')
    data_list = []
    
    with open(source_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    account = data['account']
    
    ts = account['created_at']
    ts = ts.replace('T', ' ').replace('Z', '')
    created_at = convert_human_ts_to_utc(ts)
    
    ts = account['updated_at']
    ts = ts.replace('T', ' ').replace('Z', '')
    updated_at = convert_human_ts_to_utc(ts)
    
    full_name = account['full_name']
    display_name = account['display_name']
    email = account['email_address']
    tagged_id = account['tagged_id']
       
    data_list.append((
        created_at,
        updated_at,
        full_name,
        display_name,
        email,
        tagged_id,
    ))
        
    data_headers = (
        ('Account Created Time', 'datetime'),
        ('Account Updated Time', 'datetime'),
        'Full Name',
        'Display Name',
        'Email Address',
        'Tagged ID'
    )
    
    return data_headers, data_list, source_path

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

@artifact_processor
def iOSclaudeProjects(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'cache_*.sqlite')
    data_list = []
    
    query = '''
    SELECT
        projects.createdAt AS 'Project Created Time',
        projects.updatedAt AS 'Project Updated Time',
        projects.name as 'Project Name',
        projects.description as 'Project Description',
        projects.creatorFullName as 'Project Creator',
        CASE projects.isStarred
            WHEN 0 THEN 'False'
            WHEN 1 THEN 'True'
            ELSE 'Unknown'
        END AS 'Project Starred',
        projects.docsCount as 'Number of Documents',
        projectDocuments.fileName as 'Document File Name(s)'
    FROM projects
    JOIN projectDocuments on projectID = projects.id
    '''
    
    records = get_sqlite_db_records(source_path, query)
    for record in records:
        created_at = convert_human_ts_to_utc(
            record[0]
            ) if record[0] else None
            
        updated_at = convert_human_ts_to_utc(
            record[1]
            ) if record[1] else None
        
        data_list.append((
            created_at,
            updated_at,
            record[2],
            record[3],
            record[4],
            record[5],
            record[6],
            record[7]
        ))
        
    data_headers = (
        ('Project Created Time', 'datetime'),
        ('Project Updated Time', 'datetime'),
        'Project Name',
        'Project Description',
        'Project Creator',
        'Project Starred',
        'Number of Documents',
        'Document File Name(s)'
    )
    
    return data_headers, data_list, source_path