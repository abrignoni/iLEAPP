__artifacts_v2__ = {
    "biomeIntelligenceEntities": {
        "name": "Biome DB - Intelligence Platform Entities",
        "description": "Knowledge-graph entity records (contacts, apps, identifiers and their attributes) compiled "
                       "by Apple in the IntelligencePlatform.Entity Biome database.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-07-11",
        "requirements": "none",
        "category": "Biome",
        "notes": "Based on research by North Loop Consulting: https://northloopconsulting.com/blog/f/ready-sets-go. "
                 "iOS 18 stores subject/predicate/object triples in EntityCentricSubgraph (predicate codes are "
                 "undocumented; objects carry names, bundle IDs, phone numbers and record identifiers). Newer iOS "
                 "versions use per-entity tables (Person, Location, FlightReservations) not yet present in test data.",
        "paths": ('*/Biome/databases/IntelligencePlatform.Entity/IntelligencePlatform.Entity.sqlite3*',),
        "output_types": "standard",
        "artifact_icon": "database",
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, does_table_exist_in_db, logfunc

DB_BASENAME = 'IntelligencePlatform.Entity.sqlite3'


@artifact_processor
def biomeIntelligenceEntities(context):
    data_headers = ('Subject ID', 'Predicate', 'Relationship ID', 'Relationship Predicate', 'Object')
    data_list = []

    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith(DB_BASENAME) and not file_found.endswith('-fullRebuild.sqlite3'):
            source_path = file_found
            break
    if not source_path:
        return data_headers, data_list, ''

    if does_table_exist_in_db(source_path, 'EntityCentricSubgraph'):
        for row in get_sqlite_db_records(source_path, '''
                SELECT subject, predicate, relationshipId, relationshipPredicate, object
                FROM EntityCentricSubgraph'''):
            data_list.append((str(row[0]), row[1], row[2], row[3], row[4]))
    else:
        logfunc(f'No EntityCentricSubgraph table in {source_path} '
                '(schema differs on this iOS version)')

    return data_headers, data_list, source_path
