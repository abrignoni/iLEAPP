__artifacts_v2__ = {
    "faceTimeMessages": {
        "name": "FaceTime Messages",
        "description": "Video and audio messages in FaceTimeMessageStore-local.sqlitedb, with sender, "
                       "recipient, duration, transcript and the recorded media file",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-01",
        "last_update_date": "2026-11-01",
        "requirements": "none",
        "category": "FaceTime",
        "notes": ("One row per ZSTOREDMESSAGE row in FaceTimeMessageStore-local.sqlitedb under "
                  "mobile/Library/Application Support/com.apple.FaceTime. Date Created and Date Modified are "
                  "ZDATECREATED and ZDATEMODIFIED, Core Data timestamps shown in UTC; Date Modified was at or "
                  "after Date Created on all 17 tested rows. From, Recipient, File Type and Provider are ZFROM,"
                  " ZRECIPIENT, ZFILETYPE and ZPROVIDER as stored; Provider held com.apple.coretelephony on all"
                  " 17 tested rows. Duration is ZDURATION: on the 6 tested messages measured with afinfo and "
                  "Spotlight it was within 0.7 seconds of the media file's own duration, so it is shown as "
                  "seconds. Message is the media file under Assets/<folder>/ named for the row's ZRECORDUUID "
                  "with ZFILETYPE as its extension, a link the store records: on dexter_ios18 and otto_ios17 "
                  "every ZRECORDUUID named one asset stem (6 of 6), and all 17 tested rows had their file. MOV "
                  "files are video and amr files audio; Message Type (ZMESSAGETYPE) was 0 on every MOV row and "
                  "1 on every amr row on the tested images and is shown as stored. Transcript is the text of "
                  "the keyed archive in ZTRANSCRIPT: transcriptionString when it is a dictionary, the word "
                  "texts joined in order when it is a list. It was blank on 8 of 17 tested rows: the 7 rows "
                  "whose Transcription Status (ZTRANSCRIPTIONSTATUS) was 0 and 1 row with status 4 whose "
                  "ZTRANSCRIPT was empty. Read, Message Type, Mailbox Type and Transcription Status are "
                  "integers as stored; their meanings are not established (Mailbox Type 0 on 16 rows and 2 on "
                  "1). The .transcript and .plist files beside each asset repeat transcript text and word "
                  "confidences and are not read. Not reported: ZCALLUUID and ZCONVERSATIONID (the call UUID "
                  "matched no CallHistory.storedata ZUNIQUE_ID on the 6 checked messages), ZSIMID, ZQUALITY, "
                  "the CloudKit mirroring tables, FaceTimeMessageStore-local-properties.sqlitedb "
                  "(ZLOCALMESSAGEPROPERTIES, a voicemail ID per record UUID) and the empty temp store. Rows "
                  "were seen only on iOS 17 and later images. Not tested on an iTunes backup."),
        "paths": ('*/mobile/Library/Application Support/com.apple.FaceTime/FaceTimeMessageStore-local.sqlitedb*',
                  '*/mobile/Library/Application Support/com.apple.FaceTime/Assets/*/*'),
        "output_types": "standard",
        "artifact_icon": "video",
        "sample_data": {
            "cookbook_ios1751": "iOS 17.5.1 | 1 row",
            "dexter_ios18": "iOS 18.3.2 | 3 rows",
            "felix_ios17": "iOS 17.6.1 | 4 rows",
            "hc_ios17_2": "iOS 17.2.1 | 3 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "hc_ios26": "iOS 26.5.2 | 1 row",
            "otto_ios17": "iOS 17.5.1 | 3 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
        }
    }
}

import os
import uuid

import nska_deserialize as nd

from scripts.ilapfuncs import (artifact_processor, check_in_media, convert_cocoa_core_data_ts_to_utc,
                               does_column_exist_in_db, get_sqlite_db_records, logfunc)

STORE_NAME = 'FaceTimeMessageStore-local.sqlitedb'


def _uuid_text(value):
    """A 16-byte UUID blob as its usual upper-case text form, or '' when it is not one."""
    if isinstance(value, (bytes, bytearray)) and len(value) == 16:
        return str(uuid.UUID(bytes=bytes(value))).upper()
    return ''


def _transcript_text(blob):
    """The text of the keyed archive in ZTRANSCRIPT.

    Audio messages carry a dictionary with transcriptionString; video messages carry a list of
    word entries with text and confidence, which are joined in order.
    """
    if not isinstance(blob, (bytes, bytearray)):
        return ''
    try:
        transcript = nd.deserialize_plist_from_string(bytes(blob))
    except (ValueError, TypeError, nd.DeserializeError) as ex:
        logfunc(f'FaceTime Messages: transcript not decoded: {ex}')
        return ''
    if isinstance(transcript, dict):
        return str(transcript.get('transcriptionString') or '')
    if isinstance(transcript, list):
        return ' '.join(str(entry.get('text', '')) for entry in transcript
                        if isinstance(entry, dict) and entry.get('text'))
    return ''


def _asset_index(files_found):
    """{(FaceTime folder, record UUID): [(extension, path)]} for the files under Assets.

    An asset file is named for the message's ZRECORDUUID, so the name carries the link.
    The FaceTime folder is part of the key so two extraction roots never share files.
    """
    index = {}
    for entry in files_found:
        path = str(entry)
        parent = os.path.dirname(path)
        if not os.path.isfile(path) or os.path.basename(os.path.dirname(parent)) != 'Assets':
            continue
        facetime = os.path.dirname(os.path.dirname(parent))
        stem, _, extension = os.path.basename(path).partition('.')
        index.setdefault((facetime, stem.upper()), []).append((extension, path))
    return index


@artifact_processor
def faceTimeMessages(context):
    data_headers = (('Date Created', 'datetime'), ('Date Modified', 'datetime'), 'From', 'Recipient',
                    'File Type', 'Duration (seconds)', ('Message', 'media'), 'Transcript',
                    'Read (as stored)', 'Message Type (as stored)', 'Mailbox Type (as stored)',
                    'Transcription Status (as stored)', 'Provider', 'Record UUID')
    files_found = context.get_files_found()
    assets = _asset_index(files_found)
    data_list = []
    sources = []
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.basename(file_found) != STORE_NAME or file_found in sources:
            continue
        if not does_column_exist_in_db(file_found, 'ZSTOREDMESSAGE', 'ZRECORDUUID'):
            logfunc(f'FaceTime Messages: no ZSTOREDMESSAGE.ZRECORDUUID in {file_found}')
            continue
        rows = get_sqlite_db_records(file_found, '''
            SELECT ZDATECREATED, ZDATEMODIFIED, ZFROM, ZRECIPIENT, ZFILETYPE, ZDURATION, ZTRANSCRIPT,
                   ZISREAD, ZMESSAGETYPE, ZMAILBOXTYPE, ZTRANSCRIPTIONSTATUS, ZPROVIDER, ZRECORDUUID
            FROM ZSTOREDMESSAGE''')
        sources.append(file_found)
        facetime = os.path.dirname(file_found)
        for (created, modified, sender, recipient, file_type, duration, transcript, is_read,
             message_type, mailbox_type, status, provider, record) in rows:
            record_uuid = _uuid_text(record)
            media = ''
            for extension, path in sorted(assets.get((facetime, record_uuid), [])):
                if file_type and extension.lower() == str(file_type).lower():
                    media = check_in_media(path, os.path.basename(path)) or ''
            data_list.append((convert_cocoa_core_data_ts_to_utc(created),
                              convert_cocoa_core_data_ts_to_utc(modified), sender or '',
                              recipient or '', file_type or '', duration if duration is not None else '',
                              media, _transcript_text(transcript), is_read, message_type, mailbox_type,
                              status, provider or '', record_uuid))

    return data_headers, data_list, '\n'.join(sources)
