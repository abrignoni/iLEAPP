__artifacts_v2__ = {
    "routinedParkedCar": {
        "name": "Routined Vehicle Events (Local.sqlite)",
        "description": "Rows of ZRTVEHICLEEVENTMO and ZRTVEHICLEEVENTHISTORYMO in the routined "
                       "Local.sqlite: the event and location times, coordinates and uncertainty of "
                       "each vehicle event, with the identifier, vehicle identifier, notes and the "
                       "user-set and usual location values as stored.",
        "author": "Heather Charpentier, Claude",
        "creation_date": "2026-10-14",
        "last_update_date": "2026-10-14",
        "requirements": "none",
        "category": "Locations",
        "notes": "Times are Cocoa (Core Data) seconds converted to UTC. Both tables are reported "
                 "as stored and named in the Table column; rows are not merged. On hc_ios18_7 "
                 "ZRTVEHICLEEVENTHISTORYMO has no vehicle identifier, notes, user-set, "
                 "usual-location or location-quality columns, so those are empty on its rows. "
                 "Checked against the hc_ios18_7 extraction (iPhone XS, iOS 18.7.8): the times and "
                 "coordinates of every row matched a second reader of the same file (MLEAPP). "
                 "Observed on hc_ios18_7 (iOS 18.7.8): 1 "
                 "event row and 6 history rows carrying 3 distinct identifiers; 4 history rows share "
                 "the event row's identifier, so an identifier can repeat across rows. In Whiffin's "
                 "2020 tests an event was created after the engine was turned off and he walked "
                 "away with the phone, and none after Bluetooth was turned off (on the phone or the "
                 "car stereo) while in motion or after the phone was left in the parked car for "
                 "about 25 minutes; a later update records park events without leaving the car and "
                 "says this hypothesis may be incorrect. This artifact reports the rows and does "
                 "not establish that a vehicle was parked or where. Not covered: ZPHOTODATA, "
                 "ZMAPITEMIDENTIFIER and ZLOCREFERENCEFRAME of ZRTVEHICLEEVENTMO, and the "
                 "ZRTVEHICLEMO table. Reference: Ian Whiffin, "
                 "'Locations, Locations, Locations', https://doubleblak.com/blogPost.php?k=Locations",
        "paths": ('*/Library/Caches/com.apple.routined/Local.sqlite*',),
        "output_types": ["html", "tsv", "lava", "kml", "timeline"],
        "artifact_icon": "car",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 7 rows (1 event, 6 history)",
        }
    }
}

from scripts.ilapfuncs import (artifact_processor, convert_cocoa_core_data_ts_to_utc,
                               does_table_exist_in_db, get_sqlite_db_records, null_absent_columns)


def _utc(cocoa):
    """Cocoa seconds to UTC; None for a missing or non-positive value."""
    return convert_cocoa_core_data_ts_to_utc(cocoa) if cocoa is not None and cocoa > 0 else None


@artifact_processor
def routinedParkedCar(context):
    data_headers = (('Event DateTime', 'datetime'), ('Location DateTime', 'datetime'),
                    'Latitude', 'Longitude', 'Uncertainty (as stored)', 'Identifier',
                    'Vehicle Identifier', 'Notes', 'User Set Location (as stored)',
                    'Usual Location (as stored)', 'Location Quality (as stored)', 'Table')
    data_list = []
    sources = [str(f) for f in context.get_files_found() if str(f).endswith('.sqlite')]
    for db in sources:
        for table in ('ZRTVEHICLEEVENTMO', 'ZRTVEHICLEEVENTHISTORYMO'):
            if not does_table_exist_in_db(db, table):
                continue
            rows = get_sqlite_db_records(db, null_absent_columns(db, f'''
                SELECT ZDATE, ZLOCDATE, ZLOCLATITUDE, ZLOCLONGITUDE, ZLOCUNCERTAINTY, ZIDENTIFIER,
                       ZVEHICLEIDENTIFIER, ZNOTES, ZUSERSETLOCATION, ZUSUALLOCATION,
                       ZLOCATIONQUALITY
                FROM {table}
                ORDER BY ZDATE
            '''))
            for r in rows:
                data_list.append((_utc(r[0]), _utc(r[1]), r[2], r[3], r[4], r[5], r[6], r[7],
                                  r[8], r[9], r[10], table))
    return data_headers, data_list, '\n'.join(sources)
