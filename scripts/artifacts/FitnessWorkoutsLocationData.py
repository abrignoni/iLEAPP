__artifacts_v2__ = {
    "fitnessWorkoutsAnalysis": {
        "name": "Fitness Workouts Location Data Analysis",
        "description": "Per-workout location-capture analysis from healthdb_secure.sqlite (point "
                       "count, a computed duration by interval figure, capture timespan/average, "
                       "workout type and times)",
        "author": "@SQLMcGee, @AlexisBrignoni, Codex",
        "creation_date": "2023-05-22",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Fitness",
        "notes": "Queries derived from research by James McGee, Metadata Forensics, LLC, 'Apple "
                 "Fitness Workout Location Data: Leveraging the healthdb_secure.sqlite Database' "
                 "(https://drive.google.com/file/d/1BGY8kLUyMQaosn-eb3Di98CAZSc8ywBg/view, reached "
                 "through https://tinyurl.com/4zyd6z9n). Timestamps are read as seconds since "
                 "2001-01-01 and are shown as UTC. Elapsed Time and Location Data Capture "
                 "Timespan are numeric seconds computed from timestamp differences; duration "
                 "and activity_type are reported as stored without assigning names. The 'Duration x Avg Interval "
                 "(computed)' column is the product of the workout duration and the average "
                 "location capture interval as computed by the query.",
        "paths": ('*Health/healthdb_secure.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 20 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "fitnessWorkoutsLocation": {
        "name": "Fitness Workouts Location Data",
        "description": "Per-point location data in the location_series_data table "
                       "(healthdb_secure.sqlite), with the workout type where the series joins to a "
                       "workout row",
        "author": "@SQLMcGee, @AlexisBrignoni, Codex",
        "creation_date": "2023-05-22",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Fitness",
        "notes": "Queries derived from research by James McGee, Metadata Forensics, LLC, 'Apple "
                 "Fitness Workout Location Data: Leveraging the healthdb_secure.sqlite Database' "
                 "(https://drive.google.com/file/d/1BGY8kLUyMQaosn-eb3Di98CAZSc8ywBg/view, reached "
                 "through https://tinyurl.com/4zyd6z9n). Timestamps are read as seconds since "
                 "2001-01-01 and are shown as UTC. Vertical, Speed, and Course Accuracy values also "
                 "exist in the table but are not surfaced. Altitude, Speed, Course and "
                 "Horizontal Accuracy are reported as stored without truncation. activity_type "
                 "is reported as stored without assigning names; a missing workout yields a "
                 "blank value.",
        "paths": ('*Health/healthdb_secure.sqlite*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 25473 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, does_table_exist_in_db, does_column_exist_in_db, null_absent_columns




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
        'Number of Location Points', 'Duration x Avg Interval (computed)', 'activity_type (as stored)',
        'Elapsed Time (seconds)', 'duration (as stored)', 'Location Data Capture Timespan (seconds)',
        'Location Data Capture Average (in Seconds)')
    data_list = []
    db_path = _find_healthdb(context)
    if not db_path or not _has_required_tables(db_path):
        return data_headers, data_list, db_path

    associations_child_id_exists = does_column_exist_in_db(db_path, 'associations', 'child_id')

    if associations_child_id_exists:
        query = '''
        SELECT
            datetime(workout_activities.start_date + 978307200, 'UNIXEPOCH'),
            min(datetime(location_series_data.timestamp + 978307200, 'UNIXEPOCH')),
            datetime(workout_activities.end_date + 978307200, 'UNIXEPOCH'),
            max(datetime(location_series_data.timestamp + 978307200, 'UNIXEPOCH')),
            data_series.count,
            round(((workout_activities.end_date - workout_activities.start_date) * ((max(location_series_data.timestamp) - min(location_series_data.timestamp)) / data_series.count))),
            activity_type,
            (workout_activities.end_date - workout_activities.start_date),
            workout_activities.duration,
            (max(location_series_data.timestamp) - min(location_series_data.timestamp)),
            substr(((max(location_series_data.timestamp) - min(location_series_data.timestamp)) / data_series.count),1,5)
            FROM location_series_data
            LEFT OUTER JOIN data_series on data_series.hfd_key = location_series_data.series_identifier
            LEFT OUTER JOIN associations on associations.child_id = data_series.data_id
            LEFT OUTER JOIN workout_activities on workout_activities.owner_id = associations.parent_id
            GROUP BY location_series_data.series_identifier
            ORDER BY workout_activities.start_date
        '''
    else:
        query = '''
        SELECT
            datetime(workout_activities.start_date + 978307200, 'UNIXEPOCH'),
            min(datetime(location_series_data.timestamp + 978307200, 'UNIXEPOCH')),
            datetime(workout_activities.end_date + 978307200, 'UNIXEPOCH'),
            max(datetime(location_series_data.timestamp + 978307200, 'UNIXEPOCH')),
            data_series.count,
            round(((workout_activities.end_date - workout_activities.start_date) * ((max(location_series_data.timestamp) - min(location_series_data.timestamp)) / data_series.count))),
            activity_type,
            (workout_activities.end_date - workout_activities.start_date),
            workout_activities.duration,
            (max(location_series_data.timestamp) - min(location_series_data.timestamp)),
            substr(((max(location_series_data.timestamp) - min(location_series_data.timestamp)) / data_series.count),1,5)
            FROM location_series_data
            LEFT OUTER JOIN data_series on data_series.hfd_key = location_series_data.series_identifier
            LEFT OUTER JOIN associations on associations.source_object_id = data_series.data_id
            LEFT OUTER JOIN workout_activities on workout_activities.owner_id = associations.destination_object_id
            GROUP BY location_series_data.series_identifier
            ORDER BY workout_activities.start_date
        '''        
    # for row in get_sqlite_db_records(db_path, query):
    #     data_list.append(tuple(row))
    data_list = list( get_sqlite_db_records(db_path, null_absent_columns(db_path, query)) )

    return data_headers, data_list, context.get_relative_path(db_path)


@artifact_processor
def fitnessWorkoutsLocation(context):
    data_headers = (
        ('Timestamp', 'datetime'), 'activity_type (as stored)', 'Latitude', 'Longitude', 'Altitude', 'Speed',
        'Course', 'Horizontal Accuracy', 'Series Identifier')
    data_list = []
    db_path = _find_healthdb(context)
    if not db_path or not _has_required_tables(db_path):
        return data_headers, data_list, db_path

    associations_child_id_exists = does_column_exist_in_db(db_path, 'associations', 'child_id')
    
    if associations_child_id_exists:
        query = '''
        SELECT
            datetime(timestamp+978307200,'unixepoch'),
            activity_type,
            latitude,
            longitude,
            altitude,
            speed,
            course,
            horizontal_accuracy,
            series_identifier
            FROM location_series_data
            LEFT OUTER JOIN data_series on data_series.hfd_key = location_series_data.series_identifier
            LEFT OUTER JOIN associations on associations.child_id = data_series.data_id
            LEFT OUTER JOIN workout_activities on workout_activities.owner_id = associations.parent_id
        '''
    else:
        query = '''
        SELECT
            datetime(timestamp+978307200,'unixepoch'),
            activity_type,
            latitude,
            longitude,
            altitude,
            speed,
            course,
            horizontal_accuracy,
            series_identifier
            FROM location_series_data
            LEFT OUTER JOIN data_series on data_series.hfd_key = location_series_data.series_identifier
            LEFT OUTER JOIN associations on associations.source_object_id = data_series.data_id
            LEFT OUTER JOIN workout_activities on workout_activities.owner_id = associations.destination_object_id
        '''
    # for row in get_sqlite_db_records(db_path, query):
    #     data_list.append(tuple(row))
    data_list = list( get_sqlite_db_records(db_path, null_absent_columns(db_path, query)) )

    return data_headers, data_list, context.get_relative_path(db_path)
