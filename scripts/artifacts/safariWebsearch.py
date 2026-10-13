__artifacts_v2__ = {
    "safariWebsearch": {
        "name": "Safari Browser - Search Terms",
        "description": "Query text taken from history URLs containing search?q= in each Safari History.db found",
        "author": "@abrignoni",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "Safari Browser",
        "notes": (
            "The history_visits.origin value is reported as stored. Community documentation "
            "describes 1 as a visit synced from another iCloud device, but no primary source was "
            "located. Every History.db the path patterns match is read, including a profile's "
            "History.db under Safari/Profiles/. Profile carries the profile directory name for "
            "those rows and Default for the main history database, and Source Path names the "
            "file each row came from. Search Term is the text between search?q= and the next &, "
            "with + turned into a space and percent-encoded bytes decoded as UTF-8; the URL "
            "column keeps the address as stored. Reading a History.db under Profiles/ was not "
            "exercised on the images in sample_data. A "
            "matching URL is a page address in history; it does not establish who entered the "
            "query."
        ),
        "paths": (
            '**/Safari/History.db*',
            '**/Safari/Profiles/*/History.db*',
        ),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | com.apple.mobilesafari | 95 rows",
            "dexter_ios18": "iOS 18.3.2 | 7 rows",
            "felix_ios17": "iOS 17.6.1 | 4 rows",
            "fsfull002_ios17": "iOS 17.1 | 11 rows",
            "hc_ios18_7": "iOS 18.7.8 | 7 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 26 rows",
            "iphone14plus_ios18": "iOS 18.0 | 12 rows",
            "otto_ios17": "iOS 17.5.1 | 33 rows",
            "abe_ios16": "iOS 16.5 | 41 rows",
            "felix23_ios16": "iOS 16.5 | 5 rows",
            "hickman_ios13": "iOS 13.3.1 | 6 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 29 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    }
}

from urllib.parse import unquote_plus

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records


def _profile(source_path):
    parts = source_path.replace('\\', '/').split('/')
    if len(parts) >= 3 and parts[-3] == 'Profiles':
        return parts[-2]
    return 'Default'


@artifact_processor
def safariWebsearch(context):
    data_headers = (('Visit Time', 'datetime'), 'Search Term', 'URL', 'Visit Count', 'Title',
                    'Origin (as stored)', 'Load Successful', 'Visit ID', 'Redirect Source',
                    'Redirect Destination', 'Profile', 'Source Path')
    data_list = []

    source_paths = sorted({str(file_found) for file_found in context.get_files_found()
                           if str(file_found).endswith('History.db')})
    if not source_paths:
        return data_headers, data_list, ''

    # visit_time is Apple absolute (Cocoa) time on iOS <= 18. Untested
    # expectation for iOS 26+: a Unix-epoch value would exceed this threshold.
    # Cocoa values for realistic dates stay well below the 978307200 offset
    # (year 2032 in Cocoa time), while Unix values are always above it, so the
    # magnitude disambiguates the two encodings.
    query = '''
    SELECT
        CASE
            WHEN history_visits.visit_time > 978307200
                THEN datetime(history_visits.visit_time, 'unixepoch')
            ELSE datetime(history_visits.visit_time + 978307200, 'unixepoch')
        END,
        history_items.url,
        history_items.visit_count,
        history_visits.title,
        history_visits.origin,
        history_visits.load_successful,
        history_visits.id,
        history_visits.redirect_source,
        history_visits.redirect_destination
    FROM history_items, history_visits
    WHERE history_items.id = history_visits.history_item
        AND history_items.url LIKE '%search?q=%'
    ORDER BY
        CASE
            WHEN history_visits.visit_time > 978307200 THEN history_visits.visit_time
            ELSE history_visits.visit_time + 978307200
        END,
        history_visits.id
    '''
    for source_path in source_paths:
        relative_path = context.get_relative_path(source_path)
        profile = _profile(source_path)
        for row in get_sqlite_db_records(source_path, query):
            url = row[1] or ''
            search = (unquote_plus(url.split('search?q=')[1].split('&')[0])
                      if 'search?q=' in url else '')
            data_list.append((row[0], search, row[1], row[2], row[3], row[4], row[5], row[6],
                              row[7], row[8], profile, relative_path))

    sources = '\n'.join(context.get_relative_path(path) for path in source_paths)
    return data_headers, data_list, sources
