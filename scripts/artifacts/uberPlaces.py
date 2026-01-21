__artifacts_v2__ = {
    "get_uberPlaces": {
        "name": "Uber - Places",
        "description": "Parses Uber Places Database",
        "author": "Heather Charpentier",
        "creation_date":"2024-04-10",
        "last_update_date": "2025-11-28",
        "requirements": "none",
        "category": "Uber",
        "notes": "",
        "paths": ('**/Documents/database.db*',),
        "output_types": "standard",
        "artifact_icon": "map-pin"
    }
}

from scripts.ilapfuncs import (
    artifact_processor,
    get_file_path,
    get_sqlite_db_records,
    convert_unix_ts_to_utc,
    logfunc
)


@artifact_processor
def get_uberPlaces(context):
    files_found = context.get_files_found()
    data_list = []

    source_path = get_file_path(files_found, 'database.db')
    if not source_path:
        logfunc('Uber database.db not found')
        return (), [], ''

    query = '''
    SELECT
    timestamp_ms,
    json_extract(place.place_result, '$.payload.personalPreferencesPayload.preferredVehicles[0].lastUsedTimeMillis') as Last_Used,
    json_extract(place.place_result, '$.payload.personalPayload.id') as Uber_ID,
    json_extract(place.place_result, '$.payload.locationPayload.distanceMeters') as Distance_Meters,
    json_extract(place.place_result, '$.location.accessPoints[0].attachments.distance_to_target') as Distance_To_Target,
    json_extract(place.place_result, '$.location.coordinate.latitude') as Latitude,
    json_extract(place.place_result, '$.location.coordinate.longitude') as Longitude,
    json_extract(place.place_result, '$.location.name') as Name,
    json_extract(place.place_result, '$.location.fullAddress') as Related_Location,
    tag,
    json_extract(place.place_result, '$.location.accessPoints[0].usage') as Usage,
    json_extract(place.place_result, '$.location.accessPoints[0].attachments.tripCount') as Trip_Count,
    json_extract(place.place_result, '$.location.provider') as Provider
    FROM place
    '''

    db_records = get_sqlite_db_records(source_path, query)

    for row in db_records:
        timestamp = convert_unix_ts_to_utc(int(row[0])/1000) if row[0] else ''

        last_used = ''
        if row[1]:
            try:
                last_used_ms = float(row[1])
                last_used = convert_unix_ts_to_utc(last_used_ms/1000)
            except ValueError:
                last_used = row[1]

        data_list.append((
            timestamp,
            last_used,
            row[2], # Uber ID
            row[3], # Distance Meters
            row[4], # Distance To Target
            row[5], # Latitude
            row[6], # Longitude
            row[7], # Name
            row[8], # Related Location
            row[9], # Tag
            row[10], # Usage
            row[11], # Trip Count
            row[12]  # Provider
        ))

    data_headers = (
        ('Timestamp', 'datetime'),
        ('Last Used', 'datetime'),
        'Uber ID',
        'Distance (Meters)',
        'Distance To Target',
        'Latitude',
        'Longitude',
        'Place Name',
        'Place Address',
        'Tag',
        'Usage',
        'Trip Count',
        'Provider'
    )
    if not data_list:
        logfunc('No Uber - Places data available')
        return data_headers, [], source_path
    return data_headers, data_list, source_path
