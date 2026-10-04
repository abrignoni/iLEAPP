__artifacts_v2__ = {
    "iOSclaudeAccountInfo": {
        "name": "Claude Account Information",
        "description": "Parses the account information for the Claude app",
        "author": "Brandon Baye",
        "creation_date": "2026-07-24",
        "last_update_date": "2026-08-09",
        "requirements": "none",
        "category": "Claude",
        "notes": "Timestamps are stored as ISO 8601 text ending in Z and are reported as UTC. "
                 "Only the first bootstrap JSON that holds an account object is read. "
                 "On the test data created with iOS 26, the update time changed when the account "
                 "name was changed. "
                 "Test data created with iOS 26.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/bootstrap/*.json'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "hc_ios26": "iOS 26.5.2 | 1 row",
        },
    },

    "iOSclaudeConversations": {
        "name": "Claude Conversations",
        "description": "Parses Claude Conversations",
        "author": "Brandon Baye",
        "creation_date": "2026-07-23",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Claude",
        "notes": "The Is Temporary column is the conversations.isTemporary value: 0 is shown as False "
                 "and 1 as True. What the app sets it for is not established here. On hc_ios26 the one"
                 " row with isTemporary set to 1 carried no conversation name, so that column is blank"
                 " for it; the other 6 rows there and both rows on hc_ios18_7 hold 0. Every "
                 "cache_*.sqlite the paths match is read, and the Source File column names the file "
                 "each row came from; each of the two tested images holds one such file, so reading "
                 "more than one was exercised only on constructed copies. Test data created with iOS "
                 "26.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/ClaudeCache/cache_*.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 2 rows",
            "hc_ios26": "iOS 26.5.2 | 7 rows",
        },
    },

    "iOSclaudeMessages": {
        "name": "Claude Messages",
        "description": "Parses Claude messages with the conversation name and id. The file name shown is that of the first file attached to the message.",
        "author": "Brandon Baye",
        "creation_date": "2026-07-21",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Claude",
        "notes": "The Message column joins the text of the blocks of type 'text' in the "
                 "message's content array; blocks of any other type are not reported. "
                 "On the test data the response was stored as a message whose sender is "
                 "assistant. The path containing "
                 "uploaded image files was empty on the test data. The conversation title is "
                 "joined to each message for context. "
                 "Every cache_*.sqlite the paths match is read, and the Source File column names the "
                 "file each row came from; each of the two tested images holds one such file, so "
                 "reading more than one was exercised only on constructed copies. Test data created "
                 "with iOS 26.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/ClaudeCache/cache_*.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 10 rows",
            "hc_ios26": "iOS 26.5.2 | 30 rows",
        },
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
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Claude",
        "notes": "One row is reported per project document, with the document's file name; a project "
                 "with no row in projectDocuments is listed once with that column blank. On hc_ios26 "
                 "the one project holds one document; hc_ios18_7 holds no project. The blank-document "
                 "row was exercised only on a constructed copy with the document row removed. Every "
                 "cache_*.sqlite the paths match is read, and the Source File column names the file "
                 "each row came from; each of the two tested images holds one such file, so reading "
                 "more than one was exercised only on constructed copies. Test data created with iOS "
                 "26.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/ClaudeCache/cache_*.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 1 row",
        },
    }
}

from pathlib import Path

from scripts.ilapfuncs import (
    artifact_processor, 
    get_sqlite_db_records,
    json,
    convert_human_ts_to_utc
)

def _cache_databases(files_found):
    # One cache_<id>.sqlite can exist per app container, and the paths also
    # match its -wal and -shm files. Return each database once, in path order.
    return sorted({
        str(file_found) for file_found in files_found
        if Path(str(file_found)).match('cache_*.sqlite')
    })

@artifact_processor
def iOSclaudeAccountInfo(context):
    files_found = context.get_files_found()
    data_list = []

    # iOS application containers are UUID-named, so the bootstrap glob cannot
    # be anchored to the Claude app; another app shipping a Library/Caches/
    # bootstrap directory would match too. Select by content: the first json
    # that carries an account object. On the two corpus images tested only
    # the Claude app has bootstrap jsons, so this changes nothing there.
    source_path = None
    account = None
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('.json'):
            continue
        try:
            with open(file_found, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (OSError, ValueError):
            continue
        if isinstance(data, dict) and isinstance(data.get('account'), dict):
            source_path = file_found
            account = data['account']
            break

    if account is None:
        return (
            ('Account Created Time', 'datetime'),
            ('Account Updated Time', 'datetime'),
            'Full Name',
            'Display Name',
            'Email Address',
            'Tagged ID'
        ), data_list, ''

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
    source_paths = _cache_databases(files_found)
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
            END AS 'Is Temporary',
        CASE conversations.isStarred
            WHEN 0 THEN 'False'
            WHEN 1 THEN 'True'
            ELSE 'Unknown'
            END AS 'Conversation Starred'
    FROM conversations
    '''
            
    for source_path in source_paths:
        source_file = context.get_relative_path(source_path)
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
                record[6],
                source_file
            ))

    data_headers = (
        ('Conversation Start Time', 'datetime'),
        ('Conversation Updated Time', 'datetime'),
        'Conversation ID',
        'Conversation Name',
        'Model',
        'Is Temporary',
        'Conversation Starred',
        'Source File'
    )

    return data_headers, data_list, '\n'.join(source_paths)

@artifact_processor
def iOSclaudeMessages(context):
    files_found = context.get_files_found()
    source_paths = _cache_databases(files_found)
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
    LEFT JOIN conversations ON conversations.id = messages.conversationId
    '''
            
    for source_path in source_paths:
        source_file = context.get_relative_path(source_path)
        records = get_sqlite_db_records(source_path, query)
        for record in records:
            createdAT = convert_human_ts_to_utc(
                record[0]
            ) if record[0] else None           

            data_list.append((
                createdAT,
                record[3],
                record[4],
                record[1],
                record[2],
                record[5],
                source_file
            ))

    data_headers = (
        ('Message Created Time', 'datetime'),
        'Message Sender',
        'Conversation Name',
        'Message',
        'Image File Name',
        'Conversation ID',
        'Source File',
    )

    return data_headers, data_list, '\n'.join(source_paths)

@artifact_processor
def iOSclaudeProjects(context):
    files_found = context.get_files_found()
    source_paths = _cache_databases(files_found)
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
    LEFT JOIN projectDocuments on projectDocuments.projectId = projects.id
    '''
    
    for source_path in source_paths:
        source_file = context.get_relative_path(source_path)
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
                record[7],
                source_file
            ))

    data_headers = (
        ('Project Created Time', 'datetime'),
        ('Project Updated Time', 'datetime'),
        'Project Name',
        'Project Description',
        'Project Creator',
        'Project Starred',
        'Number of Documents',
        'Document File Name(s)',
        'Source File'
    )
    
    return data_headers, data_list, '\n'.join(source_paths)