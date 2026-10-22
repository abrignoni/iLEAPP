__artifacts_v2__ = {'ppv_ecd_albums': {'author': '@CyberMike81, OpenAI Codex',
                    'creation_date': '2026-10-22',
                    'last_update_date': '2026-10-22',
                    'requirements': 'none',
                    'category': 'Private Photo Vault',
                    'output_types': ['html', 'tsv', 'lava'],
                    'artifact_icon': 'lock',
                    'name': 'Private Photo Vault - ECD Albums',
                    'description': 'Album rows from a plaintext or already decrypted PPV.ecd '
                                   'store.',
                    'paths': ('*/PPV.ecd*',),
                    'notes': 'Reads plaintext/already decrypted ECD SQLite only; does not decrypt '
                             'or render media. Supported ECD table signatures are required, not '
                             'merely a matching filename. Dates use Unix seconds. Raw numeric '
                             'dates remain in Selected Metadata JSON; invalid dates display blank. '
                             'Zero is displayed literally as 1970-01-01 UTC; whether it means '
                             'unset is unverified. Password fields are excluded. Unknown flags are '
                             'reported as stored. deletedDate, parentId (as stored) and '
                             'coverSyncId (as stored) were empty in private validation; retained '
                             'for populated stores. coverType (as stored) and '
                             'isExcludedFromScanning (as stored) were uniform but are independent '
                             'configuration fields. See admin/docs/private_photo_vault_ecd.md for '
                             'exclusions and validation boundaries. '},
 'ppv_ecd_media': {'author': '@CyberMike81, OpenAI Codex',
                   'creation_date': '2026-10-22',
                   'last_update_date': '2026-10-22',
                   'requirements': 'none',
                   'category': 'Private Photo Vault',
                   'output_types': ['html', 'tsv', 'lava'],
                   'artifact_icon': 'lock',
                   'name': 'Private Photo Vault - ECD Media Records',
                   'description': 'Stored media metadata, album references and l_viewCount values '
                                  'from PPV.ecd.',
                   'paths': ('*/PPV.ecd*',),
                   'notes': 'Reads plaintext/already decrypted ECD SQLite only; does not decrypt '
                            'or render media. Supported ECD table signatures are required, not '
                            'merely a matching filename. Dates use Unix seconds. Raw numeric dates '
                            'remain in Selected Metadata JSON; invalid dates display blank. Zero '
                            'is displayed literally as 1970-01-01 UTC; whether it means unset is '
                            'unverified. Encryption keys are excluded. l_viewCount is a cumulative '
                            'stored field, not a timestamped sequence or operator identity. '
                            'Session itemsViewed is separate and cannot be allocated to media '
                            'counters. favoriteDate, trashedDate, uploadedDate and '
                            'l_cloudDownloadDate were empty in private validation; retained as '
                            'source lifecycle fields. l_isDownloaded (as stored), isDecoy (as '
                            'stored) and purged (as stored) were uniform, retained as independent '
                            'states. See admin/docs/private_photo_vault_ecd.md for exclusions and '
                            'validation boundaries. '},
 'ppv_ecd_parts': {'author': '@CyberMike81, OpenAI Codex',
                   'creation_date': '2026-10-22',
                   'last_update_date': '2026-10-22',
                   'requirements': 'none',
                   'category': 'Private Photo Vault',
                   'output_types': ['html', 'tsv', 'lava'],
                   'artifact_icon': 'lock',
                   'name': 'Private Photo Vault - ECD Media Parts',
                   'description': 'Stored part references, byte sizes and content hashes from '
                                  'PPV.ecd.',
                   'paths': ('*/PPV.ecd*',),
                   'notes': 'Reads plaintext/already decrypted ECD SQLite only; does not decrypt '
                            'or render media. Supported ECD table signatures are required, not '
                            'merely a matching filename. Part/media IDs, sizes, offsets, hashes '
                            'and local/cloud flags are reported as stored. The private table was '
                            'empty; populated rows are synthetic-tested only. See '
                            'admin/docs/private_photo_vault_ecd.md for exclusions and validation '
                            'boundaries. '},
 'ppv_ecd_trespass': {'author': '@CyberMike81, OpenAI Codex',
                      'creation_date': '2026-10-22',
                      'last_update_date': '2026-10-22',
                      'requirements': 'none',
                      'category': 'Private Photo Vault',
                      'output_types': ['html', 'tsv', 'lava'],
                      'artifact_icon': 'lock',
                      'name': 'Private Photo Vault - ECD Trespass Records',
                      'description': 'Rows of ecdPersistentTresspassRecord, with stored login type '
                                     'and file references.',
                      'paths': ('*/PPV.ecd*',),
                      'notes': 'Reads plaintext/already decrypted ECD SQLite only; does not '
                               'decrypt or render media. Supported ECD table signatures are '
                               'required, not merely a matching filename. Dates use Unix seconds. '
                               'Raw numeric dates remain in Selected Metadata JSON; invalid dates '
                               'display blank. Zero is displayed literally as 1970-01-01 UTC; '
                               'whether it means unset is unverified. The table name does not '
                               'prove a failed login or identify an operator. loginType and '
                               'isEncrypted are reported as stored. fileName and thumbFileName are '
                               'text references only: media bytes are not selected or rendered by '
                               'this artifact. The private table was empty; populated rows are '
                               'synthetic-tested only. See admin/docs/private_photo_vault_ecd.md '
                               'for exclusions and validation boundaries. '},
 'ppv_activity_events': {'author': '@CyberMike81, OpenAI Codex',
                         'creation_date': '2026-10-22',
                         'last_update_date': '2026-10-22',
                         'requirements': 'none',
                         'category': 'Private Photo Vault',
                         'output_types': ['html', 'tsv', 'lava'],
                         'artifact_icon': 'lock',
                         'name': 'Private Photo Vault - Activity Events',
                         'description': 'Mixpanel event records and session metrics associated '
                                        'with Private Photo Vault.',
                         'paths': ('*/PPV.ecd*',
                                   '*/Library/*_MPDB.sqlite*',
                                   '*/.com.apple.mobile_container_manager.metadata.plist'),
                         'notes': 'Both outer and session bundleId fields are checked: any '
                                  'nonempty foreign or conflicting ID is rejected and logged. An '
                                  'event with neither ID requires a schema-verified ECD store or a '
                                  'matching MCMMetadataIdentifier in the same container. '
                                  'Non-SQLite PPV.ecd bytes alone do not identify the app; '
                                  'encrypted/non-plaintext stores need independent container '
                                  'metadata. App Association records the acceptance basis; bundle '
                                  'labels and container association do not prove a PPV UI action. '
                                  'Event Time uses properties.time; absolute numeric values at '
                                  'least 100000000000 are divided by 1000, otherwise by 1. Invalid '
                                  'times remain blank; properties.time Raw, Time Divisor and '
                                  'complete Event JSON are retained. SQL Queue Time Raw is not '
                                  'event time. Session itemsViewed is separate from l_viewCount, '
                                  'not allocated to media counters and does not identify the '
                                  'operator. Bad tables/records are logged with file/table/row '
                                  'context and do not suppress later tables. SQL Queue Time Raw '
                                  'and Source Table were uniform in private validation; retained '
                                  'as independent queue metadata and record provenance. See '
                                  'admin/docs/private_photo_vault_ecd.md for exclusions and '
                                  'validation boundaries. '},
 'ppv_diagnostic_log': {'name': 'Private Photo Vault - Diagnostic Log',
                        'description': 'Timestamped diagnostic text from the app-scoped '
                                       'Crashlytics log records.',
                        'author': '@CyberMike81, OpenAI Codex',
                        'creation_date': '2026-10-22',
                        'last_update_date': '2026-10-22',
                        'requirements': 'none',
                        'category': 'Private Photo Vault',
                        'notes': 'Reads app-scoped newline-delimited JSON log objects; msg is hex '
                                 'UTF-8 and time is Unix milliseconds. Message is reported text, '
                                 'not an identified operator or proof a media file was viewed. '
                                 'Malformed JSON and unsupported shapes are logged with file/line '
                                 'context and skipped. Undecodable messages retain Message Hex and '
                                 'Decode Status. Invalid dates remain blank with Time Raw '
                                 'retained. Decode Status was uniform in private validation; '
                                 'retained for raw-only records on other inputs. See '
                                 'admin/docs/private_photo_vault_ecd.md for exclusions and '
                                 'validation boundaries. ',
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


def _ecd_schema(path):
    db = open_sqlite_db_readonly(path)
    if db is None:
        return False
    try:
        for table, required in ECD_SIGNATURES.items():
            columns = {r[1] for r in db.execute('PRAGMA table_info("' + table + '")')}
            if required <= columns:
                return True
    except sqlite3.Error:
        logfunc(f'Private Photo Vault: unreadable ECD schema; file={path}')
    finally:
        db.close()
    return False


def _stores(context):
    for path in sorted({str(p) for p in context.get_files_found()}):
        if os.path.basename(path) not in ('PPV.ecd', 'PPV.ecd.decrypted') or not os.path.isfile(path):
            continue
        try:
            with open(path, 'rb') as handle:
                if handle.read(16) != b'SQLite format 3\x00':
                    logfunc(f'Private Photo Vault: not plaintext SQLite; cannot decode ECD; file={path}')
                    continue
        except OSError:
            logfunc(f'Private Photo Vault: could not read store signature; file={path}')
            continue
        if not _ecd_schema(path):
            logfunc(f'Private Photo Vault: no supported ECD table signature; file={path}')
            continue
        yield path


def _app_containers(context):
    containers = {_container(p): 'Verified ECD schema in same container' for p in _stores(context)}
    for path in sorted({str(p) for p in context.get_files_found()}):
        if os.path.basename(path) != '.com.apple.mobile_container_manager.metadata.plist':
            continue
        container = _container(path)
        if str(path).replace('\\', '/').rsplit('/', 1)[0] != container:
            continue
        try:
            with open(path, 'rb') as handle:
                metadata = plistlib.load(handle)
        except (OSError, ValueError, TypeError, OverflowError, plistlib.InvalidFileException, ExpatError):
            logfunc(f'Private Photo Vault: unreadable container metadata; file={path}')
            continue
        if isinstance(metadata, dict) and metadata.get('MCMMetadataIdentifier') == BUNDLE_ID:
            containers[_container(path)] = 'Container metadata bundle ID'
    containers.pop('', None)
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


def _rows(path, table):
    db = open_sqlite_db_readonly(path)
    if db is None:
        logfunc(f'Private Photo Vault: could not open {table}; file={path}')
        return
    try:
        cursor = db.execute('SELECT * FROM "' + table + '"')
        cols = [d[0] for d in cursor.description]
        for row in cursor:
            yield dict(zip(cols, row))
    except sqlite3.Error:
        logfunc(f'Private Photo Vault: unsupported or unreadable table={table}; file={path}')
    finally:
        db.close()


def _records(context, table, fields, dates):
    rows = []
    source = ''
    for path in _stores(context):
        source = source or path
        for row in _rows(path, table):
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


def _events(db, path):
    tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
              if re.fullmatch(r'mixpanel_[A-Za-z0-9_]+_events', r[0])]
    for table in tables:
        try:
            for row in db.execute('SELECT id,data,time FROM "' + table + '" ORDER BY id'):
                yield table, row
        except sqlite3.Error:
            logfunc(f'Private Photo Vault: unsupported or unreadable analytics table={table}; file={path}')


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
            logfunc(f'Private Photo Vault: could not open analytics; file={path}')
            continue
        try:
            for table, (rowid, raw, queue_time) in _events(db, path):
                location = f'file={path}; table={table}; row={rowid}'
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
                association = 'Event bundle ID' if identifiers else containers.get(_container(path))
                if not association:
                    logfunc(f'Private Photo Vault: skipped unlabelled event without verified app container; {location}')
                    continue
                source = source or path
                stamp, divisor = _event_time(props.get('time'))
                if stamp == '' and props.get('time') is not None:
                    logfunc(f'Private Photo Vault: invalid event time; raw retained; {location}')
                spent = session.get('timeSpent')
                spent = spent if isinstance(spent, dict) else {}
                rows.append((stamp, event.get('event'), rowid, props.get('time'), divisor,
                             queue_time, props.get('$ae_session_length'),
                             session.get('itemsViewed'), session.get('albumsViewed'),
                             spent.get('thumbnails'), spent.get('gallery'),
                             props.get('$app_version_string', props.get('$app_version')),
                             props.get('$os_version'), outer, inner, association, table, _json(event),
                             context.get_relative_path(path)))
        except sqlite3.Error:
            logfunc(f'Private Photo Vault: unreadable analytics database; file={path}')
        finally:
            db.close()
    return (('Event Time', 'datetime'), 'Event Name (as stored)', 'Event Row ID',
            'properties.time Raw', 'Time Divisor', 'SQL Queue Time Raw',
            'Session Length (as stored)', 'itemsViewed (as stored)', 'albumsViewed (as stored)',
            'timeSpent.thumbnails (as stored)', 'timeSpent.gallery (as stored)',
            'App Version', 'OS Version', 'Outer Bundle ID (as stored)', 'Session Bundle ID (as stored)',
            'App Association', 'Source Table', 'Event JSON', 'Source File'), rows, source


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
                        logfunc(f'Private Photo Vault diagnostics: skipped malformed JSON; file={path}; line={line_number}')
                        continue
                    entry = obj.get('log') if isinstance(obj, dict) else None
                    if not isinstance(entry, dict):
                        logfunc(f'Private Photo Vault diagnostics: unsupported log shape; file={path}; line={line_number}')
                        continue
                    raw = entry.get('msg')
                    if not isinstance(raw, str):
                        logfunc(f'Private Photo Vault diagnostics: non-string msg; file={path}; line={line_number}')
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
                        logfunc(f'Private Photo Vault diagnostics: invalid time; raw retained; file={path}; line={line_number}')
                    rows.append((stamp, text, line_number, time_raw, raw, status,
                                 context.get_relative_path(path)))
        except OSError:
            logfunc(f'Private Photo Vault diagnostics: could not read file={path}')
    return (('Log Time', 'datetime'), 'Message', 'Line Number', 'Time Raw (Unix milliseconds)',
            'Message Hex', 'Decode Status', 'Source File'), rows, source
