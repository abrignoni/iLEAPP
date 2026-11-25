__artifacts_v2__ = {
    "zillowRecentSearches": {
        "name": "Zillow - Recent Searches",
        "description": "Searches the Zillow app keeps in its ZRECENTSEARCH table, with the access "
                       "date, the search text and the other columns of each row.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Shopping & Marketplaces",
        "notes": "One row per row of ZRECENTSEARCH in the Zillow app's Core Data store, "
                 "Zillow.sqlite, in an app group container; a file of that name is read only when "
                 "it holds that table. The column meanings are not sourced from Zillow "
                 "documentation, so the column names are the only labels used here. Apart from "
                 "Access Date, values are reported as stored; a NULL, or a column this version of "
                 "the store lacks, shows as blank. Access Date is ZACCESSDATE read as Core Data "
                 "seconds since 2001 and shown in UTC, and a missing or non-positive value shows "
                 "as blank; what access it marks is not established. Of the three images run, only "
                 "wilkerson_iphone16_ios26 holds the store, and its 3 rows are the same with and "
                 "without the write-ahead log. There Subtitle and Surface ID are empty on every "
                 "row, Reverted Spellcheck held 0 on every row, and Search History String and "
                 "Search Key are equal on the 2 rows that hold them and both NULL on the third. "
                 "Type held 1 or 3; what the values mean is not established. The same store holds "
                 "ZLASTSEARCH (1 row), ZZFILTERMODEL (3 rows) and ZZSCHOOLFILTERS (1 row), which "
                 "are not read here; ZZSAVEDSEARCH is empty. hill_iphone15pro_ios26 and "
                 "iphone11_ios17 do not hold the store.",
        "paths": ('*/Containers/Shared/AppGroup/*/Zillow.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 3 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 0 rows, no Zillow store",
            "iphone11_ios17": "iOS 17.3 | 0 rows, no Zillow store",
        },
    }
}


from scripts.ilapfuncs import (artifact_processor, convert_cocoa_core_data_ts_to_utc,
                               does_table_exist_in_db, get_sqlite_db_records, is_sqlite_sidecar,
                               null_absent_columns)


def _utc(value):
    '''Core Data seconds since 2001 as UTC; a missing or non-positive value stays blank.'''
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        return ''
    return convert_cocoa_core_data_ts_to_utc(value)


@artifact_processor
def zillowRecentSearches(context):
    data_headers = (('Access Date', 'datetime'), 'Search Text', 'Normalized Search Text',
                    'Subtitle', 'Region ID', 'Search History String', 'Search Key',
                    'Type (as stored)', 'Reverted Spellcheck (as stored)', 'Surface ID', 'Row ID')
    data_list, sources = [], []
    for found in sorted(str(path) for path in context.get_files_found()):
        if not found.endswith('Zillow.sqlite') or is_sqlite_sidecar(found):
            continue
        if not does_table_exist_in_db(found, 'ZRECENTSEARCH'):
            continue
        sources.append(found)
        query = null_absent_columns(found, '''
            SELECT ZACCESSDATE, ZSEARCHTEXT, ZNORMALIZEDSEARCHTEXT, ZSUBTITLE, ZREGIONID,
                   ZSEARCHHISTORYSTRING, ZSEARCHKEY, ZTYPE, ZISREVERTEDSPELLCHECK, ZSURFACEID,
                   Z_PK
            FROM ZRECENTSEARCH
            ORDER BY ZACCESSDATE, Z_PK
        ''')
        for row in get_sqlite_db_records(found, query):
            data_list.append((_utc(row[0]),) + tuple('' if value is None else value
                                                      for value in row[1:]))
    return data_headers, data_list, '\n'.join(sources)
