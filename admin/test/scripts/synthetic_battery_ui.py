#!/usr/bin/env python3
"""Build SYNTHETIC ``logs/BatteryUIPlist`` property lists (fabricated apps and numbers, no device data).

The structure mirrors what the batteryUISysdiagnose artifacts read: a ``Breakdown`` dictionary with the
range entries ``PLBatteryUIQueryRangeDayKey`` and ``...WeekKey`` (one bucket each) and
``...DayTapKey`` and ``...WeekTapKey`` (lists of buckets), each bucket holding an app list, plus the
``PLBatteryUIQueryTime``, ``PLBatteryUILastChargeKey`` and ``PLBatteryUIPausedChargingKey`` entries.
All apps are ``com.example.*``; every number comes from a formula, so the output is reproducible.

Two variants follow the two shapes seen in the contribution notes: ``hourly`` (the DayTapKey buckets are
3,600 s wide and the WeekKey bucket 10 days wide) and ``stretched`` (every bucket stored one day wide).

    python synthetic_battery_ui.py hourly out.tar.gz
    python synthetic_battery_ui.py stretched out.tar.gz
"""

import io
import plistlib
import sys
import tarfile

DAY = 86400.0
HOUR = 3600.0
QUERY_TIME = 1790740800.0                     # 2026-09-30 04:00:00 UTC
BUILDS = {"hourly": "23G71", "stretched": "24A437"}
UPGRADE_NAME = "BatteryUIUpgrade_00A001_00B002.plist"
APPS = ("com.example.alpha", "com.example.beta", "com.example.gamma", "Flashlight")


def _app(index, width):
    """One app entry; the runtimes stay below the bucket width (seconds)."""
    fg = round(width * 0.05 * (index + 1) / 4, 3)
    bg = round(width * 0.01 * (index + 1), 3)
    entry = {
        "PLBatteryUIAppBundleIDKey": APPS[index],
        "PLBatteryUIAppNameKey": APPS[index].split(".")[-1].title(),
        "PLBatteryUIAppTypeKey": 1 if APPS[index] == "Flashlight" else 0,
        "PLBatteryUIAppForegroundRuntimeKey": fg,
        "PLBatteryUIAppBackgroundRuntimeKey": bg,
        "PLBatteryUIAppForegroundPluggedInRuntimeKey": round(fg / 2, 3),
        "PLBatteryUIAppBackgroundPluggedInRuntimeKey": round(bg / 2, 3),
        "PLBatteryUIAppCallOffScreenTimeKey": 0.0,
        "PLBatteryUIAppEnergyUsedKey": round(10.5 * (index + 1), 3),
        "PLBatteryUIAppEnergyValueKey": index,
        "PLBatteryUIAppBackgroundZeroPercentDrainFlagKey": 1 if index == 0 else 0,
        "PLBatteryUIAppQualifiersKey": [index + 1, 7] if index == 1 else [],
        "SynthCPU": round(4.25 * (index + 1), 3),
        "SynthDRAM": round(1.5 * (index + 1), 3),
    }
    if index == 2:
        entry["SynthWidgetCounts"] = {"b": 2, "a": 1}
    if index == 3:                                    # an entry without the plugged-in and call keys
        for key in ("PLBatteryUIAppForegroundPluggedInRuntimeKey", "PLBatteryUIAppBackgroundPluggedInRuntimeKey",
                    "PLBatteryUIAppCallOffScreenTimeKey"):
            del entry[key]
    return entry


def _bucket(start, width, app_count, week=False):
    apps = [_app(i, width) for i in range(app_count)]
    bucket = {
        "PLBatteryUIAppArrayKey": apps,
        "PLBatteryUIAppBreakdownSortOrderKey": [a["PLBatteryUIAppBundleIDKey"] for a in apps],
        "PLBatteryUIBucketStartKey": start,
        "PLBatteryUIBucketEndKey": start + width,
        "PLBatteryUIErrorCodeKey": 0 if apps else 1,
        "PLBatteryUIForegroundTimeKey": round(sum(a["PLBatteryUIAppForegroundRuntimeKey"] for a in apps), 6),
        "PLBatteryUIBackgroundTimeKey": round(sum(a["PLBatteryUIAppBackgroundRuntimeKey"] for a in apps), 6),
        "PLBatteryUIPerAppBreakdownKey": {a["PLBatteryUIAppBundleIDKey"]: dict(a) for a in apps},
        "PLBatteryUITotalAccountedEnergyKey": round(sum(a["PLBatteryUIAppEnergyUsedKey"] for a in apps), 6),
        "PLBatteryUITotalEnergyKey": round(sum(a["PLBatteryUIAppEnergyUsedKey"] for a in apps) * 1.1, 6),
    }
    if week or apps:
        bucket["PLBatteryUIExternalDrainRatio"] = 0.25
    if not apps:
        bucket["PLBatteryUIForegroundTimeKey"] = 0
        bucket["PLBatteryUIBackgroundTimeKey"] = 0
    return bucket


def build_main(variant):
    """BatteryUISysdiagnose.plist for 'hourly' or 'stretched'."""
    day_start = QUERY_TIME - DAY
    hourly = variant == "hourly"
    tap_width = HOUR if hourly else DAY
    tap = [_bucket(QUERY_TIME - (24 - i) * tap_width, tap_width, (0, 2, 4)[i % 3] if i < 12 else 0)
           for i in range(24)]
    week_tap = [_bucket(QUERY_TIME - (10 - i) * DAY, DAY, 1 + i % 4 if i != 7 else 0) for i in range(10)]
    week_width = 10 * DAY if hourly else DAY
    breakdown = {
        "PLBatteryUIDataDurationKey": 1036800.0,
        "PLBatteryUIQueryRangeDayKey": _bucket(day_start, DAY, 3),
        "PLBatteryUIQueryRangeDayTapKey": tap,
        "PLBatteryUIQueryRangeWeekKey": _bucket(QUERY_TIME - week_width, week_width, 4, week=True),
        "PLBatteryUIQueryRangeWeekTapKey": week_tap,
        "PLBatteryUISuggestionArrayKey": [],
    }
    return {
        "Breakdown": breakdown,
        "Graph": {"PLBatteryUIDidAdjustTimesKey": True},
        "PLBatteryUILastChargeKey": {"PLBatteryUILevelKey": 77, "PLBatteryUITimestampKey": QUERY_TIME - 33000.5},
        "PLBatteryUIPausedChargingKey": {"PLBatteryUIPausedChargingCurrentPercentageKey": 87,
                                         "PLBatteryUIPausedChargingStateKey": 601},
        "PLBatteryUIQueryTime": QUERY_TIME,
        "PLBatteryUIXPCVersionKey": 1.0,
        "endOfDay": QUERY_TIME,
        "endOfHour": QUERY_TIME,
    }


def build_upgrade():
    """A BatteryUIUpgrade file: empty Day entries and filled Week entries, with the HasUpgrade key."""
    earlier = QUERY_TIME - 5 * DAY
    day = _bucket(earlier - DAY, DAY, 0)
    day["PLBatteryUIHasUpgradeKey"] = 29285029.5
    tap = [dict(_bucket(earlier - (24 - i) * DAY, DAY, 0), PLBatteryUIHasUpgradeKey=29285029.5) for i in range(24)]
    obj = build_main("stretched")
    obj["Breakdown"]["PLBatteryUIQueryRangeDayKey"] = day
    obj["Breakdown"]["PLBatteryUIQueryRangeDayTapKey"] = tap
    obj["Breakdown"]["PLBatteryUIQueryRangeWeekKey"]["PLBatteryUIHasUpgradeKey"] = 29285029.5
    obj["PLBatteryUIQueryTime"] = obj["endOfDay"] = obj["endOfHour"] = earlier
    obj["PLBatteryUILastChargeKey"] = {"PLBatteryUILevelKey": 54, "PLBatteryUITimestampKey": earlier - 4000.25}
    return obj


def edge_main():
    """BatteryUISysdiagnose.plist with damaged values: text where numbers belong and a broken bucket time."""
    obj = build_main("hourly")
    broken = obj["Breakdown"]["PLBatteryUIQueryRangeDayKey"]
    broken["PLBatteryUIAppArrayKey"][0]["PLBatteryUIAppForegroundRuntimeKey"] = "n/a"
    broken["PLBatteryUIAppArrayKey"][1]["PLBatteryUIAppEnergyUsedKey"] = True
    obj["Breakdown"]["PLBatteryUIQueryRangeDayTapKey"][0]["PLBatteryUIBucketStartKey"] = "unknown"
    obj["Breakdown"]["PLBatteryUIQueryRangeDayTapKey"][1]["PLBatteryUIAppArrayKey"].append("not a dictionary")
    return obj


def _plist(obj):
    return plistlib.dumps(obj, fmt=plistlib.PlistFormat.FMT_BINARY)


def build_files(variant, with_upgrade=True):
    """{path below logs/BatteryUIPlist: bytes}."""
    files = {"BatteryUISysdiagnose.plist": _plist(build_main(variant))}
    if with_upgrade:
        files[UPGRADE_NAME] = _plist(build_upgrade())
    return files


def write_archive(path, variant, with_upgrade=True, with_noise=True):
    """Write a sysdiagnose-shaped .tar.gz; with_noise adds a sidecar and a copy outside logs/BatteryUIPlist."""
    root = f"sysdiagnose_SYNTHETIC_iPhone-OS_iPhone_{BUILDS[variant]}"
    files = {f"{root}/logs/BatteryUIPlist/{name}": data for name, data in build_files(variant, with_upgrade).items()}
    if with_noise:
        files[f"{root}/logs/BatteryUIPlist/._BatteryUISysdiagnose.plist"] = b"\x00\x05\x16\x07"
        files[f"{root}/other/BatteryUISysdiagnose.plist"] = _plist(build_main("stretched"))
    with tarfile.open(path, "w:gz") as tar:
        for name in sorted(files):
            info = tarfile.TarInfo(name)
            info.size = len(files[name])
            info.mtime = 1790708400
            tar.addfile(info, io.BytesIO(files[name]))
    return path


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in BUILDS:
        sys.exit("usage: synthetic_battery_ui.py hourly|stretched output.tar.gz")
    write_archive(sys.argv[2], sys.argv[1], with_upgrade=sys.argv[1] == "stretched")
