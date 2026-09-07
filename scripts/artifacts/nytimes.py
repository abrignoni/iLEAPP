__artifacts_v2__ = {
    "nytimes_recently_viewed": {
        "name": "New York Times - Recently Viewed Articles",
        "description": "Entries of the New York Times app's recently viewed list, with the "
                       "stored time and headline of each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "New York Times",
        "notes": "One row per entry of the app's recently viewed list, which it keeps in "
                 "Library/Application Support/productionNewsreaderDatabase.sqlite. That file is "
                 "a YapDatabase, so its rows are a collection name, a key and a serialised "
                 "value, and the list is the single row of the RecentlyViewedList collection; "
                 "the value is an NSKeyedArchiver archive and is resolved with the reader "
                 "vendored at scripts/nska_deserialize.py. Each entry carries a stored date "
                 "along with the headline, byline, summary and address the app held for it; a "
                 "row records an entry in the app's recently viewed list with that date. The "
                 "stored dates are NSDate values, which are seconds since 2001 in UTC, and are "
                 "reported as UTC. The archive carries a maximumNumberOfRecentEntries value, "
                 "which the artifact reports on each row; it was 200 on the tested image. "
                 "Capping was not exercised on a tested image, and the oldest row is not "
                 "established as the first article ever read. The tested image held one entry, "
                 "so this artifact is proven on a single row and its columns are otherwise the "
                 "ones the archive declares. Nothing else in the same database is reported here: "
                 "the Resource (3,265 rows), Article (250), ImageContent (263) and Video (7) "
                 "collections on the tested image hold article and asset content rather than a "
                 "record of reading, and the Section, FeedSectionItems, FeedCollection, "
                 "ChannelGroups and configuration collections hold feed and configuration data. "
                 "The sibling userSettingsDatabase.sqlite holds display preferences such as the "
                 "theme and the font size and is not reported either. Kicker held no value on "
                 "the single entry of the tested image and is reported as stored.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/productionNewsreaderDatabase.sqlite*',),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "book-open",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | New York Times | 1 row",
        },
    },
}

import io
import os
from datetime import datetime, timezone

import nska_deserialize as nd

from scripts.ilapfuncs import (artifact_processor, does_table_exist_in_db, get_sqlite_db_records,
                               logfunc)

_STORE_NAME = 'productionNewsreaderDatabase.sqlite'
_COLLECTION = 'RecentlyViewedList'


def _stores(files_found):
    '''Every newsreader database among the matched files, directories skipped.'''
    seen = []
    for found in files_found:
        path = str(found)
        if os.path.isdir(path):
            continue
        if os.path.basename(path) == _STORE_NAME and path not in seen:
            seen.append(path)
    return seen


def _text(value):
    '''A stored value as text, with a stored null read as absent.'''
    return '' if value is None else str(value)


def _utc(value):
    '''An NSDate the archive resolved to a naive datetime, as an aware UTC datetime.'''
    if not isinstance(value, datetime):
        return ''
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _url(value):
    '''The address an archived NSURL holds, joined from its base and relative parts.'''
    if isinstance(value, str):
        return value
    if not isinstance(value, dict):
        return ''
    base = _text(value.get('NS.base'))
    relative = _text(value.get('NS.relative'))
    return (base + relative) if base else relative


def _asset_id(value):
    '''The asset identifier an archived content-source record carries, or ''.

    The record is a dictionary rather than a URL, so it is read by its own key instead of
    being joined the way the address fields are.
    '''
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return _text(value.get('assetID'))
    return ''


def _entries(path):
    '''The items the recently viewed list holds, or nothing when it cannot be read.'''
    if not does_table_exist_in_db(path, 'database2'):
        logfunc('New York Times: database2 is not in this productionNewsreaderDatabase.sqlite')
        return []
    try:
        rows = list(get_sqlite_db_records(
            path, f"SELECT data FROM database2 WHERE collection = '{_COLLECTION}'"))
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'New York Times: could not read the recently viewed list: {error}')
        return []
    items = []
    for (blob,) in rows:
        if not blob:
            continue
        try:
            archive = nd.deserialize_plist(io.BytesIO(bytes(blob)))
        except Exception as error:               # pylint: disable=broad-except
            logfunc(f'New York Times: the recently viewed list did not resolve: {error}')
            continue
        if not isinstance(archive, dict):
            continue
        cap = archive.get('maximumNumberOfRecentEntries')
        for item in archive.get('items') or []:
            if isinstance(item, dict):
                items.append((item, cap))
    return items


@artifact_processor
def nytimes_recently_viewed(context):
    data_list = []
    sources = _stores(context.get_files_found())

    for source_path in sources:
        for item, cap in _entries(source_path):
            short = item.get('shortForm') if isinstance(item.get('shortForm'), dict) else {}
            source = (item.get('contentSource')
                      if isinstance(item.get('contentSource'), dict) else {})
            data_list.append((
                _utc(item.get('readDate')), _text(short.get('headline')),
                _text(short.get('byline')), _text(short.get('summary')),
                _text(short.get('kicker')), _text(short.get('tone')),
                _utc(short.get('lastUpdateDate')), _url(item.get('url')),
                _url(source.get('url')), _text(source.get('kind')),
                _asset_id(source.get('nytIdentifier')), '' if cap is None else _text(cap),
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)

    data_headers = (
        ('Read Date', 'datetime'), 'Headline', 'Byline', 'Summary', 'Kicker (as stored)',
        'Tone (as stored)', ('Article Last Updated', 'datetime'), 'Article URL',
        'Content Source URL', 'Content Source Kind (as stored)', 'Article Identifier',
        'List Capacity (as stored)',
    )
    return data_headers, data_list, '\n'.join(sources)
