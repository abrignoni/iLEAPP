__artifacts_v2__ = {
    "widgetEngagements": {
        "name": "Widget Engagements",
        "description": "Times the system recorded a widget as shown, as dwelled on, or as tapped, "
                       "from the widgetEngagements table of DuetExpertCenter/_ATXInfoSuggestionStore.db, "
                       "including engagements another state in its write-ahead log holds and the "
                       "current state does not",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-30",
        "last_update_date": "2026-10-30",
        "requirements": "none",
        "category": "iOS Screens",
        "notes": "Reads the widgetEngagements table of mobile/Library/DuetExpertCenter/_ATXInfoSuggestionStore.db "
                 "and its -wal. Each row is one engagement. Timestamp is the date column (mostRecentTap or "
                 "mostRecentDwell on the older layout below) read as seconds since "
                 "2001-01-01 UTC; on dexter_ios18 both Tap rows fell within 0.1 second of a Biome App.InFocus "
                 "event for the same Container Bundle ID (com.apple.Music). Engagement names the stored "
                 "engagementType with the names Apple's own NSStringForATXWidgetEngagementType "
                 "(AppPredictionClient.framework) returned when called on macOS 27.0.1 (26A434): 0 unknown, 1 "
                 "tap, 2 significant dwell, 3 shown; migration SQL in the dyld shared cache of that macOS build "
                 "fills 1 from a mostRecentTap column and 2 from mostRecentDwell. Any other value is reported as Unknown with "
                 "the number. Only 1, 2 and 3 occurred on the tested images. What the system counts as shown or "
                 "as a significant dwell, and where the widget was on screen, is not established here. A Tap row "
                 "does not establish that the app named in Container Bundle ID came to the foreground: on "
                 "fsfull002_ios17 (1 Tap) and otto_ios17 (9 Tap) no Biome App.InFocus event for that bundle fell "
                 "within 2 minutes, although each Tap lay inside the span the Biome stream covered. Widget "
                 "Extension, Widget Kind, Container Bundle ID and Widget Unique ID are extensionBundleId, "
                 "widgetKind, containerBundleIdentifier and widgetUniqueId as stored, an absent value shown "
                 "empty. Container Bundle ID is empty where the table has no such column (jess_ios15, all 50 rows) or holds no value in it "
                 "(77 rows on 8 other images). The size and intentHash columns are not reported. "
                 "Older layout: on hickman_ios14 the table holds one row per widget with its most recent tap "
                 "and most recent dwell; each becomes a Tap and a Significant dwell row, as Apple's migration "
                 "does. The reader compares whole rows of that layout, so an earlier state differing from the "
                 "current one only in its dwell would return the current tap again; engagements are compared "
                 "after the split instead, so each is reported once and a Recovered row is never one the current "
                 "state holds. There Container Bundle ID is empty on all 20 rows, and Widget Extension, Widget "
                 "Kind and Widget Unique ID held one value on all 20 rows, one widget. "
                 "Record Origin. Live rows come from a normal read. Apple's code deletes rows whose date is "
                 "older than a cutoff, so older engagements can remain only outside the current state, for "
                 "example in earlier states of the database. "
                 "A Recovered row is an engagement another state in the write-ahead log holds and the current "
                 "state does not, read through scripts/sqlite_wal.py: each readable earlier committed state of the "
                 "log's current generation (state n is the database after the first n committed transactions, "
                 "state 0 the database file without its log), the previous generation's left-over frames where "
                 "its checks pass, and frames after the last commit where quick_check passes. Recovery Location "
                 "names the oldest and newest states the engagement was read in and is empty on Live rows. "
                 "Engagements compare by every reported value, so two identical recovered engagements are "
                 "reported once. Why a row left the "
                 "current state is not established here. Every Recovered row on the tested images came from "
                 "committed states of the current generation; the previous-generation and uncommitted paths were "
                 "not exercised. Rows of the older layout held only in states before an in-log change to the "
                 "newer layout are not read; no tested image had one. On the 21 tested images with the store: "
                 "5,078 rows, 3,839 Live and 1,239 Recovered (Recovered on 14 images); 3,935 Shown, 1,130 "
                 "Significant dwell, 13 Tap. Record Origin held Live and Recovery Location was empty on every "
                 "row of the 7 images without recovered rows. Widget Extension named an extension outside the "
                 "com.apple prefix on 63 rows, all on dexter_ios18. Not reported from the same store: suggestions, "
                 "abuseControlOutcomes, proactiveStackRotations, timelineDonations, widgetReloadForSuggestion "
                 "and suggestedWidgets, which by their columns hold suggestions, stack rotations and timeline "
                 "donations rather than engagements; stackConfigurationHistory, counts of the "
                 "stacks holding each widget at a time; and dismissRecords and widgetSuggestionDismiss, which "
                 "held no rows in the current state of any tested image.",
        "paths": ('*/mobile/Library/DuetExpertCenter/_ATXInfoSuggestionStore.db*',),
        "output_types": "standard",
        "artifact_icon": "layout-grid",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 93 rows (52 Recovered)",
            "adams_iphone12mini": "iOS 17.1.1 | 102 rows (70 Recovered)",
            "belkactf6_tar": "iOS 16.3 | 205 rows (179 Recovered)",
            "cookbook_ios1751": "iOS 17.5.1 | 118 rows (10 Recovered)",
            "ctf2020_ios12": "iOS 12.4 | 0 rows (no store)",
            "dexter_ios18": "iOS 18.3.2 | 98 rows (84 Recovered)",
            "falken_ios26": "iOS 26.2.1 | 406 rows (348 Recovered)",
            "felix23_ios16": "iOS 16.5 | 125 rows (68 Recovered)",
            "felix_ios17": "iOS 17.6.1 | 21 rows",
            "fsfull002_ios17": "iOS 17.1 | 64 rows (46 Recovered)",
            "hc_ios17_2": "iOS 17.2.1 | 90 rows",
            "hc_ios18_7": "iOS 18.7.8 | 70 rows",
            "hc_ios26": "iOS 26.5.2 | 238 rows (205 Recovered)",
            "hexordia_ios1651": "iOS 16.5.1 | 147 rows (107 Recovered)",
            "hickman_ios14": "iOS 14.3 | 20 rows (18 Recovered)",
            "hickman_ios15": "iOS 15.3.1 | 136 rows",
            "iphone11_ios17": "iOS 17.3 | 198 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows (no store)",
            "iphone14plus_ios18": "iOS 18.0 | 17 rows (9 Recovered)",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 32 rows (23 Recovered)",
            "jess_ios15": "iOS 15.0.2 | 50 rows",
            "magnet_ios16": "iOS 16.1.1 | 37 rows (20 Recovered)",
            "otto_ios17": "iOS 17.5.1 | 2,811 rows",
        },
    }
}

import os
import sqlite3

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_file_path, \
    logfunc, open_sqlite_db_readonly
from scripts.sqlite_wal import KIND_COMMITTED, KIND_EARLIER, KIND_UNCOMMITTED, rows_not_in_current

# NSStringForATXWidgetEngagementType in AppPredictionClient.framework names these values.
_ENGAGEMENT = {0: 'Unknown', 1: 'Tap', 2: 'Significant dwell', 3: 'Shown'}

# The table as iOS 15 and later write it: one row per engagement.
_EVENT_QUERY = '''
SELECT date, engagementType, extensionBundleId, widgetKind, {container}, widgetUniqueId
FROM widgetEngagements
'''
# The earlier layout (hickman_ios14): one row per widget holding its most recent tap and its
# most recent dwell. Apple's own migration to the later layout turns each into a row of
# engagement type 1 (from mostRecentTap) and 2 (from mostRecentDwell); this does the same.
_WIDGET_QUERY = '''
SELECT mostRecentTap, mostRecentDwell, extensionBundleId, widgetKind, widgetUniqueId
FROM widgetEngagements
'''
_WAL_KINDS = (KIND_COMMITTED, KIND_EARLIER, KIND_UNCOMMITTED)
_ORIGIN_LIVE = 'Live'
_ORIGIN_RECOVERED = 'Recovered'


def _cocoa(value):
    """Seconds since 2001-01-01 UTC as a UTC datetime; '' when absent or not a number."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return convert_unix_ts_to_utc(value + 978307200)
    return ''


def _engagement(value):
    if value in _ENGAGEMENT:
        return _ENGAGEMENT[value]
    return '' if value is None else f'Unknown ({value})'


def _columns(db_file):
    db = open_sqlite_db_readonly(db_file)
    if db is None:
        return []
    try:
        return [row[1] for row in db.execute('PRAGMA table_info(widgetEngagements)')]
    except sqlite3.Error:
        return []
    finally:
        db.close()


def _event_rows(row):
    """Report rows for one result row of either query, as (date, type, extension, kind,
    container, unique id)."""
    if len(row) == 6:
        return [tuple(row)]
    tap, dwell, extension, kind, unique_id = row
    return [(date, engagement, extension, kind, None, unique_id)
            for date, engagement in ((tap, 1), (dwell, 2)) if date is not None]


def _widen(span, other):
    if other is None:
        return span
    if span is None:
        return other
    return (min(span[0], other[0]), max(span[1], other[1]))


def _recovered_events(found, live):
    """{event: (committed span, previous-generation span)} for the engagements of found that
    live does not hold.

    The helper compares whole query rows. On the older layout one widget row carries a tap
    and a dwell, so an earlier state that differs from the current one only in its dwell
    returns the current tap again. Comparing the split engagements, and merging the states
    each was read in, reports every engagement once."""
    events = {}
    for item in found:
        committed = (item.first_state, item.last_state) if item.first_state is not None else None
        for event in _event_rows(item.values):
            if event in live:
                continue
            spans = events.get(event, (None, None))
            events[event] = (_widen(spans[0], committed), _widen(spans[1], item.earlier_generation))
    return events


def _recovery_location(name, committed, earlier):
    """Where a recovered row was read, in the words googleChat.py and snapchat.py use."""
    parts = []
    if committed:
        first, last = committed
        if last == 0:
            parts.append(f'{name} without its log, state 0')
        elif first == 0:
            parts.append(f'{name} and {name}-wal, committed states 0 to {last}')
        else:
            states = f'state {first}' if first == last else f'states {first} to {last}'
            parts.append(f'{name}-wal, committed {states}')
    if earlier:
        first, last = earlier
        commits = f'commit {first}' if first == last else f'commits {first} to {last}'
        parts.append(f'{name}-wal, previous log generation, left-over {commits}')
    if not parts:
        return f'{name}-wal, frames after the last commit'
    return '; '.join(parts)


@artifact_processor
def widgetEngagements(context):
    data_headers = (
        ('Timestamp', 'datetime'), 'Engagement', 'Engagement Type (as stored)',
        'Widget Extension', 'Widget Kind', 'Container Bundle ID', 'Widget Unique ID',
        'Record Origin', 'Recovery Location')
    data_list = []
    db_file = get_file_path(context.get_files_found(), '_ATXInfoSuggestionStore.db')
    if not db_file:
        return data_headers, data_list, ''
    columns = _columns(db_file)
    if 'date' in columns:
        container = 'containerBundleIdentifier' if 'containerBundleIdentifier' in columns else 'NULL'
        query = _EVENT_QUERY.format(container=container)
    elif 'mostRecentTap' in columns:
        query = _WIDGET_QUERY
    else:
        logfunc('Widget Engagements: no widgetEngagements table in a layout this module reads')
        return data_headers, data_list, db_file

    rows = []
    db = open_sqlite_db_readonly(db_file)
    try:
        for row in db.execute(query):
            rows.extend((event, _ORIGIN_LIVE, '') for event in _event_rows(row))
    finally:
        db.close()

    name = os.path.basename(db_file)
    try:
        _found_columns, found, wal = rows_not_in_current(db_file, query, include=_WAL_KINDS)
        if wal.log:
            logfunc(f'Widget Engagements: {wal.summary()}')
        live = {event for event, _origin, _location in rows}
        for event, (committed, earlier) in _recovered_events(found, live).items():
            rows.append((event, _ORIGIN_RECOVERED, _recovery_location(name, committed, earlier)))
    except (sqlite3.Error, OSError) as ex:
        logfunc(f'Widget Engagements: write-ahead log not read: {ex}')

    rows.sort(key=lambda r: (r[0][0] if isinstance(r[0][0], (int, float)) else float('-inf'),
                             r[1] != _ORIGIN_LIVE))
    for (date, engagement, extension, kind, container, unique_id), origin, location in rows:
        data_list.append((
            _cocoa(date), _engagement(engagement), '' if engagement is None else str(engagement),
            extension or '', kind or '', container or '', unique_id or '', origin, location))
    return data_headers, data_list, db_file
