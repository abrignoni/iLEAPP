from itertools import chain
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly


def get_healthAll(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)

    iOSversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iOSversion) >= version.parse("12"):
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(samples.start_date + 978307200, 'unixepoch'),
        datetime(samples.end_date + 978307200, 'unixepoch'),
        metadata_values.numerical_value,
        case workouts.activity_type 
        when 63 then "high intensity interval training (hiit)" 
        when 37 then "indoor / outdoor run" 
        when 3000 then "other" 
        when 52 then "indoor / outdoor walk" 
        when 20 then "functional training" 
        when 13 then "indoor cycle" 
        when 16 then "elliptical" 
        when 35 then "rower"
        else "unknown"
        end, 
        workouts.duration / 60.00, 
        workouts.total_energy_burned, 
        workouts.total_distance,
        workouts.total_distance*0.621371, 
        case workouts.goal_type 
        when 2 then "minutes" 
        when 0 then "open" 
        end, 
        workouts.goal, 
        workouts.total_flights_climbed, 
        workouts.total_w_steps
        from
        samples, metadata_values, metadata_keys, workouts 
        where metadata_values.object_id = samples.data_id 
        and metadata_keys.rowid = metadata_values.key_id 
        and  workouts.data_id = samples.data_id 
        and workouts.activity_type not null and key is "_HKPrivateWorkoutAverageHeartRate"
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            for row in all_rows:
                data_list.append(
                    (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11]))

            report = ArtifactHtmlReport('Health Workout Cadence')
            report.start_artifact_report(report_folder, 'Workout Cadence')
            report.add_script()
            data_headers = (
                'Start Date', 'End Date', 'Strides per Min.', 'Workout Type', 'Duration in Mins.', 'Calories Burned',
                'Distance in KM', 'Distance in Miles', 'Goal Type', 'Goal', 'Flights Climbed', 'Steps')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Health Workout Cadence'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Health Workout Cadence'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No data available in Workout Cadence')

    if version.parse(iOSversion) >= version.parse("9"):
        cursor = db.cursor()
        cursor.execute("""
        select
        datetime(samples.start_date + 978307200, 'unixepoch'),
        datetime(samples.end_date + 978307200, 'unixepoch'),
        quantity,
        quantity*3.28084,
        (samples.end_date-samples.start_date)
        from
        samples 
        left join
        quantity_samples 
        on samples.data_id = quantity_samples.data_id 
        left join
        correlations 
        on samples.data_id = correlations.object 
        where
        samples.data_type = 8
        """
                       )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        if usageentries == 0:
            logfunc('No data available in Distance')
        else:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4]))

            description = ''
            report = ArtifactHtmlReport('Health Distance')
            report.start_artifact_report(report_folder, 'Distance', description)
            report.add_script()
            data_headers = ('Start Date', 'End Date', 'Distance in Meters', 'Distance in Feet', 'Time in Seconds')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Health Distance'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Health Distance'
            timeline(report_folder, tlactivity, data_list, data_headers)

    if version.parse(iOSversion) >= version.parse("12"):
        cursor = db.cursor()
        cursor.execute("""
        select
        datetime(samples.start_date + 978307200, 'unixepoch'),
        datetime(samples.end_date + 978307200, 'unixepoch'),
        metadata_values.numerical_value,
        (samples.end_date-samples.start_date)
        from
        samples 
        left join
        metadata_values 
        on metadata_values.object_id = samples.data_id 
        left join
        metadata_keys 
        on metadata_keys.rowid = metadata_values.key_id 
        left join
        workouts 
        on workouts.data_id = samples.data_id 
        where
        key is "_HKPrivateMetadataKeyElectrocardiogramHeartRate"
        """
                       )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        if usageentries == 0:
            logfunc('No data available in ECG Avg. Heart Rate')
        else:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3]))

            description = ''
            report = ArtifactHtmlReport('Health ECG Avg Heart Rate')
            report.start_artifact_report(report_folder, 'ECG Avg. Heart Rate', description)
            report.add_script()
            data_headers = ('Start Date', 'End Date', 'ECG Avg. Heart Rate', 'Time in Seconds')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Health ECG Avg Heart Rate'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Health ECG Avg Heart Rate'
            timeline(report_folder, tlactivity, data_list, data_headers)

    if version.parse(iOSversion) >= version.parse("9"):
        cursor = db.cursor()
        cursor.execute("""
        select
        datetime(samples.start_date + 978307200, 'unixepoch'),
        datetime(samples.end_date + 978307200, 'unixepoch'),
        quantity,
        (samples.end_date-samples.start_date)
        from
        samples, quantity_samples 
        where samples.data_id = quantity_samples.data_id 
        and samples.data_type = 12
        """
                       )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        if usageentries == 0:
            logfunc('No data available in Flights Climbed')
        else:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3]))

        description = ''
        report = ArtifactHtmlReport('Health Flights Climbed')
        report.start_artifact_report(report_folder, 'Flights Climbed', description)
        report.add_script()
        data_headers = ('Start Date', 'End Date', 'Flights Climbed', 'Time in Seconds')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = 'Health Flights Climbed'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Health Flights Climbed'
        timeline(report_folder, tlactivity, data_list, data_headers)

    if version.parse(iOSversion) >= version.parse("9"):
        cursor = db.cursor()
        cursor.execute("""
        select
        datetime(samples.start_date + 978307200, 'unixepoch'),
        original_quantity, 
        unit_strings.unit_string,
        quantity
        from
        samples, quantity_samples, unit_strings 
        where samples.data_type = 5
        and quantity_samples.original_unit = unit_strings.rowid 
        and samples.data_id = quantity_samples.data_id 
        """
                       )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        if usageentries == 0:
            logfunc('No data available in Heart Rate')
        else:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3]))

            description = ''
            report = ArtifactHtmlReport('Health Heart Rate')
            report.start_artifact_report(report_folder, 'Heart Rate', description)
            report.add_script()
            data_headers = ('Date', 'Heart Rate', 'Units', 'Quantity')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Health Heart Rate'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Health Heart Rate'
            timeline(report_folder, tlactivity, data_list, data_headers)

    if version.parse(iOSversion) >= version.parse("9"):
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(samples.start_date + 978307200, 'unixepoch'),
        datetime(samples.end_date + 978307200, 'unixepoch'),
        quantity,
        (samples.end_date-samples.start_date)
        from
        samples, quantity_samples 
        where samples.data_type = 75
        and samples.data_id = quantity_samples.data_id 
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3]))

            report = ArtifactHtmlReport('Health Stood Up')
            report.start_artifact_report(report_folder, 'Stood Up')
            report.add_script()
            data_headers = ('Start Date', 'End Date', 'Stood Up', 'Time in Seconds')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Health Stood Up'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Health Stood Up'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No data available in Stood Up')

    if version.parse(iOSversion) >= version.parse("9"):
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(SAMPLES.START_DATE + 978307200, 'unixepoch'),
        datetime(SAMPLES.END_DATE + 978307200, 'unixepoch'),
        QUANTITY_SAMPLES.QUANTITY,
        (SAMPLES.END_DATE - SAMPLES.START_DATE),
        DATA_PROVENANCES.ORIGIN_PRODUCT_TYPE
        FROM SAMPLES, QUANTITY_SAMPLES, DATA_PROVENANCES, OBJECTS
        WHERE SAMPLES.DATA_TYPE = 7 
            AND SAMPLES.DATA_ID = QUANTITY_SAMPLES.DATA_ID
            AND SAMPLES.DATA_ID = OBJECTS.DATA_ID
            AND OBJECTS.PROVENANCE = data_provenances.ROWID  
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            daily_steps_nested_list = []

            c = 0
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4]))

                date, hour = row[0].split(' ')

                if date not in chain(*daily_steps_nested_list):
                    daily_steps_nested_list.append([date, row[2], row[3]])
                else:
                    for entry in daily_steps_nested_list:
                        if entry[0] == date:
                            entry[1] += row[2]
                            entry[2] += row[3]

            daily_steps_list = [tuple(t) for t in daily_steps_nested_list]

            report = ArtifactHtmlReport('Health Steps')
            report.start_artifact_report(report_folder, 'Steps')
            report.add_script()
            data_headers = ('Start Date', 'End Date', 'Steps', 'Time in Seconds', 'Origin')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Health Steps'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Health Steps'
            timeline(report_folder, tlactivity, data_list, data_headers)

            description = 'Cumulative total of the steps gathered from all available sources for each day'
            report = ArtifactHtmlReport('Health Steps per Day')
            report.start_artifact_report(report_folder, 'Steps per Day', description)
            report.add_script()
            data_headers = ('Date', 'Steps', 'Time in Seconds')
            report.write_artifact_data_table(data_headers, daily_steps_list, file_found)
            report.end_artifact_report()

            tsvname = 'Health Steps per Day'
            tsv(report_folder, data_headers, daily_steps_list, tsvname)

            tlactivity = 'Health Steps per Day'
            timeline(report_folder, tlactivity, daily_steps_list, data_headers)

        else:
            logfunc('No data available in Steps')

    if version.parse(iOSversion) >= version.parse("9"):
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        DATETIME(SAMPLES.START_DATE + 978307200, 'UNIXEPOCH'),
        QUANTITY,
        QUANTITY*2.20462
        FROM
        SAMPLES , QUANTITY_SAMPLES 
        WHERE SAMPLES.DATA_TYPE = 3 
        AND "DATE" IS  NOT NULL
        and SAMPLES.DATA_ID = QUANTITY_SAMPLES.DATA_ID 
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            for row in all_rows:
                data_list.append((row[0], row[1], row[2]))

            report = ArtifactHtmlReport('Health Weight')
            report.start_artifact_report(report_folder, 'Weight')
            report.add_script()
            data_headers = ('Date', 'Weight in KG', 'Weight in LBS')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Health Weight'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Health Weight'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No data available in Weight')

    if version.parse(iOSversion) >= version.parse("9"):
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(samples.start_date + 978307200, 'unixepoch'),
        datetime(samples.end_date + 978307200, 'unixepoch'),
        metadata_values.numerical_value/100.00,
        (metadata_values.numerical_value/100.00)*3.28084,
        case workouts.activity_type 
        when 63 then "high intensity interval training (hiit)" 
        when 37 then "indoor / outdoor run" 
        when 3000 then "other" 
        when 52 then "indoor / outdoor walk" 
        when 20 then "functional training" 
        when 13 then "indoor cycle" 
        when 16 then "elliptical" 
        when 35 then "rower"
        else "unknown"
        end, 
        workouts.duration / 60.00, 
        workouts.total_energy_burned, 
        workouts.total_distance,
        workouts.total_distance*0.621371, 
        case workouts.goal_type 
        when 2 then "minutes" 
        when 0 then "open" 
        end, 
        workouts.goal, 
        workouts.total_flights_climbed, 
        workouts.total_w_steps
        from
        samples, metadata_values, metadata_keys, workouts 
        where metadata_values.object_id = samples.data_id 
        and metadata_keys.rowid = metadata_values.key_id 
        and  workouts.data_id = samples.data_id 
        and workouts.activity_type not null and (key is null or key is  "HKIndoorWorkout")
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            for row in all_rows:
                data_list.append(
                    (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11]))

            report = ArtifactHtmlReport('Health Workout General')
            report.start_artifact_report(report_folder, 'Workout General')
            report.add_script()
            data_headers = (
                'Start Date', 'End Date', 'Workout Type', 'Duration in Min.', 'Calories Burned', 'Distance in KM',
                'Distance in Miles', 'Total Base Energy Burned', 'Goal Type', 'Goal', 'Flights Climbed', 'Steps')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Health Workout General'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Health Workout General'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No data available in Workout General')

    if version.parse(iOSversion) >= version.parse("9"):
        cursor = db.cursor()
        cursor.execute('''
        SELECT 
        DATETIME(SAMPLES.START_DATE + 978307200, 'UNIXEPOCH'),
        DATETIME(SAMPLES.END_DATE + 978307200, 'UNIXEPOCH'),
        cast(ROUND(QUANTITY) as int)
        FROM SAMPLES, QUANTITY_SAMPLES
        WHERE SAMPLES.DATA_TYPE = 172 AND SAMPLES.DATA_ID = QUANTITY_SAMPLES.DATA_ID
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            for row in all_rows:
                data_list.append((row[0], row[1], row[2]))

            report = ArtifactHtmlReport('Environmental Sound Levels')
            report.start_artifact_report(report_folder, 'Environmental Sound Levels')
            report.add_script()
            data_headers = ('Start Date', 'End Date', 'Sound in dBA SPL')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Environmental Sound Levels'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Environmental Sound Levels'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No data available in Environmental Sound Levels')

    if version.parse(iOSversion) >= version.parse("9"):
        cursor = db.cursor()
        cursor.execute('''
        SELECT 
        DATETIME(SAMPLES.START_DATE + 978307200, 'UNIXEPOCH'),
        DATETIME(SAMPLES.END_DATE + 978307200, 'UNIXEPOCH'),
        (SAMPLES.END_DATE - SAMPLES.START_DATE)
        FROM SAMPLES
        WHERE SAMPLES.DATA_TYPE = 63
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            for row in all_rows:
                data_list.append((row[0], row[1], row[2]))

            report = ArtifactHtmlReport('Sleep Analysis')
            report.start_artifact_report(report_folder, 'Sleep Analysis')
            report.add_script()
            data_headers = ('Start Date', 'End Date', 'Time in Seconds')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Sleep Analysis'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Sleep Analysis'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No data available in Sleep Analysis')
