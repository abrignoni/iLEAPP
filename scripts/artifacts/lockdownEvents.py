__artifacts_v2__ = {
    "lockdownEvents": {
        "name": "Lockdownd Events",
        "description": "Passcode-change callbacks, upgrade detections, and lockdownd startup records",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-07-29",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "System Activity",
        "notes": (
            "Timestamps are stored without a UTC offset and are reported as stored text "
            "in a column headed Timestamp (as stored, no offset); the zone is not established. "
            "One row on iphone11_ios17 and dexter_ios18 carries a reading the former "
            "parser dates 1969-12-31. A lockdownd startup record shows that the daemon started; "
            "it is not, by itself, proof that the device booted. Event selection is based on "
            "research by Ian Whiffin, 'KnowledgeC (and Friends)'. A line containing roll_keys: "
            "Detected upgrade is labelled Upgrade detected by lockdownd, except that a line "
            "containing Detected upgrade from (NULL) is labelled Upgrade detected by lockdownd, "
            "from (NULL). The cited research reads the from (NULL) form as setup after a wipe; "
            "that reading was not tested here, and no line of that form was counted on the "
            "listed images. Reference: "
            "https://doubleblak.com/blogPost.php?k=knowledgec"
        ),
        "paths": ("*/private/var/logs/lockdownd.log", "*/private/var/logs/lockdownd.log.*"),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "lock",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 2 rows",
            "dexter_ios18": "iOS 18.3.2 | 38 rows",
            "felix_ios17": "iOS 17.6.1 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 48 rows",
            "otto_ios17": "iOS 17.5.1 | 10 rows",
        },
    }
}

import re
from datetime import datetime

from scripts.ilapfuncs import artifact_processor, logfunc


_LINE_RE = re.compile(
    r"^(?P<timestamp>\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d+)"
    r"\s+pid=(?P<pid>\d+)\s+(?P<message>.*)$"
)
# Order matters: the first marker found in the message decides the label, so the
# narrower from (NULL) form is tested before the general upgrade marker.
_EVENT_MARKERS = (
    ("password_changed_callback", "Device passcode changed"),
    ("Detected upgrade from (NULL)", "Upgrade detected by lockdownd, from (NULL)"),
    ("roll_keys: Detected upgrade", "Upgrade detected by lockdownd"),
    ("main: Starting Up", "Lockdownd startup"),
)


def _parse_lockdown_line(line):
    match = _LINE_RE.match(line.rstrip())
    if not match:
        return None

    message = match.group("message")
    event_type = next(
        (label for marker, label in _EVENT_MARKERS if marker in message),
        None,
    )
    if event_type is None:
        return None

    try:
        datetime.strptime(
            match.group("timestamp"), "%m/%d/%y %H:%M:%S.%f"
        )
    except ValueError:
        return None

    return match.group("timestamp"), event_type, int(match.group("pid")), message


@artifact_processor
def lockdownEvents(context):
    data_headers = (
        "Timestamp (as stored, no offset)",
        "Event",
        "PID",
        "Log Message",
        "Line Number",
        "Source File",
    )
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        relative_path = context.get_relative_path(file_found)
        try:
            with open(file_found, "r", encoding="utf-8", errors="replace") as log_file:
                for line_number, line in enumerate(log_file, 1):
                    parsed = _parse_lockdown_line(line)
                    if parsed:
                        data_list.append((*parsed, line_number, relative_path))
        except OSError as ex:
            logfunc(f"Failed to read lockdownd log {relative_path}: {ex}")
            continue
        sources.append(relative_path)

    return data_headers, data_list, "\n".join(dict.fromkeys(sources))
