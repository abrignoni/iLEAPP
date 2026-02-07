__artifacts_v2__ = {
    "get_webClips": {
        "name": "iOS Screens",
        "description": "",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-04-20",
        "last_update_date": "2025-11-20",
        "requirements": "none",
        "category": "Home Screen",
        "notes": "",
        "paths": ('*WebClips/*.webclip/*',),
        "output_types": "standard",
        "artifact_icon": "bookmark"
    }
}
import os
from scripts.ilapfuncs import (
    logfunc,
    artifact_processor,
    check_in_media,
    get_plist_file_content,
    )


@artifact_processor
def get_webClips(context):
    files_found = context.get_files_found()
    webclip_data = {}
    data_list = []
    source_path = ''
    for path_val in files_found:
        # Extract the unique identifier
        pathstr = str(path_val).replace("\\", "/")
        if not source_path:
            source_path = pathstr
        try:
            unique_id = pathstr.split("/WebClips/")[1].split(".webclip/")[0]
            if unique_id.endswith('.webclip'):
                unique_id = unique_id[:-8]
        except IndexError:
            continue
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
        # logfunc(str(data))
        title = ""
        url = ""
        icon_ref = ""
        if data["Info"]:
            info_plist = get_plist_file_content(data["Info"])
            if info_plist:
                title = info_plist.get("Title", "")
                url = info_plist.get("URL", "")
        if data["Icon_path"]:
            icon_ref = check_in_media(
                data["Icon_path"],
                f"{unique_id}_icon.png"
                )
        data_list.append((icon_ref, title, url, unique_id, data["Info"]))
    data_headers = (
        ('Icon', 'media'),
        'Title',
        'URL',
        'Unique Identifier',
        'Source File'
    )
    return data_headers, data_list, ''
