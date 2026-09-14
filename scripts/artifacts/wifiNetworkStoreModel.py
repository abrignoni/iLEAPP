# The first version of this module credited its queries to work Heather Mahalik and Jared Barnhart
# presented at the SANS DFIR Summit 2022, "Building a Pattern of Life - Leveraging Location and
# Health Data" (https://for585.com/dfirsummit22). The queries below follow the relationships
# defined in WiFiNetworkStoreModel.momd, the Core Data model the tested images carry.
__artifacts_v2__ = {
    "get_wifiNetworkStoreModel": {
        "name": "WiFi Network Store - Networks",
        "description": "Network records from the WiFiNetworkStoreModel store, with counts of the "
                       "geotag records linked to each",
        "author": "@KevinPagano, @AlexisBrignoni, Claude",
        "creation_date": "2022-08-23",
        "last_update_date": "2026-09-12",
        "requirements": "none",
        "category": "Network",
        "notes": (
            "One row per ZNETWORK record in each WiFiNetworkStoreModel.sqlite the declared paths "
            "match, read with its write-ahead log when one is present; a database the query "
            "cannot read is logged and skipped. Source File names the database a row came from. "
            "Entity is the Core Data entity name Z_PRIMARYKEY gives for the row's Z_ENT, and was "
            "RootNetwork on every tested row. The authFlag (as stored) column carries the integer "
            "unchanged, because nothing in the store documents its values. Geotags via "
            "higherBandNetwork and Geotags via lowerBandNetwork count the ZGEOTAG records whose "
            "relationship of that name holds this record's Z_PK. Those relationships are defined "
            "in the WiFiNetworkStoreModel Core Data model found on each image that held the store "
            "(usr/sbin/WiFiNetworkStoreModel.momd on iOS 12.4 and 13.3.1, "
            "System/Library/PrivateFrameworks/MobileWiFi.framework/WiFiNetworkStoreModel.momd on "
            "iOS 14.3), and each tested store's Z_METADATA version hashes match that model's "
            "current version. Earlier versions of this artifact were named Wifi Known Networks and "
            "reported beside each network the geotag sharing its Z_PK, a pairing the store does "
            "not record; WiFi Network Store - Geotags now reports geotags through the "
            "relationships the store does record. An SSID in this store need not appear among the "
            "same device's known networks: 1 of 7 on the iOS 12.4 image and 1 of 2 on the iOS "
            "13.3.1 image were absent from the List of known networks in com.apple.wifi.plist, "
            "while the one SSID on the iOS 14.3 image was present in "
            "com.apple.wifi.known-networks.plist. The model's BlacklistedNetwork entity "
            "(blacklistDate, expireDate, bssid, fenceSize, location) held no record in any tested "
            "store, and those attributes are not reported. The Score records linked to the "
            "networks are not reported: switchedToCount and switchedAwayFromCount held 0 on all "
            "10 tested Score records, isLongTermNetwork held no value on any, and isMoving, "
            "isOmniPresent and isTCPGood held at most one distinct value in each tested store, "
            "with meanings the store does not document. On the iOS 13.3.1 image both network "
            "records existed only in the write-ahead log, on the iOS 12.4 image the log alone held "
            "1 of the 7, and on the iOS 14.3 image the database file read without its log held a "
            "network record whose Z_PK differs from the reported one. Of 26 iOS extractions "
            "checked, the store was present on three (iOS 12.4, 13.3.1 and 14.3) and absent from "
            "the rest, including iOS 15.3.1 and 26.5.2 images. None of the 26 carried it under "
            "com.apple.wifianalyticsd, so that declared path is unexercised."
        ),
        "paths": (
            '*/Library/Application Support/WiFiNetworkStoreModel.sqlite*',
            '*/Library/Application Support/com.apple.wifianalyticsd/WiFiNetworkStoreModel.sqlite*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "wifi",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 7 rows",
            "hickman_ios13": "iOS 13.3.1 | 2 rows",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "hickman_ios15": "iOS 15.3.1 | 0 rows, store absent",
            "hc_ios26": "iOS 26.5.2 | 0 rows, store absent",
        }
    },
    "wifiNetworkStoreModelGeotags": {
        "name": "WiFi Network Store - Geotags",
        "description": "Geotag records from the WiFiNetworkStoreModel store, with the SSIDs of the "
                       "network records they are linked to",
        "author": "@KevinPagano, @AlexisBrignoni, Claude",
        "creation_date": "2026-09-12",
        "last_update_date": "2026-09-12",
        "requirements": "none",
        "category": "Network",
        "notes": (
            "One row per ZGEOTAG record in each WiFiNetworkStoreModel.sqlite the declared paths "
            "match, read with its write-ahead log when one is present; a database the query "
            "cannot read is logged and skipped. Source File names the database a row came from. "
            "Geotag Date is the record's date attribute, a Core Data date read as seconds since "
            "2001-01-01 UTC; nothing in the store says what event it marks. Latitude, Longitude "
            "and BSSID are reported as stored, and the GeoTag entity defines no accuracy "
            "attribute. The two SSID columns follow the geotag's to-one relationships "
            "higherBandNetwork and lowerBandNetwork, which the model defines as pointing at a "
            "RootNetwork record and the store keeps as that record's Z_PK in ZHIGHERBANDNETWORK "
            "and ZLOWERBANDNETWORK. The two network Record ID columns report those stored values "
            "and match Record ID in WiFi Network Store - Networks for the same Source File. The "
            "relationship names are reported as the model writes them; nothing in the store "
            "defines a band. The model is WiFiNetworkStoreModel.momd, found on each image that "
            "held the store, and each tested store's Z_METADATA version hashes match its current "
            "version. No tested geotag held both links, and 8 of the 21 on the iOS 12.4 image held "
            "neither; those rows are reported with the network columns blank. As a cross-check on "
            "the tested images, 14 of the 18 geotags holding a link had a BSSID listed among the "
            "same device's known networks (com.apple.wifi.plist on iOS 12.4 and 13.3.1, "
            "com.apple.wifi.known-networks.plist on iOS 14.3), all 14 under the SSID the link "
            "names. Of those, the 12 with a channel recorded there showed channel 32 or above for "
            "the 5 linked through higherBandNetwork and channel 14 or below for the 7 linked "
            "through lowerBandNetwork. Earlier versions of Wifi Known Networks, now WiFi Network "
            "Store - Networks, paired each network with the geotag sharing its Z_PK, which the "
            "store does not record as a relationship, and read ZHIGHERBANDNETWORK and "
            "ZLOWERBANDNETWORK as 5 GHz and 2.4 GHz flags; on the three images that held the "
            "store, 1 of the 9 pairings that join produced matched a recorded link. The model on "
            "the iOS 13.3.1 and 14.3 images adds taggedCount, which held 0 on all 5 geotags there "
            "and is not reported. On the iOS 13.3.1 image all 3 geotags existed only in the "
            "write-ahead log, on the iOS 12.4 image the log alone held 4 of the 21, and on the iOS "
            "14.3 image the database file read without its log held 2 geotag records whose Z_PK "
            "values differ from the 2 reported. Of 26 iOS extractions checked, the store was "
            "present on three (iOS 12.4, 13.3.1 and 14.3) and absent from the rest, including iOS "
            "15.3.1 and 26.5.2 images. None of the 26 carried it under com.apple.wifianalyticsd, "
            "so that declared path is unexercised."
        ),
        "paths": (
            '*/Library/Application Support/WiFiNetworkStoreModel.sqlite*',
            '*/Library/Application Support/com.apple.wifianalyticsd/WiFiNetworkStoreModel.sqlite*',
        ),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 21 rows",
            "hickman_ios13": "iOS 13.3.1 | 3 rows",
            "hickman_ios14": "iOS 14.3 | 2 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows, store absent",
            "hc_ios26": "iOS 26.5.2 | 0 rows, store absent",
        }
    }
}

import os
import sqlite3

from scripts.ilapfuncs import (artifact_processor, convert_cocoa_core_data_ts_to_utc, logfunc,
                               open_sqlite_db_readonly)

STORE_NAME = 'WiFiNetworkStoreModel.sqlite'

NETWORKS_QUERY = '''
    SELECT
        ZNETWORK.Z_PK,
        Z_PRIMARYKEY.Z_NAME,
        ZNETWORK.ZSSID,
        ZNETWORK.ZAUTHFLAG,
        (SELECT COUNT(*) FROM ZGEOTAG WHERE ZGEOTAG.ZHIGHERBANDNETWORK = ZNETWORK.Z_PK),
        (SELECT COUNT(*) FROM ZGEOTAG WHERE ZGEOTAG.ZLOWERBANDNETWORK = ZNETWORK.Z_PK)
    FROM ZNETWORK
    LEFT JOIN Z_PRIMARYKEY ON Z_PRIMARYKEY.Z_ENT = ZNETWORK.Z_ENT
    ORDER BY ZNETWORK.Z_PK
'''

# ZHIGHERBANDNETWORK and ZLOWERBANDNETWORK hold the Z_PK of the RootNetwork record each
# relationship names, so the joins follow a link the store records.
GEOTAGS_QUERY = '''
    SELECT
        ZGEOTAG.ZDATE,
        ZGEOTAG.ZLATITUDE,
        ZGEOTAG.ZLONGITUDE,
        ZGEOTAG.ZBSSID,
        higher_band.ZSSID,
        lower_band.ZSSID,
        ZGEOTAG.Z_PK,
        ZGEOTAG.ZHIGHERBANDNETWORK,
        ZGEOTAG.ZLOWERBANDNETWORK
    FROM ZGEOTAG
    LEFT JOIN ZNETWORK AS higher_band ON higher_band.Z_PK = ZGEOTAG.ZHIGHERBANDNETWORK
    LEFT JOIN ZNETWORK AS lower_band ON lower_band.Z_PK = ZGEOTAG.ZLOWERBANDNETWORK
    ORDER BY ZGEOTAG.ZDATE DESC
'''


def _matched_stores(context):
    '''Every matched store database once, in a stable order. The sidecars are read through it.'''
    return sorted({str(path) for path in context.get_files_found()
                   if os.path.basename(str(path)) == STORE_NAME})


def _query_store(path, query):
    '''Rows of query from one store, or None when the store cannot be read.'''
    db = open_sqlite_db_readonly(path)
    if not db:
        return None
    try:
        return db.execute(query).fetchall()
    except sqlite3.Error as ex:
        logfunc(f'Could not read {STORE_NAME}: {ex}')
        return None
    finally:
        db.close()


@artifact_processor
def get_wifiNetworkStoreModel(context):
    data_headers = (
        'Record ID',
        'Entity',
        'SSID',
        'authFlag (as stored)',
        'Geotags via higherBandNetwork',
        'Geotags via lowerBandNetwork',
        'Source File',
    )
    data_list = []
    source_paths = []
    for store in _matched_stores(context):
        rows = _query_store(store, NETWORKS_QUERY)
        if rows is None:
            continue
        source_paths.append(store)
        source_file = context.get_relative_path(store)
        data_list.extend((*row, source_file) for row in rows)
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def wifiNetworkStoreModelGeotags(context):
    data_headers = (
        ('Geotag Date', 'datetime'),
        'Latitude',
        'Longitude',
        'BSSID',
        'higherBandNetwork SSID',
        'lowerBandNetwork SSID',
        'Geotag Record ID',
        'higherBandNetwork Record ID',
        'lowerBandNetwork Record ID',
        'Source File',
    )
    data_list = []
    source_paths = []
    for store in _matched_stores(context):
        rows = _query_store(store, GEOTAGS_QUERY)
        if rows is None:
            continue
        source_paths.append(store)
        source_file = context.get_relative_path(store)
        for row in rows:
            data_list.append((convert_cocoa_core_data_ts_to_utc(row[0]), *row[1:], source_file))
    return data_headers, data_list, '\n'.join(source_paths)
