__artifacts_v2__ = {
    "gpx_files": {
        "name": "GPX Files",
        "description": "GPX files held in an app's Documents folder, with the tool named as "
                       "having written each one.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "Locations",
        "notes": "One row per GPX file matched under an app's Documents folder, at any depth. A "
                 "file that is not complete XML is still listed with the counts read before the "
                 "error; Read Error then holds the parser's message, which is also recorded in "
                 "the run log, and is blank for a file read to its end. GPX is an open XML format "
                 "published by Topografix and the values here "
                 "are read from its own elements: Creator is the file's creator attribute, Track "
                 "Points and Waypoints count the trkpt and wpt elements the file contains, and "
                 "Track Segments counts the trkseg elements the file opens, including one that "
                 "holds no point. Creator is the "
                 "attribute that names the tool the "
                 "file records as its writer: on the tested images twelve files named Open GPX "
                 "Tracker for iOS and two named other tools, a web route planner and a desktop "
                 "mapping program, so those two files record a writer other than an app on the "
                 "device and their points are not by themselves a trace of where the device went. "
                 "First Point Time and Last Point Time are the earliest and latest time values "
                 "among the file's trkpt and wpt elements. Every time on the tested images ended "
                 "in Z and is read as UTC from that designator. A time with no zone designator, or "
                 "one this reader cannot parse, is left blank and is not counted toward First "
                 "Point Time or Last Point Time; the GPX 1.1 schema documents times as UTC but "
                 "does not require the designator. Container App is the app whose data container "
                 "held the file, read from the metadata plist of the nearest folder above the "
                 "file that holds one, because a Documents folder belongs to one app; it is blank "
                 "when no such plist was matched. A file whose name begins with recovery- "
                 "carried the Open GPX Tracker creator on the tested images; why the app writes "
                 "such a file is not established here. Four of them sat on the iOS 16.5 image and "
                 "two of those had a file of the same name without the prefix beside them: one "
                 "matched its twin on point count and time span, and the other held 37,487 points "
                 "against its twin's 236, so on that image one recovery file held far more points "
                 "than the file of the same name without the prefix. The other two had no "
                 "counterpart at all. Track Name is the name element that is a direct child of a "
                 "trk element; a name inside a track point or another child element is not used. "
                 "One name is kept per file, the first one that is not empty, so a file holding "
                 "several tracks shows one track's name. The Read Error column, the "
                 "direct-child rule for Track Name, the segment count and the subfolder lookup "
                 "for Container App were exercised on constructed files, not on the tested "
                 "images. Most tested files had none: none of the eight files "
                 "on the iOS 16.5 image carried one and two of "
                 "the six on the iOS 17.5.1 image did.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/*.gpx',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "file",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Open GPX Tracker | 8 rows",
            "otto_ios17": "iOS 17.5.1 | Open GPX Tracker | 6 rows",
        },
    },
    "gpx_track_points": {
        "name": "GPX Track Points",
        "description": "The points recorded in GPX track files, with the coordinates, elevation and "
                       "time each one carries.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "Locations",
        "notes": "One row per trkpt element across the GPX files in an app's Documents folder. "
                 "Latitude and longitude are the element's own attributes and elevation and time "
                 "are its child elements, all read from the file. Every timestamp on the tested "
                 "images ended in Z and is reported as UTC from that designator. A time with no "
                 "zone designator, or one this reader cannot parse, is reported blank, so a blank "
                 "Timestamp does not always mean the point has no time element. Elevation and Time "
                 "are each absent on some points because the format does not require them; a point "
                 "missing a time still reports its coordinates. Segment is the index of the trkseg "
                 "element that holds the point; a change in segment number marks a boundary the "
                 "writer placed inside the file, and the reason a writer started a new segment is "
                 "not recorded in the file. Track Name is the name element that is a direct child of the "
                 "trk element holding the point, so points of a second track in one file carry "
                 "that track's own name or none; that case was exercised on a constructed file, "
                 "not on the tested images. A file that is not complete XML contributes the "
                 "points read before the error, which is recorded in the run log and in the Read "
                 "Error column of GPX Files. A point read from a file whose Creator names another "
                 "tool comes from a file that records a writer other than an app on this device, "
                 "and the Creator column carries that attribute onto every row. This artifact is "
                 "large by nature: the fourteen files on the two tested images together hold "
                 "451,774 points, and two files account for 361,216 of them. Track Name is absent "
                 "on every point of the iOS 16.5 image because none of its files names its track, "
                 "and Container App held one value on both tested images because a single app's "
                 "Documents folder held every GPX file on each. Time is the field most often "
                 "missing: 8,004 points of the iOS 17.5.1 image carry none, and all of them come "
                 "from one file whose Creator attribute names a tool other than Open GPX Tracker.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/*.gpx',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "timeline", "lava", "kml"],
        "artifact_icon": "navigation",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Open GPX Tracker | 77,972 rows",
            "otto_ios17": "iOS 17.5.1 | Open GPX Tracker | 373,802 rows",
        },
    },
    "gpx_waypoints": {
        "name": "GPX Waypoints",
        "description": "The waypoints marked in GPX files, with the name and time where the "
                       "waypoint carries them.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "Locations",
        "notes": "One row per wpt element across the GPX files in an app's Documents folder. A "
                 "wpt is a point marked in its own right rather than one of a track's samples. "
                 "Name, description, symbol and type are the element's own children and are "
                 "reported as they appear; a waypoint carries none of them by requirement, so a "
                 "blank name is a waypoint saved without one. A time ending in Z or carrying an "
                 "offset is converted to UTC from that designator; a time with no zone designator, "
                 "or one this reader cannot parse, is reported blank. A waypoint in a file whose "
                 "Creator "
                 "names another tool comes from a file that records a writer other than an app "
                 "on this device. "
                 "A waypoint sits outside the track elements in the GPX schema, so no track "
                 "name is carried on these rows even when the same file holds a track. "
                 "Container App held one value on the iOS 16.5 image, where a single app's "
                 "Documents folder held every GPX file, and one on the iOS 17.5.1 image for "
                 "the same reason.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/*.gpx',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "timeline", "lava", "kml"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Open GPX Tracker | 13 rows",
            "otto_ios17": "iOS 17.5.1 | Open GPX Tracker | 17 rows",
        },
    },
}

import os
import plistlib
from datetime import datetime, timezone
from xml.etree import ElementTree

from scripts.ilapfuncs import artifact_processor, logfunc

_METADATA_NAME = '.com.apple.mobile_container_manager.metadata.plist'
_GPX_NS = '{http://www.topografix.com/GPX/1/1}'


def _gpx_files(files_found):
    '''Every GPX file among the matched files, directories skipped.'''
    seen = []
    for found in files_found:
        path = str(found)
        if os.path.isdir(path):
            continue
        if path.lower().endswith('.gpx') and path not in seen:
            seen.append(path)
    return seen


def _container_apps(files_found):
    '''{container directory: bundle id} from each container's own metadata plist.'''
    apps = {}
    for found in files_found:
        path = str(found)
        if os.path.basename(path) != _METADATA_NAME or os.path.isdir(path):
            continue
        try:
            with open(path, 'rb') as handle:
                plist = plistlib.load(handle)
        except (plistlib.InvalidFileException, OSError, ValueError) as error:
            logfunc(f'GPX: could not read a container metadata plist: {error}')
            continue
        bundle_id = plist.get('MCMMetadataIdentifier')
        if bundle_id:
            apps[os.path.dirname(path).replace('\\', '/')] = bundle_id
    return apps


def _container_app(gpx_path, apps):
    '''Bundle id of the app whose container holds the file, at any depth under Documents.

    The declared pattern also matches a file in a subfolder of Documents, so the search
    walks up from the file to the nearest folder that holds a container metadata plist.
    '''
    folder = os.path.dirname(str(gpx_path)).replace('\\', '/')
    while folder:
        if folder in apps:
            return apps[folder]
        parent = os.path.dirname(folder)
        if parent == folder:
            break
        folder = parent
    return ''


def _tag(element):
    '''An element's tag with any namespace removed.'''
    tag = element.tag
    return tag.rsplit('}', 1)[-1] if '}' in tag else tag


def _child_text(element, name):
    '''The text of a named child element, namespaced or not, or ''.'''
    for child in element:
        if _tag(child) == name and child.text:
            return child.text.strip()
    return ''


def _gpx_time(value):
    '''A GPX time, which carries its own zone, as an aware UTC datetime, or ''.'''
    if not value:
        return ''
    text = value.strip().replace('Z', '+00:00')
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return ''
    if parsed.tzinfo is None:
        return ''
    return parsed.astimezone(timezone.utc)


def _walk(path):
    '''Yield (kind, payload) events while streaming a GPX file.

    Kinds: 'creator' (the gpx element's creator attribute), 'trk' (a track opens),
    'name' (the name element that is a direct child of a trk), 'trkseg' (a segment opens),
    'trkpt' and 'wpt' ((element, segment index)), and 'error' (the reason the read stopped
    early). Streamed with iterparse and cleared as it goes, because a single file on the
    tested images holds over 180,000 points.
    '''
    try:
        context = ElementTree.iterparse(path, events=('start', 'end'))
        segment = 0
        stack = []
        for event, element in context:
            tag = _tag(element)
            if event == 'start':
                stack.append(tag)
                if tag == 'gpx':
                    yield 'creator', element.get('creator', '')
                elif tag == 'trk':
                    yield 'trk', None
                elif tag == 'trkseg':
                    segment += 1
                    yield 'trkseg', segment
                continue
            if stack:
                stack.pop()
            if tag == 'name' and stack and stack[-1] == 'trk':
                yield 'name', (element.text or '').strip()
            elif tag == 'trkpt':
                yield 'trkpt', (element, segment)
                element.clear()
            elif tag == 'wpt':
                yield 'wpt', (element, segment)
                element.clear()
            elif tag == 'trkseg':
                element.clear()
    except ElementTree.ParseError as error:
        logfunc(f'GPX: {os.path.basename(path)} is not readable as XML: {error}')
        yield 'error', f'XML parse error: {error}'
    except OSError as error:
        logfunc(f'GPX: could not open {os.path.basename(path)}: {error}')
        yield 'error', f'Could not open: {error.strerror or type(error).__name__}'


@artifact_processor
def gpx_files(context):
    data_list = []
    files_found = context.get_files_found()
    sources = _gpx_files(files_found)
    apps = _container_apps(files_found)

    for source_path in sources:
        creator = track_name = read_error = ''
        points = waypoints = segments = 0
        first = last = None
        for kind, payload in _walk(source_path):
            if kind == 'creator':
                creator = payload
            elif kind == 'name' and not track_name:
                track_name = payload
            elif kind == 'trkseg':
                segments += 1
            elif kind == 'error':
                read_error = payload
            elif kind in ('trkpt', 'wpt'):
                element, _segment = payload
                if kind == 'trkpt':
                    points += 1
                else:
                    waypoints += 1
                stamp = _gpx_time(_child_text(element, 'time'))
                if stamp:
                    first = stamp if first is None or stamp < first else first
                    last = stamp if last is None or stamp > last else last
        data_list.append((
            first or '', last or '', os.path.basename(source_path), creator, track_name,
            str(points), str(waypoints), str(segments),
            _container_app(source_path, apps), read_error,
            context.get_relative_path(source_path),
        ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)

    data_headers = (
        ('First Point Time', 'datetime'), ('Last Point Time', 'datetime'), 'File Name',
        'Creator', 'Track Name', 'Track Points', 'Waypoints', 'Track Segments',
        'Container App', 'Read Error', 'Source Path',
    )
    return data_headers, data_list, '\n'.join(sources)


def _point_rows(sources, apps, wanted, fields):
    """Rows for the trkpt or wpt elements of every GPX file.

    The values are pulled out while the element is still live, because the walk clears each
    element as it goes and a cleared element has neither attributes nor children.
    """
    rows = []
    for source_path in sources:
        creator = track_name = ''
        app = _container_app(source_path, apps)
        name = os.path.basename(source_path)
        for kind, payload in _walk(source_path):
            if kind == 'creator':
                creator = payload
            elif kind == 'trk':
                track_name = ''
            elif kind == 'name' and not track_name:
                track_name = payload
            elif kind == wanted:
                element, segment = payload
                values = {'lat': element.get('lat', ''), 'lon': element.get('lon', '')}
                for field in fields:
                    values[field] = _child_text(element, field)
                rows.append((values, segment, creator, track_name, name, app))
    return rows


@artifact_processor
def gpx_track_points(context):
    data_list = []
    files_found = context.get_files_found()
    sources = _gpx_files(files_found)
    apps = _container_apps(files_found)

    for values, segment, creator, track_name, name, app in _point_rows(
            sources, apps, 'trkpt', ('time', 'ele')):
        data_list.append((
            _gpx_time(values['time']), values['lat'], values['lon'], values['ele'],
            track_name, str(segment), name, creator, app,
        ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)

    data_headers = (
        ('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Elevation', 'Track Name',
        'Segment', 'File Name', 'Creator', 'Container App',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def gpx_waypoints(context):
    data_list = []
    files_found = context.get_files_found()
    sources = _gpx_files(files_found)
    apps = _container_apps(files_found)

    for values, _segment, creator, _track_name, name, app in _point_rows(
            sources, apps, 'wpt', ('time', 'name', 'desc', 'sym', 'type', 'ele')):
        data_list.append((
            _gpx_time(values['time']), values['lat'], values['lon'], values['name'],
            values['desc'], values['sym'], values['type'], values['ele'],
            name, creator, app,
        ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)

    data_headers = (
        ('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Name', 'Description', 'Symbol',
        'Type', 'Elevation', 'File Name', 'Creator', 'Container App',
    )
    return data_headers, data_list, '\n'.join(sources)
