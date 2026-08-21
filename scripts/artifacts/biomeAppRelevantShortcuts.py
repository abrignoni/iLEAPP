__artifacts_v2__ = {
    "get_biomeAppRelevantShortcuts": {
        "name": "Biome - App Relevant Shortcuts",
        "description": "Parses relevant shortcuts donated by apps from the "
                       "App.RelevantShortcuts biome stream: the donating app, the widget the "
                       "shortcut was offered for, and the relevance window the app suggested "
                       "the shortcut should appear in.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "Each record embeds an NSKeyedArchiver plist holding the shortcut. The widget "
                 "kind, shortcut role and the relevance provider date window are surfaced; the "
                 "nested intent payload inside the shortcut is not currently unpacked.",
        "paths": ('*/streams/*/App.RelevantShortcuts/local/*',),
        "output_types": "standard",
        "artifact_icon": "zap",
        "sample_data": {
            "hc_ios26": "26.5.2 | 23 rows",
        },
    }
}


import os
import struct
from datetime import datetime as _dt
from datetime import timezone

from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import (artifact_processor, convert_time_obj_to_utc, get_plist_content,
                               logfunc)

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)


def _to_str(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', 'replace')
    if value is None or isinstance(value, (dict, list)):
        return ''
    return str(value)


def _safe_time_obj(value):
    return convert_time_obj_to_utc(value) if isinstance(value, _dt) else None


def _relevance_window(plist):
    """Relevance providers carry the window the app wanted the shortcut shown in."""
    providers = plist.get('relevanceProviders')
    if isinstance(providers, dict):
        providers = [providers]
    if not isinstance(providers, list):
        return None, None
    for provider in providers:
        if isinstance(provider, dict) and ('startDate' in provider or 'endDate' in provider):
            return _safe_time_obj(provider.get('startDate')), _safe_time_obj(provider.get('endDate'))
    return None, None


def _shortcut_detail(plist):
    shortcut = plist.get('shortcut')
    if not isinstance(shortcut, dict):
        return '', ''
    title = shortcut.get('activitySubtitle') or shortcut.get('activityBundleIdentifier') or ''
    intent = shortcut.get('intent')
    intent_name = ''
    if isinstance(intent, dict):
        intent_name = _to_str(intent.get('intentClassName') or intent.get('donationMetadata') or '')
    return _to_str(title), intent_name


@artifact_processor
def get_biomeAppRelevantShortcuts(context):

    data_list = []
    source_dirs = set()
    for file_found in sorted(context.get_files_found()):
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
            ts = record.timestamp1.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data)
                    plist = get_plist_content(protostuff.get('3'))
                except _DECODE_ERRORS as ex:
                    logfunc(f'App Relevant Shortcuts: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                if not isinstance(plist, dict):
                    plist = {}
                start, end = _relevance_window(plist)
                title, intent_name = _shortcut_detail(plist)

                data_list.append((ts, start, end, record.state.name,
                                  _to_str(protostuff.get('1')),
                                  _to_str(plist.get('widgetKind', '')),
                                  plist.get('shortcutRole', ''), title, intent_name,
                                  _to_str(plist.get('watchTemplate', '')), filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, None, record.state.name, None, None, None, None,
                                  None, None, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Relevance Start', 'datetime'),
                    ('Relevance End', 'datetime'), 'SEGB State', 'Bundle ID', 'Widget Kind',
                    'Shortcut Role (raw)', 'Shortcut Title', 'Intent', 'Watch Template',
                    'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
