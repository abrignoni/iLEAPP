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
                 "ZMAPITEMIDENTIFIER and ZLOCREFERENCEFRAME of ZRTVEHICLEEVENTMO. The ZRTVEHICLEMO "
                 "table in the same file is reported by Routined Vehicles (Local.sqlite). "
                 "Reference: Ian Whiffin, "
                 "'Locations, Locations, Locations', https://doubleblak.com/blogPost.php?k=Locations",
        "paths": ('*/Library/Caches/com.apple.routined/Local.sqlite*',),
        "output_types": ["html", "tsv", "lava", "kml", "timeline"],
        "artifact_icon": "car",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 7 rows (1 event, 6 history)",
            "dexter_ios18": "iOS 18.3.2 | 16 rows (1 event, 15 history)",
            "hc_ios17_2": "iOS 17.2.1 | 33 rows (1 event, 32 history)",
            "iphone11_ios17": "iOS 17.3 | 1 row (1 event, 0 history)",
            "abe_ios16": "iOS 16.5 | 124 rows (1 event, 123 history)",
            "hickman_ios15": "iOS 15.3.1 | 15 rows (0 event, 15 history)",
            "hickman_ios14": "iOS 14.3 | 52 rows (0 event, 52 history)",
            "hickman_ios13": "iOS 13.3.1 | 59 rows (1 event, 58 history)",
        }
    },
    "routinedVehicles": {
        "name": "Routined Vehicles (Local.sqlite)",
        "description": "Rows of ZRTVEHICLEMO in the routined Local.sqlite: start and end times "
                       "with the vehicle name, vehicle model name and Bluetooth address as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-14",
        "last_update_date": "2026-10-14",
        "requirements": "none",
        "category": "Locations",
        "notes": "Times are Cocoa (Core Data) seconds converted to UTC; zero or negative "
                 "times are left empty. The columns follow the RTVehicleMO entity (startDate, "
                 "endDate, vehicleName, vehicleModelName, bluetoothAddress) of the CoreRoutine 8 "
                 "Core Data model, read from the CoreRoutine framework on macOS 27; the iOS model was "
                 "not read. No source establishes what starts or ends a row's interval. The times "
                 "are shown at whole-second precision (the stored values carry fractions of a "
                 "second) and do not by themselves establish a connection to, or presence in, a "
                 "vehicle. Rows were found on hc_ios18_7 (12), dexter_ios18 (1) and "
                 "iphone11_ios17 (1). Vehicle Model Name and Bluetooth Address held no value on any "
                 "of those 14 rows, and on hc_ios18_7 Vehicle Name held one value on all 12. The "
                 "table is absent on the eight iOS 13.3.1 to 16.5.1 images checked and present on "
                 "all 14 iOS 17.1 to 26.5.2 images checked. On hc_ios18_7 and iphone11_ios17 the Vehicle Name equals the Vehicle "
                 "Identifier of the one ZRTVEHICLEEVENTMO row in Routined Vehicle Events "
                 "(Local.sqlite), and that event's stored time is within 0.5 seconds of a row's "
                 "stored End DateTime (the report shows whole seconds, so the two can appear one "
                 "second apart); on dexter_ios18 the two values differ and the nearest End DateTime is "
                 "about 9 days from the event. "
                 "This artifact does not join the two. On dexter_ios18 and iphone11_ios17 the rows "
                 "differ with and without the -wal file, so the database is read with its sidecars.",
        "paths": ('*/Library/Caches/com.apple.routined/Local.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "car",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 12 rows",
            "dexter_ios18": "iOS 18.3.2 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows (table absent)",
            "abe_ios16": "iOS 16.5 | 0 rows (table absent)",
            "felix23_ios16": "iOS 16.5 | 0 rows (table absent)",
            "magnet_ios16": "iOS 16.1.1 | 0 rows (table absent)",
            "hickman_ios15": "iOS 15.3.1 | 0 rows (table absent)",
            "jess_ios15": "iOS 15.0.2 | 0 rows (table absent)",
            "hickman_ios14": "iOS 14.3 | 0 rows (table absent)",
            "hickman_ios13": "iOS 13.3.1 | 0 rows (table absent)",
            "ctf2020_ios12": "iOS 12.4 | 0 rows (Local.sqlite is not a database)",
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


@artifact_processor
def routinedVehicles(context):
    data_headers = (('Start DateTime', 'datetime'), ('End DateTime', 'datetime'), 'Vehicle Name',
                    'Vehicle Model Name', 'Bluetooth Address')
    data_list = []
    sources = [str(f) for f in context.get_files_found() if str(f).endswith('.sqlite')]
    for db in sources:
        if not does_table_exist_in_db(db, 'ZRTVEHICLEMO'):
            continue
        rows = get_sqlite_db_records(db, '''
            SELECT ZSTARTDATE, ZENDDATE, ZVEHICLENAME, ZVEHICLEMODELNAME, ZBLUETOOTHADDRESS
            FROM ZRTVEHICLEMO
            ORDER BY ZSTARTDATE
        ''')
        for r in rows:
            data_list.append((_utc(r[0]), _utc(r[1]), r[2], r[3], r[4]))
    return data_headers, data_list, '\n'.join(sources)
