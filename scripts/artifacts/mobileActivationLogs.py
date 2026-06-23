__artifacts_v2__ = {
    "mobileActivationLogs": {
        "name": "Mobile Activation Logs",
        "description": "Upgrade and Mobile Activation Startup events parsed from mobileactivationd.log "
                       "(including logs found inside sysdiagnose archives)",
        "author": "@AlexisBrignoni",
        "version": "2.0",
        "date": "2026-06-23",
        "requirements": "none",
        "category": "Mobile Activation Logs",
        "notes": "",
        "paths": ('**/mobileactivationd.log*', '**/sysdiagnose_*.tar.gz'),
        "output_types": "standard",
        "artifact_icon": "settings"
    }
}

import io
import re
import tarfile
from datetime import datetime, timezone
from pathlib import Path

from scripts.ilapfuncs import artifact_processor

_DATE_RE = re.compile(r'(([A-Za-z]+[\s]+([a-zA-Z]+[\s]+[0-9]+)[\s]+([0-9]+\:[0-9]+\:[0-9]+)[\s]+'
                      r'([0-9]{4}))([\s]+[\[\d\]]+[\s]+[\<a-z\>]+[\s]+[\(\w\)]+[\s]+[A-Z]{2}\:[\s]+)'
                      r'([main\:\s]*.*)$)')
_UPGRADE_RE = re.compile(r'((.*)(Upgrade\s+from\s+[\w]+\s+to\s+[\w]+\s+detected\.$))')
_TAR_MEMBER_RE = re.compile(r"logs/MobileActivation/mobileactivationd\.log(\.\d+)?$")
_STARTUP = '____________________ Mobile Activation Startup _____________________'


def _iter_logs(files_found):
    """Yield (log_name, lines, source_full_path) for mobileactivationd.log files and those in sysdiagnose tars."""
    for filename in files_found:
        filename = str(filename)
        if 'mobileactivationd.log' in filename:
            path = filename[4:] if filename.startswith('\\\\?\\') else filename
            try:
                with open(path, 'r', encoding='utf8', errors='ignore') as fp:
                    lines = fp.readlines()
            except OSError:
                continue
            yield Path(path).name, lines, filename
        elif 'sysdiagnose_' in filename and 'IN_PROGRESS_' not in filename:
            try:
                tar = tarfile.open(filename)
            except (tarfile.TarError, OSError):
                continue
            try:
                for member in tar.getmembers():
                    if not _TAR_MEMBER_RE.search(member.name):
                        continue
                    extracted = tar.extractfile(member)
                    if extracted is not None:
                        with io.TextIOWrapper(extracted, encoding='utf-8', errors='ignore') as tfp:
                            yield member.name, tfp.readlines(), filename
            finally:
                tar.close()


@artifact_processor
def mobileActivationLogs(context):
    data_headers = (('Datetime', 'datetime'), 'Event', 'Log Name')
    data_list = []
    source_files = []

    for log_name, lines, source in _iter_logs(context.get_files_found()):
        if source not in source_files:
            source_files.append(source)
        for linecount, line in enumerate(lines, 1):
            match = _DATE_RE.match(line)
            if not match:
                continue
            try:
                dtime_obj = datetime.strptime(' '.join(match.group(3, 5, 4)),
                                              '%b %d %Y %H:%M:%S').replace(tzinfo=timezone.utc)
            except ValueError:
                continue
            values = match.group(7)
            if 'perform_data_migration' in values:
                upgrade_match = _UPGRADE_RE.search(values)
                if upgrade_match:
                    data_list.append((dtime_obj, upgrade_match.group(3), log_name))
            if _STARTUP in values:
                data_list.append((dtime_obj, f'Mobile Activation Startup at line: {linecount}', log_name))

    source_path = ', '.join(context.get_relative_path(s) for s in source_files)
    return data_headers, data_list, source_path
