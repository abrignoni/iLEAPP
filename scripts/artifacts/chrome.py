__artifacts_v2__ = {
    "chromeWebHistory": {
        "name": "Web History",
        "description": "Parses web history from Chromium Based Browsers",
        "author": "@stark4n6",
        "version": "0.0.3",
        "date": "2024-11-10",
        "requirements": "none",
        "category": "Chromium",
        "notes": "",
        "paths": ('*/Chrome/Default/History*', '*/app_sbrowser/Default/History*', '*/app_opera/History*',
                  '*/Chromium/Default/History*'),
        "output_types": "standard",
    },
    "chromeWebVisits": {
        "name": "Web Visits",
        "description": "Parses web visits from Chromium Based Browsers",
        "author": "@stark4n6",
        "version": "0.0.3",
        "date": "2024-11-10",
        "requirements": "none",
        "category": "Chromium",
        "notes": "",
        "paths": ('*/Chrome/Default/History*', '*/app_sbrowser/Default/History*', '*/app_opera/History*',
                  '*/Chromium/Default/History*'),
        "output_types": "standard",
    },
    "chromeWebSearch": {
        "name": "Web Searches",
        "description": "Parses web searches from Chromium Based Browsers",
        "author": "@stark4n6",
        "version": "0.0.3",
        "date": "2024-11-10",
        "requirements": "none",
        "category": "Chromium",
        "notes": "",
        "paths": ('*/Chrome/Default/History*', '*/app_sbrowser/Default/History*', '*/app_opera/History*',
                  '*/Chromium/Default/History*'),
        "output_types": "standard",
    },
    "chromeDownloads": {
        "name": "Downloads",
        "description": "Parses downloads from Chromium Based Browsers",
        "author": "@stark4n6",
        "version": "0.0.3",
        "date": "2024-11-10",
        "requirements": "none",
        "category": "Chromium",
        "notes": "",
        "paths": ('*/Chrome/Default/History*', '*/app_sbrowser/Default/History*', '*/app_opera/History*',
                  '*/Chromium/Default/History*'),
        "output_types": "standard",
    },
    "chromeKeywordSearchTerms": {
        "name": "Keyword Search Terms",
        "description": "Parses keyword search terms from Chromium Based Browsers",
        "author": "@stark4n6",
        "version": "0.0.3",
        "date": "2024-11-10",
        "requirements": "none",
        "category": "Chromium",
        "notes": "",
        "paths": ('*/Chrome/Default/History*', '*/app_sbrowser/Default/History*', '*/app_opera/History*',
                  '*/Chromium/Default/History*'),
        "output_types": "standard",
    },
}

import os
import textwrap
import urllib.parse

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, get_next_unused_name, open_sqlite_db_readonly, does_column_exist_in_db, lava_process_artifact, lava_insert_sqlite_data, artifact_processor, convert_utc_human_to_timezone, convert_ts_human_to_utc

def get_browser_name(file_name):

    if 'brave' in file_name.lower():
        return 'Brave'
    elif 'microsoft' in file_name.lower():
        return 'Edge'
    elif 'opera' in file_name.lower():
        return 'Opera'
    elif 'chrome' in file_name.lower():
        return 'Chrome'
    else:
        return 'Unknown'

@artifact_processor
def chromeWebHistory(files_found, report_folder, seeker, wrap_text, timezone_offset):

    # all_data will be a consolidated list of all browsers with an extra column to discriminate the browser
    all_data = []
    data_headers = ['Last Visit Time', 'URL', 'Title', 'Visit Count', 'Typed Count', 'ID', 'Hidden']

    lava_data_headers = data_headers.copy()
    lava_data_headers[0] = (lava_data_headers[0], 'datetime')

    all_data_headers = lava_data_headers + ['Browser Name']

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'History':  # skip -journal and other files
            continue
        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        
        # Web History
        cursor.execute('''
        SELECT
        datetime(last_visit_time/1000000 + (strftime('%s','1601-01-01')),'unixepoch') AS LastVisitDate,
        url AS URL,
        title AS Title,
        visit_count AS VisitCount,
        typed_count AS TypedCount,
        id AS ID,
        CASE hidden
            WHEN 0 THEN ''
            WHEN 1 THEN 'Yes'
        END as Hidden
        FROM urls  
        ''')

        all_rows = cursor.fetchall()
        if len(all_rows) > 0:
            report_name = f'{browser_name} - Web History'
            report = ArtifactHtmlReport(report_name)
            # check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{report_name}.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_list = []

            for row in all_rows:
                dt = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),timezone_offset)
                if wrap_text:
                    data_list.append((dt,textwrap.fill(row[1], width=100),row[2],row[3],row[4],row[5],row[6]))
                else:
                    data_list.append((dt,row[1],row[2],row[3],row[4],row[5],row[6]))
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            # Generate LAVA output

            category = "Chromium"
            module_name = "chromeWebHistory"
            table_name, object_columns, column_map = lava_process_artifact(category, module_name, report_name,
                                                                           lava_data_headers, len(data_list))

            lava_insert_sqlite_data(table_name, data_list, object_columns, lava_data_headers, column_map)

            # Add browser name column to the data
            data_list = [row + (browser_name,) for row in data_list]

            # Add current list to the combined list
            all_data.extend(data_list)
        else:
            logfunc(f'No {browser_name} - Web History data available')

        db.close()

    return all_data_headers, all_data, file_found


@artifact_processor
def chromeWebVisits(files_found, report_folder, seeker, wrap_text, timezone_offset):

    # all_data will be a consolidated list of all browsers with an extra column to discriminate the browser
    all_data = []
    data_headers = ['Visit Timestamp', 'URL', 'Title', 'Duration', 'Transition Type', 'Qualifier(s)', 'From Visit URL']

    lava_data_headers = data_headers.copy()
    lava_data_headers[0] = (lava_data_headers[0], 'datetime')

    all_data_headers = lava_data_headers + ['Browser Name']

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'History':  # skip -journal and other files
            continue
        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        #Web Visits
        cursor.execute('''
        SELECT
        datetime(visits.visit_time/1000000 + (strftime('%s','1601-01-01')),'unixepoch'),
        urls.url,
        urls.title,
        CASE visits.visit_duration
            WHEN 0 THEN ''
            ELSE strftime('%H:%M:%f', visits.visit_duration / 1000000.000,'unixepoch')
        END as Duration,
        CASE visits.transition & 0xff
            WHEN 0 THEN 'LINK'
            WHEN 1 THEN 'TYPED'
            WHEN 2 THEN 'AUTO_BOOKMARK'
            WHEN 3 THEN 'AUTO_SUBFRAME'
            WHEN 4 THEN 'MANUAL_SUBFRAME'
            WHEN 5 THEN 'GENERATED'
            WHEN 6 THEN 'START_PAGE'
            WHEN 7 THEN 'FORM_SUBMIT'
            WHEN 8 THEN 'RELOAD'
            WHEN 9 THEN 'KEYWORD'
            WHEN 10 THEN 'KEYWORD_GENERATED'
            ELSE NULL
        END AS CoreTransitionType,
        trim((CASE WHEN visits.transition & 0x00800000 THEN 'BLOCKED, ' ELSE '' END ||
        CASE WHEN visits.transition & 0x01000000 THEN 'FORWARD_BACK, ' ELSE '' END ||
        CASE WHEN visits.transition & 0x02000000 THEN 'FROM_ADDRESS_BAR, ' ELSE '' END ||
        CASE WHEN visits.transition & 0x04000000 THEN 'HOME_PAGE, ' ELSE '' END ||
        CASE WHEN visits.transition & 0x08000000 THEN 'FROM_API, ' ELSE '' END ||
        CASE WHEN visits.transition & 0x10000000 THEN 'CHAIN_START, ' ELSE '' END ||
        CASE WHEN visits.transition & 0x20000000 THEN 'CHAIN_END, ' ELSE '' END ||
        CASE WHEN visits.transition & 0x40000000 THEN 'CLIENT_REDIRECT, ' ELSE '' END ||
        CASE WHEN visits.transition & 0x80000000 THEN 'SERVER_REDIRECT, ' ELSE '' END ||
        CASE WHEN visits.transition & 0xC0000000 THEN 'IS_REDIRECT_MASK, ' ELSE '' END),', ')
        AS Qualifiers,
        Query2.url AS FromURL
        FROM visits
        LEFT JOIN urls ON visits.url = urls.id
        LEFT JOIN (SELECT urls.url,urls.title,visits.visit_time,visits.id FROM visits LEFT JOIN urls ON visits.url = urls.id) Query2 ON visits.from_visit = Query2.id  
        ''')

        all_rows = cursor.fetchall()
        if len(all_rows) > 0:
            report_name = f'{browser_name} - Web Visits'
            report = ArtifactHtmlReport(report_name)
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{report_name}.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()

            data_list = []
            for row in all_rows:
                dt = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),timezone_offset)
                if wrap_text:
                    data_list.append((dt,textwrap.fill(row[1], width=100),row[2],row[3],row[4],row[5],row[6]))
                else:
                    data_list.append((dt,row[1],row[2],row[3],row[4],row[5],row[6]))
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            # Generate LAVA output

            category = "Chromium"
            module_name = "chromeWebVisits"

            table_name, object_columns, column_map = lava_process_artifact(category, module_name, report_name,
                                                                           lava_data_headers, len(data_list))

            lava_insert_sqlite_data(table_name, data_list, object_columns, lava_data_headers, column_map)

            # Add browser name column to the data
            data_list = [row + (browser_name,) for row in data_list]

            # Add current list to the combined list
            all_data.extend(data_list)

        else:
            logfunc(f'No {browser_name} - Web Visits data available')

        db.close()

    return all_data_headers, all_data, file_found

@artifact_processor
def chromeWebSearch(files_found, report_folder, seeker, wrap_text, timezone_offset):

    # all_data will be a consolidated list of all browsers with an extra column to discriminate the browser
    all_data = []

    data_headers = ['Last Visit Time', 'Search Term', 'URL', 'Title', 'Visit Count']

    lava_data_headers = data_headers.copy()
    lava_data_headers[0] = (lava_data_headers[0], 'datetime')

    all_data_headers = lava_data_headers + ['Browser Name']

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'History':  # skip -journal and other files
            continue
        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        #Web Search    
        cursor.execute('''
        SELECT
            url,
            title,
            visit_count,
            datetime(last_visit_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
        FROM urls
        WHERE url like '%search?q=%'
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report_name = f'{browser_name} - Web Search'
            report = ArtifactHtmlReport(report_name)
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{report_name}.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()

            data_list = []
            for row in all_rows:
                dt = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[3]),timezone_offset)
                search = row[0].split('search?q=')[1].split('&')[0]
                search = urllib.parse.unquote(search).replace('+', ' ')
                if wrap_text:
                    data_list.append((dt, search, (textwrap.fill(row[0], width=100)),row[1],row[2]))
                else:
                    data_list.append((dt, search, row[0], row[1], row[2]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            # Generate LAVA output

            category = "Chromium"
            module_name = "chromeWebSearch"

            table_name, object_columns, column_map = lava_process_artifact(category, module_name, report_name,
                                                                           lava_data_headers, len(data_list))

            lava_insert_sqlite_data(table_name, data_list, object_columns, lava_data_headers, column_map)

            # Add browser name column to the data
            data_list = [row + (browser_name,) for row in data_list]

            # Add current list to the combined list
            all_data.extend(data_list)

        else:
            logfunc(f'No {browser_name} - Web Search Terms data available')

        db.close()

    return all_data_headers, all_data, file_found

@artifact_processor
def chromeDownloads(files_found, report_folder, seeker, wrap_text, timezone_offset):

    # all_data will be a consolidated list of all browsers with an extra column to discriminate the browser
    all_data = []

    data_headers = ['Start Time', 'End Time', 'Last Access Time', 'URL', 'Target Path', 'State', 'Danger Type',
                    'Interrupt Reason', 'Opened?', 'Received Bytes', 'Total Bytes']

    lava_data_headers = data_headers.copy()
    lava_data_headers[0] = (lava_data_headers[0], 'datetime')
    lava_data_headers[1] = (lava_data_headers[1], 'datetime')
    lava_data_headers[2] = (lava_data_headers[2], 'datetime')

    all_data_headers = lava_data_headers + ['Browser Name']

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'History':  # skip -journal and other files
            continue
        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        #Downloads
        # check for last_access_time column, an older version of chrome db (32) does not have it
        if does_column_exist_in_db(db, 'downloads', 'last_access_time') == True:
            last_access_time_query = '''
            CASE last_access_time 
                WHEN "0" 
                THEN "" 
                ELSE datetime(last_access_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
            END AS "Last Access Time"'''
        else:
            last_access_time_query = "'' as last_access_query"

        cursor.execute(f'''
        SELECT 
        CASE start_time  
            WHEN "0" 
            THEN "" 
            ELSE datetime(start_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
        END AS "Start Time", 
        CASE end_time 
            WHEN "0" 
            THEN "" 
            ELSE datetime(end_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
        END AS "End Time", 
        {last_access_time_query},
        tab_url, 
        target_path, 
        CASE state
            WHEN "0" THEN "In Progress"
            WHEN "1" THEN "Complete"
            WHEN "2" THEN "Canceled"
            WHEN "3" THEN "Interrupted"
            WHEN "4" THEN "Interrupted"
        END,
        CASE danger_type
            WHEN "0" THEN ""
            WHEN "1" THEN "Dangerous"
            WHEN "2" THEN "Dangerous URL"
            WHEN "3" THEN "Dangerous Content"
            WHEN "4" THEN "Content May Be Malicious"
            WHEN "5" THEN "Uncommon Content"
            WHEN "6" THEN "Dangerous But User Validated"
            WHEN "7" THEN "Dangerous Host"
            WHEN "8" THEN "Potentially Unwanted"
            WHEN "9" THEN "Allowlisted by Policy"
            WHEN "10" THEN "Pending Scan"
            WHEN "11" THEN "Blocked - Password Protected"
            WHEN "12" THEN "Blocked - Too Large"
            WHEN "13" THEN "Warning - Sensitive Content"
            WHEN "14" THEN "Blocked - Sensitive Content"
            WHEN "15" THEN "Safe - Deep Scanned"
            WHEN "16" THEN "Dangerous, But User Opened"
            WHEN "17" THEN "Prompt For Scanning"
            WHEN "18" THEN "Blocked - Unsupported Type"
        END,
        CASE interrupt_reason
            WHEN "0" THEN ""
            WHEN "1" THEN "File Error"
            WHEN "2" THEN "Access Denied"
            WHEN "3" THEN "Disk Full"
            WHEN "5" THEN "Path Too Long"
            WHEN "6" THEN "File Too Large"
            WHEN "7" THEN "Virus"
            WHEN "10" THEN "Temporary Problem"
            WHEN "11" THEN "Blocked"
            WHEN "12" THEN "Security Check Failed"
            WHEN "13" THEN "Resume Error"
            WHEN "20" THEN "Network Error"
            WHEN "21" THEN "Operation Timed Out"
            WHEN "22" THEN "Connection Lost"
            WHEN "23" THEN "Server Down"
            WHEN "30" THEN "Server Error"
            WHEN "31" THEN "Range Request Error"
            WHEN "32" THEN "Server Precondition Error"
            WHEN "33" THEN "Unable To Get File"
            WHEN "34" THEN "Server Unauthorized"
            WHEN "35" THEN "Server Certificate Problem"
            WHEN "36" THEN "Server Access Forbidden"
            WHEN "37" THEN "Server Unreachable"
            WHEN "38" THEN "Content Lenght Mismatch"
            WHEN "39" THEN "Cross Origin Redirect"
            WHEN "40" THEN "Canceled"
            WHEN "41" THEN "Browser Shutdown"
            WHEN "50" THEN "Browser Crashed"
        END,
        opened, 
        received_bytes, 
        total_bytes
        FROM downloads
        ''')

        all_rows = cursor.fetchall()
        if len(all_rows) > 0:
            report_name = f'{browser_name} - Downloads'
            report = ArtifactHtmlReport(report_name)
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{report_name}.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            # Generate LAVA output

            category = "Chromium"
            module_name = "chromeDownloads"

            table_name, object_columns, column_map = lava_process_artifact(category, module_name, report_name,
                                                                           lava_data_headers, len(data_list))

            lava_insert_sqlite_data(table_name, data_list, object_columns, lava_data_headers, column_map)

            # Add browser name column to the data
            data_list = [row + (browser_name,) for row in data_list]

            # Add current list to the combined list
            all_data.extend(data_list)
        else:
            logfunc(f'No {browser_name} - Downloads data available')

        db.close()

    return all_data_headers, all_data, file_found

@artifact_processor
def chromeKeywordSearchTerms(files_found, report_folder, seeker, wrap_text, timezone_offset):
    # all_data will be a consolidated list of all browsers with an extra column to discriminate the browser
    all_data = []

    data_headers = ['Last Visit Time','Term','URL']

    lava_data_headers = data_headers.copy()
    lava_data_headers[0] = (lava_data_headers[0], 'datetime')

    all_data_headers = lava_data_headers + ['Browser Name']

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'History':  # skip -journal and other files
            continue
        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        #Search Terms
        cursor.execute('''
        SELECT
            url_id,
            term,
            id,
            url,
            datetime(last_visit_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
        FROM keyword_search_terms, urls
        WHERE url_id = id
        ''')

        all_rows = cursor.fetchall()
        if len(all_rows) > 0:
            report_name = f'{browser_name} - Keyword Search Terms'
            report = ArtifactHtmlReport(report_name)
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{report_name}.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_list = []
            for row in all_rows:
                dt = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[4]),timezone_offset)
                if wrap_text:
                    data_list.append((dt, row[1],(textwrap.fill(row[3], width=100))))
                else:
                    data_list.append((dt, row[1], row[3]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            # Generate LAVA output

            category = "Chromium"
            module_name = "chromeKeywordSearchTerms"

            table_name, object_columns, column_map = lava_process_artifact(category, module_name, report_name,
                                                                           lava_data_headers, len(data_list))

            lava_insert_sqlite_data(table_name, data_list, object_columns, lava_data_headers, column_map)

            # Add browser name column to the data
            data_list = [row + (browser_name,) for row in data_list]

            # Add current list to the combined list
            all_data.extend(data_list)
        else:
            logfunc(f'No {browser_name} - Keyword Search Terms data available')
        
        db.close()

    return all_data_headers, all_data, file_found