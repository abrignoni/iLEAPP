__artifacts_v2__ = {
    "brave_ios_tabs": {
        "name": "Brave - Open Tabs",
        "description": "Tabs the Brave browser had open, with the page each was showing and the "
                       "thumbnail where the row carries one.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Brave",
        "notes": "One row per row of ZSESSIONTAB in Library/Application Support/Brave.sqlite, and "
                 "one per row of ZTABMO where a store carries that older table instead. The "
                 "Source Table column says which a row came from: three of the four tested images "
                 "use ZSESSIONTAB and the iOS 15 image uses ZTABMO. Last Updated is a Core Data "
                 "time, seconds since 2001, reported in UTC, and read that way every value falls "
                 "inside the period its own image covers. Thumbnail is a JPEG, checked by its own "
                 "leading bytes, stored inside the row, and one is attached to every ZSESSIONTAB "
                 "row, twelve of twelve across the three images. A ZTABMO row stores no image "
                 "bytes and carries a screenshot identifier instead, so those two rows show that "
                 "identifier in the Window ID or Thumbnail ID column and no picture, and whether "
                 "a file named by it survives elsewhere in the container was not established. "
                 "Private read No on every row of all four images, so no private tab was recorded "
                 "on any of them, which is not evidence that none was ever opened. Exactly one "
                 "row per image is marked Selected. Tab ID, and the window identifier a "
                 "ZSESSIONTAB row points at, are stored as sixteen byte values and are rendered "
                 "as UUIDs.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/Brave.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "layers",
        "sample_data": {
                           "hc_ios18_7": "iOS 18.7 | Brave | 6 rows",
                           "hc_ios26": "iOS 26 | Brave | 5 rows",
                           "hickman_ios15": "iOS 15.3.1 | Brave | 2 rows",
                           "iphone11_ios17": "iOS 17.3 | Brave | 1 row",
                       },
    },
    "brave_ios_recently_closed": {
        "name": "Brave - Recently Closed Tabs",
        "description": "Tabs closed in the Brave browser, with the page each was showing when it "
                       "was closed.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Brave",
        "notes": "One row per row of ZRECENTLYCLOSED in Library/Application Support/Brave.sqlite. "
                 "The table is named for closed tabs and each row carries a title, an address, a "
                 "date and a history index. Date Added is a Core Data time, seconds since 2001, "
                 "reported in UTC, and read that way every value falls inside the period its own "
                 "image covers. Two of the four tested images held rows, nine and one, and the "
                 "other two held none, so an absent row is not evidence that no tab was ever "
                 "closed. The row also carries an interaction state blob, which is not read here. "
                 "History Index is reported as stored.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/Brave.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "x-square",
        "sample_data": {
                           "hc_ios18_7": "iOS 18.7 | Brave | 0 rows",
                           "hc_ios26": "iOS 26 | Brave | 9 rows",
                           "hickman_ios15": "iOS 15.3.1 | Brave | 0 rows",
                           "iphone11_ios17": "iOS 17.3 | Brave | 1 row",
                       },
    },
    "brave_ios_recent_searches": {
        "name": "Brave - Recent Searches",
        "description": "Terms held in the Brave browser's recent search list, with the time each "
                       "was added.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Brave",
        "notes": "One row per row of ZRECENTSEARCH in Library/Application Support/Brave.sqlite, "
                 "which is the list the browser keeps of recent searches. Each row carries the "
                 "text, a type, an optional website address and the time it was added. Date Added "
                 "is a Core Data time, seconds since 2001, reported in UTC, and read that way "
                 "every value falls inside the period its own image covers. Three of the four "
                 "tested images held exactly one term each and the fourth held none. Search Type "
                 "held the value 1 on all three rows and Website URL was empty on all three, so "
                 "neither field has enough values here to say what it distinguishes, and both are "
                 "reported as stored. A term that is absent from this list is not evidence that "
                 "it was never searched for.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/Brave.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
                           "hc_ios18_7": "iOS 18.7 | Brave | 0 rows",
                           "hc_ios26": "iOS 26 | Brave | 1 row",
                           "hickman_ios15": "iOS 15.3.1 | Brave | 1 row",
                           "iphone11_ios17": "iOS 17.3 | Brave | 1 row",
                       },
    },
    "brave_ios_bookmarks": {
        "name": "Brave - Bookmarks and Favorites",
        "description": "Entries in the Brave browser's bookmark and favorite lists, with the "
                       "address of each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Brave",
        "notes": "One row per row of ZBOOKMARK in Library/Application Support/Brave.sqlite, which "
                 "carries a favourite flag and a folder flag beside the title and the address. "
                 "Created and Last Visit are Core Data times, seconds since 2001, reported in "
                 "UTC. On all four tested images every row has Favorite set to Yes, an empty "
                 "Custom Title, a Visits (as stored) value of 0, and Created equal to Last Visit. "
                 "On the two older images the six addresses match, one for one, the preloaded "
                 "favourites Brave's published source defines, so those rows are the set the app "
                 "installs and not bookmarks somebody saved. Reference: Brave, "
                 "'PreloadedFavorites.swift', https://github.com/brave/brave-ios/blob/0d693d2d909 "
                 "3dfc975e5c645beedd533c0a4c9e8/Sources/Brave/Frontend/Browser/Favorites/Preloade "
                 "dFavorites.swift. On the two newer images the four addresses are a different "
                 "set that is not in that file, so what created them was not established; their "
                 "four rows were written within 7.4 milliseconds of each other, which is not how "
                 "entries added one at a time would look. Taken together, no row on any tested "
                 "image shows a mark of having been saved by hand, and a row here is not by "
                 "itself evidence that one was. Custom Title is what the app stores when an entry "
                 "is renamed, and it was blank on every row. Folder marks a folder rather than a "
                 "page and was blank on every row. Favorite and Visits (as stored) hold one value "
                 "each across every tested image.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/Brave.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "bookmark",
        "sample_data": {
                           "hc_ios18_7": "iOS 18.7 | Brave | 4 rows",
                           "hc_ios26": "iOS 26 | Brave | 4 rows",
                           "hickman_ios15": "iOS 15.3.1 | Brave | 6 rows",
                           "iphone11_ios17": "iOS 17.3 | Brave | 6 rows",
                       },
    },
    "brave_ios_blocked_resources": {
        "name": "Brave - Blocked Resources",
        "description": "Hosts the Brave browser blocked while loading a site, with the site each "
                       "was blocked on.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Brave",
        "notes": "One row per row of ZBLOCKEDRESOURCE in Library/Application "
                 "Support/Brave.sqlite. Site Domain is the site the page belonged to, Blocked "
                 "Host is the host that was blocked, and Page URL is the address the row carries. "
                 "ZDOMAIN in this table holds the site's domain as text rather than a reference "
                 "to the separate site entry table, so nothing is joined. Timestamp is a Core "
                 "Data time, seconds since 2001, reported in UTC, and it is present on 35 of 54, "
                 "39 of 39 and 14 of 14 rows on three images and on none of the 19 rows of the "
                 "fourth, so a blank there is the store not recording one. Rows span 2 to 5 "
                 "distinct sites per image. On all four tested images every site named here is "
                 "also named by a tab, a closed tab or a bookmark in the same store, so on this "
                 "data the table corroborates those rather than adding a site of its own. Three "
                 "tables in this store are read by nothing here and are named so the omission is "
                 "visible: the site entry table, whose visit count was 0 and whose per site "
                 "protection settings were unset on every row of every tested image; the filter "
                 "list table, which is the browser's blocking configuration; and the playlist "
                 "folder table, which held one default folder on each image.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/Brave.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "shield",
        "sample_data": {
                           "hc_ios18_7": "iOS 18.7 | Brave | 19 rows",
                           "hc_ios26": "iOS 26 | Brave | 54 rows",
                           "hickman_ios15": "iOS 15.3.1 | Brave | 39 rows",
                           "iphone11_ios17": "iOS 17.3 | Brave | 14 rows",
                       },
    },
    "brave_ios_wallet_assets": {
        "name": "Brave - Wallet Assets",
        "description": "Assets listed in the Brave browser's built in crypto wallet, with the chain "
                       "of each and a contract address where one is stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Brave",
        "notes": "One row per row of ZWALLETUSERASSET in Library/Application "
                 "Support/Brave.sqlite, joined to ZWALLETUSERASSETGROUP for the group identifier "
                 "the asset belongs to. The store carries no balance, amount or address column, "
                 "so a row records that the wallet lists that asset, not that any of it is held. "
                 "One of the four tested images had rows, 17 of them, across 16 chain identifiers "
                 "and 16 groups, and one of them carries a contract address; all 17 were marked "
                 "visible, none was marked spam, none was an NFT, and Deletion Flag read No on "
                 "all 17. Those 17 are the native token of each chain plus Brave's own token, "
                 "which is the one carrying a contract address, so they look like a starting list "
                 "rather than a set somebody chose. Whether the app writes them when the wallet "
                 "is first opened or ships with them was not established, so their presence is "
                 "not by itself evidence that a wallet was created or used. Chain ID, Coin and "
                 "Decimals are reported as stored.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/Brave.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "dollar-sign",
        "sample_data": {
                           "hc_ios18_7": "iOS 18.7 | Brave | 0 rows",
                           "hc_ios26": "iOS 26 | Brave | 0 rows",
                           "hickman_ios15": "iOS 15.3.1 | Brave | 0 rows",
                           "iphone11_ios17": "iOS 17.3 | Brave | 17 rows",
                       },
    },
}

import os
import uuid
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import (artifact_processor, check_in_embedded_media,
                               does_table_exist_in_db, get_sqlite_db_records, logfunc)

_CORE_DATA_EPOCH_UTC = datetime(2001, 1, 1, tzinfo=timezone.utc)


def _stores(files_found):
    '''Every Brave.sqlite among the matches, directories and sidecars skipped.'''
    seen = []
    for found in files_found:
        path = str(found)
        if os.path.isdir(path) or path.endswith(('-wal', '-shm')):
            continue
        if os.path.basename(path) == 'Brave.sqlite' and path not in seen:
            seen.append(path)
    return seen


def _rows(path, table, columns):
    '''Rows of a table, or nothing when the store does not have it.'''
    if not does_table_exist_in_db(path, table):
        return []
    try:
        return list(get_sqlite_db_records(path, f'SELECT {columns} FROM {table}'))
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'Brave: could not read {table}: {error}')
        return []


def _text(value):
    '''A stored value as text, with a stored null read as absent.'''
    return '' if value is None else str(value)


def _core_data_to_utc(value):
    '''Core Data seconds since 2001 to an aware UTC datetime, or ''.'''
    if value in (None, ''):
        return ''
    try:
        return _CORE_DATA_EPOCH_UTC + timedelta(seconds=float(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _uuid(value):
    '''A stored 16 byte identifier as a UUID string, other values as text.'''
    if isinstance(value, (bytes, bytearray)) and len(value) == 16:
        return str(uuid.UUID(bytes=bytes(value)))
    return _text(value)


def _flag(value):
    '''A stored boolean as Yes, No or blank, reported as the store holds it.'''
    if value in (None, ''):
        return ''
    return 'Yes' if str(value) not in ('0', '0.0', 'False') else 'No'


@artifact_processor
def brave_ios_tabs(context):
    data_list = []
    sources = []
    for source_path in _stores(context.get_files_found()):
        sources.append(source_path)
        windows = dict(_rows(source_path, 'ZSESSIONWINDOW', 'Z_PK, ZWINDOWID') or [])
        for (updated, title, url, shot, private, selected, tab_id, window) in _rows(
                source_path, 'ZSESSIONTAB',
                'ZLASTUPDATED, ZTITLE, ZURL, ZSCREENSHOTDATA, ZISPRIVATE, ZISSELECTED, '
                'ZTABID, ZSESSIONWINDOW'):
            media = check_in_embedded_media(source_path, shot, _text(title)) if shot else ''
            data_list.append((
                _core_data_to_utc(updated), _text(title), _text(url), media or '',
                _flag(private), _flag(selected), _uuid(tab_id),
                _uuid(windows.get(window, '')), 'ZSESSIONTAB',
            ))
        # An older release keeps its tabs in ZTABMO and its thumbnail in a separate file that
        # the row names by identifier, so that identifier is reported rather than a picture.
        for (updated, title, url, shot, private, selected, tab_id, shot_uuid) in _rows(
                source_path, 'ZTABMO',
                'ZLASTUPDATE, ZTITLE, ZURL, ZSCREENSHOT, ZISPRIVATE, ZISSELECTED, '
                'ZSYNCUUID, ZSCREENSHOTUUID'):
            media = check_in_embedded_media(source_path, shot, _text(title)) if shot else ''
            data_list.append((
                _core_data_to_utc(updated), _text(title), _text(url), media or '',
                _flag(private), _flag(selected), _uuid(tab_id),
                _uuid(shot_uuid), 'ZTABMO',
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)
    data_headers = (
        ('Last Updated', 'datetime'), 'Title', 'URL', ('Thumbnail', 'media'), 'Private',
        'Selected', 'Tab ID', 'Window ID or Thumbnail ID', 'Source Table',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def brave_ios_recently_closed(context):
    data_list = []
    sources = []
    for source_path in _stores(context.get_files_found()):
        sources.append(source_path)
        for (added, title, url, index) in _rows(
                source_path, 'ZRECENTLYCLOSED', 'ZDATEADDED, ZTITLE, ZURL, ZHISTORYINDEX'):
            data_list.append((_core_data_to_utc(added), _text(title), _text(url), _text(index)))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)
    data_headers = (('Date Added', 'datetime'), 'Title', 'URL', 'History Index (as stored)')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def brave_ios_recent_searches(context):
    data_list = []
    sources = []
    for source_path in _stores(context.get_files_found()):
        sources.append(source_path)
        for (added, text, kind, website) in _rows(
                source_path, 'ZRECENTSEARCH', 'ZDATEADDED, ZTEXT, ZSEARCHTYPE, ZWEBSITEURL'):
            data_list.append((_core_data_to_utc(added), _text(text), _text(kind), _text(website)))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)
    data_headers = (('Date Added', 'datetime'), 'Search Text', 'Search Type (as stored)',
                    'Website URL')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def brave_ios_bookmarks(context):
    data_list = []
    sources = []
    for source_path in _stores(context.get_files_found()):
        sources.append(source_path)
        for (created, visited, title, custom, url, visits, favorite, folder) in _rows(
                source_path, 'ZBOOKMARK',
                'ZCREATED, ZLASTVISITED, ZTITLE, ZCUSTOMTITLE, ZURL, ZVISITS, '
                'ZISFAVORITE, ZISFOLDER'):
            data_list.append((
                _core_data_to_utc(created), _core_data_to_utc(visited), _text(title),
                _text(custom), _text(url), _text(visits), _flag(favorite), _flag(folder),
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)
    data_headers = (('Created', 'datetime'), ('Last Visit', 'datetime'), 'Title',
                    'Custom Title', 'URL', 'Visits (as stored)', 'Favorite', 'Folder')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def brave_ios_blocked_resources(context):
    data_list = []
    sources = []
    for source_path in _stores(context.get_files_found()):
        sources.append(source_path)
        for (stamp, host, page, domain) in _rows(
                source_path, 'ZBLOCKEDRESOURCE', 'ZTIMESTAMP, ZHOST, ZFAVICONURL, ZDOMAIN'):
            data_list.append((
                _core_data_to_utc(stamp), _text(domain), _text(host), _text(page),
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)
    data_headers = (('Timestamp', 'datetime'), 'Site Domain', 'Blocked Host', 'Page URL')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def brave_ios_wallet_assets(context):
    data_list = []
    sources = []
    for source_path in _stores(context.get_files_found()):
        sources.append(source_path)
        groups = dict(_rows(source_path, 'ZWALLETUSERASSETGROUP', 'Z_PK, ZGROUPID') or [])
        for (name, symbol, chain, contract, coin, decimals, visible, spam, deleted,
             nft, group) in _rows(
                source_path, 'ZWALLETUSERASSET',
                'ZNAME, ZSYMBOL, ZCHAINID, ZCONTRACTADDRESS, ZCOIN, ZDECIMALS, ZVISIBLE, '
                'ZISSPAM, ZISDELETEDBYUSER, ZISNFT, ZWALLETUSERASSETGROUP'):
            data_list.append((
                _text(name), _text(symbol), _text(chain), _text(contract), _text(coin),
                _text(decimals), _flag(visible), _flag(spam), _flag(deleted), _flag(nft),
                _text(groups.get(group, '')),
            ))

    data_list.sort(key=lambda row: (str(row[10]), str(row[0])))
    data_headers = (
        'Name', 'Symbol', 'Chain ID (as stored)', 'Contract Address', 'Coin (as stored)',
        'Decimals (as stored)', 'Visible', 'Marked Spam', 'Deletion Flag', 'NFT', 'Group ID',
    )
    return data_headers, data_list, '\n'.join(sources)
