__artifacts_v2__ = {
    "routinedCacheVisits": {
        "name": "Routined Visits (Cache.sqlite)",
        "description": "Rows of ZRTVISITMO in the routined Cache.sqlite: the entry, exit, detection "
                       "and location times, coordinates and uncertainty of each visit record, with "
                       "the confidence, source and type values as stored.",
        "author": "Heather Charpentier, Claude",
        "creation_date": "2026-10-14",
        "last_update_date": "2026-10-14",
        "requirements": "none",
        "category": "Locations",
        "notes": "Times are Cocoa (Core Data) seconds converted to UTC. ZTYPE, ZSOURCE and "
                 "ZCONFIDENCE are reported as stored; no meaning is assigned to their values. "
                 "Checked against the hc_ios18_7 extraction (iPhone XS, iOS 18.7.8): the times and "
                 "coordinates of every row matched an independent reader (MLEAPP) of the same "
                 "files. "
                 "Observed on hc_ios18_7 (iOS 18.7.8): 50 rows, ZSOURCE 1 on every row; the 26 "
                 "ZTYPE 1 rows are exactly the 26 with no exit time and the 24 ZTYPE 3 rows are the "
                 "24 with one, and 19 of the ZTYPE 1 rows share their entry time with a ZTYPE 3 row, "
                 "so one stay can appear as two rows. Rows are not merged. Coordinates are the "
                 "visit's location fields, not a recorded fix of the device. Not covered: the "
                 "ZPLACEINFERENCE* columns, which hold map item identifiers this artifact does not "
                 "resolve. Reference: Ian Whiffin, 'Locations, Locations, Locations', "
                 "https://doubleblak.com/blogPost.php?k=Locations",
        "paths": ('*/Library/Caches/com.apple.routined/Cache.sqlite*',),
        "output_types": ["html", "tsv", "lava", "kml", "timeline"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 50 rows",
        }
    },
    "routinedCloudVisits": {
        "name": "Routined Learned Visits (Cloud-V2.sqlite)",
        "description": "Rows of ZRTLEARNEDVISITMO in the routined Cloud-V2.sqlite with entry, exit, "
                       "creation and expiration times, coordinates, uncertainty and altitude, joined "
                       "to the learned place, its map item name and category, its address, and the "
                       "device record named by ZDEVICE.",
        "author": "Heather Charpentier, Claude",
        "creation_date": "2026-10-14",
        "last_update_date": "2026-10-14",
        "requirements": "none",
        "category": "Locations",
        "notes": "Times are Cocoa (Core Data) seconds converted to UTC. The place, map item, "
                 "address and device are left-joined, so a visit with no matching row still "
                 "appears with those columns empty. Cloud-V2.sqlite carries CloudKit record "
                 "columns (ZCKRECORDID) and a device table; the Device columns report the "
                 "ZRTDEVICEMO row the visit points to, as stored; this artifact does not establish "
                 "which device recorded a visit. Checked against the hc_ios18_7 extraction (iPhone "
                 "XS, iOS 18.7.8): the times and coordinates of every row matched an independent "
                 "reader (MLEAPP) of the same files. Observed on hc_ios18_7 (iOS 18.7.8): 12 rows, every one joined to a place, map item and address, one device row with a "
                 "model and no name, and no custom place labels. ZCONFIDENCE and ZPLACECONFIDENCE "
                 "are reported as stored. Not covered: the inbound / outbound transition columns "
                 "(ZINBOUND, ZOUTBOUND) and the finer-granularity map item fields. Reference: Ian "
                 "Whiffin, 'Locations, Locations, Locations', "
                 "https://doubleblak.com/blogPost.php?k=Locations",
        "paths": ('*/Library/Caches/com.apple.routined/Cloud-V2.sqlite*',),
        "output_types": ["html", "tsv", "lava", "kml", "timeline"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 12 rows",
        }
    }
}

from scripts.ilapfuncs import (artifact_processor, convert_cocoa_core_data_ts_to_utc,
                               does_table_exist_in_db, get_sqlite_db_records, null_absent_columns)


def _sqlite_sources(files_found):
    """The database files themselves, not their -wal / -shm / -journal sidecars."""
    return [str(f) for f in files_found if str(f).endswith('.sqlite')]


def _utc(cocoa):
    """Cocoa seconds to UTC; None for a missing or non-positive value."""
    return convert_cocoa_core_data_ts_to_utc(cocoa) if cocoa is not None and cocoa > 0 else None


@artifact_processor
def routinedCacheVisits(context):
    data_headers = (('Entry DateTime', 'datetime'), ('Exit DateTime', 'datetime'),
                    ('Detection DateTime', 'datetime'), ('Location DateTime', 'datetime'),
                    'Latitude', 'Longitude', 'Uncertainty (as stored)', 'Confidence (as stored)',
                    'Data Point Count', 'Type (as stored)', 'Source (as stored)', 'Source File')
    data_list = []
    sources = _sqlite_sources(context.get_files_found())
    for db in sources:
        if not does_table_exist_in_db(db, 'ZRTVISITMO'):
            continue
        rows = get_sqlite_db_records(db, null_absent_columns(db, '''
            SELECT ZENTRYDATE, ZEXITDATE, ZDETECTIONDATE, ZLOCATIONDATE,
                   ZLOCATIONLATITUDE, ZLOCATIONLONGITUDE, ZLOCATIONUNCERTAINTY, ZCONFIDENCE,
                   ZDATAPOINTCOUNT, ZTYPE, ZSOURCE
            FROM ZRTVISITMO
            ORDER BY ZENTRYDATE
        '''))
        for r in rows:
            data_list.append((_utc(r[0]), _utc(r[1]), _utc(r[2]), _utc(r[3]),
                              r[4], r[5], r[6], r[7], r[8], r[9], r[10],
                              context.get_relative_path(db)))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def routinedCloudVisits(context):
    data_headers = (('Entry DateTime', 'datetime'), ('Exit DateTime', 'datetime'),
                    ('Created DateTime', 'datetime'), ('Expiration DateTime', 'datetime'),
                    'Latitude', 'Longitude', 'Uncertainty (as stored)', 'Altitude (as stored)',
                    'Place Name', 'Place Category', 'Custom Label', 'Street', 'City', 'State',
                    'Postal Code', 'Country', 'Device Model', 'Device Name',
                    'Confidence (as stored)', 'Place Confidence (as stored)', 'Source File')
    data_list = []
    sources = _sqlite_sources(context.get_files_found())
    for db in sources:
        if not does_table_exist_in_db(db, 'ZRTLEARNEDVISITMO'):
            continue
        rows = get_sqlite_db_records(db, null_absent_columns(db, '''
            SELECT V.ZENTRYDATE, V.ZEXITDATE, V.ZCREATIONDATE, V.ZEXPIRATIONDATE,
                   V.ZLOCATIONLATITUDE, V.ZLOCATIONLONGITUDE, V.ZLOCATIONUNCERTAINTY,
                   V.ZLOCATIONALTITUDE,
                   M.ZNAME, M.ZCATEGORY, P.ZCUSTOMLABEL,
                   TRIM(COALESCE(A.ZSUBTHOROUGHFARE, '') || ' ' || COALESCE(A.ZTHOROUGHFARE, '')),
                   A.ZLOCALITY, A.ZADMINISTRATIVEAREA, A.ZPOSTALCODE, A.ZCOUNTRY,
                   D.ZDEVICEMODEL, D.ZDEVICENAME,
                   V.ZCONFIDENCE, V.ZPLACECONFIDENCE
            FROM ZRTLEARNEDVISITMO V
            LEFT JOIN ZRTLEARNEDPLACEMO P ON P.Z_PK = V.ZPLACE
            LEFT JOIN ZRTMAPITEMMO M ON M.Z_PK = P.ZMAPITEM
            LEFT JOIN ZRTADDRESSMO A ON A.ZMAPITEM = M.Z_PK
            LEFT JOIN ZRTDEVICEMO D ON D.Z_PK = V.ZDEVICE
            ORDER BY V.ZENTRYDATE
        '''))
        for r in rows:
            street = r[11] or None
            data_list.append((_utc(r[0]), _utc(r[1]), _utc(r[2]), _utc(r[3]),
                              r[4], r[5], r[6], r[7], r[8], r[9], r[10], street,
                              r[12], r[13], r[14], r[15], r[16], r[17], r[18], r[19],
                              context.get_relative_path(db)))
    return data_headers, data_list, '\n'.join(sources)
