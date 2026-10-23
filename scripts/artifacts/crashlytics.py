__artifacts_v2__ = {
    'crashlytics_logs': {
        'name': 'Crashlytics - Analytics Events',
        'description': 'Timestamped analytics events, including screen views, from iOS Crashlytics log records.',
        'author': '@CyberMike81, OpenAI Codex',
        'creation_date': '2026-10-23',
        'last_update_date': '2026-10-23',
        'requirements': 'none',
        'category': 'Crashlytics',
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'file-text',
        'paths': ('*/Caches/com.crashlytics.data/*/*/log_*.clsrecord',),
        'notes': 'Log Time is log.time (Unix milliseconds); zero dates are blank. Bundle ID '
                 'is the Crashlytics app-directory name. Only analytics events (log.msg '
                 'hex that decodes to text starting with $A$:) are reported; other app log '
                 'text is not. Event reads name from the $A$: JSON. For screen_view/_vs '
                 'events, Screen Name reads _sn/firebase_screen/screen_name; Screen Class '
                 'reads _sc/firebase_screen_class/screen_class. Message keeps the event JSON '
                 'with its parameters; Breadcrumb Status flags malformed analytics data. '
                 'Events do not identify an operator.',
        'sample_data': {
            'otto_ios17': 'iOS 17.5.1 | 9 apps | 230 rows',
            'iphone11_ios17': 'iOS 17.3 | 11 apps | 399 rows',
            'iphone12_ios18': 'iOS 18.7 | 8 apps | 148 rows',
            'falken_ios26': 'iOS 26.2.1 | 2 apps | 283 rows',
        },
    },
}

import json
import math
import os
import re
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, logfunc


def _bundle_id(path):
    match = re.search(r'(?:^|/)Caches/com\.crashlytics\.data/([^/]+)/.+/log_[^/]+\.clsrecord$',
                      str(path).replace('\\', '/'))
    return match.group(1) if match else ''


def _time(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value == 0:
        return ''
    try:
        if isinstance(value, float) and not math.isfinite(value):
            return ''
        return datetime.fromtimestamp(value / 1000, timezone.utc)
    except (ValueError, OverflowError, OSError):
        return ''


def _raw_time(value):
    # Preserve exact huge values through SQLite's binder without changing numeric zero.
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, int) and not -(2**63) <= value < 2**63:
        return str(value)
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return value


def _first_string(parameters, *keys):
    return next((parameters[key] for key in keys
                 if isinstance(parameters.get(key), str) and parameters[key]), '')


def _breadcrumb(text):
    # Firebase serializes {name, parameters} after the $A$: prefix; the caller passes only those.
    # https://github.com/firebase/firebase-ios-sdk/blob/13.1.1/Crashlytics/Crashlytics/Controllers/FIRCLSAnalyticsManager.m#L23
    try:
        event = json.loads(text[4:])
    except (ValueError, RecursionError):
        return '', '', '', 'Malformed analytics JSON'
    if not isinstance(event, dict) or not isinstance(event.get('name'), str):
        return '', '', '', 'Unsupported analytics shape'
    name = event['name']
    parameters = event.get('parameters', {})
    if not isinstance(parameters, dict):
        return name, '', '', 'Unsupported analytics parameters'
    screen = screen_class = ''
    if name in ('screen_view', '_vs'):
        # Compact SDK keys also occur in extracted logs; preserve the event name as stored.
        # SDK debug mapping: https://github.com/firebase/firebase-ios-sdk/issues/13002
        # Never substitute a screen class for a screen name.
        # https://firebase.google.com/docs/analytics/screenviews
        screen = _first_string(parameters, '_sn', 'firebase_screen', 'screen_name')
        screen_class = _first_string(parameters, '_sc', 'firebase_screen_class', 'screen_class')
    return name, screen, screen_class, 'Parsed analytics event'


@artifact_processor
def crashlytics_logs(context):
    rows = []
    source = ''
    for path in sorted({str(p) for p in context.get_files_found()}):
        bundle = _bundle_id(path)
        if not bundle or not os.path.isfile(path):
            continue
        display_path = context.get_relative_path(path)
        undecoded = 0
        try:
            with open(path, 'rb') as handle:
                for line_number, line in enumerate(handle, 1):
                    location = f'file={display_path}; line={line_number}'
                    try:
                        obj = json.loads(line)
                    except (ValueError, UnicodeError, RecursionError):
                        logfunc(f'Crashlytics: skipped malformed JSON; {location}')
                        continue
                    entry = obj.get('log') if isinstance(obj, dict) else None
                    if not isinstance(entry, dict):
                        logfunc(f'Crashlytics: unsupported log shape; {location}')
                        continue
                    raw = entry.get('msg')
                    if not isinstance(raw, str):
                        logfunc(f'Crashlytics: non-string msg; {location}')
                        continue
                    try:
                        text = bytes.fromhex(raw).decode('utf-8')
                    except (ValueError, UnicodeError):
                        undecoded += 1
                        continue
                    if not text.startswith('$A$:'):
                        continue
                    name, screen, screen_class, breadcrumb_status = _breadcrumb(text)
                    time_raw = entry.get('time')
                    stamp = _time(time_raw)
                    if stamp == '' and time_raw not in (None, 0):
                        logfunc(f'Crashlytics: invalid time; raw retained; {location}')
                    source = source or path
                    rows.append((stamp, bundle, name, screen, screen_class, text, line_number,
                                 _raw_time(time_raw), breadcrumb_status, display_path))
        except OSError:
            logfunc(f'Crashlytics: could not read file={display_path}')
        if undecoded:
            logfunc(f'Crashlytics: skipped {undecoded} message(s) that are not hex UTF-8; file={display_path}')
    return (('Log Time', 'datetime'), 'Bundle ID', 'Event', 'Screen Name', 'Screen Class',
            'Message', 'Line Number', 'Raw Time (Unix milliseconds)', 'Breadcrumb Status',
            'Source File'), rows, source
