""" uberPlaces """
__artifacts_v2__ = {
    "uber_places": {
        "name": "Uber - Places",
        "description": "Parses Uber Places Database",
        "author": "Heather Charpentier, @JamesHabben",
        "creation_date": "2024-04-10",
        "last_update_date": "2026-06-08",
        "requirements": "none",
        "category": "Uber",
        "notes": "",
        "paths": ('*/Documents/database.db*',), # shorter path for itunes backups also
        "output_types": "all",
        "artifact_icon": "map-pin"
    }
}

from datetime import datetime
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, open_sqlite_db_readonly

@artifact_processor
def uber_places(context):
    """ see artifact description """
    data_list = []
    found_files = context.get_files_found()
    file_found = ''

    for file_found in found_files:
        file_found = str(file_found)

        if file_found.endswith('database.db'):
            # Check if it's the right database before querying to avoid log noise
            db = open_sqlite_db_readonly(file_found)
            if db:
                cursor = db.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='place'")
                table_exists = cursor.fetchone()
                db.close()

                if not table_exists:
                    continue

            query = '''
            SELECT
            timestamp_ms, 
            json_extract(place.place_result, '$.payload.personalPreferencesPayload.preferredVehicles[0].lastUsedTimeMillis') as Last_Used,
            json_extract(place.place_result, '$.payload.personalPayload.id') as Personal_ID,
            title_segment,
            subtitle_segment,
            COALESCE(latitude, latitude_v2) as Latitude,
            COALESCE(longitude, longitude_v2) as Longitude,
            historical,
            json_extract(place.place_result, '$.location.categories') as Categories,
            json_extract(place.place_result, '$.payload.locationPayload.distanceMeters') as Distance_Meters,
            json_extract(place.place_result, '$.location.accessPoints[0].attachments.distance_to_target') as Distance_To_Target,
            tag,
            json_extract(place.place_result, '$.location.accessPoints[0].usage') as Usage,
            json_extract(place.place_result, '$.location.accessPoints[0].attachments.tripCount') as Trip_Count,
            json_extract(place.place_result, '$.location.provider') as Provider
            FROM place
            '''

            db_records = get_sqlite_db_records(file_found, query)
            for row in db_records:
                # Timestamp handling with sub-second precision (float)
                # Note: timestamp_ms in this table appears to be in seconds despite the name
                timestamp = row[0]

                last_used = row[1]
                if last_used:
                    if isinstance(last_used, (int, float)):
                        last_used = last_used / 1000.0
                    elif isinstance(last_used, str):
                        try:
                            # Try to convert ISO string to float timestamp for sub-second precision
                            last_used = datetime.fromisoformat(last_used.replace('Z', '+00:00')).timestamp()
                        except ValueError:
                            # Fallback to cleaned string if conversion fails
                            last_used = last_used.replace('T', ' ').replace('Z', '')

                data_list.append((
                    timestamp,
                    last_used,
                    row[2], # Personal ID
                    row[3], # Title
                    row[4], # Subtitle
                    row[5], # Latitude
                    row[6], # Longitude
                    row[7], # Historical
                    row[8], # Categories
                    row[9], # Distance Meters
                    row[10], # Distance To Target
                    row[11], # Tag
                    row[12], # Usage
                    row[13], # Trip Count
                    row[14], # Provider
                    context.get_relative_path(file_found)
                ))

    data_headers = (
        ('Timestamp', 'datetime'),
        ('Last Used', 'datetime'),
        'Personal ID',
        'Title',
        'Subtitle',
        'Latitude',
        'Longitude',
        'Historical',
        'Categories',
        'Distance (Meters)',
        'Distance To Target',
        'Tag',
        'Usage',
        'Trip Count',
        'Provider',
        'Source File'
    )

    return data_headers, data_list, file_found
