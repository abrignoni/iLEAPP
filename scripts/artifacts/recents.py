"""
Recents Artifact Module

Parses and extracts Recents iOS db located at 
/private/var/mobile/Library/Recents/Recents

References:
https://www.linkedin.com/posts/rebus_hidden-gems-in-apple-ios-digital-forensics-share-7179865959761920000-rFhj/

"""
__artifacts_v2__ = {
    "readRecents": {
        "name": "Recent contacts and locations",
        "description": "Recent contact and location information from Apple apps",
        "author": "Yogesh Khatri (@swiftforensics)",
        "creation_date": "2026-07-27",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "Recents",
        "notes": "dates are stored as unixepoch milliseconds in UTC",
        "paths": ('*/var/mobile/Library/Recents/Recents*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 69 rows",
            "iphone14plus_ios18": "iOS 18.0 | 8 rows",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_sqlite_db_records,get_plist_content, \
    convert_unix_ts_to_str, convert_unix_ts_to_utc
from pprint import pformat

query_recents = """
    SELECT recents.display_name, --contacts.display_name, 
        recents.bundle_identifier, recents.sending_address, 
        recents.original_source, recents.dates, 
        recents.last_date, recents.weight, recents.count, recents.group_kind,
        contacts.address, contacts.kind,
        metadata.key, metadata.value, recents.ROWID
    FROM recents LEFT JOIN contacts ON recents.ROWID=contacts.recent_id
                 LEFT JOIN metadata on recents.ROWID=metadata.recent_id
    """

def process_plist_value(value):
    """
    Process the plist value and return a formatted string representation.
    """
    if not value:
        return ''

    # check for plist content
    if isinstance(value, bytes) and (value.startswith(b'<?xml') or value.startswith(b'bplist')):
        plist_content = get_plist_content(value)
        if plist_content:
            value = plist_content
            while isinstance(value, bytes) and (value.startswith(b'<?xml') or value.startswith(b'bplist')):
                value = get_plist_content(value)

            return pformat(value)
        else:
            return ''
    else:
        return value

@artifact_processor
def readRecents(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'Recents')
    data_list = []

    data_headers = (
        'Display Name',
        'Bundle Identifier',
        'Sending Address',
        'Original Source',
        'Dates',
        ('Last Date', 'datetime'),
        'Weight',
        'Count',
        'Group Kind',
        'Contact Address',
        'Contact Kind',
        'ROWID',
        'Metadata'
    )

    db_records = get_sqlite_db_records(source_path, query_recents)

    last_rowid = None
    current_data = None
    metadata = {}
    for record in db_records:
        current_rowid = record['ROWID']
        if current_rowid != last_rowid:
            # new row
            if current_data:
                current_data.append(pformat(metadata))
                data_list.append(current_data)
                current_data = []
                metadata = {}
            last_rowid = current_rowid
            # parse dates for new row
            last_date = convert_unix_ts_to_utc(record['last_date']/1000) if record['last_date'] else ''
            dates = record['dates']
            if dates:
                dates = dates.split(':')
                for i in range(len(dates)):
                    try:
                        int_date = int(dates[i])
                        dates[i] = convert_unix_ts_to_str(int_date/1000)
                    except ValueError:
                        pass                
                dates = ', '.join(dates)
            else:
                dates = ''

            current_data = [record[0], record[1], record[2], record[3], dates, last_date, 
                            record[6], record[7], record[8], record[9], record[10], record[13]]
            val = process_plist_value(record['value']) if record['key'] else ''
            if record['key'] and val:
                metadata[record['key']] = val
        else:
            # same row, add metadata
            if record['key']:
                val = process_plist_value(record['value'])
                if val:
                    metadata[record['key']] = val
    if current_data:
        current_data.append(pformat(metadata))
        data_list.append(current_data)

    return data_headers, data_list, source_path