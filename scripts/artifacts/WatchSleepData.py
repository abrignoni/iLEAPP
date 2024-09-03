__artifacts_v2__ = {
    "HealthSleepData": {
        "name": "Apple Health Sleep Data",
        "description": "Parses Apple Health Sleep Data from the healthdb_secure.sqlite database",
        "author": "@SQLMcGee for Metadata Forensics, LLC",
        "version": "0.0.1",
        "date": "2024-08-01",
        "requirements": "none",
        "category": "Health - Sleep",
        "notes": "These artifacts provide an 'at a glance' review of sleep periods when the Apple Watch is worn, given required user settings.\
        Additional details published within 'Sleepless in Cupertino: A Forensic Dive into Apple Watch Sleep Tracking' at \
        https://metadataperspective.com/2024/08/01/sleepless-in-cupertino-a-forensic-dive-into-apple-watch-sleep-tracking/",
        "paths": ('*Health/healthdb_secure.sqlite*',),
        "function": "get_Health"
    }
}

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_Health(files_found, report_folder, seeker, wrap_text, timezone_offset):

    healthdb_secure = ''
    source_file_healthdb_secure = ''

    for file_found in files_found:
        file_name = str(file_found)
        if file_name.endswith('healthdb_secure.sqlite'):
           healthdb_secure = str(file_found)
           source_file_healthdb_secure = file_found.replace(seeker.directory, '')

        else:
            continue

    db = open_sqlite_db_readonly(healthdb_secure)
    cursor = db.cursor()
    
    # All Sleep Data Watch
    
    cursor.execute('''
    SELECT
    DATETIME(SAMPLES.START_DATE + 978307200, 'UNIXEPOCH'),
    CASE
        WHEN category_samples.value IS 2 THEN "AWAKE"
        WHEN category_samples.value IS 3 THEN "CORE"
        WHEN category_samples.value IS 4 THEN "DEEP"
        WHEN category_samples.value IS 5 THEN "REM"
    END,
    DATETIME(SAMPLES.END_DATE + 978307200, 'UNIXEPOCH'),
    STRFTIME('%H:%M:%S', (samples.end_date - samples.start_date), 'unixepoch')
    FROM samples
    LEFT OUTER JOIN category_samples ON samples.data_id = category_samples.data_id
    LEFT OUTER JOIN objects on samples.data_id = objects.data_id
    LEFT OUTER JOIN data_provenances on objects.provenance = data_provenances.ROWID
    WHERE samples.data_type IS 63 AND category_samples.value != 0 AND category_samples.value != 1 AND data_provenances.origin_product_type like "%Watch%"
    ORDER BY category_samples.data_id;
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
        
            data_list.append((row[0], row[1], row[2], row[3]))

        report = ArtifactHtmlReport('Health - Sleep - All Watch Sleep Data')
        report.start_artifact_report(report_folder, 'Health - Sleep - All Watch Sleep Data')
        report.add_script()
        data_headers = (
            'Sleep Start Time', 'Sleep State', 'Sleep End Time', 'Sleep State (HH:MM:SS)')
        report.write_artifact_data_table(data_headers, data_list, healthdb_secure)
        report.end_artifact_report()

        tsvname = 'Health - Sleep - All Watch Sleep Data'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Health - Sleep - All Watch Sleep Data'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in Health - Sleep - All Watch Sleep Data')
    
    # Sleep Data Breakdown Watch
    
    cursor.execute('''
    WITH lagged_samples AS (
        SELECT
            samples.start_date,
            samples.end_date,
            samples.data_id,
            DATETIME(samples.start_date + 978307200, 'UNIXEPOCH') AS start_time,
            DATETIME(samples.end_date + 978307200, 'UNIXEPOCH') AS end_time,
            (samples.end_date - samples.start_date) / 60 AS duration_minutes,
            samples.data_type,
            category_samples.value,
            LAG(samples.data_id) OVER (ORDER BY samples.data_id) AS prev_data_id,
            CASE
                WHEN category_samples.value = 2 THEN "AWAKE"
                WHEN category_samples.value = 3 THEN "CORE"
                WHEN category_samples.value = 4 THEN "DEEP"
                WHEN category_samples.value = 5 THEN "REM"
            END AS sleep_value
        FROM samples
        LEFT OUTER JOIN category_samples ON samples.data_id = category_samples.data_id
        LEFT OUTER JOIN objects on samples.data_id = objects.data_id
        LEFT OUTER JOIN data_provenances on objects.provenance = data_provenances.ROWID
        WHERE samples.data_type IS 63 AND category_samples.value != 0 AND category_samples.value != 1 AND data_provenances.origin_product_type like "%Watch%"
        ORDER BY category_samples.data_id
    ),
    grouped_samples AS (
        SELECT
            start_time,
            start_date,
            sleep_value,
            end_time,
            end_date,
            duration_minutes,
            data_type,
            value,
            CASE
                WHEN data_id - prev_data_id > 1 OR prev_data_id IS NULL THEN 1
                ELSE 0
            END AS is_new_group,
            SUM(CASE
                    WHEN data_id - prev_data_id > 1 OR prev_data_id IS NULL THEN 1
                    ELSE 0
                END) OVER (ORDER BY data_id) AS group_number
        FROM lagged_samples
    )
    SELECT
        MIN(start_time),
        MAX(end_time),
        STRFTIME('%H:%M:%S', SUM(CASE WHEN sleep_value IN ('AWAKE', 'REM', 'CORE', 'DEEP') THEN duration_minutes * 60 ELSE 0 END), 'unixepoch'),
        STRFTIME('%H:%M:%S', SUM(CASE WHEN sleep_value IN ('REM', 'CORE', 'DEEP') THEN duration_minutes * 60 ELSE 0 END), 'unixepoch'),
        STRFTIME('%H:%M:%S', SUM(CASE WHEN sleep_value = 'AWAKE' THEN duration_minutes * 60 ELSE 0 END), 'unixepoch'),
        STRFTIME('%H:%M:%S', SUM(CASE WHEN sleep_value = 'REM' THEN duration_minutes * 60 ELSE 0 END), 'unixepoch'),
        STRFTIME('%H:%M:%S', SUM(CASE WHEN sleep_value = 'CORE' THEN duration_minutes * 60 ELSE 0 END), 'unixepoch'),
        STRFTIME('%H:%M:%S', SUM(CASE WHEN sleep_value = 'DEEP' THEN duration_minutes * 60 ELSE 0 END), 'unixepoch'),
        ROUND(SUM(CASE WHEN sleep_value = 'AWAKE' THEN duration_minutes ELSE 0 END) * 100.0 / SUM(duration_minutes), 2),
        ROUND(SUM(CASE WHEN sleep_value = 'REM' THEN duration_minutes ELSE 0 END) * 100.0 / SUM(duration_minutes), 2),
        ROUND(SUM(CASE WHEN sleep_value = 'CORE' THEN duration_minutes ELSE 0 END) * 100.0 / SUM(duration_minutes), 2),
        ROUND(SUM(CASE WHEN sleep_value = 'DEEP' THEN duration_minutes ELSE 0 END) * 100.0 / SUM(duration_minutes), 2)
    FROM grouped_samples
    GROUP BY group_number;
''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11]))
    
        report = ArtifactHtmlReport('Health - Sleep - Watch By Sleep Period')
        report.start_artifact_report(report_folder, 'Health - Sleep - Watch By Sleep Period')
        report.add_script()
        data_headers = (
            'Sleep Start Time', 'Sleep End Time', 'Time in Bed (HH:MM:SS)', 
            'Time Asleep (HH:MM:SS)', 'Awake Duration (HH:MM:SS)', 
            'REM Duration (HH:MM:SS)', 'Core Duration (HH:MM:SS)', 
            'Deep Duration (HH:MM:SS)', 'Awake %', 'REM %', 'Core %', 'Deep %')
        report.write_artifact_data_table(data_headers, data_list, healthdb_secure)
        report.end_artifact_report()

        tsvname = 'Health - Sleep - Watch By Sleep Period'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Health - Sleep - Watch By Sleep Period'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in Health - Sleep - Watch By Sleep Period')
    
__artifacts__ = {
    "health": (
        "Health",
        ('*Health/healthdb_secure.sqlite*'),
        get_Health)
}
