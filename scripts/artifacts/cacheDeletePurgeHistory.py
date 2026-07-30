# Cache Delete Purge History
# Author: @Jadoo4QFan, with the assistance of an unknown routed AI model
# Based on The Apple Wiki : CacheDeletePurgeHistory.txt

__artifacts_v2__ = {
    "cacheDeletePurgeHistory": {
        "name": "CacheDelete Purge History",
        "description": "Parses CacheDeletePurgeHistory.txt — a headerless, pipe-delimited log of recent CacheDelete purge events (timestamp, target directory, urgency, available space, purged bytes, duration).",
        "author": "@Jadoo4QFan", 
        "creation_date": "2026-07-26",
        "last_update_date": "2026-07-26",
        "requirements": "none",
        "category": "System",
        "notes": (
            "File location: /private/var/mobile/Library/Caches/com.apple.cache_delete/CacheDeletePurgeHistory.txt, or /logs/CacheDelete/CacheDeletePurgeHistory.txt if written in a sysdiagnose"
            "Present in FFS extractions and sysdiagnoses. Headerless TSV with '|' delimiter. "
            "Timestamps prefixed with 'P' (likely 'purge'). Urgency: 1=routine, 3=critical; 2/4+ unknown. "
            "Available space and purged amount are in bytes; duration is in seconds. "
            "Reference: Apple Wiki (Filesystem:/private/var/mobile/Library/Caches/com.apple.cache_delete/CacheDeletePurgeHistory.txt)"
        ),
        "paths": ('*/CacheDeletePurgeHistory.txt',),
        "output_types": "standard",
        "artifact_icon": "trash-2",
        },
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, logfunc
from datetime import datetime, timezone


@artifact_processor
def cacheDeletePurgeHistory(context):
    """Parse CacheDeletePurgeHistory.txt (pipe-delimited, headerless) and return structured purge events."""
    files_found = [
        x for x in context.get_files_found()
        if not str(x).endswith(('-wal', '-shm', '-journal'))
    ]
    source_path = get_file_path(files_found, "CacheDeletePurgeHistory.txt")

    # Initialize headers so framework always has column definitions
    data_headers = (
        ('Timestamp', 'datetime'),
        'Target Directory',
        'Urgency Level',
        'Available Space (bytes)',
        'Purged Amount (bytes)',
        'Duration (seconds)',
    )

    # Return empty result set if file not found (framework logs "No data found" automatically)
    if not source_path:
        return data_headers, [], ""

    source_path = str(source_path)
    data_list = []

    try:
        with open(source_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Split on '|' delimiter
                parts = line.split('|')

                # Pad short lines to avoid index errors; ignore extra fields beyond 6
                while len(parts) < 6:
                    parts.append('')
                parts = parts[:6]

                # --- Timestamp (field 0) ---
                ts_raw = parts[0].strip()
                timestamp_display = ts_raw
                dt_obj = None
                if ts_raw.startswith('P'):
                    ts_raw = ts_raw[1:]

                try:
                    # Apple Wiki format: 2025-11-04 04:57:31.324150
                    dt_obj = datetime.strptime(ts_raw, "%Y-%m-%d %H:%M:%S.%f")
                    # Treat as UTC for consistent forensics reporting
                    dt_obj = dt_obj.replace(tzinfo=timezone.utc)
                    timestamp_display = dt_obj  # framework handles datetime objects
                except ValueError:
                    # Fallback: keep original stripped string for visibility
                    timestamp_display = ts_raw
                    logfunc(f"cacheDeletePurgeHistory: could not parse timestamp '{ts_raw}'")

                # --- Target directory (field 1) ---
                target_dir = parts[1].strip()

                # --- Urgency level (field 2) ---
                urgency_raw = parts[2].strip()
                # Apple Wiki mapping: 1=routine, 3=critical; 2/4+ unknown
                urgency_map = {
                    "1": "Routine (1)",
                    "3": "Critical (3)",
                }
                urgency_level = urgency_map.get(urgency_raw, f"Unknown ({urgency_raw})" if urgency_raw else "Unknown")

                # --- Available system space (bytes) (field 3) ---
                available_raw = parts[3].strip()
                available_space = available_raw
                try:
                    available_space = int(available_raw)
                except ValueError:
                    pass

                # --- Purged amount (bytes) (field 4) ---
                purged_raw = parts[4].strip()
                purged_amount = purged_raw
                try:
                    purged_amount = int(purged_raw)
                except ValueError:
                    pass

                # --- Duration (seconds) (field 5) ---
                duration_raw = parts[5].strip()
                duration = duration_raw
                try:
                    # Float to preserve sub-second precision
                    duration = float(duration_raw)
                except ValueError:
                    pass

                data_list.append((
                    timestamp_display,
                    target_dir,
                    urgency_level,
                    available_space,
                    purged_amount,
                    duration,
                ))

    except Exception as exc:
        logfunc(f"cacheDeletePurgeHistory: error reading {source_path}: {exc}")
        # Return empty list with headers so framework produces a clean report row
        return data_headers, [], source_path

    return data_headers, data_list, source_path
