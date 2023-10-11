import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline


def get_keyboardAppUsage(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []

    for file_found in files_found:
        file_found = str(file_found)
        with open(file_found, "rb") as plist_file:
            plist_content = plistlib.load(plist_file)
            for app in plist_content:
                for entry in plist_content[app]:
                    data_list.append((entry['startDate'], app, entry['appTime'], ', '.join(map(str, entry['keyboardTimes']))))

    if len(data_list) > 0:
        report = ArtifactHtmlReport('Keyboard Application Usage')
        report.start_artifact_report(report_folder, 'Keyboard Application Usage')
        report.add_script()
        data_headers = ('Date', 'Application Name', 'Application Time Used in Seconds', 'Keyboard Times Used in Seconds')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = 'Keyboard Application Usage'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Keyboard Application Usage'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Keyboard Application Usage found')

__artifacts__ = {
    "keyboardAppUsage": (
        "Keyboard",
        ('*/mobile/Library/Keyboard/app_usage_database.plist'),
        get_keyboardAppUsage)
}