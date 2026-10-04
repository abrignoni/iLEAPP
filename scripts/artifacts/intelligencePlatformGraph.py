__artifacts_v2__ = {
    "intelligencePlatformEntities": {
        "name": "Intelligence Platform Knowledge Graph - Entities",
        "description": "Entities held in IntelligencePlatform graph.db: people, "
                       "organizations, places and software, with their resolved names, "
                       "aliases, contact methods and identifiers.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-23",
        "last_update_date": "2026-09-23",
        "requirements": "none",
        "category": "Knowledge Graph",
        "notes": "Reads graph.db in Library/IntelligencePlatform. On the tested images "
                 "graph.db was present on iOS 16 with no entities and held entities on iOS "
                 "17 and later; earlier versions were not checked. graph.db holds a "
                 "reified triple store: a row with "
                 "relationshipId 0 carries a base fact about an entity (its type, name, "
                 "first and family name, external reference), and rows sharing a nonzero "
                 "relationshipId carry the parts of one compound attribute (a contact "
                 "method, an external identifier, an alias with its provenance, a postal "
                 "address, a coordinate). The predicate and class codes (PS.., SB.., CS..) "
                 "are resolved to labels from the ontology.db shipped in the same folder, "
                 "so the labels are the ones that device's ontology.db gives. The columns "
                 "are filled by matching those labels by name; if ontology.db is missing "
                 "or a label is worded differently, the row is still listed with those "
                 "columns blank. One row "
                 "is emitted per entity. Values are reported as stored. Confidence is the "
                 "highest confidence value among the entity's rows, rounded to four "
                 "places, and Latest Timestamp the newest timestamp among them; neither is "
                 "a measurement made here. How the system produces an entity is not "
                 "established here, so an entity is not "
                 "evidence the user created or confirmed it. Columns are a union across "
                 "entity types, so a person entity leaves the software and place columns "
                 "blank and the reverse. Rows of the expired_stable_graph table are read "
                 "alongside stable_graph and marked Yes in the Expired column. What moves "
                 "an entry into that table is not established, and a subject present in "
                 "both tables is listed once from each. The "
                 "IntelligencePlatform graph databases and the ontology-code resolution "
                 "were described by 0x11 Forensics and Consulting, 'That is one smart "
                 "Apple', https://0x11forensicssc.com/f/that-is-one-smart-apple, "
                 "2026-07-21.",
        "paths": (
            '*/mobile/Library/IntelligencePlatform/graph.db*',
            '*/mobile/Library/IntelligencePlatform/ontology.db*'),
        "output_types": "all",
        "artifact_icon": "share-2",
        "sample_data": {
            "otto_ios17": "iOS 17.5.1 | 1322 rows",
            "dexter_ios18": "iOS 18.3.2 | 575 rows",
            "hc_ios26": "iOS 26.5 | 356 rows",
            "falken_ios26": "iOS 26 | 325 rows",
            "felix_ios17": "iOS 17.6.1 | 314 rows",
            "iphone12_ios18": "iOS 18.7 | 305 rows",
            "hc_ios18_7": "iOS 18.7.8 | 304 rows",
            "fsfull002_ios17": "iOS 17.1 | 268 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 252 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        },
    },
    "intelligencePlatformEvents": {
        "name": "Intelligence Platform Knowledge Graph - Events",
        "description": "Dated events held in the event graph of IntelligencePlatform "
                       "graph.db, with their imputed start "
                       "and end times, and for a location visit the referenced place "
                       "resolved to a name, address and coordinates.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-23",
        "last_update_date": "2026-09-23",
        "requirements": "none",
        "category": "Knowledge Graph",
        "notes": "Reads the event graph inside IntelligencePlatform/graph.db. On the "
                 "tested images the file was present on iOS 16 with no events and held "
                 "events on iOS 17 and later; earlier versions were not checked. Each "
                 "event is a reified group of triples sharing a "
                 "subject: its type, name, a location reference, and a compound date "
                 "carrying imputed start and end times. Imputed Start Time is the earliest "
                 "of the event's imputed start time and imputed occurrence date values and "
                 "Imputed End Time the latest imputed end time, each read as Cocoa "
                 "(2001-epoch) seconds; the raw "
                 "start-time and end-time objects are stored in a serialized form and are "
                 "not reported. Predicate and class codes "
                 "are resolved from the ontology.db shipped in the same folder. How the "
                 "system produces an event is not established here, so an event is not "
                 "evidence the user was present "
                 "or confirmed it. The location reference is reported as stored (an "
                 "'md:<id>' pointer whose number is the modeled place node's id) and is "
                 "also resolved here to that place's name, composed address, latitude and "
                 "longitude by reading the referenced node from the entity tables "
                 "(stable_graph, then expired_stable_graph). A location visit whose "
                 "reference resolves to a place with coordinates carries them and is "
                 "written to KML; calendar and other events "
                 "with no location leave the location columns blank. Confidence is the "
                 "highest confidence value among the event's rows, rounded to four places, "
                 "not a measurement made here, and can hold one "
                 "value across every event on a device that stored few of them. Rows of "
                 "the expired_event_graph table are read alongside event_graph and marked "
                 "Yes in the Expired column; what moves an event into that table is not "
                 "established. The IntelligencePlatform "
                 "graph "
                 "databases were described by 0x11 Forensics and Consulting, 'That is one "
                 "smart Apple', https://0x11forensicssc.com/f/that-is-one-smart-apple, "
                 "2026-07-21.",
        "paths": (
            '*/mobile/Library/IntelligencePlatform/graph.db*',
            '*/mobile/Library/IntelligencePlatform/ontology.db*'),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 1032 rows",
            "otto_ios17": "iOS 17.5.1 | 38 rows",
            "hc_ios26": "iOS 26.5 | 35 rows",
            "felix_ios17": "iOS 17.6.1 | 33 rows",
            "falken_ios26": "iOS 26 | 27 rows",
            "fsfull002_ios17": "iOS 17.1 | 24 rows",
            "iphone12_ios18": "iOS 18.7 | 7 rows",
            "hc_ios18_7": "iOS 18.7.8 | 5 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 2 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        },
    },
    "intelligencePlatformInteractions": {
        "name": "Intelligence Platform Knowledge Graph - Interactions",
        "description": "Entries of the interactions table of IntelligencePlatform "
                       "view.db, with the contact handle, app, direction and time. On "
                       "the seven corpora measured the rows are messages and calls plus "
                       "a smaller number of Media, Notebook and blank-domain entries "
                       "(61 of 4,241 rows).",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-23",
        "last_update_date": "2026-09-23",
        "requirements": "none",
        "category": "Knowledge Graph",
        "notes": "Reads the interactions table of "
                 "IntelligencePlatform/Artifacts/siri/remembers/view.db (it held rows on "
                 "tested images from iOS 17.5.1 to iOS 26). Each row is an entry of the "
                 "interactions table as stored, joined to the handle or handles the "
                 "interactionEntities table links to it; the query does not filter on "
                 "domain and the Domain column says what kind. On felix_ios17, otto_ios17, "
                 "dexter_ios18, hc_ios18_7, hc_ios26, cookbook_ios1751 and falken_ios26, "
                 "counted on 3 October 2026, 4,180 of 4,241 rows have the domain Messages "
                 "or Calls. The other 61 have the domain Media (43), Notebook (3) or a "
                 "blank domain (15), with interaction types such as INPlayMediaIntent and "
                 "INCreateNoteIntent. One row is emitted per interaction, with the handle "
                 "or handles "
                 "(more than one for a group message) in the Handles column. Domain, "
                 "interaction type, app bundle id, direction and duration are reported as "
                 "stored; direction is an integer whose meaning is not resolved here. These "
                 "are the graph's own record of interactions and can repeat what an app's "
                 "own database holds, and the cited author reports entries here for "
                 "messages and calls that appeared to have been deleted from the app; that "
                 "was not tested here. The store was described "
                 "by 0x11 Forensics and Consulting, 'That is one smart Apple', "
                 "https://0x11forensicssc.com/f/that-is-one-smart-apple, 2026-07-21.",
        "paths": (
            '*/mobile/Library/IntelligencePlatform/Artifacts/siri/remembers/view.db*',),
        "output_types": "standard",
        "artifact_icon": "message-square",
        "sample_data": {
            "otto_ios17": "iOS 17.5.1 | 2835 rows",
            "dexter_ios18": "iOS 18.3.2 | 952 rows",
            "falken_ios26": "iOS 26 | 253 rows",
            "hc_ios26": "iOS 26.5 | 122 rows",
            "felix_ios17": "iOS 17.6.1 | 37 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 27 rows",
            "hc_ios18_7": "iOS 18.7.8 | 15 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
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


def _first(values):
    """Return the first non-empty value as text, else ''."""
    for value in values:
        text = '' if value is None else str(value)
        if text:
            return text
    return ''


def _place_lookup(files_found, predicates):
    """Map each modeled node's subject id to its resolved (name, composed address,
    latitude, longitude), gathered from the live and expired entity tables. An event
    references its location by node id (object 'md:<id>'), so this turns that pointer
    into the place the graph modeled. The live stable_graph wins over the expired
    table when a node is in both."""
    lookup = {}
    for table_name in ("stable_graph", "expired_stable_graph"):
        rows, _ = _read_triples(files_found, table_name)
        for subject, ent in _group_by_subject(rows, predicates).items():
            number = _first(_part(ent, 'has address', 'sub thoroughfare'))
            street = _first(_part(ent, 'has address', 'full street address'))
            city = _first(_part(ent, 'has address', 'city'))
            region = _first(_part(ent, 'has address', 'administrative district'))
            postal = _first(_part(ent, 'has address', 'postal code'))
            name = _first(_part(ent, 'has address', 'name'))
            lat, lon = _coords(ent)
            line1 = ' '.join(p for p in (number, street) if p)
            region_zip = ' '.join(p for p in (region, postal) if p)
            address = ', '.join(p for p in (line1, city, region_zip) if p)
            if subject not in lookup and (name or address or lat or lon):
                lookup[subject] = (name, address, lat, lon)
    return lookup


def _resolve_location(ent, places):
    """Resolve an event's location reference ('md:<id>') to the modeled place's
    (name, address, latitude, longitude). Returns blanks when the event has no
    location or the reference does not resolve to a modeled node."""
    for ref in _part(ent, 'has location relationship', 'has location'):
        if isinstance(ref, str) and ref.startswith('md:'):
            try:
                node = int(ref[3:])
            except ValueError:
                continue
            if node in places:
                return places[node]
    return '', '', '', ''


@artifact_processor
def intelligencePlatformEntities(context):
    files_found = context.get_files_found()
    predicates, classes = _load_ontology(files_found)

    data_list = []
    source_path = ''
    # stable_graph holds live entities; expired_stable_graph holds entries the graph
    # has since retired. Both share the same schema and are reported together, tagged.
    for table_name, expired in (("stable_graph", "No"), ("expired_stable_graph", "Yes")):
        rows, graph_path = _read_triples(files_found, table_name)
        if graph_path and not source_path:
            source_path = context.get_relative_path(graph_path)
        for subject, ent in _group_by_subject(rows, predicates).items():
            identifiers = _join(
                _part(ent, 'identifier', 'username')
                + _part(ent, 'identifier', 'identifier id'))
            data_list.append((
                convert_cocoa_core_data_ts_to_utc(ent['timestamp']) if ent['timestamp'] else '',
                _join(classes.get(v, v) for v in _base(ent, 'is a')),
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
                expired,
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
        'Expired',
        'Entity ID')
    return data_headers, data_list, source_path


@artifact_processor
def intelligencePlatformEvents(context):
    files_found = context.get_files_found()
    predicates, classes = _load_ontology(files_found)
    places = _place_lookup(files_found, predicates)

    data_list = []
    source_path = ''
    # event_graph holds live events; expired_event_graph holds retired ones.
    for table_name, expired in (("event_graph", "No"), ("expired_event_graph", "Yes")):
        rows, graph_path = _read_triples(files_found, table_name)
        if graph_path and not source_path:
            source_path = context.get_relative_path(graph_path)
        for subject, ent in _group_by_subject(rows, predicates).items():
            starts = [_cocoa(v) for v in
                      _part(ent, 'has date', 'imputed start time')
                      + _part(ent, 'has date', 'imputed occurrence date')]
            ends = [_cocoa(v) for v in _part(ent, 'has date', 'imputed end time')]
            starts = [s for s in starts if s]
            ends = [e for e in ends if e]
            loc_name, loc_addr, loc_lat, loc_lon = _resolve_location(ent, places)
            data_list.append((
                min(starts) if starts else '',
                max(ends) if ends else '',
                _join(classes.get(v, v) for v in _base(ent, 'is a')),
                _join(_base(ent, 'name')),
                _join(_part(ent, 'has location relationship', 'has location')),
                loc_name,
                loc_addr,
                loc_lat,
                loc_lon,
                round(ent['confidence'], 4),
                expired,
                str(subject)))

    data_headers = (
        ('Imputed Start Time', 'datetime'),
        ('Imputed End Time', 'datetime'),
        'Event Type',
        'Name',
        'Location (as stored)',
        'Location Name',
        'Location Address',
        'Latitude',
        'Longitude',
        'Confidence',
        'Expired',
        'Event ID')
    return data_headers, data_list, source_path


@artifact_processor
def intelligencePlatformInteractions(context):
    files_found = context.get_files_found()
    view_path = get_file_path(files_found, "view.db")
    data_list = []
    source_path = context.get_relative_path(view_path) if view_path else ''
    if view_path and does_table_exist_in_db(view_path, "interactions"):
        db = open_sqlite_db_readonly(view_path)
        if db is not None:
            cur = db.cursor()
            # The person handle(s) for each interaction, joined through the reified
            # interactionEntities table. A group message carries more than one.
            handles = {}
            if does_table_exist_in_db(view_path, "interactionEntities") and \
                    does_table_exist_in_db(view_path, "entities"):
                for interaction_rowid, handle_id in cur.execute(
                        "select ie.interactionRowid, e.id from interactionEntities ie "
                        "join entities e on e.rowid = ie.entityRowid "
                        "where e.type = 'PersonHandle'"):
                    handles.setdefault(interaction_rowid, []).append(handle_id)
            for (rowid, iid, domain, itype, bundle, direction, start, duration) in \
                    cur.execute(
                        "select rowid, id, domain, type, bundleId, direction, "
                        "startDate, durationSeconds from interactions"):
                data_list.append((
                    convert_cocoa_core_data_ts_to_utc(start) if start else '',
                    domain,
                    itype,
                    direction,
                    bundle,
                    duration,
                    _join(handles.get(rowid, [])),
                    iid))
            db.close()

    data_headers = (
        ('Start Date', 'datetime'),
        'Domain',
        'Interaction Type',
        'Direction (as stored)',
        'App Bundle ID',
        'Duration (Seconds)',
        ('Handles', 'phonenumber'),
        'Interaction ID')
    return data_headers, data_list, source_path
