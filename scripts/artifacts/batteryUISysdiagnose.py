__artifacts_v2__ = {
    "batteryUISysdiagnoseApps": {
        "name": "Battery UI - Per-App Runtime",
        "description": "Per-app foreground and background runtime and energy values by time bucket, from the BatteryUI property lists of a sysdiagnose (logs/BatteryUIPlist)",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-20",
        "last_update_date": "2026-10-20",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "A sysdiagnose carries logs/BatteryUIPlist/BatteryUISysdiagnose.plist and can carry one or more "
                 "BatteryUIUpgrade_<old build>_<new build>.plist files, named for two builds. Both hold a "
                 "Breakdown section with four range entries: PLBatteryUIQueryRangeDayKey and "
                 "PLBatteryUIQueryRangeWeekKey (one bucket each) and PLBatteryUIQueryRangeDayTapKey and "
                 "PLBatteryUIQueryRangeWeekTapKey (a list of buckets each). A row is one app entry of one bucket "
                 "of one range entry. The range entries overlap, so the same activity can appear in more than one "
                 "range; read the rows of one Range (as stored) at a time and do not add ranges together. Bucket "
                 "Start and Bucket End are the stored PLBatteryUIBucketStartKey and PLBatteryUIBucketEndKey read "
                 "as Unix epoch seconds and shown in UTC, and Bucket Seconds is the end minus the start. On iOS "
                 "14.3 (hickman_ios14_sysdiag) the buckets carry neither key, so those three columns are blank "
                 "and the rows have no time. The boundaries fell on whole hours (UTC) on iOS 26.5.2, 26.6 and in "
                 "the iOS 27.0 file read, but not on iOS 17.3 (rodeo_ios17_sysdiag). The last bucket of the main "
                 "file ended at the local midnight after the date in the sysdiagnose folder name on both iOS 26 "
                 "images and about ten minutes after it on iOS 17.3. The bucket width is not the same in every "
                 "file. On iOS 17.3, 26.5.2 and 26.6 the DayTapKey buckets were 3,600 seconds wide, the DayKey "
                 "and WeekTapKey buckets 86,400 and the WeekKey bucket 864,000. In the iOS 27.0 (24A437) file "
                 "read, the DayTapKey and WeekKey buckets were stored 86,400 seconds wide and the per-app values "
                 "of the WeekKey bucket exceed that width, so the stored bucket times of those entries do not "
                 "bound the values. Use Bucket Seconds as stored and not as an assumed width. Foreground Runtime "
                 "and Background Runtime are the PLBatteryUIAppForegroundRuntimeKey and "
                 "PLBatteryUIAppBackgroundRuntimeKey values in seconds. The evidence: in the iOS 27.0 file read "
                 "ten DayTapKey values equal exactly 3,600.0, one hour in seconds, and so do 13 DayTapKey values "
                 "in the upgrade files on ai16_ios26_sysdiag; one-hour DayTapKey buckets hold values far above "
                 "the 60 an hour could hold in minutes; and on the corpus images every bucket with app entries "
                 "(159 of 159) has foreground and background time equal to the sum of its app values. One value "
                 "exceeded its stored bucket width: 3,608.6 in a 3,600-second DayTapKey bucket of an upgrade file "
                 "on ai16_ios26_sysdiag. Plugged-in runtimes and the call off-screen time are given as stored, "
                 "with no unit; in the files read a plugged-in runtime can be larger than the runtime value of "
                 "the same app, so it is not part of it. Energy Used, Energy Value and the Energy Components are "
                 "the stored numbers with no unit: the unit and what the Energy Value (a whole number, stored as "
                 "an integer in most entries) expresses are not established. Energy Components lists the other "
                 "numeric keys of the app entry (for example CPU, DRAM, Foreground, Autolock) as stored; App Type "
                 "and Zero-Percent-Drain Flag are stored integers and Qualifiers is a stored list of integers; "
                 "their meaning is not established. App Identifier is the PLBatteryUIAppBundleIDKey value, which "
                 "in the files read is a reverse-DNS bundle identifier for most entries and a short name without "
                 "a dot for others; what the short names denote is not established. The per-app dictionary kept "
                 "beside the app list (PLBatteryUIPerAppBreakdownKey) held the same values as the app list in the "
                 "iOS 26 files read and is not repeated; the iOS 14.3 and 17.3 files do not carry it. These "
                 "figures are not the PowerLog - Application Runtime values: on ai16_ios26_sysdiag the main "
                 "file's 39 DayTapKey app-hours and PowerLog's values for the same hours (PowerLog rows summed by "
                 "bundle identifier within each hour bucket) shared 5 app-hours, foreground runtime matched "
                 "ScreenOnTime within 5 seconds or 5% on 2 of them, and 34 app-hours had no PowerLog value; one "
                 "does not stand in for the other. A value is a runtime figure the file records for the bucket; a "
                 "row does not show that the app was opened by a person, and an app with no row had no entry in "
                 "the file, which is not evidence that it did not run. The buckets cover a limited window; the "
                 "file states a Data Duration without a unit (see Snapshots), and an empty result is not evidence "
                 "of no activity. On the five sysdiagnoses in sample_data, read through this artifact: "
                 "hickman_ios14_sysdiag (iOS 14.3), rodeo_ios17_sysdiag (iOS 17.3), ai16_ios26_sysdiag (iOS "
                 "26.5.2, main file and three upgrade files) and hc_ios26_sysdiag (iOS 26.6, main file and two "
                 "upgrade files) gave rows; hickman_ios13_sysdiag (iOS 13.3.1) holds only BatteryUI.plist and "
                 "gives none. BatteryUI.plist, which can sit in the same folder, is not read. On hc_ios26_sysdiag "
                 "it has a different layout (daily breakdowns, a Drain section, a usage summary and battery and "
                 "screen graphs) and was an older copy whose query time matched the 23F77 to 23F84 upgrade file, "
                 "with empty app lists, zero foreground and background time and zero daily screen-on totals. On "
                 "hickman_ios13_sysdiag it has the same four range entries as the main file, held a few app "
                 "entries and hourly screen-on values, and stores no bucket times, and its query time was three "
                 "weeks before the sysdiagnose. The Graph, endOfDay and endOfHour sections of the files that are "
                 "read are not reported either. The iOS 26.6 (23G71, a different device from hc_ios26_sysdiag) "
                 "and iOS 27.0 (24A437) files the artifact was built from are not shareable as they are; the test "
                 "cases hold a copy of each with the identifying values replaced (case_ios26_sanitized, "
                 "case_ios27_sanitized) and a generated synthetic copy of each shape.",
        "paths": (
            '*/logs/BatteryUIPlist/BatteryUI*.plist',
            '*/sysdiagnose_*.tar.gz', '*/*_sysdiagnose.tar.gz'),
        "output_types": "standard",
        "artifact_icon": "battery-charging",
        "sample_data": {
            "hickman_ios13_sysdiag": "iOS 13.3.1 | 0 rows; only BatteryUI.plist, which is not read",
            "hickman_ios14_sysdiag": "iOS 14.3 | 443 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 173 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 1473 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 156 rows",
        }
    },
    "batteryUISysdiagnoseBuckets": {
        "name": "Battery UI - Time Buckets",
        "description": "Bucket totals from the BatteryUI property lists of a sysdiagnose (logs/BatteryUIPlist): foreground and background time, energy totals, error code and the number of app entries",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-20",
        "last_update_date": "2026-10-20",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "A row is one bucket of one range entry (see 'Battery UI - Per-App Runtime' for the range "
                 "entries and for how Bucket Start, Bucket End and Bucket Seconds are read; they are blank on iOS "
                 "14.3). Foreground Time and Background Time are the PLBatteryUIForegroundTimeKey and "
                 "PLBatteryUIBackgroundTimeKey values; on the corpus images they equal the sums of the per-app "
                 "Foreground Runtime and Background Runtime values of the same bucket in every bucket with app "
                 "entries (159 of 159), so they are in seconds like those. Total Energy and Total Accounted "
                 "Energy, External Drain Ratio and Has Upgrade are stored numbers with no unit; what they express "
                 "is not established. Error Code is the stored PLBatteryUIErrorCodeKey integer: it was 0 on every "
                 "bucket with app entries and 1 on most buckets without, but 0 on 5 buckets without entries on "
                 "hc_ios26_sysdiag, so it does not stand for an empty bucket and no meaning is claimed. A bucket "
                 "with no app entries is listed so that a gap is visible; a gap is not evidence that the device "
                 "was unused, because the file does not say whether data was recorded for it. App Entries is the "
                 "number of app entries in the bucket. The buckets of the different range entries overlap and "
                 "must not be added together. On the five sysdiagnoses in sample_data, read through this "
                 "artifact: hickman_ios14_sysdiag (iOS 14.3), rodeo_ios17_sysdiag (iOS 17.3), ai16_ios26_sysdiag "
                 "(iOS 26.5.2, main file and three upgrade files) and hc_ios26_sysdiag (iOS 26.6, main file and "
                 "two upgrade files) gave rows; hickman_ios13_sysdiag (iOS 13.3.1) holds only BatteryUI.plist and "
                 "gives none. BatteryUI.plist, which can sit in the same folder, is not read. On hc_ios26_sysdiag "
                 "it has a different layout (daily breakdowns, a Drain section, a usage summary and battery and "
                 "screen graphs) and was an older copy whose query time matched the 23F77 to 23F84 upgrade file, "
                 "with empty app lists, zero foreground and background time and zero daily screen-on totals. On "
                 "hickman_ios13_sysdiag it has the same four range entries as the main file, held a few app "
                 "entries and hourly screen-on values, and stores no bucket times, and its query time was three "
                 "weeks before the sysdiagnose.",
        "paths": (
            '*/logs/BatteryUIPlist/BatteryUI*.plist',
            '*/sysdiagnose_*.tar.gz', '*/*_sysdiagnose.tar.gz'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "chart-bar",
        "sample_data": {
            "hickman_ios13_sysdiag": "iOS 13.3.1 | 0 rows; only BatteryUI.plist, which is not read",
            "hickman_ios14_sysdiag": "iOS 14.3 | 36 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 36 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 144 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 108 rows",
        }
    },
    "batteryUISysdiagnoseSnapshots": {
        "name": "Battery UI - Snapshots and Upgrade Marker",
        "description": "One row per BatteryUI property list of a sysdiagnose (logs/BatteryUIPlist): query time, last charge entry and, for a BatteryUIUpgrade file, the old and new build named by the file",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-20",
        "last_update_date": "2026-10-20",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "A row is one property list: BatteryUISysdiagnose.plist, or a "
                 "BatteryUIUpgrade_<old>_<new>.plist. Old Build and New Build are the two build names in the file "
                 "name of an upgrade file; the file name is the only place they were found in the files read, and "
                 "the values inside the file do not repeat them. An upgrade file is a separate copy of the same "
                 "kind of data as the main file; its presence is a lead that the build changed, and the file does "
                 "not state when the update was done. Query Time is the stored PLBatteryUIQueryTime read as Unix "
                 "epoch seconds in UTC. It equalled the end of the last bucket in every file on both iOS 26 "
                 "images, but on iOS 17.3 it was hours before that end and on iOS 14.3, whose buckets store no "
                 "times, it was within a minute of the time in the sysdiagnose folder name; it is not the time "
                 "the file was written. Last Charge Time and Last Charge Level are the stored "
                 "PLBatteryUILastChargeKey timestamp (Unix epoch seconds, shown in UTC) and level; the unit of "
                 "the level is not stated by the file. Paused Charging State and Paused Charging Percentage are "
                 "the stored PLBatteryUIPausedChargingKey values with no further meaning claimed. Data Duration "
                 "is the stored PLBatteryUIDataDurationKey; its unit is not stated by the file. It read 864,000 "
                 "on iOS 14.3, 950,400 on iOS 17.3, 1,036,800 in the iOS 27.0 file read, in all four files on "
                 "ai16_ios26_sysdiag and in two of the three on hc_ios26_sysdiag, and 86,400 in the 23F77 to "
                 "23F84 upgrade file there. Range Entries lists the range entries found. Has Upgrade values are "
                 "given in 'Battery UI - Time Buckets'. The absence of an upgrade file is not evidence that no "
                 "update happened. On the five sysdiagnoses in sample_data, read through this artifact: "
                 "hickman_ios14_sysdiag (iOS 14.3), rodeo_ios17_sysdiag (iOS 17.3), ai16_ios26_sysdiag (iOS "
                 "26.5.2, main file and three upgrade files) and hc_ios26_sysdiag (iOS 26.6, main file and two "
                 "upgrade files) gave rows; hickman_ios13_sysdiag (iOS 13.3.1) holds only BatteryUI.plist and "
                 "gives none. BatteryUI.plist, which can sit in the same folder, is not read. On hc_ios26_sysdiag "
                 "it has a different layout (daily breakdowns, a Drain section, a usage summary and battery and "
                 "screen graphs) and was an older copy whose query time matched the 23F77 to 23F84 upgrade file, "
                 "with empty app lists, zero foreground and background time and zero daily screen-on totals. On "
                 "hickman_ios13_sysdiag it has the same four range entries as the main file, held a few app "
                 "entries and hourly screen-on values, and stores no bucket times, and its query time was three "
                 "weeks before the sysdiagnose.",
        "paths": (
            '*/logs/BatteryUIPlist/BatteryUI*.plist',
            '*/sysdiagnose_*.tar.gz', '*/*_sysdiagnose.tar.gz'),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "battery",
        "sample_data": {
            "hickman_ios13_sysdiag": "iOS 13.3.1 | 0 rows; only BatteryUI.plist, which is not read",
            "hickman_ios14_sysdiag": "iOS 14.3 | 1 row",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 1 row",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 4 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 3 rows",
        }
    }
}

import json
import plistlib
import re
from datetime import datetime, timezone
from xml.parsers.expat import ExpatError

from scripts.ilapfuncs import artifact_processor, get_sysdiagnose_files, logfunc

_PLIST_NAME = re.compile(r'BatteryUI(?:Sysdiagnose|Upgrade_[^/\\]+)\.plist$')
_PLIST_PATH = re.compile(
    r'(?:^|[/\\])logs[/\\]BatteryUIPlist[/\\]'
    r'(?:(BatteryUISysdiagnose)|BatteryUIUpgrade_([A-Za-z0-9]+)_([A-Za-z0-9]+))\.plist$')
_PLIST_ERRORS = (plistlib.InvalidFileException, ExpatError, ValueError, OverflowError, TypeError)

KIND_MAIN = 'Main file'
KIND_UPGRADE = 'Upgrade file'

# Range entries of the Breakdown dictionary, with the stored key as shown in the Range column.
RANGE_PREFIX = 'PLBatteryUIQueryRange'
APP_ARRAY = 'PLBatteryUIAppArrayKey'
APP_PREFIX = 'PLBatteryUIApp'
# App entry keys reported in their own columns; every other numeric key goes to Energy Components.
_APP_COLUMNS = {
    'PLBatteryUIAppBundleIDKey', 'PLBatteryUIAppNameKey', 'PLBatteryUIAppTypeKey',
    'PLBatteryUIAppForegroundRuntimeKey', 'PLBatteryUIAppBackgroundRuntimeKey',
    'PLBatteryUIAppForegroundPluggedInRuntimeKey', 'PLBatteryUIAppBackgroundPluggedInRuntimeKey',
    'PLBatteryUIAppCallOffScreenTimeKey', 'PLBatteryUIAppEnergyUsedKey', 'PLBatteryUIAppEnergyValueKey',
    'PLBatteryUIAppBackgroundZeroPercentDrainFlagKey', 'PLBatteryUIAppQualifiersKey',
}


def utc_from_epoch(value):
    '''Unix epoch seconds -> aware UTC datetime, or None when the value is not a usable number.'''
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        return datetime.fromtimestamp(value, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None


def _number(value):
    '''The value when it is a number, else None (a boolean is not a number here).'''
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value


def _text(value):
    if value is None:
        return ''
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return str(value)


def load_plist(data):
    '''Parsed property list, or None when it cannot be read.'''
    try:
        return plistlib.loads(data)
    except _PLIST_ERRORS as ex:
        logfunc(f'Battery UI: property list not readable: {ex}')
        return None


def read_files(context):
    '''Yield dicts for every BatteryUI plist: kind, old/new build, source and the parsed object.'''
    for stream, source in get_sysdiagnose_files(context.get_files_found(), _PLIST_NAME, text_mode=False):
        match = _PLIST_PATH.search(source.split(' >> ')[-1])
        if not match:
            continue
        upgrade = match.group(1) is None
        yield {'kind': KIND_UPGRADE if upgrade else KIND_MAIN, 'old': match.group(2) or '',
               'new': match.group(3) or '', 'source': source, 'obj': load_plist(stream.read())}


def iter_buckets(obj):
    '''Yield (range key as stored, bucket number or '', bucket dict) in file order of the Breakdown keys.'''
    breakdown = obj.get('Breakdown') if isinstance(obj, dict) else None
    if not isinstance(breakdown, dict):
        return
    for key in sorted(k for k in breakdown if str(k).startswith(RANGE_PREFIX)):
        value = breakdown[key]
        short = str(key)[len(RANGE_PREFIX):]
        if isinstance(value, dict):
            yield short, '', value
        elif isinstance(value, list):
            for number, bucket in enumerate(value, 1):
                if isinstance(bucket, dict):
                    yield short, number, bucket


def bucket_times(bucket):
    '''(start, end, seconds) from the stored bucket keys; each is None when it is not a number.'''
    start = _number(bucket.get('PLBatteryUIBucketStartKey'))
    end = _number(bucket.get('PLBatteryUIBucketEndKey'))
    seconds = end - start if start is not None and end is not None else None
    return utc_from_epoch(start), utc_from_epoch(end), seconds


def apps_of(bucket):
    '''The app entries of a bucket (dictionaries only).'''
    apps = bucket.get(APP_ARRAY)
    return [app for app in apps if isinstance(app, dict)] if isinstance(apps, list) else []


def components(app):
    '''Numeric keys of an app entry that have no column of their own, as key=value text, sorted by key.'''
    parts = []
    for key in sorted(k for k in app if str(k) not in _APP_COLUMNS):
        value = app[key]
        if _number(value) is not None:
            parts.append(f'{key}={value}')
        else:
            parts.append(f'{key}={json.dumps(value, sort_keys=True, default=str)}')
    return '; '.join(parts)


def app_rows(info):
    '''Rows (without the source) for every app entry of every bucket of one file.'''
    rows = []
    for short, number, bucket in iter_buckets(info['obj']):
        start, end, seconds = bucket_times(bucket)
        for app in apps_of(bucket):
            qualifiers = app.get('PLBatteryUIAppQualifiersKey')
            rows.append((
                start, end, seconds, short, number,
                _text(app.get('PLBatteryUIAppBundleIDKey')), _text(app.get('PLBatteryUIAppNameKey')),
                app.get('PLBatteryUIAppTypeKey'),
                _number(app.get('PLBatteryUIAppForegroundRuntimeKey')),
                _number(app.get('PLBatteryUIAppBackgroundRuntimeKey')),
                _number(app.get('PLBatteryUIAppForegroundPluggedInRuntimeKey')),
                _number(app.get('PLBatteryUIAppBackgroundPluggedInRuntimeKey')),
                _number(app.get('PLBatteryUIAppCallOffScreenTimeKey')),
                _number(app.get('PLBatteryUIAppEnergyUsedKey')),
                _number(app.get('PLBatteryUIAppEnergyValueKey')),
                app.get('PLBatteryUIAppBackgroundZeroPercentDrainFlagKey'),
                ', '.join(str(item) for item in qualifiers) if isinstance(qualifiers, list) else '',
                components(app), info['kind']))
    return rows


def bucket_rows(info):
    '''Rows (without the source) for every bucket of one file.'''
    rows = []
    for short, number, bucket in iter_buckets(info['obj']):
        start, end, seconds = bucket_times(bucket)
        rows.append((
            start, end, seconds, short, number,
            _number(bucket.get('PLBatteryUIForegroundTimeKey')), _number(bucket.get('PLBatteryUIBackgroundTimeKey')),
            _number(bucket.get('PLBatteryUITotalEnergyKey')), _number(bucket.get('PLBatteryUITotalAccountedEnergyKey')),
            _number(bucket.get('PLBatteryUIExternalDrainRatio')), _number(bucket.get('PLBatteryUIHasUpgradeKey')),
            bucket.get('PLBatteryUIErrorCodeKey'), len(apps_of(bucket)), info['kind']))
    return rows


def snapshot_row(info):
    '''Row (without the source) for one file.'''
    obj = info['obj']
    if not isinstance(obj, dict):
        return (None, None, info['kind'], info['old'], info['new'], None, None, None, None, None, '',
                'The file could not be read as a property list.')
    charge = obj.get('PLBatteryUILastChargeKey') if isinstance(obj.get('PLBatteryUILastChargeKey'), dict) else {}
    paused = obj.get('PLBatteryUIPausedChargingKey') if isinstance(obj.get('PLBatteryUIPausedChargingKey'), dict) else {}
    breakdown = obj.get('Breakdown') if isinstance(obj.get('Breakdown'), dict) else {}
    ranges = ', '.join(str(k)[len(RANGE_PREFIX):] for k in sorted(breakdown) if str(k).startswith(RANGE_PREFIX))
    return (utc_from_epoch(obj.get('PLBatteryUIQueryTime')), utc_from_epoch(charge.get('PLBatteryUITimestampKey')),
            info['kind'], info['old'], info['new'], charge.get('PLBatteryUILevelKey'),
            paused.get('PLBatteryUIPausedChargingStateKey'),
            paused.get('PLBatteryUIPausedChargingCurrentPercentageKey'),
            _number(breakdown.get('PLBatteryUIDataDurationKey')), obj.get('PLBatteryUIXPCVersionKey'),
            ranges, '')


def _collect(context, build):
    data_list, sources = [], []
    for info in sorted(read_files(context), key=lambda item: item['source']):
        sources.append(info['source'])
        relative = context.get_relative_path(info['source'])
        for row in build(info):
            data_list.append(row + (relative,))
    return data_list, '\n'.join(sorted(set(sources)))


@artifact_processor
def batteryUISysdiagnoseApps(context):
    ''' See artifact description '''
    data_headers = (
        ('Bucket Start (UTC)', 'datetime'), ('Bucket End (UTC)', 'datetime'), 'Bucket Seconds',
        'Range (as stored)', 'Bucket No.', 'App Identifier (as stored)', 'App Name', 'App Type (as stored)',
        'Foreground Runtime (s)', 'Background Runtime (s)', 'Foreground Plugged-In Runtime (as stored)',
        'Background Plugged-In Runtime (as stored)', 'Call Off-Screen Time (as stored)', 'Energy Used (as stored)',
        'Energy Value (as stored)', 'Zero-Percent-Drain Flag (as stored)', 'Qualifiers (as stored)',
        'Energy Components (as stored)', 'File Kind', 'Source File')
    data_list, source = _collect(context, app_rows)
    return data_headers, data_list, source


@artifact_processor
def batteryUISysdiagnoseBuckets(context):
    ''' See artifact description '''
    data_headers = (
        ('Bucket Start (UTC)', 'datetime'), ('Bucket End (UTC)', 'datetime'), 'Bucket Seconds',
        'Range (as stored)', 'Bucket No.', 'Foreground Time (s)', 'Background Time (s)',
        'Total Energy (as stored)', 'Total Accounted Energy (as stored)', 'External Drain Ratio (as stored)',
        'Has Upgrade (as stored)', 'Error Code (as stored)', 'App Entries', 'File Kind', 'Source File')
    data_list, source = _collect(context, bucket_rows)
    return data_headers, data_list, source


@artifact_processor
def batteryUISysdiagnoseSnapshots(context):
    ''' See artifact description '''
    data_headers = (
        ('Query Time (UTC)', 'datetime'), ('Last Charge Time (UTC)', 'datetime'), 'File Kind',
        'Old Build (from file name)', 'New Build (from file name)', 'Last Charge Level (as stored)', 'Paused Charging State (as stored)',
        'Paused Charging Percentage (as stored)', 'Data Duration (as stored)', 'XPC Version (as stored)',
        'Range Entries', 'Notes', 'Source File')
    data_list, source = _collect(context, lambda info: [snapshot_row(info)])
    return data_headers, data_list, source
