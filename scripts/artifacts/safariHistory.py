# Module Description: Parses Safari web history visits
# Author: @KevinPagano3
# Date: 2023-02-14
# Artifact version: 0.0.1
# Requirements: none

import textwrap

from scripts.ilapfuncs import (artifact_processor, open_sqlite_db_readonly,
                               convert_ts_human_to_utc, convert_utc_human_to_timezone)


@artifact_processor
def get_safariHistory(files_found, report_folder, seeker, wrap_text, timezone_offset):
    file_found = str(files_found[0])
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.db'):
            break

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()

    cursor.execute("""
    select
    history_visits.id,
    history_items.url
    from history_visits
    left join history_items on history_items.id = history_visits.history_item
    order by history_visits.id
    """)

    all_rows = cursor.fetchall()
    dl_ref_dest = {}
    for row in all_rows:
        dl_ref_dest.update({str(row[0]): row[1]})

    cursor.execute("""
    select
    datetime(history_visits.visit_time + 978307200,'unixepoch'),
    history_visits.title,
    history_items.url,
    history_items.visit_count,
    history_visits.redirect_source,
    history_visits.redirect_destination,
    history_visits.id,
    case history_visits.origin
        when 0 then "Local Device"
        when 1 then "iCloud Synced Device"
    end
    from history_visits
    left join history_items on history_visits.history_item = history_items.id
    """)

    all_rows = cursor.fetchall()
    data_list = []

    for row in all_rows:
        timestamp = convert_ts_human_to_utc(row[0])
        timestamp = convert_utc_human_to_timezone(timestamp, timezone_offset)

        redirect_source = ''
        redirect_destination = ''
        if str(row[4]) is not None:
            for key, value in dl_ref_dest.items():
                if str(row[4]) == key:
                    redirect_source = value
        if str(row[5]) is not None:
            for key, value in dl_ref_dest.items():
                if str(row[5]) == key:
                    redirect_destination = value

        data_list.append((timestamp, row[1], textwrap.fill(row[2], width=100), row[3],
                         textwrap.fill(redirect_source, width=100),
                         textwrap.fill(redirect_destination, width=100), row[6], row[7]))

    db.close()

    data_headers = ('Visit Timestamp', 'Title', 'URL', 'Visit Count', 'Redirect Source',
                    'Redirect Destination', 'Visit ID', 'Origin')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_safariHistory": {
        "name": "Safari History",
        "description": "",
        "author": "@KevinPagano3",
        "version": "0.0.1",
        "date": "2023-02-14",
        "requirements": "none",
        "category": "Safari Browser",
        "notes": "",
        "paths": ('**/Safari/History.db*',),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}
