__artifacts_v2__ = {
    "safariFavicons": {
        "name": "Safari Browser - Favicons",
        "description": "Favicon cache entries (page URL, icon URL, dimensions) from each Favicons.db found under an app container's Library/Image Cache/Favicons",
        "author": "@abrignoni",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "Safari Browser",
        "notes": (
            "Every Favicons.db the path pattern matches is read, and Source Path names the file "
            "each row came from. The path pattern matches any app container, so a row is not "
            "limited to Safari by the pattern; on every image in sample_data the container was "
            "com.apple.mobilesafari. "
            "Timestamp is read as seconds since 2001-01-01 unless the value is above 978307200, "
            "when it is read as Unix seconds."
        ),
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
                    'Generated Representations?', 'Source Path')
    data_list = []

    source_paths = sorted({str(file_found) for file_found in context.get_files_found()
                           if str(file_found).endswith('Favicons.db')})
    if not source_paths:
        return data_headers, data_list, ''

    # "timestamp" is Apple absolute (Cocoa) time on iOS <= 18. Untested
    # expectation for iOS 26+: a Unix-epoch value would exceed this threshold.
    # Cocoa values for realistic dates stay well below the 978307200 offset
    # (year 2032 in Cocoa time), while Unix values are always above it, so the
    # magnitude disambiguates the two encodings.
    query = '''
    SELECT
        CASE
            WHEN "timestamp" > 978307200
                THEN datetime("timestamp", 'unixepoch')
            ELSE datetime('2001-01-01', "timestamp" || ' seconds')
        END,
        page_url.url,
        icon_info.url,
        icon_info.width,
        icon_info.height,
        icon_info.has_generated_representations
    FROM icon_info
    LEFT JOIN page_url ON icon_info.uuid = page_url.uuid
    '''
    for source_path in source_paths:
        relative_path = context.get_relative_path(source_path)
        for row in get_sqlite_db_records(source_path, query):
            data_list.append(tuple(row) + (relative_path,))

    sources = '\n'.join(context.get_relative_path(path) for path in source_paths)
    return data_headers, data_list, sources
