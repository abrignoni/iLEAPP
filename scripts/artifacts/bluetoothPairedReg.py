import glob
import os
import sys
import stat
import pathlib
import plistlib
import datetime


from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 


def get_bluetoothPairedReg(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	os.chmod(file_found, 0o0777)
	data_list = [] 
	with open(file_found, 'rb') as f:
		deserialized = plistlib.load(f)
		#print(deserialized)
	if len(deserialized) > 0:
		for x in deserialized.items():
			macaddress = x[0]
			#print(x[1])
			if 'LastSeenTime' in x[1]:
				lastseen = x[1]['LastSeenTime']
				lastseen = (datetime.datetime.fromtimestamp(int(lastseen)).strftime('%Y-%m-%d %H:%M:%S'))
			else:
				lastseen = ''
			if 'UserNameKey' in x[1]:
				usernkey = x[1]['UserNameKey']
			else:
				usernkey = ''
				
			if 'Name' in x[1]:
				nameu = x[1]['Name']
			else: 
				nameu = ''
			if 'DeviceIdProduct' in x[1]:
				deviceid = x[1]['DeviceIdProduct']
			else:
				deviceid = ''
			if 'DefaultName' in x[1]:
				defname = x[1]['DefaultName']
			else:
				defname = ''

			data_list.append((lastseen, macaddress, usernkey, nameu, deviceid, defname))
			
		description = ''
		report = ArtifactHtmlReport('Bluetooth Paired')
		report.start_artifact_report(report_folder, 'Paired', description)
		report.add_script()
		data_headers = ('Last Seen Time','MAC Address','Name Key','Name','Device Product ID','Default Name' )     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'Bluetooth Paired'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'Bluetooth Paired'
		timeline(report_folder, tlactivity, data_list, data_headers)
	else:
		print('No Bluetooth paired devices')
	