__artifacts_v2__ = {
    "accountConfig": {
        "name": "Account Configuration",
        "description": "Extracts account configuration information",
        "author": "@AlexisBrignoni",
        "version": "0.2.3",
        "date": "2020-04-30",
        "requirements": "none",
        "category": "Accounts",
        "notes": "",
        "paths": ('*/preferences/SystemConfiguration/com.apple.accounts.exists.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user"
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_plist_file_content

@artifact_processor
def accountConfig(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "com.apple.accounts.exists.plist")
    data_list = []

    pl = get_plist_file_content(source_path)
    for key, val in pl.items():
        data_list.append((key, val))
    
    data_headers = ('Account ID', 'Data Value')
    return data_headers, data_list, source_path
