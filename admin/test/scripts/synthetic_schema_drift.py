#!/usr/bin/env python3
"""Build a SYNTHETIC extraction holding the two files the calendarAll and locServicesconfig cases read.

Everything here is fabricated: titles are fixed sentences, places are example.invalid or reserved
test names, coordinates are round numbers, and times are fixed offsets from one base date. Nothing
comes from a real device. The layouts follow what the artifacts read:

* Calendar.sqlitedb: CalendarItem, Calendar, Store, Location, Participant, Identity, Attachment and
  Sharee, reduced to the columns the calendar artifacts select. One event stores a creation_date that
  SQLite renders as year 0000 (-63114076800 seconds), the value that used to fail the whole artifact.
* clients.plist: the Routine.bundle entry under the key form 'p<path>:' used by recent iOS versions.

    python synthetic_schema_drift.py out.zip

``build(zip_path)`` writes the zip and returns {name: expected} counts the tests compare against.
"""
import os
import plistlib
import sqlite3
import sys
import tempfile
import zipfile

# 2026-03-01 12:00:00 UTC as Cocoa seconds
BASE = 794059200.0
YEAR_ZERO = -63114076800


def calendar_db(path):
    db = sqlite3.connect(path)
    db.executescript('''
        CREATE TABLE Store (ROWID INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE Calendar (ROWID INTEGER PRIMARY KEY, title TEXT, color TEXT, store_id INTEGER,
                               self_identity_email TEXT, owner_identity_email TEXT, owner_identity_id INTEGER,
                               sharing_status INTEGER, notes TEXT);
        CREATE TABLE Location (ROWID INTEGER PRIMARY KEY, title TEXT, address TEXT, latitude REAL, longitude REAL);
        CREATE TABLE Identity (ROWID INTEGER PRIMARY KEY, display_name TEXT, address TEXT);
        CREATE TABLE Participant (ROWID INTEGER PRIMARY KEY, owner_id INTEGER, identity_id INTEGER,
                                  email TEXT, status INTEGER, entity_type INTEGER);
        CREATE TABLE Attachment (ROWID INTEGER PRIMARY KEY, owner_id INTEGER, filename TEXT, file_size INTEGER);
        CREATE TABLE Sharee (ROWID INTEGER PRIMARY KEY, owner_id INTEGER, identity_id INTEGER, access_level INTEGER);
        CREATE TABLE CalendarItem (ROWID INTEGER PRIMARY KEY, summary TEXT, start_date REAL, end_date REAL,
                                   start_tz TEXT, calendar_id INTEGER, location_id INTEGER, organizer_id INTEGER,
                                   has_attendees INTEGER, conference_url TEXT, description TEXT,
                                   creation_date REAL, last_modified REAL, calendar_scale TEXT);
    ''')
    db.execute("INSERT INTO Store VALUES (1, 'Synthetic Account')")
    db.execute("INSERT INTO Calendar VALUES (1, 'Synthetic Calendar', '#1BADF8', 1, NULL, 'owner@example.invalid', 1, 0, NULL)")
    db.execute("INSERT INTO Location VALUES (1, 'Synthetic Place', '1 Example Street', 10.5, 20.5)")
    db.execute("INSERT INTO Identity VALUES (1, 'Synthetic Invitee', 'mailto:invitee@example.invalid')")
    db.execute("INSERT INTO Participant VALUES (1, 1, 1, 'invitee@example.invalid', 1, 7)")
    # Four events: ordinary, with a year 0000 creation_date, with a place and invitee, and a birthday
    items = [
        (1, 'Synthetic event one', BASE + 3600, BASE + 7200, 'UTC', 1, None, None, 0, None, 'Notes one', BASE, BASE + 60, 'iso8601'),
        (2, 'Synthetic event two', BASE + 86400, BASE + 90000, 'UTC', 1, 1, None, 1, None, 'Notes two', YEAR_ZERO, BASE + 120, 'iso8601'),
        (3, 'Synthetic event three', BASE + 172800, BASE + 176400, '_float', 1, None, None, 0, None, None, BASE + 5, None, 'iso8601'),
        (4, 'Synthetic Person', 1000000000.0, 1000086400.0, None, 1, None, None, 0, None, None, BASE, BASE, 'gregorian'),
    ]
    db.executemany('INSERT INTO CalendarItem VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', items)
    db.execute("INSERT INTO Attachment VALUES (1, 3, 'synthetic.pdf', 1234)")
    db.commit()
    db.close()
    return {'events': 3, 'year_zero_events': 1, 'birthdays': 1}


def clients_plist():
    entry = {'FenceTimeStarted': BASE, 'ReceivingLocationInformationTimeStopped': BASE + 60,
             'BundlePath': '/System/Library/LocationBundles/Routine.bundle'}
    return plistlib.dumps({
        'p/System/Library/LocationBundles/Routine.bundle:': entry,
        'p/System/Library/LocationBundles/Other.bundle:': {'Authorization': 2},
    })


def build(zip_path):
    folder = tempfile.mkdtemp()
    expected = {}
    cal = os.path.join(folder, 'cal.sqlitedb')
    expected.update(calendar_db(cal))
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(cal, 'private/var/mobile/Library/Calendar/Calendar.sqlitedb')
        zf.writestr('private/var/mobile/Library/Caches/locationd/clients.plist', clients_plist())
    for name in os.listdir(folder):
        os.remove(os.path.join(folder, name))
    os.rmdir(folder)
    return expected


if __name__ == '__main__':
    build(sys.argv[1])
