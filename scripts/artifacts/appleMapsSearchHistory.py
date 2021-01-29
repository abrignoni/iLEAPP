import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows


def get_appleMapsSearchHistory(files_found, report_folder, seeker):
    data_list = []

    for file_found in files_found:
        file_found = str(file_found)
        with open(file_found, "rb") as plist_file:
            plist_content = plistlib.load(plist_file)
            for entry in plist_content['MSPHistory']['records']:
                search_history = plist_content['MSPHistory']['records'][entry]
                content = search_history.get('contents').decode('UTF-8', 'ignore')
                timestamp = search_history.get('modificationDate')
                formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                if len(content) < 300:
                    id_search_entry = content.split('\n')
                    search_entry = id_search_entry[1].split('"')
                    search_entry_split = str(search_entry[0]).split('\x12')
                    search_entry_filtered = list(filter(None, search_entry_split))
                    data_list.append((formatted_timestamp, ', '.join(search_entry_filtered)))

    if len(data_list) > 0:
        report = ArtifactHtmlReport('Apple Maps Search History')
        report.start_artifact_report(report_folder, 'Apple Maps Search History')
        report.add_script()
        data_headers = ("Timestamp", "Search Entry")
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = 'Apple Maps Search History'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Apple Maps Search History'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No data available for Apple Maps Search History')
