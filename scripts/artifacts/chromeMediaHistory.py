import os
import sqlite3
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly

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

def get_chromeMediaHistory(files_found, report_folder, seeker, wrap_text, timezone_offset):

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('Media History'):
            continue # Skip all other files

        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(last_updated_time_s-11644473600, 'unixepoch') as last_updated_time_s,
            origin_id,
            url,
            strftime('%H:%M:%S',position_ms/1000, 'unixepoch') as position_ms,
            strftime('%H:%M:%S',duration_ms/1000, 'unixepoch') as duration_ms,
            title,
            artist,
            album,
            source_title
        from playbackSession
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'{browser_name} - Media History - Sessions')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{browser_name} - Media History - Sessions.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('Last Updated','Origin ID','URL','Position','Duration','Title','Artist','Album','Source Title') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'{browser_name} - Media History - Sessions'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'{browser_name} - Media History - Sessions'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc(f'No {browser_name} - Media History - Sessions data available')
        
        cursor.execute('''
        select
            datetime(last_updated_time_s-11644473600, 'unixepoch') as last_updated_time_s,
            id,
            origin_id,
            url,
            strftime('%H:%M:%S',watch_time_s, 'unixepoch') as watch_time_s,
            case has_audio
                when 0 then ''
                when 1 then 'Yes'
            end as has_audio,
            case has_video
                when 0 then ''
                when 1 then 'Yes'
            end as has_video  
        from playback
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'{browser_name} - Media History - Playbacks')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{browser_name} - Media History - Playbacks.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('Last Updated','ID','Origin ID','URL','Watch Time','Has Audio','Has Video') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'{browser_name} - Media History - Playbacks'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'{browser_name} - Media History - Playbacks'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc(f'No {browser_name} - Media History - Playbacks data available')
        
        cursor.execute('''
        select
            datetime(last_updated_time_s-11644473600, 'unixepoch') as last_updated_time_s,
            id,
            origin,
            cast(aggregate_watchtime_audio_video_s/86400 as integer) || ':' || strftime('%H:%M:%S', aggregate_watchtime_audio_video_s ,'unixepoch') as aggregate_watchtime_audio_video_s
        from origin
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'{browser_name} - Media History - Origins')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{browser_name} - Media History - Origins.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('Last Updated','ID','Origin','Aggregate Watchtime') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'{browser_name} - Media History - Origins'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'{browser_name} - Media History - Origins'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc(f'No {browser_name} - Media History - Origins data available')
        
        db.close()

__artifacts__ = {
        "ChromeMediaHistory": (
                "Chromium",
                ('*/Chrome/Default/Media History*','*/app_sbrowser/Default/Media History*', '*/app_opera/Media History*'),
                get_chromeMediaHistory)
}