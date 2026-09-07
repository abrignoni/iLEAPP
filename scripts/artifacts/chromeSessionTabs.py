__artifacts_v2__ = {
    "chrome_session_tabs": {
        "name": "Chromium Session Tabs - Navigation Entries",
        "description": "Pages held in the tab restore file of a Chromium browser, with the "
                       "address, page title and visit time the browser stored for each entry, and "
                       "the tab it belongs to.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-04",
        "last_update_date": "2026-09-04",
        "requirements": "none",
        "category": "Chromium Sessions",
        "notes": "Read from the Sessions/Tabs_<number> files a Chromium browser writes under "
                 "Library/Application Support, with the vendored snss_parser. The pattern carries "
                 "no bundle name because an app's data container is named by an identifier, so "
                 "the Browser column reports the vendor and browser folders the file sits under "
                 "and the same pattern covers Chrome and Edge.\n"
                 "One row per navigation entry, taken from the command Chromium calls "
                 "kCommandUpdateTabNavigation. Timestamp is the entry's stored time, microseconds "
                 "since 1601. Tab ID and Index identify the tab and the position of the entry in "
                 "that tab's back and forward list, so several rows with one Tab ID are one tab's "
                 "history. Transition Type and Referrer Policy are integers Chromium defines and "
                 "are reported as stored. Reference: Chromium, "
                 "components/sessions/core/serialized_navigation_entry.cc, which sets the field "
                 "order, and components/sessions/core/tab_restore_service_impl.cc, which sets the "
                 "command ids.\n"
                 "The format also carries an HTTP status, an original request URL, a post data "
                 "flag, a user agent override flag and a page state blob holding form and scroll "
                 "state. On every one of the 19 entries across the tested images those were "
                 "empty, zero or false, which is why they are not reported here and why an entry "
                 "written on this platform is a fraction of the size of one written on Android. "
                 "Every Chrome entry consumed its record exactly. The Edge entries left four "
                 "trailing bytes unread, one further value the format allows after the fields "
                 "read here, which Chromium's own reader also treats as optional; the reported "
                 "fields decode the same way in both browsers.\n"
                 "This is the browser's own restore file, so a row means the page was in a tab "
                 "the browser was holding, not that it was open when the device was seized, and "
                 "the file keeps a limited number of tabs rather than a full history. A page here "
                 "need not appear in the browser's History database.",
        "paths": ('*/Library/Application Support/*/Sessions/Tabs_*',),
        "output_types": "standard",
        "artifact_icon": "browser",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 0 rows",
            "belkactf6": "iOS 16.3 | 0 rows (run against the decrypted filesystem copy)",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 7 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hc_ios26_sysdiag": "iOS 26 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "hickman_ios15": "iOS 15 | 6 rows",
            "iphone11_ios17": "iOS 17.3 | 6 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 0 rows",
        },
    },
    "chrome_session_tab_state": {
        "name": "Chromium Session Tabs - Tab State",
        "description": "The entry each tab was sitting on in the tab restore file, with the "
                       "timestamp the browser stored against it.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-04",
        "last_update_date": "2026-09-04",
        "requirements": "none",
        "category": "Chromium Sessions",
        "notes": "Read from the same Tabs_<number> files, from the command Chromium calls "
                 "kCommandSelectedNavigationInTab. Unlike the navigation entries this record is "
                 "not a pickle but a fixed structure of a tab id, the selected navigation index "
                 "and a timestamp, microseconds since 1601. Chromium's tab restore service "
                 "records that timestamp when the tab is closed. One row per record.\n"
                 "Selected Index refers to the Index column of the navigation entries artifact "
                 "for the same Tab ID, so the two join on Tab ID to show which page the tab was "
                 "on. Browser reports the vendor and browser folders the file sits under.",
        "paths": ('*/Library/Application Support/*/Sessions/Tabs_*',),
        "output_types": "standard",
        "artifact_icon": "browser-check",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 0 rows",
            "belkactf6": "iOS 16.3 | 0 rows (run against the decrypted filesystem copy)",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 3 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hc_ios26_sysdiag": "iOS 26 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "hickman_ios15": "iOS 15 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 0 rows",
        },
    },
}

import datetime
import os
import re

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.snss_parser import SNSSError, read_navigation_entries, read_selected_navigations

_CHROMIUM_EPOCH = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)
# Library/Application Support/<vendor>/<browser>/<profile>/Sessions/Tabs_<n>
_BROWSER = re.compile(r'/Library/Application Support/([^/]+)/([^/]+)/', re.I)


def _chromium_time(value):
    """Microseconds since 1601 as an aware UTC datetime; 0 and empty are reported as blank."""
    if value in (None, '', 0):
        return ''
    try:
        return _CHROMIUM_EPOCH + datetime.timedelta(microseconds=int(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _browser(path):
    """The vendor and browser folders the file sits under, so one pattern still attributes a row."""
    match = _BROWSER.search(path.replace('\\', '/'))
    if not match:
        return ''
    return f'{match.group(1)}/{match.group(2)}'


def _tab_files(context):
    for file_found in sorted(context.get_files_found()):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        if not os.path.basename(file_found).startswith('Tabs_'):
            continue
        yield file_found


@artifact_processor
def chrome_session_tabs(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Browser',
        'Tab ID',
        'Index',
        'URL',
        'Title',
        'Transition Type (as stored)',
        'Referrer URL',
        'Referrer Policy (as stored)',
        'Source File',
    )
    data_list = []
    sources = []

    for file_found in _tab_files(context):
        try:
            entries = read_navigation_entries(file_found)
        except (SNSSError, OSError) as error:
            logfunc(f'Chromium Session Tabs: could not read {os.path.basename(file_found)}: {error}')
            continue
        browser = _browser(file_found)
        relative = context.get_relative_path(file_found)
        for entry in entries:
            data_list.append((
                _chromium_time(entry['timestamp']),
                browser,
                entry['tab_id'],
                entry['index'],
                entry['url'],
                entry['title'],
                entry['transition_type'] if entry['transition_type'] is not None else '',
                entry['referrer_url'],
                entry['referrer_policy'] if entry['referrer_policy'] is not None else '',
                relative,
            ))
        if entries:
            sources.append(file_found)

    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def chrome_session_tab_state(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Browser',
        'Tab ID',
        'Selected Index',
        'Source File',
    )
    data_list = []
    sources = []

    for file_found in _tab_files(context):
        try:
            records = read_selected_navigations(file_found)
        except (SNSSError, OSError) as error:
            logfunc(f'Chromium Session Tabs: could not read {os.path.basename(file_found)}: {error}')
            continue
        browser = _browser(file_found)
        relative = context.get_relative_path(file_found)
        for record in records:
            data_list.append((
                _chromium_time(record['timestamp']),
                browser,
                record['tab_id'],
                record['index'],
                relative,
            ))
        if records:
            sources.append(file_found)

    return data_headers, data_list, '\n'.join(sources)
