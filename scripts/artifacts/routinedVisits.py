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
                 "Latitude and longitude are reported as stored. Observed on the eight images in "
                 "sample_data (iOS 17.3 to 26.5.2): 195 of 381 rows are ZTYPE 1, every ZTYPE 1 row "
                 "has no exit time and every ZTYPE 3 row has one. On hc_ios18_7, 19 of the 26 "
                 "ZTYPE 1 rows share their entry time with a ZTYPE 3 row; the artifact does not "
                 "establish whether such pairs describe one stay. Rows are not merged. Location "
                 "DateTime is empty on 373 of the 381 rows. Not covered: the ZPLACEINFERENCE* "
                 "columns (place type, user type, confidence and map item identifier values), "
                 "which this artifact does not report or resolve. Background on the routined "
                 "Cache.sqlite: Ian Whiffin, 'Locations, Locations, Locations', "
                 "https://doubleblak.com/blogPost.php?k=Locations",
        "paths": ('*/Library/Caches/com.apple.routined/Cache.sqlite*',),
        "output_types": ["html", "tsv", "lava", "kml", "timeline"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 79 rows",
            "felix_ios17": "iOS 17.6.1 | 2 rows",
            "hc_ios18_7": "iOS 18.7.8 | 50 rows",
            "hc_ios26": "iOS 26.5.2 | 8 rows",
            "iphone11_ios17": "iOS 17.3 | 111 rows",
            "iphone12_ios18": "iOS 18.7 | 26 rows",
            "iphone14plus_ios18": "iOS 18.0 | 4 rows",
            "otto_ios17": "iOS 17.5.1 | 101 rows",
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
                 "appears with those columns empty. The Device columns report the ZRTDEVICEMO row "
                 "the visit's ZDEVICE points to, as stored; this artifact does not establish which "
                 "device recorded a visit. Observed on the images in sample_data: on dexter_ios18, "
                 "felix_ios17, otto_ios17 and hc_ios26 the visits point to more than one device "
                 "row, with Device Class iPad on dexter_ios18 and Mac14,12 on felix_ios17; Device "
                 "Name and Custom Label held no value on any of the eight images. Many rows repeat a visit "
                 "that Apple Maps Significant Locations Visits reports from "
                 "ZRTLEARNEDLOCATIONOFINTERESTVISITMO: 12 of 12 rows on hc_ios18_7 and 45 of 70 on "
                 "felix_ios17 share an entry time with a row there. This artifact adds the place, "
                 "address and device joins and the rows with no such match. ZCONFIDENCE and "
                 "ZPLACECONFIDENCE are reported as stored. Not covered: the inbound / outbound "
                 "transition columns (ZINBOUND, ZOUTBOUND) and the finer-granularity map item "
                 "fields.",
        "paths": ('*/Library/Caches/com.apple.routined/Cloud-V2.sqlite*',),
        "output_types": ["html", "tsv", "lava", "kml", "timeline"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 245 rows",
            "felix_ios17": "iOS 17.6.1 | 70 rows",
            "hc_ios18_7": "iOS 18.7.8 | 12 rows",
            "hc_ios26": "iOS 26.5.2 | 40 rows",
            "iphone11_ios17": "iOS 17.3 | 168 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 3 rows",
            "otto_ios17": "iOS 17.5.1 | 302 rows",
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
                    'Postal Code', 'Country', 'Device Class (as stored)', 'Device Model (as stored)',
                    'Device Name',
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
                   D.ZDEVICECLASS, D.ZDEVICEMODEL, D.ZDEVICENAME,
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
                              r[12], r[13], r[14], r[15], r[16], r[17], r[18], r[19], r[20],
                              context.get_relative_path(db)))
    return data_headers, data_list, '\n'.join(sources)
