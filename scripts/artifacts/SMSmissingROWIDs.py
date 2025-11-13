__artifacts_v2__ = {
    "SMS_Missing_ROWIDs": {
        "name": "SMS - Missing ROWIDs",
        "description": "Parses missing ROWID values from the SMS.db, presents the number of missing rows, and provides timestamps for data rows before and after the missing data",
        "author": "@SQLMcGee for Metadata Forensics, LLC",
        "creation_date": "2023-03-20",
        "last_update_date": "2025-11-13",
        "requirements": "none",
        "category": "SMS & iMessage",
        "notes": "This query was the product of research completed by James McGee, Metadata Forensics, LLC, for 'Lagging for the Win', published by Belkasoft https://belkasoft.com/lagging-for-win, updated upon further research",
        "paths": ("*SMS/sms*"),
        "output_types": "standard",
        "artifact_icon": "message-circle"
    }
}

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, open_sqlite_db_readonly

@artifact_processor
def SMS_Missing_ROWIDs(context):
    """ See artifact description """
    data_source = context.get_source_file_path('sms.db')
    
    data_list = []
    
    query = '''
	WITH LastROWID AS (
        SELECT seq AS last_rowid
        FROM sqlite_sequence
        WHERE sqlite_sequence.name = 'message'
    )
    SELECT * FROM (
	    SELECT * FROM (
	        SELECT 
	        CASE
	            WHEN length(DATE) = 18 
	            THEN LAG(DATETIME(DATE/1000000000 + 978307200, 'UNIXEPOCH'),1) OVER (ORDER BY ROWID) 
	            WHEN length(DATE) = 9
	            THEN LAG(DATETIME(DATE + 978307200, 'UNIXEPOCH'),1) OVER (ORDER BY ROWID)
	            END AS "Beginning Timestamp",
	        CASE
	            WHEN length(DATE) = 18 
	            THEN DATETIME(DATE/1000000000 + 978307200, 'UNIXEPOCH') 
	            WHEN length(DATE) = 9
	            THEN DATETIME(DATE + 978307200, 'UNIXEPOCH')
	            END  AS "Ending Timestamp",
			LAG (guid,1) OVER (ORDER BY ROWID) AS "Previous guid", 
            guid AS "guid", 
			LAG (ROWID,1) OVER (ORDER BY ROWID) AS "Previous ROWID", 
	        ROWID AS "ROWID", 
	        (ROWID - (LAG (ROWID,1) OVER (ORDER BY ROWID)) - 1) AS "Number of Missing Rows" 
	        FROM message) list
	        WHERE ROWID - "Previous ROWID" > 1

			UNION ALL

            SELECT
            CASE
                WHEN message.ROWID != (SELECT last_rowid FROM LastROWID)
                THEN MAX(CASE
                            WHEN length(DATE) = 18 THEN DATETIME(DATE/1000000000 + 978307200, 'UNIXEPOCH')
                            WHEN length(DATE) = 9  THEN DATETIME(DATE + 978307200, 'UNIXEPOCH')
                        END)
                END AS "Beginning Timestamp",
            CASE
                WHEN message.ROWID != (SELECT last_rowid FROM LastROWID)
                THEN "Time of Extraction"
                END AS "Ending Timestamp",
            CASE
                WHEN message.ROWID != (SELECT last_rowid FROM LastROWID)
                THEN guid
                END AS "Previous guid",
            CASE
                WHEN message.ROWID != (SELECT last_rowid FROM LastROWID)
                THEN "Unknown" 
                END AS "guid",
            CASE
                WHEN message.ROWID != (SELECT last_rowid FROM LastROWID)
                THEN MAX(ROWID)
                END AS "Previous ROWID",
            CASE
                WHEN message.ROWID != (SELECT last_rowid FROM LastROWID)
                THEN (SELECT last_rowid FROM LastROWID)
                END AS "ROWID",
            CASE
                WHEN message.ROWID != (SELECT last_rowid FROM LastROWID)
                THEN ((SELECT last_rowid FROM LastROWID) - message.ROWID)
                END AS "Number of Missing Rows"
            FROM message)
        WHERE "ROWID" IS NOT NULL;'''
    
    data_headers = ('Beginning Timestamp', 'Ending Timestamp', 'Previous guid', 'guid', 'Previous ROWID', 'ROWID', 'Number of Missing Rows')

    db_records = get_sqlite_db_records(data_source, query)
    
    for record in db_records:
        data_list.append(
            (record[0], record[1], record[2], record[3], record[4], record[5], record[6])
            )
    
    return data_headers, data_list, data_source
