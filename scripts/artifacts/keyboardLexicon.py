import string
from os.path import dirname

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline


def get_keyboardLexicon(files_found, report_folder, seeker):
    if len(files_found) > 0:
        data_list = []

        for file_found in files_found:
            strings_list = []
            with open(file_found, 'rb') as dat_file:
                dat_content = dat_file.read()
                dat_content_decoded = str(dat_content, 'utf-8', 'ignore')
                found_str = ''
                for char in dat_content_decoded:
                    if char in string.printable:
                        found_str += char
                    else:
                        if found_str:
                            strings_list.append(found_str)
                            found_str = ''

            location_file_found = file_found.split("Keyboard/", 1)[1]
            data_list.append(('<br>'.join(strings_list), location_file_found))

        dir_file_found = dirname(file_found).split('Keyboard', 1)[0] + 'Keyboard'

        report = ArtifactHtmlReport('Keyboard Dynamic Lexicon')
        report.start_artifact_report(report_folder, 'Keyboard Dynamic Lexicon')
        report.add_script()
        data_headers = ('Found Strings', 'File Location')
        report.write_artifact_data_table(data_headers, data_list, dir_file_found, html_no_escape=['Found Strings'])
        report.end_artifact_report()

        tsvname = 'Keyboard Dynamic Lexicon'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Keyboard Dynamic Lexicon'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Keyboard Dynamic Lexicon found')

    return
