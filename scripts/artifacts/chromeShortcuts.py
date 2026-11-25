"""Omnibox shortcuts from the Shortcuts database of Chromium based browsers on iOS."""

__artifacts_v2__ = {
    "chromeShortcuts": {
        "name": "Chromium - Omnibox Shortcuts",
        "description": "Rows of the omni_box_shortcuts table from the Shortcuts database of Chromium based browsers: "
                       "the stored input text, the URL and the text stored with it, the match type and transition, "
                       "the hit count and the last access time.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-22",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "Browsers",
        "notes": "Reads the omni_box_shortcuts table of each Shortcuts database directly inside a profile folder under"
                 " Google/Chrome, Microsoft/Edge or Chromium in Library/Application Support; one row per table row. "
                 "Measured on the nine images listed in sample_data: 10 databases, 4 of them with rows, 46 rows in "
                 "total. Browser Name uses the same container identifier logic as the other Chromium artifacts and "
                 "held one value, Chrome, on all 46 rows. Profile Folder is the folder holding the database. Profile "
                 "Folder held one value per image: Default on cookbook_ios1751 and otto_ios17 and a UUID-shaped name "
                 "on dexter_ios18 and wilkerson_iphone16_ios26. No tested image had two profile folders with a "
                 "Shortcuts database, so a browser with more than one profile is unexercised. Chromium source is cited"
                 " at commit 33f34ef179f55596f6c2fc8a55878b7ccf6276e4. Input Text is the text column, which the source"
                 " describes as the user's original input string "
                 "(https://chromium.googlesource.com/chromium/src/+/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/omnibox/browser/shortcuts_database.h#86)."
                 " The writer can expand the last word of the input to a full word of the match before it stores the "
                 "text "
                 "(https://chromium.googlesource.com/chromium/src/+/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/omnibox/browser/shortcuts_backend.cc#80"
                 " and "
                 "https://chromium.googlesource.com/chromium/src/+/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/omnibox/browser/shortcuts_backend.cc#403),"
                 " so Input Text can hold characters the user did not type. Fill Into Edit is fill_into_edit as "
                 "stored. On the 46 rows Input Text equals Fill Into Edit on 19 and is a case-insensitive prefix of it"
                 " on 40, the 19 equal rows included. Last Access Time is last_access_time, bound with BindTime "
                 "(https://chromium.googlesource.com/chromium/src/+/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/omnibox/browser/shortcuts_database.cc#48),"
                 " which stores microseconds since the Windows epoch "
                 "(https://chromium.googlesource.com/chromium/src/+/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/sql/statement.cc#43),"
                 " and it is read as microseconds since 1601-01-01 UTC. The 46 stored values are 17-digit integers and"
                 " decode to dates from 2024 to 2026. The header comment in shortcuts_database.h at the same commit "
                 "says the time is stored in seconds "
                 "(https://chromium.googlesource.com/chromium/src/+/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/omnibox/browser/shortcuts_database.h#26);"
                 " the BindTime source and the stored values both show microseconds. The source describes the time as "
                 "the last time the shortcut was selected and Hits (number_of_hits) as how many times it was selected "
                 "(https://chromium.googlesource.com/chromium/src/+/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/omnibox/browser/shortcuts_database.h#88)."
                 " Hits held 1 on all 46 rows. It is kept because the source defines it as a selection count, so a "
                 "value above 1 on another extraction is shown. Match Type is the type column, an "
                 "AutocompleteMatchType value shown as stored with the name the enum gives it "
                 "(https://chromium.googlesource.com/chromium/src/+/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/omnibox/browser/autocomplete_match_type.h#16)."
                 " The names are those of the enum at that commit. The writer's version 1 migration rewrote stored "
                 "types 9 to 12 as 13 to 16 "
                 "(https://chromium.googlesource.com/chromium/src/+/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/omnibox/browser/shortcuts_database.cc#390),"
                 " so in a database with no meta table, which the source treats as version 0, those values are named "
                 "by the value they migrate to and marked as pre-migration numbering. Where a meta table exists but "
                 "its version cannot be read, values 9 to 12 are shown as the number alone because their numbering "
                 "cannot be established. All 10 tested databases were at version 2, so those branches are covered by "
                 "synthetic tests only (admin/test/scripts/test_chrome_shortcuts.py). Transition is the transition "
                 "column, a ui::PageTransition value: the name is that of its low byte, and any higher qualifier bits "
                 "are shown in hex "
                 "(https://chromium.googlesource.com/chromium/src/+/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/ui/base/page_transition_types.h#113)."
                 " On the 46 rows only two pairs occur: 7 (SEARCH_HISTORY) with 5 (GENERATED) on 45 rows and 1 "
                 "(HISTORY_URL) with 0 (LINK) on 1 row. No qualifier bits were set, so that branch is covered by a "
                 "synthetic test only (same test file). On wilkerson_iphone16_ios26 Keyword, Match Type and Transition"
                 " each held one value on all 30 rows. URL, Description and Keyword are stored values. Description has"
                 " a value on 3 of the 46 rows and no value on any row of dexter_ios18 or wilkerson_iphone16_ios26. "
                 "Keyword was blank on 1 row. Not reported: id, contents, which equalled fill_into_edit on all 46 "
                 "rows, document_type, which held 0 on all 46 rows, and contents_class and description_class. All 46 "
                 "rows came from Chrome. The one Edge database (hickman_ios15) and the two Brave databases (hc_ios18_7"
                 " and hc_ios26, under the Chromium folder) held no rows, and the run staged no other Edge or Brave "
                 "database, so Edge and Brave are unexercised with rows.",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 2 rows",
            "dexter_ios18": "iOS 18.3.2 | 13 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 1 row",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 30 rows",
        },
        "paths": (
            '*/Library/Application Support/Google/Chrome/*/Shortcuts*',
            '*/Library/Application Support/Microsoft/Edge/*/Shortcuts*',
            '*/Library/Application Support/Chromium/*/Shortcuts*',
        ),
        "output_types": "standard",
        "artifact_icon": "search",
    },
}

import datetime
import os
import sqlite3

from scripts.artifacts.chrome import get_browser_name
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly

_WEBKIT_EPOCH = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)
_BROWSER_FOLDERS = ('Chrome', 'Edge', 'Chromium')

# Chromium at 33f34ef179f55596f6c2fc8a55878b7ccf6276e4.
# ui/base/page_transition_types.h: the core transition is the low byte of the stored value.
_TRANSITIONS = {
    0: 'LINK', 1: 'TYPED', 2: 'AUTO_BOOKMARK', 3: 'AUTO_SUBFRAME', 4: 'MANUAL_SUBFRAME',
    5: 'GENERATED', 6: 'AUTO_TOPLEVEL', 7: 'FORM_SUBMIT', 8: 'RELOAD', 9: 'KEYWORD',
    10: 'KEYWORD_GENERATED',
}
# components/omnibox/browser/autocomplete_match_type.h
_MATCH_TYPES = {
    0: 'URL_WHAT_YOU_TYPED', 1: 'HISTORY_URL', 2: 'HISTORY_TITLE', 3: 'HISTORY_BODY',
    4: 'HISTORY_KEYWORD', 5: 'NAVSUGGEST', 6: 'SEARCH_WHAT_YOU_TYPED', 7: 'SEARCH_HISTORY',
    8: 'SEARCH_SUGGEST', 9: 'SEARCH_SUGGEST_ENTITY', 10: 'SEARCH_SUGGEST_TAIL',
    11: 'SEARCH_SUGGEST_PERSONALIZED', 12: 'SEARCH_SUGGEST_PROFILE', 13: 'SEARCH_OTHER_ENGINE',
    14: 'EXTENSION_APP_DEPRECATED', 15: 'CONTACT_DEPRECATED', 16: 'BOOKMARK_TITLE',
    17: 'NAVSUGGEST_PERSONALIZED', 18: 'CALCULATOR', 19: 'CLIPBOARD_URL', 20: 'VOICE_SUGGEST',
    21: 'PHYSICAL_WEB_DEPRECATED', 22: 'PHYSICAL_WEB_OVERFLOW_DEPRECATED',
    23: 'TAB_SEARCH_DEPRECATED', 24: 'DOCUMENT_SUGGESTION', 25: 'PEDAL', 26: 'CLIPBOARD_TEXT',
    27: 'CLIPBOARD_IMAGE', 28: 'TILE_SUGGESTION', 29: 'TILE_NAVSUGGEST', 30: 'OPEN_TAB',
    31: 'HISTORY_CLUSTER', 32: 'NULL_RESULT_MESSAGE', 33: 'STARTER_PACK',
    34: 'TILE_MOST_VISITED_SITE', 35: 'TILE_REPEATABLE_QUERY', 36: 'HISTORY_EMBEDDINGS',
    37: 'FEATURED_ENTERPRISE_SEARCH', 38: 'HISTORY_EMBEDDINGS_ANSWER', 39: 'TAB_GROUP',
    40: 'CROSS_DEVICE_TAB',
}


def _webkit(value):
    """Microseconds since 1601-01-01 UTC, or '' for an empty or unusable value."""
    if not value:
        return ''
    try:
        return _WEBKIT_EPOCH + datetime.timedelta(microseconds=int(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _named(value, names):
    """The stored integer with the enum name the cited source gives it."""
    if not isinstance(value, int):
        return value
    name = names.get(value)
    return f'{value} ({name})' if name else str(value)


def _transition(value):
    if not isinstance(value, int):
        return value
    value &= 0xFFFFFFFF  # stored as a signed 32-bit int; a qualifier can set the sign bit
    core = value & 0xFF
    text = _named(core, _TRANSITIONS)
    if value != core:
        text += f', qualifiers 0x{value & 0xFFFFFF00:08X}'
    return text


def _match_type(value, version):
    """Name a stored match type by the numbering its database version establishes.

    Version 0 (no meta table) predates the version 1 migration, which rewrote stored types 9 to
    12 as 13 to 16, so those are named by the value they migrate to. With an unreadable version
    the numbering of those four values is unknown, so they stay as the bare number.
    """
    if isinstance(value, int) and 9 <= value <= 12:
        if version == 0:
            return f'{value} ({_MATCH_TYPES[value + 4]}, pre-migration numbering)'
        if version is None:
            return str(value)
    return _named(value, _MATCH_TYPES)


def _version(db):
    """The meta table's version, 0 when there is no meta table, None when it cannot be read."""
    try:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'meta'").fetchone():
            return 0
        row = db.execute("SELECT value FROM meta WHERE key = 'version'").fetchone()
        return int(row[0]) if row else None
    except (sqlite3.Error, TypeError, ValueError):
        return None


def _stores(context):
    """Shortcuts files directly inside a profile folder of a Chromium browser folder, once each."""
    found = set()
    for path in context.get_files_found():
        path = str(path)
        if os.path.basename(path) != 'Shortcuts' or os.path.isdir(path):
            continue
        profile_folder = os.path.dirname(path)
        if os.path.basename(os.path.dirname(profile_folder)) in _BROWSER_FOLDERS:
            found.add(path)
    return sorted(found)


@artifact_processor
def chromeShortcuts(context):
    data_list = []
    sources = []
    for path in _stores(context):
        db = open_sqlite_db_readonly(path)
        if db is None:
            continue
        try:
            version = _version(db)
            rows = db.execute('''
                SELECT last_access_time, text, fill_into_edit, url, description, keyword,
                       type, transition, number_of_hits
                FROM omni_box_shortcuts ORDER BY last_access_time, id''').fetchall()
        except sqlite3.Error as error:
            logfunc(f'Omnibox Shortcuts: could not read {context.get_relative_path(path)}: {error}')
            continue
        finally:
            db.close()
        sources.append(path)
        browser = get_browser_name(path)
        profile = os.path.basename(os.path.dirname(path))
        for (last_access, text, fill_into_edit, url, description, keyword, match_type,
             transition, hits) in rows:
            data_list.append((_webkit(last_access), text, fill_into_edit, url, description, keyword,
                              _match_type(match_type, version), _transition(transition), hits, browser, profile))

    data_headers = (('Last Access Time', 'datetime'), 'Input Text', 'Fill Into Edit', 'URL',
                    'Description', 'Keyword', 'Match Type', 'Transition', 'Hits', 'Browser Name', 'Profile Folder')
    return data_headers, data_list, '\n'.join(sources)
