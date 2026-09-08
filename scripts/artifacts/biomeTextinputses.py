__artifacts_v2__ = {
    "get_biomeTextinputses": {
        "name": "Biome - Text Input Session",
        "description": "Sessions recorded in the Biome Text.InputSession stream, with the app, the "
                       "start of the session, its duration and the session identifier where one is "
                       "stored",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Biome",
        "notes": "One record per text input session, holding a duration, a start time, a bundle "
                 "identifier, an undocumented flag and, on newer releases, a session identifier.\n\n"
                 "The record is written when the session ends. Measured over 3,794 written records "
                 "in 19 test images: on 3,752 of them the SEGB record timestamp minus the start "
                 "time equals the stored duration to within one second, so the record timestamp "
                 "sits at the end of the session and the start time is the earlier of the two.\n\n"
                 "The start time is a Cocoa timestamp in the public TextInputSession stream and a "
                 "Unix timestamp in the restricted Text.InputSession stream, and is converted "
                 "accordingly.\n\n"
                 "Session Identifier is blank on the older stream layout. Of the 19 test images, "
                 "three carried no identifier on any record, one carried it on part of its records, "
                 "and fifteen carried it on every record. The one that changes is a public "
                 "TextInputSession image whose last record without an identifier was written "
                 "2023-06-14 and whose first record with one was written two days later, so the "
                 "value appears at a point in that device's history rather than per app. All three "
                 "images with none, and the one that changes, read the public TextInputSession "
                 "stream; every image of the restricted Text.InputSession stream carried it. Where "
                 "present the value was distinct on every row, 2,827 of 2,827 across the tested "
                 "images. On one iOS 26.2.1 image none of its 218 identifiers was found anywhere "
                 "else in that image's Biome streams, searched as text and as 16 raw bytes across "
                 "its other 556 stream files, that stream's own tombstone file aside.\n\n"
                 "The stored value between the bundle identifier and the session identifier is not "
                 "reported. It was 0 on all 1,953 records read from the public stream and 1 on all "
                 "1,841 read from the restricted stream, so it repeats which stream the row came "
                 "from and adds nothing to it; its meaning is undocumented.\n\n"
                 "North Loop Consulting reports that these records are written for the appearance "
                 "of the on-screen keyboard, so a session is not by itself evidence that anything "
                 "was typed, and that the stream is absent on Apple devices with physical "
                 "keyboards. That behaviour was not tested here. What the tested images do show is "
                 "that a session can be far too short to hold typed text: of the 3,794 written "
                 "records, 500 ran under half a second, 87 under 50 milliseconds, and the shortest "
                 "3 milliseconds; 336 of those 500 are in Spotlight, Signal, SpringBoard and "
                 "Messages. Reference: North Loop Consulting, "
                 "'Jot this down....Text.InputSession Biome Entries', 2026-09-06, "
                 "https://northloopconsulting.com/blog/f/jot-this-downtextinputsession-biome-entries"
                 "\n\nReference: Mattia Epifani, '84 Streams Later, Part 2: Inside Apple Biome', "
                 "https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html",
        "paths":
            ('*/Biome/streams/public/TextInputSession/local/*',
             '*/Biome/streams/restricted/Text.InputSession/local/*'),
        "output_types": "standard",
        "artifact_icon": "keyboard",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 683 rows",
            "felix_ios17": "iOS 17.6.1 | 140 rows",
            "fsfull002_ios17": "iOS 17.1 | 149 rows",
            "hc_ios18_7": "iOS 18.7.8 | 677 rows",
            "iphone11_ios17": "iOS 17.3 | 1742 rows",
            "iphone12_ios18": "iOS 18.7 | 489 rows",
            "iphone14plus_ios18": "iOS 18.0 | 103 rows",
            "otto_ios17": "iOS 17.5.1 | 764 rows",
            "abe_ios16": "iOS 16.5 | 1561 rows",
            "felix23_ios16": "iOS 16.5 | 299 rows",
            "jess_ios15": "iOS 15.0.2 | 99 rows",
            "magnet_ios16": "iOS 16.1.1 | 136 rows",
            "falken_ios26": "iOS 26.2.1 | 399 rows",
        }
    }
}


import os
from datetime import timezone
from scripts import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv, convert_ts_int_to_utc


@artifact_processor
def get_biomeTextinputses(context):

    typess = {
        '1': {'type': 'double', 'name': ''},
        '2': {'type': 'double', 'name': ''},
        '3': {'type': 'str', 'name': ''},
        '4': {'type': 'int', 'name': ''},
        '5': {'type': 'str', 'name': ''}
    }

    data_list = []
    source_dirs = set()
    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in file_found:
                continue
        else:
            continue

        source_dirs.add(os.path.dirname(file_found))
        for record in read_segb_file(file_found):
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                protostuff, _ = blackboxprotobuf.decode_message(record.data, typess)

                duration = protostuff['1']
                # Records in "restricted" folder seem to have time in Unix time, whereas public was cocoa time
                if 'restricted' in file_found:
                    timestart = convert_ts_int_to_utc(protostuff['2'])
                else:
                    timestart = (webkit_timestampsconv(protostuff['2']))

                bundleid = (protostuff.get('3',''))
                # Field 5 holds a per-session identifier. The older stream layout does not carry it.
                session_id = (protostuff.get('5',''))

                data_list.append((ts, timestart, record.state.name, bundleid, duration, session_id, filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Time Start', 'datetime'), 'SEGB State', 'Bundle ID', 'Duration',
                    'Session Identifier', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
