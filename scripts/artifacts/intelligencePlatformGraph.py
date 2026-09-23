__artifacts_v2__ = {
    "intelligencePlatformEntities": {
        "name": "Intelligence Platform Knowledge Graph - Entities",
        "description": "Entities the on-device knowledge graph inferred: people, "
                       "organizations, places and software, with their resolved names, "
                       "aliases, contact methods and identifiers.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-23",
        "last_update_date": "2026-09-23",
        "requirements": "none",
        "category": "Knowledge Graph",
        "notes": "Reads the on-device knowledge graph the system builds under "
                 "IntelligencePlatform (the 'knowledged' graph). The graph.db file is "
                 "present from iOS 16; on the tested iOS 16 image it held no entities, and "
                 "it is populated on the tested iOS 17 and later images. graph.db holds a "
                 "reified triple store: a row with "
                 "relationshipId 0 carries a base fact about an entity (its type, name, "
                 "first and family name, external reference), and rows sharing a nonzero "
                 "relationshipId carry the parts of one compound attribute (a contact "
                 "method, an external identifier, an alias with its provenance, a postal "
                 "address, a coordinate). The predicate and class codes (PS.., SB.., CS..) "
                 "are resolved to labels from the ontology.db shipped in the same folder, "
                 "so resolution is exact for the device that produced the store. One row "
                 "is emitted per entity. Values are reported as stored; confidence is the "
                 "value the graph recorded, not a measurement made here. Entities are "
                 "inferred by the system from several sources, so an entity is not "
                 "evidence the user created or confirmed it. Columns are a union across "
                 "entity types, so a person entity leaves the software and place columns "
                 "blank and the reverse.",
        "paths": (
            '*/mobile/Library/IntelligencePlatform/graph.db*',
            '*/mobile/Library/IntelligencePlatform/ontology.db*'),
        "output_types": "all",
        "artifact_icon": "share-2",
        "sample_data": {
            "otto_ios17": "iOS 17.5.1 | 1321 rows",
            "felix_ios17": "iOS 17.6.1 | 314 rows",
            "fsfull002_ios17": "iOS 17.1 | 263 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 250 rows",
            "dexter_ios18": "iOS 18.3.2 | 544 rows",
            "hc_ios18_7": "iOS 18.7.8 | 304 rows",
            "iphone12_ios18": "iOS 18.7 | 304 rows",
            "hc_ios26": "iOS 26.5 | 350 rows",
            "falken_ios26": "iOS 26 | 323 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        },
    },
    "intelligencePlatformEvents": {
        "name": "Intelligence Platform Knowledge Graph - Events",
        "description": "Dated events the on-device knowledge graph inferred, such as "
                       "location visits and calendar events, with their imputed start "
                       "and end times.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-23",
        "last_update_date": "2026-09-23",
        "requirements": "none",
        "category": "Knowledge Graph",
        "notes": "Reads the event graph inside IntelligencePlatform/graph.db (the "
                 "'knowledged' graph). The file is present from iOS 16; on the tested "
                 "iOS 16 image it held no events, and it is populated on the tested iOS 17 "
                 "and later images. Each event is a reified group of triples sharing a "
                 "subject: its type, name, a location reference, and a compound date "
                 "carrying imputed start and end times. The imputed start and end times "
                 "are stored as Cocoa (2001-epoch) values and are reported here; the raw "
                 "start-time and end-time objects are stored in a serialized form and are "
                 "not reported. Predicate and class codes "
                 "are resolved from the ontology.db shipped in the same folder. Events are "
                 "inferred by the system, so an event is not evidence the user was present "
                 "or confirmed it. The location reference is reported as stored and is not "
                 "resolved to a place name here. Confidence is the value the graph "
                 "recorded, not a measurement made here, and can hold one value across "
                 "every event on a device that stored few of them.",
        "paths": (
            '*/mobile/Library/IntelligencePlatform/graph.db*',
            '*/mobile/Library/IntelligencePlatform/ontology.db*'),
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 554 rows",
            "felix_ios17": "iOS 17.6.1 | 33 rows",
            "hc_ios26": "iOS 26.5 | 28 rows",
            "falken_ios26": "iOS 26 | 22 rows",
            "otto_ios17": "iOS 17.5.1 | 20 rows",
            "fsfull002_ios17": "iOS 17.1 | 6 rows",
            "iphone12_ios18": "iOS 18.7 | 6 rows",
            "hc_ios18_7": "iOS 18.7.8 | 4 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 1 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        },
    },
}

from scripts.ilapfuncs import artifact_processor, get_file_path, \
    open_sqlite_db_readonly, convert_cocoa_core_data_ts_to_utc, does_table_exist_in_db


def _load_ontology(files_found):
    """Return dicts mapping predicate id -> label and class id -> label from the
    ontology.db shipped beside graph.db. Empty dicts if it is missing."""
    predicates = {}
    classes = {}
    onto_path = get_file_path(files_found, "ontology.db")
    if not onto_path:
        return predicates, classes
    db = open_sqlite_db_readonly(onto_path)
    if db is None:
        return predicates, classes
    cur = db.cursor()
    if does_table_exist_in_db(onto_path, "predicate"):
        for pid, label in cur.execute("select id, label from predicate"):
            predicates[pid] = label
    if does_table_exist_in_db(onto_path, "class"):
        for cid, label in cur.execute("select id, label from class"):
            classes[cid] = label
    db.close()
    return predicates, classes


def _read_triples(files_found, table_name):
    """Return (rows, graph_path) for the named table, or ([], '') if unavailable."""
    graph_path = get_file_path(files_found, "graph.db")
    if not graph_path or not does_table_exist_in_db(graph_path, table_name):
        return [], ''
    db = open_sqlite_db_readonly(graph_path)
    if db is None:
        return [], ''
    cur = db.cursor()
    rows = cur.execute(
        f'select subject, predicate, relationshipId, relationshipPredicate, '
        f'object, confidence, timestamp from "{table_name}"').fetchall()
    db.close()
    return rows, graph_path


def _group_by_subject(rows, predicates):
    """Group triples per subject. Base facts (relationshipId 0) are keyed by their
    resolved predicate label. Compound attributes (nonzero relationshipId) are grouped
    and tagged with their resolved parent predicate label and resolved part labels."""
    entities = {}
    for subject, predicate, rel_id, rel_pred, obj, confidence, timestamp in rows:
        ent = entities.setdefault(
            subject, {'base': {}, 'groups': {}, 'confidence': 0.0, 'timestamp': 0.0})
        if confidence and confidence > ent['confidence']:
            ent['confidence'] = confidence
        if timestamp and timestamp > ent['timestamp']:
            ent['timestamp'] = timestamp
        if rel_id in (0, None):
            ent['base'].setdefault(predicates.get(predicate, predicate), []).append(obj)
        else:
            grp = ent['groups'].setdefault(
                rel_id, {'parent': predicates.get(predicate, predicate), 'parts': {}})
            grp['parts'].setdefault(
                predicates.get(rel_pred, rel_pred), []).append(obj)
    return entities


def _base(ent, label):
    return ent['base'].get(label, [])


def _part(ent, parent_label, part_label):
    """Collect the values of one part across every compound group whose parent
    predicate matches."""
    out = []
    for grp in ent['groups'].values():
        if grp['parent'] == parent_label:
            out.extend(grp['parts'].get(part_label, []))
    return out


def _coords(ent):
    """Return the (latitude, longitude) of the first coordinate group, or ('', '')."""
    for grp in ent['groups'].values():
        if grp['parent'] == 'has latitude/longitude':
            lats = grp['parts'].get('latitude', [])
            lons = grp['parts'].get('longitude', [])
            if lats and lons:
                return str(lats[0]), str(lons[0])
    return '', ''


def _join(values):
    """De-duplicate preserving order and join with a comma for a report cell."""
    seen = []
    for value in values:
        text = '' if value is None else str(value)
        if text and text not in seen:
            seen.append(text)
    return ', '.join(seen)


def _cocoa(value):
    """Convert a stored Cocoa (2001-epoch) numeric string to UTC, else return None."""
    try:
        return convert_cocoa_core_data_ts_to_utc(float(value))
    except (TypeError, ValueError):
        return None


@artifact_processor
def intelligencePlatformEntities(context):
    files_found = context.get_files_found()
    predicates, classes = _load_ontology(files_found)
    rows, graph_path = _read_triples(files_found, "stable_graph")
    entities = _group_by_subject(rows, predicates)

    data_list = []
    source_path = context.get_relative_path(graph_path) if graph_path else ''
    for subject, ent in entities.items():
        entity_type = _join(classes.get(v, v) for v in _base(ent, 'is a'))
        identifiers = _join(
            _part(ent, 'identifier', 'username')
            + _part(ent, 'identifier', 'identifier id'))
        data_list.append((
            convert_cocoa_core_data_ts_to_utc(ent['timestamp']) if ent['timestamp'] else '',
            entity_type,
            _join(_base(ent, 'name')),
            _join(_base(ent, 'first name')),
            _join(_base(ent, 'family name')),
            _join(_part(ent, 'entity alias relationship', 'also known as')),
            _join(_part(ent, 'has contact information', 'phone number')),
            _join(_part(ent, 'has contact information', 'email address')),
            _join(_part(ent, 'has contact information', 'contact label')),
            identifiers,
            _join(_part(ent, 'has address', 'full street address')),
            *_coords(ent),
            _join(_base(ent, 'bundle id') + _base(ent, 'application identifier')),
            _join(_base(ent, 'same as')),
            round(ent['confidence'], 4),
            str(subject)))

    data_headers = (
        ('Latest Timestamp', 'datetime'),
        'Entity Type',
        'Name',
        'First Name',
        'Family Name',
        'Also Known As',
        ('Phone Numbers', 'phonenumber'),
        'Email Addresses',
        'Contact Labels',
        'Other Identifiers',
        'Address',
        'Latitude',
        'Longitude',
        'App Bundle ID',
        'Same As',
        'Confidence',
        'Entity ID')
    return data_headers, data_list, source_path


@artifact_processor
def intelligencePlatformEvents(context):
    files_found = context.get_files_found()
    predicates, classes = _load_ontology(files_found)
    rows, graph_path = _read_triples(files_found, "event_graph")
    events = _group_by_subject(rows, predicates)

    data_list = []
    source_path = context.get_relative_path(graph_path) if graph_path else ''
    for subject, ent in events.items():
        starts = [_cocoa(v) for v in
                  _part(ent, 'has date', 'imputed start time')
                  + _part(ent, 'has date', 'imputed occurrence date')]
        ends = [_cocoa(v) for v in _part(ent, 'has date', 'imputed end time')]
        starts = [s for s in starts if s]
        ends = [e for e in ends if e]
        data_list.append((
            min(starts) if starts else '',
            max(ends) if ends else '',
            _join(classes.get(v, v) for v in _base(ent, 'is a')),
            _join(_base(ent, 'name')),
            _join(_part(ent, 'has location relationship', 'has location')),
            round(ent['confidence'], 4),
            str(subject)))

    data_headers = (
        ('Imputed Start Time', 'datetime'),
        ('Imputed End Time', 'datetime'),
        'Event Type',
        'Name',
        'Location (as stored)',
        'Confidence',
        'Event ID')
    return data_headers, data_list, source_path
