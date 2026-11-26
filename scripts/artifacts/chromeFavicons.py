__artifacts_v2__ = {
    "chromeFavicons": {
        "name": "Chromium - Favicons",
        "description": "Page URLs that a Chromium-based browser's Favicons database maps to an "
                       "icon, with the icon's URL, type, stored sizes, times and image, and "
                       "whether the urls table of the History database in the same folder holds "
                       "the page URL.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-26",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Browsers",
        "notes": ("One row per icon_mapping row, which Chromium's source describes as a page URL and the id of "
                  "an icon mapped to it, joined to that icon's favicons row (its URL and type) and to its "
                  "favicon_bitmaps rows "
                  "(https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/favicon/core/favicon_database.cc#L41-L90)."
                  " Ported from ALEAPP's chromiumFavicons. Browser comes from the app container's bundle "
                  "identifier through get_browser_name in chrome.py. When the identifier is not a known "
                  "browser, the name comes from folder names in the path. On the tested images Chrome, Brave "
                  "(whose profile is under Application Support/Chromium) and Edge were exercised. Browser held "
                  "one value on every row of each tested image except hickman_ios15 and iphone11_ios17, which "
                  "hold all three. Each browser had one profile folder with rows (Default, or a folder named by"
                  " a UUID on dexter_ios18 and wilkerson_iphone16_ios26), so the profile is not a column. The "
                  "source paths list every Favicons and History file read, including ones that gave no rows. "
                  "Edge's Default-AAD Favicons on hickman_ios15 and iphone11_ios17 held no mappings and gives "
                  "no rows. Page URL is page_url and Icon URL is the icon's url, as stored. Icon Type is "
                  "icon_type named through Chromium's IconType: the database stores 1 shifted left by the "
                  "IconType value less one "
                  "(https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/favicon/core/favicon_database.cc#L993-L998),"
                  " so 1, 2, 4 and 8 are kFavicon, kTouchIcon, kTouchPrecomposedIcon and kWebManifestIcon "
                  "(https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/favicon_base/favicon_types.h#L36-L42);"
                  " any other value is shown as stored. The enum is Chromium's. It was not checked against "
                  "Brave's or Edge's build. Values 1, 2 and 4 occur on the tested images; 8 does not, and the "
                  "shown-as-stored case is covered by a synthetic test "
                  "(admin/test/scripts/test_chrome_favicons.py). Sizes lists the distinct width x height values"
                  " of the icon's bitmaps and Icon shows the bitmap with the largest area. Every icon on the "
                  "tested images had one bitmap. The choice of the largest bitmap and the choice of the latest "
                  "time among several are covered by the synthetic test only. Last Updated and Last Requested "
                  "are the latest last_updated and last_requested of the icon's bitmaps, read as microseconds "
                  "since 1601-01-01 UTC "
                  "(https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/favicon/core/favicon_database.cc#L446,"
                  " "
                  "https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/favicon/core/favicon_database.cc#L451"
                  " and "
                  "https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/sql/statement.cc#L42-L44),"
                  " with a zero value shown blank. Chromium's source describes last_updated as the time the "
                  "favicon was inserted, zero for a bitmap explicitly expired and zero for one fetched on "
                  "demand, and last_requested as the time the bitmap was last requested, non-zero only for one "
                  "fetched on demand "
                  "(https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/favicon/core/favicon_database.cc#L76-L90)."
                  " On every row of the tested images exactly one of the two was set. Time is Last Updated when"
                  " it is set and Last Requested otherwise, so every row with either time has a date in the "
                  "timeline. Time and Last Updated are identical on every row of abe_ios16, cookbook_ios1751, "
                  "hc_ios18_7, hc_ios26 and otto_ios17, where Last Requested has no value on any row. A time "
                  "too large to convert is shown blank (covered by the synthetic test; none on the tested "
                  "images). In History is a string comparison of Page URL against the urls table of the History"
                  " database in the same folder: Yes when it holds the URL, No when it does not, and blank when"
                  " no readable History sits beside the Favicons database (the blank case did not occur on the "
                  "tested images). No was the value on 78 of the 685 rows of the 10 tested images with rows. "
                  "The visits table is not read, so Yes does not establish a visit, and No does not establish "
                  "that the page was not visited. Why a mapped URL is absent from History was not established. "
                  "Page URL Type is page_url_type named through PageUrlType, 0 kRegular and 1 kRedirect "
                  "(https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/favicon/core/favicon_types.h#L26-L35)."
                  " Chromium adds this column in version 9 of the database "
                  "(https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/favicon/core/favicon_database.cc#L1098-L1103,"
                  " "
                  "https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/favicon/core/favicon_database.cc#L1137-L1140);"
                  " the artifact checks for the column, not the version, and reads a missing column as blank. "
                  "The version 9 databases (dexter_ios18, hc_ios18_7, hc_ios26, wilkerson_iphone16_ios26) "
                  "carried it, set on every row; the version 8 databases on the other tested images lacked it, "
                  "so Page URL Type is blank on every row there. A Favicons or History database that a read-"
                  "only open cannot read, for example one beside a hot rollback journal, is logged and not "
                  "read: a Favicons file then gives no rows, and a History file leaves In History blank. This "
                  "was not exercised: no tested image had a Favicons or History database that could not be "
                  "read. Values not reported include the favicon_bitmaps rows of icons that no page URL maps to"
                  " (none on the tested images)."),
        "paths": (
            '*/Chrome/*/Favicons*',
            '*/Edge/*/Favicons*',
            '*/Chromium/*/Favicons*',
            '*/Chrome/*/History*',
            '*/Edge/*/History*',
            '*/Chromium/*/History*',
        ),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 66 rows (Chrome)",
            "cookbook_ios1751": "iOS 17.5.1 | 21 rows (Chrome)",
            "dexter_ios18": "iOS 18.3.2 | 244 rows (Chrome)",
            "hc_ios18_7": "iOS 18.7.8 | 9 rows (Brave)",
            "hc_ios26": "iOS 26.5.2 | 16 rows (Brave)",
            "hickman_ios15": "iOS 15.3.1 | 30 rows (Chrome, Brave, Edge)",
            "iphone11_ios17": "iOS 17.3 | 28 rows (Chrome, Brave, Edge)",
            "magnet_ios16": "iOS 16.1.1 | 40 rows (Chrome)",
            "otto_ios17": "iOS 17.5.1 | 11 rows (Chrome)",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 220 rows (Chrome)",
            "hickman_ios14": "iOS 14.3 | 0 rows (no file matched the patterns)",
            "hickman_ios13": "iOS 13.3.1 | 0 rows (no file matched the patterns)",
        },
    }
}

import datetime
import os
import sqlite3

from scripts.artifacts.chrome import get_browser_name
from scripts.ilapfuncs import artifact_processor, check_in_embedded_media, logfunc, \
    open_sqlite_db_readonly

# favicons.icon_type holds 1 << (IconType - 1) (see notes), so these are the IconType
# names of the persisted values.
_ICON_TYPES = {1: 'kFavicon', 2: 'kTouchIcon', 4: 'kTouchPrecomposedIcon', 8: 'kWebManifestIcon'}
_PAGE_URL_TYPES = {0: 'kRegular', 1: 'kRedirect'}


def _webkit_to_utc(value):
    '''Chromium time: microseconds since 1601-01-01 UTC. Zero or empty is blank.'''
    if value in (None, 0, ''):
        return ''
    try:
        return datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc) + \
            datetime.timedelta(microseconds=int(value))
    except (OverflowError, ValueError, TypeError):
        return ''


def _enum_label(mapping, value):
    '''"name (value)" when the integer is known, else the value as stored.'''
    if value in (None, ''):
        return ''
    name = mapping.get(value)
    return f'{name} ({value})' if name else str(value)


def _columns(db, table):
    '''The column names of a table, or an empty set when the table does not exist.'''
    return {row[1] for row in db.execute(f'PRAGMA table_info({table})')}


def _read_urls(db):
    if not _columns(db, 'urls'):
        return None
    return {row[0] for row in db.execute('SELECT url FROM urls')}


def _bitmaps(db):
    '''{icon_id: (latest last_updated, latest last_requested, [sizes], largest image)}.

    A column the table lacks reads as NULL: an older database has no last_requested.
    '''
    present = _columns(db, 'favicon_bitmaps')
    requested = 'last_requested' if 'last_requested' in present else 'NULL'
    icons = {}
    for icon_id, updated, req, width, height, image in db.execute(
            f'SELECT icon_id, last_updated, {requested}, width, height, image_data '
            'FROM favicon_bitmaps ORDER BY icon_id, width, height, id'):
        latest_updated, latest_requested, sizes, largest = icons.get(icon_id, (0, 0, [], None))
        size = f'{width}x{height}'
        if size not in sizes:
            sizes.append(size)
        area = (width or 0) * (height or 0)
        if image and (largest is None or area >= largest[0]):
            largest = (area, image)
        icons[icon_id] = (max(latest_updated, updated or 0),
                          max(latest_requested, req or 0), sizes, largest)
    return icons


def _read_favicons(db):
    '''(mapping rows, icons), or None when a required table is missing.'''
    mapping = _columns(db, 'icon_mapping')
    if not mapping or not _columns(db, 'favicons') or not _columns(db, 'favicon_bitmaps'):
        return None
    url_type = 'm.page_url_type' if 'page_url_type' in mapping else 'NULL'
    rows = db.execute(
        f'SELECT m.page_url, m.icon_id, f.url, f.icon_type, {url_type} '
        'FROM icon_mapping m LEFT JOIN favicons f ON f.id = m.icon_id '
        'ORDER BY m.id').fetchall()
    return rows, _bitmaps(db)


def _read(path, reader):
    '''reader(db) on a read-only open of path, or None when it cannot be opened.'''
    db = open_sqlite_db_readonly(path)
    if db is None:
        return None
    try:
        return reader(db)
    finally:
        db.close()


@artifact_processor
def chromeFavicons(context):
    data_headers = (('Time', 'datetime'), ('Last Updated', 'datetime'), ('Last Requested', 'datetime'),
                    'Page URL',
                    'In History', 'Icon URL', 'Icon Type', 'Sizes', ('Icon', 'media'),
                    'Page URL Type', 'Browser')
    files = sorted(str(f) for f in context.get_files_found())
    favicons = [f for f in files if os.path.basename(f) == 'Favicons']
    histories = {os.path.dirname(f): f for f in files if os.path.basename(f) == 'History'}

    data_list = []
    sources = []
    for file_found in favicons:
        try:
            result = _read(file_found, _read_favicons)
        except sqlite3.Error as ex:
            logfunc(f'Chromium Favicons: could not read {context.get_relative_path(file_found)}: '
                    f'{type(ex).__name__}')
            continue
        if result is None:
            logfunc(f'Chromium Favicons: {context.get_relative_path(file_found)} could not be '
                    'opened or has no icon_mapping, favicons or favicon_bitmaps table')
            continue
        rows, icons = result
        sources.append(file_found)

        history_file = histories.get(os.path.dirname(file_found))
        urls = None
        if history_file:
            try:
                urls = _read(history_file, _read_urls)
            except sqlite3.Error as ex:
                logfunc(f'Chromium Favicons: could not read '
                        f'{context.get_relative_path(history_file)}: {type(ex).__name__}')
            if urls is not None:
                sources.append(history_file)

        browser = get_browser_name(file_found)
        for page_url, icon_id, icon_url, icon_type, page_url_type in rows:
            updated, requested, sizes, largest = icons.get(icon_id, (0, 0, [], None))
            media = check_in_embedded_media(file_found, largest[1]) if largest else ''
            in_history = '' if urls is None else ('Yes' if page_url in urls else 'No')
            last_updated, last_requested = _webkit_to_utc(updated), _webkit_to_utc(requested)
            data_list.append((last_updated or last_requested, last_updated, last_requested, page_url,
                              in_history, icon_url or '', _enum_label(_ICON_TYPES, icon_type),
                              ', '.join(sizes), media or '',
                              _enum_label(_PAGE_URL_TYPES, page_url_type), browser))

    return data_headers, data_list, '\n'.join(sources)
