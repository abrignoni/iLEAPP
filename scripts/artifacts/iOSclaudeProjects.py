__artifacts_v2__ = {
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
    convert_human_ts_to_utc
)

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