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
                    'notes': 'Created, Modified and Deleted are album-record Unix timestamps; zero '
                             'dates are blank. Album ID is syncId and Parent Album ID is parentId. '
                             'Metadata JSON retains the selected source fields and raw dates. '
                             'Requires a plaintext or already-decrypted ECD store.'},
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
                   'notes': 'Dates are the media-record lifecycle fields in Unix seconds, not '
                            'file-view times. Media ID and Album ID are syncId and albumSyncId. '
                            'View Count is l_viewCount; it has no viewing time or operator field. '
                            'Zero dates are blank; raw values remain in Metadata JSON. Requires a '
                            'plaintext or already-decrypted ECD; media is not decrypted or '
                            'displayed.'},
 'ppv_diagnostic_log': {'name': 'Private Photo Vault - Diagnostic Log',
                        'description': 'Timestamped app diagnostic messages and activity '
                                       'breadcrumbs from Crashlytics log records.',
                        'author': '@CyberMike81, OpenAI Codex',
                        'creation_date': '2026-10-22',
                        'last_update_date': '2026-10-22',
                        'requirements': 'none',
                        'category': 'Private Photo Vault',
                        'notes': 'Log Time is log.time in Unix milliseconds; zero dates are blank. '
                                 'Message is hex-decoded UTF-8 from log.msg. Raw time, message hex '
                                 'and source line are retained. App-reported breadcrumbs do not '
                                 'identify an operator or establish that a file was viewed.',
                        'paths': ('*/Caches/com.crashlytics.data/com.enchantedcloud.photovault/*/log_*.clsrecord',),
                        'output_types': ['html', 'tsv', 'lava'],
                        'artifact_icon': 'file-text'}}

import json
import math
import os
import re
import sqlite3
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly

ECD_SIGNATURES = {
    'ecdPersistentMediaItem': {'__objectid', 'syncId', 'albumSyncId'},
    'ecdPersistentAlbum': {'__objectid', 'syncId', 'title'},
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


def _seconds(value, divisor=1):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return ''
    if value == 0:
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
            # Only explicitly selected metadata is reported; keys/passwords stay out.
            selected = {k: row[k] for k in dict.fromkeys(
                ['__objectid'] + [k for k, _ in dates] + [k for k, _ in fields]) if k in row}
            rows.append((*(_seconds(row.get(k)) for k, _ in dates),
                         row.get('__objectid'), *(row.get(k) for k, _ in fields),
                         _json(selected), context.get_relative_path(path)))
    headers = tuple((label, 'datetime') for _, label in dates) + ('Object Row ID',) + tuple(
        label for _, label in fields) + ('Metadata JSON', 'Source File')
    return headers, rows, source


@artifact_processor
def ppv_ecd_albums(context):
    return _records(context, 'ecdPersistentAlbum', (
        ('syncId', 'Album ID'), ('title', 'Title'), ('parentId', 'Parent Album ID'),
        ('isDecoy', 'Decoy Flag (as stored)'), ('albumType', 'Album Type (as stored)'),
        ('coverType', 'Cover Type (as stored)'), ('coverSyncId', 'Cover ID'),
        ('sortPosition', 'Sort Position'), ('isExcludedFromScanning', 'Excluded from Scanning (as stored)')),
        (('createdDate', 'Created'), ('modifiedDate', 'Modified'), ('deletedDate', 'Deleted')))


@artifact_processor
def ppv_ecd_media(context):
    return _records(context, 'ecdPersistentMediaItem', (
        ('syncId', 'Media ID'), ('albumSyncId', 'Album ID'), ('fileType', 'File Type (as stored)'),
        ('largeFileExt', 'File Extension'), ('l_viewCount', 'View Count'),
        ('imageWidth', 'Width'), ('imageHeight', 'Height'), ('totalEncryptedSize', 'Encrypted Size'),
        ('l_isDownloaded', 'Downloaded Flag (as stored)'), ('isDecoy', 'Decoy Flag (as stored)'),
        ('purged', 'Purged Flag (as stored)'), ('hasMediumFile', 'Has Medium File (as stored)'),
        ('sortPosition', 'Sort Position')),
        (('createdDate', 'Created'), ('modifiedDate', 'Modified'), ('favoriteDate', 'Favorited'),
         ('trashedDate', 'Trashed'), ('uploadedDate', 'Uploaded'), ('l_cloudDownloadDate', 'Cloud Downloaded')))


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
                    if stamp == '' and time_raw not in (None, 0):
                        logfunc(f'Private Photo Vault diagnostics: invalid time; raw retained; file={context.get_relative_path(path)}; line={line_number}')
                    rows.append((stamp, text, line_number, _report_scalar(time_raw), raw, status,
                                 context.get_relative_path(path)))
        except OSError:
            logfunc(f'Private Photo Vault diagnostics: could not read file={context.get_relative_path(path)}')
    return (('Log Time', 'datetime'), 'Message', 'Line Number', 'Raw Time (Unix milliseconds)',
            'Message Hex', 'Decode Status', 'Source File'), rows, source
