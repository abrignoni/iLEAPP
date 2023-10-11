
import os
import json
from pathlib import Path
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, tsv, is_platform_windows 


def get_discordManifest(files_found, report_folder, seeker, wrap_text, timezone_offset):
	data_list = []
	for file_found in files_found:
		file_found = str(file_found)
		
		if os.path.isfile(file_found):
			with open(file_found) as f_in:
				for jsondata in f_in:
					jsonfinal = json.loads(jsondata)

		for key, value in jsonfinal.items():
			data_list.append((key, value))


	if len(data_list) > 0:	
		report = ArtifactHtmlReport('Discord Manifest')
		report.start_artifact_report(report_folder, 'Discord Manifest')
		report.add_script()
		data_headers = ('Key', 'Value')   
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'Discord Manifest'
		tsv(report_folder, data_headers, data_list, tsvname)
		
__artifacts__ = {
    "discordmanifest": (
        "Discord",
        ('*/mobile/Containers/Data/Application/*/Documents/RCTAsyncLocalStorage_V1/manifest.json'),
        get_discordManifest)
}