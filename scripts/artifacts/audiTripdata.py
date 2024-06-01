import json
import os
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, tsv, is_platform_windows, convert_utc_human_to_timezone, convert_ts_human_to_utc

def get_audiTripdata(files_found, report_folder, seeker, wrap_text, timezone_offset):
	data_list = []
	for file_found in files_found:
		file_found = str(file_found)
		
		if os.path.isdir(file_found):
			pass
		else:
			with open(file_found) as f:
				data = f.read()
				
			jsondata = json.loads(data)
			
			for key, values in jsondata.items():
				if isinstance(values, dict):
					audidata = values.get('tripData','')
					if audidata == '':
						pass
					else:
						for trip in audidata:
							timestamp = trip['timestamp']
							
							date, time = timestamp.split('T')
							time = time.split('Z')[0]
							timestamp = f'{date} {time}'
							timestamp = convert_ts_human_to_utc(timestamp)
							timestamp = convert_utc_human_to_timezone(timestamp, timezone_offset)
							
							avgspeed = trip['averageSpeed']
							tripid = trip['tripID']
							mileage = trip['mileage']
							overallmileage = trip['overallMileage']
							startmileage = trip['startMileage']
							traveltime = trip['traveltime']
							zeroemdistance = trip['zeroEmissionDistance']
							avgelecconsumpt = trip['averageElectricEngineConsumption']
							avgfuelconsumpt = trip['averageFuelConsumption']
							triptyme = trip['tripType']
							reportreason = trip['reportReason']
							
							data_list.append((timestamp,avgspeed,traveltime,startmileage,mileage,overallmileage,tripid,avgelecconsumpt,avgfuelconsumpt,zeroemdistance,triptyme,reportreason))
				
	
	if len(data_list) > 0:		
		report = ArtifactHtmlReport('Audi Trip Data')
		report.start_artifact_report(report_folder, 'Audi Trip Data')
		report.add_script()
		data_headers = ('Timestamp','Avg. Speed','Travel Time','Start Mileage','Mileage','Overall Mileage','Trip ID','Avg. Electric Consumption','Avg. Fuel Consumption','Zero Emission Distance','Trip Type','Report Reason')   
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'Audi Trip Data'
		tsv(report_folder, data_headers, data_list, tsvname)

__artifacts__ = {
    "auditrip": (
        "Audi Trip",
        ('*/Library/Caches/de.audi.myaudimobileassistant/fsCachedData/**'),
        get_audiTripdata)
}