"""
Waze Artifact Module
Parses and extracts Waze iOS artifacts including Account, Session Info,
Track GPS Quality, Search History, Recent/Favorite/Shared Locations,
Planned Events, and Text-To-Speech Navigation.
"""
# pylint: disable=too-many-lines

__artifacts_v2__ = {
    "waze_account": {
        "name": "Waze - Account",
        "description": "Parses and extracts account information",
        "author": "@djangofaiola",
        "creation_date": "2024-02-02",
        "last_update_date": "2026-06-22",
        "requirements": "none",
        "category": "Waze",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Preferences/com.waze.iphone.plist"),
        "output_types": [ "standard" ],
        "html_columns": [ "Profile Picture URL" ],
        "artifact_icon": "user"
    },
    "waze_session_info": {
        "name": "Waze - Session Info",
        "description": "Parses and extracts session information",
        "author": "@djangofaiola",
        "creation_date": "2024-02-02",
        "last_update_date": "2026-06-22",
        "requirements": "none",
        "category": "Waze",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Preferences/com.waze.iphone.plist"),
        "output_types": [ "all" ],
        "artifact_icon": "navigation-2"
    },
    "waze_track_gps_quality": {
        "name": "Waze - Track GPS Quality",
        "description": "Parses and extracts track GPS quality information",
        "author": "@djangofaiola",
        "creation_date": "2024-02-02",
        "last_update_date": "2026-06-22",
        "requirements": "none",
        "category": "Waze",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Documents/spdlog.*logdata"),
        "output_types": [ "all" ],
        "artifact_icon": "navigation-2"
    },
    "waze_search_history": {
        "name": "Waze - Search History",
        "description": "Parses and extracts searched locations information",
        "author": "@djangofaiola",
        "creation_date": "2024-02-02",
        "last_update_date": "2026-06-22",
        "requirements": "none",
        "category": "Waze",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Preferences/com.waze.iphone.plist"),
        "output_types": [ "all" ],
        "artifact_icon": "search"
    },
    "waze_recent_locations": {
        "name": "Waze - Recent Locations",
        "description": "Parses and extracts recent locations information",
        "author": "@djangofaiola",
        "creation_date": "2024-02-02",
        "last_update_date": "2026-06-22",
        "requirements": "none",
        "category": "Waze",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Preferences/com.waze.iphone.plist"),
        "output_types": [ "all" ],
        "artifact_icon": "map-pin"
    },
    "waze_favorite_locations": {
        "name": "Waze - Favorite Locations",
        "description": "Parses and extracts favorite locations information",
        "author": "@djangofaiola",
        "creation_date": "2024-02-02",
        "last_update_date": "2026-06-22",
        "requirements": "none",
        "category": "Waze",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Preferences/com.waze.iphone.plist"),
        "output_types": [ "all" ],
        "artifact_icon": "star"
    },
    "waze_shared_locations": {
        "name": "Waze - Shared Locations",
        "description": "Parses and extracts shared locations information",
        "author": "@djangofaiola",
        "creation_date": "2024-02-02",
        "last_update_date": "2026-06-22",
        "requirements": "none",
        "category": "Waze",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Preferences/com.waze.iphone.plist"),
        "output_types": [ "all" ],
        "artifact_icon": "map-pin"
    },
    "waze_planned_events": {
        "name": "Waze - Planned Events",
        "description": "Parses and extracts synchronized calendar events and planned trips.",
        "author": "@djangofaiola",
        "creation_date": "2026-06-13",
        "last_update_date": "2026-06-22",
        "requirements": "none",
        "category": "Waze",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Preferences/com.waze.iphone.plist"),
        "output_types": [ "all" ],
        "html_columns": [ "Image URL" ],
        "artifact_icon": "calendar"
    },
    "waze_tts": {
        "name": "Waze - Text-To-Speech Navigation",
        "description": "Parses and extracts text-to-speech navigation information",
        "author": "@djangofaiola",
        "creation_date": "2024-02-02",
        "last_update_date": "2026-06-22",
        "requirements": "none",
        "category": "Waze",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Preferences/com.waze.iphone.plist"),
        "output_types": [ "standard" ],
        "artifact_icon": "volume-2"
    }
}

import re
import html
import sqlite3
from pathlib import Path
from urllib.parse import urlparse
from math import log10
import blackboxprotobuf
from scripts.ilapfuncs import open_sqlite_db_readonly, get_sqlite_db_records, \
    does_column_exist_in_db, get_txt_file_content, convert_unix_ts_to_utc, \
    artifact_processor, logfunc

# Constants
COMMA_SEP = ', '
WAZE_PREFERENCES_PLIST = 'com.waze.iphone.plist'
SOURCE_FILE_NAME = 'Source File Name'
SOURCE_PATH_NOTE = f"Refer to the '{SOURCE_FILE_NAME}' column to identify the exact " \
                   "device location of the origin file."
MAX_URL_LENGTH = 4096
ALLOWED_URL_SCHEMES = (
    'http',
    'https',
    'mailto',
    'tel'
)
# Cached protobuf state
WAZE_CACHED_DATA = {
    'data': None,
    'path': None
}
UUID_RE = re.compile(
    r"^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}"
    r"-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$"
)
APPDOMAIN_RE = re.compile(r"^AppDomain-(.+)$")
BUNDLE_ID_RE = re.compile(
    r"^[a-zA-Z][a-zA-Z0-9\-]*(\.[a-zA-Z0-9][a-zA-Z0-9\-]*){1,}$"
)
LINE_PATTERN_USER_RE = re.compile(
    r"^\s*(Realtime|General|App Launch)\s*([^:\r\n]+?)\s*:\s*(.+?)\s*$"
)
LINE_PATTERN_SESSION_RE = re.compile(
    r"^\s*([A-Za-z_]+(?:\s[A-Za-z_]+)*)\s*([^:\r\n]+?)\s*:\s*(.+?)\s*$"
)
TTS_TABLE_NAME_RE = re.compile(r"^[A-Za-z0-9_]+$")

# GPS_QUALITY for legacy C++ format
LINE_PATTERN_GPS_RE = re.compile(r"STAT\(buffer#[\d]{1,2}\)\sGPS_QUALITY\s")
VALUES_PATTERN_GPS_RE = re.compile(r"(?<=\{)(.*?)(?=\})")

LEGACY_GPS_RE = re.compile(
    r"\[(?P<log_time>[0-9:.]+)\s+.*GPS_QUALITY\s+"
    r"\{LAT=(?P<lat>-?[0-9]+)\}\{LON=(?P<lon>-?[0-9]+)\}"
    r".*\{SAMPLE_COUNT=(?P<sam_cnt>[0-9]+)\}"
    r".*\{BAD_SAMPLE_COUNT=(?P<bad_cnt>[0-9]+)\}"
    r".*\{DUP_SAMPLE_COUNT=(?P<dup_cnt>[0-9]+)\}"
    r".*\{ACC_AVG=(?P<acc_avg>[0-9]+)\}"
    r".*\{ACC_MIN=(?P<acc_min>[0-9]+)\}"
    r".*\{ACC_MAX=(?P<acc_max>[0-9]+)\}"
    r".*\{PROVIDER=(?P<prov>[A-Za-z0-9_]+)\}"
    r".*\{TIMESTAMP_MS=(?P<ts_ms>[0-9]+)\}"
)

# GPS_QUALITY for new SWIFT payload format blocks
# Step 1: matches the WCEWazeAppEvent block opener line
WAZE_EVENT_RE   = re.compile(r"WCEWazeAppEvent")
# Step 2: matches the 'gps_quality {' line nested inside the block
GPS_BLOCK_RE    = re.compile(r"^\s*gps_quality\s*\{")
SWIFT_LAT_RE = re.compile(r"latitude:\s*([0-9.-]+)")
SWIFT_LON_RE = re.compile(r"longitude:\s*([0-9.-]+)")
SWIFT_SAM_CNT_RE = re.compile(r"sample_count:\s*([0-9]+)")
SWIFT_BAD_CNT_RE = re.compile(r"bad_sample_count:\s*([0-9]+)")
SWIFT_DUP_CNT_RE = re.compile(r"dup_sample_count:\s*([0-9]+)")
SWIFT_ACC_AVG_RE = re.compile(r"accuracy_avg_meters:\s*([0-9]+)")
SWIFT_ACC_MIN_RE = re.compile(r"accuracy_min_meters:\s*([0-9]+)")
SWIFT_ACC_MAX_RE = re.compile(r"accuracy_max_meters:\s*([0-9]+)")
SWIFT_PROV_RE = re.compile(r"position_provider:\s*(\S+)")
SWIFT_SEC_RE = re.compile(r"seconds:\s*([0-9]+)")
SWIFT_NANOS_RE = re.compile(r"nanos:\s*([0-9]+)")

GPS_DEDUP_WINDOW_MS = 250

# Field name constants for clarity and maintainability
F_DEVICE_PATH = 'device_path'
F_LOCATION = 'location'
F_TAG = 'tag'
F_FIRST_USE = 'first_use'
F_FIRST_NAME = 'first_name'
F_LAST_NAME = 'last_name'
F_USER_NAME = 'user_name'
#F_NICKNAME = 'nickname'
F_PIC_URL = 'profile_picture_url'
F_EMAIL = 'email'
F_WAZE_ID = 'waze_id'
F_INVISIBLE_MODE = 'invisible_mode'
F_LAST_LAUNCH = 'last_launch'
F_PROVIDER_FIRST_NAME = 'provider_first_name'
F_PROVIDER_LAST_NAME = 'provider_last_name'
F_PROVIDER_NAME = 'provider_name'
F_PROVIDER_UID = 'provider_user_id'
F_SHARED = 'shared'
F_NAME = 'name'
F_LOCATION_TYPE = 'location_type'
F_LAT = 'lat'
F_LON = 'lon'
F_CREATED = 'created'
F_MODIFIED = 'modified'
F_LAST_ACCESS = 'last_access'
F_PLACE_NAME = 'place_name'
F_HOUSE_NUM = 'house_num'
F_STREET = 'street'
F_CITY = 'city'
F_STATE = 'state'
F_COUNTRY = 'country'
F_SERVER_ID = 'server_id'
F_RANK = 'rank'
F_SHARED_ID = 'shared_id'
F_UPDATED = 'updated'
F_VENUE_ID = 'venue_id'
F_RESIDENTIAL_STATUS = 'residential_status'
F_TIMESTAMP = 'timestamp'
F_TIMESTAMP_MS = 'timestamp_ms'
F_SAMPLE_COUNT = 'sample_count'
F_BAD_SAMPLE_COUNT = 'bad_sample_count'
F_DUP_SAMPLE_COUNT = 'dup_sample_count'
F_AVG_ACCURACY = 'avg_accuracy'
F_MIN_ACCURACY = 'min_accuracy'
F_MAX_ACCURACY = 'max_accuracy'
F_PROVIDER = 'provider'
F_LAST_TS = 'last_lat_ts'
F_COURSE = 'course'
F_LAST_DEST_LAT = 'last_dest_lat'
F_LAST_DEST_LON = 'last_dest_lon'
F_LAST_DEST_NAME = 'last_dest_name'
F_LAST_DEST_VENUE_NAME = 'last_dest_venue_name'
F_LAST_SYNCED = 'last_synced'
F_LAST_WAYPOINT_ACCESS = 'last_waypoint_access'
F_CONTEXT = 'context'
F_IMAGE_ID = 'image_id'
F_EVENT_ID = 'event_id'
F_EVENT_TYPE = 'event_type'
F_EVENT_NAME = 'event_name'
F_START_TIME = 'start_time'
F_END_TIME = 'end_time'
F_ALL_DAY = 'all_day'
F_IMAGE_URL = 'image_url'
F_ORIGIN_PLACE = 'origin_place_id'

def get_device_file_path(file_path: str, context) -> str:
    """
    Converts a local report file path back to the original iOS device path.
    Strips the local report base directory and reconstructs the /private/var 
    structure for File System extractions or preserves Domain paths for iTunes.
    Version 1.0
    """

    if not file_path:
        return ''

    # Retrieve the seeker from the context to access the local data_folder
    seeker = context.get_seeker()

    # The data_folder is the root where the seeker extracted the files (e.g., E:/Case/Data/)
    base_folder = getattr(seeker, 'data_folder', '')

    # Standardize separators to forward slashes for cross-platform consistency
    norm_file_path = file_path.replace('\\', '/')
    norm_base_folder = base_folder.replace('\\', '/')

    # Check if the file is within the report's data directory
    if norm_base_folder and norm_file_path.startswith(norm_base_folder):
        # Strip the local PC base path to get the relative extraction path
        relative_path = norm_file_path[len(norm_base_folder):].lstrip('/')

        # Case 1: Path starts with 'var/' but is missing the 'private/' prefix.
        # In iOS forensics, /private/var/ is the canonical physical path.
        if relative_path.startswith('var/') and not relative_path.startswith('private/var/'):
            return '/private/' + relative_path

        # Case 2: Path already contains standard iOS system roots.
        # We add a leading slash to represent the root of the device.
        ios_system_roots = ('private/', 'Library/', 'System/', 'Developer/', 'usr/')
        if relative_path.startswith(ios_system_roots):
            return '/' + relative_path

        # Case 3: iTunes Backup Domains (e.g., AppDomain-com.apple.mobilesafari).
        # These are kept relative as they don't represent a direct file system root.
        return relative_path

    # Fallback: if the path is outside the data folder, return the cleaned input path
    return norm_file_path.lstrip('/')


def format_url(str_url: str | None, html_format: bool = False, label: str | None = None) -> str:
    """
    Safely renders a raw URL extracted from forensic evidence.
    Supports an optional label for display purposes.
    Version 1.0

    Forensic principles:
    - The original URL value is NEVER altered (only whitespace stripping)
    - No normalization, no scheme injection, no correction
    - Clickability is determined strictly from the raw URL

    Behavior:
    - Return empty string when the URL is None, empty, or null-like
    - When a label is provided and the URL is missing, return the label as-is
    - Strip surrounding whitespace only (preserves internal structure)
    - Log and truncate pathological inputs exceeding MAX_URL_LENGTH
    - Determine clickability by parsing the scheme as-is
    - Allow clickable links only for schemes in ALLOWED_URL_SCHEMES
    - HTTP/HTTPS links require a hostname to be considered clickable
    - Unsupported or malformed URLs are rendered as plain text (evidence preserved)

    HTML rendering (html_format=True):
    - Escape all output to prevent XSS
    - Add rel="noopener noreferrer" to prevent tabnabbing
    - Render clickable URLs as <a href="...">label-or-url</a>
    - Render non-clickable URLs as escaped plain text
    - When a label is provided, it replaces the visible text but NEVER alters the URL

    Plain-text rendering:
    - When clickable and a label is provided: "label (url)"
    - When clickable and no label is provided: "url"
    - When non-clickable: return label or raw URL as plain text
    """

    # Missing URL: return label or empty
    if not str_url:
        if not label:
            return ''
        return html.escape(label, quote=False) if html_format else label

    # Strip surrounding whitespace only — no other alteration
    s = str(str_url).strip()

    # Treat literal null-like values as missing
    if s.lower() in ('null', 'none'):
        return label or ''

    # Log and truncate pathological inputs — do not silently discard
    if len(s) > MAX_URL_LENGTH:
        logfunc(f"Warning - format_url URL exceeds maximum length: {s[:80]}...")
        s = s[:MAX_URL_LENGTH]

    # Determine clickability by parsing the URL as-is (no modification)
    is_clickable = False
    try:
        parsed = urlparse(s)
        scheme = parsed.scheme.lower()

        if scheme in ALLOWED_URL_SCHEMES:
            # HTTP/HTTPS must have a hostname to be safely clickable
            if scheme in ('http', 'https') and not parsed.netloc:
                is_clickable = False
            else:
                is_clickable = True

    except (ValueError, TypeError, AttributeError) as ex:
        logfunc(f"Error - format_url parse failed for {str_url!r}: {ex}")

    # Visible text: label or raw URL
    visible = label if label else s

    # HTML rendering
    if html_format:
        safe_text = html.escape(visible, quote=False)

        if is_clickable:
            safe_href = html.escape(s, quote=True)
            return (
                f'<a href="{safe_href}" target="_blank" '
                f'rel="noopener noreferrer">{safe_text}</a>'
            )

        # Non-clickable: return escaped plain text — evidence preserved
        return safe_text

    # Plain text rendering
    if is_clickable and label:
        return f"{visible} ({s})"

    # Plain text: return stripped original
    return s


def get_app_id(plist_file, context) -> str:
    """
    Extract the application identifier from an iOS container path.
    Version 1.0

    Supports three extraction modes:

    - File System extraction: path contains a UUID segment
      (e.g. Containers/Data/Application/<UUID>/)
        -> returns the UUID string.

    - iTunes/Finder Backup (raw): path contains an AppDomain segment
      (e.g. AppDomain-com.waze.iphone/)
        -> returns the bundle identifier extracted from the domain prefix.

    - iTunes/Finder Backup (normalized): the extraction tool has rewritten
      the AppDomain segment to a plain bundle identifier in filesystem form
      (e.g. Containers/Data/Application/com.waze.iphone/)
        -> returns the bundle identifier directly.

    Args:
        plist_file (str): The name of the file to locate
                          (e.g., 'com.waze.iphone.plist').
        context: The artifact context object.

    Returns:
        str: UUID, or bundle identifier (backup), if found;
             otherwise an empty string.
    """

    func_name = get_app_id.__name__

    try:
        source_path_str = context.get_source_file_path(plist_file)
        if not source_path_str:
            logfunc(f"[{context.get_artifact_name()}] Error - {func_name}: "
                    f"{plist_file} not found in context")
            return ''

        parts = Path(source_path_str).parts
        bundle_id_candidate = ''

        for part in parts:
            # Priority 1 — file system UUID
            if UUID_RE.match(part):
                return part

            # Priority 2 — raw backup AppDomain prefix
            m = APPDOMAIN_RE.match(part)
            if m:
                return m.group(1)

            # Priority 3 — normalized backup bundle ID (keep first match only)
            if not bundle_id_candidate and BUNDLE_ID_RE.match(part):
                # Exclude filenames: a path component with a known file
                # extension is not a container identifier
                if Path(part).suffix not in ('.plist', '.db', '.sqlite'):
                    bundle_id_candidate = part

        if bundle_id_candidate:
            return bundle_id_candidate

        logfunc(f"[{context.get_artifact_name()}] Error - {func_name}: "
                f"No UUID, AppDomain, or bundle ID found in path for {plist_file}")

    except (ValueError, AttributeError, IndexError) as ex:
        logfunc(f"[{context.get_artifact_name()}] Error - {func_name} failed "
                f"while processing {plist_file}: {ex}")

    return ''


def split_coordinates(value: str | None, divisor: int | float = 1.0,
                      swap: bool = False) -> tuple[str, str]:
    """
    Splits coordinates stored as 'longitude,latitude' and converts them
    using the provided divisor.
    Version 1.0

    Args:
        value (str|None): Coordinate string (e.g. "12345678,45678901")
        divisor (int|float): Conversion factor (e.g. 1_000_000.0)
        swap (bool): When False (default) the input is interpreted as
        'longitude,latitude'. When True, as 'latitude,longitude'.

    Returns:
        tuple: (latitude, longitude) as fixed-precision strings on success,
        or ('', '') if the input is invalid or cannot be parsed.
    """

    func_name = split_coordinates.__name__

    if value is None or divisor is None:
        return '', ''

    if divisor < 1:
        logfunc(f"Warning - {func_name}: divisor {divisor!r} < 1, reset to 1.0")
        divisor = 1.0

    # Derive decimal places from the divisor so the output precision reflects the natural
    # resolution of the source data.
    # e.g. 1_000_000.0 -> 6, 100_000.0 -> 5, 100.0 -> 2, 10.0 -> 1, 1.0 → 0
    decimal_places = max(0, round(log10(abs(divisor))))

    try:
        raw_lon, raw_lat = value.strip().split(',')
        raw_lat, raw_lon = (raw_lon, raw_lat) if swap else (raw_lat, raw_lon)

        latitude  = f"{float(raw_lat.strip()) / divisor:.{decimal_places}f}"
        longitude = f"{float(raw_lon.strip()) / divisor:.{decimal_places}f}"

        return latitude, longitude

    except ValueError as ex:
        # Catches: wrong number of components, non-numeric values
        logfunc(f"Warning - {func_name}: could not parse {value!r}: {ex}")
    except (TypeError, ArithmeticError) as ex:
        # Catches: unexpected type coercion failures, overflow
        logfunc(f"Warning - {func_name}: conversion error for {value!r}: {ex}")

    return '', ''


# Complete message_type schema for Waze cached_data
CACHED_DATA_MESSAGE_TYPE = {
    # account_root
    1: {
        'type': 'message',
        'name': 'account_root',
        'message_typedef': {
            # user_profile
            1: {
                'type': 'message',
                'name': 'user_profile',
                'message_typedef': {
                    1: {'type': 'string', 'name': 'first_name'},
                    2: {'type': 'string', 'name': 'last_name',
                        'message_typedef': {
                            1: {'type': 'string', 'name': 'value'},
                            9: {'type': 'int', 'name': 'ref_id'}
                        }
                    },
                    4: {'type': 'string', 'name': 'email'},
                    5: {'type': 'int', 'name': 'is_verified'},
                    9: {'type': 'int', 'name': 'ref_id'},   # last_name->ref_id
                    10: {'type': 'int', 'name': 'registration_timestamp'},
                    12: {'type': 'int', 'name': 'last_updated_timestamp'},
                    13: {'type': 'string', 'name': 'user_name'},
                    # last_known_position
                    25: {
                        'type': 'message',
                        'name': 'last_known_position',
                        'message_typedef': {
                            1: {'type': 'sint', 'name': 'lon_e6'},
                            2: {'type': 'sint', 'name': 'lat_e6'
                            }
                        }
                    }
                }
            },
            # social_profile
            2: {
                'type': 'message',
                'name': 'social_profile',
                'message_typedef': {
                    3: {'type': 'string', 'name': 'profile_picture_url'},
                    # oauth_provider
                    4: {
                        'type': 'message',
                        'name': 'oauth_provider',
                        'message_typedef': {
                            1: {'type': 'string', 'name': 'provider_name'},
                            4: {'type': 'string', 'name': 'provider_user_id'},
                            10: {'type': 'string', 'name': 'provider_email'},
                            11: {'type': 'string', 'name': 'provider_first_name'},
                            12: {'type': 'string', 'name': 'provider_last_name'}
                        }
                    },
                    5: {'type': 'int', 'name': 'social_rank'},
                    9: {'type': 'int', 'name': 'profile_state'}
                }
            }
        }
    },
    # saved_places_root
    5: {
        'type': 'message',
        'name': 'saved_places_root',
        'message_typedef': {
            # repeated saved_place
            1: {
                'type': 'message',
                'name': 'saved_place',
                'repeated': True,
                'message_typedef': {
                    # place_details
                    1: {
                        'type': 'message',
                        'name': 'place_details',
                        'message_typedef': {
                            1: {'type': 'int', 'name': 'server_id'},
                            # coords
                            2: {
                                'type': 'message',
                                'name': 'coords',
                                'message_typedef': {
                                    101: {'type': 'sint', 'name': 'lon_e6'},
                                    102: {'type': 'sint', 'name': 'lat_e6'}
                                }
                            },
                            3: {'type': 'string', 'name': 'full_address'},
                            4: {'type': 'string', 'name': 'street_name'},
                            5: {'type': 'string', 'name': 'city'},
                            6: {'type': 'string', 'name': 'region'},
                            7: {'type': 'string', 'name': 'country'},
                            8: {'type': 'string', 'name': 'house_number'},
                            9: {'type': 'string', 'name': 'place_id'},
                            #10: {}, Possible timestamp field
                            #11: {}, Field observed in samples but semantic meaning unknown
                        }
                    },
                    2: {'type': 'string', 'name': 'place_label'},
                    3: {'type': 'int', 'name': 'place_type'},
                }
            },
            3: {'type': 'int', 'name': 'places_count'}
        }
    },
    # top-level fields
    9: {'type': 'int', 'name': 'global_user_id'},
    11: {'type': 'string', 'name': 'persistent_id'},
    13: {'type': 'string', 'name': 'user_name'}
}


def _safe_str(obj: any, default: str = '') -> str:
    """
    Safely convert protobuf values to string, handling bytes and empty structures.
    Returns the 'default' value if conversion fails or obj is empty.
    """

    if obj in (None, {}, [], b'', ''):
        return default

    if isinstance(obj, (bytes, bytearray)):
        return obj.decode('utf-8', errors='replace').strip()

    try:
        s = str(obj).strip()
        return s if s else default
    except (TypeError, ValueError) as ex:
        logfunc(f"Warning - {_safe_str.__name__}: "
                f"failed to convert object of type {type(obj)}: {ex}")
        return default


def _pbget(d, key, default=None):
    """
    Retrieve a value from a dictionary using either an integer or string key.
    
    Args:
        d (dict): The dictionary to search.
        key (int/str): The protobuf tag or field name.
        default (any, optional): The value to return if the key is not found.

    Returns:
        any: The value associated with the key, or the default value.
    """

    if not isinstance(d, dict):
        return default
    # try with int key
    if key in d:
        return d[key]
    # try with str key
    sk = str(key)
    if sk in d:
        return d[sk]
    return default


def _get_cached_data(source_path, context):
    """
    Decode and cache Waze cached_data protobuf.
    """

    # Device Path
    device_path = get_device_file_path(source_path, context)

    # Reuse already parsed protobuf
    if (WAZE_CACHED_DATA['data'] is not None and WAZE_CACHED_DATA['path'] == device_path):
        return WAZE_CACHED_DATA['data']

    try:
        with open(source_path, 'rb') as f:
            data = f.read()
        if not data:
            return None

        # Strip Waze wrapper/header
        if data[0] != 0x0A:
            first_tag = data.find(b'\x0A')
            if 0 < first_tag < 32:
                data = data[first_tag:]

        decoded_data, _ = blackboxprotobuf.decode_message(
            data,
            CACHED_DATA_MESSAGE_TYPE
        )

        WAZE_CACHED_DATA['data'] = decoded_data
        WAZE_CACHED_DATA['path'] = device_path

        return decoded_data

    except (ValueError, TypeError, AttributeError, KeyError, IndexError, OverflowError) as ex:
        logfunc(
            f"[{context.get_artifact_name()}] "
            f"Failed to parse cached_data protobuf: {str(ex)}"
        )

    return None


def _parse_account_cached(source_path: str, context, data_list: list, data_list_html: list) -> None:
    """
    Parse Waze account information from cached_data protobuf.
    """

    # Initialize output fields
    fields = {
        F_FIRST_USE: None,
        F_FIRST_NAME: None,
        F_LAST_NAME: None,
        F_USER_NAME: None,
        F_PIC_URL: None,
        F_EMAIL: None,
        F_WAZE_ID: None,
        F_INVISIBLE_MODE: None,
        F_LAST_LAUNCH: None,
        F_PROVIDER_FIRST_NAME: None,
        F_PROVIDER_LAST_NAME: None,
        F_PROVIDER_NAME: None,
        F_PROVIDER_UID: None,
        F_DEVICE_PATH: None
    }

    # Shared cached protobuf decode
    decoded_data = _get_cached_data(source_path, context)
    if not decoded_data:
        return

    # Device Path
    fields[F_DEVICE_PATH] = WAZE_CACHED_DATA.get('path')

    try:
        # Top-level account_root
        account_root = _pbget(decoded_data, 1, {})
        if not account_root:
            return

        # user_profile
        profile = _pbget(account_root, 1, {})

        # social_profile
        social_profile = _pbget(account_root, 2, {})

        # oauth_provider
        oauth_provider = _pbget(social_profile, 4, {})

        # Timestamps
        registration_ts = _pbget(profile, 10)
        fields[F_FIRST_USE] = (
            convert_unix_ts_to_utc(registration_ts)
            if registration_ts else None
        )

        # Names
        fields[F_FIRST_NAME] = _safe_str(_pbget(profile, 1))
        last_name_data = _pbget(profile, 2)
        if isinstance(last_name_data, dict):
            ref_id = _safe_str(_pbget(last_name_data, 9))
            fields[F_LAST_NAME] = f"ID_REF:{ref_id}" if ref_id else "UNKNOWN"
        else:
            fields[F_LAST_NAME] = _safe_str(last_name_data)

        # Email
        fields[F_EMAIL] = _safe_str(_pbget(profile, 4))
        if not fields[F_EMAIL]:
            fields[F_EMAIL] = _safe_str(_pbget(oauth_provider, 10))

        # User Name
        fields[F_USER_NAME] = _safe_str(_pbget(profile, 13))
        if not fields[F_USER_NAME]:
            fields[F_USER_NAME] = _safe_str(_pbget(account_root, 13))

        # Profile image
        fields[F_PIC_URL] = _safe_str(_pbget(social_profile, 3))

        # Persistent identifier
        raw_uid = _safe_str(_pbget(account_root, 11))
        fields[F_WAZE_ID] = raw_uid.split('|')[-1] if raw_uid else None
        if not fields[F_WAZE_ID]:
            for value in account_root.values():
                if isinstance(value, str) and '|global|' in value:
                    fields[F_WAZE_ID] = value.split('|')[-1] if value else None
                    break

        # Provider
        fields[F_PROVIDER_NAME] = _safe_str(_pbget(oauth_provider, 1))
        fields[F_PROVIDER_UID] = _safe_str(_pbget(oauth_provider, 4))
        fields[F_PROVIDER_FIRST_NAME] = _safe_str(_pbget(oauth_provider, 11))
        fields[F_PROVIDER_LAST_NAME] = _safe_str(_pbget(oauth_provider, 12))

    except (ValueError, AttributeError, TypeError, KeyError) as ex:
        logfunc(
            f"[{context.get_artifact_name()}] "
            f"Error decoding Waze cached_data protobuf "
            f"from {source_path}: {str(ex)}"
        )

    # Base row for both lists
    base_data = (
        fields[F_FIRST_USE],
        fields[F_FIRST_NAME],
        fields[F_LAST_NAME],
        fields[F_USER_NAME],
        format_url(fields[F_PIC_URL]),                          # 4 Profile Picture URL (Plain)
        fields[F_EMAIL],
        fields[F_WAZE_ID],
        fields[F_INVISIBLE_MODE],
        fields[F_LAST_LAUNCH],
        fields[F_PROVIDER_FIRST_NAME],
        fields[F_PROVIDER_LAST_NAME],
        fields[F_PROVIDER_NAME],
        fields[F_PROVIDER_UID],
        fields[F_DEVICE_PATH]
    )

    # HTML row
    data_list_html.append((
        *base_data[:4],
        format_url(fields[F_PIC_URL], html_format=True),        # Replaces index 4
        *base_data[5:]
    ))

    # LAVA row
    data_list.append(base_data)


def _parse_account_user(source_path: str, context, data_list: list, data_list_html: list) -> None:
    """
    Parse account information from user.
    """

    # Initialize output fields
    fields = {
        F_FIRST_USE: None,
        F_FIRST_NAME: None,
        F_LAST_NAME: None,
        F_USER_NAME: None,
        #F_NICKNAME: None,
        F_PIC_URL: None,
        F_EMAIL: None,
        F_WAZE_ID: None,
        F_INVISIBLE_MODE: None,
        F_LAST_LAUNCH: None,
        F_PROVIDER_FIRST_NAME: None,
        F_PROVIDER_LAST_NAME: None,
        F_PROVIDER_NAME: None,
        F_PROVIDER_UID: None,
        F_DEVICE_PATH: None
    }

    lines = get_txt_file_content(source_path)
    if not lines:
        return

    # Device Path
    fields[F_DEVICE_PATH] = get_device_file_path(source_path, context)

    for line in lines:
        try:
            match = LINE_PATTERN_USER_RE.match(line)
            if not match:
                continue
            key = f"{match.group(1)}{match.group(2).strip()}"
            value = match.group(3).strip()

            # Mapping configuration keys
            if key == 'Realtime.FirstName':
                fields[F_FIRST_NAME] = value
            elif key == 'Realtime.LastName':
                fields[F_LAST_NAME] = value
            elif key == 'Realtime.Name':
                fields[F_USER_NAME] = value
#            elif key == 'Realtime.Nickname':
#                fields[F_NICKNAME] = value
            elif key == 'Realtime.PersistentId':
                fields[F_WAZE_ID] = value.split('|')[-1] if value else None
            elif key == 'Realtime.Invisible mode':
                fields[F_INVISIBLE_MODE] = (
                    'N/A' if value == '' else ('On' if value == '1' else 'Off')
                )
            elif key == 'General.First use':
                fields[F_FIRST_USE] = convert_unix_ts_to_utc(value)
            elif key == 'App Launch.Dynamic Splash Screen Last Shown Utc Seconds':
                fields[F_LAST_LAUNCH] = convert_unix_ts_to_utc(value)

        except (KeyError, TypeError, IndexError, ValueError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Malformed structure in {source_path}: {ex}")
            continue

    # Base row for both lists
    base_data = (
        fields[F_FIRST_USE],
        fields[F_FIRST_NAME],
        fields[F_LAST_NAME],
        fields[F_USER_NAME],
        format_url(fields[F_PIC_URL]),                          # 4 Profile Picture URL (Plain)
        fields[F_EMAIL],
        fields[F_WAZE_ID],
        fields[F_INVISIBLE_MODE],
        fields[F_LAST_LAUNCH],
        None,   # F_PROVIDER_FIRST_NAME
        None,   # F_PROVIDER_LAST_NAME
        None,   # F_PROVIDER_NAME
        None,   # F_PROVIDER_UID
        fields[F_DEVICE_PATH]
    )

    # HTML row
    data_list_html.append((
        *base_data[:4],
        format_url(fields[F_PIC_URL], html_format=True),        # Replaces index 4
        *base_data[5:]
    ))

    # LAVA row
    data_list.append(base_data)


@artifact_processor
def waze_account(context):
    """
    Extracts Waze account information from the user configuration file.
    """

    data_headers = (
        ('First Use', 'datetime'),
        'First Name',
        'Last Name',
        'User Name',
        'Profile Picture URL',
        'Email',
        'Waze User ID',
        'Invisible Mode',
        ('Last App Launch', 'datetime'),
        'Provider First Name',
        'Provider Last Name',
        'Provider Name',
        'Provider User ID',
        SOURCE_FILE_NAME
    )

    data_list = []
    data_list_html = []

    # Retrieve the app bundle identifier
    app_identifier = get_app_id(WAZE_PREFERENCES_PLIST, context)

    # Search for the 'user' config file
    source_path = context.get_seeker().search(
        f"*/{app_identifier}/Documents/user",
        return_on_first_hit=True
    )
    if source_path:
        _parse_account_user(source_path, context, data_list, data_list_html)


    # Search for the 'cached_data[.pb]' file
    source_path = context.get_seeker().search(
        f"*/{app_identifier}/Documents/cached_data*",
        return_on_first_hit=True
    )
    if source_path:
        _parse_account_cached(source_path, context, data_list, data_list_html)

    return data_headers, (data_list, data_list_html), SOURCE_PATH_NOTE


@artifact_processor
def waze_session_info(context):
    """
    Extracts session metadata stored in the Waze session file,
    including geolocation records, timestamps, navigation
    destinations and application state information.
    """
    data_headers = (
        ('Timestamp', 'datetime'),
        'Friendly Name',
        'Field',
        'Value',
        'Latitude',
        'Longitude',
        'Location'
    )

    data_list = []

    # Helper function to format the line location for forensic auditing
    def fmt_loc(ln):
        return f"row: ({ln})"

    # Maps geolocation keys to their descriptive friendly name prefixes
    geo_keys = {
        'GPS.Position': 'Last Position',
        'ORIG_GPS.Position': 'Original Position',
        'Location.Position': 'Location Position',
        'Home.Position': 'Home Position',
        'Work.Position': 'Work Position',
        'Navigation.Last position': 'Last Navigation',
        'Parking.Last GPS position': 'Last Parked Position',
        'Destination.Position': 'Active Destination Position',
        'VenueMapPin.Position': 'Dropped Map Pin Position'
    }

    # Maps epoch timestamp keys to their descriptive friendly names
    ts_keys = {
        'Config.Last synced': 'Last Synced',
        'GPS.Time': 'Last Position Timestamp',
        'ORIG_GPS.Time': 'Original Position Timestamp',
        'Location.Time': 'Location Timestamp',
        'General.First use': 'First Use Timestamp',
        'Rewire.Main menu last viewed time': 'Main Menu Last Viewed',
        'Rewire.Inbox last viewed time': 'Inbox Last Viewed',
        'Places.Places Table Cleanup Time': 'Database Cleanup Time'
    }

    # Maps standard text/numeric keys to their final friendly names
    plain_keys = {
        'GPS.Direction': 'Last Position Direction',
        'General.Sessions since first install': 'Total Sessions Count',
        'Push Notifications.Token': 'Push Notification Token',
        'Map.Zoom': 'Current Map Zoom Level',
        'Navigation.Last dest name': 'Last Navigation Destination',
        'Navigation.Last dest venue name': 'Last Navigation Venue Name',
        'Navigation.Last dest number': 'Last Destination House Number',
        'Navigation.Last dest street': 'Last Destination Street',
        'Navigation.Last dest city': 'Last Destination City',
        'Navigation.Last dest state': 'Last Destination State',
        'Navigation.Last dest country': 'Last Destination Country'
    }

    # Retrieve the app bundle identifier and search for the 'session' config file
    app_identifier = get_app_id(WAZE_PREFERENCES_PLIST, context)
    source_path = context.get_seeker().search(
        f"*/{app_identifier}/Documents/session",
        return_on_first_hit=True
    )
    if not source_path:
        return data_headers, data_list, source_path

    lines = get_txt_file_content(source_path)
    if not lines:
        return data_headers, data_list, source_path

    for line_num, line in enumerate(lines, start=1):
        try:
            match = LINE_PATTERN_SESSION_RE.match(line)
            if not match:
                continue

            key = f"{match.group(1)}{match.group(2).strip()}"
            value = match.group(3).strip()

            # Skip empty or unpopulated records to keep the report clean
            if not value:
                continue

            # Geolocation data processing
            if key in geo_keys:
                prefix = geo_keys[key]
                lat, lon = split_coordinates(value, 1_000_000.0)
                data_list.append(
                    (None, prefix, key, value, lat, lon, fmt_loc(line_num))
                )
                continue

            # Timestamp processing
            if key in ts_keys:
                friendly_name = ts_keys[key]
                val_utc = convert_unix_ts_to_utc(value if value != '0' else 0)
                data_list.append(
                    (val_utc, friendly_name, key, value, None, None, fmt_loc(line_num))
                )
                continue

            # Standard textual/numeric metadata processing
            if key in plain_keys:
                friendly_name = plain_keys[key]
                data_list.append(
                    (None, friendly_name, key, value, None, None, fmt_loc(line_num))
                )
                continue

        except (KeyError, TypeError, IndexError, ValueError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Malformed structure in {source_path} at line {line_num}: {ex}")
            continue

    return data_headers, data_list, source_path


@artifact_processor
def waze_track_gps_quality(context):
    """
    Unified forensic parser for Waze spdlog files. Extracts high-precision
    positioning data and matches absolute Unix Epoch timestamps (in milliseconds)
    across legacy C++ log lines and modern Swift telemetry payloads for
    heuristic deduplication.

    Two log architectures are handled:

    Legacy C++ single-line
        [HH:MM:SS.mmm ...] STAT(buffer#N) GPS_QUALITY
            {LAT=N}{LON=N}{SAMPLE_COUNT=N}{BAD_SAMPLE_COUNT=N}{DUP_SAMPLE_COUNT=N}
            {ACC_AVG=N}{ACC_MIN=N}{ACC_MAX=N}{PROVIDER=X}{TIMESTAMP_MS=N}

    Modern Swift multi-line protobuf-text block (two-level nested structure)
        [HH:MM:SS.mmm ...] New stats ... <WCEWazeAppEvent>: {   <- WAZE_EVENT_RE
            payload { gps_stats_wrapper {
                gps_quality {                                    <- GPS_BLOCK_RE
                    sample_count: N      bad_sample_count: N
                    duplicate_sample_count: N
                    accuracy_avg_meters: N  ...  position_provider: X
                    coordinates { latitude: N  longitude: N }
                }
            }}
            metadata { event_client_timestamp {
                seconds: N   nanos: N                            <- read anywhere in block
            }}
        }

    Deduplication: when a Legacy line is immediately followed by a Swift block
    whose timestamp differs by <= 250 ms, they represent the same GPS sample.
    The richer Swift record is kept and the Legacy one discarded.
    """

    data_headers = (
        ('Timestamp', 'datetime'),
        'Timestamp (ms)',
        'Latitude',
        'Longitude',
        'Sample Count',
        'Bad Sample Count',
        'Duplicate Sample Count',
        'Accuracy Min (m)',
        'Accuracy Avg (m)',
        'Accuracy Max (m)',
        'Position Provider',
        SOURCE_FILE_NAME,
        'Location'
    )

    data_list = []

    files_found = sorted(context.get_files_found())
    for file_found in files_found:
        filename = Path(file_found).name

        # Target only valid spdlog structural data files
        if not (filename.startswith('spdlog') and filename.endswith('.logdata')):
            continue

        # Read text file
        lines = get_txt_file_content(file_found)
        if not lines:
            continue

        # Device Path
        device_path = get_device_file_path(file_found, context)

        # Buffered Legacy record awaiting pairing
        pending_legacy = None

        # Swift two-level state machine tracking:
        #   inside_event  — we are inside a WCEWazeAppEvent { ... } block
        #   inside_gps    — we are inside the nested gps_quality { ... } sub-block
        #   event_depth   — { } nesting depth; when it reaches 0 the event closes
        inside_event   = False
        event_depth    = 0
        inside_gps     = False
        event_start_line = 0
        current_payload  = {}

        for line_count, line in enumerate(lines, start=1):
            try:
                clean_line = line.strip()

                # Legacy C++ GPS_QUALITY line
                legacy_match = LEGACY_GPS_RE.search(clean_line)
                if legacy_match:
                    # Flush any buffered Legacy record that had no matching Swift block
                    if pending_legacy:
                        data_list.append((
                            pending_legacy[F_TIMESTAMP],
                            pending_legacy[F_TIMESTAMP_MS],
                            pending_legacy[F_LAT],
                            pending_legacy[F_LON],
                            pending_legacy[F_SAMPLE_COUNT] or 'N/A',
                            pending_legacy[F_BAD_SAMPLE_COUNT] or 'N/A',
                            pending_legacy[F_DUP_SAMPLE_COUNT] or 'N/A',
                            pending_legacy[F_MIN_ACCURACY] or 'N/A',
                            pending_legacy[F_AVG_ACCURACY] or 'N/A',
                            pending_legacy[F_MAX_ACCURACY] or 'N/A',
                            pending_legacy[F_PROVIDER] or 'N/A',
                            pending_legacy[F_DEVICE_PATH],
                            pending_legacy[F_LOCATION]
                        ))
                        pending_legacy = None

                    legacy_ts_ms = int(legacy_match.group('ts_ms'))
                    # Legacy format stores integers scaled by 10^6 (E6)
                    lat_e6 = legacy_match.group('lat')
                    lon_e6 = legacy_match.group('lon')

                    # Store into the temporary pending slot
                    pending_legacy = {
                        F_TIMESTAMP: convert_unix_ts_to_utc(legacy_ts_ms / 1_000.0),
                        F_TIMESTAMP_MS: legacy_ts_ms,
                        F_LAT: float(lat_e6) / 1_000_000.0 if lat_e6 is not None else None,
                        F_LON: float(lon_e6) / 1_000_000.0 if lon_e6 is not None else None,
                        F_SAMPLE_COUNT: legacy_match.group('sam_cnt'),
                        F_BAD_SAMPLE_COUNT: legacy_match.group('bad_cnt'),
                        F_DUP_SAMPLE_COUNT: legacy_match.group('dup_cnt'),
                        F_MIN_ACCURACY: legacy_match.group('acc_min'),
                        F_AVG_ACCURACY: legacy_match.group('acc_avg'),
                        F_MAX_ACCURACY: legacy_match.group('acc_max'),
                        F_PROVIDER: legacy_match.group('prov'),
                        F_DEVICE_PATH: device_path,
                        F_LOCATION: f"{filename} (row: {line_count})"
                    }
                    continue

                # Swift block: State 0 -> 1
                if not inside_event:
                    if WAZE_EVENT_RE.search(clean_line):
                        inside_event = True
                        event_depth = clean_line.count('{') - clean_line.count('}')
                        event_start_line = line_count
                        current_payload = {
                            'lat' : None, 'lon' : None,
                            'sam_cnt': None, 'bad_cnt': None, 'dup_cnt': None,
                            'acc_min': None, 'acc_avg': None, 'acc_max': None,
                            'prov' : None,
                            'sec' : None, 'ns' : 0,
                        }
                    continue

                # Swift block: State 1 (inside event)
                opens  = clean_line.count('{')
                closes = clean_line.count('}')

                # State 1 -> 2: enter gps_quality sub-block
                if not inside_gps and GPS_BLOCK_RE.match(clean_line):
                    inside_gps = True

                # State 2: parse GPS fields
                if inside_gps:
                    m = SWIFT_SAM_CNT_RE.search(clean_line)
                    if m and current_payload['sam_cnt'] is None:
                        current_payload['sam_cnt'] = m.group(1)

                    m = SWIFT_BAD_CNT_RE.search(clean_line)
                    if m and current_payload['bad_cnt'] is None:
                        current_payload['bad_cnt'] = m.group(1)

                    m = SWIFT_DUP_CNT_RE.search(clean_line)
                    if m and current_payload['dup_cnt'] is None:
                        current_payload['dup_cnt'] = m.group(1)

                    m = SWIFT_ACC_MIN_RE.search(clean_line)
                    if m and current_payload['acc_min'] is None:
                        current_payload['acc_min'] = m.group(1)

                    m = SWIFT_ACC_AVG_RE.search(clean_line)
                    if m and current_payload['acc_avg'] is None:
                        current_payload['acc_avg'] = m.group(1)

                    m = SWIFT_ACC_MAX_RE.search(clean_line)
                    if m and current_payload['acc_max'] is None:
                        current_payload['acc_max'] = m.group(1)

                    m = SWIFT_PROV_RE.search(clean_line)
                    if m and current_payload['prov'] is None:
                        current_payload['prov'] = (
                            m.group(1).replace('LOCATION_PROVIDER_', '')
                        )

                    m = SWIFT_LAT_RE.search(clean_line)
                    if m and current_payload['lat'] is None:
                        current_payload['lat'] = float(m.group(1))

                    m = SWIFT_LON_RE.search(clean_line)
                    if m and current_payload['lon'] is None:
                        current_payload['lon'] = float(m.group(1))

                # Timestamp fields are in metadata — read from anywhere inside event
                m = SWIFT_SEC_RE.search(clean_line)
                if m and current_payload['sec'] is None:
                    current_payload['sec'] = int(m.group(1))

                m = SWIFT_NANOS_RE.search(clean_line)
                if m and current_payload.get('ns') == 0:
                    current_payload['ns'] = int(m.group(1))

                # Update depth after parsing fields
                event_depth += opens - closes

                # Detect gps_quality sub-block close (closes > opens at that level)
                if inside_gps and closes > opens:
                    inside_gps = False

                # State 1 -> 0: event block fully closed
                if event_depth <= 0:
                    inside_event = False
                    inside_gps   = False

                    # Emit record only if we have timestamp and coordinates
                    if (current_payload['sec'] is not None
                            and current_payload['lat'] is not None
                            and current_payload['lon'] is not None):

                        modern_ts_ms = (
                            current_payload['sec'] * 1_000
                            + current_payload['ns'] // 1_000_000
                        )
                        ts_utc = convert_unix_ts_to_utc(modern_ts_ms / 1_000.0)

                        if pending_legacy:
                            legacy_ts_ms = pending_legacy[F_TIMESTAMP_MS]
                            if abs(modern_ts_ms - legacy_ts_ms) > GPS_DEDUP_WINDOW_MS:
                                # Different samples: preserve both by writing legacy first
                                data_list.append((
                                    pending_legacy[F_TIMESTAMP],
                                    pending_legacy[F_TIMESTAMP_MS],
                                    pending_legacy[F_LAT],
                                    pending_legacy[F_LON],
                                    pending_legacy[F_SAMPLE_COUNT] or 'N/A',
                                    pending_legacy[F_BAD_SAMPLE_COUNT] or 'N/A',
                                    pending_legacy[F_DUP_SAMPLE_COUNT] or 'N/A',
                                    pending_legacy[F_MIN_ACCURACY] or 'N/A',
                                    pending_legacy[F_AVG_ACCURACY] or 'N/A',
                                    pending_legacy[F_MAX_ACCURACY] or 'N/A',
                                    pending_legacy[F_PROVIDER] or 'N/A',
                                    pending_legacy[F_DEVICE_PATH],
                                    pending_legacy[F_LOCATION]
                                ))

                            pending_legacy = None

                        # Always commit the modern Swift record
                        data_list.append((
                            ts_utc,
                            modern_ts_ms,
                            current_payload['lat'],
                            current_payload['lon'],
                            current_payload['sam_cnt'] or 'N/A',
                            current_payload['bad_cnt'] or 'N/A',
                            current_payload['dup_cnt'] or 'N/A',
                            current_payload['acc_min'] or 'N/A',
                            current_payload['acc_avg'] or 'N/A',
                            current_payload['acc_max'] or 'N/A',
                            current_payload['prov'] or 'N/A',
                            device_path,
                            f"{filename} (row: {event_start_line})"
                        ))

                    current_payload = {}

            except (ValueError, IndexError, TypeError) as ex:
                logfunc(f"[{context.get_artifact_name()}] "
                        f"Error - Failed parsing line {line_count} "
                        f"in {file_found}: {ex}")
                continue

        # Handle file boundary check for an orphaned legacy record
        if pending_legacy:
            data_list.append((
                pending_legacy[F_TIMESTAMP],
                pending_legacy[F_TIMESTAMP_MS],
                pending_legacy[F_LAT],
                pending_legacy[F_LON],
                pending_legacy[F_SAMPLE_COUNT] or 'N/A',
                pending_legacy[F_BAD_SAMPLE_COUNT] or 'N/A',
                pending_legacy[F_DUP_SAMPLE_COUNT] or 'N/A',
                pending_legacy[F_MIN_ACCURACY] or 'N/A',
                pending_legacy[F_AVG_ACCURACY] or 'N/A',
                pending_legacy[F_MAX_ACCURACY] or 'N/A',
                pending_legacy[F_PROVIDER] or 'N/A',
                pending_legacy[F_DEVICE_PATH],
                pending_legacy[F_LOCATION]
            ))

    return data_headers, data_list, SOURCE_PATH_NOTE


@artifact_processor
def waze_search_history(context):
    """
    Extracts all locations manually searched by the user from the PLACES table.
    """

    data_headers = (
        ('Updated', 'datetime'),
        'Name',
        'House Number',
        'Street',
        'City',
        'State',
        'Country',
        'Latitude',
        'Longitude',
        'Residential Status',
        ('Created', 'datetime'),
        'Venue ID',
        'Location'
    )

    data_list = []

    # Retrieve the app bundle identifier and search for the user database
    app_identifier = get_app_id(WAZE_PREFERENCES_PLIST, context)
    source_path = context.get_seeker().search(
        f"*/{app_identifier}/Documents/user.db*",
        return_on_first_hit=True
    )
    if not source_path:
        return data_headers, data_list, source_path

    db = open_sqlite_db_readonly(source_path)
    if not db:
        return data_headers, data_list, source_path

    try:
        cursor = db.cursor()
        # updated_time
        if does_column_exist_in_db(source_path, 'PLACES', 'updated_time'):
            has_updated_time = "P.updated_time"
        else:
            has_updated_time = "NULL"
        # is_residential
        if does_column_exist_in_db(source_path, 'PLACES', 'is_residential'):
            has_is_residential = """
                CASE
                    WHEN P.is_residential = 0 THEN 'No'
                    WHEN P.is_residential = 1 THEN 'Yes'
                    ELSE coalesce(CAST(P.is_residential AS TEXT), 'N/A')
                END
            """
        else:
            has_is_residential = "NULL"

        query = f'''
        SELECT 
            P.id,
            {has_updated_time} AS "updated",
            P.name,
            P.house,
            P.street,
            P.city,
            P.state,
            P.country,
            CAST((CAST(P.latitude AS REAL) / 1000000) AS TEXT) AS "latitude",
            CAST((CAST(P.longitude AS REAL) / 1000000) AS TEXT) AS "longitude",
            {has_is_residential} AS "residential_status",
            P.created_time,
            P.venue_id
        FROM PLACES AS "P"
        '''

        cursor.execute(query)
        for record in cursor:
            try:
                # Initialize output fields
                fields = {
                    F_UPDATED: None,
                    F_NAME: None,
                    F_HOUSE_NUM: None,
                    F_STREET: None,
                    F_CITY: None,
                    F_STATE: None,
                    F_COUNTRY: None,
                    F_LAT: None,
                    F_LON: None,
                    F_RESIDENTIAL_STATUS: None,
                    F_CREATED: None,
                    F_VENUE_ID: None,
                    F_LOCATION: None
                }

                # Extract only the identifiers needed for location metadata
                place_id = record[0]

                # Convert timestamps to UTC
                fields[F_UPDATED] = convert_unix_ts_to_utc(record[1])
                fields[F_CREATED] = convert_unix_ts_to_utc(record[11])

                # Name
                fields[F_NAME] = record[2]

                # Location Address
                fields[F_HOUSE_NUM] = record[3]
                fields[F_STREET] = record[4]
                fields[F_CITY] = record[5]
                fields[F_STATE] = record[6]
                fields[F_COUNTRY] = record[7]

                # Coordinates
                fields[F_LAT] = record[8]
                fields[F_LON] = record[9]

                # Is Residential?
                fields[F_RESIDENTIAL_STATUS] = record[10]

                # Venue Identifier
                fields[F_VENUE_ID] = record[12]

                # Precise location within the source database table for validation
                fields[F_LOCATION] = f"PLACES (id: {place_id})"

                # Base row for both lists
                #base_data = tuple(fields.values())
                base_data = (
                    fields[F_UPDATED],
                    fields[F_NAME],
                    fields[F_HOUSE_NUM],
                    fields[F_STREET],
                    fields[F_CITY],
                    fields[F_STATE],
                    fields[F_COUNTRY],
                    fields[F_LAT],
                    fields[F_LON],
                    fields[F_RESIDENTIAL_STATUS],
                    fields[F_CREATED],
                    fields[F_VENUE_ID],
                    fields[F_LOCATION]
                )

                # LAVA row
                data_list.append(base_data)

            except (ValueError, IndexError, TypeError) as ex:
                _id = record[0] if record and len(record) > 0 else 'UNKNOWN'
                logfunc(f"[{context.get_artifact_name()}] "
                        f"Error - Failed parsing record PLACES {_id} in {source_path}: {ex}")
                continue

    except sqlite3.Error as db_ex:
        # Log fatal database errors (e.g., malformed DB or missing tables)
        logfunc(f"[{context.get_artifact_name()}] "
                f"Error - executing query on {source_path}: {db_ex}")
    finally:
        # Ensure the database connection is closed safely
        db.close()

    return data_headers, data_list, source_path


@artifact_processor
def waze_recent_locations(context):
    """
    Extracts the history of recently visited or selected locations, 
    joining RECENTS with the PLACES table for full coordinates.
    """

    data_headers = (
        ('Last Access', 'datetime'),
        'Type',
        'Name',
        'House Number',
        'Street',
        'City',
        'State',
        'Country',
        'Latitude',
        'Longitude',
        ('Created', 'datetime'),
        ('Last Waypoint Access', 'datetime'),
        'Context',
        'Image ID',
        'Venue ID',
        'Location'
    )

    data_list = []

    # Retrieve the app bundle identifier and search for the user database
    app_identifier = get_app_id(WAZE_PREFERENCES_PLIST, context)
    source_path = context.get_seeker().search(
        f"*/{app_identifier}/Documents/user.db*",
        return_on_first_hit=True
    )
    if not source_path:
        return data_headers, data_list, source_path

    query = '''
    SELECT 
        R.id,
        P.id,
        R.access_time,
        CASE R.type
            WHEN -1 THEN 'N/A'
            WHEN 0 THEN 'User Search'
            WHEN 1 THEN 'Advertising'
            WHEN 2 THEN 'Map Interaction'
            WHEN 3 THEN 'Shared'
            WHEN 4 THEN 'Navigation History'
            ELSE CAST(R.type AS TEXT)
        END AS "entry_type",
        coalesce(R.name, P.name) AS "name",
        P.house,
        P.street,
        P.city,
        P.state,
        P.country,
        CAST((CAST(P.latitude AS REAL) / 1000000) AS TEXT) AS "latitude",
        CAST((CAST(P.longitude AS REAL) / 1000000) AS TEXT) AS "longitude",
	    R.created_time,
        R.waypoint_access_time,
        R.string_context,
	    R.image_id,
        P.venue_id
    FROM RECENTS AS "R"
    LEFT JOIN PLACES AS "P" ON (R.place_id = P.id)
    ORDER BY R.access_time DESC
    '''

    db = get_sqlite_db_records(source_path, query)
    if not db:
        return data_headers, data_list, source_path

    for record in db:
        try:
            # Initialize output fields
            fields = {
                F_LAST_ACCESS: None,
                F_LOCATION_TYPE: None,
                F_NAME: None,
                F_HOUSE_NUM: None,
                F_STREET: None,
                F_CITY: None,
                F_STATE: None,
                F_COUNTRY: None,
                F_LAT: None,
                F_LON: None,
                F_CREATED: None,
                F_LAST_WAYPOINT_ACCESS: None,
                F_CONTEXT: None,
                F_IMAGE_ID: None,
                F_VENUE_ID: None,
                F_LOCATION: None
            }

            # Extract only the identifiers needed for location metadata
            recent_id = record[0]
            place_id = record[1]

            # Convert timestamps to UTC
            fields[F_LAST_ACCESS] = convert_unix_ts_to_utc(record[2])
            fields[F_CREATED] = convert_unix_ts_to_utc(record[12])
            fields[F_LAST_WAYPOINT_ACCESS] = convert_unix_ts_to_utc(record[13])

            # Location Type
            fields[F_LOCATION_TYPE] = record[3]

            # Location Name
            fields[F_NAME] = record[4]

            # Address
            fields[F_HOUSE_NUM] = record[5]
            fields[F_STREET] = record[6]
            fields[F_CITY] = record[7]
            fields[F_STATE] = record[8]
            fields[F_COUNTRY] = record[9]

            # Coordinates
            fields[F_LAT] = record[10]
            fields[F_LON] = record[11]

            # String Context
            fields[F_CONTEXT] = record[14]
            fields[F_IMAGE_ID] = record[15]

            # Venue ID
            fields[F_VENUE_ID] = record[16]

            # Precise location within the source database table for validation
            location = [ f"RECENTS (id: {recent_id})" ]
            if place_id is not None:
                location.append(f"PLACES (id: {place_id})")
            fields[F_LOCATION] = COMMA_SEP.join(location)

            # Create a tuple of the variables to check for content
            data_row = (
                fields[F_LAST_ACCESS],
                fields[F_LOCATION_TYPE],
                fields[F_NAME],
                fields[F_HOUSE_NUM],
                fields[F_STREET],
                fields[F_CITY],
                fields[F_STATE],
                fields[F_COUNTRY],
                fields[F_LAT],
                fields[F_LON],
                fields[F_CREATED],
                fields[F_LAST_WAYPOINT_ACCESS],
                fields[F_CONTEXT],
                fields[F_IMAGE_ID],
                fields[F_VENUE_ID],
                fields[F_LOCATION]
            )

            # LAVA row
            data_list.append(data_row)

        except (ValueError, IndexError, TypeError) as ex:
            _id = record[0] if record and len(record) > 0 else 'UNKNOWN'
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Failed parsing record RECENTS {_id} in {source_path}: {ex}")
            continue

    return data_headers, data_list, source_path


def _parse_favorite_cached(source_path: str, context, data_list: list) -> None:
    """
    Parse favorite locations from cached_data.
    """

    # Shared cached protobuf decode
    decoded_data = _get_cached_data(source_path, context)
    if not decoded_data:
        return None

    # Device Path
    device_path = WAZE_CACHED_DATA.get('path')

    try:
        # Top-level account_root
        account_root = _pbget(decoded_data, 1, {})

        # saved_places_root
        saved_places_root = _pbget(account_root, 5, {})

        # Iterate through the saved places collection
        raw_places = _pbget(saved_places_root, 1)
        if isinstance(raw_places, list):
            saved_places_iter = enumerate(raw_places, start=1)
        elif isinstance(raw_places, dict):
            saved_places_iter = saved_places_root.items()
        else:
            saved_places_iter = enumerate(saved_places_root.values(), start=1)

        for i, saved_place in saved_places_iter:
            # field 1.5.i
            if not isinstance(saved_place, dict):
                continue

            # place_details = field 1.5.i.1
            place_details = _pbget(saved_place, 1, {})
            if not place_details:
                continue

            # Initialize output fields
            fields = {
                F_LAST_ACCESS: None,
                F_LOCATION_TYPE: None,
                F_NAME: None,
                F_PLACE_NAME: None,
                F_HOUSE_NUM: None,
                F_STREET: None,
                F_CITY: None,
                F_STATE: None,
                F_COUNTRY: None,
                F_LAT: None,
                F_LON: None,
                F_CREATED: None,
                F_MODIFIED: None,
                F_LAST_WAYPOINT_ACCESS: None,
                F_RANK: None,
                F_SERVER_ID: None,
                F_VENUE_ID: None,
                F_DEVICE_PATH: None,
                F_LOCATION: None
            }

            # coords = field 1.5.i.1.2
            coords = _pbget(place_details, 2, {})
            lat_e6 = _pbget(coords, 102)
            fields[F_LAT] = float(lat_e6) / 1_000_000.0 if lat_e6 is not None else None
            lon_e6 = _pbget(coords, 101)
            fields[F_LON] = float(lon_e6) / 1_000_000.0 if lon_e6 is not None else None

            # Favorite Name
            fields[F_NAME] = _safe_str(_pbget(saved_place, 2))

            # Location Address
            fields[F_PLACE_NAME] = _safe_str(_pbget(place_details, 3)).strip()
            fields[F_STREET] = _safe_str(_pbget(place_details, 4))
            fields[F_CITY] = _safe_str(_pbget(place_details, 5))
            fields[F_STATE] = _safe_str(_pbget(place_details, 6))
            fields[F_COUNTRY] = _safe_str(_pbget(place_details, 7))
            fields[F_HOUSE_NUM] = _safe_str(_pbget(place_details, 8))

            # Location Type and Label
            #loc_type_str = _safe_str(_pbget(saved_place, 2))
            loc_type = _safe_str(_pbget(saved_place, 3))
            if loc_type == '-1':
                loc_type_str = 'N/A'
            elif loc_type == '0':
                loc_type_str = 'Custom'
            elif loc_type == '1':
                loc_type_str = 'Home'
            elif loc_type == '2':
                loc_type_str = 'Work'
            elif loc_type == '3':
                loc_type_str = 'Events'
            elif loc_type == '4':
                loc_type_str = 'Saved POI'
            else:
                loc_type_str = f"{loc_type}"

            fields[F_LOCATION_TYPE] = loc_type_str

            # Convert timestamps to UTC
            #created = convert_unix_ts_to_utc(_pbget(place_details, ))
            fields[F_MODIFIED] = convert_unix_ts_to_utc(_pbget(place_details, 10))

            # Server Identifier
            fields[F_SERVER_ID] = _safe_str(_pbget(place_details, 1))

            # Venue Identifier
            fields[F_VENUE_ID] = _safe_str(_pbget(place_details, 9))

            # Precise location within the protobuf data for validation
            fields[F_LOCATION] = f"Tag: 1.5.{i}"

            # Device Path
            fields[F_DEVICE_PATH] = device_path

            # Base row for both lists
            #base_data = tuple(fields.values())
            base_data = (
                fields[F_LAST_ACCESS],
                fields[F_LOCATION_TYPE],
                fields[F_NAME],
                fields[F_PLACE_NAME],
                fields[F_HOUSE_NUM],
                fields[F_STREET],
                fields[F_CITY],
                fields[F_STATE],
                fields[F_COUNTRY],
                fields[F_LAT],
                fields[F_LON],
                fields[F_CREATED],
                fields[F_MODIFIED],
                fields[F_LAST_WAYPOINT_ACCESS],
                fields[F_RANK],
                fields[F_SERVER_ID],
                fields[F_VENUE_ID],
                fields[F_DEVICE_PATH],
                fields[F_LOCATION]
            )

            # LAVA row
            data_list.append(base_data)

    except (ValueError, AttributeError, TypeError, KeyError) as ex:
        logfunc(
            f"[{context.get_artifact_name()}] "
            f"Error decoding Waze cached_data protobuf "
            f"from {source_path}: {str(ex)}"
        )

    return data_list


def _parse_favorite_user_db(source_path: str, context, data_list: list) -> None:
    """
    Parse favorite locations from user.db.
    """

    query = '''
    SELECT 
	    F.id,
	    P.id,
        F.access_time,
        CASE f.type
            WHEN -1 THEN 'N/A'
            WHEN 0 THEN 'Custom'
            WHEN 1 THEN 'Home'
            WHEN 2 THEN 'Work'
            WHEN 3 THEN 'Events'
            WHEN 4 THEN 'Saved POI'
            ELSE 'Unknown (' || IFNULL(f.type, 'N/A') || ')'	
        END AS "entry_type",        
	    F.name,
        P.name AS "place_name",
	    P.house,
        P.street,
        P.city,
        P.state,
        P.country,
        CAST((CAST(P.latitude AS REAL) / 1000000) AS TEXT) AS "latitude",
        CAST((CAST(P.longitude AS REAL) / 1000000) AS TEXT) AS "longitude",
	    F.created_time,
	    F.modified_time,
        F.waypoint_access_time,
        F.rank,
        F.server_id,
        P.venue_id
    FROM FAVORITES AS "F"
    LEFT JOIN PLACES AS "P" ON (F.place_id = P.id)
    '''

    db = get_sqlite_db_records(source_path, query)
    if not db:
        return
    device_path = get_device_file_path(source_path, context)

    for record in db:
        try:
            # Initialize output fields
            fields = {
                F_LAST_ACCESS: None,
                F_LOCATION_TYPE: None,
                F_NAME: None,
                F_PLACE_NAME: None,
                F_HOUSE_NUM: None,
                F_STREET: None,
                F_CITY: None,
                F_STATE: None,
                F_COUNTRY: None,
                F_LAT: None,
                F_LON: None,
                F_CREATED: None,
                F_MODIFIED: None,
                F_LAST_WAYPOINT_ACCESS: None,
                F_RANK: None,
                F_SERVER_ID: None,
                F_VENUE_ID: None,
                F_DEVICE_PATH: None,
                F_LOCATION: None
            }

            # Extract only the identifiers needed for location metadata
            favorite_id = record[0]
            place_id = record[1]

            # Convert timestamps to UTC
            fields[F_LAST_ACCESS] = convert_unix_ts_to_utc(record[2])
            fields[F_CREATED] = convert_unix_ts_to_utc(record[13])
            fields[F_MODIFIED] = convert_unix_ts_to_utc(record[14])
            fields[F_LAST_WAYPOINT_ACCESS] = convert_unix_ts_to_utc(record[15])

            # Location Type
            fields[F_LOCATION_TYPE] = record[3]

            # Name
            fields[F_NAME] = record[4]

            # Location Address
            fields[F_PLACE_NAME] = record[5]
            fields[F_HOUSE_NUM] = record[6]
            fields[F_STREET] = record[7]
            fields[F_CITY] = record[8]
            fields[F_STATE] = record[9]
            fields[F_COUNTRY] = record[10]

            # Coordinates
            fields[F_LAT] = record[11]
            fields[F_LON] = record[12]

            # Rank
            fields[F_RANK] = record[16]

            # Identifiers
            fields[F_SERVER_ID] = record[17]
            fields[F_VENUE_ID] = record[18]

            # Device Path
            fields[F_DEVICE_PATH] = device_path

            # Precise location within the source database table for validation
            location = [ f"FAVORITES (id: {favorite_id})" ]
            if place_id is not None:
                location.append(f"PLACES (id: {place_id})")
            fields[F_LOCATION] = COMMA_SEP.join(location)

            # Base row for both lists
            #base_data = tuple(fields.values())
            base_data = (
                fields[F_LAST_ACCESS],
                fields[F_LOCATION_TYPE],
                fields[F_NAME],
                fields[F_PLACE_NAME],
                fields[F_HOUSE_NUM],
                fields[F_STREET],
                fields[F_CITY],
                fields[F_STATE],
                fields[F_COUNTRY],
                fields[F_LAT],
                fields[F_LON],
                fields[F_CREATED],
                fields[F_MODIFIED],
                fields[F_LAST_WAYPOINT_ACCESS],
                fields[F_RANK],
                fields[F_SERVER_ID],
                fields[F_VENUE_ID],
                fields[F_DEVICE_PATH],
                fields[F_LOCATION]
            )

            # LAVA row
            data_list.append(base_data)

        except (ValueError, IndexError, TypeError) as ex:
            _id = record[0] if record and len(record) > 0 else 'UNKNOWN'
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Failed parsing record FAVORITES id {_id} in {source_path}: {ex}")
            continue


@artifact_processor
def waze_favorite_locations(context):
    """
    Extracts locations saved as favorites (Home, Work, etc.) by the user.
    """

    data_headers = (
        ('Last Access', 'datetime'),
        'Type',
        'Name',
        'Place Name',
        'House Number',
        'Street',
        'City',
        'State',
        'Country',
        'Latitude',
        'Longitude',
        ('Created', 'datetime'),
        ('Modified', 'datetime'),
        ('Last Waypoint Access', 'datetime'),
        'Rank',
        'Server ID',
        'Venue ID',
        SOURCE_FILE_NAME,
        'Location'
    )

    data_list = []

    # Retrieve the app bundle identifier and search for the user database
    app_identifier = get_app_id(WAZE_PREFERENCES_PLIST, context)
    source_path = context.get_seeker().search(
        f"*/{app_identifier}/Documents/user.db*",
        return_on_first_hit=True
    )

    if source_path:
        _parse_favorite_user_db(source_path, context, data_list)


    # Search for the 'cached_data[.pb]' file
    source_path = context.get_seeker().search(
        f"*/{app_identifier}/Documents/cached_data*",
        return_on_first_hit=True
    )
    if source_path:
        _parse_favorite_cached(source_path, context, data_list)

    return data_headers, data_list, SOURCE_PATH_NOTE


@artifact_processor
def waze_shared_locations(context):
    """
    Extracts locations that the user has shared with others or received via sharing.
    """

    data_headers = (
        ('Shared', 'datetime'),
        'Name',
        'House Number',
        'Street',
        'City',
        'State',
        'Country',
        'Latitude',
        'Longitude',
        ('Created', 'datetime'),
        ('Modified', 'datetime'),
        ('Last Access', 'datetime'),
        'Waze User ID',
        'Venue ID',
        'Location'
    )

    data_list = []

    # Retrieve the app bundle identifier and search for the user database
    app_identifier = get_app_id(WAZE_PREFERENCES_PLIST, context)
    source_path = context.get_seeker().search(
        f"*/{app_identifier}/Documents/user.db*",
        return_on_first_hit=True
    )
    if not source_path:
        return data_headers, data_list, source_path

    query = '''
    SELECT 
	    SP.id,
	    P.id,
        SP.share_time,
	    coalesce(SP.name, P.name) AS "name",
        P.house,
        P.street,
        P.city,
        P.state,
        P.country,
        CAST((CAST(P.latitude AS REAL) / 1000000) AS TEXT) AS "latitude",
        CAST((CAST(P.longitude AS REAL) / 1000000) AS TEXT) AS "longitude",
	    SP.created_time,
	    SP.modified_time,
        SP.access_time,
	    SP.owner_id,
        P.venue_id
    FROM SHARED_PLACES AS "SP"
    LEFT JOIN PLACES AS "P" ON (SP.place_id = P.id)                   
    '''

    db = get_sqlite_db_records(source_path, query)
    if not db:
        return data_headers, data_list, source_path

    for record in db:
        try:
            # Initialize output fields
            fields = {
                F_SHARED: None,
                F_NAME: None,
                F_HOUSE_NUM: None,
                F_STREET: None,
                F_CITY: None,
                F_STATE: None,
                F_COUNTRY: None,
                F_LAT: None,
                F_LON: None,
                F_CREATED: None,
                F_MODIFIED: None,
                F_LAST_ACCESS: None,
                F_WAZE_ID: None,
                F_VENUE_ID: None,
                F_LOCATION: None
            }

            # Extract only the identifiers needed for location metadata
            shared_id = record[0]
            place_id = record[1]

            # Convert timestamps to UTC
            fields[F_SHARED] = convert_unix_ts_to_utc(record[2])
            fields[F_CREATED] = convert_unix_ts_to_utc(record[11])
            fields[F_MODIFIED] = convert_unix_ts_to_utc(record[12])
            fields[F_LAST_ACCESS] = convert_unix_ts_to_utc(record[13])

            # Name
            fields[F_NAME] = record[3]

            # Address
            fields[F_HOUSE_NUM] = record[4]
            fields[F_STREET] = record[5]
            fields[F_CITY] = record[6]
            fields[F_STATE] = record[7]
            fields[F_COUNTRY] = record[8]

            # Coordinates
            fields[F_LAT] = record[9]
            fields[F_LON] = record[10]

            # Waze User Identifier
            fields[F_WAZE_ID] = str(record[14]).rsplit('|', maxsplit=1)[-1] if record[14] else None

            # Identifiers
            fields[F_VENUE_ID] = record[15]

            # Precise location within the source database table for validation
            location_list = [ f"SHARED_PLACES (id: {shared_id})" ]
            if place_id is not None:
                location_list.append(f"PLACES (id: {place_id})")
            fields[F_LOCATION] = COMMA_SEP.join(location_list)

            # Base row for both lists
            #base_data = tuple(fields.values())
            base_data = (
                fields[F_SHARED],
                fields[F_NAME],
                fields[F_HOUSE_NUM],
                fields[F_STREET],
                fields[F_CITY],
                fields[F_STATE],
                fields[F_COUNTRY],
                fields[F_LAT],
                fields[F_LON],
                fields[F_CREATED],
                fields[F_MODIFIED],
                fields[F_LAST_ACCESS],
                fields[F_WAZE_ID],
                fields[F_VENUE_ID],
                fields[F_LOCATION],
            )

            # LAVA row
            data_list.append(base_data)

        except (ValueError, IndexError, TypeError) as ex:
            _id = record[0] if record and len(record) > 0 else 'UNKNOWN'
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Failed parsing record SHARED_PLACES {_id} in {source_path}: {ex}")
            continue

    return data_headers, data_list, source_path


@artifact_processor
def waze_planned_events(context):
    """
    Extracts locations and scheduled destinations synchronized from calendar
    events.  Waze reads the device calendar, resolves each event address
    against the PLACES table and stores the result in EVENTS_PLACES inside
    user.db.
    """

    data_headers = (
        ('Created Time', 'datetime'),
        'Type',
        'Event Name',
        ('Start Time', 'datetime'),
        ('End Time', 'datetime'),
        'All Day',
        'Image URL',
        'Place Name',
        'House Number',
        'Street',
        'City',
        'State',
        'Country',
        'Latitude',
        'Longitude',
        'Origin Place Name',
        'Venue ID',
        'Event ID',
        'Location'
    )

    data_list = []
    data_list_html = []

    # Retrieve the app bundle identifier and search for the user database
    app_identifier = get_app_id(WAZE_PREFERENCES_PLIST, context)
    source_path = context.get_seeker().search(
        f"*/{app_identifier}/Documents/user.db*",
        return_on_first_hit=True
    )
    if not source_path:
        return data_headers, (data_list, data_list_html), source_path

    db = open_sqlite_db_readonly(source_path)
    if not db:
        return data_headers, (data_list, data_list_html), source_path

    try:
        cursor = db.cursor()
        # origin_place_name
        if does_column_exist_in_db(source_path, 'EVENTS_PLACES', 'origin_place_id'):
            has_origin_place_name = "OP.name"
            join_origin_place_name = "LEFT JOIN PLACES AS \"OP\" ON (E.origin_place_id = OP.id)"
            has_op_id = "OP.id"
        else:
            has_origin_place_name = "NULL"
            join_origin_place_name = ""
            has_op_id = "NULL"

        query = f'''
        SELECT
            E.id,
            P.id,
            {has_op_id},
            E.created_time,
            CASE 
                WHEN E.type = 1 THEN 'Calendar'
                WHEN E.type = 2 THEN 'Partner'
                WHEN E.type = 6 THEN 'Reservation'
                ELSE coalesce(CAST(E.type AS TEXT), 'N/A')
            END AS "event_type",
            E.name,
            E.start_time,
            E.end_time,
            CASE
                WHEN E.all_day = 0 THEN 'No'
                WHEN E.all_day = 1 THEN 'Yes'
                ELSE coalesce(CAST(E.all_day AS TEXT), 'N/A')
            END AS "all_day",
            E.image_url,
            P.name,
            P.house,
            P.street,
            P.city,
            P.state,
            P.country,
            CAST((CAST(P.latitude  AS REAL) / 1000000) AS TEXT) AS "latitude",
            CAST((CAST(P.longitude AS REAL) / 1000000) AS TEXT) AS "longitude",
            {has_origin_place_name} AS "origin_name",
            P.venue_id,
            E.event_id
        FROM EVENTS_PLACES AS "E"
        LEFT JOIN PLACES AS "P" ON (E.place_id = P.id)
        {join_origin_place_name}
        ORDER BY E.created_time DESC
        '''

        cursor.execute(query)
        for record in cursor:
            try:
                # Initialize output fields
                fields = {
                    F_CREATED: None,
                    F_EVENT_TYPE: None,
                    F_EVENT_NAME: None,
                    F_START_TIME: None,
                    F_END_TIME: None,
                    F_ALL_DAY: None,
                    F_IMAGE_URL: None,
                    F_NAME: None,
                    F_HOUSE_NUM: None,
                    F_STREET: None,
                    F_CITY: None,
                    F_STATE: None,
                    F_COUNTRY: None,
                    F_LAT: None,
                    F_LON: None,
                    F_ORIGIN_PLACE: None,
                    F_VENUE_ID: None,
                    F_EVENT_ID: None,
                    F_LOCATION: None
                }

                # Extract only the identifiers needed for location metadata
                event_id = record[0]
                place_id = record[1]
                orig_place_id = record[2]

                # Convert timestamps to UTC
                fields[F_CREATED] = convert_unix_ts_to_utc(record[3])
                fields[F_START_TIME] = convert_unix_ts_to_utc(record[6])
                fields[F_END_TIME] = convert_unix_ts_to_utc(record[7])

                # Event metadata
                fields[F_EVENT_TYPE] = record[4]
                fields[F_EVENT_NAME] = record[5]

                # Boolean flags
                fields[F_ALL_DAY] = record[8]

                # Image URL
                fields[F_IMAGE_URL] = record[9]

                # Place address
                fields[F_NAME] = record[10]
                fields[F_HOUSE_NUM] = record[11]
                fields[F_STREET] = record[12]
                fields[F_CITY] = record[13]
                fields[F_STATE] = record[14]
                fields[F_COUNTRY] = record[15]

                # Coordinates
                fields[F_LAT] = record[16]
                fields[F_LON] = record[17]

                # Origin place name
                fields[F_ORIGIN_PLACE] = record[18]

                # Place identifiers
                fields[F_VENUE_ID] = record[19]
                fields[F_EVENT_ID] = record[20]

                # Precise location within the source database table for validation
                location_list = [ f"EVENTS_PLACES (id: {event_id})" ]
                if place_id is not None or orig_place_id is not None:
                    place_ids = []
                    if place_id is not None:
                        place_ids.append(f"(id: {place_id})")
                    if orig_place_id is not None:
                        place_ids.append(f"(id: {orig_place_id})")
                    # Joins the IDs matching your exact formatting style
                    location_list.append(f"PLACES {', '.join(place_ids)}")
                fields[F_LOCATION] = COMMA_SEP.join(location_list)

                # Base row
                #base_data = tuple(fields.values())
                base_data = (
                    fields[F_CREATED],
                    fields[F_EVENT_TYPE],
                    fields[F_EVENT_NAME],
                    fields[F_START_TIME],
                    fields[F_END_TIME],
                    fields[F_ALL_DAY],
                    format_url(fields[F_IMAGE_URL]),                        # 6 Image URL (Plain)
                    fields[F_NAME],
                    fields[F_HOUSE_NUM],
                    fields[F_STREET],
                    fields[F_CITY],
                    fields[F_STATE],
                    fields[F_COUNTRY],
                    fields[F_LAT],
                    fields[F_LON],
                    fields[F_ORIGIN_PLACE],
                    fields[F_VENUE_ID],
                    fields[F_EVENT_ID],
                    fields[F_LOCATION],
                )

                # HTML row
                data_list_html.append((
                    *base_data[:6],
                    format_url(fields[F_IMAGE_URL], html_format=True),      # Replaces index 6
                    *base_data[7:]
                ))

                # LAVA row
                data_list.append(base_data)

            except (ValueError, IndexError, TypeError) as ex:
                _id = record[0] if record and len(record) > 0 else 'UNKNOWN'
                logfunc(f"[{context.get_artifact_name()}] "
                        f"Error - Failed parsing record EVENTS_PLACES {_id} in {source_path}: {ex}")
                continue

    except sqlite3.Error as db_ex:
        # Log fatal database errors (e.g., malformed DB or missing tables)
        logfunc(f"[{context.get_artifact_name()}] "
                f"Error - executing query on {source_path}: {db_ex}")
    finally:
        # Ensure the database connection is closed safely
        db.close()

    return data_headers, (data_list, data_list_html), source_path


def _parse_tts_table(cursor, table_name: str, source_path: str, context, data_list: list) -> None:
    """
    Extract TTS records from a single table.
    """

    # Dynamic query for each validated table
    query = f'''
    SELECT
	    T.ROWID,
        T.update_time,
        CASE
            WHEN T.text_type = 0 THEN 'Prompt'
            WHEN T.text_type = 1 THEN 'Maneuver'
            WHEN T.text_type = 2 THEN 'Route'
            WHEN T.text_type = 3 THEN 'Alert'
            ELSE COALESCE(CAST(T.text_type AS TEXT), 'N/A')
        END AS "text_type",
        T.text
    FROM {table_name} AS "T"
    '''

    try:
        cursor.execute(query)

        for record in cursor:
            try:
                # Unpack record for clarity
                (row_id, raw_ts, text, text_type) = record

                # Convert timestamps to UTC
                timestamp = convert_unix_ts_to_utc(raw_ts)

                # Precise location within the source database table for validation
                location = f"{table_name} (rowid: {row_id})"

                # Create a tuple of the variables to check for content
                data_row = (
                    timestamp, text_type, text, location
                )

                # LAVA row
                data_list.append(data_row)

            except (ValueError, IndexError, TypeError) as ex:
                logfunc(
                    f"[{context.get_artifact_name()}] "
                    f"Error - Failed parsing record in table "
                    f"{table_name} rowid {row_id} "
                    f"in {source_path}: {ex}"
                )

    except sqlite3.Error as ex:
        # Log fatal database errors (e.g., malformed DB or missing tables)
        logfunc(
            f"[{context.get_artifact_name()}] "
            f"Error - executing query on table "
            f"{table_name} in {source_path}: {ex}"
        )


@artifact_processor
def waze_tts(context):
    """
    Dynamically scans all tables in tts.db to extract a history of 
    text-to-speech instructions provided during navigation.
    """

    data_headers = (
        ('Timestamp', 'datetime'),
        'Text Type',
        'Text',
        'Location'
    )

    data_list = []

    # Retrieve the app bundle identifier and search for the TTS database
    app_identifier = get_app_id(WAZE_PREFERENCES_PLIST, context)
    source_path = context.get_seeker().search(
        f"*/{app_identifier}/Library/Caches/tts/tts.db*",
        return_on_first_hit=True
    )
    if not source_path:
        return data_headers, data_list, source_path

    # Get all table names from the database
    query = "SELECT name FROM sqlite_master WHERE type='table'"
    all_tables = get_sqlite_db_records(source_path, query)
    if not all_tables:
        return data_headers, data_list, source_path

    # Open the database ONCE for all subsequent table scans
    db_table = open_sqlite_db_readonly(source_path)
    if not db_table:
        return data_headers, data_list, source_path

    try:
        cursor = db_table.cursor()

        for table in all_tables:
            # table name
            table_name = table[0]

            if not TTS_TABLE_NAME_RE.match(table_name):
                logfunc(f"[{context.get_artifact_name()}] "
                        f"Invalid table name skipped: {table_name}")
                continue

            _parse_tts_table(cursor, table_name, source_path, context, data_list)

    finally:
        # Ensure the database connection is closed safely
        db_table.close()

    return data_headers, data_list, source_path
