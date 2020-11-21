import os
import plistlib
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, is_platform_windows 

def get_iconsScreen(files_found, report_folder, seeker):
    data_list = []
    data_pre_list = []
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        plist = plistlib.load(fp)
        for key, val in plist.items():
            if key == "buttonBar":
                bbar = val
            elif key == "iconLists":
                icon = val

        for x in range(0, len(icon)):
            page = icon[x]
            htmlstring = (f"<table><tr>")
            htmlstring = htmlstring + (f'<td colspan="4"> Icons screen #{x}</td>')
            for y in range(0, len(page)):
                rows = page[y]
                if (y == 0) or (y % 4 == 0):
                    htmlstring = htmlstring + ("</tr><tr>")
                    
                if isinstance(rows, dict):
                    var = rows
                    foldername = var['displayName']
                    rows = (f'Folder: {foldername}')
                    bundlesinfolder = var['iconLists'][0]
                    for items in bundlesinfolder:
                        rows = rows + '<br>' + items
                
                htmlstring = htmlstring + (f"<td width = 25%>{rows}</td>")
            htmlstring = htmlstring + ("</tr></table>")
            data_list.append((htmlstring,))

        htmlstring = ''
        htmlstring = (f'<table><tr> <td colspan="4"> Icons bottom bar</td></tr><tr>')
        for x in range(0, len(bbar)):
            htmlstring = htmlstring +(f"<td width = 25%>{bbar[x]}</td>")
        htmlstring = htmlstring +("</tr></table>")
        data_list.append((htmlstring,))

        logfunc("Screens: " + str(len(icon)))

        report = ArtifactHtmlReport(f'Apps per screen')
        report.start_artifact_report(report_folder, f'Apps per screen')
        report.add_script()
        data_headers = ((f'Apps per Screens',))     
        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()
     
        