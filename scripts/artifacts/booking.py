__artifacts_v2__ = {
    "booking_account": {
        "name": "Booking - Account",
        "description": "Extracts Booking.com user profile details.",
        "author": "@djangofaiola",
        "creation_date": "2024-05-28",
        "last_update_date": "2026-03-30",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Application Support/"
                  "KeyValueStorageAccountDomain*",
                  "*/mobile/Containers/Data/Application/*/Library/Application Support/"
                  "AccountSettings*"),
        "output_types": [ "lava", "html", "tsv" ],
        "html_columns": [ "Profile Picture URL", "Emails", "Facilities" ],
        "artifact_icon": "user"
    },
    "booking_travellers": {
        "name": "Booking - Travel Companions",
        "description": "Extracts Booking.com saved travel companions details.",
        "author": "@djangofaiola",
        "creation_date": "2026-03-21",
        "last_update_date": "2026-03-30",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Application Support/"
                  "AccountSettings*"),
        "output_types": [ "lava", "html", "tsv" ],
        "artifact_icon": "users"
    },
    "booking_payment_methods": {
        "name": "Booking - Payment Methods",
        "description": "Extracts Booking.com saved payment methods and credit card details.",
        "author": "@djangofaiola",
        "creation_date": "2024-05-28",
        "last_update_date": "2026-03-30",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Application Support/"
                  "KeyValueStorageAccountDomain*",
                  "*/mobile/Containers/Data/Application/*/Library/Application Support/"
                  "AccountSettings*"),
        "output_types": [ "lava", "html", "tsv" ],
        "artifact_icon": "credit-card"
    },
    "booking_wish_lists": {
        "name": "Booking - Wish Lists",
        "description": "Extracts Booking.com saved property wish lists.",
        "author": "@djangofaiola",
        "creation_date": "2024-05-28",
        "last_update_date": "2026-03-30",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Application Support/KeyValueStorageRecentsDomain*"),
        "output_types": [ "standard" ],
        "artifact_icon": "star"
    },
    "booking_viewed": {
        "name": "Booking - Viewed",
        "description": "Extracts Booking.com recently viewed accommodations.",
        "author": "@djangofaiola",
        "creation_date": "2024-05-28",
        "last_update_date": "2026-03-30",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Application Support/KeyValueStorageRecentsDomain*"),
        "output_types": [ "standard" ],
        "html_columns": [ "Image URL", "Website" ],
        "artifact_icon": "eye"
    },
    "booking_recently_searched": {
        "name": "Booking - Recently Searched",
        "description": "Extracts Booking.com recent searches for accommodations and destinations.",
        "author": "@djangofaiola",
        "creation_date": "2024-05-28",
        "last_update_date": "2026-03-30",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Application Support/KeyValueStorageRecentsDomain*"),
        "output_types": [ "standard" ],
        "artifact_icon": "search"
    },
    "booking_recently_booked": {
        "name": "Booking - Recently Booked",
        "description": "Extracts Booking.com recently booked accommodations and reservations.",
        "author": "@djangofaiola",
        "creation_date": "2024-05-28",
        "last_update_date": "2026-03-30",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Application Support/KeyValueStorageRecentsDomain*"),
        "output_types": [ "lava", "html", "tsv" ],
        "html_columns": [ "Image URL", "Website" ],
        "artifact_icon": "shopping-bag"
    },
    "booking_booked": {
        "name": "Booking - Booked",
        "description": "Extracts Booking.com saved and confirmed reservations.",
        "author": "@djangofaiola",
        "creation_date": "2024-05-28",
        "last_update_date": "2026-03-30",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Application Support/BookingClouds*",
                  "*/mobile/Containers/Data/Application/*/Documents/Booking #*.pdf",
                  "*/mobile/Containers/Data/Application/*/Library/Preferences/com.booking.BookingApp.plist"),
        "output_types": [ "standard" ],
        "html_columns": [ "Check-In/Out (Hotel Time Zone)", "Hotel Contacts",
                          "Confirmation Number/PIN Code", "Rooms", "Booker Details",
                          "Attachment", "Source File Name" ],
        "artifact_icon": "shopping-bag"
    },
    "booking_stored_destinations": {
        "name": "Booking - Stored Destinations",
        "description": "Extracts Booking.com stored travel destinations.",
        "author": "@djangofaiola",
        "creation_date": "2024-05-28",
        "last_update_date": "2026-03-30",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Application Support/KeyValueStorageSharedDomain*"),
        "output_types": [ "standard" ],
        "html_columns": [ "Image URL" ],
        "artifact_icon": "map"
    },
    "booking_notifications": {
        "name": "Booking - Notifications",
        "description": "Extracts Booking.com app notifications and messages.",
        "author": "@djangofaiola",
        "creation_date": "2024-05-28",
        "last_update_date": "2026-03-30",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Application Support/NotificationsModel.sqlite*"),
        "output_types": [ "standard" ],
        "artifact_icon": "bell"
    },
    "booking_flights_searched": {
        "name": "Booking - Flights Searched",
        "description": "Extracts Booking.com recent flight searches and trip preferences.",
        "author": "@djangofaiola",
        "creation_date": "2024-05-28",
        "last_update_date": "2026-03-30",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Application Support/flight_rs_v2"),
        "output_types": [ "standard" ],
        "html_columns": [ "Source Airports", "Destination Airports", "Routes",
                          "Travellers' Details" ],
        "artifact_icon": "search"
    }
    #P2GV2Messages.sqlite
}

import re
import json
import html
from urllib.parse import urlparse, urlunparse
from datetime import timezone, date, datetime
from pathlib import Path
import pytz
from scripts.ilapfuncs import get_sqlite_db_records, \
    get_plist_content, get_plist_file_content, convert_plist_date_to_utc, \
    convert_unix_ts_to_utc, check_in_media, artifact_processor, logfunc


# Constants
LINE_BREAK = '\n'
COMMA_SEP = ', '
HTML_LINE_BREAK = '<br>'
HTML_HORZ_RULE = '<hr>'
SOURCE_PATH_NOTE = "Refer to the 'Source file name' column to identify the exact " \
                   "device location of the origin file."


def unordered_list(values: list[str] | None, html_format: bool = False) -> str | None:
    """
    Format a list of strings as an unordered list.
    - If the input list is None or empty, return None.
    - If html_format=True, join items using <br> tags.
    - Otherwise, join items using line breaks.
   
    Args:
        values: A list of string items to format.
        html_format: If True, format output for HTML.

    Returns:
        A formatted string with items separated by line breaks or <br>, or None if input is empty.
    """

    if not values:
        return None

    separator = HTML_LINE_BREAK if html_format else LINE_BREAK

    return separator.join(values) if isinstance(values, list) else values


# Pattern to normalize timezone offsets from +HHMM -> +HH:MM
ISO_OFFSET_FIX = re.compile(r'([+-]\d{2})(\d{2})$')

def convert_iso8601_to_utc(str_date: str | bytes | None) -> str | None:
    """
    Convert an ISO 8601 formatted date string to a canonical UTC string
    consistent with convert_unix_ts_to_utc.
    - Input is expected to be a string or bytes.
    - Decodes bytes using UTF-8 with errors ignored.
    - Normalizes trailing 'Z' and compact offsets (+HHMM -> +HH:MM).
    - Returns the canonical UTC string on success.
    - On failure, returns the trimmed original string and logs the parse failure.

    Args:
        str_date: ISO 8601 formatted string or bytes, or None.

    Returns:
        str | None: Canonical UTC string, trimmed original string if parsing fails,
                    or None if input is None or cannot be decoded.
    """

    # Explicitly preserve None input
    if str_date is None:
        return None

    # Decode bytes to string if necessary
    if isinstance(str_date, bytes):
        str_date = str_date.decode('utf-8', errors='ignore')

    # Ensure the input is a string
    if not isinstance(str_date, str):
        str_date = str(str_date)

    # Trim leading/trailing whitespace
    s = str_date.strip()

    # Return early for empty or "null"-like values
    if not s or s.lower() == 'null':
        return s

    # Replace comma with dot in fractional seconds
    s = s.replace(",", ".")

    # Normalize trailing 'Z' (UTC designator) to explicit offset
    if s.endswith('Z'):
        s = s[:-1] + '+00:00'

    # Normalize compact timezone offsets (+HHMM -> +HH:MM)
    s = ISO_OFFSET_FIX.sub(r"\1:\2", s)

    try:
        # Parse ISO 8601 string
        dt = datetime.fromisoformat(s)

        if dt.tzinfo is None:
            # Treat naive datetimes as UTC
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            # Convert aware datetimes to UTC
            dt = dt.astimezone(timezone.utc)

        # Convert to canonical UTC string using helper
        return convert_unix_ts_to_utc(dt.timestamp())

    except (ValueError, TypeError) as e:
        # Log parsing failure and return original trimmed string
        logfunc(f"Error - convert_iso8601_to_utc: parse failed for {s!r}: {e}")
        return s


def format_url(str_url : str | None, html_format : bool = False) -> str:
    """
    Normalize a raw URL and optionally format it as a safe HTML anchor.
    - Return an empty string if str_url is None, empty, or the literal 'null'.
    - Strip leading and trailing whitespace.
    - If the URL has no scheme, default to 'https'.
    - In case of unexpected errors, return the cleaned input (do not raise).
    - When html_format=True, escape values and add rel attributes to prevent tabnabbing.
    """

    # Treat None, empty strings, and the literal 'null' as missing input.
    if not str_url or str_url.strip().lower() == 'null':
        return ''

    s = str_url.strip()
    try:
        parsed = urlparse(s)

        # If no scheme is present, assume http
        if not parsed.scheme:
            parsed = urlparse(f"https://{s}")
        normalized = urlunparse(parsed)

    except (ValueError, TypeError, AttributeError) as e:
        # Log the error and return the cleaned input without raising
        logfunc(f"Error - format_url parse failed for {str_url!r}: {e}")
        return s

    if html_format:
        # Escape both the href and the visible text to prevent XSS
        safe_href = html.escape(normalized, quote=True)
        safe_text = html.escape(normalized, quote=False)
        # Add rel="noopener noreferrer" with target="_blank" to prevent tabnabbing
        return (
            f'<a href="{safe_href}" target="_blank" '
            f'rel="noopener noreferrer">{safe_text}</a>'
        )

    return normalized


def get_json_file_content(file_path):
    """
    Read a JSON file and return its content as a dictionary.
    - On success, returns the parsed JSON as a dict.
    - If the file is missing, unreadable, or malformed, logs the error and returns {}.

    Args:
        file_path: Path to the JSON file.

    Returns:
        dict: Parsed JSON content, or {} if an error occurs.
    """

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            return json.load(file)
    except FileNotFoundError:
        logfunc(f"Error: JSON file not found at {file_path}")
    except PermissionError:
        logfunc(f"Error: Permission denied when trying to read {file_path}")
    except json.JSONDecodeError as e:
        logfunc(f"Error: Malformed JSON in file {file_path}: {str(e)}")
    except (OSError, UnicodeDecodeError) as e:
        logfunc(f"Error: OS or Encoding issue reading {file_path}: {e}")
    except Exception as e: # pylint: disable=broad-except
        logfunc(f"Unexpected error reading json data: {str(e)}")
    return {}


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


def location_type_names(value: int | None) -> str:
    """
    Convert a numeric location type code into its human-readable name.

    Args:
        value: Integer code representing a location type (0-7), or None.

    Returns:
        str: Corresponding location type name, or empty string if value is None,
             or 'N/D: <value>' if value is unknown.
    """

    if value is None:
        return ''

    mapping = {
        0 : 'City',
        1 : 'District',
        2 : 'Region',
        3 : 'Country',
        4 : 'Hotel',
        5 : 'Airport',
        6 : 'Landmark',
        7 : 'Google Places',
    }

    return mapping.get(value, f"N/D: {value}")


def hotel_type_names(value: int | None) -> str:
    """
    Convert a numeric hotel type code into its human-readable name.

    Args:
        value: Integer code representing a hotel type, or None.

    Returns:
        str: Corresponding hotel type name, or empty string if value is None,
             or 'N/D: <value>' if value is unknown.
    """

    if value is None:
        return ''

    mapping = {
        201 : 'Apartment',
        202 : 'Guest Accommodation',
        203 : 'Hostel',
        204 : 'Hotel',
        205 : 'Motel',
        206 : 'Resort',
        207 : 'Residence',
        208 : 'Bed and Breakfast',
        209 : 'Ryokan',
        210 : 'Farmstay',
        211 : 'Bungalow',
        212 : 'Resort Village',
        213 : 'Villa',
        214 : 'Campground',
        215 : 'Boat',
        216 : 'Guesthouse',
        218 : 'Inn',
        219 : 'Condo Hotel',
        220 : 'Vacation Home',
        221 : 'Lodge',
        222 : 'Homestay',
        223 : 'Country House',
        224 : 'Luxury Tent',
        225 : 'Capsule Hotel',
        226 : 'Love Hotel',
        227 : 'Riad',
        228 : 'Chalet',
        229 : 'Condo',
        230 : 'Cottage',
        231 : 'Economy Hotel',
        232 : 'Gite',
        233 : 'Health Resort',
        234 : 'Cruise',
        235 : 'Student Accommodation',
    }

    return mapping.get(value, f"N/D: {value}")


def convert_utc_to_hotel_timezone(ts, timezone_offset):
    """
    Convert a UTC datetime object to a specific hotel timezone.

    Args:
        ts: Datetime object (assumed UTC; may be naïve or timezone aware).
        timezone_offset: String representing the target timezone (e.g., 'Europe/Rome').

    Returns:
        datetime: Adjusted datetime object in the target timezone.
    """

    # Define UTC timezone using pytz
    utc_tz = pytz.utc

    try:
        # Define target timezone from the offset string
        target_tz = pytz.timezone(timezone_offset)

        # Fix naive datetime by localizing it to UTC
        if ts.tzinfo is None:
            ts = utc_tz.localize(ts)
        else:
            # If already aware, ensure it's converted to UTC first
            ts = ts.astimezone(utc_tz)

        # Convert to target timezone
        return ts.astimezone(target_tz)

    except (pytz.exceptions.UnknownTimeZoneError, ValueError, AttributeError, TypeError) as ex:
        # Log the error using the specific pytz exception
        logfunc(f"Error - Timezone conversion failed for {timezone_offset!r}: {ex}")

        # Fallback: ensure return is at least UTC aware if possible
        return ts if (ts and ts.tzinfo) else (utc_tz.localize(ts) if ts else None)


def format_check_in_out(ts_from, ts_until, tz: str = '') -> str:
    """
    Format check-in and check-out times into a single string.

    Args:
        ts_from: Starting timestamp, float, or string.
        ts_until: Ending timestamp, float, or string.
        tz: Timezone offset string.

    Returns:
        str: Formatted time range string (e.g., "10:00 - 23:59").
    """

    def _format_time(ts, timezone_str):
        # Helper to format individual timestamp based on type
        if not ts:
            return '00:00'

        # Handle seconds as float
        if isinstance(ts, float):
            return convert_unix_ts_to_utc(ts).strftime('%H:%M')

        # Handle direct string format
        if isinstance(ts, str):
            return ts

        # Handle timestamp with timezone conversion
        if len(timezone_str) > 0:
            return convert_utc_to_hotel_timezone(ts, timezone_str).strftime('%H:%M')

        # Handle standard datetime object
        return ts.strftime('%H:%M')

    # Use the helper for both values
    check_from = _format_time(ts_from, tz)
    check_until = _format_time(ts_until, tz)

    return f"{check_from} - {check_until}"


def append_tag_value(target: list, tag: str, value: any) -> None:
    """
    Append a formatted tag-value string to the target list.

    Args:
        target: The list to which the formatted string will be appended.
        tag: The label/key for the value.
        value: The data to be appended (skipped if None or empty collection).
    """

    # Skip if value is None
    if value is None:
        return

    # Skip if it's a string that is empty or contains only whitespace
    if isinstance(value, str) and not value.strip():
        return

    # Check for collections (dict, list, set, tuple)
    if isinstance(value, (dict, list, set, tuple)):
        # Only append if the collection is not empty
        if len(value) > 0:
            target.append(f"{tag}: {value}")
    else:
        # For all other types, append directly using f-string
        target.append(f"{tag}: {value}")


def get_booking_app_id(context) -> str:
    """
    Extract the Booking app identifier (UUID) from the source file path.

    Args:
        context: The artifact context object.

    Returns:
        str: The app UUID if found, otherwise an empty string.
    """

    # Expected path structure: /private/var/mobile/Containers/Data/Application/<UUID>/
    #                          Library/Preferences/com.booking.BookingApp.plist
    try:
        source_path_str = context.get_source_file_path('com.booking.BookingApp.plist')

        # Check if a path was actually returned
        if not source_path_str:
            logfunc("Booking Error - get_booking_app_id: plist file not found in context")
            return ''

        source_path = Path(source_path_str)

        # Verify the path is deep enough to have 3 parents (index 2)
        if len(source_path.parents) > 2:
            # parents[0] = Preferences, parents[1] = Library, parents[2] = <UUID>
            return source_path.parents[2].name

        logfunc("Booking Error - get_booking_app_id: Path structure is too shallow: "
                f"{source_path_str}")

    except (ValueError, AttributeError, IndexError) as e:
        logfunc(f"Booking Error - get_booking_app_id failed: {e}")

    return ''


def _get_avatar_url(data_dict: dict) -> str | None:
    """
    Extract the first available avatar URL from a dictionary.
    """

    urls = data_dict.get('urls', {})

    return next(iter(urls.values()), None) if urls else None


def _parse_key_value_account(plist_data: dict, device_path: str) -> tuple:
    """
    Parse data from KeyValueStorageAccountDomain plist.
    """

    user_profile = plist_data.get('user_profile', {})

    # Extract facilities
    facility_list = user_profile.get('preferred', {}).get('facility', [])
    selected_facs = [ x.get('name') for x in facility_list if x.get('is_selected') ]

    # Profile picture
    pp_url = _get_avatar_url(user_profile.get('avatar_details', {}))

    return (
        user_profile.get('first_name'), user_profile.get('last_name'),
        user_profile.get('nickname'), pp_url, user_profile.get('gender'),
        user_profile.get('date_of_birth'), user_profile.get('street'),
        user_profile.get('city'), user_profile.get('zipcode'),
        user_profile.get('country'), user_profile.get('telephone'),
        user_profile.get('email_address'), user_profile.get('is_genius'),
        selected_facs, user_profile.get('uid'), plist_data.get('auth_token'),
        device_path, '[user_profile], [auth_token]'
    )


def _parse_booking_dob(dob_dict: dict) -> date | str:
    """
    Safely parse Date of Birth from Booking.com dictionary.
    
    Returns:
        date: if the date is complete and valid.
        str: if the date is partial (e.g., '2024-05-00') or an empty string.
    """

    if not isinstance(dob_dict, dict):
        return ''

    # Extract values with 0 as fallback
    try:
        year = int(dob_dict.get('year', 0))
        month = int(dob_dict.get('month', 0))
        day = int(dob_dict.get('day', 0))
    except (ValueError, TypeError):
        return ''

    # Full and valid date
    if year > 0 and month > 0 and day > 0:
        try:
            return date(year, month, day)
        except ValueError:
            # For invalid dates like Feb 31st, return formatted string
            return f"{year:04d}-{month:02d}-{day:02d}"

    # Partial date (only year or year/month)
    if year > 0:
        m_str = f"{month:02d}" if month > 0 else "00"
        d_str = f"{day:02d}" if day > 0 else "00"
        return f"{year:04d}-{m_str}-{d_str}"

    return ''


def _parse_account_settings(plist_data: dict, device_path: str) -> tuple:
    """
    Parse data from AccountSettings plist.
    """

    u_details = plist_data.get('userDetailsResponse', {}).get('userDetails', {})
    personal = u_details.get('personalDetails', {})
    contact = u_details.get('contactDetails', {})

    # Birth date construction
    bday = _parse_booking_dob(personal.get('dateOfBirth'))

    pp_url = _get_avatar_url(personal.get('avatar', {}))
    addr = contact.get('address', {})

    return (
        personal.get('name', {}).get('first'), personal.get('name', {}).get('last'),
        personal.get('displayName'), pp_url, personal.get('gender'),
        bday, addr.get('street'), addr.get('cityName'),
        addr.get('zip'), addr.get('countryCode'),
        contact.get('primaryPhone', {}).get('fullNumber'),
        contact.get('primaryEmail', {}).get('address'),
        None, None, None, None, device_path, '[userDetailsResponse][userDetails]'
    )


@artifact_processor
def booking_account(context):
    """
    Extract Booking.com user account details.
    """

    data_headers = (
        'First Name',
        'Last Name',
        'Nickname',
        'Profile Picture URL',
        'Gender',
        ('Birth Date', 'date'),
        'Street',
        'City',
        'Zip Code',
        'Country',
        ('Phone Number', 'phonenumber'),
        'Emails', 
        'Genius Membership',
        'Facilities',
        'Unique ID',
        'Authentication Token',
        'Source File Name',
        'Location'
    )

    data_list = []
    data_list_html = []

    for file_found in context.get_files_found():
        file_found = str(file_found)

        # Check for AccountSettings (with or without .plist)
        is_account_settings = (file_found.endswith('AccountSettings') or
                               file_found.endswith('AccountSettings.plist'))

        # Check for KeyValueStorage (with or without .plist)
        is_key_value = (file_found.endswith('KeyValueStorageAccountDomain') or
                        file_found.endswith('KeyValueStorageAccountDomain.plist'))

        if not (is_account_settings or is_key_value):
            continue

        try:
            plist_data = get_plist_file_content(file_found)
            if not plist_data:
                continue
            device_path = get_device_file_path(file_found, context)

            # Determine which parser to use
            row_data = None
            if is_account_settings:
                row_data = _parse_account_settings(plist_data, device_path)
            else:
                row_data = _parse_key_value_account(plist_data, device_path)

            if row_data:
                # Unpack row_data for processing
                (f_name, l_name, nick, pp, gnd, bday, strt, cty,
                 zipc, cntry, ph, em, gen, fac, id_u, token, src, location) = row_data

                # Prepare HTML and LAVA versions
                pp_html = format_url(pp, html_format=True)
                emails_p = unordered_list(em)
                emails_h = unordered_list(em, html_format=True)
                fac_p = unordered_list(fac)
                fac_h = unordered_list(fac, html_format=True)

                # HTML row
                data_list_html.append((
                    f_name, l_name, nick, pp_html, gnd, bday, strt, cty, zipc, cntry, ph,
                    emails_h, gen, fac_h, id_u, token, src, location
                ))

                # LAVA row
                data_list.append((
                    f_name, l_name, nick, pp, gnd, bday, strt, cty, zipc, cntry, ph,
                    emails_p, gen, fac_p, id_u, token, src, location
                ))

        except (KeyError, TypeError, IndexError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Malformed structure in {file_found}: {ex}")
        except OSError as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Could not read {file_found}: {ex}")

    return data_headers, (data_list, data_list_html), SOURCE_PATH_NOTE


@artifact_processor
def booking_travellers(context):
    """
    Extract travel companions (saved guests) from Booking.com account data.
    """

    data_headers = (
        'First Name',
        'Last Name',
        'Gender',
        ('Birth Date', 'date'),
        'Unique ID',
        'Location'
    )

    data_list = []
    source_path = ''

    for file_found in context.get_files_found():
        file_found = str(file_found)

        # Check for AccountSettings (with or without .plist)
        if not (file_found.endswith('AccountSettings') or
                file_found.endswith('AccountSettings.plist')):
            continue

        try:
            source_path = file_found

            # Get the original source path from the context/seeker
            plist_data = get_plist_file_content(source_path)
            if not plist_data:
                continue

            # Path to the travellers list
            user_details_resp = plist_data.get('userDetailsResponse', {})
            user_details = user_details_resp.get('userDetails', {})
            travellers = user_details.get('travellers', [])

            for i, tc in enumerate(travellers):
                # Extract name components
                fullname = tc.get('fullName', {})
                first_name = fullname.get('first')
                last_name = fullname.get('last')

                # Gender
                gender = tc.get('gender', '')

                # Birth date with safety parsing (returns date or '')
                bday = _parse_booking_dob(tc.get('dateOfBirth'))

                # Unique identifier
                uid = tc.get('id')

                # Precise location within the plist structure for validation
                loc = f"[userDetailsResponse][userDetails][travellers][{i}]"

                # LAVA row
                data_list.append((first_name, last_name, gender, bday, uid, loc))

            # Stop the parser if data was successfully extracted from
            # either the legacy or the modern version of the file.
            if data_list:
                break

        except (KeyError, TypeError, IndexError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Malformed structure in {file_found}: {ex}")
        except OSError as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Could not read {file_found}: {ex}")

    return data_headers, data_list, source_path


def _parse_key_value_payment(plist_data: dict, device_path: str) -> list:
    """
    Parse payment methods from KeyValueStorageAccountDomain.
    """

    rows = []
    cc_details = plist_data.get('user_profile', {}).get('cc_details', [])

    for i, cc in enumerate(cc_details):
        # Format: mm-yyyy
        month = cc.get('cc_expire_month', 0)
        year = cc.get('cc_expire_year', '')
        valid_thru = f"{month:02}-{year}" if month and year else ''

        rows.append((
            cc.get('cc_id'),
            cc.get('cc_type'),
            cc.get('cc_status'),
            valid_thru,
            cc.get('cc_name'),
            cc.get('last_digits'),
            cc.get('cc_is_business'),
            device_path,
            f"[user_profile][cc_details][{i}]"
        ))

    return rows


def _parse_account_settings_payment(plist_data: dict, device_path: str) -> list:
    """
    Parse payment methods from AccountSettings.
    """

    rows = []
    cc_details = plist_data.get('cardsResponse', {}).get('values', [])

    for i, cc in enumerate(cc_details):
        rows.append((cc.get('id'), cc.get('name'), cc.get('status'),
                     cc.get('expirationDateFormatted'), None,
                     cc.get('lastDigits'), cc.get('cc_is_business'),
                     device_path, f"[cardsResponse][values][{i}]"
        ))
    return rows


@artifact_processor
def booking_payment_methods(context):
    """
    Extract payment methods from Booking.com account data.
    """

    data_headers = (
        'Unique ID',
        'Type',
        'Status',
        'Valid Thru',
        'Cardholder Name',
        'Last Four Digits',
        'Business',
        'Source File Name',
        'Location'
    )

    data_list = []

    for file_found in context.get_files_found():
        file_found = str(file_found)

        # Check for AccountSettings (with or without .plist)
        is_account_settings = (file_found.endswith('AccountSettings') or
                               file_found.endswith('AccountSettings.plist'))

        # Check for KeyValueStorage (with or without .plist)
        is_key_value = (file_found.endswith('KeyValueStorageAccountDomain') or
                        file_found.endswith('KeyValueStorageAccountDomain.plist'))

        if not (is_account_settings or is_key_value):
            continue

        try:
            plist_data = get_plist_file_content(file_found)
            if not plist_data:
                continue
            device_path = get_device_file_path(file_found, context)

            # Determine which parser to use
            rows_data = None
            if is_account_settings:
                rows_data = _parse_account_settings_payment(plist_data, device_path)
            else:
                rows_data = _parse_key_value_payment(plist_data, device_path)

            if rows_data:
                for row in rows_data:
                    # LAVA row
                    data_list.append(row)

        except (KeyError, TypeError, IndexError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Malformed structure in {file_found}: {ex}")
        except OSError as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Could not read {file_found}: {ex}")

    return data_headers, data_list, SOURCE_PATH_NOTE


def _get_destination_details(loc_dict: dict) -> tuple:
    """
    Extract location details from nested Booking.com data structures.
    """

    # Description/Address fallback
    description = loc_dict.get('substring_') or loc_dict.get('address', '')

    # City and Region handling
    city_data = loc_dict.get('city_')
    if city_data:
        city_name = city_data.get('string_')
        region_name = city_data.get('region_name')
    else:
        city_name = loc_dict.get('cityName_')
        region_name = loc_dict.get('region_name')

    # Country fallback
    country_name = loc_dict.get('countryName_') or loc_dict.get('country', '')

    # Coordinates fallback (standard vs locationType 7)
    loc_nested = loc_dict.get('location', {})
    if loc_nested:
        lat = loc_nested.get('latitude')
        lon = loc_nested.get('longitude')
    else:
        lat = loc_dict.get('latitude_')
        lon = loc_dict.get('longitude_')

    return description, city_name, region_name, country_name, lat, lon


@artifact_processor
def booking_stored_destinations(context):
    """
    Extract stored destinations from Booking.com shared data.
    """

    data_headers = (
        ('Created', 'datetime'),
        'Location Type',
        'Unique ID',
        'Destination Name',
        'Address/Description',
        'City',
        'Region',
        'Country',
        'Latitude',
        'Longitude',
        'Time Zone',
        'Image URL',
        'Location'
    )

    data_list = []
    data_list_html = []
    source_path = ''

    for file_found in context.get_files_found():
        file_found = str(file_found)

        # Check for KeyValueStorageSharedDomain (with or without .plist)
        if not (file_found.endswith('KeyValueStorageSharedDomain') or
                file_found.endswith('KeyValueStorageSharedDomain.plist')):
            continue

        try:
            source_path = file_found

            plist_data = get_plist_file_content(source_path)
            if not plist_data:
                continue

            destinations = plist_data.get('stored_destinations', []) if plist_data else []

            for i, dest in enumerate(destinations):
                loc_dict = dest.get('loc', {})
                desc, city, region, country, lat, lon = _get_destination_details(loc_dict)

                # Basic fields
                created = convert_plist_date_to_utc(dest.get('created'))
                loc_type = location_type_names(loc_dict.get('locationType_'))
                img_url = loc_dict.get('image_url')
                img_url_h = format_url(img_url, html_format=True)

                # Standard row data (excluding image and source)
                base_data = (
                    created, loc_type, loc_dict.get('id_'), loc_dict.get('string_'),
                    desc, city, region, country, lat, lon, loc_dict.get('timezone')
                )

                # Precise location within the plist structure for validation
                location = f"[stored_destinations][{i}]"

                # HTML row
                data_list_html.append(base_data + (img_url_h, location))

                # LAVA row
                data_list.append(base_data + (img_url, location))

            # Stop the parser if data was successfully extracted from
            # either the legacy or the modern version of the file.
            if data_list:
                break

        except (KeyError, TypeError, IndexError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Malformed structure in {file_found}: {ex}")
        except OSError as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Could not read {file_found}: {ex}")

    return data_headers, (data_list, data_list_html), source_path


@artifact_processor
def booking_recently_searched(context):
    """
    Extract recently searched destinations from Booking.com recents plist.
    """

    data_headers = (
        ('Searched', 'datetime'),
        'Location Type',
        'Unique ID',
        'Destination Name',
        'Description',
        'City',
        'Region',
        'Country',
        'Latitude',
        'Longitude',
        'Time Zone',
        'Check-In',
        'Check-Out',
        'Number of Rooms',
        'Guests',
        'Number of Nights',
        'App Source',
        'Location'
    )

    data_list = []
    source_path = ''

    for file_found in context.get_files_found():
        file_found = str(file_found)

        # Check for KeyValueStorageRecentsDomain (with or without .plist)
        if not (file_found.endswith('KeyValueStorageRecentsDomain') or
                file_found.endswith('KeyValueStorageRecentsDomain.plist')):
            continue

        try:
            source_path = file_found

            plist_data = get_plist_file_content(source_path)
            if not plist_data:
                continue

            searches = plist_data.get('stored_searches', []) if plist_data else []

            for i, ss in enumerate(searches):
                dest_dict = ss.get('destination', {})
                desc, city, region, country, lat, lon = _get_destination_details(dest_dict)

                # Basic search info
                searched = convert_plist_date_to_utc(ss.get('created'))
                loc_type = location_type_names(dest_dict.get('locationType_'))

                # Precise location within the plist structure for validation
                loc = f"[stored_searches][{i}]"

                # LAVA row
                data_list.append((
                    searched, loc_type, dest_dict.get('id_'), dest_dict.get('string_'),
                    desc, city, region, country, lat, lon, dest_dict.get('timezone'),
                    ss.get('checkin'), ss.get('checkout'), ss.get('number_of_rooms'),
                    ss.get('guests_per_room'), ss.get('number_of_nights'), ss.get('source'),
                    loc
                ))

            # Stop the parser if data was successfully extracted from
            # either the legacy or the modern version of the file.
            if data_list:
                break

        except (KeyError, TypeError, IndexError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Malformed structure in {file_found}: {ex}")
        except OSError as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Could not read {file_found}: {ex}")

    return data_headers, data_list, source_path


def _get_hotel_location(hotel: dict) -> tuple:
    """
    Extract city, region and zip details for a hotel.
    """

    city_data = hotel.get('city')
    if city_data:
        city_name = city_data.get('string_')
        region_name = city_data.get('region_name')
    else:
        city_name = hotel.get('cityName')
        region_name = hotel.get('region_name')

    return city_name, region_name, hotel.get('zip')


@artifact_processor
def booking_recently_booked(context):
    """
    Extract recently booked hotels from Booking.com recents plist.
    """

    data_headers = (
        'Hotel Type',
        'Hotel ID',
        'Hotel Name',
        'Address',
        'City',
        'Region',
        'Zip Code',
        'Latitude',
        'Longitude',
        'Check-In (Hotel Time Zone)',
        'Check-Out (Hotel Time Zone)',
        'Image URL',
        'Website', 
        'Location'
    )

    data_list = []
    data_list_html = []
    source_path = ''

    for file_found in context.get_files_found():
        file_found = str(file_found)

        # Check for KeyValueStorageRecentsDomain (with or without .plist)
        if not (file_found.endswith('KeyValueStorageRecentsDomain') or
                file_found.endswith('KeyValueStorageRecentsDomain.plist')):
            continue

        try:
            source_path = file_found

            plist_data = get_plist_file_content(source_path)
            if not plist_data:
                continue

            booked_dict = plist_data.get('booked', {}) if plist_data else {}

            for key, value in booked_dict.items():
                hotel = value.get('hotel', {})
                if not hotel:
                    continue

                # Location and address details
                city_name, region_name, zip_code = _get_hotel_location(hotel)

                # Check-in/out times
                check_in = format_check_in_out(
                    hotel.get('checkInFrom'),
                    hotel.get('checkInUntil')
                )
                check_out = format_check_in_out(
                    hotel.get('checkOutFrom'),
                    hotel.get('checkOutUntil')
                )

                # URLs
                p_url = hotel.get('pictureURL')
                p_url_h = format_url(p_url, html_format=True)
                website = hotel.get('hotelURL')
                website_h = format_url(website, html_format=True)

                # Precise location within the plist structure for validation
                loc = f"[booked][{key}]"

                # Standard row data (excluding profile picture url, website and location)
                base_data = (
                    hotel_type_names(hotel.get('hotel_type')), hotel.get('hotel_id'),
                    hotel.get('name'), hotel.get('address'), city_name, region_name,
                    zip_code, hotel.get('latitude'), hotel.get('longitude'),
                    check_in, check_out
                )

                # HTML row
                data_list_html.append(base_data + (p_url_h, website_h, loc))

                # LAVA row
                data_list.append(base_data + (p_url, website, loc))

            # Stop the parser if data was successfully extracted from
            # either the legacy or the modern version of the file.
            if data_list:
                break

        except (KeyError, TypeError, IndexError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Malformed structure in {file_found}: {ex}")
        except OSError as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Could not read {file_found}: {ex}")

    return data_headers, (data_list, data_list_html), source_path


def _get_room_details(rooms: list, html_format: bool = False) -> str:
    """
    Extract and format room-specific information.
    """

    if not isinstance(rooms, list) or not rooms:
        return ''

    results = []
    for i, room in enumerate(rooms):
        if not room:
            continue

        meta = []

        meta.append(f"Room {i} - {room.get('name', 'N/A')}")
        append_tag_value(meta, 'Guest name', room.get('guest_name'))
        append_tag_value(meta, 'Number of guests', room.get('nr_guests'))
        append_tag_value(meta, 'Cancelled', room.get('is_cancelled'))

        cancel_date = convert_plist_date_to_utc(room.get('cancel_date'))
        append_tag_value(meta, 'Cancel date', cancel_date)
        append_tag_value(meta, 'Identifier', room.get('room_id'))
        append_tag_value(meta, 'URL photo', room.get('room_photo'))

        for j, photo in enumerate(room.get('room_photos', [])):
            append_tag_value(meta, f"URL photo #{j}", photo.get('url_original'))

        results.append(unordered_list(meta, html_format=html_format))

    separator = HTML_HORZ_RULE if html_format else f"{LINE_BREAK}{LINE_BREAK}"

    return separator.join(results)


def _format_booking_registration(val: dict, tz: str) -> tuple:
    """
    Format check-in and check-out information.
    """

    check_io = []
    for action in [ 'checkin', 'checkout' ]:
        date_val = val.get(action)
        if date_val:
            prefix = 'Check-in' if action == 'checkin' else 'Check-out'
            time_str = format_check_in_out(
                val.get(f"{action}_from_epoch"),
                val.get(f"{action}_until_epoch"),
                tz=tz
            )
            check_io.append(f"{prefix}: {date_val.strftime('%Y-%m-%d')} {time_str}")

    return unordered_list(check_io), unordered_list(check_io, html_format=True)


@artifact_processor
def booking_booked(context):
    """
    Extract full booking confirmations and room details.
    """

    data_headers = (
        ('Created', 'datetime'),
        'Hotel ID',
        'Hotel Name',
        'Full Address',
        'Time Zone',
        'Check-In/Out (Hotel Time Zone)',
        'Hotel Contacts',
        'Confirmation Number/PIN Code',
        'Total Price',
        'Number of Rooms',
        'Rooms',
        'Booker Details',
        'Source',
        ('Attachment', 'media'),
        'Source File Name',
        'Location'
    )

    data_list = []
    data_list_html = []

    booking_app_id = get_booking_app_id(context)

    for file_found in context.get_files_found():
        file_found = str(file_found)

        # Check for BookingClouds (with or without .plist)
        if not (file_found.endswith('BookingClouds') or
                file_found.endswith('BookingClouds.plist')):
            continue

        try:
            plist_data = get_plist_file_content(file_found)
            if not plist_data:
                continue

            device_path = get_device_file_path(file_found, context)

            for root_key in ['DeviceBookings', 'AccountBookings']:
                bookings = plist_data.get(root_key, {})
                if not isinstance(bookings, dict):
                    continue

                for key, val in bookings.items():
                    # Address and Contacts
                    full_addr = COMMA_SEP.join(
                        filter(None, [val.get('hotel_full_address'), val.get('hotel_country_name')])
                    )
                    tz = val.get('hotel_timezone')

                    contacts = []
                    append_tag_value(contacts, 'Telephone', val.get('hotel_telephone'))
                    append_tag_value(contacts, 'Email', val.get('hotel_email'))

                    # Identifiers and Pricing
                    conf_info = []
                    append_tag_value(conf_info, 'Confirmation number', val.get('id'))
                    append_tag_value(conf_info, 'Pin code', val.get('pincode'))
                    price = (
                        f"{val.get('user_selected_currency_code')} "
                        f"{val.get('totalprice', 0):.2f}"
                    )

                    # Booker info
                    booker = []
                    append_tag_value(booker, 'First name', val.get('booker_firstname'))
                    append_tag_value(booker, 'Last name', val.get('booker_lastname'))
                    append_tag_value(booker, 'Email', val.get('booker_email'))
                    append_tag_value(booker, 'CC Last 4', val.get('cc_number_last_digits'))

                    # Attachment handling
                    src_files = [ device_path ]
                    booking_pdf = f"Booking #{key}.pdf"
                    media_path = f"{booking_app_id}/Documents/{booking_pdf}"
                    media_ref_id = None
                    src_file_path = get_device_file_path(media_path, context)
                    # Ensure the path exists and is not just the fallback input
                    if src_file_path and src_file_path != media_path:
                        media_ref_id = check_in_media(media_path, booking_pdf)
                        if media_ref_id:
                            src_files.append(src_file_path)

                    # Format complex fields
                    reg_p, reg_h = _format_booking_registration(val, tz)
                    rooms_list = val.get('room', [])

                    # Standard row data
                    base_data = (
                        convert_plist_date_to_utc(val.get('created_epoch')),
                        val.get('hotel_id'),
                        val.get('hotel_name'),
                        full_addr,
                        tz,
                        None,                                   # 5 Registration (Placeholder)
                        unordered_list(contacts),
                        unordered_list(conf_info),
                        price,
                        len(rooms_list),
                        None,                                   # 10 Rooms (Placeholder)
                        unordered_list(booker),
                        val.get('source'),
                        media_ref_id,
                        None,                                   # 14 Source Files (Placeholder)
                        f"[{root_key}][{key}]"
                    )

                    # HTML row
                    html_row = list(base_data)
                    html_row[5] = reg_h
                    html_row[10] = _get_room_details(rooms_list, html_format=True)
                    html_row[14] = unordered_list(src_files, html_format=True)
                    data_list_html.append(tuple(html_row))

                    # LAVA row
                    lava_row = list(base_data)
                    lava_row[5] = reg_p
                    lava_row[10] = _get_room_details(rooms_list)
                    lava_row[14] = unordered_list(src_files)
                    data_list.append(tuple(lava_row))

            # Stop the parser if data was successfully extracted from
            # either the legacy or the modern version of the file.
            if data_list:
                break

        except (KeyError, TypeError, IndexError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Malformed structure in {file_found}: {ex}")
        except OSError as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Could not read {file_found}: {ex}")

    return data_headers, (data_list, data_list_html), SOURCE_PATH_NOTE


@artifact_processor
def booking_wish_lists(context):
    """
    Extract hotel wish lists from Booking.com recents plist.
    """

    data_headers = (
        ('Added', 'datetime'),
        'Title', 'Hotel ID',
        'Location'
    )

    data_list = []
    source_path = ''

    for file_found in context.get_files_found():
        file_found = str(file_found)

        # Check for KeyValueStorageRecentsDomain (with or without .plist)
        if not (file_found.endswith('KeyValueStorageRecentsDomain') or
                file_found.endswith('KeyValueStorageRecentsDomain.plist')):
            continue

        try:
            source_path = file_found

            plist_data = get_plist_file_content(source_path)
            if not plist_data:
                continue

            wish_lists = plist_data.get('wishlists', []) if plist_data else []

            for i, wish in enumerate(wish_lists):
                list_name = wish.get('name')
                hotels = wish.get('hotels', [])

                for j, hotel in enumerate(hotels):
                    added = convert_plist_date_to_utc(hotel.get('date'))
                    hotel_id = hotel.get('id')

                    # Precise location within the plist structure for validation
                    location = f"[wishlists][{i}], [wishlists][{i}][hotels][{j}]"

                    # LAVA row
                    data_list.append((added, list_name, hotel_id, location))

            # Stop the parser if data was successfully extracted from
            # either the legacy or the modern version of the file.
            if data_list:
                break

        except (KeyError, TypeError, IndexError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Malformed structure in {file_found}: {ex}")
        except OSError as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Could not read {file_found}: {ex}")

    return data_headers, data_list, source_path


@artifact_processor
def booking_viewed(context):
    """
    Extract recently viewed hotels from Booking.com storage.
    """

    data_headers = (
        ('Last Viewed', 'datetime'),
        'Hotel Type',
        'Hotel ID',
        'Hotel Name',
        'Address',
        'City',
        'Region',
        'Zip Code',
        'Latitude',
        'Longitude',
        'Image URL',
        'Website',
        'Location'
    )

    data_list = []
    data_list_html = []
    source_path = ''

    for file_found in context.get_files_found():
        file_found = str(file_found)

        # Check for KeyValueStorageRecentsDomain (with or without .plist)
        if not (file_found.endswith('KeyValueStorageRecentsDomain') or
                file_found.endswith('KeyValueStorageRecentsDomain.plist')):
            continue

        try:
            source_path = file_found

            plist_data = get_plist_file_content(source_path)
            if not plist_data:
                continue

            viewed = plist_data.get('viewed', {}) if plist_data else {}

            for key, value in viewed.items():
                hotel = value.get('hotel', {})
                if not hotel:
                    continue

                # Basic Info
                last_viewed = convert_plist_date_to_utc(hotel.get('lastViewed'))
                h_type = hotel_type_names(hotel.get('hotel_type'))

                # City and Region logic: checks 'city' dict first, then flattens to root keys
                city_data = hotel.get('city', {}) or {}
                city_name = city_data.get('string_', hotel.get('cityName'))
                region_name = city_data.get('region_name', hotel.get('region_name'))

                # URLs
                p_url = hotel.get('pictureURL')
                web_url = hotel.get('hotelURL')

                # Standard row data
                base_data = (
                    last_viewed,
                    h_type,
                    hotel.get('hotel_id'),
                    hotel.get('name'),
                    hotel.get('address'),
                    city_name,
                    region_name,
                    hotel.get('zip'),
                    hotel.get('latitude'),
                    hotel.get('longitude'),
                    None,                                   # 10 URL (Placeholder)
                    None,                                   # 11 Website (Placeholder)
                    f"[viewed][{key}]"
                )

                # HTML row
                html_row = list(base_data)
                html_row[10] = format_url(p_url, html_format=True)
                html_row[11] = format_url(web_url, html_format=True)
                data_list_html.append(tuple(html_row))

                # LAVA row
                lava_row = list(base_data)
                lava_row[10] = p_url
                lava_row[11] = web_url
                data_list.append(tuple(lava_row))

            # Stop the parser if data was successfully extracted from
            # either the legacy or the modern version of the file.
            if data_list:
                break

        except (KeyError, TypeError, IndexError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Malformed structure in {file_found}: {ex}")
        except OSError as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Could not read {file_found}: {ex}")

    return data_headers, (data_list, data_list_html), source_path


@artifact_processor
def booking_notifications(context):
    """
    Extract notification history from Booking.com SQLite database.
    """

    data_headers = (
        ('Timestamp', 'datetime'),
        'Identifier',
        'Title',
        'Message',
        'Viewed',
        'Deleted',
        'Action ID',
        'Action Arguments',
        'Location'
    )

    data_list = []

    source_path = context.get_source_file_path('NotificationsModel.sqlite')

    query = '''
    SELECT
        ROWID,
        (ZDATE + 978307200) AS timestamp,
        ZIDENTIFIER,
        ZTITLE,
        ZBODY,
        ZVIEWED,
        ZLOCALLYDELETED,
        ZACTIONIDENTIFIER,
        ZACTIONARGUMENTS
    FROM ZNOTIFICATION
    '''

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        (
            row_id, ts_val, identifier, title, body,
            viewed, deleted, action_id, blob_args
         ) = record

        try:
            # Convert timestamps to UTC
            timestamp = convert_unix_ts_to_utc(ts_val)

            args_content = get_plist_content(blob_args) if blob_args else ''

            # Reference to the source table and row
            location = f"ZNOTIFICATION (ROWID: {row_id})"

            # LAVA row
            data_list.append((
                timestamp, identifier,
                title, body,
                "Yes" if viewed else "No",
                "Yes" if deleted else "No",
                action_id, args_content,
                location
            ))

        except (IndexError, TypeError, ValueError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Failed parsing record ZNOTIFICATION ROWID {record[0]} in "
                    f"{source_path}: {ex}")
            continue

    return data_headers, data_list, source_path


def _format_traveller_details(details: dict, html_format: bool = False) -> str:
    """
    Extract and format passenger information.
    """

    if not isinstance(details, dict) or not details:
        return ''

    meta = []
    append_tag_value(meta, 'Adults count', details.get('adultsCount'))
    append_tag_value(meta, 'Children count', details.get('childrenCount'))

    ages = details.get('childrenAges', [])
    if ages:
        append_tag_value(meta, 'Children ages', COMMA_SEP.join(map(str, ages)))

    return unordered_list(meta, html_format=html_format)


def _format_airports(airports: list, section: str = 'Airport', html_format: bool = False) -> str:
    """
    Extract and format list of airports (source or destination).
    """

    if not isinstance(airports, list) or not airports:
        return ''

    results = []
    for i, airport in enumerate(airports):
        if not airport:
            continue

        meta = [f"{section} {i} - {airport.get('name', 'N/A')}"]
        append_tag_value(meta, 'City', airport.get('cityName'))
        append_tag_value(meta, 'Region', airport.get('regionName'))
        append_tag_value(meta, 'Country', airport.get('countryName'))
        append_tag_value(meta, 'Type', airport.get('type'))
        append_tag_value(meta, 'Code', airport.get('code'))
        append_tag_value(meta, 'Selected', airport.get('selected'))

        results.append(unordered_list(meta, html_format=html_format))

    sep = HTML_HORZ_RULE if html_format else f"{LINE_BREAK}{LINE_BREAK}"

    return sep.join(results)


def _format_routes(routes: list, html_format: bool = False) -> str:
    """
    Extract and format flight routes with dates and airports.
    """

    if not isinstance(routes, list) or not routes:
        return ''

    results = []
    for i, route in enumerate(routes):
        try:
            r_date = date(route.get('startYear'), route.get('startMonth'), route.get('startDay'))
            meta = [f"Route {i} - {r_date}"]

            # Nested airport formatting
            meta.append(
                _format_airports(route.get('sourceAirports'),
                'Source airport', html_format
            ))
            meta.append(
                _format_airports(route.get('destinationAirports'),
                'Destination airport', html_format
            ))

            results.append(unordered_list(meta, html_format=html_format))
        except (TypeError, ValueError):
            continue

    sep = HTML_HORZ_RULE if html_format else f"{LINE_BREAK}{LINE_BREAK}"

    return sep.join(results)


def _get_safe_date(params, prefix):
    """
    Safely builds a date object. Logs errors if data is present but malformed.
    """

    try:
        y = params.get(f"{prefix}Year")
        m = params.get(f"{prefix}Month")
        d = params.get(f"{prefix}Day")

        # Only attempt conversion if all fields are present to avoid spamming logs for missing dates
        if all(v is not None for v in (y, m, d)):
            return date(int(y), int(m), int(d))

    except (TypeError, ValueError) as e:
        # logfunc is the standard logger in iLEAPP/aLEAPP frameworks
        logfunc(f"[_get_safe_date] Error parsing {prefix} date with values ({y}, {m}, {d}): {e}")

    return None


@artifact_processor
def booking_flights_searched(context):
    """
    Extract flight search history from JSON storage.
    """

    data_headers = (
        ('Last Updated', 'datetime'),
        'Start Date',
        'Return Date',
        'Direct Flight',
        'Search Type',
        'Cabin Class',
        'Source Airports',
        'Destination Airports',
        'Routes',
        "Travellers' Details",
        'Location'
    )

    data_list = []
    data_list_html = []
    source_path = ''

    for file_found in context.get_files_found():
        file_found = str(file_found)

        # Check for flight_rs_v2
        if not file_found.endswith('flight_rs_v2'):
            continue

        try:
            source_path = file_found

            json_data = get_json_file_content(source_path)
            if not json_data:
                continue

            flights = json_data.get('value', [])

            for i, flight in enumerate(flights):
                # Convert timestamps to UTC
                last_updated = convert_iso8601_to_utc(flight.get('lastUpdated'))

                params = flight.get('parameters', {}).get('searchOptionModel', {})

                # Refactored date parsing
                start_dt = _get_safe_date(params, 'start')
                return_dt = _get_safe_date(params, 'return')

                # Standard row data
                base_data = (
                    last_updated,
                    start_dt,
                    return_dt,
                    params.get('direct'),
                    params.get('searchType'),
                    params.get('cabin'),
                    None,                                   # 6 Source Airports (Placeholder)
                    None,                                   # 7 Destination Airports (Placeholder)
                    None,                                   # 8 Routes (Placeholder)
                    None,                                   # 9 Travellers' Details (Placeholder)
                    f"[value][{i}]"
                )

                # HTML row
                html_row = list(base_data)
                html_row[6] = _format_airports(params.get('sourceAirports'), html_format=True)
                html_row[7] = _format_airports(params.get('destinationAirports'), html_format=True)
                html_row[8] = _format_routes(params.get('routes'), html_format=True)
                html_row[9] = _format_traveller_details(params.get('travellersDetails'),
                    html_format=True)
                data_list_html.append(tuple(html_row))

                # LAVA row
                lava_row = list(base_data)
                lava_row[6] = _format_airports(params.get('sourceAirports'))
                lava_row[7] = _format_airports(params.get('destinationAirports'))
                lava_row[8] = _format_routes(params.get('routes'))
                lava_row[9] = _format_traveller_details(params.get('travellersDetails'))
                data_list.append(tuple(lava_row))

        except (KeyError, TypeError, IndexError) as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Malformed structure in {file_found}: {ex}")
        except OSError as ex:
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Could not read {file_found}: {ex}")

    return data_headers, (data_list, data_list_html), source_path
