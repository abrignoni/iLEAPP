__artifacts_v2__ = {
    "biomeIntelligenceEntities": {
        "name": "Biome DB - Intelligence Platform Entities",
        "description": "Subject, predicate and object rows from the EntityCentricSubgraph table "
                       "of the IntelligencePlatform.Entity Biome database, reported as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-07-11",
        "requirements": "none",
        "category": "Biome",
        "notes": "The database is described, for iOS 26.5, in North Loop Consulting, 'Apple Did "
                 "Your Homework: Pre-Analyzed Data in Biome Databases', "
                 "https://northloopconsulting.com/blog/f/ready-sets-go. That article does not "
                 "cover the EntityCentricSubgraph table read here. On the three tested iOS 18 "
                 "images the database holds an EntityCentricSubgraph table of subject, predicate "
                 "and object values. The predicate codes are undocumented and are reported as "
                 "stored; the objects seen included names, bundle IDs, phone numbers and record "
                 "identifiers. The cited research describes per-entity tables (Person, Location, "
                 "FlightReservations and others) on iOS 26.5. This artifact does not read those "
                 "tables and reports no rows when EntityCentricSubgraph is absent. Only the first "
                 "matching database file is read.",
        "paths": ('*/Biome/databases/IntelligencePlatform.Entity/IntelligencePlatform.Entity.sqlite3*',),
        "output_types": "standard",
        "artifact_icon": "database",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 5123 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1685 rows",
            "iphone12_ios18": "iOS 18.7 | 1765 rows",
        },
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
