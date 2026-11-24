__artifacts_v2__ = {
    "ios_version_diagnostic_reports": {
        "name": "iOS Version - Diagnostic Reports",
        "description": "The iOS version and build each .ips diagnostic report names, one row per version and "
                       "build, read only when no version file gave the iOS version. The version of the "
                       "newest report, by metadata timestamp, is used as the iOS version for the run.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-24",
        "last_update_date": "2026-11-24",
        "requirements": "none",
        "category": "IOS Build",
        "notes": "A fallback for a run in which last_build and the selected version readers gave no iOS "
                 "version. It runs after them, and only when none of them gave a version; otherwise it "
                 "is not run and the log says so. It reads the .ips files under "
                 "Library/Logs/CrashReporter, including the Retired subfolder. For a report of bug_type "
                 "309 the version is the body's osVersion train and build, which Apple documents in "
                 "'Interpreting the JSON format of a crash report' "
                 "(https://developer.apple.com/documentation/xcode/interpreting-the-json-format-of-a-crash-report). "
                 "When that body gives no readable train, and for every other report, it is the "
                 "os_version key of the first line of metadata, and Field says which was read. That "
                 "page does not list os_version among the metadata keys, so that value is data-proven "
                 "only. The version is the dotted number in that text and the build is the text in "
                 "parentheses. A value with no dotted number is not read as a version: on falken_ios26 "
                 "the two OTAUpdate reports held a build alone, and they are counted in the log as "
                 "giving no readable version, as is a file with no metadata line. When the reports name "
                 "more than one version and build, the one named by the report with the newest metadata "
                 "timestamp is used; if no report has a readable timestamp, the one with the most "
                 "reports is used. The log names that file and the field read. When more than one "
                 "version and build is seen it lists each with its report count. Used marks the row "
                 "whose version was used, Field says which value the newest report of that row was read "
                 "from, and Newest Report Time is that report's metadata timestamp in UTC. The version "
                 "is the one the newest report names; the device may have updated after that report. "
                 "Evidence: on a private iOS 27.2.1 extraction where no version file gave a version, the "
                 "version and build read here matched the known data for the device, and the "
                 "Photos.sqlite artifacts in the test profile then queried the database. On "
                 "iphone11_ios17, abe_ios16, ctf2020_ios12, dexter_ios18 and falken_ios26 the version "
                 "files gave the version and the fallback was not run. Read on their diagnostic reports "
                 "alone (falken_ios26 by a run of this artifact, abe_ios16 and ctf2020_ios12 by a script "
                 "using its functions), the newest report matched that version on abe_ios16 (16.5), "
                 "ctf2020_ios12 (12.4) and falken_ios26 (26.2.1). On the four bug_type 309 reports (two on "
                 "abe_ios16, two on falken_ios26) the body osVersion and the metadata os_version gave the "
                 "same version and build. falken_ios26 holds 64 reports of 26.2 and 18 of 26.2.1, and "
                 "the newest named 26.2.1. iphone11_ios17 and dexter_ios18 hold no .ips file in that "
                 "folder, so this fallback would give them no version.",
        "paths": ('*/Library/Logs/CrashReporter/*.ips',),
        "output_types": "standard",
        "artifact_icon": "git-commit",
    }
}

import re

from scripts.ilapfuncs import artifact_processor, device_info, iOS, logfunc
from scripts.artifacts.iosDiagnosticReports import _ips_files, _json_body, _offset_ts, _split

_VERSION = re.compile(r'^(?P<platform>.*?)\s*(?P<version>\d+(?:\.\d+)+)\s*(?:\((?P<build>[^)]*)\))?\s*$')


def _parse(text):
    '''(version, build) from "iPhone OS 26.2.1 (23C71)" or "iPhone OS 26.2.1", else None.'''
    match = _VERSION.match(str(text or '').strip())
    if not match:
        return None
    return match.group('version'), (match.group('build') or '').strip()


def _report_version(meta, body, path):
    '''(version, build, field) for one report, else None.'''
    if str(meta.get('bug_type')) == '309':
        report = _json_body(body, path)
        os_version = report.get('osVersion') if isinstance(report, dict) else None
        if isinstance(os_version, dict) and os_version.get('train'):
            parsed = _parse(os_version.get('train'))
            if parsed:
                build = str(os_version.get('build') or parsed[1])
                return parsed[0], build, 'osVersion (body)'
    parsed = _parse(meta.get('os_version'))
    if parsed:
        return parsed[0], parsed[1], 'os_version (metadata)'
    return None


@artifact_processor
def ios_version_diagnostic_reports(context):
    groups = {}
    unread = 0
    for path, _ in _ips_files(context):
        meta, body = _split(path, log=False)
        found = _report_version(meta, body, path) if meta else None
        if not found:
            unread += 1
            continue
        version, build, field = found
        when = _offset_ts(meta.get('timestamp'))
        group = groups.setdefault((version, build), {'count': 0, 'newest': None,
                                                     'newest_path': path, 'newest_field': field})
        group['count'] += 1
        if when and (group['newest'] is None or when > group['newest']):
            group['newest'], group['newest_path'], group['newest_field'] = when, path, field

    if unread:
        logfunc(f'{unread} diagnostic report(s) gave no readable iOS version')
    if not groups:
        logfunc('No diagnostic report gave an iOS version. The iOS version is still unknown.')
        return (), [], ''

    def rank(item):
        newest = item[1]['newest']
        return (newest is not None, newest.timestamp() if newest else 0, item[1]['count'])

    used_key, used = max(groups.items(), key=rank)
    version, build = used_key
    source = used['newest_path']
    if not iOS.get_version():
        # A reader that found an empty version stored '', and set_version replaces only None.
        iOS._version = None  # pylint: disable=protected-access
    iOS.set_version(version)
    context.set_installed_os_version(version)
    which = ('the newest diagnostic report' if used['newest'] is not None
             else 'a diagnostic report with no readable timestamp')
    logfunc(f'iOS version: {version} (build {build or "not given"}), from {used["newest_field"]} '
            f'of {which}, {context.get_relative_path(source)}')
    if len(groups) > 1:
        seen = '; '.join(f'{v} ({b}): {g["count"]}' for (v, b), g in sorted(groups.items()))
        reason = ('The newest report decides.' if used['newest'] is not None
                  else 'No report has a readable timestamp, so the pair with the most reports decides.')
        logfunc(f'Diagnostic reports name {len(groups)} iOS version and build pairs, with report counts: '
                f'{seen}. {reason}')
    device_info('Device Information', 'iOS version', version, source)
    if build:
        device_info('Device Information', 'ProductBuildVersion', build, source)

    data_list = []
    ordered = sorted(groups.items(), key=rank, reverse=True)
    for (row_version, row_build), group in ordered:
        data_list.append((group['newest'] or '', row_version, row_build, group['newest_field'],
                          group['count'], context.get_relative_path(group['newest_path']),
                          'Yes' if (row_version, row_build) == used_key else 'No'))
    data_headers = (('Newest Report Time', 'datetime'), 'iOS Version', 'Build', 'Field', 'Report Count',
                    'Newest Report', 'Used')
    return data_headers, data_list, '\n'.join(group['newest_path'] for _, group in ordered)
