__artifacts_v2__ = {
    'life360CrashDetection': {
        'name': 'Life360 - Crash Detection Diagnostics',
        'description': 'Crash and collision detections, detector intervals, collision data-exchange metadata and '
                       'accelerometer-anomaly diagnostics from the Life360 internal logs.',
        'author': '@CyberMike81, OpenAI Codex',
        'creation_date': '2026-10-21',
        'last_update_date': '2026-10-22',
        'requirements': 'none',
        'category': 'Life360',
        'notes': 'Reads com.life360.safetymap*.log files, including those in the shared app group; other files '
                 'the wildcard matches, such as Crashlytics sdk.log, are skipped and logged. One row per crash, '
                 'collision, detector or accelerometer-anomaly record from the DriverBehavior component, plus '
                 'Metrics accelerometer-anomaly-detected records, including continuation lines; Raw Log Record '
                 'keeps the record text and Source Line and Source Line End give its lines in the file. Logged '
                 'Time is the line prefix, Event Time the Timestamp of a Crash detected record, and Detector '
                 'Start and Detector End the startTimestamp and endTimestamp of a DvBArity record; each uses its '
                 'own logged UTC offset and renders in UTC. Record Kind is the parser label for the message. '
                 'Values are as logged. Inspection by the contributor of the SDK 3.11.16 collision producer '
                 'found Speed logged in metres per second; this was not re-verified here, and units for other '
                 'versions are not established. Confidence is not a percentage or probability. Payload Size is '
                 'the logged size, not recovered sensor data. Records are not joined to each other. A row does '
                 'not establish that a physical crash happened, and no row does not establish that none did. '
                 'Tested on Life360 26.31.5.2066 (iOS 18.6, SDK 3.11.16), which logs "| [DriverBehavior | ...] '
                 '-". The Life360 23.x and 24.x logs on abe_ios16, felix_ios17, fsfull002_ios17 and '
                 'iphone11_ios17 write "| DriverBehavior | ...|" without brackets, which is not parsed; those '
                 'logs held no crash or collision records.',
        'paths': ('*/com.life360.safetymap*.log',),
        'output_types': 'all',
        'artifact_icon': 'alert-triangle',
        'sample_data': {
            'abe_ios16': 'iOS 16.5 | Life360 23.19.0 | 0 rows',
            'felix_ios17': 'iOS 17.6.1 | Life360 24.34.0 | 0 rows',
            'fsfull002_ios17': 'iOS 17.1 | Life360 23.43.1 | 0 rows',
            'iphone11_ios17': 'iOS 17.3 | Life360 24.28.0 | 0 rows',
        },
    },
}

import os
import re
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.life360_common import columns_first

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
    match = re.match(_STAMP + r'(?=\s|\||$)', message[label.end():])
    return _time(match.group() if match else '', field, where)


def _token(message, field, where):
    label = re.search(r'\b' + re.escape(field) + r':\s*', message)
    if label is None:
        return ''
    remainder = message[label.end():]
    match = re.match(r'([^\s|]+)', remainder)
    value = match.group(1) if match else ''
    if (not value or value.endswith(':') or
            re.match(r'(?:Event Type|Data exchange type|payload size)\s*:', remainder)):
        logfunc(f'Life360 {field} was empty at {where}; value left blank and raw record retained')
        return ''
    return value


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
                yield start, end, ''.join(lines).removesuffix('\n').removesuffix('\r')
                start, lines = number, []
            lines.append(text)
            end = number
        if lines:
            yield start, end, ''.join(lines).removesuffix('\n').removesuffix('\r')


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
        trip, event_id = _token(message, 'TripID', where), _token(message, 'EventID', where)
        event_type = _token(message, 'Event Type', where)
        latitude, longitude = _coordinates(message, 'Location', True, where)
        accuracy, speed = _token(message, 'Accuracy', where), _token(message, 'Speed', where)
    elif kind == 'Detector details':
        missing = [field for field in ('Confidence', 'startTimestamp', 'endTimestamp', 'location')
                   if not re.search(r'\b' + field + r':', message)]
        if missing:
            logfunc(f'Life360 detector detail fields absent at {where}: {", ".join(missing)}; '
                    'available fields and raw record retained')
        begin, finish = (_field_time(message, field, where) for field in ('startTimestamp', 'endTimestamp'))
        confidence = _token(message, 'Confidence', where)
        latitude, longitude = _coordinates(message, 'location', False, where)
    elif kind == 'Collision data exchange':
        exchange = _token(message, 'Data exchange type', where)
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
        basename = os.path.basename(candidate)
        if (not basename.startswith('com.life360.safetymap') or not basename.lower().endswith('.log') or
                os.path.isdir(candidate)):
            logfunc(f'Life360 skipped matching diagnostic path {context.get_relative_path(candidate)!r}: '
                    'basename is not a com.life360.safetymap*.log application file')
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
    headers, rows = columns_first(headers, rows, ('Logged Time', 'Event Time', 'Detector Start', 'Detector End',
                                                  'Trip ID', 'Event ID'))
    return headers, rows, '\n'.join(sources)
