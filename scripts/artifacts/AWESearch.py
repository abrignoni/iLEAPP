__artifacts_v2__ = {
    "get_AWESearch": {
        "name": "TikTok",
        "description": "Parses TikTok in-app search terms and timestamps from the AWESearchHistory file.",
        "author": "@gforce4n6",
        "creation_date": "2023-02-25",
        "last_update_date": "2026-07-10",
        "requirements": "none",
        "category": "TikTok",
        "notes": "",
        "paths": ('*/Documents/search_history/history_words/AWESearchHistory*',),
        "output_types": "standard",
        "artifact_icon": "brand-tiktok",
        "sample_data": {
            "otto_ios17": "iOS 17.5.1 | TikTok 35.6.0 | 6 rows",
            "dexter_ios18": "iOS 18.3.2 | TikTok - Videos, Shop & LIVE 41.8.0 | 3 rows",
            "iphone12_ios18": "iOS 18.7 | TikTok - Videos, Shop & LIVE 42.7.0 | 4 rows",
            "abe_ios16": "iOS 16.5 | TikTok 30.0.0 | 8 rows",
        },
    }
}

from scripts.ilapfuncs import convert_cocoa_core_data_ts_to_utc, get_plist_file_content ,artifact_processor

@artifact_processor
def get_AWESearch(context):
    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        
        pl = get_plist_file_content(file_found)
        # Older TikTok versions store a list of search entries at the root;
        # newer versions wrap the same entries in a dict under 'historyList'.
        if isinstance(pl, dict):
            entries = pl.get('historyList') or []
        else:
            entries = pl or []
        for x in entries:
            if not isinstance(x, dict):
                continue
            kword = (x['keyword'])
            cocoatime = (x['time'])
            timestamp = convert_cocoa_core_data_ts_to_utc(cocoatime)
            data_list.append((timestamp, kword, context.get_relative_path(file_found)))
            
    data_headers = (('Time', 'datetime'), 'Keyword', 'Source File')
    return data_headers, data_list, 'see Source File for more info'


