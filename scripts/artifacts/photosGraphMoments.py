__artifacts_v2__ = {
    "photosGraphMoments": {
        "name": "Photos Graph Moment Locations (photosgraph.kgdb)",
        "description": "Places the Photos app's knowledge graph (photosgraph.kgdb) links a moment "
                       "(a group of photos) to: the time window, coordinates and photo count the link "
                       "records, the place's name and coordinates, the moment's identifier, and the "
                       "moment's located photos captured inside that window.",
        "author": "Heather Charpentier, Claude",
        "creation_date": "2026-10-14",
        "last_update_date": "2026-10-14",
        "requirements": "none",
        "category": "Photos",
        "notes": "The graph is a generic store of nodes (things such as a moment or an address), "
                 "edges (links between two nodes) and named attributes on either (Attribute, "
                 "NodeValue, EdgeValue). Each row is an edge that carries a lat attribute (every such "
                 "edge on the extractions checked also carried lng): "
                 "the times, coordinates and count are its utcs, utce (Unix seconds), lat, lng and noa; "
                 "the moment identifier is the lclid of the node it starts from; the Address column is "
                 "the name attribute of the node it points to and its coordinates are that node's lat "
                 "and lng. No source says the name is an address: most names on the extractions "
                 "checked carry a street number and some do not. Column meanings "
                 "come from the attribute names and from cross-checks against Photos.sqlite, not from "
                 "Apple documentation. A moment can link to more than one place, one row each, so a "
                 "Moment Identifier can repeat. "
                 "Checked on 19 extractions (iOS 15 to 26; 16 hold located edges, 3 hold no lat "
                 "attribute and give no rows): 751 moments counted per extraction (745 distinct "
                 "identifiers, 6 present in two extractions of the same device), 674 with one place, "
                 "64 with two, 11 with three, 2 with four. Every edge's lclid matched a ZMOMENT.ZUUID and its utcs to utce "
                 "window lay inside that moment's ZSTARTDATE to ZENDDATE; the window equalled the "
                 "moment's span for 561 of the 674 one-place moments and for one edge in 3 of the 77 "
                 "others (where the other place's window lies inside it). This is consistent with utcs "
                 "and utce being the time span of the photos at that place rather than of the whole "
                 "moment; no source states this. "
                 "The Photos column lists, in capture order, the ZDIRECTORY / ZFILENAME of the "
                 "moment's ZASSET rows whose ZDATECREATED falls inside the edge's utcs to utce window "
                 "and whose ZLATITUDE is not -180 (the stored value the other iLEAPP Photos artifacts "
                 "treat as no location; a source for what -180 marks was not found). This is a match "
                 "on time, not a link the artifact reads from the store: no column read here names "
                 "which photo belongs to which place. On the 19 "
                 "extractions the photos listed this way equalled noa for 824 of 843 edges; for the "
                 "other 19 the window held more located photos than noa (5 of them overlap another "
                 "place's window in the same moment). When the counts differ the photos are listed but "
                 "not attached, and Photo Check says so. "
                 "When they agree, the Photo Media column attaches a listed photo only when exactly "
                 "one file exists at its stored ZDIRECTORY / ZFILENAME (compared without regard to "
                 "letter case) inside the same Media folder as "
                 "the Photos.sqlite being read, and that file's size equals the ZORIGINALFILESIZE "
                 "Photos.sqlite stored for it; any other photo is not attached and Photo Check names it "
                 "and why. That match is by path and size and does not prove the file's content: no "
                 "file hash is compared. A HEIC / HEIF still is attached as a JPEG copy made for the "
                 "report, as the photosDbexif artifact does; the original file is not changed. The "
                 "Photos columns are empty when Photos.sqlite is not in the extraction. "
                 "The moments are groups of photos in the library, which may not have been taken on "
                 "this device; a row does not establish that the device was at the place. Moment "
                 "approximate locations are also reported per asset by the Photos REFforAssetAnalysis "
                 "artifacts. Not covered: edges and nodes without lat / lng (scenes, people, dates "
                 "and the other graph labels) and the tombstone tables. Reference: Cellebrite, 'Was it "
                 "actually there? Locations Cheat Sheet' (May 2026), Media: photosgraph.kgdb.",
        "paths": ('*/PhotoData/Caches/GraphService/PhotosGraph/photosgraph.kgdb*',
                  '*/mobile/Media/PhotoData/Photos.sqlite*',
                  '*/mobile/Media/DCIM/*/*'),
        "output_types": ["html", "tsv", "lava", "kml", "timeline"],
        "artifact_icon": "photo",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 309 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 3 rows",
            "dexter_ios18": "iOS 18.3.2 | 189 rows",
            "felix_ios17": "iOS 17.6.1 | 11 rows",
            "hc_ios18_7": "iOS 18.7.8 | 6 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 10 rows",
            "otto_ios17": "iOS 17.5.1 | 195 rows",
        }
    }
}

import io
import os
from datetime import datetime, timezone

from PIL import Image
from pillow_heif import register_heif_opener

from scripts.ilapfuncs import (artifact_processor, check_in_embedded_media, check_in_media,
                               does_table_exist_in_db, get_sqlite_db_records, logfunc,
                               null_absent_columns, open_sqlite_db_readonly)

register_heif_opener()


def _attach(path, name):
    """Register one photo / video file as media. A HEIC / HEIF still is attached as a JPEG copy
    so a browser can show it (as photosDbexif does); the original stays in the extraction."""
    if str(path).upper().endswith(('.HEIC', '.HEIF')):
        try:
            with io.BytesIO() as buf, Image.open(path) as image:
                image.save(buf, format='JPEG')
                return check_in_embedded_media(path, buf.getvalue(), f'{name}.jpg',
                                               force_type='image/jpeg', force_extension='jpg')
        except (OSError, ValueError) as ex:
            logfunc(f'Error converting {name} to JPEG for the report: {ex}')
    return check_in_media(path, name)


def _norm(path):
    return str(path).replace('\\', '/').lower()


def _media_root(photos_db):
    """The Media folder the Photos.sqlite being read belongs to (.../Media/PhotoData/Photos.sqlite)."""
    norm = _norm(photos_db)
    i = norm.rfind('/photodata/photos.sqlite')
    return norm[:i] if i >= 0 else None


def _resolve(media_root, found, relative, stored_size):
    """(path, reason) for one photo. The file must be the one at the stored ZDIRECTORY /
    ZFILENAME inside the same Media folder as the Photos.sqlite being read, exactly one such
    file, and its size must equal the stored ZORIGINALFILESIZE; otherwise no path and why."""
    if not media_root:
        return None, 'no Photos.sqlite location'
    want = f'{media_root}/{relative.lower()}'
    hits = [p for p in found if _norm(p) == want]
    if not hits:
        return None, 'not in the extraction'
    if len(hits) > 1:
        return None, 'more than one file at that path'
    if stored_size is None:
        return None, 'no stored size to compare'
    try:
        size = os.path.getsize(hits[0])
    except OSError:
        return None, 'file could not be read'
    if size != stored_size:
        return None, 'size differs from Photos.sqlite'
    return hits[0], None


NO_LOCATION = -180          # ZASSET.ZLATITUDE of a photo with no location
COCOA_EPOCH = 978307200     # ZDATECREATED is seconds since 2001-01-01 UTC


def _photos_by_moment(photos_db):
    """{ZMOMENT.ZUUID: [(ZDIRECTORY/ZFILENAME, ZORIGINALFILESIZE, capture time in Unix seconds,
    located), ...]} in capture order."""
    out = {}
    if not photos_db or not (does_table_exist_in_db(photos_db, 'ZASSET')
                             and does_table_exist_in_db(photos_db, 'ZMOMENT')):
        return out
    size_join = ('LEFT JOIN ZADDITIONALASSETATTRIBUTES ON ZADDITIONALASSETATTRIBUTES.ZASSET = ZASSET.Z_PK'
                 if does_table_exist_in_db(photos_db, 'ZADDITIONALASSETATTRIBUTES') else '')
    size_col = 'ZADDITIONALASSETATTRIBUTES.ZORIGINALFILESIZE' if size_join else 'NULL'
    rows = get_sqlite_db_records(photos_db, null_absent_columns(photos_db, f'''
        SELECT ZMOMENT.ZUUID, ZASSET.ZDIRECTORY, ZASSET.ZFILENAME, {size_col},
               ZASSET.ZDATECREATED, ZASSET.ZLATITUDE
        FROM ZASSET JOIN ZMOMENT ON ZMOMENT.Z_PK = ZASSET.ZMOMENT
        {size_join}
        ORDER BY ZASSET.ZDATECREATED, ZASSET.Z_PK
    '''))
    for uuid, directory, filename, size, created, latitude in rows:
        if uuid and filename:
            out.setdefault(uuid, []).append((
                f'{directory}/{filename}' if directory else filename, size,
                created + COCOA_EPOCH if created is not None else None,
                latitude is not None and latitude != NO_LOCATION))
    return out


def _in_window(entries, start, end):
    """The located photos captured inside the edge's utcs to utce window (both ends included)."""
    if start is None or end is None:
        return []
    return [e for e in entries if e[3] and e[2] is not None and start <= e[2] <= end]


def _unix_utc(value):
    """Unix seconds to UTC; None for a missing or non-positive value."""
    if value is None:
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return datetime.fromtimestamp(value, tz=timezone.utc) if value > 0 else None


def _values(db, table, element_id, wanted):
    """{attribute name: value} for one node or edge, limited to the wanted attribute ids."""
    out = {}
    for attribute_id, int_value, real_value, string_value in db.execute(
            f'SELECT attributeId, intValue, realValue, stringValue FROM {table} WHERE elementId = ?',
            (element_id,)):
        name = wanted.get(attribute_id)
        if name is not None:
            out[name] = real_value if real_value is not None else \
                int_value if int_value is not None else string_value
    return out


@artifact_processor
def photosGraphMoments(context):
    data_headers = (('Start DateTime (utcs)', 'datetime'), ('End DateTime (utce)', 'datetime'),
                    'Latitude', 'Longitude', 'Photo Count (noa, as stored)', 'Address (as stored)',
                    'Address Latitude', 'Address Longitude', 'Moment Identifier (lclid)',
                    'Relevance (as stored)', 'Photos in Window (from Photos.sqlite)', 'Photo Check',
                    ('Photo Media', 'media'))
    data_list = []
    found = [str(f) for f in context.get_files_found()]
    sources = [f for f in found if f.endswith('.kgdb')]
    photos_db = next((f for f in found if f.endswith('Photos.sqlite')), None)
    photos = _photos_by_moment(photos_db)
    media_root = _media_root(photos_db) if photos_db else None

    attached = {}               # one check-in (and HEIC conversion) per photo across rows

    def media(entries, noa):
        """(media refs or None, check text) for the photos listed on one row."""
        if not photos_db:
            return None, None
        if noa is None:
            return None, (f'located photos in the window: {len(entries)}, the graph records no count; '
                          'not attached')
        if len(entries) != noa:
            return None, (f'located photos in the window: {len(entries)}, the graph counts {noa}; '
                          'not attached because the counts differ')
        if not entries:
            return None, None
        refs, problems = [], []
        for relative, stored_size, _created, _located in entries:
            if relative not in attached:
                path, reason = _resolve(media_root, found, relative, stored_size)
                attached[relative] = (_attach(path, relative) if path else None, reason)
            ref, reason = attached[relative]
            if ref:
                refs.append(ref)
            else:
                problems.append(f'{relative} ({reason or "could not be attached"})')
        check = f'{len(refs)} of {len(entries)} attached (path and size match Photos.sqlite)'
        if problems:
            check += '; not attached: ' + ', '.join(problems)
        return refs or None, check
    for source in sources:
        if not all(does_table_exist_in_db(source, t) for t in ('Attribute', 'Edge', 'EdgeValue', 'NodeValue')):
            continue
        db = open_sqlite_db_readonly(source)
        if not db:
            continue
        try:
            attributes = dict(db.execute('SELECT identifier, name FROM Attribute'))
            by_name = {name: identifier for identifier, name in attributes.items()}
            if 'lat' not in by_name or 'lng' not in by_name:
                continue
            edge_wanted = {by_name[n]: n for n in ('lat', 'lng', 'utcs', 'utce', 'noa', 'relevance') if n in by_name}
            node_wanted = {by_name[n]: n for n in ('lat', 'lng', 'name', 'lclid') if n in by_name}
            edges = db.execute('''
                SELECT Edge.identifier, Edge.sourceNodeId, Edge.targetNodeId
                FROM Edge JOIN EdgeValue ON EdgeValue.elementId = Edge.identifier
                WHERE EdgeValue.attributeId = ?
                ORDER BY Edge.identifier''', (by_name['lat'],)).fetchall()
            for edge_id, source_node, target_node in edges:
                edge = _values(db, 'EdgeValue', edge_id, edge_wanted)
                moment = _values(db, 'NodeValue', source_node, node_wanted)
                place = _values(db, 'NodeValue', target_node, node_wanted)
                entries = _in_window(photos.get(moment.get('lclid'), []),
                                     edge.get('utcs'), edge.get('utce'))
                refs, check = media(entries, edge.get('noa'))
                data_list.append((_unix_utc(edge.get('utcs')), _unix_utc(edge.get('utce')),
                                  edge.get('lat'), edge.get('lng'), edge.get('noa'),
                                  place.get('name'), place.get('lat'), place.get('lng'),
                                  moment.get('lclid'), edge.get('relevance'),
                                  ', '.join(e[0] for e in entries) or None, check, refs))
        except Exception as ex:  # pylint: disable=broad-exception-caught
            logfunc(f'Error reading photosgraph.kgdb moment locations: {ex}')
        finally:
            db.close()
    data_list.sort(key=lambda r: (r[0] is None, r[0] or datetime.min.replace(tzinfo=timezone.utc)))
    return data_headers, data_list, '\n'.join(sources + ([photos_db] if photos_db else []))
