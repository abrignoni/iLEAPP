"""
Foursquare Swarm Artifact Module
Extracts account, contact, and check-in history from Foursquare Swarm on iOS, 
including social graph details, shared tips, earned stickers, venue photos, 
and check-in comments with geographic metadata.
"""
# pylint: disable=too-many-lines

__artifacts_v2__ = {
    "foursquare_swarm_account": {
        "name": "Foursquare Swarm - Account",
        "description": "Parses and extracts Foursquare Swarm Account",
        "author": "@djangofaiola",
        "creation_date": "2024-11-10",
        "last_update_date": "2026-05-25",
        "requirements": "none",
        "category": "Foursquare Swarm",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Caches/foursquare.sqlite*",
                  "*/com.pinterest.PINDiskCache.PINRemoteImageManagerCache/*%2Fimg%2Fuser%2F*",
                  "*/com.pinterest.PINDiskCache.PINRemoteImageManagerCache/*%2Fimg%2Fgeneral%2F*"),
        "output_types": [ "standard" ],
        "html_columns": [ "Facebook Profile", "Twitter Profile", "Profile Picture URL", "UID" ],
        "artifact_icon": "user"
    },
    "foursquare_swarm_contacts": {
        "name": "Foursquare Swarm - Contacts",
        "description": "Parses and extracts Foursquare Swarm Contacts",
        "author": "@djangofaiola",
        "creation_date": "2024-11-10",
        "last_update_date": "2026-05-25",
        "requirements": "none",
        "category": "Foursquare Swarm",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Caches/foursquare.sqlite*",
                  "*/com.pinterest.PINDiskCache.PINRemoteImageManagerCache/*%2Fimg%2Fuser%2F*"),
        "output_types": [ "standard" ],
        "html_columns": [ "Profile Picture URL", "UID" ],
        "artifact_icon": "users"
    },
    "foursquare_swarm_address_book": {
        "name": "Foursquare Swarm - Address Book",
        "description": "Parses and extracts device address book contacts harvested by Swarm",
        "author": "@djangofaiola",
        "creation_date": "2026-04-16",
        "last_update_date": "2026-05-25",
        "requirements": "none",
        "category": "Foursquare Swarm",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Caches/foursquare.sqlite*"),
        "output_types": [ "standard" ],
        "html_columns": [ "Profile Picture", "Phone Numbers", "Facebook Profile" ],
        "artifact_icon": "book-open"
    },
    "foursquare_swarm_checkins": {
        "name": "Foursquare Swarm - Check-ins",
        "description": "Parses and extracts Foursquare Swarm manual and passive check-ins",
        "author": "@djangofaiola",
        "creation_date": "2024-11-10",
        "last_update_date": "2026-05-25",
        "requirements": "none",
        "category": "Foursquare Swarm",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Caches/foursquare.sqlite*",
                  "*/com.pinterest.PINDiskCache.PINRemoteImageManagerCache/*%2Fimg%2Fgeneral%2F*",
                  "*/com.pinterest.PINDiskCache.PINRemoteImageManagerCache/*%2Fimg%2Fcheckin%2F*"),
        "output_types": [ "all" ],
        "html_columns": [ "Facebook Profile", "Twitter Profile", "Instagram Profile",
                          "Venue URL", "Check-in URL", "Website", "Entities" ],
        "artifact_icon": "user-check"
    },
    "foursquare_swarm_tips": {
        "name": "Foursquare Swarm - Tips",
        "description": "Parses and extracts Foursquare Swarm Tips",
        "author": "@djangofaiola",
        "creation_date": "2024-11-10",
        "last_update_date": "2026-05-25",
        "requirements": "none",
        "category": "Foursquare Swarm",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Caches/foursquare.sqlite*",
                  "*/com.pinterest.PINDiskCache.PINRemoteImageManagerCache/*%2Fimg%2Ftips%2F*",
                  "*/com.pinterest.PINDiskCache.PINRemoteImageManagerCache/*%2Fimg%2Fgeneral%2F*"),
        "output_types": [ "all" ],
        "html_columns": [ "Tip URL", "Short URL", "Photo URL" ],
        "artifact_icon": "info"
    },
    "foursquare_swarm_stickers": {
        "name": "Foursquare Swarm - Stickers",
        "description": "Parses and extracts Foursquare Swarm Stickers",
        "author": "@djangofaiola",
        "creation_date": "2024-11-10",
        "last_update_date": "2026-05-25",
        "requirements": "none",
        "category": "Foursquare Swarm",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Caches/foursquare.sqlite*",
                  "*/com.pinterest.PINDiskCache.PINRemoteImageManagerCache/*%2Fimg%2Fsticker%2F*",
                  "*/com.pinterest.PINDiskCache.PINRemoteImageManagerCache/*%2Fimg%2Fbadge%2F*"),
        "output_types": [ "lava", "html", "tsv" ],
        "html_columns": [ "Sticker URL" ],
        "artifact_icon": "award"
    },
    "foursquare_swarm_venues_history": {
        "name": "Foursquare Swarm - Venues History",
        "description": "Parses and extracts Foursquare Swarm Venues History",
        "author": "@djangofaiola",
        "creation_date": "2024-11-10",
        "last_update_date": "2026-05-25",
        "requirements": "none",
        "category": "Foursquare Swarm",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Caches/foursquare.sqlite*",
                  "*/com.pinterest.PINDiskCache.PINRemoteImageManagerCache/*%2Fimg%2Fgeneral%2F*",
                  "*/com.pinterest.PINDiskCache.PINRemoteImageManagerCache/*%2Fimg%2Fvenue%2F*"),
        "output_types": [ "all" ],
        "html_columns": [ "Facebook Profile", "Twitter Profile", "Instagram Profile",
                          "Foursquare Profile", "Website" ],
        "artifact_icon": "map-pin"
    },
    "foursquare_swarm_photos": {
        "name": "Foursquare Swarm - Photos",
        "description": "Parses and extracts Foursquare Swarm photos from all artifacts",
        "author": "@djangofaiola",
        "creation_date": "2024-11-10",
        "last_update_date": "2026-05-25",
        "requirements": "none",
        "category": "Foursquare Swarm",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Caches/foursquare.sqlite*",
                  "*/mobile/Containers/Data/Application/*/Library/Caches/"
                  "com.pinterest.PINDiskCache.PINRemoteImageManagerCache/*%2Fimg%2F*"),
        "output_types": [ "all" ],
        "html_columns": [ "Facebook Profile", "Twitter Profile", "Instagram Profile",
                          "Foursquare Profile", "Website", "Photo URL" ],
        "artifact_icon": "camera"
    },
    "foursquare_swarm_comments": {
        "name": "Foursquare Swarm - Comments",
        "description": "Parses and extracts all Foursquare Swarm comments from "
                       "check-ins, plans, tips, lists, and stickers",
        "author": "@djangofaiola",
        "creation_date": "2024-11-10",
        "last_update_date": "2026-05-25",
        "requirements": "none",
        "category": "Foursquare Swarm",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Caches/foursquare.sqlite*"),
        "output_types": [ "all" ],
        "html_columns": [ "Entities" ],
        "artifact_icon": "message-square"
    },
    "foursquare_swarm_friend_requests": {
        "name": "Foursquare Swarm - Friend Requests",
        "description": "Parses and extracts Foursquare Swarm incoming and outgoing friend requests",
        "author": "@djangofaiola",
        "creation_date": "2026-04-18",
        "last_update_date": "2026-05-25",
        "requirements": "none",
        "category": "Foursquare Swarm",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Caches/foursquare.sqlite*",
                  "*/com.pinterest.PINDiskCache.PINRemoteImageManagerCache/*%2Fimg%2Fuser%2F*"),                  
        "output_types": [ "standard" ],
        "html_columns": [ "Requester ID", "Requestee ID" ],
        "artifact_icon": "user-plus"
    },
    "foursquare_swarm_plans": {
        "name": "Foursquare Swarm - Plans",
        "description": "Parses and extracts Foursquare Swarm Plans (meetups)",
        "author": "@djangofaiola",
        "creation_date": "2026-04-18",
        "last_update_date": "2026-05-25",
        "requirements": "none",
        "category": "Foursquare Swarm",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Caches/foursquare.sqlite*",
                  "*/com.pinterest.PINDiskCache.PINRemoteImageManagerCache/*%2Fimg%2Fgeneral%2F*",
                  "*/com.pinterest.PINDiskCache.PINRemoteImageManagerCache/*%2Fimg%2Fuser%2F*"),                  
        "output_types": [ "standard" ],
        "html_columns": [ "Entities" ],
        "artifact_icon": "calendar"
    },
    "foursquare_swarm_events": {
        "name": "Foursquare Swarm - Events",
        "description": "Extracts scheduled events (concerts, movies, etc.) linked to venues",
        "author": "@djangofaiola",
        "creation_date": "2026-04-18",
        "last_update_date": "2026-05-25",
        "requirements": "none",
        "category": "Foursquare Swarm",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Caches/foursquare.sqlite*",
                  "*/com.pinterest.PINDiskCache.PINRemoteImageManagerCache/*%2Fimg%2Fevent%2F*",
                  "*/com.pinterest.PINDiskCache.PINRemoteImageManagerCache/*%2Fimg%2Fgeneral%2F*"),
        "output_types": [ "standard" ],
        "html_columns": [ "Event URL" ],
        "artifact_icon": "calendar"
    },
    "foursquare_swarm_saved_lists": {
        "name": "Foursquare Swarm - Saved Lists",
        "description": "Parses and extracts user-created lists and saved venues (items)",
        "author": "@djangofaiola",
        "creation_date": "2026-04-20",
        "last_update_date": "2026-05-25",
        "requirements": "none",
        "category": "Foursquare Swarm",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Caches/foursquare.sqlite*"),
        "output_types": [ "all" ],
        "html_columns": [ "List URL", "Source URL" ],
        "artifact_icon": "list"
    },
    "foursquare_swarm_location_history": {
        "name": "Foursquare Swarm - Location History",
        "description": "Extracts passive location history (GPS breadcrumbs)",
        "author": "@djangofaiola",
        "creation_date": "2026-04-20",
        "last_update_date": "2026-05-25",
        "requirements": "none",
        "category": "Foursquare Swarm",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Caches/foursquare.sqlite*"),
        "output_types": ["all"],
        "artifact_icon": "navigation"
    },
    "foursquare_swarm_plog": {
        "name": "Foursquare Swarm - Logs",
        "description": "Parses and extracts Foursquare Swarm/Pilgrim SDK Logs",
        "author": "@djangofaiola",
        "creation_date": "2024-11-10",
        "last_update_date": "2026-05-25",
        "requirements": "none",
        "category": "Foursquare Swarm",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Caches/foursquare.sqlite*",),
        "output_types": [ "standard" ],
        "html_columns": [ "Details" ],
        "artifact_icon": "terminal"
    },
    "foursquare_swarm_feed": {
        "name": "Foursquare Swarm - Activity Feed & Bulletins",
        "description": "Parses and extracts the social activity feed, notifications, "
                       "and interactive bulletins",
        "author": "@djangofaiola",
        "creation_date": "2026-05-16",
        "last_update_date": "2026-05-25",
        "requirements": "none",
        "category": "Foursquare Swarm",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Caches/foursquare.sqlite*",
                  "*/com.pinterest.PINDiskCache.PINRemoteImageManagerCache/*%2Fimg%2F*"),
        "output_types": [ "standard" ],
        "html_columns": [ "Participants", "Replies", "Social Actors", 
                          "Image URL", "Entities", "Target" ],
        "artifact_icon": "activity"
    },
}

import json
import html
import sqlite3
import re
from pathlib import Path
from urllib.parse import urlparse
from scripts.filetype import get_type
from scripts.ilapfuncs import get_sqlite_db_records, open_sqlite_db_readonly, \
    does_column_exist_in_db, get_plist_content, check_in_embedded_media, \
    convert_unix_ts_to_utc, get_birthdate, check_in_media, artifact_processor, logfunc

# Constants
COMMA_SEP = ', '
LIST_SEP = '|'
SQL_LIST_SEP = "'|'"
HTML_LINE_BREAK = '<br>'
HTML_HORZ_RULE = '<hr>'

ALLOWED_URL_SCHEMES = (
    'http',
    'https',
    'mailto',
    'tel'
)

MAX_URL_LENGTH = 4096


def get_device_file_path(file_path: str, context) -> str:
    """
    Converts a local report file path back to the original iOS device path.
    Strips the local report base directory and reconstructs the /private/var 
    structure for File System extractions or preserves Domain paths for iTunes.
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

    except (ValueError, TypeError, AttributeError) as e:
        logfunc(f"Error - format_url parse failed for {str_url!r}: {e}")

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


def facebook_url(fid : str | None, html_format : bool = False) -> str:
    """
    Generate a Facebook profile URL from a given ID and format it using format_url.
    """

    # Handle missing, empty, or literal 'null' values
    if not fid or str(fid).strip().lower() == 'null':
        return ''

    # Construct the base URL using the Facebook profile ID
    url = f"https://www.facebook.com/profile.php?id={fid.strip()}"

    # We still call format_url for safe HTML construction
    if html_format:
        return format_url(url, html_format=html_format, label=fid)

    return url


def twitter_url(tid : str | None, html_format : bool = False) -> str:
    """
    Generate a Twitter (X) profile URL from a given ID and format it using format_url.
    """

    # Handle missing, empty, or literal 'null' values
    if not tid or str(tid).strip().lower() == 'null':
        return ''

    # Construct the base URL using the Twitter handle
    url = f"https://twitter.com/{tid.strip()}"

    # We still call format_url for safe HTML construction
    if html_format:
        return format_url(url, html_format=html_format, label=tid)

    return url


def instagram_url(iid : str | None, html_format: bool = False) -> str:
    """
    Generate an Instagram profile URL from a given ID and format it using format_url.
    """

    # Handle missing, empty, or literal 'null' values
    if not iid or str(iid).strip().lower() == 'null':
        return ''

    # Construct the base URL using the Instagram handle
    url = f"https://www.instagram.com/{iid.strip()}"

    # We still call format_url for safe HTML construction
    if html_format:
        return format_url(url, html_format=html_format, label=iid)

    return url


def foursquare_uid_url(uid: str | None, url: str | None, html_format: bool = False) -> str:
    """
    Generate a Foursquare profile link. Use canonical URL if available,
    otherwise fall back to the UID-based URL. If UID is missing but URL
    exists, render the URL as the visible label in HTML.

    Behavior:
    - If uid is missing and url is missing -> return ''
    - If url missing but uid present -> build fallback https://foursquare.com/user/{uid}
    - If uid present and html_format True -> use uid as label
    - If uid missing and html_format True -> use the URL (or a readable segment) as label
    - In plain text do not show UID as label; return the URL (fallback if needed)
    """

    # Normalize inputs
    uid_val = None
    if uid and str(uid).strip().lower() not in ('', 'null', 'none'):
        uid_val = str(uid).strip()

    url_val = None
    if url and str(url).strip().lower() not in ('', 'null', 'none'):
        url_val = str(url).strip()

    # If both missing, nothing to show
    if not uid_val and not url_val:
        return ''

    # Build fallback URL when canonical missing but uid present
    if not url_val and uid_val:
        target_url = f"https://foursquare.com/user/{uid_val}"
    else:
        target_url = url_val

    # Decide label: only use uid as label when html_format and uid present.
    # If uid missing but html_format True, use a readable label derived from URL
    # (last path segment) or the URL itself.
    label = None
    if html_format:
        if uid_val:
            label = uid_val
        else:
            # Try to extract a short, readable label from the URL path
            try:
                parsed = urlparse(target_url)
                path = parsed.path.rstrip('/').split('/')
                candidate = path[-1] if path and path[-1] else None
                # fallback to hostname or full URL if nothing readable
                label = candidate or parsed.hostname or target_url
            except (ValueError, AttributeError):
                label = target_url

    # Call the generalized format_url which enforces forensic rules
    return format_url(target_url, html_format=html_format, label=label)


def _build_photo_map(context):
    """
    Builds and incrementally updates a dual-tier index of cached image files
    found in the PINDiskCache directory.
    Safe to call multiple times: new entries are merged into the existing cache.
    Already-indexed keys are overwritten with the same value (idempotent).

    Index structure:
      'direct'   : { "resolution%2Ffilename" : "/full/path/to/file" }
                   Exact lookup by full resolution+filename suffix (Tier 1).
      'fallback' : { "filename" : { 'path': ..., 'priority': ... } }
                   Lookup by filename only, retaining the highest-resolution
                   path seen so far (Tier 2).
    """

    seeker = context.get_seeker()
    session_key = getattr(seeker, 'data_folder', None) or id(seeker)

    # Reset the cache when the case changes, so photo paths from a previous
    # analysis run do not contaminate the current one.
    if (not hasattr(_build_photo_map, 'session_key')
            or _build_photo_map.session_key != session_key):
        _build_photo_map.data = { 'direct': {}, 'fallback': {} }
        _build_photo_map.session_key = session_key

    cache = _build_photo_map.data

    # Skip iOS-generated images masks, e.g. ...%2Epng-_{48, 48}1_
    skip_pattern = re.compile(r'-_\{\d+,\s*\d+\}\d+_$', re.IGNORECASE)

    # Match the percent-encoded resource URL used as the PINDiskCache filename.
    # Example: https%3A%2F%2Ffastly%2E4sqi%2Enet%2Fimg%2Fgeneral%2Foriginal%2F12345%2Ejpg
    # Pattern groups:
    #   Group 1 — resolution segment  (e.g. "original", "width768", "96x96")
    #   Group 2 — encoded filename     (e.g. "12345%2Ejpg" or extensionless)
    match_pattern = re.compile(
        r'%2Fimg%2F.+%2F'                # ...%2Fimg%2F<bucket>%2F
        r'((?:(?!%2F).)+)'               # group 1: resolution segment
        r'%2F'
        r'(.+?)(?:\r?$)',                # group 2: encoded filename
        re.IGNORECASE
    )

    # The basename of a PINDiskCache file IS the percent-encoded resource URL,
    # so we match directly against the key without any Path().name extraction
    lookup_map = context.get_filename_lookup_map()

    for encoded_key, paths in lookup_map.items():
        encoded_key = encoded_key.strip()

        # Skip iOS image masks
        if skip_pattern.search(encoded_key):
            continue

        match = match_pattern.search(encoded_key)
        if not match:
            continue

        resolution = match.group(1).lower()  # e.g. "original", "width768", "96x96"
        filename   = match.group(2)          # e.g. "...OOAZzKNe1XKOlxc5xY%2Ejpg"
        full_path  = paths[0]

        # Tier 1: map the full "resolution%2Ffilename" suffix to the file path.
        # Used when the DB suffix includes the resolution segment.
        full_suffix = f"{resolution}%2F{filename}"
        cache['direct'][full_suffix] = full_path

        # Tier 2: map the filename to the highest-resolution path seen so far.
        # "original" always wins; numeric sizes are compared by their largest dimension.
        try:
            if resolution == 'original':
                priority = 99999
            else:
                dims = re.findall(r'\d+', resolution)
                priority = max(map(int, dims)) if dims else 0

        except (ValueError, TypeError):
            # Fallback for unexpected resolution format
            priority = 0

        fb = cache['fallback']
        # Update only if the new path has higher resolution priority
        if filename not in fb or priority > fb[filename]['priority']:
            fb[filename] = {'path': full_path, 'priority': priority}

    return cache


def _check_in_media_with_suffix(suffix, photo_map):
    """
    Retrieves the best media path from the index based on the provided suffix.
    1. Attempts a direct exact match
    2. Falls back to the best available resolution

    Returns:
    {
        'path': str,
        'match_type': str,
        'resolution': str|None
    }
    """

    if not suffix or not isinstance(photo_map, dict):
        return None

    # Normalize the suffix: remove leading slashes and convert to encoded format
    search_key = suffix.lstrip('/').replace('.', '%2E')

    # Tier 1: Direct exact search
    # Check if the complete suffix (e.g., 'original%2Ffilename') exists
    direct_map = photo_map.get('direct', {})
    path = direct_map.get(f"original%2F{search_key}")
    if path:
        return {
            'path': path,
            'match_type': 'direct',
            'resolution': 'original'
        }

    # Tier 2: Fallback to best resolution
    # Extract the filename only from the suffix (everything after the last %2F)
    filename = search_key.rsplit('%2F', 1)[-1]

    fallback_map = photo_map.get('fallback', {})
    fallback_data = fallback_map.get(filename)
    if isinstance(fallback_data, dict):
        return {
            'path': fallback_data.get('path'),
            'match_type': 'fallback',
            'resolution': fallback_data.get('resolution')
        }

    return None


def resolve_media_reference(suffix, photo_map, context, fallback_ext=None):
    """
    Resolves a media file from cache and prepares
    forensic/media metadata for iLEAPP artifacts.

    Returns:
    {
        'found': bool,
        'media_path': str|None,
        'device_path': str|None,
        'media_ref_id': str|None,
        'mime_type': str|None,
        'filename': str|None,
        'match_type': str|None,
        'resolution': str|None
    }
    """

    result = {
        'found': False,
        'media_path': None,
        'device_path': None,
        'media_ref_id': None,
        'mime_type': None,
        'filename': None,
        'match_type': None,
        'resolution': None
    }

    media_data = _check_in_media_with_suffix(suffix, photo_map)
    if not media_data:
        return result

    # Backward compatibility if old resolver returns only path
    if isinstance(media_data, str):
        media_data = {
            'path': media_data,
            'match_type': 'unknown',
            'resolution': None
        }

    media_path = media_data.get('path')
    if not media_path:
        return result

    file_name = Path(media_path).name

    # Prefer extension from suffix
    media_ext = Path(suffix).suffix.strip('.')

    # Fallback to actual media file extension
    if not media_ext:
        media_ext = Path(media_path).suffix.strip('.')

    # Optional fallback extension
    if not media_ext:
        media_ext = fallback_ext

    mime = None

    if media_ext:
        matcher = get_type(mime=None, ext=media_ext)
        if matcher:
            mime = getattr(matcher, 'mime', None)

    media_ref_id = check_in_media(media_path, name=file_name, force_type=mime)
    device_path = None
    if media_ref_id:
        device_path = get_device_file_path(media_path, context)

    result.update({
        'found': True,
        'media_path': media_path,
        'device_path': device_path,
        'media_ref_id': media_ref_id,
        'mime_type': mime,
        'filename': file_name,
        'match_type': media_data.get('match_type'),
        'resolution': media_data.get('resolution')
    })

    return result


def _resolve_coredata_relationship(context, db, entity_name: str,
                                   relationship_suffix: str, inverse_suffix: str) -> dict:
    """
    Resolves Core Data many-to-many table and column names dynamically.
    
    Args:
        db: SQLite database connection.
        entity_name (str): The Core Data entity name (e.g., 'FSCheckin').
        relationship_suffix (str): The property/relationship name uppercase (e.g., 'WITHFRIENDS').
        
    Returns:
        dict: Contains 'table', 'inverse_col' (parent), and 'target_col' (destination/user).
    """
    res = { 'table': None, 'inverse_col': None, 'target_col': None }

    try:
        cursor = db.cursor()

        # Get the Z_ENT ID for the requested entity from Z_PRIMARYKEY
        cursor.execute("SELECT Z_ENT FROM Z_PRIMARYKEY WHERE Z_NAME = ?;", (entity_name,))
        row = cursor.fetchone()
        if not row:
            return res

        # This will be 6 for FSCheckin in your current DB
        z_ent = row[0]

        # Reconstruct the expected Core Data table name format: Z_<Z_ENT><SUFFIX>
        expected_table = f"Z_{z_ent}{relationship_suffix}"

        # Verify if this table actually exists in sqlite_master
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name = ?;", 
            (expected_table,)
        )
        table_match = cursor.fetchone()

        if table_match:
            actual_table = table_match[0]
            res['table'] = actual_table

            # Parse columns to isolate INVERSE (parent) and target (destination)
            cursor.execute(f"PRAGMA table_info({actual_table});")
            columns = [ col[1] for col in cursor.fetchall() ]

            # Parent column always contains <inverse_suffix>
            inv_cols = [c for c in columns if inverse_suffix in c]

            # Target column is the other relationship pointer
            # (excluding structural Core Data fields)
            tgt_cols = [c for c in columns
                if c not in inv_cols
                and c not in ('Z_PK', 'Z_ENT', 'Z_OPT')
                and not c.startswith('Z_FOK')]

            if inv_cols:
                res['inverse_col'] = inv_cols[0]
            if tgt_cols:
                res['target_col'] = tgt_cols[0]

    except sqlite3.Error as sq_ex:
        logfunc(f"[{context.get_artifact_name()}] "
                f"Database Error - Core Data resolution failed for {entity_name}: {str(sq_ex)}")
    except IndexError as idx_ex:
        logfunc(f"[{context.get_artifact_name()}] "
                "Schema Error - Unexpected columns in relationship table for "
                f"{entity_name}: {str(idx_ex)}")

    return res


@artifact_processor
def foursquare_swarm_account(context):
    """
    Extracts the owner account information from the foursquare.sqlite database.
    """

    data_headers = (
        ('Created', 'datetime'),
        ('Joined at', 'datetime'),
        ('Profile Picture', 'media', 'height: 48px; border-radius: 5%;'),
        'First Name',
        'Last Name',
        'Biography',
        'Gender',
        'Birthday',
        'Home City',
        ('Phone Number', 'phonenumber'),
        'Email',
        'Facebook Profile',
        'Twitter Profile',
        'Profile Picture URL',
        'Ping Notifications',
        'Friends',
        'Check-ins',
        'Mayorships',
        'UID',
        'Profile Picture Path (Cached)',
        'Location'
    )

    data_list = []
    data_list_html = []

    source_path = context.get_source_file_path('foursquare.sqlite')
    if not source_path:
        return data_headers, (data_list, data_list_html), source_path

    # This maps all files in the cache by their suffix
    photo_map = _build_photo_map(context)

    query = '''
    SELECT
        U.Z_PK AS "U_PK",
        FU.Z_PK AS "FU_PK",
	    (U.ZSWARMCREATEDAT + 978307200) AS "created",
	    (U.ZJOINEDAT + 978307200) AS "joined_at",
        U.ZFIRSTNAME,
        U.ZLASTNAME,
        U.ZBIO,
        U.ZGENDER,
        U.ZBIRTHDAY,
        U.ZHOMECITY,
        U.ZPHONE,
        U.ZEMAIL,
        FU.ZMONGOID AS "facebook",
        U.ZTWITTER,
        U.ZCANONICALURL,
        U.ZPHOTOPREFIX,
        U.ZPHOTOSUFFIX,
        U.ZCHECKINPINGS,
        coalesce(U.ZFRIENDSCOUNT, 0) AS "friends",
        COALESCE(U.ZCHECKINSCOUNT, 0) AS "checkins",
        COALESCE(U.ZMAYORSHIPSCOUNT, 0) AS "mayorships",
        U.ZMONGOID AS "uid"
    FROM ZFSUSER AS "U"
    LEFT JOIN ZFSFACEBOOKUSER AS "FU" ON (U.ZFACEBOOKUSER = FU.Z_PK)
    WHERE U.ZRELATIONSHIP = 'self'
    '''

    db_records = get_sqlite_db_records(source_path, query)
    if not db_records:
        return data_headers, (data_list, data_list_html), source_path

    for record in db_records:
        try:
            # Unpack record for clarity
            (user_pk, facebook_pk, raw_created, raw_joined, first_name, last_name, bio,
             gender, raw_bday, home_city, phone_number, email, facebook_id, twitter_id,
             swarm_url, pp_prefix, pp_suffix, checkin_pings_setting, friends, checkins,
             mayorships, uid) = record

            # Convert timestamps to UTC
            created = convert_unix_ts_to_utc(raw_created)
            joined = convert_unix_ts_to_utc(raw_joined)

            # Birthday as string
            bday = get_birthdate(raw_bday) if raw_bday is not None else ''

            # Profile Picture URL
            pp_url =f"{pp_prefix}original{pp_suffix}" if pp_prefix and pp_suffix else ''

            # This handles exact suffix matches and resolution fallbacks automatically
            media = resolve_media_reference(pp_suffix, photo_map, context)
            media_ref_id = media['media_ref_id']
            media_device_path = media['device_path']

            # Precise location within the source database table for validation
            location = [ f"ZFSUSER (Z_PK: {user_pk})" ]
            if facebook_pk is not None:
                location.append(f"ZFSFACEBOOKUSER (Z_PK: {facebook_pk})")
            location = COMMA_SEP.join(location)

            # Base row for both lists
            base_data = (
                created, joined,
                media_ref_id,
                first_name, last_name, bio,
                gender, bday, home_city, phone_number, email,
                facebook_url(facebook_id),                          # 11 Facebook URL (Plain)
                twitter_url(twitter_id),                            # 12 Twitter URL (Plain)
                format_url(pp_url),                                 # 13 Profile Picture URL (Plain)
                checkin_pings_setting, friends,
                checkins, mayorships,
                foursquare_uid_url(uid, swarm_url),                 # 18 Swarm Profile URL (Plain)
                media_device_path, location
            )

            # HTML row
            data_list_html.append((
                *base_data[:11],
                facebook_url(facebook_id, html_format=True),        # Replaces index 11
                twitter_url(twitter_id, html_format=True),          # Replaces index 12
                format_url(pp_url, html_format=True),               # Replaces index 13
                *base_data[14:18],
                foursquare_uid_url(uid, swarm_url,
                                   html_format=True),               # Replaces index 18
                *base_data[19:]
            ))

            # LAVA row
            data_list.append(base_data)

        except (ValueError, IndexError, TypeError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Failed parsing record ZFSUSER {record[0]} in {source_path}: {ex}")
            continue

    return data_headers, (data_list, data_list_html), source_path


# Pre-compile the regex at the module level for better performance
CLEAN_RELATIONSHIP_RE = re.compile(r'[\s\-_]+')

# Move the dictionary outside the function so it is created only once
RELATIONSHIP_MAP = {
    'self': 'Self',
    'friend': 'Friend',
    'friendship': 'Friend',
    'pendingme': 'Incoming Request',
    'pendingthem': 'Outgoing Request',
    'requested': 'Outgoing Request',
    'following': 'Following',
    'followingthem': 'Following',
    'followedby': 'Follower',
    'blocked': 'Blocked',
    'blockedby': 'Blocked By User',
    'ignored': 'Ignored',
    'archived': 'Archived',
    'muted': 'Muted',
    'contact': 'Address Book Contact',
    'stranger': 'Stranger',
    'suggested': 'Suggested',
    'recommended': 'Recommended',
    'nearby': 'Nearby',
    'none': 'None',
    'null': 'Unknown'
}

def _normalize_relationship(value: str | None) -> str:
    """
    Normalize Swarm user relationship values.
    """

    if value is None:
        return 'N/A'

    # Clean the input string
    raw_value = str(value).strip()
    if not raw_value:
        return 'N/D'

    # Apply the pre-compiled regex and convert to lowercase
    lookup = CLEAN_RELATIONSHIP_RE.sub('', raw_value.lower())

    # Retrieve the mapped label
    normalized = RELATIONSHIP_MAP.get(lookup)

    # If the value is not in the map, log it for investigation
    if not normalized:
        logfunc(
            f"[Foursquare Swarm] Unknown relationship value: "
            f"raw='{raw_value}' normalized='{lookup}'"
        )
        return raw_value

    return normalized


@artifact_processor
def foursquare_swarm_contacts(context):
    """
    Extracts Swarm contacts and friends from the foursquare.sqlite database.
    """

    data_headers = (
        ('Last Mentioned', 'datetime'),
        'Contact type',
        'Relationship',
        ('Profile Picture', 'media', 'height: 48px; border-radius: 5%;'),
        'First Name',
        'Last Name',
        'Gender',
        'Birthday',
        ('Phone Number', 'phonenumber'),
        'Email',
        'Profile Picture URL',
        'Blocked',
        'Muted',
        'Friendship Disabled',
        'Ping Notifications',
        'Friends',
        'Check-ins',
        'Mayorships',
        'UID',
        'Profile Picture Path (Cached)',
        'Location'
    )

    data_list = []
    data_list_html = []

    source_path = context.get_source_file_path('foursquare.sqlite')
    if not source_path:
        return data_headers, (data_list, data_list_html), source_path

    # This maps all files in the cache by their suffix
    photo_map = _build_photo_map(context)

    query = '''
    SELECT
	    U.Z_PK AS "U_PK",
        (U.ZLASTMENTIONED + 978307200) AS "last_mentioned",
        CASE
            WHEN U.ZUSERTYPE IS NULL THEN 'N/A'
            WHEN U.ZUSERTYPE = '' THEN 'N/D'
            WHEN U.ZUSERTYPE = 'brand' Then 'Brand'
            WHEN U.ZUSERTYPE = 'celebrity' Then 'Celebrity'
            WHEN U.ZUSERTYPE = 'venuePage' Then 'Venue Page'
            WHEN U.ZUSERTYPE = 'page' Then 'Page'
            WHEN U.ZUSERTYPE = 'chain' Then 'Chain'
            ELSE UPPER(SUBSTR(U.ZUSERTYPE, 1, 1)) || SUBSTR(U.ZUSERTYPE, 2)
        END AS "user_type",
        U.ZRELATIONSHIP,
	    U.ZFIRSTNAME,
	    U.ZLASTNAME,
	    U.ZGENDER,
	    U.ZBIRTHDAY,
	    U.ZPHONE,
	    U.ZEMAIL,
	    U.ZCANONICALURL,
        U.ZPHOTOPREFIX,
        U.ZPHOTOSUFFIX,
        IIF(U.ZBLOCKEDSTATUS = 1 OR U.ZRELATIONSHIP = 'blocked', 'Yes', 
          IIF(U.ZBLOCKEDSTATUS = 0 AND (U.ZRELATIONSHIP != 'blocked' OR U.ZRELATIONSHIP IS NULL), 'No', NULL)
        ) AS "blocked",
        IIF(U.ZMUTED = 1 OR U.ZRELATIONSHIP = 'muted', 'Yes', 
          IIF(U.ZMUTED = 0 AND (U.ZRELATIONSHIP != 'muted' OR U.ZRELATIONSHIP IS NULL), 'No', NULL)
        ) AS "muted",
        IIF(U.ZFRIENDDISABLED = 1, 'Yes', IIF(U.ZFRIENDDISABLED = 0, 'No', NULL)) AS "friend_disabled",
        U.ZCHECKINPINGS,
        coalesce(U.ZFRIENDSCOUNT, 0) AS "friends",
        COALESCE(U.ZCHECKINSCOUNT, 0) AS "checkins",
	    COALESCE(U.ZMAYORSHIPSCOUNT, 0) AS "mayorship",
	    U.ZMONGOID AS "uid"
    FROM ZFSUSER AS "U"
    WHERE (U.ZRELATIONSHIP != 'self') OR (U.ZRELATIONSHIP IS NULL)
    '''

    db_records = get_sqlite_db_records(source_path, query)
    if not db_records:
        return data_headers, (data_list, data_list_html), source_path

    for record in db_records:
        try:
            # Unpack record for clarity
            (user_pk, raw_mentioned, user_type, relationship, first_name, last_name,
             gender, raw_bday, phone_number, email, p_url, pp_prefix, pp_suffix,
             blocked, muted, friendship_disabled, checkin_pings_setting, friends,
             checkins, mayorships, uid) = record

            # Convert timestamps to UTC
            mentioned = convert_unix_ts_to_utc(raw_mentioned)

            # Birthday as string
            bday = get_birthdate(raw_bday) if raw_bday is not None else ''

            # Profile Picture URL
            pp_url =f"{pp_prefix}original{pp_suffix}" if pp_prefix and pp_suffix else ''

            # This handles exact suffix matches and resolution fallbacks automatically
            media = resolve_media_reference(pp_suffix, photo_map, context)
            media_ref_id = media['media_ref_id']
            media_device_path = media['device_path']

            # Precise location within the source database table for validation
            location = f"ZFSUSER (Z_PK: {user_pk})"

            # Base row for both lists
            base_data = (
                mentioned,
                user_type,
                _normalize_relationship(relationship),
                media_ref_id,
                first_name, last_name,
                gender, bday, phone_number, email,
                format_url(pp_url),                                 # 10 Profile Picture URL (Plain)
                blocked, muted, friendship_disabled,
                checkin_pings_setting, friends,
                checkins, mayorships,
                foursquare_uid_url(uid, p_url),                     # 18 Swarm Profile URL (Plain)
                media_device_path, location
            )

            # HTML row
            data_list_html.append((
                *base_data[:10],
                format_url(pp_url, html_format=True),               # Replaces index 10
                *base_data[11:18],
                foursquare_uid_url(uid, p_url, html_format=True),   # Replaces index 18
                *base_data[19:]
            ))

            # LAVA row
            data_list.append(base_data)

        except (ValueError, IndexError, TypeError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Failed parsing record ZFSUSER {record[0]} in {source_path}: {ex}")
            continue

    return data_headers, (data_list, data_list_html), source_path


# iOS built-in label constants mapped to display names
_IOS_PHONE_LABEL_MAP = {
    '_$!<Mobile>!$_':  'Mobile',
    '_$!<iPhone>!$_':  'iPhone',
    '_$!<Home>!$_':    'Home',
    '_$!<Work>!$_':    'Work',
    '_$!<Main>!$_':    'Main',
    '_$!<HomeFax>!$_': 'Home Fax',
    '_$!<WorkFax>!$_': 'Work Fax',
    '_$!<Pager>!$_':   'Pager',
    '_$!<Other>!$_':   'Other',
}


def _decode_phone_entries(numbers_blob: bytes | None, labels_blob: bytes | None) -> tuple[str, str]:
    """
    Decodes phone numbers and labels from plist BLOBs.
    """

    # Internal helper for safe data extraction from plists
    def _get_list(blob: bytes | None) -> list[str]:
        if not blob:
            return []

        res = get_plist_content(bytes(blob))
        if not isinstance(res, list):
            return []

        return [
            item for item in res
            if isinstance(item, str) and item not in ('$null', '')
        ]

    numbers = _get_list(numbers_blob)
    labels = [
        _IOS_PHONE_LABEL_MAP.get(l, l)
        for l in _get_list(labels_blob)
    ]

    plain_items = []
    html_items = []

    for i, number in enumerate(numbers):
        number = number.strip()

        # Label handling (if available)
        label = labels[i].strip() if i < len(labels) else ''

        # Prepare items for Plain text version
        plain_text = f"{label}: {number}" if label else number
        plain_items.append(plain_text)

        # Prepare items for HTML version
        safe_label = html.escape(label)
        safe_number = html.escape(number)
        html_content = (
            f"<b>{safe_label}:</b> {safe_number}"
            if safe_label else safe_number
        )
        html_items.append(html_content)

    # Join items (Plain uses LIST_SEP, HTML uses <br>)
    plain_output = LIST_SEP.join(plain_items) if plain_items else ""
    html_output = HTML_LINE_BREAK.join(html_items) if html_items else ""

    return plain_output, html_output


@artifact_processor
def foursquare_swarm_address_book(context):
    """
    Extracts device address book contacts that Foursquare Swarm has accessed,
    including phone numbers with labels, email, Facebook ID.
    """

    data_headers = (
        ('Last Mentioned', 'datetime'),
        ('Profile Picture', 'media', 'height: 48px; border-radius: 5%;'),
        'First Name',
        'Last Name',
        'Phone Numbers',
        'Email',
        'Facebook Profile',
        'UID',
        'Location'
    )

    data_list = []
    data_list_html = []

    source_path = context.get_source_file_path('foursquare.sqlite')
    if not source_path:
        return data_headers, (data_list, data_list_html), source_path

    # Updated query to include phone numbers and labels BLOBs
    query = '''
    SELECT
        AB.Z_PK,
        (AB.ZLASTMENTIONED + 978307200) AS "last_mentioned",
        AB.ZFIRSTNAME,
        AB.ZLASTNAME,
        AB.ZEMAILADDRESS,
        AB.ZFACEBOOKID,
        AB.ZMONGOID AS "uid",
        AB.ZPHONENUMBERS,
        AB.ZPHONENUMBERLABELS,
        AB.ZIMAGE
    FROM ZFSADDRESSBOOKUSER AS "AB"
    ORDER BY AB.ZLASTNAME ASC, AB.ZFIRSTNAME ASC
    '''

    db_records = get_sqlite_db_records(source_path, query)
    if not db_records:
        return data_headers, (data_list, data_list_html), source_path

    for record in db_records:
        try:
            # Unpack record
            (ab_pk, raw_last_mentioned, first_name, last_name, email,
             facebook_id, uid, numbers_blob, labels_blob, image_blob) = record

            # Convert timestamp
            last_mentioned = convert_unix_ts_to_utc(raw_last_mentioned)

            # Decode multiple phone numbers using the custom utility
            # e.g., "Label: Number, Label: Number"
            phone_plain, phone_html = _decode_phone_entries(numbers_blob, labels_blob)

            # Profile Picture (embedded)
            pp_ref_id = None
            if image_blob:
                pp_ref_id = check_in_embedded_media('foursquare.sqlite',
                                                    image_blob, 'embedded_file')

            # Precise location within the source database table for validation
            location = f"ZFSADDRESSBOOKUSER (Z_PK: {ab_pk})"

            # Base row (Plain)
            base_data = (
                last_mentioned,
                pp_ref_id,
                first_name, last_name,
                phone_plain,                                        # 4 List of phones
                email,
                facebook_url(facebook_id),                          # 6 Facebook URL (Plain)
                uid,
                location
            )

            # HTML row
            data_list_html.append((
                *base_data[:4],
                phone_html,                                         # Replaces index 4
                base_data[5],
                facebook_url(facebook_id, html_format=True),        # Replaces index 6
                *base_data[7:]
            ))

            # LAVA row
            data_list.append(base_data)

        except (ValueError, IndexError, TypeError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Failed parsing record ZFSADDRESSBOOKUSER "
                    f"{record[0]} in {source_path}: {ex}")
            continue

    return data_headers, (data_list, data_list_html), source_path


def _normalize_visibility(value) -> str:
    """
    Normalize Swarm check-in visibility values.
    """

    # Default to 'Public' if the value is missing or null
    if value in (None, '', 'null', 'None'):
        return 'Public'

    # Clean the input string
    value_str = str(value).strip().lower()

    # Map raw database values to human-readable labels
    visibility_map = {
        'public': 'Public',
        'everyone': 'Public',
        'private': 'Private',
        'friends': 'Friends',
        'closefriends': 'Close Friends',
        'trusted_friends': 'Trusted Friends',
        'trustedfriends': 'Trusted Friends',
        'me': 'Private (Self Only)',
        'privateonly': 'Private Only',
        'trusted': 'Trusted',
        'offthegrid': 'Off The Grid'
    }

    # Retrieve the mapped label
    normalized = visibility_map.get(value_str)

    # If the value is not in the map, log it as a warning so you can investigate
    if not normalized:
        logfunc(f"Warning - New or unexpected visibility value encountered: '{value_str}'")
        return value_str.capitalize()

    return normalized


def _decode_zentities(blob: bytes | None) -> tuple[str, str]:
    """
    Decodes ZENTITIES BLOB. Supports both NSKeyedArchiver Plists 
    and standard JSON strings.

    Output:
        Plain: key: value, key: value
        HTML : <b>key:</b> value, <b>key:</b> value
    """

    if not blob:
        return '', ''

    # Check magic bytes before full plist parsing
    if blob.startswith(b'bplist'):
        decoded_data = get_plist_content(bytes(blob))
    else:
        decoded_data = None

    # JSON fallback
    if not isinstance(decoded_data, (list, dict)):
        for encoding in ('utf-8', 'utf-16'):
            try:
                decoded_str = blob.decode(encoding, errors='ignore').strip()
                if decoded_str:
                    decoded_data = json.loads(decoded_str)
                    break

            except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
                continue


    # Final check: if we still don't have a collection, return the raw representation
    if not isinstance(decoded_data, (list, dict)):
        return str(blob), html.escape(str(blob))

    entities = ([decoded_data]if isinstance(decoded_data, dict) else decoded_data)
    if not isinstance(entities, list):
        return '', ''

    plain_entries = []
    html_entries = []

    for entity in entities:
        if not isinstance(entity, dict):
            continue

        plain_pairs = []
        html_pairs = []

        for key in sorted(entity.keys()):
            if key in ('range.location', 'range.length'):
                continue

            value = entity.get(key)
            if value in (None, '', '$null'):
                continue
            safe_key = str(key)

            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if sub_value in (None, '', '$null'):
                        continue

                    full_key = f"{safe_key}.{sub_key}"
                    plain_pairs.append(f"{full_key}: {sub_value}")
                    html_pairs.append(
                        f"<b>{html.escape(full_key)}:</b> {html.escape(str(sub_value))}"
                    )

            elif isinstance(value, list):
                clean_values = [
                    str(v) for v in value if v not in (None, '', '$null')
                ]
                if clean_values:
                    joined = ", ".join(clean_values)
                    plain_pairs.append(f"{safe_key}: {joined}")
                    html_pairs.append(
                        f"<b>{html.escape(safe_key)}:</b> {html.escape(joined)}"
                    )

            else:
                value_str = str(value)
                plain_pairs.append(f"{safe_key}: {value_str}")
                html_pairs.append(
                    f"<b>{html.escape(safe_key)}:</b> {html.escape(value_str)}"
                )

        # Join pairs (Plain uses LIST_SEP, HTML uses <br>)
        if plain_pairs:
            plain_entries.append(LIST_SEP.join(plain_pairs))
            html_entries.append(HTML_LINE_BREAK.join(html_pairs))

    # Join entities (Plain uses LIST_SEP, HTML uses <br>)
    plain_output = f"{LIST_SEP}{LIST_SEP}".join(plain_entries) if plain_entries else ""
    html_output = HTML_HORZ_RULE.join(html_entries) if html_entries else ""

    return plain_output, html_output


@artifact_processor
def foursquare_swarm_checkins(context):
    """
    Extracts Swarm check-in history from ZFSCHECKIN, covering both manual
    check-ins and passive background detections, including timestamps,
    visibility, venue details, device GPS coordinates, shout entities,
    and associated social media profiles.
    """

    data_headers = (
        ('Created', 'datetime'),
        'Edited',
        'Check-in Type',
        'Check-in Status',
        'Check-in Retries',
        'In Activity Feed',
        'With Friends',
        'TZ Offset (minutes)',
        'Relationship',
        'Full Name',
        'Visibility',
        'Venue Name',
        'Distance (meters)',
        'Latitude',
        'Longitude',
        'Address',
        'Neighborhood',
        'Country',
        'State',
        'City',
        'Cross Street',
        'Postal Code',
        ('Phone Number', 'phonenumber'),
        'Facebook Profile',
        'Twitter Profile',
        'Instagram Profile',
        'Venue URL',
        'Check-in URL',
        'Website',
        'Liked',
        'Mayor',
        'Comment',
        'Entities',
        'Passive Latitude',
        'Passive Longitude',
        'Passive Location Name',
        'Contextual Location',
        'Exact Context',
        'Display Geo',
        'Passive Stop ID',
        'Nearby Venues',
        'Source App',
        'UID',
        'Location'
    )

    data_list = []
    data_list_html = []

    source_path = context.get_source_file_path('foursquare.sqlite')
    if not source_path:
        return data_headers, (data_list, data_list_html), source_path

    db = open_sqlite_db_readonly(source_path)
    if not db:
        return data_headers, (data_list, data_list_html), source_path

    try:
        cursor = db.cursor()

        # Resolve the 'WITHFRIENDS' relationship for the 'FSCheckin' entity
        relation = _resolve_coredata_relationship(context, db, 'FSCheckin',
                                                  'WITHFRIENDS', 'WITHFRIENDSINVERSE')

        subquery_friends = "'' AS with_friends"

        # If Core Data mapped the table successfully, inject the dynamic columns
        if (relation['table']
                and relation['inverse_col']
                and relation['target_col']):
            subquery_friends = f'''
            (
                SELECT GROUP_CONCAT(
                    TRIM(IFNULL(UW.ZFIRSTNAME, '') || ' ' || IFNULL(UW.ZLASTNAME, '')),
                    {SQL_LIST_SEP}
                )
                FROM {relation['table']} AS "WF"
                JOIN ZFSUSER AS "UW" ON (WF.{relation['target_col']} = UW.Z_PK)
                WHERE WF.{relation['inverse_col']} = CI.Z_PK
            ) AS "with_friends"
            '''

        # Resolve the 'NEARBYVENUES' relationship for the 'FSCheckin' entity
        relation_nearby = _resolve_coredata_relationship(context, db, 'FSCheckin',
                                                         'NEARBYVENUES', 'NEARBYCHECKIN')

        subquery_nearby = "'' AS nearby_venues"
        if (relation_nearby['table']
                and relation_nearby['inverse_col']
                and relation_nearby['target_col']):
            subquery_nearby = f'''
            (
                SELECT GROUP_CONCAT(V2.ZNAME, {SQL_LIST_SEP})
                FROM {relation_nearby['table']} AS "NV"
                JOIN ZFSVENUE AS "V2" ON (NV.{relation_nearby['target_col']} = V2.Z_PK)
                WHERE NV.{relation_nearby['inverse_col']} = CI.Z_PK
            ) AS "nearby_venues"
            '''

        # Swarm 6.x: ZDISPLAYGEO
        if does_column_exist_in_db(source_path, 'ZFSCHECKIN', 'ZDISPLAYGEO'):
            has_g_pk = "G.Z_PK"
            has_display_geo = "G.ZDISPLAYNAME"
            join_display_geo = "LEFT JOIN ZFSROBINDISPLAYGEO AS \"G\" ON (CI.ZDISPLAYGEO = G.Z_PK)"
        else:
            has_g_pk = "NULL"
            has_display_geo = "NULL"
            join_display_geo = ""

        query = f'''
        SELECT 
            CI.Z_PK AS "CI_PK",
            V.Z_PK AS "V_PK",
            U.Z_PK AS "U_PK",
            {has_g_pk} AS "G_PK",
            (CI.ZCREATEDAT + 978307200) AS "created",
            IIF(CI.ZEDITED = 1, 'Yes', IIF(CI.ZEDITED = 0, 'No', NULL)) AS "is_edited",
            CASE
                WHEN CI.ZISAUTOMATIC IS NULL AND CI.ZPASSIVESTOPID IS NULL AND CI.ZCHECKINTYPE IS NULL THEN 'N/A'
                WHEN CI.ZISAUTOMATIC = '' AND CI.ZPASSIVESTOPID = '' AND CI.ZCHECKINTYPE = '' THEN 'N/D'
                WHEN CI.ZISAUTOMATIC = 1 THEN 'Automatic'
                WHEN CI.ZPASSIVESTOPID IS NOT NULL THEN 'Passive'
                WHEN LOWER(CI.ZCHECKINTYPE) = 'passive' THEN 'Passive'
                ELSE 'Manual'
            END AS "checkin_type",
            CASE
                WHEN CI.ZCHECKINSTATUS IS NULL THEN 'N/A'
                WHEN CI.ZCHECKINSTATUS = '' THEN 'N/D'
                WHEN CI.ZCHECKINSTATUS = 0 THEN 'Draft/Failed'
                WHEN CI.ZCHECKINSTATUS = 1 THEN 'Sent/Synchronizing'
                WHEN CI.ZCHECKINSTATUS = 2 THEN 'Confirmed/Published'
                WHEN CI.ZCHECKINSTATUS = 3 THEN 'Deleted (Local)'
                ELSE 'Unknown (' || CI.ZCHECKINSTATUS || ')'
            END AS "checkin_status",
            CI.ZCHECKINRETRIES,
            IIF(EXISTS (
                SELECT 1 FROM ZFSSIMPLEFEEDITEM
                WHERE ZCHECKIN = CI.Z_PK
            ), 'Yes', 'No') AS "in_activity_feed",
            {subquery_friends},
            CI.ZTIMEZONEOFFSET AS "tzoffset_min",
            U.ZRELATIONSHIP,
            TRIM(IFNULL(U.ZFIRSTNAME, '') || ' ' || IFNULL(U.ZLASTNAME, '')) AS "full_name",
            COALESCE(CI.ZVISIBILITY, IIF(CI.ZPRIVATE = 1, 'private', 'public')) AS "visibility",
            V.ZNAME AS "venue_name",
            V.ZDISTANCE,
            V.ZGEOLAT AS "venue_lat",
            V.ZGEOLONG AS "venue_lon",
            V.ZADDRESS,
            V.ZNEIGHBORHOOD,
            V.ZCOUNTRY,
            V.ZSTATE,
            V.ZCITY,
            V.ZCROSSSTREET,
            V.ZPOSTALCODE,
            V.ZPHONE,
            V.ZFACEBOOKID,
            V.ZTWITTER,
            V.ZINSTAGRAM,
            V.ZCANONICALURL AS "venue_url",
            CI.ZCHECKINSHORTURL AS "checkin_url",
            V.ZURL AS "website",
            IIF(CI.ZLIKE = 1, 'Yes', IIF(CI.ZLIKE = 0, 'No', NULL)) AS "liked",
            IIF(CI.ZISMAYOR = 1, 'Yes', IIF(CI.ZISMAYOR = 0, 'No', NULL)) AS "is_mayor",
            CI.ZSHOUT,
            CI.ZENTITIES,
            CI.ZVENUELESSLAT AS "passive_lat",
            CI.ZVENUELESSLNG AS "passive_lng",
            CI.ZVENUELESSLOCATIONNAME AS "passive_location_name",
            CI.ZCONTEXTUALLOCATIONNAME AS "contextual_location",
            CI.ZEXACTCONTEXTLINE AS "exact_context",
            {has_display_geo} AS "display_geo",
            CI.ZPASSIVESTOPID AS "passive_stop_id",
            {subquery_nearby},
            CI.ZSOURCENAME AS "source_app",
            CI.ZMONGOID AS "uid"
        FROM ZFSCHECKIN AS "CI"
        LEFT JOIN ZFSVENUE AS "V" ON (CI.ZVENUE = V.Z_PK)
        LEFT JOIN ZFSUSER AS "U" ON (CI.ZUSER = U.Z_PK)
        {join_display_geo}
        ORDER BY CI.ZCREATEDAT DESC
        '''

        cursor.execute(query)
        for record in cursor:
            try:
                # Unpack record for clarity
                (ci_pk, v_pk, u_pk, g_pk, raw_created, is_edited, checkin_type,
                 checkin_status, checkin_retries, in_activity_feed, with_friends,
                 tz_offset, relationship, full_name, visibility, venue_name, distance,
                 lat, lon, address, neighborhood, country, state, city, cross_street,
                 postal_code, phone_number, facebook_id, twitter_id, instagram_id,
                 v_url, ci_url, website, liked, is_mayor, shout, entities_blob,
                 passive_lat, passive_lng, passive_location_name, contextual_location,
                 exact_context, display_geo, passive_stop_id, nearby_venues,
                 source_app, uid) = record

                # Convert timestamps to UTC
                created = convert_unix_ts_to_utc(raw_created)

                # Decode ZENTITIES plist
                p_entities, h_entities = _decode_zentities(entities_blob)

                # Precise location within the source database table for validation
                location = [ f"ZFSCHECKIN (Z_PK: {ci_pk})" ]
                if v_pk is not None:
                    location.append(f"ZFSVENUE (Z_PK: {v_pk})")
                if u_pk is not None:
                    location.append(f"ZFSUSER (Z_PK: {u_pk})")
                if g_pk is not None:
                    location.append(f"ZFSROBINDISPLAYGEO (Z_PK: {g_pk})")
                location = COMMA_SEP.join(location)

                # Base row for both lists
                base_data = (
                    created, is_edited, checkin_type,
                    checkin_status, checkin_retries,
                    in_activity_feed, with_friends, tz_offset,
                    _normalize_relationship(relationship),
                    full_name,
                    _normalize_visibility(visibility),
                    venue_name, distance, lat, lon, address,
                    neighborhood, country, state, city, cross_street,
                    postal_code, phone_number,
                    facebook_url(facebook_id),                          # 23 Facebook URL (Plain)
                    twitter_url(twitter_id),                            # 24 Twitter URL (Plain)
                    instagram_url(instagram_id),                        # 25 Instagram URL (Plain)
                    format_url(v_url),                                  # 26 Venue URL (Plain)
                    format_url(ci_url),                                 # 27 Check-in URL (Plain)
                    format_url(website),                                # 28 Website (Plain)
                    liked, is_mayor, shout,
                    p_entities,                                         # 32 Entities (Plain)
                    passive_lat, passive_lng,
                    passive_location_name,
                    contextual_location, exact_context,
                    display_geo, passive_stop_id, nearby_venues,
                    source_app, uid,
                    location
                )

                # HTML row
                data_list_html.append((
                    *base_data[:23],
                    facebook_url(facebook_id, html_format=True),        # Replaces index 23
                    twitter_url(twitter_id, html_format=True),          # Replaces index 24
                    instagram_url(instagram_id, html_format=True),      # Replaces index 25
                    format_url(v_url, html_format=True),                # Replaces index 26
                    format_url(ci_url, html_format=True),               # Replaces index 27
                    format_url(website, html_format=True),              # Replaces index 28
                    *base_data[29:32],
                    h_entities,                                         # Replaces index 32
                    *base_data[33:]
                ))

                # LAVA row
                data_list.append(base_data)

            except (ValueError, IndexError, TypeError) as ex:
                logfunc(f"[{context.get_artifact_name()}] "
                        f"Error - Failed parsing record ZFSCHECKIN {record[0]} "
                        f"in {source_path}: {ex}")
                continue

    except sqlite3.Error as db_ex:
        # Log fatal database errors (e.g., malformed DB or missing tables)
        logfunc(f"[{context.get_artifact_name()}] "
                f"Error - executing query on {source_path}: {db_ex}")
    finally:
        # Ensure the database connection is closed safely
        db.close()

    return data_headers, (data_list, data_list_html), source_path


@artifact_processor
def foursquare_swarm_tips(context):
    """
    Extracts user-generated tips and reviews for venues from the ZFSTIP table,
    including creation and modification timestamps.
    """

    data_headers = (
        ('Created', 'datetime'),
        ('Modified', 'datetime'),
        ('Photo', 'media', 'height: 48px; border-radius: 5%;'),
        'Author Type',
        'Relationship',
        'Full Name',
        'Tip',
        'Title',
        'Agrees',
        'Disagrees',
        'Likes',
        'Saves',
        'Comments',
        'Views',
        'Dones',
        'Venue Name',
        'Distance (meters)',
        'Latitude',
        'Longitude',
        'Tip URL',
        'Short URL',
        'Photo URL',
        'UID',
        'Photo Path (Cached)',
        'Location'
    )

    data_list = []
    data_list_html = []

    source_path = context.get_source_file_path('foursquare.sqlite')
    if not source_path:
        return data_headers, (data_list, data_list_html), source_path

    # This maps all files in the cache by their suffix
    photo_map = _build_photo_map(context)

    query = '''
    SELECT 
        T.Z_PK AS "T_PK",
        V.Z_PK AS "V_PK",
        U.Z_PK AS "U_PK",
        P.Z_PK AS "P_PK",
        (T.ZCREATEDAT + 978307200) AS "created",
        T.ZCACHEMODIFIEDAT AS "modified",
        CASE
            WHEN T.ZTYPE IS NULL THEN 'N/A'
            WHEN T.ZTYPE = '' THEN 'N/D'
            WHEN T.ZTYPE = 'user' THEN 'User'
            WHEN T.ZTYPE = 'mayor' THEN 'Mayor'
            WHEN T.ZTYPE = 'foursquare' THEN 'Foursquare'
            WHEN T.ZTYPE = 'brand' THEN 'Brand'
            WHEN T.ZTYPE = 'expert' THEN 'Expert'
            ELSE UPPER(SUBSTR(T.ZTYPE, 1, 1)) || SUBSTR(T.ZTYPE, 2)
        END AS "author_type",
    	U.ZRELATIONSHIP,
        TRIM(IFNULL(U.ZFIRSTNAME, '') || ' ' || IFNULL(U.ZLASTNAME, '')) AS "full_name",
	    T.ZTEXT AS "tip",
        T.ZTITLE,
		T.ZAGREECOUNT,
        T.ZDISAGREECOUNT,
        T.ZLIKESCOUNT,
        T.ZSAVERSCOUNT,
        T.ZCOMMENTSCOUNT,
        T.ZVIEWCOUNT,
        T.ZDONESCOUNT,
        V.ZNAME AS "venue_name",
        V.ZDISTANCE,
	    V.ZGEOLAT,
	    V.ZGEOLONG,
	    T.ZCANONICALURL AS "tip_url",
        T.ZSHORTURL,
        P.ZPREFIX,
        P.ZSUFFIX,
        T.ZMONGOID AS "uid"	
    FROM ZFSTIP AS "T"
    LEFT JOIN ZFSUSER AS "U" ON (T.ZUSER = U.Z_PK)
    LEFT JOIN ZFSVENUE AS "V" ON (T.ZVENUE = V.Z_PK)
    LEFT JOIN ZFSPHOTO AS "P" ON (T.ZPHOTO = P.Z_PK)
    ORDER BY T.ZCREATEDAT DESC
    '''

    db_records = get_sqlite_db_records(source_path, query)
    if not db_records:
        return data_headers, (data_list, data_list_html), source_path

    for record in db_records:
        try:
            # Unpack record for clarity
            (t_pk, v_pk, u_pk, p_pk, raw_created, raw_modified, author_type,
             relationship, full_name, tip, title, agrees, disagrees, likes,
             saves, comments, views, dones, venue_name, distance, lat, lon,
             tip_url, short_url, p_prefix, p_suffix, uid) = record

            # Convert timestamps to UTC
            created = convert_unix_ts_to_utc(raw_created)
            modified = convert_unix_ts_to_utc(raw_modified)

            # Photo
            p_url =f"{p_prefix}original{p_suffix}" if p_prefix and p_suffix else ''

            # This handles exact suffix matches and resolution fallbacks automatically
            media = resolve_media_reference(p_suffix, photo_map, context)
            media_ref_id = media['media_ref_id']
            media_device_path = media['device_path']

            # Precise location within the source database table for validation
            location = [ f"ZFSTIP (Z_PK: {t_pk})" ]
            if v_pk is not None:
                location.append(f"ZFSVENUE (Z_PK: {v_pk})")
            if u_pk is not None:
                location.append(f"ZFSUSER (Z_PK: {u_pk})")
            if p_pk is not None:
                location.append(f"ZFSPHOTO (Z_PK: {p_pk})")
            location = COMMA_SEP.join(location)

            # Base row for both lists
            base_data = (
                created, modified, media_ref_id, author_type,
                _normalize_relationship(relationship),
                full_name, tip, title, agrees, disagrees, likes,
                saves, comments, views, dones, venue_name,
                distance, lat, lon,
                format_url(tip_url),                                # 19 Tip URL (Plain)
                format_url(short_url),                              # 20 Short URL (Plain)
                format_url(p_url),                                  # 21 Photo URL (Plain)
                uid, media_device_path, location
            )

            if any(x is not None and x != '' for x in base_data[:-1]):
                # HTML row
                data_list_html.append((
                    *base_data[:19],
                    format_url(tip_url, html_format=True),          # Replaces index 19
                    format_url(short_url, html_format=True),        # Replaces index 20
                    format_url(p_url, html_format=True),            # Replaces index 21
                    *base_data[22:]
                ))

                # LAVA row
                data_list.append(base_data)

        except (ValueError, IndexError, TypeError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Failed parsing record ZFSTIP {record[0]} in {source_path}: {ex}")
            continue

    return data_headers, (data_list, data_list_html), source_path


@artifact_processor
def foursquare_swarm_stickers(context):
    """
    Extracts Swarm stickers, including titles, unlock status, bonus text, and image URL.
    """

    data_headers = (
        'Sticker Name',
        'Category',
        ('Sticker', 'media', 'height: 48px; border-radius: 5%;'),
        'Unlocked',
        'Bonus Type',
        'Status',
        'Multiplier',
        'Check-ins Earned',
        'Check-ins Required',
        'Progress (%)',
        'Sticker URL',
        'UID',
        'Sticker Path (Cached)',
        'Location'
    )

    data_list = []
    data_list_html = []

    source_path = context.get_source_file_path('foursquare.sqlite')
    if not source_path:
        return data_headers, (data_list, data_list_html), source_path

    # This maps all files in the cache by their suffix
    photo_map = _build_photo_map(context)

    query = '''
    SELECT
        S.Z_PK AS "S_PK",
	    SB.Z_PK AS "SB_PK",
	    S.ZNAME,
        S.ZCATEGORYNAME,
        IIF(S.ZUNLOCKED = 1, 'Yes', IIF(S.ZUNLOCKED = 0, 'No', NULL)) AS "unlocked",
        SB.ZBONUSTYPE,
        SB.ZSTATUS,
        SB.ZVALUE AS "multiplier",
        SB.ZPROGRESSCHECKINSEARNED AS "earned",
        SB.ZPROGRESSCHECKINSREQUIRED AS "required",
        SB.ZPROGRESSPERCENTCOMPLETE AS "percent",
        S.ZIMAGEPREFIX,
        S.ZIMAGENAME,
        COALESCE(SB.ZMONGOID, S.ZMONGOID) AS "uid"
    FROM ZFSSTICKER AS "S"
    LEFT JOIN ZFSSTICKERBONUS AS "SB" ON (S.Z_PK = SB.ZBONUSESINVERSE)
    '''

    db_records = get_sqlite_db_records(source_path, query)
    if not db_records:
        return data_headers, (data_list, data_list_html), source_path

    for record in db_records:
        try:
            # Unpack record for clarity
            (s_pk, sb_pk, title, category, unlocked, bonus_type, bonus_status,
             multiplier, earned, required, percent, s_prefix, s_suffix, uid) = record

            # Sticker
            s_url =f"{s_prefix}original{s_suffix}" if s_prefix and s_suffix else ''

            # This handles exact suffix matches and resolution fallbacks automatically
            media = resolve_media_reference(s_suffix, photo_map, context)
            media_ref_id = media['media_ref_id']
            media_device_path = media['device_path']

            # Precise location within the source database table for validation
            location = [ f"ZFSSTICKER (Z_PK: {s_pk})" ]
            if sb_pk is not None:
                location.append(f"ZFSSTICKERBONUS (Z_PK: {sb_pk})")
            location = COMMA_SEP.join(location)

            # Base row for both lists
            base_data = (
                title, category,
                media_ref_id,
                unlocked, bonus_type, bonus_status,
                multiplier, earned, required, percent,
                format_url(s_url),                                  # 10 Sticker URL (Plain)
                uid, media_device_path, location
            )

            # HTML row
            data_list_html.append((
                *base_data[:10],
                format_url(s_url, html_format=True),                # Replaces index 10
                *base_data[11:]
            ))

            # LAVA row
            data_list.append(base_data)

        except (ValueError, IndexError, TypeError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Failed parsing record ZFSSTICKER {record[0]} in {source_path}: {ex}")
            continue

    return data_headers, (data_list, data_list_html), source_path


@artifact_processor
def foursquare_swarm_venues_history(context):
    """
    Extracts a history of visited venues with detailed metadata including
    contact info, coordinates, statistics, and mayoralty status.
    """

    data_headers = (
        ('Last Visited', 'datetime'),
        'Category',
        'Venue Name',
        'Distance (meters)',
        'Latitude',
        'Longitude',
        'Address',
        'Neighborhood',
        'Country',
        'State',
        'City',
        'Cross Street',
        'Postal Code',
        ('Phone Number', 'phonenumber'),
        'Facebook Profile',
        'Twitter Profile',
        'Instagram Profile',
        'Foursquare Profile',
        'Website',
        'Description',
        'Liked',
        'Disliked',
        'Closed',
        'Saved',
        'Been Here Count',
        'Rating',
        'Mayor',
        'Mayor Count',
        'Mayor Info',
        'Friends Visits Info',
        'Event Info',
        'Reason Info',
        'Likes Count',
        'Visitors Count',
        'Check-ins Count',
        'Photo Count',
        'Tips Count',
        'Events Count', 
        'Location'
    )

    data_list = []
    data_list_html = []

    source_path = context.get_source_file_path('foursquare.sqlite')
    if not source_path:
        return data_headers, (data_list, data_list_html), source_path

    query = '''
    SELECT
	    V.Z_PK AS "V_PK",
	    C.Z_PK AS "C_PK",
	    U.Z_PK AS "U_PK",
        (V.ZLASTVISITEDAT + 978307200) AS "last_visited",
	    C.ZNAME AS "category_name",
	    V.ZNAME AS "venue_name",
	    V.ZDISTANCE,
	    V.ZGEOLAT,
	    V.ZGEOLONG,
	    V.ZADDRESS,
	    V.ZNEIGHBORHOOD,
	    V.ZCOUNTRY,
	    V.ZSTATE,
	    V.ZCITY,
	    V.ZCROSSSTREET,
	    V.ZPOSTALCODE,
	    V.ZPHONE,
	    V.ZFACEBOOKID,
	    V.ZTWITTER,
	    V.ZINSTAGRAM,
	    V.ZCANONICALURL AS "foursquare_url",
	    V.ZURL AS "website",	
	    V.ZDESCRIPTIONTEXT,
        IIF(V.ZLIKE = 1, 'Yes', IIF(V.ZLIKE = 0, 'No', NULL)) AS "liked",
        IIF(V.ZDISLIKE = 1, 'Yes', IIF(V.ZDISLIKE = 0, 'No', NULL)) AS "disliked",
        IIF(V.ZCLOSED = 1, 'Yes', IIF(V.ZCLOSED = 0, 'No', NULL)) AS "closed",
        IIF(V.ZSAVED = 1, 'Yes', IIF(V.ZSAVED = 0, 'No', NULL)) AS "saved",
        V.ZBEENHERECOUNT AS "been_here_count",
        V.ZRATING AS "rating",
	    U.ZMONGOID AS "mayor_uid",
        V.ZMAYORCOUNT AS "mayor_count",
        TRIM(IFNULL(U.ZFIRSTNAME, '') || ' ' || IFNULL(U.ZLASTNAME, '')) AS "full_name",
	    V.ZMAYORSUMMARY,
	    V.ZFRIENDVISITSSUMMARY,
        V.ZEVENTSSUMMARY,
	    V.ZREASONSUMMARY,
	    V.ZLIKESCOUNT,
	    V.ZUSERSCOUNT AS "visitors_count",
	    V.ZCHECKINSCOUNT,
	    V.ZPHOTOSCOUNT,
	    V.ZTIPSCOUNT,
	    V.ZEVENTSCOUNT
    FROM ZFSVENUE AS "V"
    LEFT JOIN ZFSCATEGORY AS "C" ON (V.ZPRIMARYCATEGORY = C.Z_PK)
    LEFT JOIN ZFSUSER AS "U" ON (V.ZMAYOR = U.Z_PK)
    ORDER BY V.ZLASTVISITEDAT DESC
    '''

    db_records = get_sqlite_db_records(source_path, query)
    if not db_records:
        return data_headers, (data_list, data_list_html), source_path

    for record in db_records:
        try:
            # Unpack record for clarity
            (v_pk, c_pk, u_pk, raw_last_visited, categ_name, venue_name,
             distance, lat, lon, address, neighborhood, country, state,
             city, cross_street, postal_code, phone_number, facebook_id,
             twitter_id, instagram_id, foursquare_id, website, description,
             liked, disliked, closed, saved,  been_here_count, rating,
             mayor_uid, mayor_count, mayor_name, mayor_summary, fvisits_sum,
             event_sum, reason_sum, likes_cnt, fvisits_cnt, checkins_cnt,
             photo_cnt, tips_cnt, events_cnt) = record

            # Convert timestamps to UTC
            last_visited = convert_unix_ts_to_utc(raw_last_visited)

            # mayor
            if mayor_uid is not None:
                mayor = f"{mayor_uid} ({mayor_name})" if mayor_name is not None else mayor_uid
            else:
                mayor = ''

            # Precise location within the source database table for validation
            location = [ f"ZFSVENUE (Z_PK: {v_pk})" ]
            if c_pk is not None:
                location.append(f"ZFSCATEGORY (Z_PK: {c_pk})")
            if u_pk is not None:
                location.append(f"ZFSUSER (Z_PK: {u_pk})")
            location = COMMA_SEP.join(location)

            # Base row for both lists
            base_data = (
                last_visited, categ_name, venue_name, distance,
                lat, lon, address, neighborhood, country, state,
                city, cross_street, postal_code, phone_number,
                facebook_url(facebook_id),                          # 14 Facebook URL (Plain)
                twitter_url(twitter_id),                            # 15 Twitter URL (Plain)
                instagram_url(instagram_id),                        # 16 Instagram URL (Plain)
                format_url(foursquare_id),                          # 17 Swarm URL (Plain)
                format_url(website),                                # 18 website (Plain)
                description, liked, disliked, closed, saved,
                been_here_count, rating, mayor,
                mayor_count, mayor_summary, fvisits_sum,
                event_sum, reason_sum, likes_cnt, fvisits_cnt,
                checkins_cnt, photo_cnt, tips_cnt, events_cnt,
                location
            )

            # HTML row
            data_list_html.append((
                *base_data[:14],
                facebook_url(facebook_id, html_format=True),        # Replaces index 14
                twitter_url(twitter_id, html_format=True),          # Replaces index 15
                instagram_url(instagram_id, html_format=True),      # Replaces index 16
                format_url(foursquare_id, html_format=True),        # Replaces index 17
                format_url(website, html_format=True),              # Replaces index 18
                *base_data[19:]
            ))

            # LAVA row
            data_list.append(base_data)

        except (ValueError, IndexError, TypeError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Failed parsing record ZFSVENUE {record[0]} in {source_path}: {ex}")
            continue

    return data_headers, (data_list, data_list_html), source_path


@artifact_processor
def foursquare_swarm_photos(context):
    """
    Extracts all photos including user details, associated venue metadata,
    and geographic coordinates.
    """

    data_headers = (
        ('Created', 'datetime'),
        'Photo Type',
        ('Photo', 'media', 'height: 96px; border-radius: 5%;'),
        'User ID',
        'Full Name',
        'Venue Source',
        'Venue Name',
        'Distance (meters)',
        'Latitude',
        'Longitude',
        'Address',
        'Neighborhood',
        'Country',
        'State',
        'City',
        'Cross Street',
        'Postal Code',
        ('Phone Number', 'phonenumber'),
        'Facebook Profile',
        'Twitter Profile',
        'Instagram Profile',
        'Foursquare Profile',
        'Website',
        'Description',
        'Pending',
        'Public',
        'Has Sticker',
        'Photo URL',
        'Photo Size',
        'Privacy',
        'App Source',
        'UID',
        'Photo Path (Cached)',
        'Location'
    )

    data_list = []
    data_list_html = []

    source_path = context.get_source_file_path('foursquare.sqlite')
    if not source_path:
        return data_headers, (data_list, data_list_html), source_path

    # This maps all files in the cache by their suffix
    photo_map = _build_photo_map(context)

    query = '''
    SELECT
	    P.Z_PK AS "P_PK",
        CI.Z_PK AS "CI_PK",
        T.Z_PK AS "T_PK",
	    V.Z_PK AS "V_PK",
	    U.Z_PK AS "U_PK",
	    (P.ZCREATEDAT + 978307200) AS "created",
        P.ZPHOTOTYPE,
	    U.ZMONGOID AS "user_id",
        TRIM(IFNULL(U.ZFIRSTNAME, '') || ' ' || IFNULL(U.ZLASTNAME, '')) AS "full_name",
        CASE
            WHEN P.ZVENUE IS NOT NULL AND P.ZVENUE != '' THEN 'Direct'
            WHEN P.ZPREVIEWVENUE IS NOT NULL AND P.ZPREVIEWVENUE != '' THEN 'Preview'
            WHEN CI.ZVENUE IS NOT NULL AND CI.ZVENUE != '' THEN 'Checkin'
            WHEN T.ZVENUE IS NOT NULL AND T.ZVENUE != '' THEN 'Tip'
            WHEN P.ZVENUE IS NULL AND P.ZPREVIEWVENUE IS NULL
              AND CI.ZVENUE IS NULL AND T.ZVENUE IS NULL THEN 'N/A'
            ELSE 'N/D'
        END AS "venue_source",
    	V.ZNAME AS "venue_name",
	    V.ZDISTANCE,
	    V.ZGEOLAT,
	    V.ZGEOLONG,
	    V.ZADDRESS,
	    V.ZNEIGHBORHOOD,
	    V.ZCOUNTRY,
	    V.ZSTATE,
	    V.ZCITY,
	    V.ZCROSSSTREET,
	    V.ZPOSTALCODE,
	    V.ZPHONE,
	    V.ZFACEBOOKID,
        V.ZTWITTER,
	    V.ZINSTAGRAM,
        V.ZCANONICALURL AS "foursquare_url",
	    V.ZURL AS "website",
        V.ZDESCRIPTIONTEXT,
        IIF(P.ZPENDING = 1, 'Yes', IIF(P.ZPENDING = 0, 'No', NULL)) AS "pending",
        IIF(P.ZPUBLIC = 1, 'Yes', IIF(P.ZPUBLIC = 0, 'No', NULL)) AS "public",
        IIF(P.ZHASSTICKER = 1, 'Yes', IIF(P.ZHASSTICKER = 0, 'No', NULL)) AS "has_sticker",
        P.ZPREFIX,
        P.ZSUFFIX,
        (P.ZWIDTH || 'x' || P.ZHEIGHT) AS "photo_size",
        P.ZSWARMPRIVACYSETTING,
        P.ZSOURCENAME,
        P.ZMONGOID
    FROM ZFSPHOTO AS "P"
    LEFT JOIN ZFSCHECKIN AS "CI" ON (P.ZCHECKIN = CI.Z_PK)
    LEFT JOIN ZFSTIP AS "T" ON (P.ZTIP = T.Z_PK)
    LEFT JOIN ZFSVENUE AS "V" ON (V.Z_PK = COALESCE(P.ZVENUE, P.ZPREVIEWVENUE, CI.ZVENUE, T.ZVENUE))
    LEFT JOIN ZFSUSER AS "U" ON (P.ZUSER = U.Z_PK)
    ORDER BY P.ZCREATEDAT DESC
    '''

    db_records = get_sqlite_db_records(source_path, query)
    if not db_records:
        return data_headers, (data_list, data_list_html), source_path

    for record in db_records:
        try:
            # Unpack record for clarity
            (p_pk, ci_pk, t_pk, v_pk, u_pk, raw_created, photo_type, user_id, full_name,
             venue_source, venue_name, distance, lat, lon, address, neighborhood, country,
             state, city, cross_street, postal_code, phone_number, facebook_id, twitter_id,
             instagram_id, foursquare_id, website, description, pending, public, has_sticker,
             ph_prefix, ph_suffix, photo_size, privacy, app_source, p_id) = record

            # Convert timestamps to UTC
            created = convert_unix_ts_to_utc(raw_created)

            # Photo URL
            photo_url =f"{ph_prefix}original{ph_suffix}" if ph_prefix and ph_suffix else ''

            # This handles exact suffix matches and resolution fallbacks automatically
            media = resolve_media_reference(ph_suffix, photo_map, context)
            media_ref_id = media['media_ref_id']
            media_device_path = media['device_path']

            # Precise location within the source database table for validation
            location = [ f"ZFSPHOTO (Z_PK: {p_pk})" ]
            if ci_pk is not None:
                location.append(f"ZFSCHECKIN (Z_PK: {ci_pk})")
            if t_pk is not None:
                location.append(f"ZFSTIP (Z_PK: {t_pk})")
            if v_pk is not None:
                location.append(f"ZFSVENUE (Z_PK: {v_pk})")
            if u_pk is not None:
                location.append(f"ZFSUSER (Z_PK: {u_pk})")
            location = COMMA_SEP.join(location)

            # Base row for both lists
            base_data = (
                created, photo_type, media_ref_id, user_id, full_name,
                venue_source, venue_name, distance, lat, lon, address,
                neighborhood, country, state, city, cross_street,
                postal_code, phone_number,
                facebook_url(facebook_id),                          # 18 Facebook URL (Plain)
                twitter_url(twitter_id),                            # 19 Twitter URL (Plain)
                instagram_url(instagram_id),                        # 20 Instagram URL (Plain)
                format_url(foursquare_id),                          # 21 Swarm URL (Plain)
                format_url(website),                                # 22 Website (Plain)
                description, pending, public, has_sticker,
                format_url(photo_url),                              # 27 Photo URL (Plain)
                photo_size,
                _normalize_visibility(privacy),
                app_source, p_id, media_device_path, location
            )

            # HTML row
            data_list_html.append((
                *base_data[:18],
                facebook_url(facebook_id, html_format=True),        # Replaces index 18
                twitter_url(twitter_id, html_format=True),          # Replaces index 19
                instagram_url(instagram_id, html_format=True),      # Replaces index 20
                format_url(foursquare_id, html_format=True),        # Replaces index 21
                format_url(website, html_format=True),              # Replaces index 22
                *base_data[23:27],
                format_url(photo_url, html_format=True),            # Replaces index 27
                *base_data[28:]
            ))

            # LAVA row
            data_list.append(base_data)

        except (ValueError, IndexError, TypeError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Failed parsing record ZFSPHOTO {record[0]} in {source_path}: {ex}")
            continue

    return data_headers, (data_list, data_list_html), source_path


@artifact_processor
def foursquare_swarm_comments(context):
    """
    Extracts all comments from ZFSCOMMENT regardless of source, including
    comments on check-ins, plans, tips, lists, and stickers. For each comment,
    the source type, author, text, GPS coordinates, and associated venue
    details are extracted where available.
    """

    data_headers = (
        ('Created', 'datetime'),
        'Source Type',
        'Source Text',
        'Relationship',
        'Full Name',
        'Text',
        'Pending',
        'Status',
        'Comment Type',
        'Mention Ranges',
        'Entities',
        'Latitude',
        'Longitude',
        'Display Geo',
        'Venue Name',
        'Venue Latitude',
        'Venue Longitude',
        'Unique ID',
        'Location'
    )

    data_list = []
    data_list_html = []

    source_path = context.get_source_file_path('foursquare.sqlite')
    if not source_path:
        return data_headers, (data_list, data_list_html), source_path

    # Swarm 6.x: ZDISPLAYGEO
    if does_column_exist_in_db(source_path, 'ZFSCOMMENT', 'ZDISPLAYGEO'):
        has_g_pk = "G.Z_PK"
        has_display_geo = "G.ZDISPLAYNAME"
        join_display_geo = "LEFT JOIN ZFSROBINDISPLAYGEO AS \"G\" ON (C.ZDISPLAYGEO = G.Z_PK)"
    else:
        has_g_pk = "NULL"
        has_display_geo = "NULL"
        join_display_geo = ""

    query = f'''
    SELECT
        C.Z_PK AS "C_PK",
        U.Z_PK AS "U_PK",
        CI.Z_PK AS "CI_PK",
        PL.Z_PK AS "PL_PK",
        T.Z_PK AS "T_PK",
        L.Z_PK AS "L_PK",
        S.Z_PK AS "S_PK",
        {has_g_pk} AS "G_PK",
        V.Z_PK AS "V_PK",
	    (C.ZCREATEDAT + 978307200) AS "created",
        CASE
            WHEN C.ZCHECKIN IS NOT NULL THEN 'Check-in'
            WHEN C.ZPLAN IS NOT NULL THEN 'Plan'
            WHEN C.ZTIP IS NOT NULL THEN 'Tip'
            WHEN C.ZLIST IS NOT NULL THEN 'List'
            WHEN C.ZSTICKER IS NOT NULL THEN 'Sticker'
            ELSE 'Unknown'
        END AS "source_type",
        CASE
            WHEN C.ZCHECKIN IS NOT NULL THEN IFNULL(CI.ZSHOUT, '')
            WHEN C.ZPLAN IS NOT NULL THEN IFNULL(PL.ZTEXT, '')
            WHEN C.ZTIP IS NOT NULL THEN IFNULL(T.ZTEXT, '')
            WHEN C.ZLIST IS NOT NULL THEN IFNULL(L.ZNAME, '')
            WHEN C.ZSTICKER IS NOT NULL THEN IFNULL(S.ZNAME, '')
            ELSE ''
        END AS "source_text",
	    U.ZRELATIONSHIP,
	    TRIM(IFNULL(U.ZFIRSTNAME, '') || ' ' || IFNULL(U.ZLASTNAME, '')) AS "full_name",
    	C.ZTEXT,
	    IIF(C.ZPENDING = 1, 'Yes', IIF(C.ZPENDING = 0, 'No', NULL)) AS "pending",
        CASE
            WHEN C.ZSTATUS IS NULL THEN 'N/A'
            WHEN CAST(C.ZSTATUS AS TEXT) = '' THEN 'N/D'
            WHEN C.ZSTATUS = 0 THEN 'Draft/Failed'
            WHEN C.ZSTATUS = 1 THEN 'Sent/Synchronizing'
            WHEN C.ZSTATUS = 2 THEN 'Confirmed/Published'
            WHEN C.ZSTATUS = 3 THEN 'Deleted (Local Flag)'
            ELSE 'Unknown (' || CAST(C.ZSTATUS AS TEXT) || ')'
        END AS "status",
        CASE
            WHEN C.ZPLANCOMMENTTYPE IS NULL THEN 'N/A'
            WHEN C.ZPLANCOMMENTTYPE = '' THEN 'N/D'
            WHEN LOWER(C.ZPLANCOMMENTTYPE) = 'default' or C.ZPLANCOMMENTTYPE = '0' THEN 'Default'
            WHEN LOWER(C.ZPLANCOMMENTTYPE) = 'system' or C.ZPLANCOMMENTTYPE = '1' THEN 'System'
            WHEN LOWER(C.ZPLANCOMMENTTYPE) = 'shout' or C.ZPLANCOMMENTTYPE = '2' THEN 'Shout'
            ELSE 'Unknown (' || C.ZPLANCOMMENTTYPE || ')'
        END AS "comment_type",
	    C.ZMENTIONRANGESSTRING,
	    C.ZENTITIES,
    	C.ZLAT,
	    C.ZLNG,
    	{has_display_geo} AS "display_geo",
    	V.ZNAME AS "venue_name",
	    V.ZGEOLAT AS "venue_lat",
	    V.ZGEOLONG AS "venue_lng",
	    C.ZMONGOID AS "uid"
    FROM ZFSCOMMENT AS "C"
    LEFT JOIN ZFSUSER AS "U" ON (C.ZUSER = U.Z_PK)
    LEFT JOIN ZFSCHECKIN AS "CI" ON (C.ZCHECKIN = CI.Z_PK)
    LEFT JOIN ZFSPLAN AS "PL" ON (C.ZPLAN = PL.Z_PK)
    LEFT JOIN ZFSTIP AS "T" ON (C.ZTIP = T.Z_PK)
    LEFT JOIN ZFSLIST AS "L" ON (C.ZLIST = L.Z_PK)
    LEFT JOIN ZFSSTICKER AS "S" ON (C.ZSTICKER = S.Z_PK)
    {join_display_geo}
    LEFT JOIN ZFSVENUE AS "V" ON (V.Z_PK = COALESCE(CI.ZVENUE, T.ZVENUE))
    ORDER BY C.ZCREATEDAT DESC
    '''

    db_records = get_sqlite_db_records(source_path, query)
    if not db_records:
        return data_headers, (data_list, data_list_html), source_path

    for record in db_records:
        try:
            # Unpack record for clarity
            (c_pk, u_pk, ci_pk, pl_pk, t_pk, l_pk, s_pk, g_pk, v_pk,
             raw_created, source_type, source_text, relationship, full_name,
             comment, pending, status, comment_type, mention_ranges,
             entities_blob, lat, lon, display_geo,
             venue_name, v_lat, v_lng, uid) = record

            # Convert timestamps to UTC
            created = convert_unix_ts_to_utc(raw_created)

            # Decode ZENTITIES plist
            p_entities, h_entities = _decode_zentities(entities_blob)

            # Precise location within the source database table for validation
            location = [ f"ZFSCOMMENT (Z_PK: {c_pk})" ]
            if u_pk is not None:
                location.append(f"ZFSUSER (Z_PK: {u_pk})")
            if ci_pk is not None:
                location.append(f"ZFSCHECKIN (Z_PK: {ci_pk})")
            if pl_pk is not None:
                location.append(f"ZFSPLAN (Z_PK: {pl_pk})")
            if t_pk is not None:
                location.append(f"ZFSTIP (Z_PK: {t_pk})")
            if l_pk is not None:
                location.append(f"ZFSLIST (Z_PK: {l_pk})")
            if s_pk is not None:
                location.append(f"ZFSSTICKER (Z_PK: {s_pk})")
            if g_pk is not None:
                location.append(f"ZFSROBINDISPLAYGEO (Z_PK: {g_pk})")
            if v_pk is not None:
                location.append(f"ZFSVENUE (Z_PK: {v_pk})")
            location = COMMA_SEP.join(location)

            # Base row for both lists
            base_data = (
                created, source_type, source_text,
                _normalize_relationship(relationship),
                full_name, comment, pending, status,
                comment_type, mention_ranges,
                p_entities,                                         # 10 Entities (Plain)
                lat, lon, display_geo,
                venue_name, v_lat, v_lng,
                uid, location
            )

            # HTML row
            data_list_html.append((
                *base_data[:10],
                h_entities,                                         # Replaces index 10
                *base_data[11:]
            ))

            # LAVA row
            data_list.append(base_data)

        except (ValueError, IndexError, TypeError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Failed parsing record ZFSCOMMENT {record[0]} in {source_path}: {ex}")
            continue

    return data_headers, (data_list, data_list_html), source_path


@artifact_processor
def foursquare_swarm_friend_requests(context):
    """
    Extracts Foursquare Swarm friend requests from ZFSFRIENDREQUEST,
    including requester and requestee identities with their Swarm profile URLs.
    """

    data_headers = (
        ('Date Requested', 'datetime'),
        'Direction',
        'Status',
        'Requester Name',
        'Requester Relationship',
        'Requester ID',
        'Requestee Name',
        'Requestee Relationship',
        'Requestee ID',
        'UID',
        'Location'
    )

    data_list = []
    data_list_html = []

    source_path = context.get_source_file_path('foursquare.sqlite')
    if not source_path:
        return data_headers, (data_list, data_list_html), source_path

    query = '''
    SELECT
        FR.Z_PK AS "FR_PK",
        UR.Z_PK AS "UR_PK",
        UE.Z_PK AS "UE_PK",
        (FR.ZDATEREQUESTED + 978307200) AS "date_requested",
        CASE
            WHEN UE.ZRELATIONSHIP = 'self' THEN 'Inbound'
            WHEN UR.ZRELATIONSHIP = 'self' THEN 'Outbound'
            ELSE ''
        END AS "direction",
        CASE
            WHEN UE.ZRELATIONSHIP IS NULL AND UR.ZRELATIONSHIP IS NULL THEN 'N/A'
            WHEN CAST(UE.ZRELATIONSHIP AS TEXT) = '' AND CAST(UR.ZRELATIONSHIP AS TEXT) = '' THEN 'N/D'
            WHEN LOWER(UE.ZRELATIONSHIP) = 'self' THEN
            CASE LOWER(IFNULL(UR.ZRELATIONSHIP, ''))
                WHEN 'friend' THEN 'Accepted'
                WHEN 'friendship' THEN 'Accepted'
                WHEN 'pendingthem' THEN 'Pending'
                WHEN 'requested' THEN 'Pending'
                WHEN 'ignored' THEN 'Ignored'
                WHEN '' THEN 'N/D'
                ELSE 'Unknown (' || CAST(UR.ZRELATIONSHIP AS TEXT) || ')'
            END
            WHEN LOWER(UR.ZRELATIONSHIP) = 'self' THEN
            CASE LOWER(IFNULL(UE.ZRELATIONSHIP, ''))
                WHEN 'friend' THEN 'Accepted'
                WHEN 'friendship' THEN 'Accepted'
                WHEN 'pendingme' THEN 'Pending'
                WHEN 'ignored' THEN 'Ignored'
                WHEN '' THEN 'N/D'
                ELSE 'Unknown (' || CAST(UE.ZRELATIONSHIP AS TEXT) || ')'
            END
            ELSE
                'Non-Self Relation'
        END AS "derived_status",
        TRIM(IFNULL(UR.ZFIRSTNAME, '') || ' ' || IFNULL(UR.ZLASTNAME, '')) AS "requester_name",
        UR.ZRELATIONSHIP AS "requester_relationship",
        UR.ZCANONICALURL AS "requester_url",
        UR.ZMONGOID AS "requester_uid",
        TRIM(IFNULL(UE.ZFIRSTNAME, '') || ' ' || IFNULL(UE.ZLASTNAME, '')) AS "requestee_name",
        UE.ZRELATIONSHIP AS "requestee_relationship",
        UE.ZCANONICALURL AS "requestee_url",
        UE.ZMONGOID AS "requestee_uid",
        FR.ZMONGOID AS "uid"
    FROM ZFSFRIENDREQUEST AS "FR"
    LEFT JOIN ZFSUSER AS "UR" ON (FR.ZREQUESTER = UR.Z_PK)
    LEFT JOIN ZFSUSER AS "UE" ON (FR.ZREQUESTEE = UE.Z_PK)
    ORDER BY FR.ZDATEREQUESTED DESC
    '''

    db_records = get_sqlite_db_records(source_path, query)
    if not db_records:
        return data_headers, (data_list, data_list_html), source_path

    for record in db_records:
        try:
            # Unpack record for clarity
            (fr_pk, ur_pk, ue_pk, raw_date, direction, status,
             requester_name, requester_rel, requester_url, requester_uid,
             requestee_name, requestee_rel, requestee_url, requestee_uid,
             uid) = record

            # Convert timestamps to UTC
            date_requested = convert_unix_ts_to_utc(raw_date)

            # Precise location within the source database table for validation
            location = [ f"ZFSFRIENDREQUEST (Z_PK: {fr_pk})" ]
            if ur_pk is not None:
                location.append(f"ZFSUSER/requester (Z_PK: {ur_pk})")
            if ue_pk is not None:
                location.append(f"ZFSUSER/requestee (Z_PK: {ue_pk})")
            location = COMMA_SEP.join(location)

            base_data = (
                date_requested, direction,
                status, requester_name,
                _normalize_relationship(requester_rel),
                foursquare_uid_url(requester_uid, requester_url),   # 5 Requester Profile (Plain)
                requestee_name,
                _normalize_relationship(requestee_rel),
                foursquare_uid_url(requestee_uid, requestee_url),   # 8 Requestee Profile (Plain)
                uid, location
            )

            # HTML row
            data_list_html.append((
                *base_data[:5],
                foursquare_uid_url(requester_uid, requester_url,
                                   html_format=True),               # Replaces index 5
                *base_data[6:8],
                foursquare_uid_url(requestee_uid, requestee_url,
                                   html_format=True),               # Replaces index 8
                *base_data[9:]
            ))

            # LAVA row
            data_list.append(base_data)

        except (ValueError, IndexError, TypeError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    "Error - Failed parsing record ZFSFRIENDREQUEST "
                    f"{record[0]} in {source_path}: {ex}")
            continue

    return data_headers, (data_list, data_list_html), source_path


@artifact_processor
def foursquare_swarm_plans(context):
    """
    Extracts Swarm plans (meetups), including participants, text, draft comments,
    status flags, interest counts, entities, and read/mute state.
    """

    data_headers = (
        ('Created', 'datetime'),
        ('Last Modified', 'datetime'),
        'Relationship',
        'Author Name',
        'Type',
        'Participants',
        'Text',
        'Draft Comment',
        'Status',
        'Is Hidden',
        'In Feed',
        'Unread',
        'Mute State',
        'Read Marker',
        'Read Receipt',
        'Interested Count',
        'Interested Summary',
        'Comments Count',
        'Entities',
        'UID',
        'Location'
    )

    data_list = []
    data_list_html = []

    source_path = context.get_source_file_path('foursquare.sqlite')
    if not source_path:
        return data_headers, (data_list, data_list_html), source_path

    db = open_sqlite_db_readonly(source_path)
    if not db:
        return data_headers, (data_list, data_list_html), source_path

    try:
        cursor = db.cursor()

        # Resolve the 'PARTICIPANTS' relationship for the 'FSPlan' entity
        relation = _resolve_coredata_relationship(context, db, 'FSPlan',
                                                  'PARTICIPANTS', 'PARTICIPANTPLANS')

        subquery_participants = "'' AS participants"

        # If Core Data mapped the table successfully, inject the dynamic columns
        if (relation['table']
                and relation['inverse_col']
                and relation['target_col']):
            subquery_participants = f'''
            (
                SELECT GROUP_CONCAT(
                    TRIM(IFNULL(UP.ZFIRSTNAME, '') || ' ' || IFNULL(UP.ZLASTNAME, '')),
                    {SQL_LIST_SEP}
                )
                FROM {relation['table']} AS "PP"
                JOIN ZFSUSER AS "UP" ON (PP.{relation['target_col']} = UP.Z_PK)
                WHERE PP.{relation['inverse_col']} = P.Z_PK
            ) AS "participants"
            '''

        query = f'''
        SELECT
            P.Z_PK AS "P_PK",
            U.Z_PK AS "U_PK",
            (P.ZCREATEDAT + 978307200) AS "created",
            (P.ZLASTMODIFIEDTIME + 978307200) AS "last_modified",
            U.ZRELATIONSHIP,
            TRIM(IFNULL(U.ZFIRSTNAME, '') || ' ' || IFNULL(U.ZLASTNAME, '')) AS "author_name",
            CASE
                WHEN P.ZISGROUP IS NULL THEN 'N/A'
                WHEN CAST(P.ZISGROUP AS TEXT) = '' THEN 'N/D'
                WHEN P.ZISGROUP = 1 THEN 'Group'
                WHEN P.ZISGROUP = 0 THEN 'Individual'
                ELSE 'Unknown (' || CAST(P.ZISGROUP AS TEXT) || ')'
            END AS "plan_type",
            {subquery_participants},
            P.ZTEXT,
            P.ZDRAFTCOMMENT,
            CASE P.ZSTATUS
                WHEN 0 THEN 'Open'
                WHEN 1 THEN 'Confirmed'
                WHEN 2 THEN 'Cancelled'
                WHEN 3 THEN 'Expired'
                WHEN 4 THEN 'Deleted'
                WHEN 5 THEN 'Archived'
                WHEN 6 THEN 'System Deleted'
                ELSE 'Unknown (' || P.ZSTATUS || ')'
            END AS "status",
            IIF(P.ZHIDDENBYUSER = 1, 'Yes', IIF(P.ZHIDDENBYUSER = 0, 'No', NULL)) AS "is_hidden",
            IIF(P.ZINFEED = 1, 'Yes', IIF(P.ZINFEED = 0, 'No', NULL)) AS "in_feed",
            IIF(P.ZISUNREAD = 1, 'Yes', IIF(P.ZISUNREAD = 0, 'No', NULL)) AS "is_unread",
            CASE
                WHEN P.ZMUTESTATE IS NULL THEN 'N/A'
                WHEN P.ZMUTESTATE = '' THEN 'N/D'
                WHEN P.ZMUTESTATE = '0' THEN 'Not Muted'
                WHEN P.ZMUTESTATE = '1' THEN 'Muted Temporarily'
                WHEN P.ZMUTESTATE = '2' THEN 'Muted Permanently'
                ELSE 'Unknown (' || P.ZMUTESTATE || ')'
            END AS "mute_state",
            CASE
                WHEN P.ZREADMARKER IS NULL THEN 'N/A'
                WHEN P.ZREADMARKER = '' THEN 'N/D'
                WHEN P.ZREADMARKER = '0' THEN 'Initialized (No Read Activity)'
                WHEN CAST(P.ZREADMARKER AS DOUBLE) > 0.0 THEN 'Last Read at: ' ||
                  datetime(CAST(P.ZREADMARKER AS DOUBLE) + 978307200, 'unixepoch')
                WHEN P.ZREADMARKER = 'false' THEN 'Never Read'
                ELSE 'Marker: ' || P.ZREADMARKER
            END AS "read_marker",
            CASE  
                WHEN P.ZREADRECEIPT IS NULL THEN 'N/A'
                WHEN P.ZREADRECEIPT = '' THEN 'N/D'
                WHEN P.ZREADRECEIPT = '0' THEN 'Unread/New'
                WHEN P.ZREADRECEIPT = '1' THEN 'Confirmed (Read)'
                WHEN P.ZREADRECEIPT = '2' THEN 'Read (Group)'
                ELSE 'Status: ' || P.ZREADRECEIPT
            END AS "read_receipt",
            P.ZINTERESTEDCOUNT,
            P.ZINTERESTEDSUMMARY,
            P.ZCOMMENTSCOUNT,
            P.ZENTITIES,
            P.ZMONGOID AS "uid"
        FROM ZFSPLAN AS "P"
        LEFT JOIN ZFSUSER AS "U" ON (P.ZUSER = U.Z_PK)
        ORDER BY P.ZCREATEDAT DESC
        '''

        cursor.execute(query)
        for record in cursor:
            try:
                # Unpack record for clarity
                (p_pk, u_pk, raw_created, raw_last_modified, relationship, author_name,
                plan_type, participants, text, draft_comment, status, is_hidden, in_feed,
                unread, mute_state, read_marker, read_receipt, interested_count,
                interested_summary, comments_count, entities_blob, uid) = record

                # Convert timestamps to UTC
                created = convert_unix_ts_to_utc(raw_created)
                last_modified = convert_unix_ts_to_utc(raw_last_modified)

                # Decode ZENTITIES plist
                p_entities, h_entities = _decode_zentities(entities_blob)

                # Precise location within the source database table for validation
                location = [ f"ZFSPLAN (Z_PK: {p_pk})" ]
                if u_pk is not None:
                    location.append(f"ZFSUSER (Z_PK: {u_pk})")
                location = COMMA_SEP.join(location)

                base_data = (
                    created, last_modified,
                    _normalize_relationship(relationship),
                    author_name, plan_type, participants, text,
                    draft_comment, status, is_hidden, in_feed,
                    unread, mute_state, read_marker, read_receipt,
                    interested_count, interested_summary,
                    comments_count,
                    p_entities,                                         # 18 Entities (Plain)
                    uid, location
                )

                # HTML row
                data_list_html.append((
                    *base_data[:18],
                    h_entities,                                         # Replaces index 18
                    *base_data[19:]
                ))

                # LAVA row
                data_list.append(base_data)

            except (ValueError, IndexError, TypeError) as ex:
                logfunc(f"[{context.get_artifact_name()}] "
                        f"Error - Failed parsing record ZFSPLAN {record[0]} "
                        f"in {source_path}: {ex}")
                continue

    except sqlite3.Error as db_ex:
        # Log fatal database errors (e.g., malformed DB or missing tables)
        logfunc(f"[{context.get_artifact_name()}] "
                f"Error - executing query on {source_path}: {db_ex}")
    finally:
        # Ensure the database connection is closed safely
        db.close()

    return data_headers, (data_list, data_list_html), source_path


@artifact_processor
def foursquare_swarm_events(context):
    """
    Extracts events associated with venues from ZFSEVENT, providing
    temporal context to the user's presence at a location. Includes
    event type, category, attendance count, and optional media metadata.
    """

    data_headers = (
        ('Start At', 'datetime'),
        ('End At', 'datetime'),
        ('Date', 'datetime'),
        'All Day',
        'Event Name',
        'Event Type',
        'Summary',
        'Here Now Count',
        'Friends Attended',
        'Venue Name',
        'Category',
        'Cast',
        'Directors',
        'Genres',
        'Rating',
        'Running Time (seconds)',
        'Provider',
        'Event URL',
        'UID',
        'Location'
    )

    data_list = []
    data_list_html = []

    source_path = context.get_source_file_path('foursquare.sqlite')
    if not source_path:
        return data_headers, (data_list, data_list_html), source_path

    db = open_sqlite_db_readonly(source_path)
    if not db:
        return data_headers, (data_list, data_list_html), source_path

    try:
        cursor = db.cursor()

        # Resolve the 'FRIENDSATTENDED' relationship for the 'FSEvent' entity
        relation = _resolve_coredata_relationship(context, db, 'FSEvent',
                                                  'FRIENDSATTENDED', 'EVENTSFRIENDSATTENDED')

        subquery_friends_attended = "'' AS friends_attended"

        # If Core Data mapped the table successfully, inject the dynamic columns
        if (relation['table']
                and relation['inverse_col']
                and relation['target_col']):
            subquery_friends_attended = f'''
            (
                SELECT GROUP_CONCAT(
                    TRIM(IFNULL(UA.ZFIRSTNAME, '') || ' ' || IFNULL(UA.ZLASTNAME, '')),
                    {SQL_LIST_SEP}
                )
                FROM {relation['table']} AS "FA"
                JOIN ZFSUSER AS "UA" ON (FA.{relation['target_col']} = UA.Z_PK)
                WHERE FA.{relation['inverse_col']} = E.Z_PK
            ) AS "friends_attended"
            '''

        query = f'''
        SELECT
            E.Z_PK AS "E_PK",
            V.Z_PK AS "V_PK",
            C.Z_PK AS "C_PK",
            (E.ZSTARTAT + 978307200) AS "start_at",
            (E.ZENDAT + 978307200) AS "end_at",
            (E.ZDATE + 978307200) AS "date",
            IIF(E.ZALLDAY = 1, 'Yes', IIF(E.ZALLDAY = 0, 'No', NULL)) AS "all_day",
            E.ZNAME AS "event_name",
            IFNULL(E.ZEVENTTYPE, 'standard') AS "event_type",
            E.ZSUMMARY,
            E.ZHERENOWCOUNT AS "here_now_count",
            {subquery_friends_attended},
            V.ZNAME AS "venue_name",
            C.ZNAME AS "category_name",
            E.ZCAST,
            E.ZDIRECTORS,
            E.ZGENRES,
            E.ZRATING,
            E.ZRUNNINGTIMESECONDS,
            E.ZPROVIDERNAME AS "provider",
            E.ZEVENTURL AS "event_url",
            E.ZMONGOID AS "uid"
        FROM ZFSEVENT AS "E"
        LEFT JOIN ZFSVENUE AS "V" ON (E.ZVENUE = V.Z_PK)
        LEFT JOIN ZFSCATEGORY AS "C" ON (E.ZPRIMARYCATEGORY = C.Z_PK)
        ORDER BY E.ZSTARTAT DESC
        '''

        cursor.execute(query)
        for record in cursor:
            try:
                # Unpack record for clarity
                (e_pk, v_pk, c_pk, raw_start, raw_end, raw_date,
                all_day, event_name, event_type, summary, here_now,
                friends_attended, venue_name, category, cast_,
                directors, genres, rating, running_time, provider,
                event_url, uid) = record

                # Convert timestamps to UTC
                start_at = convert_unix_ts_to_utc(raw_start)
                end_at = convert_unix_ts_to_utc(raw_end)
                date = convert_unix_ts_to_utc(raw_date)

                # Precise location within the source database table for validation
                location = [ f"ZFSEVENT (Z_PK: {e_pk})" ]
                if v_pk is not None:
                    location.append(f"ZFSVENUE (Z_PK: {v_pk})")
                if c_pk is not None:
                    location.append(f"ZFSCATEGORY (Z_PK: {c_pk})")
                location = COMMA_SEP.join(location)

                base_data = (
                    start_at, end_at, date, all_day,
                    event_name, event_type, summary, here_now,
                    friends_attended, venue_name, category,
                    cast_, directors, genres,
                    rating, running_time, provider,
                    format_url(event_url),                              # 17 Event URL (Plain)
                    uid, location
                )

                # HTML row
                data_list_html.append((
                    *base_data[:17],
                    format_url(event_url, html_format=True),            # Replaces index 17
                    *base_data[18:]
                ))

                # LAVA row
                data_list.append(base_data)

            except (ValueError, IndexError, TypeError) as ex:
                logfunc(f"[{context.get_artifact_name()}] "
                        f"Error - Failed parsing record ZFSEVENT "
                        f"{record[0]} in {source_path}: {ex}")
                continue

    except sqlite3.Error as db_ex:
        # Log fatal database errors (e.g., malformed DB or missing tables)
        logfunc(f"[{context.get_artifact_name()}] "
                f"Error - executing query on {source_path}: {db_ex}")
    finally:
        # Ensure the database connection is closed safely
        db.close()

    return data_headers, (data_list, data_list_html), source_path


@artifact_processor
def foursquare_swarm_saved_lists(context):
    """
    Extracts user-created and followed lists, including saved venues, 
    personal notes, and collaboration metadata.
    """

    data_headers = (
        ('Created', 'datetime'),
        ('Updated', 'datetime'),
        ('Client Updated', 'datetime'),
        ('Last Viewed', 'datetime'),
        ('Metadata Updated', 'datetime'),
        'Owner',
        'Creator',
        'Name',
        'Type',
        'Description',
        'Collaborative',
        'Access Level',
        'Items',
        'Followers',
        'Liked',
        'Likes',
        'List URL',
        ('Venue Added', 'datetime'),
        ('Venue Shared', 'datetime'),
        'Venue Name',
        'Address/City',
        'Latitude',
        'Longitude',
        'Visited',
        'Item Unread',
        'Item Status',
        'User Note',
        'Source Title',
        'Source URL',
        'Item Source',
        'Item Server ID',
        'UID',
        'Location'
    )

    data_list = []
    data_list_html = []

    source_path = context.get_source_file_path('foursquare.sqlite')
    if not source_path:
        return data_headers, (data_list, data_list_html), source_path

    # Swarm 7.x: ZCREATOR
    if does_column_exist_in_db(source_path, 'ZFSLIST', 'ZCREATOR'):
        has_creator_name = "TRIM(IFNULL(UC.ZFIRSTNAME, '') || ' ' || IFNULL(UC.ZLASTNAME, ''))"
        join_creator = "LEFT JOIN ZFSUSER AS \"UC\" ON (L.ZCREATOR = UC.Z_PK)"
    else:
        has_creator_name = "NULL"
        join_creator = ""
    # Swarm 7.x: ZCLIENTUPDATEDAT
    if does_column_exist_in_db(source_path, 'ZFSLIST', 'ZCLIENTUPDATEDAT'):
        has_client_updated = "(L.ZCLIENTUPDATEDAT + 978307200)"
    else:
        has_client_updated = "NULL"
    # Swarm 7.x: ZLASTVIEWEDAT
    if does_column_exist_in_db(source_path, 'ZFSLIST', 'ZLASTVIEWEDAT'):
        has_last_viewed = "(L.ZLASTVIEWEDAT + 978307200)"
    else:
        has_last_viewed = "NULL"
    # Swarm 7.x: ZACCESS
    if does_column_exist_in_db(source_path, 'ZFSLIST', 'ZACCESS'):
        has_access = "L.ZACCESS"
    # Swarm 6.x: ZEDITABLE and ZFOLLOWING
    elif (does_column_exist_in_db(source_path, 'ZFSLIST', 'ZEDITABLE')
          and does_column_exist_in_db(source_path, 'ZFSLIST', 'ZFOLLOWING')
          and does_column_exist_in_db(source_path, 'ZFSLIST', 'ZCOLLABORATIVE')):
        has_access = """CASE
            WHEN L.ZEDITABLE IS NULL AND L.ZCOLLABORATIVE IS NULL THEN 'N/A'
            WHEN CAST(L.ZEDITABLE AS TEXT) = '' AND CAST(L.ZCOLLABORATIVE AS TEXT) = '' THEN 'N/D'
            WHEN L.ZEDITABLE = 1 AND L.ZCOLLABORATIVE = 1 THEN 'friends (derived)'
            WHEN L.ZEDITABLE = 1 AND L.ZCOLLABORATIVE = 0 THEN 'private (derived)'
            WHEN L.ZEDITABLE = 0 THEN 'public (derived)'
            ELSE 'unknown (derived)'
        END"""
    else:
        has_access = "NULL"
    # Swarm 6.x: ZCOLLABORATIVE
    if does_column_exist_in_db(source_path, 'ZFSLIST', 'ZCOLLABORATIVE'):
        has_collaborative = (
            "IIF(L.ZCOLLABORATIVE = 1, 'Yes', "
            "IIF(L.ZCOLLABORATIVE = 0, 'No', NULL))"
        )
    else:
        has_collaborative = "NULL"
    # Swarm 7.x: ZUNREAD
    if does_column_exist_in_db(source_path, 'ZFSLISTITEM', 'ZUNREAD'):
        has_item_unread = "IIF(LI.ZUNREAD = 1, 'Yes', '')"
    else:
        has_item_unread = "''"
    # Swarm 7.x: ZSOURCE
    if does_column_exist_in_db(source_path, 'ZFSLISTITEM', 'ZSOURCE'):
        has_item_source = "LI.ZSOURCE"
    else:
        has_item_source = "NULL"
    # Swarm 7.x: ZSERVERID, Swarm 6.x: ZLISTITEMID / ZID
    if does_column_exist_in_db(source_path, 'ZFSLISTITEM', 'ZSERVERID'):
        has_item_server_id = "LI.ZSERVERID"
    elif does_column_exist_in_db(source_path, 'ZFSLISTITEM', 'ZLISTITEMID'):
        has_item_server_id = "LI.ZLISTITEMID"
    elif does_column_exist_in_db(source_path, 'ZFSLISTITEM', 'ZID'):
        has_item_server_id = "LI.ZID"
    else:
        has_item_server_id = "NULL"

    query = f'''
    SELECT
        L.Z_PK AS "L_PK",
        LI.Z_PK AS "LI_PK",
        V.Z_PK AS "V_PK",
        U.Z_PK AS "U_PK",
        (L.ZCREATEDAT + 978307200) AS "list_created",
        (L.ZLISTUPDATEDAT + 978307200) AS "list_updated",
        {has_client_updated} AS "list_client_updated",
        {has_last_viewed} AS "list_last_viewed",
        (L.ZUPDATEDAT + 978307200) AS "list_metadata_updated",
        TRIM(IFNULL(U.ZFIRSTNAME, '') || ' ' || IFNULL(U.ZLASTNAME, '')) AS "owner_name",
        {has_creator_name} AS "creator_name",
        L.ZNAME AS "list_name",
        L.ZLISTTYPE,
        L.ZLISTDESCRIPTION,
        {has_collaborative} AS "collaborative",
        {has_access} AS "access_level",
        L.ZLISTITEMSCOUNT,
        L.ZFOLLOWERSCOUNT,
        IIF(L.ZLIKE = 1, 'Yes', IIF(L.ZLIKE = 0, 'No', NULL)) AS "list_liked",
        L.ZLIKESCOUNT,
        L.ZCANONICALURL AS "list_url",
        (LI.ZCREATEDAT + 978307200) AS "item_added",
        (LI.ZSHAREDAT + 978307200) AS "item_shared",
        V.ZNAME AS "venue_name",
        V.ZADDRESS AS "venue_address",
        V.ZCITY AS "venue_city",
        V.ZGEOLAT AS "latitude",
        V.ZGEOLONG AS "longitude",
        IIF(LI.ZVISITED = 1, 'Yes', IIF(LI.ZVISITED = 0, 'No', NULL)) AS "visited",
        {has_item_unread} AS "item_unread",
        CASE
            WHEN LI.ZSTATE IS NULL THEN 'N/A'
            WHEN LI.ZSTATE = '' THEN 'N/D'
            WHEN LI.ZSTATE = '0' THEN 'Active/Saved'
            WHEN LI.ZSTATE = '1' THEN 'Archived'
            WHEN LI.ZSTATE = '2' THEN 'Removed'
            ELSE 'Unknown (' || LI.ZSTATE || ')'
        END AS "item_status",
        LI.ZTEXT AS "item_note",
        LI.ZSOURCEWEBTITLE AS "source_title",
        LI.ZSOURCEWEBURL AS "source_url",
        {has_item_source} AS "item_source",
        {has_item_server_id} AS "item_server_id",
        L.ZMONGOID AS "list_uid"
    FROM ZFSLIST AS "L"
    LEFT JOIN ZFSUSER AS "U" ON (L.ZUSER = U.Z_PK)
    {join_creator}
    LEFT JOIN ZFSLISTITEM AS "LI" ON (LI.ZLIST = L.Z_PK)
    LEFT JOIN ZFSVENUE AS "V" ON (LI.ZVENUE = V.Z_PK)
    WHERE L.ZNAME IS NOT NULL
    ORDER BY L.ZLISTUPDATEDAT DESC, LI.ZCREATEDAT DESC
    '''

    db_records = get_sqlite_db_records(source_path, query)
    if not db_records:
        return data_headers, (data_list, data_list_html), source_path

    for record in db_records:
        try:
            # Unpack record for clarity
            (l_pk, li_pk, v_pk, u_pk, l_raw_created, l_raw_updated,
             l_raw_client_updated, l_raw_last_viewed, l_raw_meta_updated,
             l_owner, l_creator, l_name, l_type, l_desc, l_collab, l_access_lvl,
             l_items_cnt, l_followers_cnt, l_liked, l_likes_cnt, l_url,
             i_raw_added, i_raw_shared, v_name, v_addr, v_city, v_lat, v_lon,
             i_visited, i_unread, i_status, i_note, i_src_title, i_src_url, i_src,
             i_srv_id, uid) = record

            # Convert timestamps
            list_created = convert_unix_ts_to_utc(l_raw_created)
            list_updated = convert_unix_ts_to_utc(l_raw_updated)
            list_client_updated = convert_unix_ts_to_utc(l_raw_client_updated)
            list_last_viewed = convert_unix_ts_to_utc(l_raw_last_viewed)
            list_metadata_updated = convert_unix_ts_to_utc(l_raw_meta_updated)
            item_added = convert_unix_ts_to_utc(i_raw_added)
            item_shared = convert_unix_ts_to_utc(i_raw_shared)

            # Combine address and city gracefully
            address_parts = [p for p in (v_addr, v_city) if p]
            full_address  = LIST_SEP.join(address_parts)

            # Note
            h_note = html.escape(str(i_note)) if i_note is not None else ""

            # Precise location within the source database table for validation
            location = [f"ZFSLIST (Z_PK: {l_pk})"]
            if u_pk:
                location.append(f"ZFSUSER (PK: {u_pk})")
            if li_pk is not None:
                location.append(f"ZFSLISTITEM (Z_PK: {li_pk})")
            if v_pk is not None:
                location.append(f"ZFSVENUE (Z_PK: {v_pk})")
            location = COMMA_SEP.join(location)

            base_data = (
                list_created, list_updated, list_client_updated,
                list_last_viewed, list_metadata_updated, l_owner,
                l_creator, l_name, l_type, l_desc, l_collab,
                l_access_lvl, l_items_cnt, l_followers_cnt,
                l_liked, l_likes_cnt,
                format_url(l_url),                                  # 16 List URL (Plain)
                item_added, item_shared, v_name, full_address,
                v_lat, v_lon, i_visited, i_unread, i_status,
                i_note,                                             # 26 Note (Plain)
                i_src_title,
                format_url(i_src_url),                              # 28 Source URL (Plain)
                i_src, i_srv_id, uid, location
            )

            # HTML Row (with escaped notes and formatted URLs)
            data_list_html.append((
                *base_data[:16], 
                format_url(l_url, html_format=True),                # Replaces index 16
                *base_data[17:26],
                h_note,                                             # Replaces index 26
                base_data[27],
                format_url(i_src_url, html_format=True),            # Replaces index 28
                *base_data[29:]
            ))

            # LAVA row
            data_list.append(base_data)

        except (ValueError, IndexError, TypeError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Failed parsing record ZFSLIST {record[0]} in {source_path}: {ex}")
            continue

    return data_headers, (data_list, data_list_html), source_path


@artifact_processor
def foursquare_swarm_location_history(context):
    """
    Extracts passive location history (GPS breadcrumbs) from the
    ZFSPLOCATION table, providing a granular movement trail.
    """

    data_headers = (
        ('Timestamp', 'datetime'),
        'Latitude',
        'Longitude',
        'Accuracy (meters)',
        'Accuracy Context',
        'Speed State',
        'Sync Status',
        'Location'
    )

    data_list = []

    source_path = context.get_source_file_path('foursquare.sqlite')
    if not source_path:
        return data_headers, data_list, source_path

    query = '''
    SELECT
		PL.Z_PK AS "PL_PK",
		(PL.ZTIMESTAMP + 978307200) AS "timestamp",
		PL.ZLATITUDE,
		PL.ZLONGITUDE,
		PL.ZHORIZONTALACCURACY,
        CASE
            WHEN PL.ZHORIZONTALACCURACY IS NULL THEN 'N/A'
            WHEN CAST(PL.ZHORIZONTALACCURACY AS TEXT) = '' THEN 'N/D'
            WHEN PL.ZHORIZONTALACCURACY < 0.0 THEN 'Invalid (No Fix/Negative)'
            WHEN PL.ZHORIZONTALACCURACY = 0.0 THEN 'Invalid (Zero Accuracy)'
            WHEN PL.ZHORIZONTALACCURACY <= 30.0 THEN 'High (GPS/Precise Wi-Fi)'
            WHEN PL.ZHORIZONTALACCURACY <= 200.0 THEN 'Medium (Wi-Fi Network)'
            WHEN PL.ZHORIZONTALACCURACY <= 1500.0 THEN 'Low (Cell Tower/Triangulation)'
            ELSE 'Very Low (' || CAST(PL.ZHORIZONTALACCURACY AS TEXT) || 'm)'
        END AS "accuracy_context",
        CASE
            WHEN PL.ZSPEEDSTATE IS NULL THEN 'N/A'
            WHEN CAST(PL.ZSPEEDSTATE AS TEXT) = '' THEN 'N/D'
            WHEN PL.ZSPEEDSTATE = 0 THEN 'Stationary'
            WHEN PL.ZSPEEDSTATE = 1 THEN 'Walking'
            WHEN PL.ZSPEEDSTATE = 2 THEN 'Automotive'
            WHEN PL.ZSPEEDSTATE = 3 THEN 'Cycling'
            WHEN PL.ZSPEEDSTATE = 4 THEN 'Running'
            ELSE 'Unknown (' || CAST(PL.ZSPEEDSTATE AS TEXT) || ')'
        END AS "speed_state",
        IIF(PL.ZSENT = 1, 'Synchronized', IIF(PL.ZSENT = 0, 'Local Only', NULL)) AS "sync_status"
    FROM ZFSPLOCATION AS "PL"
    WHERE PL.ZLATITUDE IS NOT NULL AND PL.ZLONGITUDE IS NOT NULL
    ORDER BY PL.ZTIMESTAMP DESC
    '''

    db_records = get_sqlite_db_records(source_path, query)
    if not db_records:
        return data_headers, data_list, source_path

    for record in db_records:
        try:
            # Unpack record for clarity
            (pl_pk, raw_ts, lat, lon, horz_acc,
             acc_ctx, speed_state, sync_status) = record

            # Convert timestamps to UTC
            ts = convert_unix_ts_to_utc(raw_ts)

            # Precise location within the source database table for validation
            location = f"ZFSPLOCATION (Z_PK: {pl_pk})"

            base_data = (
                ts, lat, lon, horz_acc,
                acc_ctx, speed_state, sync_status,
                location
            )

            # LAVA row
            data_list.append(base_data)

        except (ValueError, IndexError, TypeError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    "Error - Failed parsing record ZFSPLOCATION "
                    f"{record[0]} in {source_path}: {ex}")
            continue

    return data_headers, data_list, source_path


@artifact_processor
def foursquare_swarm_plog(context):
    """
    Extracts diagnostic and background event logs from the Pilgrim SDK.
    """

    data_headers = (
        ('Timestamp', 'datetime'),
        'Log Level',
        'App State',
        'Title',
        'Details', 
        'Event Type',
        'Latitude',
        'Longitude',
        'Accuracy (m)', 
        'Accuracy Context',
        'Radius (m)',
        'Location'
    )

    data_list = []
    data_list_html = []

    source_path = context.get_source_file_path('foursquare.sqlite')
    if not source_path:
        return data_headers, (data_list, data_list_html), source_path

    query = '''
    SELECT
        PL.Z_PK AS "Z_PK",
        (PL.ZTIMESTAMP + 978307200) AS "timestamp",
        CASE
            WHEN PL.ZLOGLEVEL IS NULL THEN 'N/A'
            WHEN CAST(PL.ZLOGLEVEL AS TEXT) = '' THEN 'N/D'
            WHEN PL.ZLOGLEVEL = 1 THEN 'Error'
            WHEN PL.ZLOGLEVEL = 2 THEN 'Warning'
            WHEN PL.ZLOGLEVEL = 3 THEN 'Info'
            WHEN PL.ZLOGLEVEL = 4 THEN 'Debug'
            ELSE 'Unknown (' || CAST(PL.ZLOGLEVEL AS TEXT) || ')'
        END AS "log_level",
        CASE
            WHEN PL.ZAPPSTATE IS NULL THEN 'N/A'
            WHEN CAST(PL.ZAPPSTATE AS TEXT) = '' THEN 'N/D'
            WHEN PL.ZAPPSTATE = 0 THEN 'Background'
            WHEN PL.ZAPPSTATE = 1 THEN 'Foreground'
            ELSE 'Unknown (' || CAST(PL.ZAPPSTATE AS TEXT) || ')'
        END AS "app_state",
        PL.ZLOGTITLE,
        PL.ZINFO,
        PL.ZEVENTTYPE,
        PL.ZLATITUDE ,
        PL.ZLONGITUDE,
        PL.ZHORIZONTALACCURACY,
        CASE
            WHEN PL.ZHORIZONTALACCURACY IS NULL THEN 'N/A'
            WHEN CAST(PL.ZHORIZONTALACCURACY AS TEXT) = '' THEN 'N/D'
            WHEN PL.ZHORIZONTALACCURACY < 0.0 THEN 'Invalid (No Fix/Negative)'
            WHEN PL.ZHORIZONTALACCURACY = 0.0 THEN 'Invalid (Zero Accuracy)'
            WHEN PL.ZHORIZONTALACCURACY <= 30.0 THEN 'High (GPS/Precise Wi-Fi)'
            WHEN PL.ZHORIZONTALACCURACY <= 200.0 THEN 'Medium (Wi-Fi Network)'
            WHEN PL.ZHORIZONTALACCURACY <= 1500.0 THEN 'Low (Cell Tower/Triangulation)'
            ELSE 'Very Low (' || CAST(PL.ZHORIZONTALACCURACY AS TEXT) || 'm)'
        END AS "accuracy_context",
        PL.ZRADIUS
    FROM ZFSPLOG AS "PL"
    WHERE PL.ZTIMESTAMP IS NOT NULL
    ORDER BY PL.ZTIMESTAMP DESC
    '''

    db_records = get_sqlite_db_records(source_path, query)
    if not db_records:
        return data_headers, (data_list, data_list_html), source_path

    for record in db_records:
        try:
            # Unpack record for clarity
            (pl_pk, raw_ts, level, app_state, title, info,
             event_type, lat, lon, horz_acc, acc_ctx, radius) = record

            # Convert timestamps to UTC
            ts = convert_unix_ts_to_utc(raw_ts)

            # Info
            h_info = html.escape(str(info)) if info is not None else ""

            # Precise location within the source database table for validation
            location = f"ZFSPLOG (Z_PK: {pl_pk})"

            base_data = (
                ts, level, app_state, title,
                info,                                               # 4 Info (Plain)
                event_type, lat, lon, horz_acc,
                acc_ctx, radius,
                location
            )

            # HTML Row
            data_list_html.append((
                *base_data[:4],
                h_info,                                             # Replaces index 4
                *base_data[5:]
            ))

            # LAVA row
            data_list.append(base_data)

        except (ValueError, IndexError, TypeError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    "Error - Failed parsing record ZFSPLOG "
                    f"{record[0]} in {source_path}: {ex}")
            continue

    return data_headers, (data_list, data_list_html), source_path


def _recursive_find_keys(data, target_keys: set[str] | frozenset[str]) -> list:
    """
    Recursively searches nested dict/list structures for specific keys,
    stopping recursion at matched nodes to avoid double-extraction.

    Args:
        data: dict, list, or any scalar value
        target_keys: set of key names to match

    Returns:
        list of matched values; matched nodes are not recursed into
    """

    results = []

    if isinstance(data, dict):
        for key, value in data.items():
            if key in target_keys:
                # Collect matched value as-is; do NOT recurse into it.
                if value not in (None, '', '$null'):
                    results.append(value)
            elif isinstance(value, (dict, list)):
                results.extend(_recursive_find_keys(value, target_keys))

    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                results.extend(_recursive_find_keys(item, target_keys))

    return results


def _decode_zblob_structure(blob: bytes) -> dict | list | None:
    """
    Decodes Swarm/Foursquare Core Data structured BLOBs into
    a Python dict or list for structured key extraction.

    Returns:
        dict or list on success; None if the payload is empty,
        unrecognised, or unparseable.
    """

    if not blob:
        return None

    decoded: dict | list | None = None

    # Binary plist
    if blob.startswith(b'bplist'):
        decoded = get_plist_content(bytes(blob))

    # JSON fallback — only attempted when plist produced no structured result.
    if not isinstance(decoded, (dict, list)):
        for encoding in ('utf-8', 'utf-16'):
            try:
                decoded = json.loads(blob.decode(encoding, errors='strict'))
                break
            except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
                continue

    # Drop raw strings, numbers, and other non-structured results
    if not isinstance(decoded, (dict, list)):
        return None

    # Filter Core Data null sentinels from top-level lists
    if isinstance(decoded, list):
        return [item for item in decoded
                if item not in (None, '', '$null')]

    return decoded


def _format_user_display(user: dict) -> str:
    """
    Formats a Swarm user dict into a readable display string.

    Output: "First Last (@username) [id]"
    Each component is omitted when the value is absent.
    """

    user_id = (user.get('id') or user.get('uid')
            or user.get('userId') or user.get('mongoId') or '')

    first  = (user.get('firstName')  or user.get('firstname')  or '').strip()
    last   = (user.get('lastName')   or user.get('lastname')   or '').strip()
    display = (user.get('displayName')
            or ' '.join(filter(None, [first, last])) or '')

    username = (user.get('username') or '').strip()
    if username:
        display = f"{display} (@{username})" if display else f"@{username}"

    if user_id:
        display = f"{display} [{user_id}]" if display else f"[{user_id}]"

    return display.strip()


def _extract_zblob_participants(*payloads: bytes) -> list[str]:
    """
    Extracts participant/user objects from Swarm feed payloads.

    Returns list[str] — not a pre-joined string — so the caller can
    apply different separators for plain text (LIST_SEP) and HTML output.
    Caller pattern:
        parts = _extract_zblob_participants(blob_a, blob_b)
        p_participants = LIST_SEP.join(parts)
        h_participants = HTML_LINE_BREAK.join(parts)

    Args:
        *payloads: raw BLOB bytes from ZENTITIES or ZTARGET columns

    Output format per entry: "Alice Smith (@alice) [123]"
    """

    _participant_keys = {
        'participants',
        'users',
        'attendees',
        'friends',
        'interestedUsers'
    }

    participants: list[str] = []

    for payload in payloads:
        decoded = _decode_zblob_structure(payload)
        if not isinstance(decoded, (dict, list)):
            continue

        for match in _recursive_find_keys(decoded, _participant_keys):
            # Normalise single objects to a list for uniform processing
            items = match if isinstance(match, list) else [match]

            for user in items:
                if isinstance(user, dict):
                    display = _format_user_display(user)
                    if display:
                        participants.append(display)
                elif isinstance(user, str):
                    clean = user.strip()
                    if clean:
                        participants.append(clean)

    # Deduplicate preserving insertion order
    return list(dict.fromkeys(p for p in participants if p))


def _extract_zblob_social_actors(*payloads: bytes) -> list[str]:
    """
    Extracts social actors (likers, voters, followers, etc.)
    from Swarm feed payloads.

    Args:
        *payloads: raw BLOB bytes from ZENTITIES or ZTARGET columns

    Output format per entry: "Alice (@alice) [123]"
    """

    _actor_keys = {
        'likers',
        'voters',
        'interestedUsers',
        'reactedUsers',
        'followers'
    }

    actors: list[str] = []

    for payload in payloads:
        decoded = _decode_zblob_structure(payload)
        if not isinstance(decoded, (dict, list)):
            continue

        for match in _recursive_find_keys(decoded, _actor_keys):
            items = match if isinstance(match, list) else [match]

            for user in items:
                if isinstance(user, dict):
                    display = _format_user_display(user)
                    if display:
                        actors.append(display)
                elif isinstance(user, str):
                    clean = user.strip()
                    if clean:
                        actors.append(clean)

    # Deduplicate preserving insertion order
    return list(dict.fromkeys(a for a in actors if a))


def _extract_zblob_replies(*payloads: bytes) -> list[str]:
    """
    Extracts replies/comments/responses from Swarm feed payloads.

    Args:
        *payloads: raw BLOB bytes from ZENTITIES or ZTARGET columns

    Output format per entry: "author: text" or "text"
    """

    _reply_keys = {
        'replies',
        'responses',
        'comments'
    }

    replies: list[str] = []

    for payload in payloads:
        decoded = _decode_zblob_structure(payload)
        if not isinstance(decoded, (dict, list)):
            continue

        for match in _recursive_find_keys(decoded, _reply_keys):
            items = match if isinstance(match, list) else [match]

            for item in items:
                if isinstance(item, dict):
                    text = (item.get('text') or item.get('message')
                            or item.get('body') or item.get('reply') or '')
                    if not text:
                        continue

                    author = (item.get('author') or item.get('username')
                              or item.get('displayName') or '')

                    replies.append(f"{author}: {text}" if author else str(text))

                elif isinstance(item, str):
                    clean = item.strip()
                    if clean:
                        replies.append(clean)

    return list(dict.fromkeys(r for r in replies if r))


@artifact_processor
def foursquare_swarm_feed(context):
    """
    Extracts the social activity feed stream and notifications.
    """

    data_headers = (
        ('Created', 'datetime'),
        'Feed Type',
        'Content Type',
        'Bulletin Type',
        'Title',
        'Text',
        'Action Text',
        'Participants',
        'Replies',
        'Social Actors',
        'Actor Name',
        'Target Name',
        'Image URL',
        ('Bulletin Image', 'media', 'height: 48px; border-radius: 5%;'),
        'Native Check-in Shout',
        'Venue Name',
        'Venue Latitude',
        'Venue Longitude',
        'Entities',
        'Target',
        'UID',
        'Location'
    )

    data_list = []
    data_list_html = []

    source_path = context.get_source_file_path('foursquare.sqlite')
    if not source_path:
        return data_headers, (data_list, data_list_html), source_path

    # Build or retrieve the photo cache map
    photo_map = _build_photo_map(context)

    query = '''
    SELECT
        FI.Z_PK AS "FI_PK",
        B.Z_PK AS "B_PK",
        UA.Z_PK AS "UA_PK",
        UT.Z_PK AS "UT_PK",
        CI.Z_PK AS "CI_PK",
        V.Z_PK AS "V_PK",
        (FI.ZCREATEDAT + 978307200) AS "created",
        FI.ZFEEDTYPE,
        CASE
            WHEN FI.ZFEEDCONTENTTYPE IS NULL THEN 'N/A'
            WHEN CAST(FI.ZFEEDCONTENTTYPE AS TEXT) = '' THEN 'N/D'
            WHEN FI.ZFEEDCONTENTTYPE = 1 THEN 'Friend Check-in'
            WHEN FI.ZFEEDCONTENTTYPE = 2 THEN 'Social Interaction (Like/Comment)'
            WHEN FI.ZFEEDCONTENTTYPE = 3 THEN 'Friend Request/Recommendation'
            WHEN FI.ZFEEDCONTENTTYPE = 4 THEN 'System Notification/Milestone'
            ELSE 'Unknown (' || CAST(FI.ZFEEDCONTENTTYPE AS TEXT) || ')'
        END AS "content_type",
        B.ZBULLETINTYPE,
        B.ZTITLETEXT,
        B.ZTEXT,
        B.ZACTIONTEXT,
        TRIM(IFNULL(UA.ZFIRSTNAME, '') || ' ' || IFNULL(UA.ZLASTNAME, '')) AS "actor_name",
        TRIM(IFNULL(UT.ZFIRSTNAME, '') || ' ' || IFNULL(UT.ZLASTNAME, '')) AS "target_name",
        B.ZIMAGEPREFIX,
        B.ZIMAGESUFFIX,
        IFNULL(CI.ZSHOUT, '') AS "native_checkin_shout",
        COALESCE(V.ZNAME, B.ZVENUEID) AS "resolved_venue_name",
        V.ZGEOLAT AS "venue_latitude",
        V.ZGEOLONG AS "venue_longitude",
        B.ZENTITIES AS "entities",
        B.ZTARGET AS "target",
        FI.ZMONGOID
    FROM ZFSSIMPLEFEEDITEM AS "FI"
    LEFT JOIN ZFSACTIVITYSTREAMBULLETIN AS "B" ON (FI.ZACTIVITYSTREAMBULLETIN = B.Z_PK)
    LEFT JOIN ZFSUSER AS "UA" ON (FI.ZUSER = UA.Z_PK)
    LEFT JOIN ZFSUSER AS "UT" ON (B.ZUSER = UT.Z_PK)
    LEFT JOIN ZFSCHECKIN AS "CI" ON (FI.ZCHECKIN = CI.Z_PK)
    LEFT JOIN ZFSVENUE AS "V" ON (CI.ZVENUE = V.Z_PK)
    ORDER BY FI.ZCREATEDAT DESC
    '''

    db_records = get_sqlite_db_records(source_path, query)
    if not db_records:
        return data_headers, (data_list, data_list_html), source_path

    for record in db_records:
        try:
            # Unpack the database record fields
            (fi_pk, b_pk, ua_pk, ut_pk, ci_pk, v_pk, raw_created,
             feed_type, content_type, bulletin_type, title, text,
             action_text, actor_name, target_name, img_prefix,
             img_suffix, native_ci_shout, venue_name, venue_lat,
             venue_lng, entities_blob, target_blob, uid) = record

            # Convert Core Data timestamps to UTC format
            created = convert_unix_ts_to_utc(raw_created)

            # Decode ZENTITIES and ZTARGET plists
            p_entities, h_entities = _decode_zentities(entities_blob)
            p_target, h_target = _decode_zentities(target_blob)

            decoded_entities = _decode_zblob_structure(entities_blob)
            decoded_target = _decode_zblob_structure(target_blob)

            # Extract social intelligence
            participants = _extract_zblob_participants(entities_blob, target_blob)
            p_participants = LIST_SEP.join(participants)
            h_participants = HTML_LINE_BREAK.join(participants)

            replies = _extract_zblob_replies(entities_blob, target_blob)
            p_replies = LIST_SEP.join(replies)
            h_replies = HTML_LINE_BREAK.join(replies)

            social_actors = _extract_zblob_social_actors(entities_blob, target_blob)
            p_social_actors = LIST_SEP.join(social_actors)
            h_social_actors = HTML_LINE_BREAK.join(social_actors)

            # Fallback mechanism: extract strings directly from the decoded Core Data object
            if not text:
                if isinstance(decoded_entities, dict):
                    text = decoded_entities.get('text') or decoded_entities.get('message') or ''

                if (not text and isinstance(decoded_target, dict)):
                    text = decoded_target.get('text') or decoded_target.get('message') or ''

            if not title:
                if isinstance(decoded_entities, dict):
                    title = decoded_entities.get('title') or ''

                if not title and isinstance(decoded_target, dict):
                    title = decoded_target.get('title') or ''


            # If the user relation didn't resolve via SQL, parse it from the embedded object
            if not actor_name:
                user_obj = None
                if isinstance(decoded_entities, dict):
                    user_obj = decoded_entities.get('user')

                if not user_obj and isinstance(decoded_target, dict):
                    user_obj = decoded_target.get('user')

                if isinstance(user_obj, dict):
                    first_name = user_obj.get('firstName') or ''
                    last_name = user_obj.get('lastName') or ''
                    actor_name = (f"{first_name} {last_name}").strip()
                    uid = uid or user_obj.get('id')

            # Resolve external media URLs using the internal PINDiskCache mapper
            image_url = f"{img_prefix}original{img_suffix}" if img_prefix and img_suffix else ""
            media_ref_id = None
            if img_suffix:
                media = resolve_media_reference(img_suffix, photo_map, context)
                media_ref_id = media['media_ref_id']

            # Precise location within the source database table for validation
            location = [f"ZFSSIMPLEFEEDITEM (Z_PK: {fi_pk})"]
            if b_pk is not None:
                location.append(f"ZFSACTIVITYSTREAMBULLETIN (Z_PK: {b_pk})")
            if ua_pk is not None and ut_pk is not None:
                location.append(f"ZFSUSER (Z_PK: {ua_pk}), (Z_PK: {ut_pk})")
            elif ua_pk is not None:
                location.append(f"ZFSUSER (Z_PK: {ua_pk})")
            elif ut_pk is not None:
                location.append(f"ZFSUSER (Z_PK: {ut_pk})")
            if ci_pk is not None:
                location.append(f"ZFSCHECKIN (Z_PK: {ci_pk})")
            if v_pk is not None:
                location.append(f"ZFSVENUE (Z_PK: {v_pk})")
            location = COMMA_SEP.join(location)

            base_data = (
                created, feed_type, content_type,
                bulletin_type, title, text, action_text,
                p_participants,                                     # 7 Participants (Plain)
                p_replies,                                          # 8 Replies (Plain)
                p_social_actors,                                    # 9 Social Actors (Plain)
                actor_name, target_name,
                format_url(image_url),                              # 12 Image URL (Plain)
                media_ref_id, native_ci_shout,
                venue_name, venue_lat, venue_lng,
                p_entities,                                         # 18 Entities (Plain)
                p_target,                                           # 19 Target (Plain)
                uid, location
            )

            # HTML row
            data_list_html.append((
                *base_data[:7],
                h_participants,                                     # Replaces Index 7
                h_replies,                                          # Replaces Index 8
                h_social_actors,                                    # Replaces Index 9
                *base_data[10:12],
                format_url(image_url, html_format=True),            # Replaces Index 12
                *base_data[13:18],
                h_entities,                                         # Replaces Index 18
                h_target,                                           # Replaces Index 19
                *base_data[20:]
            ))

            # LAVA row
            data_list.append(base_data)

        except (ValueError, IndexError, TypeError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Failed parsing record ZFSSIMPLEFEEDITEM {record[0]} "
                    f"in {source_path}: {ex}")
            continue

    return data_headers, (data_list, data_list_html), source_path
