__artifacts_v2__ = {
    "get_audiTripdata": {
        "name": "Audi Trip Data",
        "description": "",
        "author": "@AuthorUsername",
        "creation_date": "2024-06-01",
        "last_update_date": "2025-04-13",
        "requirements": "none",
        "category": "Audi Trips",
        "notes": "",
        "paths": ('*/Library/Caches/de.audi.myaudimobileassistant/fsCachedData/**',),
        "output_types": "standard"
    }
}

import json
import os

from scripts.ilapfuncs import convert_ts_human_to_utc, artifact_processor

@artifact_processor
def get_audiTripdata(context):
	data_list = []
	for file_found in context.get_files_found():
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
							
							data_list.append((timestamp,avgspeed,traveltime,startmileage,mileage,overallmileage,tripid,avgelecconsumpt,avgfuelconsumpt,zeroemdistance,triptyme,reportreason, file_found))
	data_headers = (('Timestamp', 'datetime'),'Avg. Speed','Travel Time','Start Mileage','Mileage','Overall Mileage','Trip ID','Avg. Electric Consumption','Avg. Fuel Consumption','Zero Emission Distance','Trip Type','Report Reason', 'Source File')   
	return data_headers, data_list, ''