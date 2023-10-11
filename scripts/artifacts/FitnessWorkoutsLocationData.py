# Module Description: Parses Apple Fitness Workouts Location Data and additional analysis data
# Author: @SQLMcGee
# Date: 2023-05-22

# Queries are a derivative of research provided by James McGee, Metadata Forensics, LLC, and 
# explained further in "Apple Fitness Workout Location Data: Leveraging the healthdb_secure.sqlite Database"
# available for review at https://tinyurl.com/4zyd6z9n

import sqlite3
import textwrap
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_Health(files_found, report_folder, seeker, wrap_text, timezone_offset):

    healthdb_secure = ''
    source_file_healthdb_secure = ''
   
    for file_found in files_found:
        file_name = str(file_found)
        if file_name.endswith('healthdb_secure.sqlite'):
           healthdb_secure = str(file_found)
           source_file_healthdb_secure = file_found.replace(seeker.directory, '')

    db = open_sqlite_db_readonly(healthdb_secure)
    
    cursor = db.cursor()
    
# Fitness Workouts Location Data Analysis

    cursor.execute('''
    SELECT
        datetime(workout_activities.start_date + 978307200, 'UNIXEPOCH') as "Workout Start Time",
        min(datetime(location_series_data.timestamp + 978307200, 'UNIXEPOCH')) as "Min Location Timestamp",
        datetime(workout_activities.end_date + 978307200, 'UNIXEPOCH') as "Workout End Time",
        max(datetime(location_series_data.timestamp + 978307200, 'UNIXEPOCH')) as "Max Location Timestamp",
        data_series.count as "Number of Location Points",
        round(((workout_activities.end_date - workout_activities.start_date) * ((max(location_series_data.timestamp) - min(location_series_data.timestamp)) / data_series.count))) as "Expected Number of Location Points",
        CASE activity_type
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
        END as "Workout Type",
        substr(datetime((workout_activities.end_date - workout_activities.start_date) + 978307200, 'UNIXEPOCH'),12,8) as "Elapsed Time",
        substr(datetime(workout_activities.duration + 978307200, 'UNIXEPOCH'),12,8) as "Workout Time",
        substr((datetime((max(location_series_data.timestamp) - min(location_series_data.timestamp)) + 978307200, 'UNIXEPOCH')),12,8) as "Location Data Capture Timespan",
        substr(((max(location_series_data.timestamp) - min(location_series_data.timestamp)) / data_series.count),1,5) as "Location Data Capture Average (in Seconds)"
        FROM location_series_data
        LEFT OUTER JOIN data_series on data_series.hfd_key = location_series_data.series_identifier
        LEFT OUTER JOIN associations on associations.child_id = data_series.data_id
        LEFT OUTER JOIN workout_activities on workout_activities.owner_id = associations.parent_id 
        GROUP BY location_series_data.series_identifier
        ORDER BY workout_activities.start_date
    ''') 
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
        
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))

        report = ArtifactHtmlReport('Fitness Workouts Location Data Analysis')
        report.start_artifact_report(report_folder, 'Fitness Workouts Location Data Analysis')
        report.add_script()
        data_headers = (
            'Workout Start Time', 'Min Location Timestamp', 'Workout End Time', 'Max Location Timestamp', 'Number of Location Points', 'Expected Number of Location Points', 'Workout Type', 'Elapsed Time', 'Workout Time', 'Location Data Capture Timespan', 'Location Data Capture Average (in Seconds)')
        report.write_artifact_data_table(data_headers, data_list, healthdb_secure)
        report.end_artifact_report()

        tsvname = 'Fitness Workouts Location Data Analysis'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Fitness Workouts Location Data Analysis'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in Fitness Workouts Location Data Analysis')

# Fitness Workouts Location Data

    cursor.execute('''
    SELECT
        datetime(timestamp+978307200,'unixepoch') as "Timestamp",
        CASE activity_type
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
        END as "Workout Type",
        latitude as "Latitude",
        longitude as "Longitude",
        substr(altitude,1,8) as "Altitude",
        substr(speed,1,6) as "Speed",
        substr(course,1,6) as "Course",
        substr(horizontal_accuracy,1,6) as "Horizontal Accuracy",
        series_identifier as "Series Identifier"
        FROM location_series_data
        LEFT OUTER JOIN data_series on data_series.hfd_key = location_series_data.series_identifier
        LEFT OUTER JOIN associations on associations.child_id = data_series.data_id
        LEFT OUTER JOIN workout_activities on workout_activities.owner_id = associations.parent_id 
    ''') #Note Vertical, Speed, and Course Accuracy values also in database table, not added here to reduce processing
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
        
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))

        report = ArtifactHtmlReport('Fitness Workouts Location Data')
        report.start_artifact_report(report_folder, 'Fitness Workouts Location Data')
        report.add_script()
        data_headers = (
            'Timestamp', 'Workout Type', 'Latitude', 'Longitude', 'Altitude', 'Speed', 'Course', 'Horizontal Accuracy', 'Series Identifier')
        report.write_artifact_data_table(data_headers, data_list, healthdb_secure)
        report.end_artifact_report()

        tsvname = 'Fitness Workouts Location Data'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Fitness Workouts Location Data'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in Fitness Workouts Location Data')
        
__artifacts__ = {
    "Fitness": (
        "Fitness",
        ('*Health/healthdb_secure.sqlite*'),
        get_Health)
}
