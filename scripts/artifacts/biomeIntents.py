__artifacts_v2__ = {
    "get_biomeIntents": {
        "name": "Biome - Intents",
        "description": "Parses app intent entries from biomes",
        "author": "@JohnHyla, @mattiaepi (Mattia Epifani)",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "Each record is parsed independently: a record that cannot be decoded is "
                 "logged with its file and offset and skipped, so one malformed entry no "
                 "longer discards the rest of the stream. Intent payloads are app-authored "
                 "and their inner shape varies by app and iOS version, so an app branch that "
                 "cannot read its own payload still emits the record metadata. Labels inside "
                 "the Data column (thread, sender, number) are inferred from observed record "
                 "content; the underlying protobuf fields are not documented.",
        "paths": (
            '*/AppIntent/local/*',
            '*/streams/*/App.Intent/local/*',
        ),
        "html_columns": ["Data"],
        "output_types": "standard",
        "artifact_icon": "bolt",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 460 rows",
            "felix23_ios16": "iOS 16.5 | 31 rows",
            "hickman_ios14": "iOS 14.3 | 277 rows",
            "jess_ios15": "iOS 15.0.2 | 30 rows",
            "magnet_ios16": "iOS 16.1.1 | 38 rows",
            "hc_ios18_7": "iOS 18.7.8 | 17 rows",
            "iphone11_ios17": "iOS 17.3 | 90 rows",
        },
    }
}

import os
import struct
from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import convert_time_obj_to_utc, get_plist_content, logfunc, artifact_processor
from scripts.html_safe import esc, safe_source

from datetime import datetime as _dt

_RECORD_ERRORS = (DecodeError, struct.error, AttributeError, KeyError, ValueError,
                  TypeError, IndexError, UnicodeDecodeError)


_CONTROL_MAP = str.maketrans({'\t': '\\t', '\r': '\\r', '\n': '\\n', '\x00': ''})


def _safe_time_obj(value):
    """Set UTC tzinfo on datetime objects; pass strings/None through unchanged."""
    return convert_time_obj_to_utc(value) if isinstance(value, _dt) else value


def _delimited_safe(value):
    """Keep intent payloads on one line and free of NULs.

    Intent data is an app-authored blob, so it can carry tabs, line breaks and
    NUL bytes. Those are legal in the HTML report but break or disfigure the TSV
    export, and a writer configured without quoting rejects them outright.
    Tabs and line breaks become their printable escapes so no content is lost.
    """
    return value.translate(_CONTROL_MAP) if isinstance(value, str) else value


def _intent_payload(deserialized_plist):
    """Return the raw inner intent protobuf bytes, or None when absent."""
    intent = deserialized_plist.get('intent')
    backing_store = intent.get('backingStore') if isinstance(intent, dict) else None
    raw = backing_store.get('bytes') if isinstance(backing_store, dict) else None
    return raw if isinstance(raw, bytes) else None


def _notes_data(protostuffinner):
    """Notes intents carry field 2 either as a submessage or as raw bytes."""
    first = protostuffinner.get('1')
    action = first.get('16') if isinstance(first, dict) else None
    action = action.decode() if isinstance(action, bytes) else ('' if action is None else action)
    second = protostuffinner.get('2')
    if isinstance(second, dict):
        field_one, field_two = second.get('1'), second.get('2')
    else:
        field_one = second.decode('latin-1') if isinstance(second, bytes) else second
        field_two = ''
    return f'Action: {action}, Data Field 1: {field_one}, Data Field 2: {field_two}'


def _parse_record(protostuff, filename, offset):
    """Build the plain and HTML rows for one intent record, or None to skip it."""
    typeofintent = protostuff.get('2', '')
    try:
        typeofintent = typeofintent.decode()
    except (AttributeError, UnicodeDecodeError):
        logfunc(f'Biome Intents: record at offset {offset} in {filename} skipped, '
                'app id is not a decodable string')
        return None
    appid = typeofintent

    classname = (protostuff.get('4', ''))
    try:
        classname = classname.decode()
    except (AttributeError, UnicodeDecodeError):
        pass

    action = protostuff.get('5')

    deserialized_plist = get_plist_content(protostuff.get('8'))
    if not deserialized_plist or not isinstance(deserialized_plist, dict):
        logfunc(f'Biome Intents: record at offset {offset} in {filename} skipped, '
                'intent plist could not be deserialized')
        return None

    date_interval = deserialized_plist.get('dateInterval')
    if not isinstance(date_interval, dict):
        date_interval = {}
    startdate = _safe_time_obj(date_interval.get('NS.startDate'))
    enddate = _safe_time_obj(date_interval.get('NS.endDate'))
    durationinterval = date_interval.get('NS.duration')

    donatedbysiri = 'True' if deserialized_plist.get('_donatedBySiri') else 'False'
    groupid = deserialized_plist.get('groupIdentifier', '')

    direction = deserialized_plist.get('direction')
    if direction == 0:
        direction = 'Unspecified'
    elif direction == 1:
        direction = 'Outgoing'
    elif direction == 2:
        direction = 'Incoming'

    raw_intent = _intent_payload(deserialized_plist)
    if raw_intent is None:
        logfunc(f'Biome Intents: record at offset {offset} in {filename} skipped, '
                'intent backing store holds no bytes')
        return None
    protostuffinner, _ = blackboxprotobuf.decode_message(raw_intent)

    # Defaults, so an app branch that cannot read its own payload still returns a row
    # carrying the record metadata instead of raising.
    datos = ''
    datoshtml = 'Unsupported intent.'

    try:
        #Instagram
        if typeofintent == 'com.burbn.instagram':
            datos = raw_intent.decode('latin-1')
            datoshtml = safe_source(datos)

        #snapchat
        elif typeofintent == 'com.toyopagroup.picaboo':
            datos = raw_intent.decode('latin-1')
            datoshtml = safe_source(datos)

        #notes
        elif typeofintent == 'com.apple.assistant_service':
            datos = raw_intent.decode('latin-1')
            datoshtml = safe_source(datos)

        #notes
        elif typeofintent == 'com.apple.mobilenotes':
            datos = _notes_data(protostuffinner)
            datoshtml = (esc(datos).replace(',', '<br>'))

        #telegraph
        elif typeofintent == 'ph.telegra.Telegraph':
            datos = raw_intent.decode('latin-1')
            datoshtml = safe_source(datos)

        #calls
        elif typeofintent == 'com.apple.InCallService':
            a = ''
            try:
                a = (protostuffinner['5']['1']['4'].decode()) #content number
            except (KeyError, TypeError, AttributeError, UnicodeDecodeError):
                pass

            datos = f'Number: {a}'
            datoshtml = (esc(datos).replace(',', '<br>'))

        #whatsapp
        elif typeofintent == 'net.whatsapp.WhatsApp':
            datos = str(protostuffinner)
            datoshtml = safe_source(datos)

        elif typeofintent == 'org.whispersystems.signal':
            datos = str(protostuffinner)
            datoshtml = safe_source(datos)

        #sms
        elif typeofintent == 'com.apple.MobileSMS':
            if protostuffinner.get('5', '') != '':
                if type(protostuffinner['5']['1']['2']) is not dict:
                    a = protostuffinner['5']['1']['2'].decode()
                else:
                    a = protostuffinner['5']['1']['2']

                b = (protostuffinner.get('8', ''))#threadid

                c = (protostuffinner.get('15', ''))#senderid if not binary show dict

                datos = f'Thread ID: {b}, Sender ID: {c}, Content:, {a}'
                datoshtml = (esc(datos).replace(',', '<br>'))

        #maps
        elif typeofintent == 'com.apple.Maps':
            if (protostuffinner['4'][0]['2']['2']['2']) == b'com.apple.Maps':
                a = (protostuffinner['3'].decode()) #action
                b = (protostuffinner['1']['16'].decode()) #value

                c = (protostuffinner['4'][0]['1'].decode())#source
                d = (protostuffinner['4'][0]['2']['2']['2'].decode()) #value of above

                e = (protostuffinner['4'][1]['1'].decode()) #nav_identifier
                f = (protostuffinner['4'][1]['2']['2']['2'].decode()) #value of above

                g = (protostuffinner['4'][2]['1'].decode()) #navigation_type
                h = (protostuffinner['4'][2]['2']['2']['2'].decode()) #value of above

                datos = f'{a}: {b}, {c}: {d}, {e}: {f}, {g}: {h}'
                datoshtml = (esc(datos).replace(',', '<br>'))

            else:
                datos = ''
                a = (protostuffinner['3'].decode()) #action
                b = (protostuffinner['1']['16'].decode()) #value

                datos = datos + f'{a}: {b},'

                for loopy in protostuffinner['4']:
                    a = loopy['1'].decode()
                    try:
                        b = loopy['2']['2']['2']
                    except (KeyError, TypeError):
                        b = loopy['2']
                    datos = datos + f'{a}: {b},'

                datoshtml = (esc(datos).replace(',', '<br>'))
    except _RECORD_ERRORS as ex:
        logfunc(f'Biome Intents: record at offset {offset} in {filename} kept without intent '
                f'data, {appid} payload could not be read, {type(ex).__name__}: {ex}')
        datos = ''
        datoshtml = 'Intent data could not be parsed.'

    row = (startdate, enddate, durationinterval, donatedbysiri, appid, classname, action,
           direction, groupid, _delimited_safe(datos), filename, offset)
    row_html = (startdate, enddate, durationinterval, donatedbysiri, appid, classname, action,
                direction, groupid, datoshtml, filename, offset)
    return row, row_html


@artifact_processor
def get_biomeIntents(context):
    data_headers = (('Timestamp', 'datetime'), ('End Date', 'datetime'), 'Duration Interval', 'Donated by Siri',
                         'App ID', 'Classname', 'Action', 'Direction', 'Group ID', 'Data', 'Filename',
                         'Protobuf data Offset')
    files_found = context.get_files_found()
    files_found = sorted(files_found)

    data_list_html = []
    data_list = []
    source_dirs = set()
    for file_found in files_found:
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
            if record.state != EntryState.Written:
                continue
            offset = record.data_start_offset
            try:
                protostuff, _ = blackboxprotobuf.decode_message(record.data)
                parsed = _parse_record(protostuff, filename, offset)
            except _RECORD_ERRORS as ex:
                logfunc(f'Biome Intents: record at offset {offset} in {filename} skipped, '
                        f'{type(ex).__name__}: {ex}')
                continue
            if parsed is None:
                continue
            row, row_html = parsed
            data_list.append(row)
            data_list_html.append(row_html)

    return data_headers, (data_list, data_list_html), '\n'.join(sorted(source_dirs))
