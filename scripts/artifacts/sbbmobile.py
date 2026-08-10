__artifacts_v2__ = {
    "sbb_searchhistory": {
        "name": "SBB Mobile - Search History",
        "description": "Parse search history in the SBB Mobile app",
        "author": "jonah.osterwalder@vd.ch",
        "creation_date": "2026-03-18",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Travel",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/ch.sbb.coredata.searchhistory.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "search"
    },
    "sbb_easyride_trips": {
        "name": "SBB Mobile - EasyRide Trips",
        "description": "Parse EasyRide check-in and check-out events",
        "author": "jonah.osterwalder@vd.ch",
        "creation_date": "2026-03-23",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Travel",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/ch.sbb.coredata.logs.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "map"
    },
    "sbb_purchased_tickets": {
        "name": "SBB Mobile - Purchased Tickets",
        "description": "Parse purchased tickets from SbbMobile",
        "author": "jonah.osterwalder@vd.ch",
        "creation_date": "2026-03-24",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Travel",
        "notes": "Refund-state values other than COMPLETE are reported as stored.",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/SbbMobile.db*'),
        "output_types": "standard",
        "artifact_icon": "star"
    }
}


from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, logfunc
from bs4 import BeautifulSoup


@artifact_processor
def sbb_searchhistory(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "ch.sbb.coredata.searchhistory.sqlite")
    data_list = []

    if not source_path:
        logfunc('No ch.sbb.coredata.searchhistory.sqlite database found')
        return

    query = """
        SELECT	
            datetime(ZTIMESTAMP / 1000, 'unixepoch'),
            ZFROM,
            ZFROMTYPE,
            ZTO,
            ZTOTYPE,
            ZLAT,
            ZLON
        FROM ZSEARCHRESULT
    """

    data_headers = (
        ('Search timestamp (UTC)','datetime'),
        'Departure', 
        'Departure type', 
        'Target', 
        'Target type', 
        'Result Coordinates (lat/lon)',
    )

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:

        # Coordinates as text
        if record[5] and record[6]:
            map_link = coordinate_to_text(record[5]/1_000_000, record[6]/1_000_000)
        else:
            map_link = ""

        data_list.append(record[:5] + (map_link,))

    return data_headers, data_list, source_path


@artifact_processor
def sbb_easyride_trips(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "ch.sbb.coredata.logs.sqlite")
    data_list = []

    if not source_path:
        logfunc("No ch.sbb.coredata.logs.sqlite database found")
        return

    query = '''
        SELECT 
            ZTIMESTAMP,
            ZMESSAGE,
            datetime(ZTIMESTAMP + 978307200, 'unixepoch')
        FROM ZLOGENTRY
        ORDER BY ZTIMESTAMP ASC
    '''

    data_headers = (
        ('Check-in Time (UTC)', 'datetime'),
        'Check-out Time (UTC)',
        'Duration (min)',
    )

    records = get_sqlite_db_records(source_path, query)

    current_checkin = None
    checkin_timestamp = None

    for record in records:
        timestamp = record[0]
        message = record[1]
        timestamp_str = record[2]

        # Detect checkin / checkout 
        CHECKIN_MESSAGES = (
            "EasyRide slider on the right, starting check-in process",
            "Fairtiq state update: [checkingIn]",
        )

        CHECKOUT_MESSAGES = (
            "EasyRide slider on the left, starting check-out process",
            "Fairtiq state update: [checkingOut]",
        )

        is_checkin = any(msg in message for msg in CHECKIN_MESSAGES)
        is_checkout = any(msg in message for msg in CHECKOUT_MESSAGES)

        if is_checkin:
            # previous checkin without checkout → Unknown checkout
            if current_checkin:
                data_list.append((current_checkin, "Unknown", "Unknown"))

            current_checkin = timestamp_str
            checkin_timestamp = timestamp

        elif is_checkout:
            if current_checkin:
                # calculate duration in minutes if both times known
                if checkin_timestamp and timestamp:
                    duration = round((timestamp - checkin_timestamp)/ 60, 1)
                else:
                    duration = "Unknown"

                data_list.append((current_checkin, timestamp_str, duration))
                current_checkin = None
                checkin_timestamp = None
            else:
                # checkout without preceding checkin
                data_list.append(("Unknown", timestamp_str, "Unknown"))

    # if last trip has no checkout
    if current_checkin:
        data_list.append((current_checkin, "Unknown", "Unknown"))

    return data_headers, data_list, source_path


@artifact_processor
def sbb_purchased_tickets(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "SbbMobile.db")
    data_list = []

    if not source_path:
        logfunc("No SbbMobile database found")
        return

    query = '''
        SELECT
            traveler,
            validFrom,
            validUntil,
            CASE
                WHEN refundState = 'COMPLETE' THEN 'Refunded'
                ELSE refundState
            END AS refundState,
            paymentMethodType,
            displayInfo_ticketType,
            screenTicket_contentHtml
        FROM PurchasedTickets
    '''

    db_records = get_sqlite_db_records(source_path, query)

    data_headers = (
        "Traveler",
        "Valid from",
        "Valid until",
        "is Refunded",
        "Payment method",
        "Ticket description",
        "Purchase Time",
        "Departure",
        "Target",
        "Zones",
        )

    for record in db_records:
        html = record[-1]
        parsed = parse_ticket_html(html)

        data_list.append(
            record[:6] + (parsed["purchase_time"], parsed["departure"], parsed["target"], parsed["zones"])
            )

    return data_headers, data_list, source_path


def parse_ticket_html(html):

    soup = BeautifulSoup(html, "html.parser")

    def get_text(class_name):
        el = soup.find(class_=class_name)
        return el.get_text(strip=True) if el else ""

    def get_first_value(selector):
        el = soup.select_one(selector)
        return el.get_text(strip=True) if el else ""

    data = {}

    data["purchase_time"] = get_first_value(".ticketinformationen .item .value")
    data["departure"] = get_text("abgang")
    data["target"] = get_text("bestimmung")
    data["zones"] = get_text("zonen")

    return data


def coordinate_to_text(lat, lon):
    """Return the coordinates as text.

    This built an openstreetmap.org URL. A report links to nothing outside its own
    folder, so the coordinates are reported as the data they are.
    """
    return f"{lat}, {lon}"
