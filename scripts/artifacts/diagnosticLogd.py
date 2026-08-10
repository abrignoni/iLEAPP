__artifacts_v2__ = {
    "diagnosticLogdEvents": {
        "name": "Diagnostic Logd Time Zone and Shutdown Events",
        "description": "Explicit time-zone-change and shutdown-related records from logd.0.log",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-07-29",
        "last_update_date": "2026-07-29",
        "requirements": "none",
        "category": "System Activity",
        "notes": (
            "The report converts the offset-bearing log timestamp to UTC and preserves the "
            "recorded offset. A time-zone-change line does not identify the destination time "
            "zone. Shutdown-related records should be correlated with other evidence and are "
            "not, alone, proof of a user-initiated shutdown or device wipe. Research reference: "
            "https://cellebrite.com/en/blog/upgrade-from-null-detecting-ios-wipe-artifacts/"
        ),
        "paths": ("*/private/var/db/diagnostics/logd.0.log",),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "timezone",
        "sample_data": {
            "fsfull002_ios17": "iOS 17.1 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 13 rows",
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
            "jess_ios15": "iOS 15.0.2 | 1 row",
            "otto_ios17": "iOS 17.5.1 | 9 rows",
        },
    }
}

import re
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, logfunc


_LINE_RE = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
    r"(?P<offset>[+-]\d{4})\s+"
    r"(?P<process>[^\s\[]+)\[(?P<pid>\d+)\]:\s*(?P<message>.*)$"
)
_TIME_ZONE_MESSAGE = "Time zone changed, updating file headers"
_SHUTDOWN_RE = re.compile(r"\b(?:shut\s+down|shutdown|shutting\s+down)\b", re.IGNORECASE)


def _parse_logd_line(line):
    match = _LINE_RE.match(line.rstrip())
    if not match:
        return None

    message = match.group("message")
    if _TIME_ZONE_MESSAGE in message:
        event_type = "Time zone changed"
    elif _SHUTDOWN_RE.search(message):
        event_type = "Shutdown-related log entry"
    else:
        return None

    try:
        recorded = datetime.strptime(
            f"{match.group('timestamp')}{match.group('offset')}",
            "%Y-%m-%d %H:%M:%S%z",
        )
    except ValueError:
        return None

    return (
        recorded.astimezone(timezone.utc),
        match.group("offset"),
        event_type,
        match.group("process"),
        int(match.group("pid")),
        message,
    )


@artifact_processor
def diagnosticLogdEvents(context):
    data_headers = (
        ("Timestamp (UTC)", "datetime"),
        "Recorded UTC Offset",
        "Event",
        "Process",
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
                    parsed = _parse_logd_line(line)
                    if parsed:
                        data_list.append((*parsed, line_number, relative_path))
        except OSError as ex:
            logfunc(f"Failed to read diagnostic log {relative_path}: {ex}")
            continue
        sources.append(relative_path)

    return data_headers, data_list, "\n".join(dict.fromkeys(sources))
