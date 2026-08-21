__artifacts_v2__ = {
    "firefox_ios_history": {
        "name": "Firefox - Web History",
        "description": "Parses the browsing history recorded by Firefox for iOS, with the "
                       "time of each visit, the address and the page title.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Firefox",
        "notes": "One row per recorded visit. Firefox for iOS keeps its history in places.db, "
                 "a store with the Mozilla schema but not the same timestamp unit as the "
                 "desktop browser: the visit time is Unix milliseconds here, not the "
                 "microseconds desktop Firefox uses, so it is read as milliseconds. A visit "
                 "is joined to its page for the address and title. Visit Type is the value "
                 "the row carries, reported as stored, and Local Visit Count and Remote "
                 "Visit Count are the two counts the page record keeps, which separate visits "
                 "made on this device from visits the account synced from elsewhere. On the "
                 "tested device Is Local Visit was set on every visit and no page carried a "
                 "description, so those two columns were uniform there. Field "
                 "mapping was done against a private sample provided by Mattia; no sample "
                 "data is recorded for it.",
        "paths": ('*/profile.profile/places.db*',),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "globe"
    },
    "firefox_ios_bookmarks": {
        "name": "Firefox - Bookmarks",
        "description": "Parses the bookmarks saved in Firefox for iOS, with the address, "
                       "the title and the time each was added.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Firefox",
        "notes": "One row per bookmark that names an address. The store also holds the "
                 "folders that organise bookmarks, which carry no address and are not "
                 "reported as bookmarks; the folder a bookmark sits in is reported beside it. "
                 "Date Added and Last Modified are Unix milliseconds. On the tested device "
                 "the store held the standard root folders and one saved page. Field mapping "
                 "was done against a private sample provided by Mattia; no sample data is "
                 "recorded for it.",
        "paths": ('*/profile.profile/places.db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "bookmark"
    },
}

import os
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, logfunc

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def _ms(value):
    '''A Unix millisecond value as a UTC datetime, or '' when absent or zero.'''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if not value:
        return ''
    return _EPOCH + timedelta(milliseconds=value)


def _text(value):
    '''A stored value as text, with a stored null read as absent.'''
    return '' if value is None else str(value)


def _databases(files_found):
    '''Every copy of places.db among the matched files.'''
    seen = []
    for found in files_found:
        path = str(found)
        if os.path.basename(path) == 'places.db' and path not in seen:
            seen.append(path)
    return seen


def _rows(path, statement):
    '''The rows a statement returns, or nothing when the table is absent.'''
    try:
        return list(get_sqlite_db_records(path, statement))
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'Firefox iOS: could not read from places.db: {error}')
        return []


@artifact_processor
def firefox_ios_history(context):
    data_list = []
    source_files = []

    for path in _databases(context.get_files_found()):
        relative = context.get_relative_path(path)
        for row in _rows(path, '''
                SELECT v.visit_date, p.url, p.title, v.visit_type, v.is_local,
                       p.visit_count_local, p.visit_count_remote, p.frecency, p.description,
                       p.guid
                FROM moz_historyvisits v
                LEFT JOIN moz_places p ON p.id = v.place_id'''):
            (visit_date, url, title, visit_type, is_local, local, remote, frecency,
             description, guid) = row
            source_files.append(relative)
            data_list.append((
                _ms(visit_date),
                _text(url),
                _text(title),
                _text(visit_type),
                _text(is_local),
                _text(local),
                _text(remote),
                _text(frecency),
                _text(description),
                _text(guid),
                relative,
            ))

    data_list.sort(key=lambda r: (str(r[0]), str(r[9])), reverse=True)

    data_headers = (
        ('Visit Time', 'datetime'),
        'URL',
        'Title',
        'Visit Type (as stored)',
        'Is Local Visit (as stored)',
        'Local Visit Count',
        'Remote Visit Count',
        'Frecency (as stored)',
        'Description',
        'Page GUID',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def firefox_ios_bookmarks(context):
    data_list = []
    source_files = []

    for path in _databases(context.get_files_found()):
        relative = context.get_relative_path(path)
        # Folder titles by id, so a bookmark can name the folder it sits in.
        folders = {}
        for identifier, title, kind in _rows(
                path, 'SELECT id, title, type FROM moz_bookmarks'):
            if kind == 2:
                folders[identifier] = _text(title)

        for row in _rows(path, '''
                SELECT b.dateAdded, b.lastModified, p.url, b.title, p.title, b.parent,
                       b.guid, b.position
                FROM moz_bookmarks b
                LEFT JOIN moz_places p ON p.id = b.fk
                WHERE b.type = 1 AND p.url IS NOT NULL'''):
            date_added, modified, url, bookmark_title, page_title, parent, guid, position = row
            source_files.append(relative)
            data_list.append((
                _ms(date_added),
                _ms(modified),
                _text(url),
                _text(bookmark_title) or _text(page_title),
                folders.get(parent, _text(parent)),
                _text(position),
                _text(guid),
                relative,
            ))

    data_list.sort(key=lambda r: (str(r[0]), str(r[6])), reverse=True)

    data_headers = (
        ('Date Added', 'datetime'),
        ('Last Modified', 'datetime'),
        'URL',
        'Title',
        'Folder',
        'Position',
        'GUID',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))
