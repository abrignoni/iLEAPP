import base64
import json
import sqlite3
import os
import scripts.artifacts.artGlobals
from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, strings, open_sqlite_db_readonly, does_table_exist


def get_geodPDPlaceCache(files_found, report_folder, seeker, wrap_text, timezone_offset):
	for file_found in files_found:
		file_found = str(file_found)
		
		if file_found.endswith('.db'):
			break
		
	db = open_sqlite_db_readonly(file_found)
	if does_table_exist(db, 'pdplacelookup'):
		query = ("""
	SELECT requestkey, pdplacelookup.pdplacehash, datetime('2001-01-01', "lastaccesstime" || ' seconds') as lastaccesstime, datetime('2001-01-01', "expiretime" || ' seconds') as expiretime, pdplace
	FROM pdplacelookup
	INNER JOIN pdplaces on pdplacelookup.pdplacehash = pdplaces.pdplacehash
	""")
	else:
		logfunc()
	cursor = db.cursor()
	cursor.execute(query)
	

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []
	if usageentries > 0:
		for row in all_rows:
			pd_place = ''.join(f'{row}<br>' for row in set(strings(row[4])))
			data_list.append((row[2], row[0], row[1], row[3], pd_place))
		description = ''
		report = ArtifactHtmlReport('Geolocation')
		report.start_artifact_report(report_folder, 'PD Place Cache', description)
		report.add_script()
		data_headers = ( "last access time", "requestkey", "pdplacehash", "expire time", "pd place")
		report.write_artifact_data_table(data_headers, data_list, file_found, html_escape = False)
		report.end_artifact_report()

		tsvname = 'Geolocation PD Place Caches'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'Geolocation PD Place Caches'
		timeline(report_folder, tlactivity, data_list, data_headers)

	else:
		logfunc('No data available for Geolocation PD Place Caches')

	db.close()
	return
	
__artifacts__ = {
    "geodpdplacecache": (
        "Geolocation",
        ('**/PDPlaceCache.db*'),
        get_geodPDPlaceCache)
}