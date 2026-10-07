__artifacts_v2__ = {
    "SMS_Missing_ROWIDs": {
        "name": "SMS - Missing ROWIDs",
        "description": "Lists the gaps in the ROWID sequence of the message table in sms.db: the size of each gap and the timestamps of the rows before and after it. A gap is a run of ROWID values absent from the table. It does not by itself establish that a message was deleted.",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2023-03-20",
        "last_update_date": "2026-10-07",
        "requirements": "none",
        "category": "SMS & iMessage",
        "notes": "Number of Missing Rows is the size of the gap. A final row compares the table "
                 "using its greatest live ROWID record with the message entry in sqlite_sequence. "
                 "Only a positive sequence difference is reported, using that record's date and guid, "
                 "with the text 'Time of Extraction' as its end. This query was the "
                 "product of research completed by @SQLMcGee (James McGee), Metadata Forensics, LLC, for "
                 "'Lagging for the Win', published by Belkasoft "
                 "https://belkasoft.com/lagging-for-win",
        "paths": ("*SMS/sms*"),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 15 rows",
            "dexter_ios18": "iOS 18.3.2 | 52 rows",
            "felix_ios17": "iOS 17.6.1 | 9 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 3 rows",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 30 rows",
            "abe_ios16": "iOS 16.5 | 1 row",
            "felix23_ios16": "iOS 16.5 | 1 row",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, convert_cocoa_core_data_ts_to_utc

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
	        LAG(message.date,1) OVER (ORDER BY ROWID) AS "Beginning Timestamp",
            message.date AS "Ending Timestamp",
			LAG (guid,1) OVER (ORDER BY ROWID) AS "Previous guid", 
            guid AS "guid", 
			LAG (ROWID,1) OVER (ORDER BY ROWID) AS "Previous ROWID", 
	        ROWID AS "ROWID", 
	        (ROWID - (LAG (ROWID,1) OVER (ORDER BY ROWID)) - 1) AS "Number of Missing Rows" 
	        FROM message) list
	        WHERE ROWID - "Previous ROWID" > 1

			UNION ALL

            SELECT
                last_live.date AS "Beginning Timestamp",
                'Time of Extraction' AS "Ending Timestamp",
                last_live.guid AS "Previous guid",
                'Unknown' AS "guid",
                last_live.live_rowid AS "Previous ROWID",
                (SELECT last_rowid FROM LastROWID) AS "ROWID",
                ((SELECT last_rowid FROM LastROWID) - last_live.live_rowid) AS "Number of Missing Rows"
            FROM (
                SELECT date, guid, ROWID AS live_rowid
                FROM message
                ORDER BY ROWID DESC
                LIMIT 1
            ) AS last_live
            WHERE ((SELECT last_rowid FROM LastROWID) - last_live.live_rowid) > 0)
        WHERE "ROWID" IS NOT NULL;'''
    
    data_headers = (('Beginning Timestamp', 'datetime'), ('Ending Timestamp', 'datetime'), 'Previous guid', 'guid', 'Previous ROWID', 'ROWID', 'Number of Missing Rows')

    db_records = get_sqlite_db_records(data_source, query)
    
    def fix_ts(val):
        if not isinstance(val, (int, float)):
            return val
            
        digits = len(str(abs(int(val))))

        if digits > 17:
            val = val / 1e9

        elif digits > 14: 
            val = val / 1e6

        return convert_cocoa_core_data_ts_to_utc(val)
    
    for record in db_records:
        start_raw = record[0]
        end_raw   = record[1]

        start_timestamp = fix_ts(start_raw)
        end_timestamp   = fix_ts(end_raw)

        data_list.append(
            (start_timestamp, end_timestamp, record[2], record[3], record[4], record[5], record[6])
        )
    
    return data_headers, data_list, data_source
