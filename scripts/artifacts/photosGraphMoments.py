__artifacts_v2__ = {
    "photosGraphMoments": {
        "name": "Photos Graph Moment Locations (photosgraph.kgdb)",
        "description": "Moments (groups of photos) linked to a place in the Photos app's knowledge "
                       "graph (photosgraph.kgdb): the moment's start and end times, coordinates and "
                       "photo count, the place's address and coordinates, and the moment's identifier.",
        "author": "Heather Charpentier, Claude",
        "creation_date": "2026-10-14",
        "last_update_date": "2026-10-14",
        "requirements": "none",
        "category": "Photos",
        "notes": "The graph is a generic store of nodes (things such as a moment or an address), "
                 "edges (links between two nodes) and named attributes on either (Attribute, "
                 "NodeValue, EdgeValue). Each row is an edge that carries lat and lng attributes: "
                 "times, coordinates and count are its utcs, utce, lat, lng and noa; the moment "
                 "identifier is the lclid of the node it starts from; the address and its "
                 "coordinates are the name, lat and lng of the node it points to. Column meanings "
                 "come from the attribute names and from cross-checks, not from Apple documentation. "
                 "utcs / utce are Unix seconds. Checked "
                 "against the hc_ios18_7 extraction (iPhone XS, iOS 18.7.8): 6 edges carry lat / lng; "
                 "for each, the source node's lclid equals a ZMOMENT.ZUUID in Photos.sqlite, utcs and "
                 "utce equal that moment's ZSTARTDATE and ZENDDATE to the second, noa equals its "
                 "ZCACHEDCOUNT and the number of located ZASSET rows in that window, and the edge "
                 "coordinates equal its ZAPPROXIMATELATITUDE / LONGITUDE in 4 cases; in the other 2 "
                 "the moment stores -180 (no location) and the graph edge carries coordinates. The "
                 "target node's name was an address and its coordinates were within about 75 m of the "
                 "edge's. The moments are groups of photos in the library, which may not have been "
                 "taken on this device; a row does not establish that the device was at the location. "
                 "Moment approximate locations are also reported per asset by the Photos "
                 "REFforAssetAnalysis artifacts; this artifact adds the address and the coordinates "
                 "where ZMOMENT has none. The Photos column lists, in capture order, the "
                 "ZDIRECTORY / ZFILENAME of every ZASSET row in Photos.sqlite whose ZMOMENT is the "
                 "ZMOMENT row with that identifier (ZMOMENT.ZUUID = lclid); it is empty when "
                 "Photos.sqlite is not in the extraction. The Photo Media column attaches each listed "
                 "file found under Media/DCIM in the extraction; a listed file that is not in the "
                 "extraction is named but not attached. A HEIC / HEIF still is attached as a JPEG "
                 "copy made for the report, so a browser can show it, as the photosDbexif artifact "
                 "does; the original file is not changed. On hc_ios18_7 every moment's identifier "
                 "matched a ZMOMENT row, the number of photos listed equalled the graph's count, and "
                 "every listed file was found and attached. "
                 "Not covered: edges and nodes without lat / lng (scenes, "
                 "people, dates and the other graph labels) and the tombstone tables. Reference: "
                 "Cellebrite, 'Was it actually there? Locations Cheat Sheet' (May 2026), Media: "
                 "photosgraph.kgdb.",
        "paths": ('*/PhotoData/Caches/GraphService/PhotosGraph/photosgraph.kgdb*',
                  '*/mobile/Media/PhotoData/Photos.sqlite*',
                  '*/mobile/Media/DCIM/*/*'),
        "output_types": ["html", "tsv", "lava", "kml", "timeline"],
        "artifact_icon": "photo",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 6 rows",
        }
    }
}

import io
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
            with io.BytesIO() as buf:
                Image.open(path).save(buf, format='JPEG')
                return check_in_embedded_media(path, buf.getvalue(), f'{name}.jpg',
                                               force_type='image/jpeg', force_extension='jpg')
        except (OSError, ValueError) as ex:
            logfunc(f'Error converting {name} to JPEG for the report: {ex}')
    return check_in_media(path, name)


def _dcim_index(found):
    """{'DCIM/<folder>/<file>' (lower case): path found} for the photo files in the extraction."""
    out = {}
    for path in found:
        norm = path.replace('\\', '/')
        i = norm.find('/Media/DCIM/')
        if i >= 0:
            out[norm[i + len('/Media/'):].lower()] = path
    return out


def _photos_by_moment(photos_db):
    """{ZMOMENT.ZUUID: [ZDIRECTORY/ZFILENAME, ...]} in capture order, from Photos.sqlite."""
    out = {}
    if not photos_db or not (does_table_exist_in_db(photos_db, 'ZASSET')
                             and does_table_exist_in_db(photos_db, 'ZMOMENT')):
        return out
    rows = get_sqlite_db_records(photos_db, null_absent_columns(photos_db, '''
        SELECT ZMOMENT.ZUUID, ZASSET.ZDIRECTORY, ZASSET.ZFILENAME
        FROM ZASSET JOIN ZMOMENT ON ZMOMENT.Z_PK = ZASSET.ZMOMENT
        ORDER BY ZASSET.ZDATECREATED, ZASSET.Z_PK
    '''))
    for uuid, directory, filename in rows:
        if uuid and filename:
            out.setdefault(uuid, []).append(f'{directory}/{filename}' if directory else filename)
    return out


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
                    'Relevance (as stored)', 'Photos (from Photos.sqlite)', ('Photo Media', 'media'))
    data_list = []
    found = [str(f) for f in context.get_files_found()]
    sources = [f for f in found if f.endswith('.kgdb')]
    photos_db = next((f for f in found if f.endswith('Photos.sqlite')), None)
    photos = _photos_by_moment(photos_db)
    dcim = _dcim_index(found)

    def media(names):
        refs = []
        for name in names:
            path = dcim.get(name.lower())
            ref = _attach(path, name) if path else None
            if ref:
                refs.append(ref)
        return refs or None
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
                data_list.append((_unix_utc(edge.get('utcs')), _unix_utc(edge.get('utce')),
                                  edge.get('lat'), edge.get('lng'), edge.get('noa'),
                                  place.get('name'), place.get('lat'), place.get('lng'),
                                  moment.get('lclid'), edge.get('relevance'),
                                  ', '.join(photos.get(moment.get('lclid'), [])) or None,
                                  media(photos.get(moment.get('lclid'), []))))
        except Exception as ex:  # pylint: disable=broad-exception-caught
            logfunc(f'Error reading photosgraph.kgdb moment locations: {ex}')
        finally:
            db.close()
    data_list.sort(key=lambda r: (r[0] is None, r[0] or datetime.min.replace(tzinfo=timezone.utc)))
    return data_headers, data_list, '\n'.join(sources + ([photos_db] if photos_db else []))
