__artifacts_v2__ = {
    "screenTimeStoreSettings": {
        "name": "Screen Time Store - Settings",
        "description": "The store-level Screen Time flags held in RMAdminStore-Local.sqlite and "
                       "RMAdminStore-Cloud.sqlite (com.apple.remotemanagementd), with 0 and 1 shown as No and Yes.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Screen Time",
        "notes": "One row per ZSCREENTIMESETTINGS row of each store file. Screen Time Enabled, Cloud "
                 "Sync Enabled and Family Setup Complete are the stored 0/1 flags shown as No and "
                 "Yes; a NULL is left blank, which says the store holds no value, not that the "
                 "setting is off. Row Version is the Core Data optimistic-locking counter (Z_OPT) of "
                 "the row. In the five tested full file systems (iOS 26.2.1 to 26.5.2, iPhones) the "
                 "table held one row in the local store and none in the cloud store; Screen Time "
                 "Enabled was Yes on two and No on three, and Cloud Sync Enabled and Family Setup Complete were No on all five. On the corpus Cloud Sync Enabled was Yes on 10 of 22 stores and Family Setup Complete was blank on 16 (the column is absent on older stores), so neither column is uniform. The flags do not record when a setting changed (see Screen Time Store - "
                 "Change History) and are a different table from the per-device flags in Screen "
                 "Time Store - Users and Devices. The tables the store also holds for downtime "
                 "schedules, usage limits and app exceptions (ZDOWNTIME, ZDAILYSCHEDULE, "
                 "ZBLUEPRINTSCHEDULE, ZBLUEPRINTUSAGELIMIT, ZAPPEXCEPTION) were empty in every tested "
                 "store and are not read. No store with a managed child profile in force was available to the contributor. One corpus Organization Settings row holds Managed Yes; what that row describes is not established. On 22 corpus iOS extractions (iOS 12.4 to 26.5.2) the LAVA row count equalled an independent SQL count of the same rows in the Local and Cloud stores, taken on copies read with their -wal files where present; sample_data lists six of them.",
        "paths": ('*/mobile/Library/Application Support/com.apple.remotemanagementd/RMAdminStore-*.sqlite*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | iPhone | 1 row",
            "hickman_ios14": "iOS 14.3 | iPhone | 1 row",
            "jess_ios15": "iOS 15.0.2 | iPhone | 1 row",
            "felix_ios17": "iOS 17.6.1 | iPhone | 1 row",
            "dexter_ios18": "iOS 18.3.2 | iPhone | 1 row",
            "hc_ios26": "iOS 26.5.2 | iPhone | 1 row",
        },
    },
    "screenTimeStoreOrgSettings": {
        "name": "Screen Time Store - Organization Settings",
        "description": "The organization settings rows (communication policies, Communication Safety "
                       "flags, passcode presence) held in the remotemanagementd RMAdminStore databases.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Screen Time",
        "notes": "One row per ZCOREORGANIZATIONSETTINGS row of each store file. Zero and one in the "
                 "flag columns are shown as No and Yes; a NULL is left blank, which says the store "
                 "holds no value, not that the setting is off. Communication Policy, Communication "
                 "While Limited Policy and Contact Management State are shown as stored, because no "
                 "source that defines their values was found. App And Website Activity is the first non-NULL of the two ZISAPPANDWEBSITEACTIVITYENABLED columns, where the table carries them; older stores have neither and the column is blank. "
                 "Passcode Stored says whether any of the three passcode columns holds a value; the "
                 "value itself is deliberately never read into the report. Modification Date is a "
                 "Core Data date. In the five tested stores (iOS 26.2.1 to 26.5.2, iPhones) the table held one row in the local store (corpus stores hold one, two or eight rows); All Limits Enabled was Yes on all five, "
                 "the three integer columns and Needs To Set Passcode were 0 on all five, and "
                 "the passcode columns and Modification Date were NULL on all five, so Passcode Stored reads No and Modification Date is empty there. On the corpus Modification Date is filled on three stores and one store holds a passcode value, so Passcode Stored reads Yes there. Eye Relief Enabled "
                 "was empty on three of them, Share Web Usage and Managed on all five (on the corpus Managed holds No on 12 rows and Yes on one), and "
                 "Communication Safety Receiving Restricted and Sending Restricted on one. On two "
                 "further stores (iOS 26.6 and 26.6.2, iPhones) Communication Safety Sending "
                 "Restricted, Communication Safety Receiving Restricted and Eye Relief Enabled "
                 "held no value in the single row. How the columns read on a device with a Screen Time passcode or a child profile was not tested by the contributor; one corpus row holds a passcode value and one holds Managed Yes, and neither device's configuration is known. On 22 corpus iOS extractions (iOS 12.4 to 26.5.2) the LAVA row count equalled an independent SQL count of the same rows in the Local and Cloud stores, taken on copies read with their -wal files where present; sample_data lists six of them.",
        "paths": ('*/mobile/Library/Application Support/com.apple.remotemanagementd/RMAdminStore-*.sqlite*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | iPhone | 2 rows",
            "hickman_ios14": "iOS 14.3 | iPhone | 2 rows",
            "jess_ios15": "iOS 15.0.2 | iPhone | 1 row",
            "felix_ios17": "iOS 17.6.1 | iPhone | 2 rows",
            "dexter_ios18": "iOS 18.3.2 | iPhone | 1 row",
            "hc_ios26": "iOS 26.5.2 | iPhone | 1 row",
        },
    },
    "screenTimeStoreUsers": {
        "name": "Screen Time Store - Users and Devices",
        "description": "Users, devices and the per-device Screen Time state held in the "
                       "remotemanagementd RMAdminStore databases.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Screen Time",
        "notes": "One row per ZUSERDEVICESTATE row, joined to its user (ZCOREUSER, on ZUSER) and "
                 "device (ZCOREDEVICE, on ZDEVICE); a row whose user or device is missing is still "
                 "reported with those columns blank. Apple Account, DSID, Alt DSID, Given Name and "
                 "Family Name are the stored account fields. Family Member Type is the stored "
                 "string. Platform is the stored integer. Last Passcode Use, Passcode Entry Timeout "
                 "End and Last Family Check-in are Core Data dates (seconds since 2001-01-01 UTC), "
                 "blank where the store holds no value. Screen Time Enabled, Cloud Sync Enabled, "
                 "Management Enabled and Legacy Usage Disabled are the stored flags of the "
                 "user-device row; NULL is blank. In the five tested stores (iOS 26.2.1 to "
                 "26.5.2, iPhones) each held one user-device row whose user and device joined (corpus stores hold one to seven rows); "
                 "Apple Account was NULL on all five (filled on three corpus stores), DSID was present on all five (zero on one), "
                 "Alt DSID, Given Name and Family Name were present on four, Family Organizer was "
                 "Yes on one, Family Member Type was 'Unknown' and Platform was 2 on all five (the corpus also holds a second Family Member Type value and Platform values 1 and 4), Management Enabled was No on all five, and Last Passcode Use was "
                 "filled on one and Last Family Check-in on none, and Cloud Sync Enabled was empty "
                 "on one; the meaning of Platform "
                 "and of 'Unknown' was not established. The device blobs (ZDEVICEINFOPLIST, "
                 "ZCAPABILITIESPLIST) were NULL on every tested store and are not read. On 22 corpus iOS extractions (iOS 12.4 to 26.5.2) the LAVA row count equalled an independent SQL count of the same rows in the Local and Cloud stores, taken on copies read with their -wal files where present; sample_data lists six of them.",
        "paths": ('*/mobile/Library/Application Support/com.apple.remotemanagementd/RMAdminStore-*.sqlite*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "users",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | iPhone | 1 row",
            "hickman_ios14": "iOS 14.3 | iPhone | 3 rows",
            "jess_ios15": "iOS 15.0.2 | iPhone | 1 row",
            "felix_ios17": "iOS 17.6.1 | iPhone | 7 rows",
            "dexter_ios18": "iOS 18.3.2 | iPhone | 1 row",
            "hc_ios26": "iOS 26.5.2 | iPhone | 1 row",
        },
    },
    "screenTimeStoreBlueprints": {
        "name": "Screen Time Store - Blueprints and Configurations",
        "description": "Screen Time blueprints and the declarative configuration payloads stored "
                       "with them in the remotemanagementd RMAdminStore databases.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Screen Time",
        "notes": "One row per ZBLUEPRINTCONFIGURATION row, with the blueprint (ZBLUEPRINT) that owns "
                 "it; a blueprint with no configuration is reported on one row with the "
                 "configuration columns blank. Blueprint Identifier and Blueprint Type are the "
                 "stored ZIDENTIFIER and ZTYPE; Enabled, Tombstoned and Limit Enabled are the "
                 "stored flags (NULL blank). The configuration's ZPAYLOADPLIST is decoded with "
                 "plistlib: Declaration Type and Server Hash are its Type and ServerHash keys "
                 "(its Identifier key equalled Configuration Identifier on every tested row, so it "
                 "is not repeated), and Payload is its Payload key written "
                 "as JSON text (dates as ISO 8601, binary values as hexadecimal). A declaration "
                 "under a blueprint whose Enabled is No is shown but is not claimed to be in "
                 "force, and the store does not say here whether an Enabled blueprint is being "
                 "applied. A payload that does not decode leaves the two declaration columns "
                 "blank and Payload reads 'undecodable' with the byte length. Configuration Type and "
                 "Declaration Type are identical where the stored type is the full declaration "
                 "type. Store was Local on every tested row (the cloud stores held no rows), "
                 "Tombstoned was No and Limit Enabled was Yes on every tested row of the "
                 "store with four rows, and Expires and Minimum Installation Date were empty on "
                 "every tested row. In the five tested "
                 "stores (iOS 26.2.1 to 26.5.2, iPhones) every one of the five held an always-allowed-apps blueprint (Enabled Yes) with a com.apple.configuration.policy.application declaration (on the corpus 14 of 22 images hold one such blueprint and 8 hold none); a restrictions blueprint was present on three (Enabled Yes on one, "
                 "No on two, and with no configuration on the one where it was Yes), a "
                 "managed-user blueprint on one (Enabled No), and the other declaration types "
                 "seen were com.apple.configuration.application.store, "
                 "com.apple.configuration.system.icloud, "
                 "com.apple.configuration.system.dateandtime and "
                 "com.apple.configuration.policy.icloud.account, each on one store. Created was NULL on every tested blueprint and Modified was filled on all five; on the corpus Modified is blank on 8 of 14 rows because older stores lack the column. On 22 corpus iOS extractions (iOS 12.4 to 26.5.2) the LAVA row count equalled an independent SQL count of the same rows in the Local and Cloud stores, taken on copies read with their -wal files where present; sample_data lists six of them.",
        "paths": ('*/mobile/Library/Application Support/com.apple.remotemanagementd/RMAdminStore-*.sqlite*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "clipboard-list",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | iPhone | 0 rows",
            "hickman_ios14": "iOS 14.3 | iPhone | 1 row",
            "jess_ios15": "iOS 15.0.2 | iPhone | 1 row",
            "felix_ios17": "iOS 17.6.1 | iPhone | 1 row",
            "dexter_ios18": "iOS 18.3.2 | iPhone | 1 row",
            "hc_ios26": "iOS 26.5.2 | iPhone | 0 rows",
        },
    },
    "screenTimeStoreInstalledApps": {
        "name": "Screen Time Store - Installed Apps",
        "description": "Apps the Screen Time store lists for the device (ZINSTALLEDAPP in the "
                       "remotemanagementd RMAdminStore databases).",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Screen Time",
        "notes": "One row per ZINSTALLEDAPP row. Bundle Identifier, Display Name and Distributor ID "
                 "are the stored values; Installed Locally and Distributor Is Third Party are "
                 "stored flags; Adam ID, Version Identifier and Beta Version Identifier are shown "
                 "as stored (zero where the store holds zero). In the tested stores (iOS 26.2.1 to "
                 "26.5.2, iPhones) two held rows, 336 and 21, Display Name was NULL on every one of those rows (on the corpus it is filled on 465 of 1,831 rows across four stores), Installed Locally was Yes on every row (No on 747 of 1,831 corpus rows), and Distributor ID was filled on 72 of the 336 and on 1 of the "
                 "21. Store was Local, Distributor Is Third Party was No and Beta Version Identifier was 0 on every tested row; on the corpus both columns are blank where older stores lack them, and no Yes or non-zero value was seen. "
                 "The table is a list that Screen Time keeps. It is not a record of when an "
                 "app was installed or removed, and an app missing from it is not shown to be "
                 "absent from the device; the other three tested stores held no rows, which is a "
                 "store state and not a statement about the apps on the phone. For rows the store "
                 "has since deleted see Screen Time Store - Deleted Rows. The icon blobs are not "
                 "read. On 22 corpus iOS extractions (iOS 12.4 to 26.5.2) the LAVA row count equalled an independent SQL count of the same rows in the Local and Cloud stores, taken on copies read with their -wal files where present; sample_data lists six of them.",
        "paths": ('*/mobile/Library/Application Support/com.apple.remotemanagementd/RMAdminStore-*.sqlite*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "apps",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | iPhone | 95 rows",
            "hickman_ios14": "iOS 14.3 | iPhone | 156 rows",
            "jess_ios15": "iOS 15.0.2 | iPhone | 53 rows",
            "felix_ios17": "iOS 17.6.1 | iPhone | 442 rows",
            "dexter_ios18": "iOS 18.3.2 | iPhone | 0 rows",
            "hc_ios26": "iOS 26.5.2 | iPhone | 0 rows",
        },
    },
    "screenTimeStoreUsage": {
        "name": "Screen Time Store - Usage",
        "description": "Usage blocks and the category, app, web domain, pickup and notification "
                       "tallies stored beneath them in the remotemanagementd RMAdminStore databases.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Screen Time",
        "notes": "Evidence tier: row counts data-proven on the corpus (see the last sentence); the reading of each column rests on the table schema. The usage tables (ZUSAGE, ZUSAGEBLOCK, ZUSAGECATEGORY, "
                 "ZUSAGETIMEDITEM, ZUSAGECOUNTEDITEM) exist in every tested store and their "
                 "columns were read from those schemas, but all five tested full file systems "
                 "(iOS 26.2.1 to 26.5.2, iPhones) held zero rows in all five tables, in the local and the cloud store; on the corpus the tables held rows on 15 of 22 images (iOS 12.4 to 17.6.1); the seven with none were one iOS 17.1.1 image and the six iOS 18 and 26 images. The persistent-history tables of three of them record the "
                 "creation and later deletion of usage rows (see Screen Time Store - Change "
                 "History), so rows may be written and removed again; The corpus shows rows left in these tables on 15 of 22 images; whether they are the device's own usage or a family member's is not established here, because the ZUSAGE user and device are not joined. A row is one tally of one usage block: Kind says whether "
                 "it comes from a category row (seconds per category), a timed item (seconds per "
                 "bundle identifier or web domain; its Category is the category row it points at, and "
                 "that row's block is the block shown) or a counted item (pickups and notifications "
                 "per bundle identifier). Block Start, First Pickup, Longest Session Start and End "
                 "and Last Event are Core Data dates. Duration is the block's "
                 "ZDURATIONINMINUTES. Usage Trusted is the stored ZUSAGETRUSTED flag. Pickups "
                 "Without App Usage is the block's ZNUMBEROFPICKUPSWITHOUTAPPLICATIONUSAGE. Usage "
                 "Row is the key of the block's parent ZUSAGE row, whose user and device are not "
                 "joined here. The meaning of the category identifiers is not defined. On 22 corpus iOS extractions (iOS 12.4 to 26.5.2) the LAVA row count equalled an independent SQL count of the same rows in the Local and Cloud stores, taken on copies read with their -wal files where present; sample_data lists six of them.",
        "paths": ('*/mobile/Library/Application Support/com.apple.remotemanagementd/RMAdminStore-*.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "chart-bar",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | iPhone | 753 rows",
            "hickman_ios14": "iOS 14.3 | iPhone | 1,993 rows",
            "jess_ios15": "iOS 15.0.2 | iPhone | 354 rows",
            "felix_ios17": "iOS 17.6.1 | iPhone | 746 rows",
            "dexter_ios18": "iOS 18.3.2 | iPhone | 0 rows",
            "hc_ios26": "iOS 26.5.2 | iPhone | 0 rows",
        },
    },
    "screenTimeStoreChanges": {
        "name": "Screen Time Store - Change History",
        "description": "Core Data persistent-history transactions kept in the remotemanagementd "
                       "RMAdminStore databases, with the author, bundle, context and the "
                       "number of rows each transaction inserted, updated and deleted.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Screen Time",
        "notes": "One row per ATRANSACTION row. Timestamp is ZTIMESTAMP as a Core Data date. Author, "
                 "Bundle ID, Context Name and Process (as stored) are the strings that the "
                 "transaction's ZAUTHORTS, ZBUNDLEIDTS, ZCONTEXTNAMETS and ZPROCESSIDTS point at "
                 "in ATRANSACTIONSTRING; the process column holds a process name in the tested "
                 "stores, and Author or Context Name are blank where the transaction has none. "
                 "Inserts, Updates and Deletes count the transaction's ACHANGE rows by "
                 "ZCHANGETYPE, read as the Core Data persistent history change types "
                 "(NSPersistentHistoryChangeType: insert 0, update 1, delete 2). Entities lists "
                 "the model entity names (Z_PRIMARYKEY.Z_NAME, on ZENTITY) the transaction's "
                 "changes touched. A transaction with no change rows is shown with zero counts. "
                 "Core Data can trim history, so the rows are the transactions the store still "
                 "holds. Four of the five tested stores (iOS 26.2.1 to 26.5.2, iPhones) held "
                 "history: 322, 375, 131 and 1 transactions, spanning 2025-07-02 to 2026-07-21 "
                 "across them. The bundle IDs seen were com.apple.ScreenTimeAgent, "
                 "com.apple.Preferences and com.apple.ScreenTimeWidgetApplication.ScreenTimeWidgetExtension, "
                 "and the context names STPersistLocalAppsOperation and cleanOrphanedDatabaseEntities. "
                 "Store was Local on every row of the five tested stores, whose cloud stores held no history; on the corpus 14 of 22 cloud stores hold history (354 transactions), so Store is not uniform. A row says that the named process saved a change to the store, not what the "
                 "user did. On the three larger stores most deletes were of usage entities "
                 "(UsageTimedItem, UsageCategory, UsageBlock, UsageCountedItem) and their inserts "
                 "were of the same entities, which fits the empty usage tables; the counts are of "
                 "rows, and the content of a deleted usage row is not kept. On 22 corpus iOS extractions (iOS 12.4 to 26.5.2) the LAVA row count equalled an independent SQL count of the same rows in the Local and Cloud stores, taken on copies read with their -wal files where present; sample_data lists six of them.",
        "paths": ('*/mobile/Library/Application Support/com.apple.remotemanagementd/RMAdminStore-*.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "history",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | iPhone | 1,193 rows",
            "hickman_ios14": "iOS 14.3 | iPhone | 979 rows",
            "jess_ios15": "iOS 15.0.2 | iPhone | 153 rows",
            "felix_ios17": "iOS 17.6.1 | iPhone | 7,208 rows",
            "dexter_ios18": "iOS 18.3.2 | iPhone | 1 row",
            "hc_ios26": "iOS 26.5.2 | iPhone | 5 rows",
        },
    },
    "screenTimeStoreDeletedRows": {
        "name": "Screen Time Store - Deleted Rows",
        "description": "Deleted-row entries from the Core Data persistent history of the "
                       "remotemanagementd RMAdminStore databases, with the values the history "
                       "kept for the deleted row.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Screen Time",
        "notes": "One row per ACHANGE row with ZCHANGETYPE 2 (delete in NSPersistentHistoryChangeType), "
                 "dated by its transaction. Entity is the model entity name (Z_PRIMARYKEY.Z_NAME, "
                 "on ZENTITY) and Entity Row ID is ZENTITYPK, the key the row had. Value 1 to "
                 "Value 4 are ZTOMBSTONE0 to ZTOMBSTONE3 as stored (text and integers as they are, "
                 "binary values as hexadecimal, blank where the history kept none); which "
                 "attribute each position holds is set by the store's data model, which is not "
                 "read here, so the positions are not named. In the tested stores (iOS 26.2.1 to "
                 "26.5.2, iPhones) the InstalledApp deletes held a bundle identifier in Value 1 on "
                 "every row: 158 deletes (90 distinct bundle identifiers) on two stores and 20 (17 distinct) on one. On the corpus that holds from iOS 14.3 on; on the iOS 12.4 and 13.3.1 stores Value 1 is a binary value shown as hexadecimal and Value 2 is text. The installed-apps list was empty on the two stores with 158 "
                 "deletes, so it does not show those apps, and a bundle identifier is repeated "
                 "across deletes, so one identifier can appear on several rows. Value 4 "
                 "of those rows began 'app:<bundle identifier>-uds:' followed by two further identifiers whose meaning is not established (on the iOS 12.4 and 13.3.1 corpus stores Value 4 is empty); Blueprint deletes held a 'bp:<identifier>' "
                 "string in Value 2. A delete entry shows that the history recorded the row's "
                 "removal; it does not say why the row was removed, and it is not evidence that "
                 "the app was uninstalled or that its entry was not recreated later. Usage entity "
                 "deletes (the large majority of rows) kept no values, so they are blank in "
                 "all four value columns. Core Data can trim history, so absence of a delete "
                 "entry does not mean a row was never removed. In the five tested stores Store, Bundle ID and Process held one value each on every delete row: Local, com.apple.ScreenTimeAgent and ScreenTimeAgent. On the corpus seven cloud stores also hold delete rows (1,390, of other entities, shown as stored), so Store is not uniform. On the iOS 26.6.2 store the four delete rows came "
                 "from one transaction and were deletes of Blueprint, BlueprintConfiguration, "
                 "LocalOrganization and LocalOrganizationSettings entities, so Timestamp and "
                 "Transaction Row held one value on all four rows and Value 3 had no value on any "
                 "of them; the contributor's iOS 26.6 and 26.5.2 stores held no delete rows (the corpus iOS 26.5.2 image holds one). On 22 corpus iOS extractions (iOS 12.4 to 26.5.2) the LAVA row count equalled an independent SQL count of the same rows in the Local and Cloud stores, taken on copies read with their -wal files where present; sample_data lists six of them.",
        "paths": ('*/mobile/Library/Application Support/com.apple.remotemanagementd/RMAdminStore-*.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "trash",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | iPhone | 4,658 rows",
            "hickman_ios14": "iOS 14.3 | iPhone | 7,292 rows",
            "jess_ios15": "iOS 15.0.2 | iPhone | 245 rows",
            "felix_ios17": "iOS 17.6.1 | iPhone | 98,412 rows",
            "dexter_ios18": "iOS 18.3.2 | iPhone | 0 rows",
            "hc_ios26": "iOS 26.5.2 | iPhone | 1 row",
        },
    },
}

import json
import os
import plistlib
from datetime import datetime
from xml.parsers.expat import ExpatError

from scripts.ilapfuncs import (
    artifact_processor,
    convert_cocoa_core_data_ts_to_utc,
    does_table_exist_in_db,
    get_sqlite_db_records,
    null_absent_columns,
)


def _stores(context):
    """The RMAdminStore databases found, as (store label, path), main database files only."""
    stores = []
    for path in context.get_files_found():
        name = os.path.basename(path)
        if name.startswith('RMAdminStore-') and name.endswith('.sqlite'):
            stores.append((name[len('RMAdminStore-'):-len('.sqlite')], path))
    return sorted(stores)


def _source(stores):
    return '\n'.join(path for _, path in stores)


def _time_first(headers, rows):
    """(headers, rows) with the datetime columns moved to the front, in their own order, so the
    event time leads and the other times follow it."""
    order = ([i for i, h in enumerate(headers) if isinstance(h, tuple) and h[1] == 'datetime']
             + [i for i, h in enumerate(headers) if not (isinstance(h, tuple) and h[1] == 'datetime')])
    return tuple(headers[i] for i in order), [tuple(row[i] for i in order) for row in rows]


def _flag(value):
    """A stored 0/1 flag as No/Yes; NULL stays blank; any other value is kept as stored."""
    if value is None:
        return ''
    if value in (0, 1):
        return 'Yes' if value == 1 else 'No'
    return value


def _date(value):
    """A Core Data date as UTC text; blank when NULL."""
    return convert_cocoa_core_data_ts_to_utc(value) if value is not None else ''


def _rows(path, table, query):
    """Rows of query, or [] when table is absent; absent columns read as NULL."""
    if not does_table_exist_in_db(path, table):
        return []
    return list(get_sqlite_db_records(path, null_absent_columns(path, query)))


def _json_default(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).hex()
    return str(value)


def _stored(value):
    """A tombstone value as stored: text and integers unchanged, binary as hexadecimal, NULL blank."""
    if value is None:
        return ''
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).hex()
    return value


@artifact_processor
def screenTimeStoreSettings(context):
    data_headers = (
        'Store', 'Row ID', 'Row Version', 'Screen Time Enabled', 'Cloud Sync Enabled',
        'Family Setup Complete')
    data_list = []
    stores = _stores(context)
    for label, path in stores:
        for row in _rows(path, 'ZSCREENTIMESETTINGS', '''
                SELECT Z_PK, Z_OPT, ZSCREENTIMEENABLED, ZCLOUDSYNCENABLED, ZFAMILYSETUPCOMPLETE
                FROM ZSCREENTIMESETTINGS ORDER BY Z_PK'''):
            data_list.append((label, row[0], row[1], _flag(row[2]), _flag(row[3]), _flag(row[4])))
    return _time_first(data_headers, data_list) + (_source(stores),)


@artifact_processor
def screenTimeStoreOrgSettings(context):
    data_headers = (
        'Store', 'Row ID', 'Row Version', ('Modification Date', 'datetime'), 'All Limits Enabled',
        'Communication Policy', 'Communication While Limited Policy', 'Contact Management State',
        'Communication Safety Analytics', 'Communication Safety Notification',
        'Communication Safety Receiving Restricted', 'Communication Safety Sending Restricted',
        'Eye Relief Enabled', 'Needs To Set Passcode', 'App And Website Activity',
        'Managed', 'Share Web Usage', 'Passcode Stored')
    data_list = []
    stores = _stores(context)
    for label, path in stores:
        # An absent column must stand alone in the select list for null_absent_columns to blank it,
        # so the two activity columns and the three passcode columns are selected one by one; the
        # passcode columns are reduced to 0/1 in SQL and no passcode text leaves the query.
        for row in _rows(path, 'ZCOREORGANIZATIONSETTINGS', '''
                SELECT Z_PK, Z_OPT, ZMODIFICATIONDATE, ZALLLIMITSENABLED, ZCOMMUNICATIONPOLICY,
                       ZCOMMUNICATIONWHILELIMITEDPOLICY, ZCONTACTMANAGEMENTSTATE,
                       ZISCOMMUNICATIONSAFETYANALYTICSENABLED, ZISCOMMUNICATIONSAFETYNOTIFICATIONENABLED,
                       ZISCOMMUNICATIONSAFETYRECEIVINGRESTRICTED, ZISCOMMUNICATIONSAFETYSENDINGRESTRICTED,
                       ZISEYERELIEFENABLED, ZNEEDSTOSETPASSCODE, ZISMANAGED, ZSHAREWEBUSAGE,
                       ZISAPPANDWEBSITEACTIVITYENABLED, ZISAPPANDWEBSITEACTIVITYENABLED1,
                       CASE WHEN ZPASSCODE IS NOT NULL AND ZPASSCODE != '' THEN 1 ELSE 0 END,
                       CASE WHEN ZPASSCODE1 IS NOT NULL AND ZPASSCODE1 != '' THEN 1 ELSE 0 END,
                       CASE WHEN ZPASSCODE2 IS NOT NULL AND ZPASSCODE2 != '' THEN 1 ELSE 0 END
                FROM ZCOREORGANIZATIONSETTINGS ORDER BY Z_PK'''):
            activity = row[15] if row[15] is not None else row[16]
            data_list.append((label, row[0], row[1], _date(row[2]), _flag(row[3]), row[4], row[5], row[6],
                              _flag(row[7]), _flag(row[8]), _flag(row[9]), _flag(row[10]), _flag(row[11]),
                              _flag(row[12]), _flag(activity), _flag(row[13]), _flag(row[14]),
                              _flag(1 if row[17] or row[18] or row[19] else 0)))
    return _time_first(data_headers, data_list) + (_source(stores),)


@artifact_processor
def screenTimeStoreUsers(context):
    data_headers = (
        'Store', 'Device State Row', 'Apple Account', 'DSID', 'Alt DSID', 'Given Name', 'Family Name',
        'Family Member Type', 'Family Organizer', 'Parent', 'Passcode Entry Attempt Count',
        'Passcode Recovery Attempt Count', ('Passcode Entry Timeout End', 'datetime'),
        'Device Name', 'Device Identifier', 'Platform', ('Last Passcode Use', 'datetime'),
        'Supports Passcode Activity', 'Screen Time Enabled', 'Cloud Sync Enabled',
        'Management Enabled', 'Legacy Usage Disabled', ('Last Family Check-in', 'datetime'))
    data_list = []
    stores = _stores(context)
    for label, path in stores:
        for row in _rows(path, 'ZUSERDEVICESTATE', '''
                SELECT s.Z_PK, u.ZAPPLEID, u.ZDSID, u.ZALTDSID, u.ZGIVENNAME, u.ZFAMILYNAME,
                       u.ZFAMILYMEMBERTYPE, u.ZISFAMILYORGANIZER, u.ZISPARENT,
                       u.ZPASSCODEENTRYATTEMPTCOUNT, u.ZPASSCODERECOVERYATTEMPTCOUNT,
                       u.ZPASSCODEENTRYTIMEOUTENDDATE, d.ZNAME, d.ZIDENTIFIER, d.ZPLATFORM,
                       d.ZLASTPASSCODEUSEDATE, d.ZSUPPORTSPASSCODEACTIVITY, s.ZSCREENTIMEENABLED,
                       s.ZCLOUDSYNCENABLED, s.ZMANAGEMENTENABLED, s.ZISLEGACYUSAGEDISABLED,
                       s.ZLASTFAMILYCHECKINDATE
                FROM ZUSERDEVICESTATE s
                LEFT JOIN ZCOREUSER u ON u.Z_PK = s.ZUSER
                LEFT JOIN ZCOREDEVICE d ON d.Z_PK = s.ZDEVICE
                ORDER BY s.Z_PK'''):
            data_list.append((
                label, row[0], row[1], row[2], row[3], row[4], row[5], row[6], _flag(row[7]), _flag(row[8]),
                row[9], row[10], _date(row[11]), row[12], row[13], row[14], _date(row[15]),
                _flag(row[16]), _flag(row[17]), _flag(row[18]), _flag(row[19]), _flag(row[20]),
                _date(row[21])))
    return data_headers, data_list, _source(stores)


def _decode_declaration(blob):
    """(declaration type, server hash, payload text) from a ZPAYLOADPLIST blob."""
    if blob is None:
        return '', '', ''
    try:
        declaration = plistlib.loads(bytes(blob))
    except (plistlib.InvalidFileException, ExpatError, ValueError, OverflowError):
        return '', '', f'undecodable ({len(blob)} bytes)'
    if not isinstance(declaration, dict):
        return '', '', f'undecodable ({len(blob)} bytes)'
    payload = declaration.get('Payload')
    return (declaration.get('Type', ''), declaration.get('ServerHash', ''),
            json.dumps(payload, default=_json_default, sort_keys=True) if payload is not None else '')


@artifact_processor
def screenTimeStoreBlueprints(context):
    data_headers = (
        'Store', 'Blueprint Row', 'Blueprint Identifier', 'Blueprint Type', 'Enabled', 'Tombstoned',
        'Limit Enabled', ('Created', 'datetime'), ('Modified', 'datetime'), ('Expires', 'datetime'),
        ('Minimum Installation Date', 'datetime'), 'Configuration Identifier', 'Configuration Type',
        'Declaration Type', 'Server Hash', 'Payload')
    data_list = []
    stores = _stores(context)
    for label, path in stores:
        for row in _rows(path, 'ZBLUEPRINT', '''
                SELECT b.Z_PK, b.ZIDENTIFIER, b.ZTYPE, b.ZENABLED, b.ZISTOMBSTONED, b.ZLIMITENABLED,
                       b.ZCREATIONDATE, b.ZMODIFICATIONDATE, b.ZEXPIRATION, b.ZMINIMUMINSTALLATIONDATE,
                       c.ZIDENTIFIER, c.ZTYPE, c.ZPAYLOADPLIST
                FROM ZBLUEPRINT b
                LEFT JOIN ZBLUEPRINTCONFIGURATION c ON c.ZBLUEPRINT = b.Z_PK
                ORDER BY b.Z_PK, c.Z_PK'''):
            data_list.append((
                label, row[0], row[1], row[2], _flag(row[3]), _flag(row[4]), _flag(row[5]),
                _date(row[6]), _date(row[7]), _date(row[8]), _date(row[9]),
                row[10] or '', row[11] or '', *_decode_declaration(row[12])))
    return _time_first(data_headers, data_list) + (_source(stores),)


@artifact_processor
def screenTimeStoreInstalledApps(context):
    data_headers = (
        'Store', 'Row ID', 'Bundle Identifier', 'Display Name', 'Installed Locally',
        'Distributor ID', 'Distributor Is Third Party', 'Adam ID', 'Version Identifier',
        'Beta Version Identifier', 'Unique Identifier')
    data_list = []
    stores = _stores(context)
    for label, path in stores:
        for row in _rows(path, 'ZINSTALLEDAPP', '''
                SELECT Z_PK, ZBUNDLEIDENTIFIER, ZDISPLAYNAME, ZINSTALLEDLOCALLY, ZDISTRIBUTORID,
                       ZDISTRIBUTORISTHIRDPARTY, ZADAMID, ZVERSIONIDENTIFIER, ZBETAVERSIONIDENTIFIER,
                       ZUNIQUEIDENTIFIER
                FROM ZINSTALLEDAPP ORDER BY ZBUNDLEIDENTIFIER, Z_PK'''):
            data_list.append((label, row[0], row[1], row[2], _flag(row[3]), row[4], _flag(row[5]),
                              row[6], row[7], row[8], row[9]))
    return _time_first(data_headers, data_list) + (_source(stores),)


_USAGE_BASE = '''
    SELECT b.ZSTARTDATE, b.ZUSAGE, b.Z_PK, b.ZDURATIONINMINUTES, b.ZFIRSTPICKUPDATE,
           b.ZNUMBEROFPICKUPSWITHOUTAPPLICATIONUSAGE, b.ZLONGESTSESSIONSTARTDATE,
           b.ZLONGESTSESSIONENDDATE, b.ZLASTEVENTDATE, b.ZSCREENTIMEINSECONDS,
           {fields}
    FROM {source}
    ORDER BY b.ZSTARTDATE, b.Z_PK, t.Z_PK'''

# (kind, table, selected fields from t and c, FROM clause). A timed item belongs to a category row
# (ZCATEGORY), which belongs to the block; category and counted items carry the block key themselves.
_USAGE_KINDS = (
    ('Category', 'ZUSAGECATEGORY',
     'NULL, NULL, t.ZIDENTIFIER, t.ZTOTALTIMEINSECONDS, NULL, NULL, NULL',
     'ZUSAGECATEGORY t JOIN ZUSAGEBLOCK b ON b.Z_PK = t.ZBLOCK'),
    ('Timed item', 'ZUSAGETIMEDITEM',
     't.ZBUNDLEIDENTIFIER, t.ZDOMAIN, c.ZIDENTIFIER, t.ZTOTALTIMEINSECONDS, NULL, NULL, t.ZUSAGETRUSTED',
     'ZUSAGETIMEDITEM t JOIN ZUSAGECATEGORY c ON c.Z_PK = t.ZCATEGORY JOIN ZUSAGEBLOCK b ON b.Z_PK = c.ZBLOCK'),
    ('Counted item', 'ZUSAGECOUNTEDITEM',
     't.ZBUNDLEIDENTIFIER, NULL, NULL, NULL, t.ZNUMBEROFPICKUPS, t.ZNUMBEROFNOTIFICATIONS, t.ZUSAGETRUSTED',
     'ZUSAGECOUNTEDITEM t JOIN ZUSAGEBLOCK b ON b.Z_PK = t.ZBLOCK'),
)


@artifact_processor
def screenTimeStoreUsage(context):
    data_headers = (
        ('Block Start', 'datetime'), 'Store', 'Usage Row', 'Block Row', 'Duration (minutes)', 'Kind',
        'Bundle Identifier', 'Web Domain', 'Category', 'Seconds', 'Pickups', 'Notifications',
        'Usage Trusted', ('First Pickup', 'datetime'), 'Pickups Without App Usage',
        ('Longest Session Start', 'datetime'), ('Longest Session End', 'datetime'),
        ('Last Event', 'datetime'), 'Block Screen Time (seconds)')
    data_list = []
    stores = _stores(context)
    for label, path in stores:
        if not does_table_exist_in_db(path, 'ZUSAGEBLOCK'):
            continue
        for kind, table, fields, source in _USAGE_KINDS:
            for row in _rows(path, table, _USAGE_BASE.format(fields=fields, source=source)):
                data_list.append((
                    _date(row[0]), label, row[1], row[2], row[3], kind, row[10] or '', row[11] or '',
                    row[12] or '', row[13], row[14], row[15], _flag(row[16]), _date(row[4]), row[5],
                    _date(row[6]), _date(row[7]), _date(row[8]), row[9]))
    data_list.sort(key=lambda item: (str(item[0]), item[1], item[2] or 0, item[3] or 0))
    return _time_first(data_headers, data_list) + (_source(stores),)


def _history(path):
    """(entity names by id, per-transaction [inserts, updates, deletes], entities touched per transaction)."""
    entities = {}
    for entity_id, name in _rows(path, 'Z_PRIMARYKEY', 'SELECT Z_ENT, Z_NAME FROM Z_PRIMARYKEY'):
        entities[entity_id] = name
    counts = {}
    touched = {}
    for transaction, change_type, entity_id in _rows(
            path, 'ACHANGE', 'SELECT ZTRANSACTIONID, ZCHANGETYPE, ZENTITY FROM ACHANGE'):
        tally = counts.setdefault(transaction, [0, 0, 0])
        if change_type in (0, 1, 2):
            tally[change_type] += 1
        touched.setdefault(transaction, set()).add(entities.get(entity_id, f'entity {entity_id}'))
    return entities, counts, touched


_TRANSACTION_JOIN = '''
    FROM ATRANSACTION t
    LEFT JOIN ATRANSACTIONSTRING a ON a.Z_PK = t.ZAUTHORTS
    LEFT JOIN ATRANSACTIONSTRING b ON b.Z_PK = t.ZBUNDLEIDTS
    LEFT JOIN ATRANSACTIONSTRING c ON c.Z_PK = t.ZCONTEXTNAMETS
    LEFT JOIN ATRANSACTIONSTRING p ON p.Z_PK = t.ZPROCESSIDTS'''


@artifact_processor
def screenTimeStoreChanges(context):
    data_headers = (
        ('Timestamp', 'datetime'), 'Store', 'Transaction Row', 'Author', 'Bundle ID', 'Context Name',
        'Process (as stored)', 'Inserts', 'Updates', 'Deletes', 'Entities')
    data_list = []
    stores = _stores(context)
    for label, path in stores:
        if not does_table_exist_in_db(path, 'ATRANSACTION'):
            continue
        _, counts, touched = _history(path)
        for row in _rows(path, 'ATRANSACTION', '''
                SELECT t.Z_PK, t.ZTIMESTAMP, a.ZNAME, b.ZNAME, c.ZNAME, p.ZNAME''' + _TRANSACTION_JOIN + '''
                ORDER BY t.ZTIMESTAMP, t.Z_PK'''):
            tally = counts.get(row[0], [0, 0, 0])
            data_list.append((
                _date(row[1]), label, row[0], row[2] or '', row[3] or '', row[4] or '', row[5] or '',
                tally[0], tally[1], tally[2], ', '.join(sorted(touched.get(row[0], ())))))
    return _time_first(data_headers, data_list) + (_source(stores),)


@artifact_processor
def screenTimeStoreDeletedRows(context):
    data_headers = (
        ('Timestamp', 'datetime'), 'Store', 'Transaction Row', 'Change Row', 'Bundle ID', 'Process (as stored)',
        'Entity', 'Entity Row ID', 'Value 1 (as stored)', 'Value 2 (as stored)', 'Value 3 (as stored)',
        'Value 4 (as stored)')
    data_list = []
    stores = _stores(context)
    for label, path in stores:
        if not does_table_exist_in_db(path, 'ACHANGE') or not does_table_exist_in_db(path, 'ATRANSACTION'):
            continue
        entities, _, _ = _history(path)
        for row in _rows(path, 'ACHANGE', '''
                SELECT x.Z_PK, x.ZTRANSACTIONID, x.ZENTITY, x.ZENTITYPK, x.ZTOMBSTONE0, x.ZTOMBSTONE1,
                       x.ZTOMBSTONE2, x.ZTOMBSTONE3, t.ZTIMESTAMP, b.ZNAME, p.ZNAME
                FROM ACHANGE x
                LEFT JOIN ATRANSACTION t ON t.Z_PK = x.ZTRANSACTIONID
                LEFT JOIN ATRANSACTIONSTRING b ON b.Z_PK = t.ZBUNDLEIDTS
                LEFT JOIN ATRANSACTIONSTRING p ON p.Z_PK = t.ZPROCESSIDTS
                WHERE x.ZCHANGETYPE = 2
                ORDER BY t.ZTIMESTAMP, x.Z_PK'''):
            data_list.append((
                _date(row[8]), label, row[1], row[0], row[9] or '', row[10] or '',
                entities.get(row[2], f'entity {row[2]}'), row[3],
                _stored(row[4]), _stored(row[5]), _stored(row[6]), _stored(row[7])))
    return _time_first(data_headers, data_list) + (_source(stores),)
