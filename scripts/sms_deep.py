"""Shared readers for the Messages database (sms.db) fields that sit outside the plain text column.

Used by the smsReactions, smsEdits, smsReplies, smsRecentlyDeleted and smsAppPayloads artifacts.
Nothing here opens a file: callers pass bytes already read from the database, or an open read-only
connection. Every decoder returns None (or an empty value) on input it cannot read and never raises,
so one damaged blob costs one cell and not the artifact.

Formats (all read from the stored bytes; see each artifact's notes for the evidence behind them):

* attributedBody, edit-history versions and recoverable part text are NSAttributedString
  "typedstream" archives. The text is the first object of the archive.
* message_summary_info is a binary property list. Its keys are short codes; the ones used here are
  ec (edit history, a dict of part index to a list of versions, each {d: seconds, t: typedstream}),
  ep (edited part indexes), otr (original text range per part, {lo, le}) and rp (retracted part
  indexes).
* payload_data is an NSKeyedArchiver archive.
* associated_message_guid is "p:<part>/<guid>" or "bp:<guid>" or a bare guid.
"""
import plistlib
import re

import typedstream

from scripts.ilapfuncs import (convert_cocoa_core_data_ts_to_utc, get_plist_content, logfunc)

# Messages stores nanoseconds since 2001-01-01 from iOS 11 and seconds before that.
_NANOSECOND_THRESHOLD = 1_000_000_000_000_000


def cocoa_to_utc(value):
    """Cocoa seconds or nanoseconds to a UTC datetime; '' for an empty or zero value."""
    if not value:
        return ''
    try:
        number = float(value)
        if number > _NANOSECOND_THRESHOLD:
            number = number / 1_000_000_000
        return convert_cocoa_core_data_ts_to_utc(number)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def typedstream_text(buffer):
    """The text of an NSAttributedString typedstream archive, or None when it cannot be read."""
    if not buffer:
        return None
    try:
        root = typedstream.unarchive_from_data(bytes(buffer))
        first = root.contents[0]
        value = first.value.value
        return value if isinstance(value, str) else None
    except Exception:  # pylint: disable=broad-exception-caught
        # The library raises several unrelated types on damaged archives.
        return None


def message_text(text, attributed_body):
    """message.text, or the text decoded from attributedBody where text is empty."""
    if text:
        return text
    return typedstream_text(attributed_body)


def summary_info(blob):
    """message_summary_info as a dict; {} when absent or unreadable."""
    if not blob:
        return {}
    try:
        value = plistlib.loads(bytes(blob))
    except Exception:  # pylint: disable=broad-exception-caught
        return {}
    return value if isinstance(value, dict) else {}


def keyed_archive(blob):
    """An NSKeyedArchiver payload as plain Python objects; None when it cannot be read."""
    if not blob or not bytes(blob[:8]).startswith((b'bplist', b'<?xml')):
        return None
    try:
        return get_plist_content(bytes(blob))
    except Exception:  # pylint: disable=broad-exception-caught
        return None


def split_associated_guid(value):
    """associated_message_guid to (part index or None, target message guid).

    "p:2/GUID" is part 2 of GUID, "bp:GUID" names the message's balloon, and a bare
    value is a message guid.
    """
    if not value:
        return None, ''
    match = re.match(r'^p:(\d+)/(.*)$', value)
    if match:
        return int(match.group(1)), match.group(2)
    if value.startswith('bp:'):
        return None, value[3:]
    return None, value


def query_chunks(db, sql_template, keys, chunk=400):
    """Run sql_template once per chunk of keys; the template holds one {marks} for the placeholders."""
    keys = list(keys)
    for start in range(0, len(keys), chunk):
        part = keys[start:start + chunk]
        marks = ','.join('?' * len(part))
        try:
            yield from db.execute(sql_template.format(marks=marks), part)
        except Exception as error:  # pylint: disable=broad-exception-caught
            logfunc(f'sms.db lookup failed: {error}')
            return


def messages_by_guid(db, guids):
    """{guid: (rowid, date, is_from_me, sender_id, text)} for the given message guids."""
    found = {}
    sql = ('SELECT m.guid, m.ROWID, m.date, m.is_from_me, h.id, m.text, m.attributedBody '
           'FROM message m LEFT JOIN handle h ON h.ROWID = m.handle_id '
           'WHERE m.guid IN ({marks})')
    for guid, rowid, date, from_me, sender, text, body in query_chunks(db, sql, guids):
        found[guid] = (rowid, date, from_me, sender, message_text(text, body))
    return found


def message_columns(db):
    """The column names of the message table (empty when it is absent)."""
    try:
        return {row[1] for row in db.execute('PRAGMA table_info(message)')}
    except Exception:  # pylint: disable=broad-exception-caught
        return set()


def table_exists(db, name):
    """True when the database has a table of that name."""
    try:
        return db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                          (name,)).fetchone() is not None
    except Exception:  # pylint: disable=broad-exception-caught
        return False
