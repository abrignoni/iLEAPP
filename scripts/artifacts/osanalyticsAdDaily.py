__artifacts_v2__ = {
    "osanalytics_addaily_net_usage": {
        "name": "OS Analytics - Network Usage Baseline",
        "description": "Per-process Wi-Fi and cellular in and out values with a date, from the netUsageBaseline "
                       "dictionary of com.apple.osanalytics.addaily.plist.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Network & Connectivity",
        "notes": "Reads the netUsageBaseline dictionary of com.apple.osanalytics.addaily.plist in "
                 "mobile/Library/Preferences: one row per key, each key holding a date and four numbers. The numbers "
                 "are stored as reals; all 18,580 on the 24 images were whole and are shown without a decimal part. "
                 "Process is the key as stored. On 19 images, 3,476 of 3,653 keys equalled a netusage.sqlite bundle "
                 "name or process name; 158 more, on cookbook_ios1751 and iphone11_ios17, equalled a netusage "
                 "process name that holds a slash, and what the part after the slash names is not established. Date "
                 "is the first value, shown in UTC, and Wi-Fi In, Wi-Fi Out, Cellular In and Cellular Out are the "
                 "next four values. No Apple documentation of this file is cited here. MVT reads the four values in "
                 "that order (mvt-project/mvt src/mvt/ios/modules/mixed/osanalytics_addaily.py lines 90 to 93 at "
                 "commit 3b7a6fef). The order was checked against netusage.sqlite under networkd on 19 images, "
                 "matching a key to netusage processes by name; 155 keys matched more than one netusage row, and "
                 "those rows were summed. On the 1,111 processes that netusage recorded only Wi-Fi use for, Cellular "
                 "In and Cellular Out were 0 on all 1,111. On the 330 it recorded only cellular use for, Wi-Fi In "
                 "and Wi-Fi Out were 0 on all 330; 171 of those are on iphone12_ios18, where both Wi-Fi columns are "
                 "0 on every row. Among pairs where both values were non-zero and unequal in both stores, the larger "
                 "value was on the same side as netusage's in and out columns for 3,071 of 3,082 Wi-Fi pairs and "
                 "2,269 of 2,278 cellular pairs. Where netusage's total was not 0, the values were equal to it on "
                 "7,776, lower on 3,086 and higher on 3 of 10,865 comparisons, and one more value was above a "
                 "netusage total of 0. What this file records and when it is written is not established. Date was "
                 "within 2 minutes of netusage's ZPROCESS.ZFIRSTTIMESTAMP on the nearest matching row for 3,475 of "
                 "3,476 matched keys; what moment either marks is not established, so rows are not written to the "
                 "timeline. Much of this repeats the netusage artifacts in the Network Usage category. It is kept "
                 "because this file can hold rows where netusage.sqlite is not readable: on otto_ios17 the "
                 "netusage.sqlite under networkd was a 4,096-byte file with no tables, and the archive holds no -wal "
                 "for it, while this file held 235 processes. On belkactf6_tar Cellular In and Cellular Out held one "
                 "value, 0, on all 126 rows. On magnet_ios16 Cellular In held one value, 0, on all 155 rows, and "
                 "netusage there recorded no cellular input either. On iphone12_ios18 Wi-Fi In and Wi-Fi Out held "
                 "one value, 0, on all 174 rows; netusage's one row with Wi-Fi input there is dated about 4 days "
                 "after the latest Date in this file. netUsageBaseline was the only top-level key on all 24 images, "
                 "and any other key is not read.",
        "paths": ('*/mobile/Library/Preferences/com.apple.osanalytics.addaily.plist',),
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 226 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 172 rows",
            "belkactf6_tar": "iOS 16.3 | 126 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 239 rows",
            "ctf2020_ios12": "iOS 12.4 | 170 rows",
            "dexter_ios18": "iOS 18.3.2 | 110 rows",
            "falken_ios26": "iOS 26.2.1 | 225 rows",
            "felix23_ios16": "iOS 16.5 | 177 rows",
            "felix_ios17": "iOS 17.6.1 | 198 rows",
            "fsfull002_ios17": "iOS 17.1 | 168 rows",
            "hc_ios17_2": "iOS 17.2.1 | 210 rows",
            "hc_ios18_7": "iOS 18.7.8 | 210 rows",
            "hc_ios26": "iOS 26.5.2 | 206 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 149 rows",
            "hickman_ios13": "iOS 13.3.1 | 179 rows",
            "hickman_ios14": "iOS 14.3 | 260 rows",
            "hickman_ios15": "iOS 15.3.1 | 192 rows",
            "iphone11_ios17": "iOS 17.3 | 340 rows",
            "iphone12_ios18": "iOS 18.7 | 174 rows",
            "iphone14plus_ios18": "iOS 18.0 | 164 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 225 rows",
            "jess_ios15": "iOS 15.0.2 | 135 rows",
            "magnet_ios16": "iOS 16.1.1 | 155 rows",
            "otto_ios17": "iOS 17.5.1 | 235 rows",
        },
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "chart-pie",
    },
}

import datetime
import plistlib
from xml.parsers.expat import ExpatError

from scripts.ilapfuncs import artifact_processor, logfunc

_PLIST_ERRORS = (plistlib.InvalidFileException, ExpatError, ValueError, TypeError, OverflowError, OSError)


def _number(value):
    """A whole real as an int, so HTML, TSV and LAVA show the same digits; anything else unchanged."""
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def _utc(value):
    if isinstance(value, datetime.datetime):
        return value if value.tzinfo else value.replace(tzinfo=datetime.timezone.utc)
    return ''


@artifact_processor
def osanalytics_addaily_net_usage(context):
    data_list = []
    sources = []
    for path in context.get_files_found():
        path = str(path)
        if not path.endswith('com.apple.osanalytics.addaily.plist'):
            continue
        sources.append(path)
        try:
            with open(path, 'rb') as handle:
                data = plistlib.load(handle)
        except _PLIST_ERRORS as error:
            logfunc(f'OS Analytics addaily: could not read {path}: {error}')
            continue
        baseline = data.get('netUsageBaseline') if isinstance(data, dict) else None
        if not isinstance(baseline, dict):
            continue
        for process, values in sorted(baseline.items()):
            values = list(values) if isinstance(values, (list, tuple)) else []
            values += [''] * (5 - len(values))
            data_list.append((_utc(values[0]), str(process), *(_number(v) for v in values[1:5])))
    data_headers = (
        ('Date', 'datetime'), 'Process', ('Wi-Fi In', 'number'), ('Wi-Fi Out', 'number'),
        ('Cellular In', 'number'), ('Cellular Out', 'number'),
    )
    return data_headers, data_list, '\n'.join(sources)
