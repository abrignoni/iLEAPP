import json

from ileapp.scripts.artifact_report import ArtifactHtmlReport
from ileapp.scripts.ilapfuncs import logfunc, timeline, kmlgen, tsv, is_platform_windows

def get_teamsSegment(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list_location = []
    data_list_motion = []
    data_list_timecheck = []
    data_list_power = []
    data_list_statechange = []
    
    for file_found in files_found:
        with open(file_found) as file:
            for line in file:
                serial = json.loads(line)
                timestamp = serial[0].replace('T',' ')
                #print(serial[1])
                if serial[1] == 'location':
                    locationtimestamp = serial[2].get('sourceTimestamp', '')
                    locationtimestamp = locationtimestamp.replace('T',' ')
                    longitude = serial[2].get('longitude', '')
                    latitude = serial[2].get('latitude', '')
                    speed = serial[2].get('speed', '')
                    altitude = serial[2].get('altitude', '')
                    vertacc = serial[2].get('verticalAccuracy', '')
                    horiacc = serial[2].get('horizontalAccuracy', '')
                    data_list_location.append((locationtimestamp, longitude, latitude, speed, altitude, vertacc, horiacc))
                    
                if serial[1] == 'motion':
                    motionact = (serial[2].get('activityName', ''))
                    data_list_motion.append((timestamp, motionact))
                    
                if serial[1] == 'timeCheck':
                    tczone = serial[2].get('timezone', '')
                    tcoffset = serial[2].get('offset', '')
                    tcreason = serial[2].get('reason', '')
                    data_list_timecheck.append((timestamp, tczone, tcoffset, tcreason))
                    
                if serial[1] == 'power':
                    plugged = serial[2].get('isPluggedIn', '')
                    batlvl = serial[2].get('batteryLevel', '')
                    data_list_power.append((timestamp, plugged, batlvl))
                    
                if serial[1] == 'stateChange':
                    agg = ' '
                    for a, b in serial[2].items():
                        agg = agg + (f'{a}: {b} ')
                    agg = agg.lstrip()
                    data_list_statechange.append((timestamp, agg))

    if len(data_list_location) > 0:
        report = ArtifactHtmlReport('Microsoft Teams Locations')
        report.start_artifact_report(report_folder, 'Teams Locations')
        report.add_script()
        data_headers_location = ('Timestamp', 'Longitude', 'Latitude', 'Speed', 'Altitude', 'Vertical Accuracy', 'Horizontal Accuracy')   
        report.write_artifact_data_table(data_headers_location, data_list_location, file_found)
        report.end_artifact_report()
        
        tsvname = 'Microsoft Teams Locations'
        tsv(report_folder, data_headers_location, data_list_location, tsvname)
        
        tlactivity = 'Microsoft Teams Locations'
        timeline(report_folder, tlactivity,  data_list_location, data_headers_location)
        
        kmlactivity = 'Microsoft Teams Locations'
        kmlgen(report_folder, kmlactivity, data_list_location, data_headers_location)
    else:
        logfunc('No Microsoft Teams Locations data')
    
        
    if len(data_list_motion) > 0:
        report = ArtifactHtmlReport('Microsoft Teams Motion')
        report.start_artifact_report(report_folder, 'Teams Motion')
        report.add_script()
        data_headers_motion = ('Timestamp', 'Activity')
        report.write_artifact_data_table(data_headers_motion, data_list_motion, file_found)
        report.end_artifact_report()
        
        tsvname = 'Microsoft Teams Motion'
        tsv(report_folder, data_headers_motion, data_list_motion, tsvname)
        
        tlactivity = 'Microsoft Teams Motion'
        timeline(report_folder, tlactivity, data_list_motion, data_headers_motion)
        
    else:
        logfunc('No Microsoft Teams Motion data')
        
    if len(data_list_timecheck) > 0:
        report = ArtifactHtmlReport('Microsoft Teams Timezone')
        report.start_artifact_report(report_folder, 'Teams Timezone')
        report.add_script()
        data_headers_timecheck = ('Timestamp', 'Timezone', 'Timezone Offset', 'Timezone reason')
        report.write_artifact_data_table(data_headers_timecheck, data_list_timecheck, file_found)
        report.end_artifact_report()
        
        tsvname = 'Microsoft Teams Timezone'
        tsv(report_folder, data_headers_timecheck, data_list_timecheck, tsvname)
        
        tlactivity = 'Microsoft Teams Timezone'
        timeline(report_folder, tlactivity, data_list_timecheck, data_headers_timecheck)
        
    else:
        logfunc('No Microsoft Teams Timezone data')
        
    if len(data_list_power) > 0:
        report = ArtifactHtmlReport('Microsoft Teams Power Log')
        report.start_artifact_report(report_folder, 'Teams Power Log')
        report.add_script()
        data_headers_power = ('Timestamp', 'Is plugged in?', 'Battery Level')
        report.write_artifact_data_table(data_headers_power, data_list_power, file_found)
        report.end_artifact_report()
        
        tsvname = 'Microsoft Teams Power Log'
        tsv(report_folder, data_headers_power, data_list_power, tsvname)
        
        tlactivity = 'Microsoft Teams Power Log'
        timeline(report_folder, tlactivity, data_list_power, data_headers_power)
        
    else:
        logfunc('No Microsoft Teams Power Log data')

    if len(data_list_statechange) > 0:
        report = ArtifactHtmlReport('Microsoft Teams State Change')
        report.start_artifact_report(report_folder, 'Teams State Change')
        report.add_script()
        data_headers_statechange = ('Timestamp', 'Change')
        report.write_artifact_data_table(data_headers_statechange, data_list_statechange, file_found)
        report.end_artifact_report()
        
        tsvname = 'Microsoft Teams State Change'
        tsv(report_folder, data_headers_statechange, data_list_statechange, tsvname)
        
        tlactivity = 'Microsoft Teams State Change'
        timeline(report_folder, tlactivity, data_list_statechange, data_headers_statechange)
        
    else:
        logfunc('No Microsoft Teams Power State Change')

__artifacts__ = {
    "teamsSegment": (
        "Microsoft Teams - Logs",
        ('*/mobile/Containers/Data/Application/*/Library/DriveIQ/segments/current/*.*'),
        get_teamsSegment)
}