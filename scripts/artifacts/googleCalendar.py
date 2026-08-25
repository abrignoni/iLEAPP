__artifacts_v2__ = {
    "googleCalendarEvents": {
        "name": "Google Calendar - Events",
        "description": "Calendar events synced by the Google Calendar iOS app, decoded from the "
                       "per-event protobuf held in the UnifiedSync store",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Google Calendar",
        "notes": "Rows come from the Events table of unifiedsync.db. Most event content is held in a "
                 "protobuf in the Proto column; field positions were established from the tested samples "
                 "and cross-checked against the columns beside them (the event id in the protobuf matched "
                 "the EventId column on every row, and the all-day start matched StartDayUtc on every "
                 "all-day row). "
                 "Two mutually exclusive start and end encodings were observed, and exactly one was "
                 "present on each of the 4,496 rows tested. All-day events store a value that fell on "
                 "exactly 00:00:00 UTC on all 1,418 rows carrying that form, so it encodes a calendar "
                 "date rather than an instant; those rows carry the date in the All Day Start Date and "
                 "All Day End Date columns, which are date typed so the date is not moved by a report "
                 "timezone conversion. Timed events store an instant together with an IANA timezone name, "
                 "present on all 3,078 timed rows tested; that name is reported in its own column and the "
                 "wall clock time in that zone is reported separately, so the conversion can be redone. "
                 "Created, Updated and the event start and end are milliseconds; the microsecond values "
                 "stored elsewhere in this database are converted separately. "
                 "Event Type is reported as stored: the app binary is not present in an application data "
                 "container, so the mapping was not recoverable. "
                 "No attachment or media reference was found in any event protobuf across both samples, "
                 "so no media is checked in. Events with no title also carried no description and no "
                 "location in the tested samples and are reported with the remaining fields rather than "
                 "dropped. "
                 "Path reference: Park, Park, Kim, Kang, Kim, 'A comprehensive artifact analysis of "
                 "Google applications on Android and iOS platforms', Forensic Science International: "
                 "Digital Investigation.",
        "paths": ('*/Library/Application Support/UnifiedSync/unifiedsync.db*',),
        "output_types": "standard",
        "artifact_icon": "calendar",
    },
    "googleCalendarEventAttendees": {
        "name": "Google Calendar - Event Attendees",
        "description": "Attendees recorded on Google Calendar events",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Google Calendar",
        "notes": "One row per attendee entry in the repeated attendee field of the event protobuf. "
                 "The attendee response and role integers are reported as stored: the app binary is not "
                 "present in an application data container and no mapping for them was sourced. "
                 "The attendee timestamp is milliseconds.",
        "paths": ('*/Library/Application Support/UnifiedSync/unifiedsync.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "googleCalendarEventLocations": {
        "name": "Google Calendar - Event Locations",
        "description": "Structured locations attached to Google Calendar events, with coordinates where present",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Google Calendar",
        "notes": "Coordinates are stored as two 64 bit values in the event protobuf and are read back as "
                 "IEEE 754 doubles. In the tested samples the decoded pairs fell in the region matching "
                 "the timezone the same events carried, which is a consistency check and not a statement "
                 "about where the device was. A structured location records a place associated with the "
                 "event, not an observed device position. Rows are emitted for structured locations that "
                 "carry no coordinates as well, so the count is not limited to mappable rows.",
        "paths": ('*/Library/Application Support/UnifiedSync/unifiedsync.db*',),
        "output_types": ["html", "tsv", "timeline", "lava", "kml"],
        "artifact_icon": "map-pin",
    },
    "googleCalendarCalendars": {
        "name": "Google Calendar - Calendars",
        "description": "Calendars known to the Google Calendar iOS app",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Google Calendar",
        "notes": "Rows come from the Calendars table of unifiedsync.db. The calendar timezone is the "
                 "zone recorded for the calendar itself and is not necessarily the zone of any event on "
                 "it. The calendar timestamp in this table is stored as a microsecond string, a different "
                 "unit from the millisecond values in the Events table, and is converted as microseconds. "
                 "Colour and access integers are reported as stored.",
        "paths": ('*/Library/Application Support/UnifiedSync/unifiedsync.db*',),
        "output_types": "standard",
        "artifact_icon": "calendar",
    },
    "googleCalendarCalendarSync": {
        "name": "Google Calendar - Calendar Sync Settings",
        "description": "Per calendar selection and sync flags",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Google Calendar",
        "notes": "Rows come from the CalendarSyncInfo table of unifiedsync.db. IsSelected and "
                 "IsSyncEnabled are the values stored by the app. A day number observed in the protobuf "
                 "is reported as a date derived by counting days from 1970-01-01 UTC; it is reported as "
                 "a date rather than a datetime because the stored value has no time component.",
        "paths": ('*/Library/Application Support/UnifiedSync/unifiedsync.db*',),
        "output_types": "standard",
        "artifact_icon": "refresh-cw",
    },
    "googleCalendarCalendarAccess": {
        "name": "Google Calendar - Calendar Access",
        "description": "Access control entries recorded for calendars",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Google Calendar",
        "notes": "One row per access entry in the AccessData table of unifiedsync.db. The role integer is "
                 "reported as stored; no mapping for it was sourced. An entry may name an individual or a "
                 "group, and both are reported in the column that held the value.",
        "paths": ('*/Library/Application Support/UnifiedSync/unifiedsync.db*',),
        "output_types": "standard",
        "artifact_icon": "lock",
    },
    "googleCalendarAccounts": {
        "name": "Google Calendar - Accounts",
        "description": "Accounts registered in the Google Calendar UnifiedSync store",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Google Calendar",
        "notes": "Rows come from the Accounts table of unifiedsync.db, joined to the sync state recorded "
                 "for the same account where present. In the tested samples the account identifier was a "
                 "numeric Google account identifier rather than an address; addresses appear on the "
                 "calendars and events belonging to the account. The sync timestamp is milliseconds.",
        "paths": ('*/Library/Application Support/UnifiedSync/unifiedsync.db*',),
        "output_types": "standard",
        "artifact_icon": "user",
    },
    "googleCalendarSettings": {
        "name": "Google Calendar - Account Settings",
        "description": "Per account settings recorded in the UnifiedSync store",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Google Calendar",
        "notes": "Rows come from the Settings table of unifiedsync.db. The setting identifier is a "
                 "readable key stored by the app. A setting value may be a string or a nested structure; "
                 "where it is a structure the decoded content is reported rather than the row being "
                 "skipped, so the row count matches the number of settings stored. A minority of settings "
                 "carry no value in the usual field and hold a structured value in another; those are "
                 "reported from that field rather than as an empty cell. The setting timestamp "
                 "is stored as a microsecond string and is converted as microseconds.",
        "paths": ('*/Library/Application Support/UnifiedSync/unifiedsync.db*',),
        "output_types": "standard",
        "artifact_icon": "settings",
    },
    "googleCalendarAppointmentSchedules": {
        "name": "Google Calendar - Appointment Schedules",
        "description": "Appointment schedules defined on a calendar",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Google Calendar",
        "notes": "Rows come from the AppointmentSlot table of unifiedsync.db. This table was empty in one "
                 "of the two tested samples, so an empty result does not establish that the feature was "
                 "unused. The timezone reported is the one stored on the schedule.",
        "paths": ('*/Library/Application Support/UnifiedSync/unifiedsync.db*',),
        "output_types": "standard",
        "artifact_icon": "clock",
    },
    "googleCalendarContacts": {
        "name": "Google Calendar - Cached Contacts",
        "description": "Contacts cached by the Google Calendar iOS app for guest lookup",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Google Calendar",
        "notes": "Rows come from the contacts table of the per account Contacts cache database. This is a "
                 "cache the app holds for looking up guests; presence of a contact here does not establish "
                 "that the user contacted or invited that person. The affinity value is reported as stored "
                 "and no meaning is asserted for it. The cache file name is not specific to this app, so "
                 "a container is only reported when it also holds the Google Calendar preferences file; a "
                 "container holding the same cache without that marker is skipped and logged. "
                 "In the tested samples every contact carried one "
                 "lookup key holding an address and a second lookup key whose value was an empty string "
                 "on all 517 rows of the largest cache, so the second key type is reported as present and "
                 "empty rather than omitted. Photo values are the remote URLs recorded by the app; the "
                 "image bytes were not present in the tested samples, so nothing is checked in as media.",
        "paths": ('*/Library/Caches/Contacts_*.db*',
                  '*/Library/Preferences/com.google.calendar.plist'),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "googleCalendarAccountPreferences": {
        "name": "Google Calendar - Account Preferences",
        "description": "Per account calendar preferences cached by the app",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Google Calendar",
        "notes": "One row per preference key in the per account cached preferences property list under "
                 "CALFileStorage. The account identifier is taken from the file name. Values are reported "
                 "as stored, including the app's own string spellings of true and false. A nested value is "
                 "reported as its decoded content.",
        "paths": ('*/Library/Application Support/CALFileStorage/cached.preferences.storage.*',),
        "output_types": "standard",
        "artifact_icon": "sliders",
    },
    "googleCalendarAppState": {
        "name": "Google Calendar - Application State",
        "description": "Application level preferences recorded by the Google Calendar iOS app",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Google Calendar",
        "notes": "One row per key in the app's preferences property list. Values are reported as stored. "
                 "The first launch value is an ISO 8601 string that carries its own UTC offset, so it is "
                 "read from the string rather than converted from an epoch. Permission status integers "
                 "are reported as stored; no mapping for them was sourced. Absence of a key means the app "
                 "wrote no value for it and is not evidence that a feature was unused.",
        "paths": ('*/Library/Preferences/com.google.calendar.plist',),
        "output_types": "standard",
        "artifact_icon": "smartphone",
    },
}

import os
import sqlite3
import struct
from datetime import datetime, timedelta, timezone

import pytz
from google.protobuf.message import DecodeError

from scripts import blackboxprotobuf
from scripts.ilapfuncs import (
    artifact_processor,
    get_file_path,
    get_plist_file_content,
    get_sqlite_db_records,
    logfunc,
)

_UNIX_EPOCH_UTC = datetime(1970, 1, 1, tzinfo=timezone.utc)

# The exception types the vendored protobuf reader raises on malformed input. Established
# by feeding it several hundred malformed and random byte strings and recording what came
# back, rather than by catching everything: a bare Exception here would also swallow bugs
# in this module's own field handling.
_PROTOBUF_ERRORS = (DecodeError, KeyError, IndexError, ValueError, struct.error)


# --------------------------------------------------------------------------------------
# Unit specific timestamp helpers.
#
# This database stores three different units, so each converter is named for the unit it
# takes and the call sites choose. Nothing here infers a unit from the magnitude of the
# value, because the same value can be valid in more than one unit.
# --------------------------------------------------------------------------------------

def _from_ms(value):
    """Milliseconds since the Unix epoch to an aware UTC datetime."""
    if value in (None, ''):
        return ''
    try:
        return _UNIX_EPOCH_UTC + timedelta(milliseconds=int(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _from_us(value):
    """Microseconds since the Unix epoch to an aware UTC datetime.

    The value arrives as a byte string in this store, so it is decoded before conversion.
    """
    if value in (None, ''):
        return ''
    if isinstance(value, bytes):
        value = value.decode('utf-8', 'replace')
    try:
        return _UNIX_EPOCH_UTC + timedelta(microseconds=int(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _date_from_ms(value):
    """A whole day value to a YYYY-MM-DD string read in UTC.

    Used only for the all-day encoding, whose values were observed to fall on exact UTC
    midnight. Returned as a plain date so a report timezone conversion cannot move it onto
    the neighbouring day.
    """
    if value in (None, ''):
        return ''
    try:
        return (_UNIX_EPOCH_UTC + timedelta(milliseconds=int(value))).strftime('%Y-%m-%d')
    except (TypeError, ValueError, OverflowError):
        return ''


def _date_from_day_number(value):
    """A count of days since 1970-01-01 UTC to a YYYY-MM-DD string."""
    if value in (None, ''):
        return ''
    try:
        return (_UNIX_EPOCH_UTC + timedelta(days=int(value))).strftime('%Y-%m-%d')
    except (TypeError, ValueError, OverflowError):
        return ''


def _local_wall_time(ms_value, tz_name):
    """The wall clock time of an instant in the zone the record itself carries.

    Returns a plain string, never a datetime, so nothing downstream converts it a second
    time. Uses pytz rather than zoneinfo: pytz carries its own copy of the zone database,
    so the column is populated on every platform, where zoneinfo depends on a system
    database that Windows does not provide. Falls back to an empty string when the zone is
    absent or is a name this zone database does not know.
    """
    if ms_value in (None, '') or not tz_name:
        return ''
    try:
        instant = _UNIX_EPOCH_UTC + timedelta(milliseconds=int(ms_value))
        return instant.astimezone(pytz.timezone(tz_name)).strftime('%Y-%m-%d %H:%M:%S')
    except (pytz.exceptions.UnknownTimeZoneError, TypeError, ValueError, OverflowError):
        return ''


# --------------------------------------------------------------------------------------
# Protobuf access helpers.
#
# blackboxprotobuf returns a dict keyed by field number as a string. A field that appeared
# more than once in the encoded message comes back as a list, and a field that appeared
# once comes back as a bare value, so every accessor has to cope with both.
# --------------------------------------------------------------------------------------

def _first(value):
    """The first element of a repeated field, or the value itself when it is not repeated."""
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _get(message, *path):
    """Walk a field number path, taking the first element of any repeated field."""
    current = message
    for key in path:
        current = _first(current)
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return _first(current)


def _repeated(message, key):
    """Every element of a field, as a list, whether or not it was encoded repeated."""
    if not isinstance(message, dict) or key not in message:
        return []
    value = message[key]
    return value if isinstance(value, list) else [value]


def _text(value):
    """A stored value rendered as text.

    Byte strings are decoded. A nested structure is rendered rather than discarded, so a
    value the app stored in a shape this reader did not expect stays visible in the report
    instead of silently becoming a blank cell.
    """
    if value is None:
        return ''
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    if isinstance(value, (dict, list)):
        return str(value)
    return value


def _as_stored(value):
    """An integer whose meaning was not sourced, rendered without asserting a label."""
    return '' if value is None else value


def _double_from_fixed64(value):
    """Reinterpret a 64 bit value as an IEEE 754 double."""
    if value is None:
        return ''
    try:
        return struct.unpack('<d', struct.pack('<Q', int(value) & 0xFFFFFFFFFFFFFFFF))[0]
    except (TypeError, ValueError, struct.error):
        return ''


def _container_root(path):
    """The app container directory a Library/... path sits under, or None.

    Both the contacts cache and the preferences file live under the container's Library
    directory, so splitting on the last Library separator gives a key the two share.
    """
    normalised = str(path).replace('\\', '/')
    marker = '/Library/'
    index = normalised.rfind(marker)
    return normalised[:index] if index != -1 else None


def _decode(blob):
    """Decode a protobuf blob, returning None when it cannot be read."""
    if not blob:
        return None
    try:
        message, _ = blackboxprotobuf.decode_message(blob)
        return message
    except _PROTOBUF_ERRORS as error:
        logfunc(f'Google Calendar: could not decode a protobuf value: {error}')
        return None


def _event_time(message, field):
    """Read one of the two start or end encodings.

    Returns (utc_datetime, all_day_date, timezone_name, is_all_day).

    Exactly one of the two encodings was present on every row of both tested samples. The
    all-day form holds a single value that fell on exact UTC midnight on every row that
    carried it, so it encodes a calendar date. The timed form holds an instant together
    with an IANA zone name.
    """
    node = _get(message, field)
    if not isinstance(node, dict):
        return '', '', '', False

    all_day_ms = _first(node.get('1'))
    if all_day_ms is not None:
        return _from_ms(all_day_ms), _date_from_ms(all_day_ms), '', True

    timed_ms = _get(node, '2', '1')
    tz_name = _text(_first(node.get('3')))
    return _from_ms(timed_ms), '', tz_name, False


def _unifiedsync_rows(context, query):
    """Run a query against every UnifiedSync database the seeker matched.

    Yields (source_path, row). Sidecar files matched by the glob are skipped: they are
    picked up so the WAL travels with the database, not so they are opened themselves.
    """
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('unifiedsync.db'):
            continue
        try:
            # get_sqlite_db_records returns a cursor, so the rows are produced while it is
            # iterated. Materialise inside the guard, otherwise a database error raised
            # part way through iteration escapes this artifact and kills the run.
            records = list(get_sqlite_db_records(file_found, query))
        except sqlite3.Error as error:
            logfunc(f'Google Calendar: could not read {context.get_relative_path(file_found)}: {error}')
            continue
        for record in records:
            yield file_found, record


def _unifiedsync_sources(context):
    """The UnifiedSync databases the seeker matched, newline joined."""
    return '\n'.join(sorted({
        str(f) for f in context.get_files_found() if str(f).endswith('unifiedsync.db')
    }))


@artifact_processor
def googleCalendarEvents(context):
    data_list = []
    query = '''
    SELECT AccountId, CalendarId, EventId, EventType, Proto
    FROM Events
    '''
    for file_found, record in _unifiedsync_rows(context, query):
        account_id, calendar_id, event_id, event_type, blob = record
        message = _decode(blob)
        if message is None:
            continue

        start_utc, start_date, start_tz, all_day = _event_time(message, '36')
        end_utc, end_date, end_tz, _ = _event_time(message, '37')
        orig_utc, orig_date, _, _ = _event_time(message, '38')

        # The start carries the zone for the event; the end repeats it. Report the start's,
        # and fall back to the end's only when the start had none.
        event_tz = start_tz or end_tz

        conference_url = _text(_get(message, '58', '1', '2'))
        structured_place = _text(_get(message, '49', '1', '2'))

        data_list.append((
            start_utc,
            end_utc,
            start_date,
            end_date,
            _local_wall_time(_get(message, '36', '2', '1'), event_tz),
            _local_wall_time(_get(message, '37', '2', '1'), event_tz),
            _from_ms(_get(message, '4')),
            _from_ms(_get(message, '5')),
            orig_utc or orig_date,
            'Yes' if all_day else 'No',
            event_tz,
            _text(_get(message, '6')),
            _text(_get(message, '7')),
            _text(_get(message, '8')),
            structured_place,
            _text(_get(message, '10', '1')),
            _text(_get(message, '10', '2')),
            _text(_get(message, '35', '2')),
            _text(_get(message, '13')),
            _text(_get(message, '14')),
            conference_url,
            len(_repeated(message, '21')),
            _as_stored(event_type),
            calendar_id,
            event_id,
            _text(_get(message, '19')),
            _text(_get(message, '3')),
            account_id,
            context.get_relative_path(file_found),
        ))

    data_headers = (
        ('Start Timestamp', 'datetime'),
        ('End Timestamp', 'datetime'),
        ('All Day Start Date', 'date'),
        ('All Day End Date', 'date'),
        'Start Local Time',
        'End Local Time',
        ('Created Timestamp', 'datetime'),
        ('Updated Timestamp', 'datetime'),
        'Original Start',
        'All Day',
        'Event Time Zone',
        'Title',
        'Description',
        'Location',
        'Structured Location',
        'Organizer Address',
        'Organizer Name',
        'Calendar Name',
        'Recurrence Rule',
        'Recurring Event ID',
        'Conferencing URL',
        'Attendee Count',
        'Event Type (as stored)',
        'Calendar ID',
        'Event ID',
        'iCal UID',
        'Event Link',
        'Account ID',
        'Source File',
    )
    return data_headers, data_list, _unifiedsync_sources(context)


@artifact_processor
def googleCalendarEventAttendees(context):
    data_list = []
    query = '''
    SELECT AccountId, CalendarId, EventId, Proto
    FROM Events
    '''
    for file_found, record in _unifiedsync_rows(context, query):
        account_id, calendar_id, event_id, blob = record
        message = _decode(blob)
        if message is None:
            continue
        attendees = _repeated(message, '21')
        if not attendees:
            continue

        start_utc, start_date, _, _ = _event_time(message, '36')
        title = _text(_get(message, '6'))

        for attendee in attendees:
            if not isinstance(attendee, dict):
                # Keep an unexpected shape visible rather than dropping the attendee.
                data_list.append((
                    start_utc, start_date, '', title, _text(attendee), '', '', '', '',
                    calendar_id, event_id, account_id,
                    context.get_relative_path(file_found),
                ))
                continue
            data_list.append((
                start_utc,
                start_date,
                _from_ms(_first(attendee.get('15'))),
                title,
                _text(_first(attendee.get('1'))),
                _text(_first(attendee.get('2'))),
                _as_stored(_first(attendee.get('6'))),
                _as_stored(_first(attendee.get('9'))),
                _as_stored(_first(attendee.get('10'))),
                calendar_id,
                event_id,
                account_id,
                context.get_relative_path(file_found),
            ))

    data_headers = (
        ('Event Start Timestamp', 'datetime'),
        ('Event All Day Start Date', 'date'),
        ('Attendee Timestamp', 'datetime'),
        'Event Title',
        'Attendee Address',
        'Attendee Name',
        'Attendee Value 6 (as stored)',
        'Attendee Value 9 (as stored)',
        'Attendee Value 10 (as stored)',
        'Calendar ID',
        'Event ID',
        'Account ID',
        'Source File',
    )
    return data_headers, data_list, _unifiedsync_sources(context)


@artifact_processor
def googleCalendarEventLocations(context):
    data_list = []
    query = '''
    SELECT AccountId, CalendarId, EventId, Proto
    FROM Events
    '''
    for file_found, record in _unifiedsync_rows(context, query):
        account_id, calendar_id, event_id, blob = record
        message = _decode(blob)
        if message is None:
            continue
        place = _get(message, '49', '1')
        if not isinstance(place, dict):
            continue

        start_utc, start_date, _, _ = _event_time(message, '36')
        address = _get(place, '3')
        data_list.append((
            start_utc,
            start_date,
            _text(_get(message, '6')),
            _text(_first(place.get('2'))),
            _text(_get(address, '1') if isinstance(address, dict) else None),
            _text(_get(address, '3') if isinstance(address, dict) else None),
            _text(_get(address, '4') if isinstance(address, dict) else None),
            _text(_get(address, '2') if isinstance(address, dict) else None),
            _double_from_fixed64(_get(place, '4', '1')),
            _double_from_fixed64(_get(place, '4', '2')),
            _text(_first(place.get('1'))),
            _text(_first(place.get('5'))),
            _text(_get(message, '8')),
            calendar_id,
            event_id,
            account_id,
            context.get_relative_path(file_found),
        ))

    data_headers = (
        ('Timestamp', 'datetime'),
        ('All Day Start Date', 'date'),
        'Event Title',
        'Place Name',
        'Address',
        'City',
        'Region',
        'Country Code',
        'Latitude',
        'Longitude',
        'Place ID',
        'Maps URL',
        'Location Text',
        'Calendar ID',
        'Event ID',
        'Account ID',
        'Source File',
    )
    return data_headers, data_list, _unifiedsync_sources(context)


@artifact_processor
def googleCalendarCalendars(context):
    data_list = []
    query = '''
    SELECT AccountId, CalendarId, HasOwnerAccess, ToBeRemoved, Proto
    FROM Calendars
    '''
    for file_found, record in _unifiedsync_rows(context, query):
        account_id, calendar_id, has_owner_access, to_be_removed, blob = record
        message = _decode(blob) or {}
        details = _get(message, '2')
        details = details if isinstance(details, dict) else {}
        colours = _get(message, '3')
        colours = colours if isinstance(colours, dict) else {}

        data_list.append((
            _from_us(_get(message, '8')),
            _text(_first(details.get('1'))),
            _text(_first(details.get('4'))),
            _text(_get(message, '22')),
            _text(_first(details.get('17'))),
            _as_stored(has_owner_access),
            _as_stored(to_be_removed),
            _as_stored(_first(colours.get('6'))),
            _as_stored(_get(message, '12')),
            _as_stored(_get(message, '23')),
            calendar_id,
            account_id,
            context.get_relative_path(file_found),
        ))

    data_headers = (
        ('Calendar Timestamp', 'datetime'),
        'Calendar Name',
        'Calendar Time Zone',
        'Owner Address',
        'Domain',
        'Has Owner Access',
        'To Be Removed',
        'Colour Value (as stored)',
        'Value 12 (as stored)',
        'Value 23 (as stored)',
        'Calendar ID',
        'Account ID',
        'Source File',
    )
    return data_headers, data_list, _unifiedsync_sources(context)


@artifact_processor
def googleCalendarCalendarSync(context):
    data_list = []
    query = '''
    SELECT AccountId, CalendarId, IsSelected, IsSyncEnabled, ToBeRemoved, Proto
    FROM CalendarSyncInfo
    '''
    for file_found, record in _unifiedsync_rows(context, query):
        account_id, calendar_id, is_selected, is_sync_enabled, to_be_removed, blob = record
        message = _decode(blob) or {}
        data_list.append((
            _date_from_day_number(_get(message, '3', '3')),
            _as_stored(is_selected),
            _as_stored(is_sync_enabled),
            _as_stored(to_be_removed),
            _as_stored(_get(message, '1')),
            _as_stored(_get(message, '2')),
            _as_stored(_get(message, '7')),
            _as_stored(_get(message, '8')),
            calendar_id,
            account_id,
            context.get_relative_path(file_found),
        ))

    data_headers = (
        ('Sync Date', 'date'),
        'Is Selected',
        'Is Sync Enabled',
        'To Be Removed',
        'Value 1 (as stored)',
        'Value 2 (as stored)',
        'Value 7 (as stored)',
        'Value 8 (as stored)',
        'Calendar ID',
        'Account ID',
        'Source File',
    )
    return data_headers, data_list, _unifiedsync_sources(context)


@artifact_processor
def googleCalendarCalendarAccess(context):
    data_list = []
    query = '''
    SELECT AccountId, CalendarId, Proto
    FROM AccessData
    '''
    for file_found, record in _unifiedsync_rows(context, query):
        account_id, calendar_id, blob = record
        message = _decode(blob)
        if message is None:
            continue
        domain = _get(message, '3')
        domain = domain if isinstance(domain, dict) else {}

        for entry in _repeated(message, '2'):
            if not isinstance(entry, dict):
                continue
            data_list.append((
                _text(_first(entry.get('1'))),
                _text(_first(entry.get('2'))),
                _as_stored(_first(entry.get('5'))),
                _as_stored(_first(entry.get('7'))),
                _text(_first(domain.get('2'))),
                _text(_first(domain.get('1'))),
                calendar_id,
                account_id,
                context.get_relative_path(file_found),
            ))

    data_headers = (
        'Individual Address',
        'Group Address',
        'Role Value (as stored)',
        'Value 7 (as stored)',
        'Domain Name',
        'Domain Customer ID',
        'Calendar ID',
        'Account ID',
        'Source File',
    )
    return data_headers, data_list, _unifiedsync_sources(context)


@artifact_processor
def googleCalendarAccounts(context):
    data_list = []
    query = '''
    SELECT a.AccountId, a.PlatformAccountName, s.UpdateTimestampMs
    FROM Accounts a
    LEFT JOIN SyncState s ON s.AccountId = a.AccountId
    '''
    for file_found, record in _unifiedsync_rows(context, query):
        account_id, platform_account_name, update_ms = record
        data_list.append((
            _from_ms(update_ms),
            account_id,
            platform_account_name,
            context.get_relative_path(file_found),
        ))

    data_headers = (
        ('Sync State Timestamp', 'datetime'),
        'Account ID',
        'Platform Account Name',
        'Source File',
    )
    return data_headers, data_list, _unifiedsync_sources(context)


@artifact_processor
def googleCalendarSettings(context):
    data_list = []
    query = '''
    SELECT AccountId, SettingId, ToBeRemoved, Proto
    FROM Settings
    '''
    for file_found, record in _unifiedsync_rows(context, query):
        account_id, setting_id, to_be_removed, blob = record
        message = _decode(blob) or {}
        # Most settings hold their value in field 2. A minority hold no field 2 at all and
        # carry a structured value elsewhere instead; reporting those as an empty cell would
        # hide a value the app did store, so fall back to the structured content.
        value = _text(_first(message.get('2')))
        if value == '':
            value = _text(_first(message.get('8')))
        data_list.append((
            _from_us(_get(message, '3')),
            setting_id,
            value,
            _as_stored(to_be_removed),
            account_id,
            context.get_relative_path(file_found),
        ))

    data_headers = (
        ('Setting Timestamp', 'datetime'),
        'Setting',
        'Value',
        'To Be Removed',
        'Account ID',
        'Source File',
    )
    return data_headers, data_list, _unifiedsync_sources(context)


@artifact_processor
def googleCalendarAppointmentSchedules(context):
    data_list = []
    query = '''
    SELECT AccountId, CalendarId, AppointmentSlotId, ToBeRemoved, Proto
    FROM AppointmentSlot
    '''
    for file_found, record in _unifiedsync_rows(context, query):
        account_id, calendar_id, slot_id, to_be_removed, blob = record
        message = _decode(blob) or {}
        data_list.append((
            _text(_get(message, '1')),
            _text(_get(message, '5')),
            _as_stored(to_be_removed),
            slot_id,
            calendar_id,
            account_id,
            context.get_relative_path(file_found),
        ))

    data_headers = (
        'Schedule Title',
        'Time Zone',
        'To Be Removed',
        'Appointment Slot ID',
        'Calendar ID',
        'Account ID',
        'Source File',
    )
    return data_headers, data_list, _unifiedsync_sources(context)


@artifact_processor
def googleCalendarContacts(context):
    data_list = []
    source_files = set()

    # Contacts_<n>_<account>.db under Library/Caches is a shared Google people cache name and
    # is not specific to this app. Anchor on the container: only report a cache that sits
    # beside the Google Calendar preferences file, so another Google app's copy of the same
    # cache is not reported as this app's.
    files = [str(f) for f in context.get_files_found()]
    calendar_containers = {
        _container_root(f) for f in files
        if os.path.basename(f) == 'com.google.calendar.plist'
    }
    calendar_containers.discard(None)

    for file_found in files:
        base = os.path.basename(file_found)
        # The glob picks up the WAL and SHM sidecars so they travel with the database.
        # Only the database itself is opened.
        if not base.startswith('Contacts_') or not base.endswith('.db'):
            continue
        if _container_root(file_found) not in calendar_containers:
            logfunc('Google Calendar: skipping a contacts cache with no Google Calendar '
                    f'preferences file in the same container: '
                    f'{context.get_relative_path(file_found)}')
            continue

        source_files.add(file_found)

        # The file name carries the account identifier after the source number.
        account_id = base[len('Contacts_'):-len('.db')]
        if '_' in account_id:
            account_id = account_id.split('_', 1)[1]

        query = '''
        SELECT c.identifier, c.affinity, c.source, c.type, c.proto_data,
               (SELECT group_concat(k.value, ' | ') FROM contact_lookup_keys k
                 WHERE k.contact_identifier = c.identifier AND k.type = 0),
               (SELECT count(*) FROM contact_lookup_keys k
                 WHERE k.contact_identifier = c.identifier AND k.type = 2 AND k.value = '')
        FROM contacts c
        '''
        try:
            records = list(get_sqlite_db_records(file_found, query))
        except sqlite3.Error as error:
            logfunc(f'Google Calendar: could not read {context.get_relative_path(file_found)}: {error}')
            continue

        for identifier, affinity, source, ctype, blob, lookup_addresses, empty_keys in records:
            message = _decode(blob) or {}
            person = _get(message, '4')
            person = person if isinstance(person, dict) else {}

            display_name = _text(_get(person, '3', '2'))
            photo_url = _text(_get(person, '4', '2'))

            addresses = []
            names = []
            for contact_method in _repeated(person, '10'):
                if not isinstance(contact_method, dict):
                    continue
                value = _text(_first(contact_method.get('2')))
                if value:
                    addresses.append(value)
                nested_name = _text(_get(contact_method, '9', '2'))
                if nested_name and nested_name not in names:
                    names.append(nested_name)

            data_list.append((
                display_name or (names[0] if names else ''),
                ' | '.join(addresses),
                _text(lookup_addresses),
                photo_url,
                _as_stored(affinity),
                _as_stored(source),
                _as_stored(ctype),
                _as_stored(empty_keys),
                identifier,
                account_id,
                context.get_relative_path(file_found),
            ))

    data_headers = (
        'Display Name',
        'Addresses',
        'Lookup Addresses',
        'Photo URL',
        'Affinity (as stored)',
        'Source (as stored)',
        'Type (as stored)',
        'Empty Lookup Keys',
        'Contact Identifier',
        'Account ID',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(sorted(source_files))


@artifact_processor
def googleCalendarAccountPreferences(context):
    data_list = []
    source_files = set()
    marker = 'cached.preferences.storage.'
    for file_found in context.get_files_found():
        file_found = str(file_found)
        base = os.path.basename(file_found)
        if not base.startswith(marker):
            continue
        source_files.add(file_found)
        account_id = base[len(marker):]

        content = get_plist_file_content(file_found)
        if not isinstance(content, dict):
            continue
        for key in sorted(content):
            data_list.append((
                key,
                _text(content[key]),
                account_id,
                context.get_relative_path(file_found),
            ))

    data_headers = ('Preference', 'Value', 'Account ID', 'Source File')
    return data_headers, data_list, '\n'.join(sorted(source_files))


@artifact_processor
def googleCalendarAppState(context):
    data_list = []
    file_found = get_file_path(context.get_files_found(), 'com.google.calendar.plist')
    if file_found:
        content = get_plist_file_content(file_found)
        if isinstance(content, dict):
            for key in sorted(content):
                data_list.append((
                    key,
                    _text(content[key]),
                    context.get_relative_path(file_found),
                ))

    data_headers = ('Preference', 'Value', 'Source File')
    return data_headers, data_list, file_found
