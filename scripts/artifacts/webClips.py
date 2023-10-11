import os
import plistlib
import base64

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 


def get_webClips(files_found, report_folder, seeker, wrap_text, timezone_offset):
    webclip_data = {}
    data_list = []
    for path_val in files_found:
        # Extract the unique identifier
        pathstr = str(path_val).replace("\\", "/")
        
        unique_id = pathstr.split("/WebClips/")[1].split(".webclip/")[0]
        if unique_id.endswith('.webclip'):
            unique_id = unique_id[:-8]
        if unique_id != "" and unique_id not in webclip_data:
            webclip_data[unique_id] = {
                "Info": "",
                "Icon_path": "",
                "Icon_data": "",
                "Title": "",
                "URL": "",
            }
        # Is this the path to the info.plist?
        if "Info.plist" in pathstr:
            webclip_data[unique_id]["Info"] = path_val

        # Is this the path to the icon?
        if "icon.png" in pathstr:
            webclip_data[unique_id]["Icon_path"] = path_val
    
    logfunc(f"Webclips found: {len(webclip_data)} ")

    for unique_id, data in webclip_data.items():
        # Info plist information
        #logfunc(str(data))
        info_plist_raw = open(data["Info"], "rb")
        info_plist = plistlib.load(info_plist_raw)
        webclip_data[unique_id]["Title"] = info_plist["Title"]
        webclip_data[unique_id]["URL"] = info_plist["URL"]
        info_plist_raw.close()

        # Open and convert icon into b64 for serialisation in report
        icon_data_raw = open(data["Icon_path"], "rb")
        icon_data = base64.b64encode(icon_data_raw.read()).decode("utf-8")
        webclip_data[unique_id]["Icon_data"] = icon_data
        icon_data_raw.close()
        
    # Create the report
    for unique_id, data in webclip_data.items():
        htmlstring = (f'<table>')
        htmlstring = htmlstring +('<tr>')
        htmlstring = htmlstring +(f'<td><img src="data:image/png;base64,{data["Icon_data"]}"></td>')
        htmlstring = htmlstring +(f'<td><b>UID:{unique_id}</b><br> Title: {data["Title"]}<br>URL: {data["URL"]}</td>')
        htmlstring = htmlstring +('</tr>')
        htmlstring = htmlstring +('</table>')
        data_list.append((htmlstring,))
        
    
    report = ArtifactHtmlReport(f'WebClips')
    report.start_artifact_report(report_folder, f'WebClips')
    report.add_script()
    data_headers = ((f'WebClips',))     
    report.write_artifact_data_table(data_headers, data_list, files_found[0], html_escape=False)
    report.end_artifact_report()

__artifacts__ = {
    "webClips": (
        "iOS Screens",
        ('*WebClips/*.webclip/*'),
        get_webClips)
}