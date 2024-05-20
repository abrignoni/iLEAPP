# Module Description: Parses Apple Watch Worn Data from the healthdb_secure.sqlite database
# Author: @SQLMcGee for Metadata Forensics, LLC
# Date: 2024-05-20
# Artifact version: 0.0.1
# Requirements: none
# This artifact provides an "at a glance" review of time periods in which the Apple Watch is worn. This data can lend to pattern of life analysis as well as providing structure to periods in which data such as heart rate data will be generated and recorded.
# Additional details published within "Apple Watch Worn Data Analysis" at https://metadataperspective.com/2024/05/20/apple-watch-worn-data-analysis/.

import sqlite3
import textwrap
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

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

    cursor.execute('''
    WITH TimeData AS (
        SELECT
            datetime(start_date + 978307200, 'UNIXEPOCH') AS "Start Time",
            datetime(end_date + 978307200, 'UNIXEPOCH') AS "End Time",
            LAG(datetime(start_date + 978307200, 'UNIXEPOCH')) OVER (ORDER BY start_date) AS "Prev Start Time",
            LAG(datetime(end_date + 978307200, 'UNIXEPOCH')) OVER (ORDER BY start_date) AS "Prev End Time"
        FROM samples
        WHERE data_type = "70"
    ),
    PeriodData AS (
        SELECT
            *,
            strftime('%s', "Start Time") - strftime('%s', "Prev End Time") AS "Gap in Seconds",
            CASE 
                WHEN strftime('%s', "Start Time") - strftime('%s', "Prev End Time") > 3600 THEN 1 
                ELSE 0 
            END AS "New Period"
        FROM TimeData
    ),
    PeriodGroup AS (
        SELECT
            *,
            SUM("New Period") OVER (ORDER BY "Start Time" ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS "Period ID"
        FROM PeriodData
    ),
    Summary AS (
        SELECT
            "Period ID",
            MIN("Start Time") AS "Watch Worn Start Time",
            MAX("End Time") AS "Last Watch Worn Hour Time",
            (strftime('%s', MAX("End Time")) - strftime('%s', MIN("Start Time"))) / 3600.0 AS "Hours Worn"
        FROM PeriodGroup
        GROUP BY "Period ID"
    )
    SELECT 
        s1."Watch Worn Start Time",
        CAST(s1."Hours Worn" AS INT),
        s1."Last Watch Worn Hour Time",
        CAST(
            (strftime('%s', s2."Watch Worn Start Time") - 
             strftime('%s', s1."Last Watch Worn Hour Time")
            ) / 3600 AS INT
        ) AS "Hours Off Before Next Worn"
    FROM 
        Summary s1
    LEFT JOIN
        Summary s2 ON s1."Period ID" + 1 = s2."Period ID"
    ORDER BY s1."Period ID";
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
        
            data_list.append((row[0], row[1], row[2], row[3]))

        report = ArtifactHtmlReport('Health - Device - Watch Worn Data')
        report.start_artifact_report(report_folder, 'Health - Watch Worn Data')
        report.add_script()
        data_headers = (
            'Watch Worn Start Time', 'Hours Worn', 'Last Watch Worn Hour Time', 'Hours Off Before Next Worn Start Time')
        report.write_artifact_data_table(data_headers, data_list, healthdb_secure)
        report.end_artifact_report()

        tsvname = 'Health - Device - Watch Worn Data'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Health - Device - Watch Worn Data'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in Health - Device - Watch Worn Data')

__artifacts__ = {
    "Health - Device": (
        "Health - Device",
        ('*Health/healthdb_secure.sqlite*'),
        get_Health)
}
