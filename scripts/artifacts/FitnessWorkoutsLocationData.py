__artifacts_v2__ = {
    "fitnessWorkoutsAnalysis": {
        "name": "Fitness Workouts Location Data Analysis",
        "description": "Per-workout location-capture analysis from healthdb_secure.sqlite "
                       "(point counts vs expected, capture timespan/average, workout type and times)",
        "author": "@SQLMcGee",
        "creation_date": "2023-05-22",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Fitness",
        "notes": "Queries derived from research by James McGee, Metadata Forensics, LLC — 'Apple Fitness "
                 "Workout Location Data: Leveraging the healthdb_secure.sqlite Database' "
                 "(https://tinyurl.com/4zyd6z9n). Timestamps are UTC. Elapsed/Workout/Timespan columns are "
                 "HH:MM:SS durations, not absolute times.",
        "paths": ('*Health/healthdb_secure.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "activity"
    },
    "fitnessWorkoutsLocation": {
        "name": "Fitness Workouts Location Data",
        "description": "Per-point GPS location data captured during Apple Fitness workouts "
                       "(healthdb_secure.sqlite)",
        "author": "@SQLMcGee",
        "creation_date": "2023-05-22",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Fitness",
        "notes": "Queries derived from research by James McGee, Metadata Forensics, LLC — 'Apple Fitness "
                 "Workout Location Data: Leveraging the healthdb_secure.sqlite Database' "
                 "(https://tinyurl.com/4zyd6z9n). Timestamps are UTC. Vertical, Speed, and Course Accuracy "
                 "values also exist in the table but are not surfaced.",
        "paths": ('*Health/healthdb_secure.sqlite*',),
        "output_types": "all",
        "artifact_icon": "map-pin"
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, does_table_exist_in_db

_ACTIVITY_TYPE_CASE = '''CASE activity_type
    WHEN 1 THEN "American Football"
    WHEN 2 THEN "Archery"
    WHEN 3 THEN "Australian Football"
    WHEN 4 THEN "Badminton"
    WHEN 5 THEN "Baseball"
    WHEN 6 THEN "Basketball"
    WHEN 7 THEN "Bowling"
    WHEN 8 THEN "Boxing"
    WHEN 9 THEN "Climbing"
    WHEN 10 THEN "Cricket"
    WHEN 11 THEN "Cross Training"
    WHEN 12 THEN "Curling"
    WHEN 13 THEN "Indoor/Outdoor Cycle"
    WHEN 16 THEN "Elliptical"
    WHEN 17 THEN "Equestrian Sports"
    WHEN 18 THEN "Fencing"
    WHEN 19 THEN "Fishing"
    WHEN 20 THEN "Functional Strength Training"
    WHEN 21 THEN "Golf"
    WHEN 22 THEN "Gymnastics"
    WHEN 23 THEN "Handball"
    WHEN 24 THEN "Hiking"
    WHEN 25 THEN "Hockey"
    WHEN 26 THEN "Hunting"
    WHEN 27 THEN "Lacrosse"
    WHEN 28 THEN "Martial Arts"
    WHEN 29 THEN "Mind and Body"
    WHEN 31 THEN "Paddling"
    WHEN 32 THEN "Play"
    WHEN 33 THEN "Rolling"
    WHEN 34 THEN "Racquetball"
    WHEN 35 THEN "Rower"
    WHEN 36 THEN "Rugby"
    WHEN 37 THEN "Outdoor Run"
    WHEN 38 THEN "Sailing"
    WHEN 39 THEN "Skating"
    WHEN 40 THEN "Snow Sports"
    WHEN 41 THEN "Soccer"
    WHEN 42 THEN "Softball"
    WHEN 43 THEN "Squash"
    WHEN 44 THEN "Stair Stepper"
    WHEN 45 THEN "Surfing"
    WHEN 46 THEN "Pool/Open Water Swim"
    WHEN 47 THEN "Table Tennis"
    WHEN 48 THEN "Tennis"
    WHEN 49 THEN "Track and Field"
    WHEN 50 THEN "Traditional Strength Training"
    WHEN 51 THEN "Volleyball"
    WHEN 52 THEN "Outdoor/Indoor Walk"
    WHEN 53 THEN "Water Fitness"
    WHEN 54 THEN "Water Polo"
    WHEN 55 THEN "Water Sports"
    WHEN 56 THEN "Wrestling"
    WHEN 57 THEN "Yoga"
    WHEN 58 THEN "Barre"
    WHEN 59 THEN "Core Training"
    WHEN 60 THEN "Cross Country Skiing"
    WHEN 62 THEN "Flexibility"
    WHEN 63 THEN "High Intensity Interval Training"
    WHEN 64 THEN "Jump Rope"
    WHEN 65 THEN "Kickboxing"
    WHEN 66 THEN "Pilates"
    WHEN 67 THEN "Snowboarding"
    WHEN 68 THEN "Stairs"
    WHEN 69 THEN "Step Training"
    WHEN 72 THEN "Tai Chi"
    WHEN 73 THEN "Mixed Cardio"
    WHEN 74 THEN "Hand Cycling"
    WHEN 75 THEN "Disc Sports"
    WHEN 76 THEN "Fitness Gaming"
    WHEN 77 THEN "Dance"
    WHEN 78 THEN "Social Dance"
    WHEN 79 THEN "Pickleball"
    WHEN 80 THEN "Cooldown"
    WHEN 3000 THEN "Other"
    ELSE "Undefined"
    END'''


def _find_healthdb(context):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('healthdb_secure.sqlite'):
            return file_found
    return ''


def _has_required_tables(db_path):
    return (does_table_exist_in_db(db_path, 'location_series_data')
            and does_table_exist_in_db(db_path, 'associations'))


@artifact_processor
def fitnessWorkoutsAnalysis(context):
    data_headers = (
        ('Workout Start Time', 'datetime'), ('Min Location Timestamp', 'datetime'),
        ('Workout End Time', 'datetime'), ('Max Location Timestamp', 'datetime'),
        'Number of Location Points', 'Expected Number of Location Points', 'Workout Type',
        'Elapsed Time', 'Workout Time', 'Location Data Capture Timespan',
        'Location Data Capture Average (in Seconds)')
    data_list = []

    db_path = _find_healthdb(context)
    if not db_path or not _has_required_tables(db_path):
        return data_headers, data_list, ''

    query = f'''
    SELECT
        datetime(workout_activities.start_date + 978307200, 'UNIXEPOCH'),
        min(datetime(location_series_data.timestamp + 978307200, 'UNIXEPOCH')),
        datetime(workout_activities.end_date + 978307200, 'UNIXEPOCH'),
        max(datetime(location_series_data.timestamp + 978307200, 'UNIXEPOCH')),
        data_series.count,
        round(((workout_activities.end_date - workout_activities.start_date) * ((max(location_series_data.timestamp) - min(location_series_data.timestamp)) / data_series.count))),
        {_ACTIVITY_TYPE_CASE},
        substr(datetime((workout_activities.end_date - workout_activities.start_date) + 978307200, 'UNIXEPOCH'),12,8),
        substr(datetime(workout_activities.duration + 978307200, 'UNIXEPOCH'),12,8),
        substr((datetime((max(location_series_data.timestamp) - min(location_series_data.timestamp)) + 978307200, 'UNIXEPOCH')),12,8),
        substr(((max(location_series_data.timestamp) - min(location_series_data.timestamp)) / data_series.count),1,5)
        FROM location_series_data
        LEFT OUTER JOIN data_series on data_series.hfd_key = location_series_data.series_identifier
        LEFT OUTER JOIN associations on associations.child_id = data_series.data_id
        LEFT OUTER JOIN workout_activities on workout_activities.owner_id = associations.parent_id
        GROUP BY location_series_data.series_identifier
        ORDER BY workout_activities.start_date
    '''
    for row in get_sqlite_db_records(db_path, query):
        data_list.append(tuple(row))

    return data_headers, data_list, context.get_relative_path(db_path)


@artifact_processor
def fitnessWorkoutsLocation(context):
    data_headers = (
        ('Timestamp', 'datetime'), 'Workout Type', 'Latitude', 'Longitude', 'Altitude', 'Speed',
        'Course', 'Horizontal Accuracy', 'Series Identifier')
    data_list = []

    db_path = _find_healthdb(context)
    if not db_path or not _has_required_tables(db_path):
        return data_headers, data_list, ''

    query = f'''
    SELECT
        datetime(timestamp+978307200,'unixepoch'),
        {_ACTIVITY_TYPE_CASE},
        latitude,
        longitude,
        substr(altitude,1,8),
        substr(speed,1,6),
        substr(course,1,6),
        substr(horizontal_accuracy,1,6),
        series_identifier
        FROM location_series_data
        LEFT OUTER JOIN data_series on data_series.hfd_key = location_series_data.series_identifier
        LEFT OUTER JOIN associations on associations.child_id = data_series.data_id
        LEFT OUTER JOIN workout_activities on workout_activities.owner_id = associations.parent_id
    '''
    for row in get_sqlite_db_records(db_path, query):
        data_list.append(tuple(row))

    return data_headers, data_list, context.get_relative_path(db_path)
