__artifacts_v2__ = {
    'life360CrashDetection': {
        'name': 'Life360 - Crash Detection Diagnostics',
        'description': 'Crash/collision detections, detector intervals, collision data-exchange metadata and '
                       'accelerometer-anomaly diagnostics Life360 wrote to its internal logs. '
                       'Speed is as stored: metres per second for the examined SDK 3.11.16 collision '
                       'producer; other versions are unverified.',
        'author': '@CyberMike81, OpenAI Codex',
        'creation_date': '2026-10-21',
        'last_update_date': '2026-10-21',
        'requirements': 'none',
        'category': 'Life360',
        'notes': 'Reads com.life360.safetymap*.log files, including logs in a shared app-group container. '
                 'The application-specific filename and the logged component/message select records; no '
                 'container marker is required. One row represents one diagnostic log record, including '
                 'its continuation lines. Repeated records, copies in separate files and separate '
                 'containers remain separate observations. Duplicate file-list entries and physical '
                 'symlink aliases are read once. Source Line and Source Line End are one-based physical '
                 'line numbers. Raw Log Record retains the decoded record, including unreported fields '
                 'and embedded newlines, with only its final line terminator removed. Invalid UTF-8 is '
                 'replaced for display and logged; the preserved source file remains authoritative. '
                 'Logged Time comes from the record prefix, Event Time from Timestamp in a Crash detected '
                 'entry, and Detector Start/End from startTimestamp/endTimestamp in a DvBArity confidence '
                 'entry. Each uses its own explicit numeric UTC offset and renders in UTC, preserving '
                 'subseconds up to microsecond precision. No time zone is taken from the filename or '
                 'the examiner computer. Missing times remain blank; invalid times or offsets are '
                 'logged and left blank with the raw record retained. '
                 'Record Kind is a parser classification of the message: Crash detected, High confidence '
                 'collision detected, Collision detected, Detector details, Collision data exchange, '
                 'Accelerometer anomaly warning/diagnostic, or Other crash/collision diagnostic. The '
                 'component text, event type, IDs and numeric field text are reported as stored. '
                 'Detector details and SDK warnings are not joined to another event by proximity; no '
                 'confidence, identifier, coordinate or capability state is carried to another row. '
                 'Confidence is not converted to a percentage or interpreted as a probability. '
                 'Payload Size is the logged size text, not recovered collision/sensor data. '
                 'Speed and Accuracy retain their logged numeric text without conversion. Inspection of '
                 'the recovered collision producer with CoreEngine SDK 3.11.16 found sampleSpeed read '
                 'with milesPerHour and converted to metersPerSecond before the logged event field. '
                 'Thus the examined collision Speed field is already metres per second; the parser '
                 'does not convert it again. Units for other producer versions and other speed or '
                 'accuracy fields are not established by that inspection. Coordinates identify the '
                 'values recorded in the diagnostic, not an '
                 'independently established location fix or who carried the device. '
                 'The warnings remain alongside later detection messages; this artifact does not decide '
                 'whether the detector was effective, what triggered it, or whether a physical crash '
                 'occurred. Missing records do not establish that no event occurred. Layout coverage '
                 'includes the diagnostic format recorded by Life360 26.31.5.2066 on iOS 18.6 with '
                 'SDK 3.11.16 and fabricated fixtures; other layouts '
                 'and producer versions may differ. Unrecognised crash/collision messages from '
                 'DriverBehavior retain their raw record with a log entry. Unreadable files are logged '
                 'and other files continue. Partial detector-detail records retain their available '
                 'fields and raw text, with missing expected labels logged. Other DriverBehavior '
                 'telemetry, saved sensor files, upload '
                 'queues, Cache.db API responses, and historical main-database/WAL recovery are outside '
                 'this artifact. The database Driving Incidents and Driver Reports artifacts read '
                 'different sources and are not treated as equivalent observations.',
        'paths': ('*/com.life360.safetymap*.log',),
        'output_types': 'all',
        'artifact_icon': 'alert-triangle',
        'sample_data': {
            'private_driverbehavior_ios18_6': 'iOS 18.6 | Life360 26.31.5.2066 | SDK 3.11.16 | '
                                             '7 rows from 36 diagnostic logs; private source',
            'private_ios18_6': 'iOS 18.6 | Life360 26.34.0.5 | 0 rows '
                              '(no com.life360.safetymap*.log files in the tested container)',
            'synthetic_driverbehavior': 'Fabricated diagnostic logs | 9 rows | main and sidecar layouts; '
                                       'sidecar diagnostics and malformed variants are synthetic controls',
        },
    },
}

import os
import re
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, logfunc

_START = re.compile(r'^\ufeff?\d{4}-\d{2}-\d{2}[T ]')
_STAMP = (r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?'
          r'\s*(?:Z|[+-]\d{2}:?\d{2})')
_PREFIX_TIME = re.compile(r'^\ufeff?(' + _STAMP + r')(?=\s)')
_COMPONENT = re.compile(r'\|\s*\[(?P<component>[^\]\r\n]+)\]\s*-?\s*'
                        r'(?P<message>.*)', re.DOTALL)
_NUMBER = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'
_KINDS = (
    ('Crash detected', re.compile(r'^Crash detected\s*:')),
    ('High confidence collision detected', re.compile(r'^High confidence collision detected\b')),
    ('Collision detected', re.compile(r'^Collision detected\b')),
    ('Collision data exchange', re.compile(r'^Data exchange type:\s*collision\b')),
)


def _kind(component, message):
    if component == 'Metrics' and message.strip() == 'accelerometer-anomaly-detected':
        return 'Accelerometer anomaly diagnostic'
    if component.split('|', 1)[0].strip() != 'DriverBehavior':
        return ''
    if 'Accelerometer anomaly detected' in message:
        return 'Accelerometer anomaly warning'
    for label, pattern in _KINDS:
        if pattern.search(message):
            return label
    if 'DvBArity' in component and any(re.search(r'\b' + field + r':', message) for field in
                                      ('Confidence', 'startTimestamp', 'endTimestamp')):
        return 'Detector details'
    if re.search(r'\b(?:crash|collision)\b', message, re.IGNORECASE):
        return 'Other crash/collision diagnostic'
    return ''


def _time(value, label, where):
    match = re.fullmatch(r'(\d{4}-\d{2}-\d{2})[T ]'
                         r'(\d{2}:\d{2}:\d{2}(?:\.\d+)?)\s*(Z|[+-]\d{2}:?\d{2})', value)
    if match:
        day, clock, zone = match.groups()
        zone = '+0000' if zone == 'Z' else zone
        form = '%Y-%m-%d %H:%M:%S.%f %z' if '.' in clock else '%Y-%m-%d %H:%M:%S %z'
        try:
            return datetime.strptime(f'{day} {clock} {zone}', form).astimezone(timezone.utc)
        except (ValueError, OverflowError):
            pass
    logfunc(f'Life360 {label} could not be converted at {where}; raw record retained')
    return ''


def _field_time(message, field, where):
    label = re.search(r'\b' + re.escape(field) + r':\s*', message)
    if label is None:
        return ''
    match = re.match(_STAMP, message[label.end():])
    return _time(match.group() if match else '', field, where)


def _token(message, field):
    match = re.search(r'\b' + re.escape(field) + r':\s*([^\s|]+)', message)
    return match.group(1) if match else ''


def _coordinates(message, field, bracketed, where):
    label = re.search(r'\b' + re.escape(field) + r':\s*', message)
    if label is None:
        return '', ''
    pattern = (r'<\s*(' + _NUMBER + r')\s*,\s*(' + _NUMBER + r')\s*>' if bracketed else
               r'(' + _NUMBER + r')\s*,\s*(' + _NUMBER + r')(?=\s*(?:\||$))')
    match = re.match(pattern, message[label.end():])
    if match:
        return match.groups()
    logfunc(f'Life360 diagnostic location could not be decoded at {where}; raw record retained')
    return '', ''


def _records(path, relative):
    start, end, lines = 1, 0, []
    with open(path, 'rb') as source:
        for number, raw in enumerate(source, 1):
            try:
                text = raw.decode('utf-8')
            except UnicodeDecodeError:
                text = raw.decode('utf-8', errors='replace')
                logfunc(f'Life360 log UTF-8 decode failed in {relative!r}, line {number}; '
                        'replacement characters used for display')
            if _START.match(text) and lines:
                yield start, end, ''.join(lines).rstrip('\r\n')
                start, lines = number, []
            lines.append(text)
            end = number
        if lines:
            yield start, end, ''.join(lines).rstrip('\r\n')


def _row(raw, start, end, relative):
    part = _COMPONENT.search(raw)
    if part is None:
        return None
    component, message = part.group('component').strip(), part.group('message')
    kind = _kind(component, message)
    if not kind:
        return None
    where = f'{relative!r}, line {start}'
    stamp = _PREFIX_TIME.match(raw)
    logged = _time(stamp.group(1) if stamp else '', 'log timestamp', where)
    event = begin = finish = ''
    trip = event_id = event_type = latitude = longitude = accuracy = speed = confidence = ''
    exchange = size = ''
    if kind == 'Crash detected':
        event = _field_time(message, 'Timestamp', where)
        trip, event_id = _token(message, 'TripID'), _token(message, 'EventID')
        event_type = _token(message, 'Event Type')
        latitude, longitude = _coordinates(message, 'Location', True, where)
        accuracy, speed = _token(message, 'Accuracy'), _token(message, 'Speed')
    elif kind == 'Detector details':
        missing = [field for field in ('Confidence', 'startTimestamp', 'endTimestamp', 'location')
                   if not re.search(r'\b' + field + r':', message)]
        if missing:
            logfunc(f'Life360 detector detail fields absent at {where}: {", ".join(missing)}; '
                    'available fields and raw record retained')
        begin, finish = (_field_time(message, field, where) for field in ('startTimestamp', 'endTimestamp'))
        confidence = _token(message, 'Confidence')
        latitude, longitude = _coordinates(message, 'location', False, where)
    elif kind == 'Collision data exchange':
        exchange = _token(message, 'Data exchange type')
        match = re.search(r'\bpayload size:\s*(.*)$', message)
        size = match.group(1).strip() if match else ''
    elif kind == 'Other crash/collision diagnostic':
        logfunc(f'Life360 unrecognised DriverBehavior collision diagnostic at {where}; raw record retained')
    return (logged, event, begin, finish, kind, component, trip, event_id, event_type,
            latitude, longitude, accuracy, speed, confidence, exchange, size, start, end, relative, raw)


@artifact_processor
def life360CrashDetection(context):
    headers = (('Logged Time', 'datetime'), ('Event Time', 'datetime'), ('Detector Start', 'datetime'),
               ('Detector End', 'datetime'), 'Record Kind', 'Component (as stored)', 'Trip ID', 'Event ID',
               'Event Type (as stored)', 'Latitude', 'Longitude', 'Accuracy (as stored)',
               'Speed (as stored)', 'Confidence (as stored)', 'Data Exchange Type (as stored)',
               'Payload Size (as stored)', 'Source Line', 'Source Line End', 'Source File', 'Raw Log Record')
    paths = {}
    for candidate in sorted({str(path) for path in context.get_files_found()},
                            key=context.get_relative_path):
        if not candidate.lower().endswith('.log') or os.path.isdir(candidate):
            continue
        physical = os.path.normcase(os.path.realpath(candidate))
        paths.setdefault(physical, candidate)
    rows, sources = [], []
    for path in paths.values():
        relative = context.get_relative_path(path)
        sources.append(relative)
        try:
            for start, end, raw in _records(path, relative):
                row = _row(raw, start, end, relative)
                if row is not None:
                    rows.append(row)
        except OSError as error:
            logfunc(f'Life360 diagnostic log read failed in {relative!r} ({type(error).__name__}); '
                    'earlier rows retained and other files continue')
    return headers, rows, '\n'.join(sources)
