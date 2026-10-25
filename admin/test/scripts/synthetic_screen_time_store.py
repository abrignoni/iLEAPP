#!/usr/bin/env python3
"""Build SYNTHETIC com.apple.remotemanagementd RMAdminStore databases (fabricated rows, no data from any device).

The tables and columns follow the Core Data schema that the screenTimeStore artifacts read in the
RMAdminStore-Local.sqlite and RMAdminStore-Cloud.sqlite files of iOS 17 to iOS 26 full file systems
(table and column names only; every row below is invented). Identifiers are ``com.example.*``, the
account is ``child.example@example.invalid`` and every date derives from the fixed epoch below, so the
output is reproducible. Two variants:

    python synthetic_screen_time_store.py child out.tar.gz   # managed child profile, populated usage
    python synthetic_screen_time_store.py plain out.tar.gz   # an unmanaged device: one user, no usage rows

``build_store(path, variant, store)`` writes one database; ``write_archive(path, variant)`` packs the
two stores below ``private/var/mobile/Library/Application Support/com.apple.remotemanagementd`` in a tar.gz,
with a decoy store in an unrelated folder. ``SCHEMA`` is the table list; ``trim_columns`` removes
columns to imitate an older store.
"""

import io
import plistlib
import sqlite3
import sys
import tarfile
import tempfile
from pathlib import Path

EPOCH = 800000000          # Core Data seconds, 2026-05-09 UTC
DAY = 86400

_Z = [("Z_PK", "INTEGER PRIMARY KEY"), ("Z_ENT", "INTEGER"), ("Z_OPT", "INTEGER")]

SCHEMA = {
    "ZSCREENTIMESETTINGS": _Z + [("ZCLOUDSYNCENABLED", "INTEGER"), ("ZFAMILYSETUPCOMPLETE", "INTEGER"),
                                 ("ZSCREENTIMEENABLED", "INTEGER"), ("ZCURRENTORGANIZATION", "INTEGER")],
    "ZCOREUSER": _Z + [("ZALLDEVICESARENEWUSAGE", "INTEGER"), ("ZDSID", "INTEGER"),
                       ("ZISFAMILYORGANIZER", "INTEGER"), ("ZISPARENT", "INTEGER"),
                       ("ZPASSCODEENTRYATTEMPTCOUNT", "INTEGER"), ("ZPASSCODERECOVERYATTEMPTCOUNT", "INTEGER"),
                       ("ZPASSCODEENTRYTIMEOUTENDDATE", "TIMESTAMP"), ("ZALTDSID", "VARCHAR"),
                       ("ZAPPLEID", "VARCHAR"), ("ZFAMILYMEMBERTYPE", "VARCHAR"), ("ZFAMILYNAME", "VARCHAR"),
                       ("ZGIVENNAME", "VARCHAR")],
    "ZCOREDEVICE": _Z + [("ZPLATFORM", "INTEGER"), ("ZIDENTIFIER", "VARCHAR"), ("ZNAME", "VARCHAR"),
                         ("ZLASTPASSCODEUSEDATE", "TIMESTAMP"), ("ZSUPPORTSPASSCODEACTIVITY", "INTEGER")],
    "ZUSERDEVICESTATE": _Z + [("ZCLOUDSYNCENABLED", "INTEGER"), ("ZISLEGACYUSAGEDISABLED", "INTEGER"),
                              ("ZMANAGEMENTENABLED", "INTEGER"), ("ZSCREENTIMEENABLED", "INTEGER"),
                              ("ZDEVICE", "INTEGER"), ("ZUSER", "INTEGER"),
                              ("ZLASTFAMILYCHECKINDATE", "TIMESTAMP"), ("ZDEVICEINFOPLIST", "BLOB")],
    "ZCOREORGANIZATIONSETTINGS": _Z + [
        ("ZALLLIMITSENABLED", "INTEGER"), ("ZCOMMUNICATIONPOLICY", "INTEGER"),
        ("ZCOMMUNICATIONWHILELIMITEDPOLICY", "INTEGER"), ("ZCONTACTMANAGEMENTSTATE", "INTEGER"),
        ("ZISCOMMUNICATIONSAFETYANALYTICSENABLED", "INTEGER"),
        ("ZISCOMMUNICATIONSAFETYNOTIFICATIONENABLED", "INTEGER"),
        ("ZISCOMMUNICATIONSAFETYRECEIVINGRESTRICTED", "INTEGER"),
        ("ZISCOMMUNICATIONSAFETYSENDINGRESTRICTED", "INTEGER"), ("ZISEYERELIEFENABLED", "INTEGER"),
        ("ZNEEDSTOSETPASSCODE", "INTEGER"), ("ZISAPPANDWEBSITEACTIVITYENABLED", "INTEGER"),
        ("ZISAPPANDWEBSITEACTIVITYENABLED1", "INTEGER"), ("ZISMANAGED", "INTEGER"),
        ("ZSHAREWEBUSAGE", "INTEGER"), ("ZMODIFICATIONDATE", "TIMESTAMP"), ("ZPASSCODE", "VARCHAR"),
        ("ZPASSCODE1", "VARCHAR"), ("ZPASSCODE2", "VARCHAR")],
    "ZBLUEPRINT": _Z + [("ZENABLED", "INTEGER"), ("ZISTOMBSTONED", "INTEGER"), ("ZLIMITENABLED", "INTEGER"),
                        ("ZCREATIONDATE", "TIMESTAMP"), ("ZEXPIRATION", "TIMESTAMP"),
                        ("ZMINIMUMINSTALLATIONDATE", "TIMESTAMP"), ("ZMODIFICATIONDATE", "TIMESTAMP"),
                        ("ZIDENTIFIER", "VARCHAR"), ("ZTYPE", "VARCHAR")],
    "ZBLUEPRINTCONFIGURATION": _Z + [("ZBLUEPRINT", "INTEGER"), ("ZIDENTIFIER", "VARCHAR"),
                                     ("ZTYPE", "VARCHAR"), ("ZPAYLOADPLIST", "BLOB")],
    "ZINSTALLEDAPP": _Z + [("ZADAMID", "INTEGER"), ("ZBETAVERSIONIDENTIFIER", "INTEGER"),
                           ("ZDISTRIBUTORISTHIRDPARTY", "INTEGER"), ("ZINSTALLEDLOCALLY", "INTEGER"),
                           ("ZVERSIONIDENTIFIER", "INTEGER"), ("ZBUNDLEIDENTIFIER", "VARCHAR"),
                           ("ZDISPLAYNAME", "VARCHAR"), ("ZDISTRIBUTORID", "VARCHAR"),
                           ("ZUNIQUEIDENTIFIER", "VARCHAR"), ("ZICONDATA", "BLOB")],
    "ZUSAGE": _Z + [("ZDEVICE", "INTEGER"), ("ZUSER", "INTEGER"), ("ZLASTEVENTDATE", "TIMESTAMP"),
                    ("ZLASTUPDATEDDATE", "TIMESTAMP")],
    "ZUSAGEBLOCK": _Z + [("ZDURATIONINMINUTES", "INTEGER"), ("ZNUMBEROFPICKUPSWITHOUTAPPLICATIONUSAGE", "INTEGER"),
                         ("ZSCREENTIMEINSECONDS", "INTEGER"), ("ZUSAGE", "INTEGER"),
                         ("ZFIRSTPICKUPDATE", "TIMESTAMP"), ("ZLASTEVENTDATE", "TIMESTAMP"),
                         ("ZLONGESTSESSIONENDDATE", "TIMESTAMP"), ("ZLONGESTSESSIONSTARTDATE", "TIMESTAMP"),
                         ("ZSTARTDATE", "TIMESTAMP")],
    "ZUSAGECATEGORY": _Z + [("ZTOTALTIMEINSECONDS", "INTEGER"), ("ZBLOCK", "INTEGER"), ("ZIDENTIFIER", "VARCHAR")],
    "ZUSAGECOUNTEDITEM": _Z + [("ZNUMBEROFNOTIFICATIONS", "INTEGER"), ("ZNUMBEROFPICKUPS", "INTEGER"),
                               ("ZUSAGETRUSTED", "INTEGER"), ("ZBLOCK", "INTEGER"), ("ZBUNDLEIDENTIFIER", "VARCHAR")],
    "ZUSAGETIMEDITEM": _Z + [("ZTOTALTIMEINSECONDS", "INTEGER"), ("ZUSAGETRUSTED", "INTEGER"),
                             ("ZCATEGORY", "INTEGER"), ("ZBUNDLEIDENTIFIER", "VARCHAR"), ("ZDOMAIN", "VARCHAR")],
    "ATRANSACTIONSTRING": _Z + [("ZNAME", "VARCHAR")],
    "ATRANSACTION": _Z + [("ZAUTHORTS", "INTEGER"), ("ZBUNDLEIDTS", "INTEGER"), ("ZCONTEXTNAMETS", "INTEGER"),
                          ("ZPROCESSIDTS", "INTEGER"), ("ZTIMESTAMP", "FLOAT"), ("ZQUERYGEN", "BLOB")],
    "ACHANGE": _Z + [("ZCHANGETYPE", "INTEGER"), ("ZENTITY", "INTEGER"), ("ZENTITYPK", "INTEGER"),
                     ("ZTRANSACTIONID", "INTEGER"), ("ZCOLUMNS", "BLOB"), ("ZTOMBSTONE0", "BLOB"),
                     ("ZTOMBSTONE1", "BLOB"), ("ZTOMBSTONE2", "BLOB"), ("ZTOMBSTONE3", "BLOB")],
    "Z_PRIMARYKEY": [("Z_ENT", "INTEGER PRIMARY KEY"), ("Z_NAME", "VARCHAR"), ("Z_SUPER", "INTEGER"),
                     ("Z_MAX", "INTEGER")],
}

ENTITIES = {3: "Blueprint", 8: "CoreOrganization", 17: "CoreUser", 23: "ScreenTimeSettings",
            27: "UserDeviceState", 30: "UsageRequest"}


def _declaration(identifier, declaration_type, payload):
    return plistlib.dumps({"Identifier": identifier, "Type": declaration_type, "Payload": payload,
                           "ServerHash": "0123456789abcdef0123456789abcdef01234567"},
                          fmt=plistlib.PlistFormat.FMT_BINARY)


def _insert(db, table, **values):
    columns = ", ".join(values)
    marks = ", ".join("?" for _ in values)
    db.execute(f"INSERT INTO {table} ({columns}) VALUES ({marks})", tuple(values.values()))


def trim_columns(db, table, columns):
    """Rebuild ``table`` without ``columns`` (imitates a store from an older release)."""
    keep = [c for c, _ in SCHEMA[table] if c not in columns]
    db.execute(f"ALTER TABLE {table} RENAME TO {table}_old")
    definition = ", ".join(f"{c} {t}" for c, t in SCHEMA[table] if c in keep)
    db.execute(f"CREATE TABLE {table} ({definition})")
    db.execute(f"INSERT INTO {table} ({', '.join(keep)}) SELECT {', '.join(keep)} FROM {table}_old")
    db.execute(f"DROP TABLE {table}_old")


def build_store(path, variant="child", store="Local"):
    """Write one synthetic RMAdminStore database; the Cloud store of ``plain`` is empty."""
    path = Path(path)
    if path.exists():
        path.unlink()
    db = sqlite3.connect(path)
    for table, columns in SCHEMA.items():
        db.execute(f"CREATE TABLE {table} ({', '.join(f'{c} {t}' for c, t in columns)})")
    for entity, name in ENTITIES.items():
        _insert(db, "Z_PRIMARYKEY", Z_ENT=entity, Z_NAME=name, Z_SUPER=0, Z_MAX=1)
    if store == "Cloud" and variant == "plain":
        db.commit()
        db.close()
        return path
    if store == "Cloud":
        # the cloud store of the child variant holds only a usage block, as a second source
        _insert(db, "ZUSAGE", Z_PK=1, Z_ENT=1, Z_OPT=1, ZDEVICE=1, ZUSER=1,
                ZLASTEVENTDATE=EPOCH + 5 * DAY, ZLASTUPDATEDDATE=EPOCH + 5 * DAY + 60)
        _insert(db, "ZUSAGEBLOCK", Z_PK=1, Z_ENT=2, Z_OPT=1, ZDURATIONINMINUTES=60,
                ZNUMBEROFPICKUPSWITHOUTAPPLICATIONUSAGE=2, ZSCREENTIMEINSECONDS=1500, ZUSAGE=1,
                ZFIRSTPICKUPDATE=EPOCH + 5 * DAY + 100, ZLASTEVENTDATE=EPOCH + 5 * DAY + 3000,
                ZLONGESTSESSIONENDDATE=EPOCH + 5 * DAY + 1000, ZLONGESTSESSIONSTARTDATE=EPOCH + 5 * DAY + 200,
                ZSTARTDATE=EPOCH + 5 * DAY)
        _insert(db, "ZUSAGECATEGORY", Z_PK=1, Z_ENT=5, Z_OPT=1, ZTOTALTIMEINSECONDS=900, ZBLOCK=1,
                ZIDENTIFIER="SYNTH-CAT-CLOUD")
        _insert(db, "ZUSAGETIMEDITEM", Z_PK=1, Z_ENT=3, Z_OPT=1, ZTOTALTIMEINSECONDS=900, ZUSAGETRUSTED=1,
                ZCATEGORY=1, ZBUNDLEIDENTIFIER="com.example.cloudapp", ZDOMAIN=None)
        db.commit()
        db.close()
        return path

    child = variant == "child"
    _insert(db, "ZSCREENTIMESETTINGS", Z_PK=1, Z_ENT=23, Z_OPT=40, ZCLOUDSYNCENABLED=1 if child else 0,
            ZFAMILYSETUPCOMPLETE=1 if child else None, ZSCREENTIMEENABLED=1 if child else 0)
    _insert(db, "ZCOREUSER", Z_PK=1, Z_ENT=17, Z_OPT=3, ZDSID=1000000001 if child else 0,
            ZISFAMILYORGANIZER=0, ZISPARENT=0, ZPASSCODEENTRYATTEMPTCOUNT=2 if child else 0,
            ZPASSCODERECOVERYATTEMPTCOUNT=0, ZPASSCODEENTRYTIMEOUTENDDATE=EPOCH + DAY if child else None,
            ZAPPLEID="child.example@example.invalid" if child else None,
            ZFAMILYMEMBERTYPE="Child" if child else "Unknown",
            ZFAMILYNAME="Sample" if child else None, ZGIVENNAME="Example" if child else None)
    _insert(db, "ZCOREDEVICE", Z_PK=1, Z_ENT=25, Z_OPT=2, ZPLATFORM=2, ZIDENTIFIER="SYNTH-DEVICE-0001",
            ZNAME="Example iPhone", ZLASTPASSCODEUSEDATE=EPOCH + 2 * DAY, ZSUPPORTSPASSCODEACTIVITY=1)
    _insert(db, "ZUSERDEVICESTATE", Z_PK=1, Z_ENT=27, Z_OPT=5, ZCLOUDSYNCENABLED=1 if child else 0,
            ZISLEGACYUSAGEDISABLED=1, ZMANAGEMENTENABLED=1 if child else 0,
            ZSCREENTIMEENABLED=1 if child else 0, ZDEVICE=1, ZUSER=1,
            ZLASTFAMILYCHECKINDATE=EPOCH + 3 * DAY if child else None)
    # a second state row whose user and device rows do not exist
    _insert(db, "ZUSERDEVICESTATE", Z_PK=2, Z_ENT=27, Z_OPT=1, ZSCREENTIMEENABLED=None, ZDEVICE=99, ZUSER=99)
    _insert(db, "ZCOREORGANIZATIONSETTINGS", Z_PK=1, Z_ENT=8, Z_OPT=7, ZALLLIMITSENABLED=1 if child else 0,
            ZCOMMUNICATIONPOLICY=2 if child else 0, ZCOMMUNICATIONWHILELIMITEDPOLICY=1 if child else 0,
            ZCONTACTMANAGEMENTSTATE=None,
            ZISCOMMUNICATIONSAFETYANALYTICSENABLED=0, ZISCOMMUNICATIONSAFETYNOTIFICATIONENABLED=1 if child else None,
            ZISCOMMUNICATIONSAFETYRECEIVINGRESTRICTED=1 if child else None,
            ZISCOMMUNICATIONSAFETYSENDINGRESTRICTED=None, ZISEYERELIEFENABLED=1 if child else None,
            ZNEEDSTOSETPASSCODE=0 if child else None, ZISAPPANDWEBSITEACTIVITYENABLED=None,
            ZISAPPANDWEBSITEACTIVITYENABLED1=1 if child else None, ZISMANAGED=1 if child else None,
            ZSHAREWEBUSAGE=1 if child else None, ZMODIFICATIONDATE=EPOCH + 4 * DAY if child else None,
            ZPASSCODE="synthetic-secret-1234" if child else None, ZPASSCODE1=None, ZPASSCODE2="")
    _insert(db, "ZBLUEPRINT", Z_PK=1, Z_ENT=3, Z_OPT=1, ZENABLED=1, ZISTOMBSTONED=0, ZLIMITENABLED=1,
            ZCREATIONDATE=None, ZMODIFICATIONDATE=EPOCH + DAY, ZIDENTIFIER="always_allow_activation_personal",
            ZTYPE="always-allowed-apps")
    _insert(db, "ZBLUEPRINTCONFIGURATION", Z_PK=1, Z_ENT=4, Z_OPT=1, ZBLUEPRINT=1,
            ZIDENTIFIER="always_allow_app_configuration_personal",
            ZTYPE="com.apple.configuration.policy.application",
            ZPAYLOADPLIST=_declaration("always_allow_app_configuration_personal",
                                       "com.apple.configuration.policy.application",
                                       {"Mode": "Override", "Apps": ["com.example.phone", "com.example.messages"]}))
    if child:
        _insert(db, "ZBLUEPRINT", Z_PK=2, Z_ENT=3, Z_OPT=2, ZENABLED=0, ZISTOMBSTONED=0, ZLIMITENABLED=1,
                ZCREATIONDATE=EPOCH + 2 * DAY, ZMODIFICATIONDATE=EPOCH + 3 * DAY, ZEXPIRATION=EPOCH + 90 * DAY,
                ZMINIMUMINSTALLATIONDATE=EPOCH, ZIDENTIFIER="digital_health_restrictions", ZTYPE="restrictions")
        _insert(db, "ZBLUEPRINTCONFIGURATION", Z_PK=2, Z_ENT=4, Z_OPT=1, ZBLUEPRINT=2,
                ZIDENTIFIER="digital_health_restrictions.application.store", ZTYPE="application.store",
                ZPAYLOADPLIST=_declaration("digital_health_restrictions.application.store",
                                           "com.apple.configuration.application.store",
                                           {"allowAppInstallation": False, "allowInAppPurchases": False,
                                            "checked": EPOCH_DATE, "token": b"\x01\x02\x03"}))
        _insert(db, "ZBLUEPRINTCONFIGURATION", Z_PK=3, Z_ENT=4, Z_OPT=1, ZBLUEPRINT=2,
                ZIDENTIFIER="broken_configuration", ZTYPE="broken", ZPAYLOADPLIST=b"not a property list")
        _insert(db, "ZBLUEPRINT", Z_PK=3, Z_ENT=3, Z_OPT=1, ZENABLED=None, ZISTOMBSTONED=1, ZLIMITENABLED=None,
                ZIDENTIFIER="managed_user_activation_0", ZTYPE="managed-user")
        for index, (bundle, name) in enumerate([("com.example.chat", "Example Chat"),
                                                ("com.example.game", None), ("com.example.notes", "Notes")]):
            _insert(db, "ZINSTALLEDAPP", Z_PK=index + 1, Z_ENT=12, Z_OPT=1, ZADAMID=1000 + index,
                    ZBETAVERSIONIDENTIFIER=0, ZDISTRIBUTORISTHIRDPARTY=0, ZINSTALLEDLOCALLY=1,
                    ZVERSIONIDENTIFIER=5000 + index, ZBUNDLEIDENTIFIER=bundle, ZDISPLAYNAME=name,
                    ZDISTRIBUTORID="com.apple.AppStore", ZUNIQUEIDENTIFIER=f"synth-app-{index}",
                    ZICONDATA=b"\x89PNG")
        # usage: two blocks, the second with every kind of tally
        _insert(db, "ZUSAGE", Z_PK=1, Z_ENT=1, Z_OPT=1, ZDEVICE=1, ZUSER=1, ZLASTEVENTDATE=EPOCH + 4 * DAY,
                ZLASTUPDATEDDATE=EPOCH + 4 * DAY + 30)
        blocks = [(1, EPOCH + 4 * DAY, 60, 900, 1), (2, EPOCH + 4 * DAY + 3600, 60, 2400, 3)]
        for pk, start, minutes, seconds, pickups in blocks:
            _insert(db, "ZUSAGEBLOCK", Z_PK=pk, Z_ENT=2, Z_OPT=1, ZDURATIONINMINUTES=minutes,
                    ZNUMBEROFPICKUPSWITHOUTAPPLICATIONUSAGE=pickups, ZSCREENTIMEINSECONDS=seconds, ZUSAGE=1,
                    ZFIRSTPICKUPDATE=start + 60, ZLASTEVENTDATE=start + 3500,
                    ZLONGESTSESSIONENDDATE=start + 1200, ZLONGESTSESSIONSTARTDATE=start + 300, ZSTARTDATE=start)
        _insert(db, "ZUSAGECATEGORY", Z_PK=1, Z_ENT=5, Z_OPT=1, ZTOTALTIMEINSECONDS=600, ZBLOCK=1,
                ZIDENTIFIER="SYNTH-CAT-SOCIAL")
        _insert(db, "ZUSAGECATEGORY", Z_PK=2, Z_ENT=5, Z_OPT=1, ZTOTALTIMEINSECONDS=1800, ZBLOCK=2,
                ZIDENTIFIER="SYNTH-CAT-GAMES")
        _insert(db, "ZUSAGETIMEDITEM", Z_PK=1, Z_ENT=6, Z_OPT=1, ZTOTALTIMEINSECONDS=600, ZUSAGETRUSTED=1,
                ZCATEGORY=1, ZBUNDLEIDENTIFIER="com.example.chat")
        _insert(db, "ZUSAGETIMEDITEM", Z_PK=2, Z_ENT=6, Z_OPT=1, ZTOTALTIMEINSECONDS=300, ZUSAGETRUSTED=0,
                ZCATEGORY=2, ZBUNDLEIDENTIFIER=None, ZDOMAIN="www.example.invalid")
        _insert(db, "ZUSAGECOUNTEDITEM", Z_PK=1, Z_ENT=7, Z_OPT=1, ZNUMBEROFNOTIFICATIONS=4,
                ZNUMBEROFPICKUPS=2, ZUSAGETRUSTED=1, ZBLOCK=2, ZBUNDLEIDENTIFIER="com.example.chat")
    # change history: three transactions, the middle one touching two entities
    for pk, name in [(1, "com.example.settingsagent"), (2, "SettingsAgent"), (9, "com.example.prefs"),
                     (10, "Prefs"), (15, "ExampleOperation")]:
        _insert(db, "ATRANSACTIONSTRING", Z_PK=pk, Z_ENT=16003, ZNAME=name)
    for pk, author, bundle, context, process, when in [
            (1, 15, 1, None, 2, EPOCH + DAY), (2, None, 9, None, 10, EPOCH + 2 * DAY),
            (3, 15, 1, None, 2, EPOCH + 3 * DAY)]:
        _insert(db, "ATRANSACTION", Z_PK=pk, Z_ENT=16002, ZAUTHORTS=author, ZBUNDLEIDTS=bundle,
                ZCONTEXTNAMETS=context, ZPROCESSIDTS=process, ZTIMESTAMP=when + 0.5)
    for pk, change, entity, transaction in [(1, 0, 3, 1), (2, 1, 23, 2), (3, 1, 23, 2), (4, 2, 3, 2),
                                            (5, 1, 17, 2), (6, 0, 99, 3)]:
        _insert(db, "ACHANGE", Z_PK=pk, Z_ENT=16001, ZCHANGETYPE=change, ZENTITY=entity, ZENTITYPK=1,
                ZTRANSACTIONID=transaction)
    db.commit()
    db.close()
    return path


EPOCH_DATE = __import__("datetime").datetime(2026, 5, 10, 12, 0, 0)

STORE_DIR = "private/var/mobile/Library/Application Support/com.apple.remotemanagementd"


def write_archive(path, variant="child", with_noise=True):
    """Write a full-file-system-shaped .tar.gz holding the Local and Cloud stores of ``variant``."""
    with tempfile.TemporaryDirectory() as folder:
        files = {}
        for store in ("Local", "Cloud"):
            db_path = build_store(Path(folder) / f"RMAdminStore-{store}.sqlite", variant, store)
            files[f"{STORE_DIR}/RMAdminStore-{store}.sqlite"] = Path(db_path).read_bytes()
        if with_noise:
            decoy = build_store(Path(folder) / "decoy.sqlite", "plain", "Local")
            files["private/var/mobile/Library/Application Support/com.example.other/RMAdminStore-Local.sqlite"] = \
                Path(decoy).read_bytes()
    with tarfile.open(path, "w:gz") as tar:
        for name in sorted(files):
            info = tarfile.TarInfo(name)
            info.size = len(files[name])
            info.mtime = 1799970000
            tar.addfile(info, io.BytesIO(files[name]))
    return path


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("child", "plain"):
        sys.exit("usage: synthetic_screen_time_store.py child|plain output.tar.gz")
    write_archive(sys.argv[2], sys.argv[1])
