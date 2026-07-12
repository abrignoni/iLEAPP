__artifacts_v2__ = {
    "safariFavicons": {
        "name": "Safari Browser - Favicons",
        "description": "Safari favicon cache entries (page URL, icon URL, dimensions)",
        "author": "",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Safari Browser",
        "notes": "",
        "paths": ('*/Containers/Data/Application/*/Library/Image Cache/Favicons/Favicons.db*',),
        "output_types": "standard",
        "artifact_icon": "photo",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | com.apple.mobilesafari | 153 rows",
            "dexter_ios18": "iOS 18.3.2 | com.apple.mobilesafari | 3 rows",
            "felix_ios17": "iOS 17.6.1 | com.apple.mobilesafari | 9 rows",
            "fsfull002_ios17": "iOS 17.1 | com.apple.mobilesafari | 5 rows",
            "hc_ios18_7": "iOS 18.7.8 | com.apple.mobilesafari | 4 rows",
            "iphone11_ios17": "iOS 17.3 | com.apple.mobilesafari | 3 rows",
            "iphone12_ios18": "iOS 18.7 | com.apple.mobilesafari | 16 rows",
            "iphone14plus_ios18": "iOS 18.0 | com.apple.mobilesafari | 6 rows",
            "otto_ios17": "iOS 17.5.1 | com.apple.mobilesafari | 71 rows",
            "abe_ios16": "iOS 16.5 | com.apple.mobilesafari | 93 rows",
            "felix23_ios16": "iOS 16.5 | com.apple.mobilesafari | 6 rows",
            "hickman_ios13": "iOS 13.3.1 | com.apple.mobilesafari | 8 rows",
            "hickman_ios14": "iOS 14.3 | com.apple.mobilesafari | 11 rows",
            "jess_ios15": "iOS 15.0.2 | com.apple.mobilesafari | 16 rows",
            "magnet_ios16": "iOS 16.1.1 | com.apple.mobilesafari | 1 row",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records


@artifact_processor
def safariFavicons(context):
    data_headers = (('Timestamp', 'datetime'), 'Page URL', 'Icon URL', 'Width', 'Height',
                    'Generated Representations?')
    data_list = []

    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('Favicons.db'):
            source_path = file_found
            break
    if not source_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        datetime('2001-01-01', "timestamp" || ' seconds'),
        page_url.url,
        icon_info.url,
        icon_info.width,
        icon_info.height,
        icon_info.has_generated_representations
    FROM icon_info
    LEFT JOIN page_url ON icon_info.uuid = page_url.uuid
    '''
    for row in get_sqlite_db_records(source_path, query):
        data_list.append(tuple(row))

    return data_headers, data_list, context.get_relative_path(source_path)
