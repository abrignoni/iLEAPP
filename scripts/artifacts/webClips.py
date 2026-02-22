import plistlib
import base64

from scripts.ilapfuncs import logfunc, artifact_processor


@artifact_processor
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
        if "Info.plist" in pathstr:
            webclip_data[unique_id]["Info"] = path_val

        if "icon.png" in pathstr:
            webclip_data[unique_id]["Icon_path"] = path_val

    logfunc(f"Webclips found: {len(webclip_data)} ")

    for unique_id, data in webclip_data.items():
        info_plist_raw = open(data["Info"], "rb")
        info_plist = plistlib.load(info_plist_raw)
        webclip_data[unique_id]["Title"] = info_plist["Title"]
        webclip_data[unique_id]["URL"] = info_plist["URL"]
        info_plist_raw.close()

        icon_data_raw = open(data["Icon_path"], "rb")
        icon_data = base64.b64encode(icon_data_raw.read()).decode("utf-8")
        webclip_data[unique_id]["Icon_data"] = icon_data
        icon_data_raw.close()

    for unique_id, data in webclip_data.items():
        htmlstring = '<table>'
        htmlstring = htmlstring + '<tr>'
        htmlstring = htmlstring + f'<td><img src="data:image/png;base64,{data["Icon_data"]}"></td>'
        htmlstring = htmlstring + f'<td><b>UID:{unique_id}</b><br> Title: {data["Title"]}<br>URL: {data["URL"]}</td>'
        htmlstring = htmlstring + '</tr>'
        htmlstring = htmlstring + '</table>'
        data_list.append((htmlstring,))

    data_headers = ('WebClips',)
    return data_headers, data_list, str(files_found[0])

__artifacts_v2__ = {
    "get_webClips": {
        "name": "Web Clips",
        "description": "Home screen web clips with icons and URLs.",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "iOS Screens",
        "notes": "",
        "paths": ('*WebClips/*.webclip/*',),
        "output_types": ["html"],
        "artifact_icon": "globe",
        "html_columns": ["WebClips"]
    }
}
