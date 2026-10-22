__artifacts_v2__ = {'ppv_ecd_albums': {'author': '@CyberMike81, OpenAI Codex',
                    'creation_date': '2026-10-22',
                    'last_update_date': '2026-10-22',
                    'requirements': 'none',
                    'category': 'Private Photo Vault',
                    'output_types': ['html', 'tsv', 'lava'],
                    'artifact_icon': 'lock',
                    'name': 'Private Photo Vault - ECD Albums',
                    'description': 'Vault album IDs, titles, relationships and stored states.',
                    'paths': ('*/PPV.ecd*',),
                    'notes': 'createdDate, modifiedDate and deletedDate are the corresponding '
                             'album-record fields in Unix seconds. Zero displays as 1970-01-01 '
                             'UTC; its application meaning is unknown. Invalid dates are blank; '
                             'raw values remain in Selected Metadata JSON. Parent/cover IDs and '
                             'flags are reported as stored. Only plaintext or already decrypted '
                             'stores are read; passwords are omitted.'},
 'ppv_ecd_media': {'author': '@CyberMike81, OpenAI Codex',
                   'creation_date': '2026-10-22',
                   'last_update_date': '2026-10-22',
                   'requirements': 'none',
                   'category': 'Private Photo Vault',
                   'output_types': ['html', 'tsv', 'lava'],
                   'artifact_icon': 'lock',
                   'name': 'Private Photo Vault - ECD Media Records',
                   'description': 'Vault media IDs, album references, lifecycle dates and stored '
                                  'view counters.',
                   'paths': ('*/PPV.ecd*',),
                   'notes': 'Dates are vault-record fields in Unix seconds: creation, '
                            'modification, favorite, trash, upload and local cloud-download. They '
                            'are not established original-file dates. Zero displays as 1970-01-01 '
                            'UTC with unknown application meaning; raw values remain in Selected '
                            'Metadata JSON. l_viewCount is a cumulative stored counter, not a '
                            'timed viewing sequence or operator identity. Session itemsViewed '
                            'cannot be allocated to individual files. Only plaintext/already '
                            'decrypted records are read; media and keys are not included.'},
 'ppv_ecd_parts': {'author': '@CyberMike81, OpenAI Codex',
                   'creation_date': '2026-10-22',
                   'last_update_date': '2026-10-22',
                   'requirements': 'none',
                   'category': 'Private Photo Vault',
                   'output_types': ['html', 'tsv', 'lava'],
                   'artifact_icon': 'lock',
                   'name': 'Private Photo Vault - ECD Media Parts',
                   'description': 'Stored media-part IDs, parent media IDs, sizes, offsets and '
                                  'hashes.',
                   'paths': ('*/PPV.ecd*',),
                   'notes': 'mediaItemSyncId links a part to its media record. Sizes, offsets, '
                            'hashes and local/cloud flags are reported as stored; the rows do not '
                            'establish current file availability or content. Selected Metadata '
                            'JSON retains the reported fields. Only plaintext or already decrypted '
                            'stores are read; media bytes are not included.'},
 'ppv_ecd_trespass': {'author': '@CyberMike81, OpenAI Codex',
                      'creation_date': '2026-10-22',
                      'last_update_date': '2026-10-22',
                      'requirements': 'none',
                      'category': 'Private Photo Vault',
                      'output_types': ['html', 'tsv', 'lava'],
                      'artifact_icon': 'lock',
                      'name': 'Private Photo Vault - ECD Trespass Records',
                      'description': 'App-stored login-related records, locations and file '
                                     'references.',
                      'paths': ('*/PPV.ecd*',),
                      'notes': 'date is the stored record time in Unix seconds. Zero displays as '
                               '1970-01-01 UTC with unknown application meaning; invalid dates are '
                               'blank and raw values remain in Selected Metadata JSON. loginType, '
                               'device/location fields and encryption state are reported as '
                               'stored. The record does not by itself establish a failed login or '
                               'identify an operator. File and thumbnail names are references, not '
                               'displayed media; only plaintext/already decrypted stores are '
                               'read.'},
 'ppv_activity_events': {'author': '@CyberMike81, OpenAI Codex',
                         'creation_date': '2026-10-22',
                         'last_update_date': '2026-10-22',
                         'requirements': 'none',
                         'category': 'Private Photo Vault',
                         'output_types': ['html', 'tsv', 'lava'],
                         'artifact_icon': 'lock',
                         'name': 'Private Photo Vault - Activity Events',
                         'description': 'App-associated analytics events and stored session '
                                        'metrics.',
                         'paths': ('*/PPV.ecd*',
                                   '*/Library/*_MPDB.sqlite*',
                                   '*/.com.apple.mobile_container_manager.metadata.plist'),
                         'notes': 'Event Time comes from properties.time; Time Divisor shows '
                                  'whether the raw value was treated as seconds or milliseconds. '
                                  'SQL Queue Time Raw is separate queue metadata. Event JSON '
                                  'preserves the event and raw values; invalid dates remain blank. '
                                  'App Association identifies the available app/container '
                                  'evidence; Container Identity Status flags conflicts or missing '
                                  'metadata. Labels and association do not prove a UI action or '
                                  'operator. Session itemsViewed is separate from per-file '
                                  'l_viewCount and cannot be allocated to files.'},
 'ppv_diagnostic_log': {'name': 'Private Photo Vault - Diagnostic Log',
                        'description': 'App diagnostic messages, record times and decoding status.',
                        'author': '@CyberMike81, OpenAI Codex',
                        'creation_date': '2026-10-22',
                        'last_update_date': '2026-10-22',
                        'requirements': 'none',
                        'category': 'Private Photo Vault',
                        'notes': 'Time is the source log time in Unix milliseconds; Time Raw '
                                 'retains the stored value and invalid dates remain blank. Message '
                                 'contains decoded diagnostic text; Message Hex and Decode Status '
                                 'preserve undecoded content. A diagnostic message is not proof '
                                 'that a file was viewed and does not identify the operator.',
                        'paths': ('*/Caches/com.crashlytics.data/com.enchantedcloud.photovault/*/log_*.clsrecord',),
                        'output_types': ['html', 'tsv', 'lava'],
                        'artifact_icon': 'file-text'}}

import json
import math
import os
import plistlib
import re
import sqlite3
from datetime import datetime, timezone
from xml.parsers.expat import ExpatError

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


def _container(path):
    match = re.search(r'(.*/Containers/Data/Application/[^/]+)/', str(path).replace('\\', '/'))
    return match.group(1) if match else ''


BUNDLE_ID = 'com.enchantedcloud.photovault'
ECD_SIGNATURES = {
    'ecdPersistentMediaItem': {'__objectid', 'syncId', 'albumSyncId'},
    'ecdPersistentAlbum': {'__objectid', 'syncId', 'title'},
    'ecdPersistentMediaItemPart': {'__objectid', 'syncId', 'mediaItemSyncId'},
    'ecdPersistentTresspassRecord': {'__objectid', 'syncId', 'loginType'},
}


def _ecd_schema(path, display_path):
    db = open_sqlite_db_readonly(path)
    if db is None:
        logfunc(f'Private Photo Vault: could not open ECD schema; file={display_path}')
        return False
    unreadable = False
    try:
        for table, required in ECD_SIGNATURES.items():
            try:
                columns = {r[1] for r in db.execute('PRAGMA table_info("' + table + '")')}
            except sqlite3.Error:
                unreadable = True
                logfunc(f'Private Photo Vault: unreadable ECD schema; table={table}; file={display_path}')
                continue
            if required <= columns:
                return True
    finally:
        db.close()
    if unreadable:
        logfunc(f'Private Photo Vault: could not verify ECD schema; some objects unreadable; file={display_path}')
    else:
        logfunc(f'Private Photo Vault: no supported ECD table signature; file={display_path}')
    return False


def _stores(context):
    for path in sorted({str(p) for p in context.get_files_found()}):
        if os.path.basename(path) not in ('PPV.ecd', 'PPV.ecd.decrypted') or not os.path.isfile(path):
            continue
        try:
            with open(path, 'rb') as handle:
                if handle.read(16) != b'SQLite format 3\x00':
                    logfunc(f'Private Photo Vault: not plaintext SQLite; cannot decode ECD; file={context.get_relative_path(path)}')
                    continue
        except OSError:
            logfunc(f'Private Photo Vault: could not read store signature; file={context.get_relative_path(path)}')
            continue
        if not _ecd_schema(path, context.get_relative_path(path)):
            continue
        yield path


def _app_containers(context):
    containers = {}
    for path in _stores(context):
        container = _container(path)
        if container:
            containers[container] = {'bases': ['Verified ECD schema in same container'],
                                     'bundle_id': None}
    for path in sorted({str(p) for p in context.get_files_found()}):
        if os.path.basename(path) != '.com.apple.mobile_container_manager.metadata.plist':
            continue
        container = _container(path)
        if not container or str(path).replace('\\', '/').rsplit('/', 1)[0] != container:
            continue
        try:
            with open(path, 'rb') as handle:
                metadata = plistlib.load(handle)
        except (OSError, ValueError, TypeError, OverflowError, plistlib.InvalidFileException, ExpatError):
            logfunc(f'Private Photo Vault: unreadable container metadata; file={context.get_relative_path(path)}')
            continue
        bundle = metadata.get('MCMMetadataIdentifier') if isinstance(metadata, dict) else None
        if not isinstance(bundle, str) or not bundle:
            logfunc(f'Private Photo Vault: missing or unsupported container identifier; file={context.get_relative_path(path)}')
            continue
        info = containers.setdefault(container, {'bases': [], 'bundle_id': None})
        info['bundle_id'] = bundle
        if bundle == BUNDLE_ID:
            info['bases'].append('Container metadata bundle ID')
    return containers


def _seconds(value, divisor=1):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return ''
    try:
        if isinstance(value, float) and not math.isfinite(value):
            return ''
        return datetime.fromtimestamp(value / divisor, timezone.utc)
    except (ValueError, OverflowError, OSError):
        return ''


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def _report_scalar(value):
    # SQLite's Python binder rejects integers beyond signed 64-bit even for TEXT
    # columns. Keep their exact digits; typed event values remain in Event JSON.
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, int) and not -(2**63) <= value < 2**63:
        return str(value)
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, (dict, list)):
        return _json(value)
    return value


def _rows(path, table, display_path):
    emitted = 0
    db = open_sqlite_db_readonly(path)
    if db is None:
        logfunc(f'Private Photo Vault: could not open {table}; file={display_path}')
        return
    try:
        present = db.execute("SELECT 1 FROM sqlite_master WHERE type IN ('table','view') "
                             "AND name = ? COLLATE NOCASE", (table,)).fetchone()
        if present is None:
            logfunc(f'Private Photo Vault: table not present; table={table}; file={display_path}')
            return
        cursor = db.execute('SELECT * FROM "' + table + '"')
        cols = [d[0] for d in cursor.description]
        for row in cursor:
            emitted += 1
            yield dict(zip(cols, row))
    except sqlite3.Error:
        logfunc(f'Private Photo Vault: unsupported or unreadable table={table}; read incomplete; rows emitted={emitted}; file={display_path}')
    finally:
        db.close()


def _records(context, table, fields, dates):
    rows = []
    source = ''
    for path in _stores(context):
        source = source or path
        for row in _rows(path, table, context.get_relative_path(path)):
            # Key/password fields are deliberately not copied into the selected metadata JSON.
            selected = {k: row[k] for k in dict.fromkeys(['__objectid'] + list(dates) + list(fields))
                        if k in row}
            rows.append((*(_seconds(row.get(k)) for k in dates),
                         row.get('__objectid'), *(row.get(k) for k in fields),
                         _json(selected), context.get_relative_path(path)))
    headers = tuple((k, 'datetime') for k in dates) + ('Object Row ID',) + tuple(
        k + ' (as stored)' for k in fields) + ('Selected Metadata JSON', 'Source File')
    return headers, rows, source


@artifact_processor
def ppv_ecd_albums(context):
    return _records(context, 'ecdPersistentAlbum', (
        'syncId', 'title', 'parentId', 'isDecoy', 'albumType', 'coverType', 'coverSyncId',
        'sortPosition', 'isExcludedFromScanning'), ('createdDate', 'modifiedDate', 'deletedDate'))


@artifact_processor
def ppv_ecd_media(context):
    return _records(context, 'ecdPersistentMediaItem', (
        'syncId', 'albumSyncId', 'fileType', 'largeFileExt', 'l_viewCount', 'imageWidth',
        'imageHeight', 'totalEncryptedSize', 'l_isDownloaded', 'isDecoy', 'purged',
        'hasMediumFile', 'sortPosition'),
        ('createdDate', 'modifiedDate', 'favoriteDate', 'trashedDate', 'uploadedDate', 'l_cloudDownloadDate'))


@artifact_processor
def ppv_ecd_parts(context):
    return _records(context, 'ecdPersistentMediaItemPart', (
        'syncId', 'mediaItemSyncId', 'size', 'contentOffset', 'contentHash', 'contentHashVersion',
        'contentType', 'l_expectedOnDisk', 'l_expectedInCloud', 'l_bytesTransfered'), ())


@artifact_processor
def ppv_ecd_trespass(context):
    return _records(context, 'ecdPersistentTresspassRecord', (
        'syncId', 'loginType', 'deviceName', 'latitude', 'longitude', 'fileName',
        'thumbFileName', 'isEncrypted'), ('date',))


def _event_time(value):
    # Expose the modern-event unit heuristic; never substitute SQL queue time.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return '', None
    if isinstance(value, float) and not math.isfinite(value):
        return '', None
    divisor = 1000 if abs(value) >= 100_000_000_000 else 1
    return _seconds(value, divisor), divisor


def _events(db, display_path):
    tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
              if re.fullmatch(r'mixpanel_[A-Za-z0-9_]+_events', r[0])]
    for table in tables:
        try:
            for row in db.execute('SELECT id,data,time FROM "' + table + '" ORDER BY id'):
                yield table, row
        except sqlite3.Error:
            logfunc(f'Private Photo Vault: unsupported or unreadable analytics table={table}; file={display_path}')


@artifact_processor
def ppv_activity_events(context):
    rows = []
    source = ''
    containers = _app_containers(context)
    for path in sorted({str(p) for p in context.get_files_found()}):
        if not path.endswith('_MPDB.sqlite') or not os.path.isfile(path):
            continue
        db = open_sqlite_db_readonly(path)
        if db is None:
            logfunc(f'Private Photo Vault: could not open analytics; file={context.get_relative_path(path)}')
            continue
        try:
            for table, (rowid, raw, queue_time) in _events(db, context.get_relative_path(path)):
                location = f'file={context.get_relative_path(path)}; table={table}; row={rowid}'
                try:
                    event = json.loads(raw)
                except (ValueError, TypeError, UnicodeError):
                    logfunc(f'Private Photo Vault: skipped malformed event JSON; {location}')
                    continue
                if not isinstance(event, dict) or not isinstance(event.get('properties'), dict):
                    logfunc(f'Private Photo Vault: unsupported event/properties shape; {location}')
                    continue
                props = event['properties']
                session = props.get('sessionParams')
                session = session if isinstance(session, dict) else {}
                outer, inner = props.get('bundleId'), session.get('bundleId')
                identifiers = [v for v in (outer, inner) if v is not None and v != '']
                if any(v != BUNDLE_ID for v in identifiers):
                    logfunc(f'Private Photo Vault: rejected foreign/conflicting app identifier; {location}')
                    continue
                info = containers.get(_container(path), {})
                bases = (['Event bundle ID'] if identifiers else []) + info.get('bases', [])
                if not bases:
                    logfunc(f'Private Photo Vault: skipped unlabelled event without verified app container; {location}')
                    continue
                association = '; '.join(bases)
                container_bundle = info.get('bundle_id')
                if container_bundle and container_bundle != BUNDLE_ID:
                    identity_status = 'Conflict: container metadata names another app'
                    logfunc(f'Private Photo Vault: app association conflicts with container metadata; {location}')
                elif container_bundle == BUNDLE_ID:
                    identity_status = 'Container metadata matches'
                else:
                    identity_status = 'Container metadata unavailable'
                source = source or path
                stamp, divisor = _event_time(props.get('time'))
                if stamp == '' and props.get('time') is not None:
                    logfunc(f'Private Photo Vault: invalid event time; raw retained; {location}')
                spent = session.get('timeSpent')
                spent = spent if isinstance(spent, dict) else {}
                rows.append(tuple(_report_scalar(value) for value in (
                             stamp, event.get('event'), rowid, props.get('time'), divisor,
                             queue_time, props.get('$ae_session_length'),
                             session.get('itemsViewed'), session.get('albumsViewed'),
                             spent.get('thumbnails'), spent.get('gallery'),
                             props.get('$app_version_string', props.get('$app_version')),
                             props.get('$os_version'), outer, inner, association, container_bundle,
                             identity_status, table, _json(event),
                             context.get_relative_path(path))))
        except sqlite3.Error:
            logfunc(f'Private Photo Vault: unreadable analytics database; file={context.get_relative_path(path)}')
        finally:
            db.close()
    return (('Event Time', 'datetime'), 'Event Name (as stored)', 'Event Row ID',
            'properties.time Raw', 'Time Divisor', 'SQL Queue Time Raw',
            'Session Length (as stored)', 'itemsViewed (as stored)', 'albumsViewed (as stored)',
            'timeSpent.thumbnails (as stored)', 'timeSpent.gallery (as stored)',
            'App Version', 'OS Version', 'Outer Bundle ID (as stored)', 'Session Bundle ID (as stored)',
            'App Association', 'Container Bundle ID (as stored)', 'Container Identity Status',
            'Source Table', 'Event JSON', 'Source File'), rows, source


@artifact_processor
def ppv_diagnostic_log(context):
    rows = []
    source = ''
    for path in sorted({str(p) for p in context.get_files_found()}):
        if not os.path.isfile(path) or not re.fullmatch(r'log_[^/]+\.clsrecord', os.path.basename(path)):
            continue
        source = source or path
        try:
            with open(path, 'rb') as handle:
                for line_number, line in enumerate(handle, 1):
                    try:
                        obj = json.loads(line)
                    except (ValueError, UnicodeError):
                        logfunc(f'Private Photo Vault diagnostics: skipped malformed JSON; file={context.get_relative_path(path)}; line={line_number}')
                        continue
                    entry = obj.get('log') if isinstance(obj, dict) else None
                    if not isinstance(entry, dict):
                        logfunc(f'Private Photo Vault diagnostics: unsupported log shape; file={context.get_relative_path(path)}; line={line_number}')
                        continue
                    raw = entry.get('msg')
                    if not isinstance(raw, str):
                        logfunc(f'Private Photo Vault diagnostics: non-string msg; file={context.get_relative_path(path)}; line={line_number}')
                        continue
                    try:
                        text = bytes.fromhex(raw).decode('utf-8')
                        status = 'Decoded hex UTF-8'
                    except (ValueError, UnicodeError):
                        text = ''
                        status = 'Undecoded; see message hex'
                    time_raw = entry.get('time')
                    stamp = _seconds(time_raw, 1000)
                    if stamp == '' and time_raw is not None:
                        logfunc(f'Private Photo Vault diagnostics: invalid time; raw retained; file={context.get_relative_path(path)}; line={line_number}')
                    rows.append((stamp, text, line_number, _report_scalar(time_raw), raw, status,
                                 context.get_relative_path(path)))
        except OSError:
            logfunc(f'Private Photo Vault diagnostics: could not read file={context.get_relative_path(path)}')
    return (('Log Time', 'datetime'), 'Message', 'Line Number', 'Time Raw (Unix milliseconds)',
            'Message Hex', 'Decode Status', 'Source File'), rows, source
