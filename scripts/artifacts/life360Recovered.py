__artifacts_v2__ = {'life360RecoveredTopics': {'name': 'Life360 - Recovered Topic Records',
                            'description': 'Non-live topic records read from main-file and earlier committed '
                                           'WAL page images.',
                            'author': '@CyberMike81, OpenAI Codex',
                            'creation_date': '2026-10-22',
                            'last_update_date': '2026-10-22',
                            'requirements': 'none',
                            'category': 'Life360',
                            'notes': 'Logged Time is ZTIMESTAMP (Unix seconds). Payload retains the stored '
                                     'ZDATA text; invalid UTF-8 is shown as hex with a diagnostic. Covers '
                                     'the same eleven topic families as the current awareness parsers; other '
                                     'topics are excluded. Exact current record contents are excluded, '
                                     'ignoring Core Data bookkeeping columns. Identical recovered content is '
                                     'grouped per database, retaining all page/cell/frame appearances. '
                                     'Source States distinguish the main-file view without WAL from '
                                     'checksum-valid page versions ending in a committed WAL transaction. '
                                     'Main-file pages may reflect checkpoint state; these are recovered '
                                     'records, not a guaranteed consistent historical database snapshot. WAL '
                                     'overflow uses only available preceding WAL page versions, never '
                                     'main-file bytes. Freeblocks, freelists, old-salt frames, incomplete '
                                     'transactions and unsupported/incomplete cells are not carved; failures '
                                     'and exclusions are logged. Overwriting or absence from the live view '
                                     'does not establish user deletion. Times render in UTC. Tested on '
                                     'Life360 26.34.0.5 / iOS 18.6; other schemas may differ. Payload Format '
                                     'held one value, JSON object, in both tested inputs. Source File and '
                                     'Store identify one database per store in the single-container tests; '
                                     'Source File is retained to distinguish containers/copies. Complete '
                                     'payloads above 32 MiB are excluded with a diagnostic.',
                            'paths': ('*/Library/Application Support/com.eventkit/*/*.sqlite*',
                                      '*/Library/Application Support/DriveModelStore.sqlite*',
                                      '*/.com.apple.mobile_container_manager.metadata.plist'),
                            'output_types': 'standard',
                            'artifact_icon': 'database'},
 'life360RecoveredLocations': {'name': 'Life360 - Recovered Location Samples',
                               'description': 'Location objects within non-live device-location and '
                                              'failed-location topic records.',
                               'author': '@CyberMike81, OpenAI Codex',
                               'creation_date': '2026-10-22',
                               'last_update_date': '2026-10-22',
                               'requirements': 'none',
                               'category': 'Life360',
                               'notes': 'Location Time is the location timestamp (Cocoa seconds); Logged '
                                        'Time is the parent ZTIMESTAMP (Unix seconds). Buffered samples are '
                                        'used when present, otherwise the headline location. Values and '
                                        'units are as stored. A point can also occur in a different live '
                                        'parent record. Exact current record contents are excluded, ignoring '
                                        'Core Data bookkeeping columns. Identical recovered content is '
                                        'grouped per database, retaining all page/cell/frame appearances. '
                                        'Source States distinguish the main-file view without WAL from '
                                        'checksum-valid page versions ending in a committed WAL transaction. '
                                        'Main-file pages may reflect checkpoint state; these are recovered '
                                        'records, not a guaranteed consistent historical database snapshot. '
                                        'WAL overflow uses only available preceding WAL page versions, never '
                                        'main-file bytes. Freeblocks, freelists, old-salt frames, incomplete '
                                        'transactions and unsupported/incomplete cells are not carved; '
                                        'failures and exclusions are logged. Overwriting or absence from the '
                                        'live view does not establish user deletion. Times render in UTC. '
                                        'Tested on Life360 26.34.0.5 / iOS 18.6; other schemas may differ. '
                                        'Store and Sample Index were uniform in the tested extraction '
                                        'because every recovered location came from a single headline '
                                        'location in FailedLocationTopic.',
                               'paths': ('*/Library/Application Support/com.eventkit/*/*.sqlite*',
                                         '*/Library/Application Support/DriveModelStore.sqlite*',
                                         '*/.com.apple.mobile_container_manager.metadata.plist'),
                               'output_types': 'all',
                               'artifact_icon': 'map-pin'},
 'life360RecoveredMovement': {'name': 'Life360 - Recovered Movement Events',
                              'description': 'Drive, trip and cancellation objects within non-live Life360 '
                                             'topic records.',
                              'author': '@CyberMike81, OpenAI Codex',
                              'creation_date': '2026-10-22',
                              'last_update_date': '2026-10-22',
                              'requirements': 'none',
                              'category': 'Life360',
                              'notes': 'Drive/trip Event Time, Start Time and End Time are Cocoa seconds; '
                                       'cancellation Event Time and parent Logged Time are Unix seconds. '
                                       'Event labels and numeric fields are as stored. No sensor payload or '
                                       'physical crash conclusion is inferred. Exact current record contents '
                                       'are excluded, ignoring Core Data bookkeeping columns. Identical '
                                       'recovered content is grouped per database, retaining all '
                                       'page/cell/frame appearances. Source States distinguish the main-file '
                                       'view without WAL from checksum-valid page versions ending in a '
                                       'committed WAL transaction. Main-file pages may reflect checkpoint '
                                       'state; these are recovered records, not a guaranteed consistent '
                                       'historical database snapshot. WAL overflow uses only available '
                                       'preceding WAL page versions, never main-file bytes. Freeblocks, '
                                       'freelists, old-salt frames, incomplete transactions and '
                                       'unsupported/incomplete cells are not carved; failures and exclusions '
                                       'are logged. Overwriting or absence from the live view does not '
                                       'establish user deletion. Times render in UTC. Tested on Life360 '
                                       '26.34.0.5 / iOS 18.6; other schemas may differ. End Time is empty in '
                                       'the synthetic drive-only case. Source File identifies the '
                                       'originating database even when recovery provenance also identifies '
                                       'that file.',
                              'paths': ('*/Library/Application Support/com.eventkit/*/*.sqlite*',
                                        '*/Library/Application Support/DriveModelStore.sqlite*',
                                        '*/.com.apple.mobile_container_manager.metadata.plist'),
                              'output_types': 'all',
                              'artifact_icon': 'route'},
 'life360RecoveredWaypoints': {'name': 'Life360 - Recovered Movement Waypoints',
                               'description': 'Distinct waypoint and route objects within non-live Life360 '
                                              'movement records.',
                               'author': '@CyberMike81, OpenAI Codex',
                               'creation_date': '2026-10-22',
                               'last_update_date': '2026-10-22',
                               'requirements': 'none',
                               'category': 'Life360',
                               'notes': 'Waypoint Time is Unix seconds for drive waypoints and Cocoa seconds '
                                        'for trip route points. Complete objects are grouped within a '
                                        'container and trip/session; conflicting payloads stay separate. '
                                        'Parent references retain enclosing records and recovery provenance. '
                                        'A point can also occur in another live parent record. Exact current '
                                        'record contents are excluded, ignoring Core Data bookkeeping '
                                        'columns. Identical recovered content is grouped per database, '
                                        'retaining all page/cell/frame appearances. Source States '
                                        'distinguish the main-file view without WAL from checksum-valid page '
                                        'versions ending in a committed WAL transaction. Main-file pages may '
                                        'reflect checkpoint state; these are recovered records, not a '
                                        'guaranteed consistent historical database snapshot. WAL overflow '
                                        'uses only available preceding WAL page versions, never main-file '
                                        'bytes. Freeblocks, freelists, old-salt frames, incomplete '
                                        'transactions and unsupported/incomplete cells are not carved; '
                                        'failures and exclusions are logged. Overwriting or absence from the '
                                        'live view does not establish user deletion. Times render in UTC. '
                                        'Tested on Life360 26.34.0.5 / iOS 18.6; other schemas may differ.',
                               'paths': ('*/Library/Application Support/com.eventkit/*/*.sqlite*',
                                         '*/Library/Application Support/DriveModelStore.sqlite*',
                                         '*/.com.apple.mobile_container_manager.metadata.plist'),
                               'output_types': 'all',
                               'artifact_icon': 'map-pin'},
 'life360RecoveredIncidents': {'name': 'Life360 - Recovered Driving Incidents',
                               'description': 'Driving-incident objects within non-live Life360 movement '
                                              'records.',
                               'author': '@CyberMike81, OpenAI Codex',
                               'creation_date': '2026-10-22',
                               'last_update_date': '2026-10-22',
                               'requirements': 'none',
                               'category': 'Life360',
                               'notes': 'Incident Time is the incident timestamp (Unix seconds). Complete '
                                        'objects are grouped within a container/trip; conflicting payloads '
                                        'stay separate. Labels are as stored. These are stored app incident '
                                        'objects, not independent evidence of a physical crash. An incident '
                                        'can also occur in another live parent record. Exact current record '
                                        'contents are excluded, ignoring Core Data bookkeeping columns. '
                                        'Identical recovered content is grouped per database, retaining all '
                                        'page/cell/frame appearances. Source States distinguish the '
                                        'main-file view without WAL from checksum-valid page versions ending '
                                        'in a committed WAL transaction. Main-file pages may reflect '
                                        'checkpoint state; these are recovered records, not a guaranteed '
                                        'consistent historical database snapshot. WAL overflow uses only '
                                        'available preceding WAL page versions, never main-file bytes. '
                                        'Freeblocks, freelists, old-salt frames, incomplete transactions and '
                                        'unsupported/incomplete cells are not carved; failures and '
                                        'exclusions are logged. Overwriting or absence from the live view '
                                        'does not establish user deletion. Times render in UTC. Tested on '
                                        'Life360 26.34.0.5 / iOS 18.6; other schemas may differ. Parent '
                                        'Records was uniform in the tested extraction; each grouped incident '
                                        'had one recovered parent record.',
                               'paths': ('*/Library/Application Support/com.eventkit/*/*.sqlite*',
                                         '*/Library/Application Support/DriveModelStore.sqlite*',
                                         '*/.com.apple.mobile_container_manager.metadata.plist'),
                               'output_types': 'all',
                               'artifact_icon': 'alert-triangle'},
 'life360RecoveredDrives': {'name': 'Life360 - Recovered Drives',
                            'description': 'Non-live ZDRIVEMODEL records from main-file and earlier '
                                           'committed WAL page images.',
                            'author': '@CyberMike81, OpenAI Codex',
                            'creation_date': '2026-10-22',
                            'last_update_date': '2026-10-22',
                            'requirements': 'none',
                            'category': 'Life360',
                            'notes': 'Start Time, End Time, Created At, Updated At and Last Retrieved are '
                                     'Cocoa seconds. Other numeric fields remain as stored; their units are '
                                     'not independently established. Circle associations are not joined from '
                                     'the current relationship table because that would mix source states. '
                                     'Exact current record contents are excluded, ignoring Core Data '
                                     'bookkeeping columns. Identical recovered content is grouped per '
                                     'database, retaining all page/cell/frame appearances. Source States '
                                     'distinguish the main-file view without WAL from checksum-valid page '
                                     'versions ending in a committed WAL transaction. Main-file pages may '
                                     'reflect checkpoint state; these are recovered records, not a '
                                     'guaranteed consistent historical database snapshot. WAL overflow uses '
                                     'only available preceding WAL page versions, never main-file bytes. '
                                     'Freeblocks, freelists, old-salt frames, incomplete transactions and '
                                     'unsupported/incomplete cells are not carved; failures and exclusions '
                                     'are logged. Overwriting or absence from the live view does not '
                                     'establish user deletion. Times render in UTC. Tested on Life360 '
                                     '26.34.0.5 / iOS 18.6; other schemas may differ. Score, Speeding Count, '
                                     'Drive Type, User Mode and User Tag were uniform in the tested '
                                     'extraction; Rideshare Vendor was empty in real and fabricated inputs. '
                                     'Created At and Updated At were identical in the tested extraction; '
                                     'both are retained as separately stored fields.',
                            'paths': ('*/Library/Application Support/com.eventkit/*/*.sqlite*',
                                      '*/Library/Application Support/DriveModelStore.sqlite*',
                                      '*/.com.apple.mobile_container_manager.metadata.plist'),
                            'output_types': 'standard',
                            'artifact_icon': 'car'},
 'life360RecoveredBreaches': {'name': 'Life360 - Recovered Geofence Breaches',
                              'description': 'Geofence breach objects within non-live Life360 topic records.',
                              'author': '@CyberMike81, OpenAI Codex',
                              'creation_date': '2026-10-22',
                              'last_update_date': '2026-10-22',
                              'requirements': 'none',
                              'category': 'Life360',
                              'notes': 'Event Time is the entry timestamp (Unix seconds); Location Time is '
                                       'the stored location timestamp (Cocoa seconds). Place, direction, '
                                       'distance and unit values are as stored. Raw parent JSON retains '
                                       'unknown fields; no place is supplied from another source. Only '
                                       'non-live parent records are selected, comparing their stored content '
                                       'with the current database/WAL view. Source States and Recovery '
                                       'Sources JSON distinguish main-file views from checksum-valid '
                                       'committed WAL page versions. These are recovered observations, not '
                                       'proof of deletion or a consistent historical snapshot. '
                                       'Unsupported/incomplete cells are logged; freeblocks, freelists, '
                                       'old-salt frames and incomplete transactions are excluded. Times '
                                       'render in UTC. Tested on Life360 26.34.0.5 / iOS 18.6; other layouts '
                                       'may differ. Unit and Algorithm were uniform and Event Time and '
                                       'Logged Time were identical in the tested extraction; the separate '
                                       'source fields are retained.',
                              'paths': ('*/Library/Application Support/com.eventkit/*/*.sqlite*',
                                        '*/.com.apple.mobile_container_manager.metadata.plist'),
                              'output_types': 'all',
                              'artifact_icon': 'map-pin'},
 'life360RecoveredDwells': {'name': 'Life360 - Recovered Dwell Events',
                            'description': 'Dwell objects within non-live Life360 topic and session records.',
                            'author': '@CyberMike81, OpenAI Codex',
                            'creation_date': '2026-10-22',
                            'last_update_date': '2026-10-22',
                            'requirements': 'none',
                            'category': 'Life360',
                            'notes': 'Event Time is dwell.timestamp (Cocoa seconds), Dwell Start and Dwell '
                                     'End are location.startTime/endTime (Unix seconds), and Logged Time is '
                                     'the parent ZTIMESTAMP (Unix seconds). Labels are as stored. Separate '
                                     'parent payloads are retained without filling fields from each other. '
                                     'Only non-live parent records are selected, comparing their stored '
                                     'content with the current database/WAL view. Source States and Recovery '
                                     'Sources JSON distinguish main-file views from checksum-valid committed '
                                     'WAL page versions. These are recovered observations, not proof of '
                                     'deletion or a consistent historical snapshot. Unsupported/incomplete '
                                     'cells are logged; freeblocks, freelists, old-salt frames and '
                                     'incomplete transactions are excluded. Times render in UTC. Tested on '
                                     'Life360 26.34.0.5 / iOS 18.6; other layouts may differ. Algorithm was '
                                     'uniform in the tested extraction. Session ID and User ID are empty in '
                                     'the fabricated engine-topic case. Source File and Store identify each '
                                     'database; the separate Source File preserves container/copy '
                                     'provenance.',
                            'paths': ('*/Library/Application Support/com.eventkit/*/*.sqlite*',
                                      '*/.com.apple.mobile_container_manager.metadata.plist'),
                            'output_types': 'all',
                            'artifact_icon': 'map-pin'}}
import json
import math
import os
from pathlib import Path
import uuid

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.life360_common import get_life360_files, seconds_to_utc
from scripts.life360_recovery import recover_rows

_TOPICS = {'DeviceLocationTopic', 'FailedLocationTopic', 'drive_session', 'trip_session',
           'DriveCancellationTopic', 'TripCancellationTopic', 'DriveEvent', 'DwellTopic',
           'dwell_session', 'BreachTopic', 'active_modality'}
_MOVEMENT = {'drive_session', 'trip_session', 'DriveEvent', 'DriveCancellationTopic', 'TripCancellationTopic'}


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _text(value):
    return '' if value is None else _json(value) if isinstance(value, (dict, list)) else value


def _object(value, label):
    if isinstance(value, dict):
        return value
    if value is not None:
        logfunc(f'Life360 recovered {label} was not an object; raw parent retained')
    return {}


def _array(value, label):
    if value is None:
        return []
    if not isinstance(value, list):
        logfunc(f'Life360 recovered {label} was not an array; raw parent retained')
        return []
    result = []
    for item in value:
        if isinstance(item, dict):
            result.append(item)
        else:
            logfunc(f'Life360 recovered {label} contained a non-object item; raw parent retained')
    return result


def _enum(value):
    if isinstance(value, dict) and len(value) == 1:
        return next(iter(value))
    return _text(value)


def _files(context, drives=False):
    result = []
    for name in get_life360_files(context):
        path = Path(name)
        if path.suffix != '.sqlite' or not path.is_file():
            continue
        topic = path.stem.rsplit('.', 1)[-1]
        is_drive = path.name == 'DriveModelStore.sqlite' and path.parent.name == 'Application Support'
        is_topic = (topic in _TOPICS and path.stem.startswith('com.life360.')
                    and path.parent.name == path.stem and path.parent.parent.name == 'com.eventkit')
        if (drives and is_drive) or (not drives and is_topic):
            result.append(name)
        elif not drives and path.name != 'DriveModelStore.sqlite':
            logfunc(f'Life360 recovery skipped {context.get_relative_path(name)!r}: topic outside supported recovery scope')
    return result


def _records(context, drives=False):
    for name in _files(context, drives):
        relative = context.get_relative_path(name)
        grouped = {}
        for record in recover_rows(name, 'ZDRIVEMODEL' if drives else 'ZENTRY', relative):
            entry = grouped.setdefault(record['fingerprint'], dict(record, appearances=[]))
            appearance = dict(record['source'], sourceFile=relative + ('-wal' if record['source']['frame'] else ''))
            entry['appearances'].append(appearance)
        for key, record in sorted(grouped.items()):
            record.update(path=name, file=relative, key=key,
                          wal=context.get_relative_path(name + '-wal') if Path(name + '-wal').exists() else '',
                          topic=Path(name).stem.rsplit('.', 1)[-1],
                          states='; '.join(sorted({v['state'] for v in record['appearances']})))
            yield record


def _documents(context):
    for record in _records(context):
        data = record['values'].get('ZDATA')
        try:
            raw = data.decode('utf-8') if isinstance(data, bytes) else data
            document = json.loads(raw)
            form = 'JSON object' if isinstance(document, dict) else 'JSON value'
            if not isinstance(document, dict):
                document = {}
                logfunc(f'Life360 recovered payload in {record["file"]!r} was not an object; raw value retained')
        except (ValueError, TypeError, UnicodeError, RecursionError):
            raw = data.hex() if isinstance(data, bytes) else _text(data)
            form = 'Hex bytes' if isinstance(data, bytes) else 'Stored text'
            document = {}
            logfunc(f'Life360 recovered payload decode failed in {record["file"]!r}; raw value retained')
        identity = record['values'].get('ZID')
        if isinstance(identity, bytes) and len(identity) == 16:
            identity = str(uuid.UUID(bytes=identity))
        elif isinstance(identity, bytes):
            identity = identity.hex()
        record.update(document=document, raw=raw, form=form, entry_id=_text(identity),
                      logged=seconds_to_utc(record['values'].get('ZTIMESTAMP'), 1970))
        yield record


def _provenance(record):
    return (record['states'], len(record['appearances']), record['key'], _json(record['appearances']),
            record['file'])


def _sources(context, drives=False):
    result = []
    for name in _files(context, drives):
        result.append(name)
        if Path(name + '-wal').exists():
            result.append(name + '-wal')
    return '\n'.join(result)


@artifact_processor
def life360RecoveredTopics(context):
    headers = (('Logged Time', 'datetime'), 'Entry ID', 'Store', 'Payload Format', 'Payload (as stored)',
               'Source States', 'Appearances', 'Record Fingerprint', 'Recovery Sources JSON', 'Source File')
    rows = [(r['logged'], r['entry_id'], r['topic'], r['form'], r['raw']) + _provenance(r)
            for r in _documents(context)]
    return headers, rows, _sources(context)


def _coordinate(value, limit):
    if value is None or value == '':
        return ''
    try:
        number = float(value)
        if isinstance(value, bool) or not math.isfinite(number) or abs(number) > limit:
            raise ValueError
        return value
    except (TypeError, ValueError, OverflowError):
        logfunc('Life360 coordinate was invalid; coordinate left blank and source JSON retained')
        return ''


def _coordinates(point):
    coordinate = point.get('coordinate') if 'coordinate' in point else point
    coordinate = _object(coordinate, 'coordinate')
    return _coordinate(coordinate.get('latitude'), 90), _coordinate(coordinate.get('longitude'), 180)


@artifact_processor
def life360RecoveredLocations(context):
    headers = (('Location Time', 'datetime'), ('Logged Time', 'datetime'), 'Entry ID', 'Store',
               'Latitude', 'Longitude', 'Altitude', 'Speed (as stored)', 'Course (as stored)',
               'Horizontal Accuracy (as stored)', 'Vertical Accuracy (as stored)', 'Sample Index',
               'Location JSON', 'Source States', 'Appearances', 'Record Fingerprint', 'Recovery Sources JSON',
               'Source File')
    rows = []
    for record in _documents(context):
        if record['topic'] not in ('DeviceLocationTopic', 'FailedLocationTopic'):
            continue
        doc = record['document']
        samples = _array(doc.get('bufferedSamples'), 'bufferedSamples')
        if not samples:
            location = doc.get('location')
            samples = [location] if isinstance(location, dict) else []
        if not samples:
            logfunc(f'Life360 recovered location entry in {record["file"]!r} has no supported location object')
        for index, point in enumerate(samples):
            rows.append((seconds_to_utc(point.get('timestamp'), 2001), record['logged'], record['entry_id'],
                         record['topic']) + _coordinates(point) +
                        tuple(_text(point.get(k)) for k in ('altitude', 'speed', 'course', 'horizontalAccuracy', 'verticalAccuracy')) +
                        (index, _json(point)) + _provenance(record))
    return headers, rows, _sources(context)


@artifact_processor
def life360RecoveredMovement(context):
    headers = (('Event Time', 'datetime'), ('Start Time', 'datetime'), ('End Time', 'datetime'),
               ('Logged Time', 'datetime'), 'Entry ID', 'Event ID', 'Trip ID', 'Session ID', 'User ID',
               'Kind', 'Event Type (as stored)', 'Distance (as stored)', 'Latitude', 'Longitude', 'Record JSON', 'Source States',
               'Appearances', 'Record Fingerprint', 'Recovery Sources JSON', 'Source File')
    rows = []
    for r in _documents(context):
        topic, doc = r['topic'], r['document']
        if topic not in _MOVEMENT:
            continue
        drive = _object(doc.get('drive'), 'drive')
        if topic in ('drive_session', 'DriveEvent'):
            event = (seconds_to_utc(drive.get('timestamp'), 2001), seconds_to_utc(doc.get('startTime'), 2001), '')
            values = (_text(drive.get('id')), _text(drive.get('tripID')), _text(doc.get('sessionID')),
                      _text(doc.get('userId')), 'drive', _enum(drive.get('eventType')), _text(drive.get('distance')))
        elif topic == 'trip_session':
            event = tuple(seconds_to_utc(doc.get(k), 2001) for k in ('currentTimestamp', 'startTime', 'endTime'))
            values = (_text(doc.get('id')), '', _text(doc.get('sessionId')), _text(doc.get('userId')),
                      'trip', _enum(doc.get('eventType')), _text(doc.get('distance')))
        else:
            event = (seconds_to_utc(doc.get('timestamp'), 1970), '', '')
            session = doc.get('driveSessionId') if topic == 'DriveCancellationTopic' else doc.get('tripSessionId')
            values = (_text(doc.get('id')), '', _text(session), '', 'cancel', 'cancel', '')
        coordinate = _coordinates(drive) if topic in ('drive_session', 'DriveEvent') else ('', '')
        rows.append(event + (r['logged'], r['entry_id']) + values + coordinate + (_json(doc),) + _provenance(r))
    return headers, rows, _sources(context)


def _nested(context, incidents):
    grouped = {}
    for record in _documents(context):
        topic, doc = record['topic'], record['document']
        if topic not in ('drive_session', 'DriveEvent', 'trip_session') or (incidents and topic == 'trip_session'):
            continue
        drive = _object(doc.get('drive'), 'drive')
        if topic == 'trip_session':
            items = doc.get('route')
            kind, session = 'trip', doc.get('sessionId')
        else:
            items = drive.get('drivingIncidents' if incidents else 'waypoints')
            kind, session = 'drive', drive.get('tripID')
        container = record['path'].split(os.sep + 'Library' + os.sep)[0]
        for item in _array(items, 'drivingIncidents' if incidents else 'waypoints/route'):
            key = (container, kind, _text(session), _json(item))
            entry = grouped.setdefault(key, {'item': item, 'kind': kind, 'session': _text(session),
                                             'parents': [], 'files': set(), 'states': set()})
            entry['parents'].append({'entryID': record['entry_id'], 'recordFingerprint': record['key'],
                                     'sourceFile': record['file'], 'walSourceFile': record['wal'],
                                     'recoverySources': record['appearances']})
            entry['files'].add(record['file'])
            entry['states'].add(record['states'])
    return [entry for _, entry in sorted(grouped.items())]


@artifact_processor
def life360RecoveredWaypoints(context):
    headers = (('Waypoint Time', 'datetime'), 'Trip ID or Session ID', 'Parent Entry IDs', 'Kind',
               'Latitude', 'Longitude', 'Speed (as stored)', 'Course (as stored)', 'Horizontal Accuracy (as stored)',
               'Point JSON', 'Source States', 'Parent Records', 'Contributing Records', 'Source Files')
    rows = []
    for entry in _nested(context, False):
        item = entry['item']
        rows.append((seconds_to_utc(item.get('timestamp'), 1970 if entry['kind'] == 'drive' else 2001),
                     entry['session'], _json(sorted({p['entryID'] for p in entry['parents']})), entry['kind']) +
                    _coordinates(item) + tuple(_text(item.get(k)) for k in ('speed', 'course', 'horizontalAccuracy')) +
                    (_json(item), '; '.join(sorted(entry['states'])), len(entry['parents']),
                     _json(entry['parents']), '\n'.join(sorted(entry['files']))))
    return headers, rows, _sources(context)


@artifact_processor
def life360RecoveredIncidents(context):
    headers = (('Incident Time', 'datetime'), 'Trip ID', 'Parent Entry IDs', 'Type (as stored)', 'Latitude',
               'Longitude', 'Incident JSON', 'Source States', 'Parent Records', 'Contributing Records', 'Source Files')
    rows = []
    for entry in _nested(context, True):
        item = entry['item']
        rows.append((seconds_to_utc(item.get('timestamp'), 1970), entry['session'],
                     _json(sorted({p['entryID'] for p in entry['parents']})), _text(item.get('type'))) +
                    _coordinates(item) + (_json(item), '; '.join(sorted(entry['states'])), len(entry['parents']),
                                         _json(entry['parents']), '\n'.join(sorted(entry['files']))))
    return headers, rows, _sources(context)


@artifact_processor
def life360RecoveredDrives(context):
    headers = (('Start Time', 'datetime'), ('End Time', 'datetime'), ('Created At', 'datetime'),
               ('Updated At', 'datetime'), ('Last Retrieved', 'datetime'), 'Drive ID', 'User ID',
               'Duration (as stored)', 'Distance (as stored)', 'Average Speed (as stored)', 'Top Speed (as stored)',
               'Score (as stored)', 'Distracted Count', 'Hard Braking Count', 'Rapid Acceleration Count',
               'Speeding Count', 'Drive Type (as stored)', 'User Mode (as stored)', 'User Tag (as stored)',
               'Rideshare Vendor', 'Source States', 'Appearances', 'Record Fingerprint', 'Recovery Sources JSON',
               'Source File')
    rows = []
    for record in _records(context, drives=True):
        item = record['values']
        rows.append(tuple(seconds_to_utc(item.get(k), 2001) for k in
                          ('ZSTARTTIME', 'ZENDTIME', 'ZCREATEDAT', 'ZUPDATEDAT', 'ZLASTRETRIEVED')) +
                    tuple(_text(item.get(k)) for k in ('ZID', 'ZUSERID', 'ZDURATION', 'ZDISTANCE',
                        'ZAVERAGESPEED', 'ZTOPSPEED', 'ZSCORE', 'ZDISTRACTEDCOUNT', 'ZHARDBRAKINGCOUNT',
                        'ZRAPIDACCELERATIONCOUNT', 'ZSPEEDINGCOUNT', 'ZDRIVETYPE', 'ZUSERMODE', 'ZUSERTAG',
                        'ZRIDESHAREVENDOR')) + _provenance(record))
    return headers, rows, _sources(context, drives=True)


@artifact_processor
def life360RecoveredBreaches(context):
    headers = (('Event Time', 'datetime'), ('Location Time', 'datetime'), ('Logged Time', 'datetime'),
               'Entry ID', 'Place ID', 'Circle ID', 'Name', 'Direction (as stored)', 'Distance To Fence',
               'Unit', 'Algorithm (as stored)', 'Latitude', 'Longitude', 'Speed (as stored)', 'Record JSON',
               'Source States', 'Appearances', 'Record Fingerprint', 'Recovery Sources JSON', 'Source File')
    rows = []
    for record in _documents(context):
        if record['topic'] != 'BreachTopic':
            continue
        doc = record['document']
        location = _object(doc.get('location'), 'breach location')
        for place in _array(doc.get('places'), 'breach places') or [{}]:
            distance = _object(place.get('distanceToFence'), 'distanceToFence')
            unit = _object(distance.get('unit'), 'distance unit')
            rows.append((seconds_to_utc(doc.get('timestamp', record['values'].get('ZTIMESTAMP')), 1970),
                         seconds_to_utc(location.get('timestamp'), 2001), record['logged'], record['entry_id']) +
                        tuple(_text(place.get(k)) for k in ('id', 'circleId', 'name', 'direction')) +
                        (_text(distance.get('value')), _text(unit.get('symbol')), _text(place.get('algorithm'))) +
                        _coordinates(location) + (_text(location.get('speed')), _json(doc)) + _provenance(record))
    return headers, rows, _sources(context)


@artifact_processor
def life360RecoveredDwells(context):
    headers = (('Event Time', 'datetime'), ('Dwell Start', 'datetime'), ('Dwell End', 'datetime'),
               ('Logged Time', 'datetime'), 'Entry ID', 'Dwell ID', 'Session ID', 'User ID', 'Store',
               'Event Type (as stored)', 'State (as stored)', 'Latitude', 'Longitude',
               'Horizontal Accuracy (as stored)', 'Algorithm (as stored)', 'Record JSON', 'Source States',
               'Appearances', 'Record Fingerprint', 'Recovery Sources JSON', 'Source File')
    rows = []
    for record in _documents(context):
        if record['topic'] not in ('DwellTopic', 'dwell_session'):
            continue
        doc = record['document']
        dwell = _object(doc.get('dwell'), 'dwell')
        location = _object(dwell.get('location'), 'dwell location')
        rows.append((seconds_to_utc(dwell.get('timestamp'), 2001),
                     seconds_to_utc(location.get('startTime'), 1970), seconds_to_utc(location.get('endTime'), 1970),
                     record['logged'], record['entry_id'], _text(dwell.get('id')), _text(doc.get('sessionID')),
                     _text(doc.get('userId')), record['topic'], _enum(dwell.get('eventType')), _enum(dwell.get('state'))) +
                    _coordinates(location) + (_text(location.get('horizontalAccuracy')), _text(dwell.get('algorithm')),
                                             _json(doc)) + _provenance(record))
    return headers, rows, _sources(context)
