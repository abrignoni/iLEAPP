import os
import blackboxprotobuf
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, convert_utc_human_to_timezone, timestampsconv
from ccl_segb import ccl_segb
from ccl_segb.ccl_segb_common import EntryState

def get_biomeInfocus(files_found, report_folder, seeker, wrap_text, timezone_offset):

    typess = {'10': {'name': '', 'type': 'str'}, '2': {'name': '', 'type': 'int'}, '3': {'name': '', 'type': 'int'},
     '4': {'name': '', 'type': 'double'}, '6': {'name': '', 'type': 'str'}, '9': {'name': '', 'type': 'str'}}

    data_list = []

    for file_found in files_found:
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in file_found:
                continue
            else:
                report_file = os.path.dirname(file_found)
        else:
            continue



        for record in ccl_segb.read_segb_file(file_found):
            if record.state == EntryState.Written:
                protostuff, types = blackboxprotobuf.decode_message(record.data, typess)

                bundleid = (protostuff['6'])
                timestart = (timestampsconv(protostuff['4']))
                timestart = convert_utc_human_to_timezone(timestart, timezone_offset)

                foreground = ('Foreground' if protostuff['3'] == 1 else 'Background')

                data_list.append((timestart, bundleid, foreground, filename))


    if len(data_list) > 0:

        description = ''
        report = ArtifactHtmlReport(f'Biome AppInFocus')
        report.start_artifact_report(report_folder, f'Biome AppInFocus', description)
        report.add_script()
        data_headers = ('Time','Bundle ID','Action', 'Filename')
        report.write_artifact_data_table(data_headers, data_list, report_file)
        report.end_artifact_report()

        tsvname = f'Biome AppInFocus'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Biome AppInFocus'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc(f'No data available for Biome AppInFocus')


__artifacts__ = {
    "biomeInFocus": (
        "Biome in Focus",
        ('*/biome/streams/restricted/App.InFocus/local/*'),
        get_biomeInfocus)
}
