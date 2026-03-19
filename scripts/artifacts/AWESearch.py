__artifacts_v2__ = {
    "get_AWESearch": {
        "name": "TikTok",
        "description": "",
        "author": "@gforce4n6",
        "creation_date": "2023-02-25",
        "last_update_date": "2022-09-26",
        "requirements": "none",
        "category": "TikTok",
        "notes": "",
        "paths": ('*/Documents/search_history/history_words/AWESearchHistory*',),
        "output_types": "standard",
    }
}

from scripts.ilapfuncs import convert_cocoa_core_data_ts_to_utc, get_plist_file_content ,artifact_processor

@artifact_processor
def get_AWESearch(context):
    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        
        pl = get_plist_file_content(file_found)
        for x in pl:
            kword = (x['keyword'])
            cocoatime = (x['time'])
            timestamp = convert_cocoa_core_data_ts_to_utc(cocoatime)
            data_list.append((timestamp, kword, file_found))
            
    data_headers = (('Time', 'datetime'), 'Keyword', 'Source File')
    return data_headers, data_list, 'see Source File for more info'


