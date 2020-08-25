import base64
import json
import sqlite3
import os
import string
import scripts.artifacts.artGlobals
from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, generate_hexdump


def get_geodMapTiles(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	os.chmod(file_found, 0o0777)
	db = sqlite3.connect(file_found)
	cursor = db.cursor()
	cursor.execute(
	"""
	SELECT datetime(access_times.timestamp, 'unixepoch') as timestamp, key_a, key_b, key_c, key_d, tileset, data as image, size, etag
	FROM data
	INNER JOIN access_times on data.rowid = access_times.data_pk
	""")

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []
	if usageentries > 0:
		for row in all_rows:
			if row[6][:11] == b'\xff\xd8\xff\xe0\x00\x10\x4a\x46\x49\x46\x00':
				img_base64 = base64.b64encode(row[6]).decode('utf-8')
				img_html = f'<img src="data:image/jpeg;base64, {img_base64}" alt="Map Tile" />'
				data_list.append((row[0], row[5], row[1], row[2], row[3], row[4], img_html, row[7], row[8]))
			else:
				header_bytes = row[6][:28]
				hexdump = generate_hexdump(header_bytes, 5)
							
				data_list.append((row[0], row[5], row[1], row[2], row[3], row[4],
					              hexdump, row[7], row[8]))
		description = ''
		report = ArtifactHtmlReport('Geolocation')
		report.start_artifact_report(report_folder, 'Map Tile Cache', description)
		report.add_script()
		data_headers = ("Timestamp", "Tileset", "Key A", "Key B", "Key C", "Key D", "Image/Hex", "Size", "ETAG")
		report.write_artifact_data_table(data_headers, data_list, file_found, html_escape = False)
		report.end_artifact_report()

		tsvname = 'Geolocation'
		tsv(report_folder, data_headers, data_list, tsvname)

	else:
		logfunc('No data available for Geolocation')

	db.close()
	return

