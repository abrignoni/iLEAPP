import sqlite3
import sys, os, re
import glob
import ccl_bplist
import datetime
import plistlib
from parse3 import ParseProto
import codecs
import json
import sqlite3
import io
import sys
import csv
import pathlib
import shutil
import textwrap
from time import process_time

nl = '\n' 
now = datetime.datetime.now()
currenttime = str(now.strftime('%Y-%m-%d_%A_%H%M%S'))
reportfolderbase = './ILEAPP_Reports_'+currenttime+'/'
temp = reportfolderbase+'temp/'

def logfunc(message):
	if pathlib.Path(reportfolderbase+'Script Logs/Screen Output.html').is_file():
		with open(reportfolderbase+'Script Logs/Screen Output.html', 'a', encoding='utf8') as f:
			print(message)
			f.write(message+'<br>')
	else:
		with open(reportfolderbase+'Script Logs/Screen Output.html', 'a', encoding='utf8') as f:
			print(message)
			f.write(message+'<br>')

def datausage(filefound):
	os.makedirs(reportfolderbase+'Data Usage/')
	try:
		db = sqlite3.connect(filefound[0])
		cursor = db.cursor()
		cursor.execute('''
		SELECT
				DATETIME(ZPROCESS.ZTIMESTAMP + 978307200, 'unixepoch') AS "PROCESS TIMESTAMP",
				DATETIME(ZPROCESS.ZFIRSTTIMESTAMP + 978307200, 'unixepoch') AS "PROCESS FIRST TIMESTAMP",
				DATETIME(ZLIVEUSAGE.ZTIMESTAMP + 978307200, 'unixepoch') AS "LIVE USAGE TIMESTAMP",
				ZBUNDLENAME AS "BUNDLE ID",
				ZPROCNAME AS "PROCESS NAME",
				ZWIFIIN AS "WIFI IN",
				ZWIFIOUT AS "WIFI OUT",
				ZWWANIN AS "WWAN IN",
				ZWWANOUT AS "WWAN OUT",
				ZLIVEUSAGE.Z_PK AS "ZLIVEUSAGE TABLE ID" 
			FROM ZLIVEUSAGE 
			LEFT JOIN ZPROCESS ON ZPROCESS.Z_PK = ZLIVEUSAGE.ZHASPROCESS
		''')

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			logfunc(f'Data Usage - Zliveusage function executing')
			with open(reportfolderbase+'Data Usage/Zliveusage.html', 'w', encoding='utf8') as f:
				f.write('<html><body>')
				f.write('<h2> Zliveusage report</h2>')
				f.write(f'Zliveusage entries: {usageentries}<br>')
				f.write(f'Zliveusage located at: {filefound[0]}<br>')
				f.write('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
				f.write('<br/>')
				f.write('')
				f.write(f'<table>')
				f.write(f'<tr><td>Process Timestamp</td><td>Process First Timestamp</td><td>Live Usage Timestamp</td><td>Bundle ID</td><td>Process Name</td><td>WIFI In</td><td>WIFI Out</td><td>WWAN IN</td><td>WWAN Out</td><td>Table ID</td></tr>')
				for row in all_rows:
					f.write(f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td></tr>')
				f.write(f'</table></body></html>')
				logfunc(f'Data Usage - Zliveusage function completed')
		else:
				logfunc('No Data Usage - Zliveusage available')
	except:
		logfunc('Error in Data Usage - Zliveusage section.')
 
	try:
		db = sqlite3.connect(filefound[0])
		cursor = db.cursor()
		cursor.execute('''
		SELECT
				DATETIME(ZPROCESS.ZTIMESTAMP+ 978307200, 'unixepoch') AS "TIMESTAMP",
				DATETIME(ZPROCESS.ZFIRSTTIMESTAMP + 978307200, 'unixepoch') AS "PROCESS FIRST TIMESTAMP",
				ZPROCESS.ZPROCNAME AS "PROCESS NAME",
				ZPROCESS.ZBUNDLENAME AS "BUNDLE ID",
				ZPROCESS.Z_PK AS "ZPROCESS TABLE ID" 
			FROM ZPROCESS
		''')

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			logfunc(f'Data Usage - Zprocess function executing')
			with open(reportfolderbase+'Data Usage/Zprocess.html', 'w', encoding='utf8') as f:
				f.write('<html><body>')
				f.write('<h2> Zprocess report</h2>')
				f.write(f'Zprocess entries: {usageentries}<br>')
				f.write(f'Zprocess located at: {filefound[0]}<br>')
				f.write('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
				f.write('<br/>')
				f.write('')
				f.write(f'<table>')
				f.write(f'<tr><tr><td>Process Timestamp</td><td>Process First Timestamp</td><td>Live Usage Timestamp</td><td>Bundle ID</td><td>Table ID</td></tr>')
				for row in all_rows:
					f.write(f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></tr>')
				f.write(f'</table></body></html>')
				logfunc(f'Data Usage - Zprocess function completed')
		else:
				logfunc('No Data Usage - Zprocess available')
	except:
		logfunc('Error in Data Usage - Zprocess Section.')

def medlib(filefound):
	os.makedirs(reportfolderbase+'Media Library/')
	try:
		db = sqlite3.connect(filefound[0])
		cursor = db.cursor()
		cursor.execute('''
		select
		ext.title AS "Title",
		ext.media_kind AS "Media Type",
		itep.format AS "File format",
		ext.location AS "File",
		ext.total_time_ms AS "Total time (ms)",
		ext.file_size AS "File size",
		ext.year AS "Year",
		alb.album AS "Album Name",
		alba.album_artist AS "Artist", 
		com.composer AS "Composer", 
		gen.genre AS "Genre",
		art.artwork_token AS "Artwork",
		itev.extended_content_rating AS "Content rating",
		itev.movie_info AS "Movie information",
		ext.description_long AS "Description",
		ite.track_number AS "Track number",
		sto.account_id AS "Account ID",
		strftime('%d/%m/%Y %H:%M:%S', datetime(sto.date_purchased + 978397200,'unixepoch'))date_purchased,
		sto.store_item_id AS "Item ID",
		sto.purchase_history_id AS "Purchase History ID",
		ext.copyright AS "Copyright"
		from
		item_extra ext
		join item_store sto using (item_pid)
		join item ite using (item_pid)
		join item_stats ites using (item_pid)
		join item_playback itep using (item_pid)
		join item_video itev using (item_pid)
		left join album alb on sto.item_pid=alb.representative_item_pid
		left join album_artist alba on sto.item_pid=alba.representative_item_pid
		left join composer com on sto.item_pid=com.representative_item_pid
		left join genre gen on sto.item_pid=gen.representative_item_pid
		left join item_artist itea on sto.item_pid=itea.representative_item_pid
		left join artwork_token art on sto.item_pid=art.entity_pid 
		''')

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			logfunc(f'Media Library function executing')
			with open(reportfolderbase+'Media Library/Media Library.html', 'w', encoding='utf8') as f:
				f.write('<html><body>')
				f.write('<h2> Media Library report</h2>')
				f.write(f'Media Library entries: {usageentries}<br>')
				f.write(f'Media Library located at: {filefound[0]}<br>')
				f.write('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
				f.write('<br/>')
				f.write('')
				f.write(f'<table>')
				f.write(f'<tr><td>Title</td><td>Media Type</td><td>File Format</td><td>File</td><td>Total Time (ms)</td><td>File Size</td><td>Year</td><td>Album Name</td><td>Artist</td><td>Composer</td><td>Genre</td><td>Artwork</td><td>Content Rating</td><td>Movie Information</td><td>Description</td><td>Track Number</td><td>Account ID</td><td>Date Purchased</td><td>Item ID</td><td>Purchase History ID</td><td>Copyright</td></tr>')
				for row in all_rows:
					f.write(f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td><td>{row[10]}</td><td>{row[11]}</td><td>{row[12]}</td><td>{row[13]}</td><td>{row[14]}</td><td>{row[15]}</td><td>{row[16]}</td><td>{row[17]}</td><td>{row[18]}</td><td>{row[19]}</td><td>{row[20]}</td></tr>')
				f.write(f'</table></body></html>')
				logfunc(f'Media Library function completed')
		else:
				logfunc('No Media Library available')
	except:
		logfunc('Error in Media Library Section.')

def accs(filefound):
	os.makedirs(reportfolderbase+'Accounts/')
	try:
		db = sqlite3.connect(filefound[0])
		cursor = db.cursor()
		cursor.execute('''
		SELECT
		ZACCOUNTTYPEDESCRIPTION,
		ZUSERNAME,
		DATETIME(ZDATE+978307200,'UNIXEPOCH','UTC' ) AS 'ZDATE TIMESTAMP',
		ZACCOUNTDESCRIPTION,
		ZACCOUNT.ZIDENTIFIER,
		ZACCOUNT.ZOWNINGBUNDLEID
		FROM ZACCOUNT
		JOIN ZACCOUNTTYPE ON ZACCOUNTTYPE.Z_PK=ZACCOUNT.ZACCOUNTTYPE
		ORDER BY ZACCOUNTTYPEDESCRIPTION
		''')

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			logfunc(f'Account Data function executing')
			with open(reportfolderbase+'Accounts/Accounts.html', 'w', encoding='utf8') as f:
				f.write('<html><body>')
				f.write('<h2> Account Data report</h2>')
				f.write(f'Account Data entries: {usageentries}<br>')
				f.write(f'Account Data located at: {filefound[0]}<br>')
				f.write('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
				f.write('<br/>')
				f.write('')
				f.write(f'<table>')
				f.write(f'<tr><td>Account Desc</td><td>Usermane</td><td>Timestamp</td><td>Description</td><td>Identifier</td><td>Bundle ID</td></tr>')
				for row in all_rows:
					f.write(f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td></tr>')
				f.write(f'</table></body></html>')
				logfunc(f'Account Data function completed')
		else:
				logfunc('No Account Data available')
	except:
		logfunc('Error in Account Data Section.')

def conndevices(filefound):	
	with open(filefound[0], "rb") as f:
		data = f.read()

	logfunc(f'Connected devices function executing.')
	outpath = reportfolderbase +'Devices Connected/'
	os.mkdir(outpath)
	nl = '\n' 
	
	userComps = ""

	logfunc("Data being interpreted for FRPD is of type: " + str(type(data)))
	x = type(data)
	byteArr = bytearray(data)
	userByteArr = bytearray()
	
	magicOffset = byteArr.find(b'\x01\x01\x80\x00\x00')
	magic = byteArr[magicOffset:magicOffset + 5]

	flag = 0

	if magic == b'\x01\x01\x80\x00\x00':
		logfunc("Found magic bytes in iTunes Prefs FRPD... Finding Usernames and Desktop names now")
		f = open(outpath+'DevicesConnected.html', 'w')
		f.write('<html>')
		f.write(f'Artifact name and path: {filefound[0]}<br>')
		f.write(f'Usernames and Computer names:<br><br>')
		for x in range (int(magicOffset + 92), len(data)):
			if (data[x]) == 0:
				x = int(magicOffset) + 157
				if userByteArr.decode() == "":
					continue
				else:
					if flag == 0:
						userComps += userByteArr.decode() + " - "
						flag = 1
					else:
						userComps += userByteArr.decode() + "\n"
						flag = 0
					userByteArr = bytearray()
					continue
			else:
				char =  (data[x])
				userByteArr.append(char)

		logfunc(f'{userComps}{nl}')
		f.write(f'{userComps}<br>')
	f.write(f'</html>')
	f.close()
	logfunc(f'Connected devices function completed. ')

def applicationstate(filefound):
	#iOSversion = versionf
	logfunc(f'ApplicationState.db queries executing.')
	outpath = reportfolderbase +'Application State/'
	
	try: 
		os.mkdir(outpath)
		os.mkdir(outpath+"exported-dirty/")
		os.mkdir(outpath+"exported-clean/")
	except OSError:  
		logfunc("Error making directories")
	
	freepath = 1
	
	for pathfile in filefound:
		if isinstance(pathfile, pathlib.PurePath):
			freepath = os.path.abspath(pathfile)
			if freepath.endswith('.db'):
				apstatefiledb = freepath
		elif pathfile.endswith('.db'):		
			apstatefiledb = pathfile	

	#connect sqlite databases
	db = sqlite3.connect(apstatefiledb)
	cursor = db.cursor()

	cursor.execute('''
		select
		application_identifier_tab.[application_identifier],
		kvs.[value]
		from kvs, key_tab,application_identifier_tab
		where 
		key_tab.[key]='compatibilityInfo' and kvs.[key] = key_tab.[id]
		and application_identifier_tab.[id] = kvs.[application_identifier]
		order by application_identifier_tab.[id]
		''')

	all_rows = cursor.fetchall()
	
	#poner un try except por si acaso
	extension = '.bplist'
	count = 0
	
	for row in all_rows:
		bundleid = str(row[0])
		bundleidplist = bundleid+'.bplist'
		f = row[1]
		output_file = open(outpath+'/exported-dirty/'+bundleidplist, 'wb') #export dirty from DB
		output_file.write(f)
		output_file.close()	

		g = open(outpath+'/exported-dirty/'+bundleidplist, 'rb')
		#plist = plistlib.load(g)
		
		plist = ccl_bplist.load(g)
		
		output_file = open(outpath+'exported-clean/'+bundleidplist, 'wb') 
		output_file.write(plist)
		output_file.close()
	
	#create html headers
	filedatahtml = open(outpath+'Application State.html', mode='a+')
	filedatahtml.write('<html><body>')
	filedatahtml.write('<h2>iOS ApplicationState.db Report </h2>')
	filedatahtml.write ('<style> table, th, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;}</style>')
	filedatahtml.write('<br/>')
	filedatahtml.write('<table>')
	filedatahtml.write(f'<tr><td colspan = "4">{apstatefiledb}</td></tr>')
	filedatahtml.write('<tr><td>Bundle ID</td><td>Bundle Path</td><td>Sandbox Path</td></tr>')
	
		
	for filename in glob.glob(outpath+'exported-clean/*.bplist'):	
		p = open(filename, 'rb')
		#cfilename = os.path.basename(filename)
		plist = ccl_bplist.load(p)
		ns_keyed_archiver_obj = ccl_bplist.deserialise_NsKeyedArchiver(plist, parse_whole_structure=False)#deserialize clean 
		#logfunc(ns_keyed_archiver_obj)
		bid = (ns_keyed_archiver_obj['bundleIdentifier'])
		bpath = (ns_keyed_archiver_obj['bundlePath'])
		bcontainer = (ns_keyed_archiver_obj['bundleContainerPath'])
		bsandbox = (ns_keyed_archiver_obj['sandboxPath'])
		
		if bsandbox == '$null':
			bsandbox = ''
		if bcontainer == '$null':
			bcontainer = ''
		
		
		#csv report
		filedata = open(outpath+'ApplicationState_InstalledAppInfo.csv', mode='a+')
		filewrite = csv.writer(filedata, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		filewrite.writerow([bid, bpath, bcontainer, bsandbox])
		count = count + 1
		filedata.close()
		
		#html report
		filedatahtml.write(f'<tr><td>{bid}</td><td>{bpath}</td><td>{bsandbox}</td></tr>')
		
		
		filemetadata = open(outpath+'ApplicationState_InstalledAppInfo_Path.txt', mode='w')
		filemetadata.write(f'Artifact name and file path: {apstatefiledb} ')
		filemetadata.close()
	
	#close html footer
	filedatahtml.write('</table></html>')
	filedatahtml.close()
	
	logfunc(f'Installed app GUIDs and app locations processed: {count}')
	logfunc(f'ApplicationState.db queries completed.')
	
def knowledgec(filefound):
	logfunc(f'Incepted bplist extractions in knowlwdgeC.db executing.')

	iOSversion = versionf
	supportediOS = ['11', '12', '13']

	if iOSversion not in supportediOS:
		logfunc ("Unsupported version"+iOSversion)
		return()
		
	extension = '.bplist'
	dump = True
	#create directories
	outpath = reportfolderbase+'KnowledgeC/'


	try: 
		os.mkdir(outpath)
		os.mkdir(outpath+"clean/")
		os.mkdir(outpath+"/dirty")
	except OSError:  
		logfunc("Error making directories")
		
	#connect sqlite databases
	db = sqlite3.connect(filefound[0])
	cursor = db.cursor()

	#variable initializations
	dirtcount = 0
	cleancount = 0
	intentc = {}
	intentv = {}

	cursor.execute('''
	SELECT
	Z_PK,
	Z_DKINTENTMETADATAKEY__SERIALIZEDINTERACTION,
	Z_DKINTENTMETADATAKEY__INTENTCLASS,
	Z_DKINTENTMETADATAKEY__INTENTVERB
	FROM ZSTRUCTUREDMETADATA
	WHERE Z_DKINTENTMETADATAKEY__SERIALIZEDINTERACTION is not null
	''')

	all_rows = cursor.fetchall()

	for row in all_rows:
		pkv = str(row[0])
		pkvplist = pkv+extension
		f = row[1]
		intentclass = str(row[2])
		intententverb = str(row[3])
		output_file = open(outpath+'/dirty/D_Z_PK'+pkvplist, 'wb') #export dirty from DB
		output_file.write(f)
		output_file.close()	

		g = open(outpath+'/dirty/D_Z_PK'+pkvplist, 'rb')
		plistg = ccl_bplist.load(g)
		
		if (iOSversion == '11'):
			ns_keyed_archiver_obj = ccl_bplist.deserialise_NsKeyedArchiver(plistg)	
			newbytearray = ns_keyed_archiver_obj
		if (iOSversion == '12'):
			ns_keyed_archiver_objg = ccl_bplist.deserialise_NsKeyedArchiver(plistg)
			newbytearray = (ns_keyed_archiver_objg["NS.data"])
		if (iOSversion == '13'):
			ns_keyed_archiver_objg = ccl_bplist.deserialise_NsKeyedArchiver(plistg)
			newbytearray = (ns_keyed_archiver_objg["NS.data"])

		dirtcount = dirtcount+1
			
		binfile = open(outpath+'/clean/C_Z_PK'+pkvplist, 'wb')
		binfile.write(newbytearray)
		binfile.close()	
		
		#add to dictionaries
		intentc['C_Z_PK'+pkvplist] = intentclass
		intentv['C_Z_PK'+pkvplist] = intententverb
		
		cleancount = cleancount+1

	h = open(outpath+'/StrucMetadata.html', 'w')	
	h.write('<html><body>')
	h.write('<h2>iOS ' + iOSversion + ' - KnowledgeC ZSTRUCTUREDMETADATA bplist report</h2>')
	h.write ('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
	h.write('<br/>')

	for filename in glob.glob(outpath+'/clean/*'+extension):	
		p = open(filename, 'rb')
		cfilename = os.path.basename(filename)
		plist = ccl_bplist.load(p)
		ns_keyed_archiver_obj = ccl_bplist.deserialise_NsKeyedArchiver(plist, parse_whole_structure=True)#deserialize clean
		#Get dictionary values
		A = intentc.get(cfilename)
		B = intentv.get(cfilename)
		
		if A is None:
			A = 'No value'
		if B is None:
			A = 'No value'
		
		#logfunc some values from clean bplist
		if iOSversion == '13':
			NSdata = (ns_keyed_archiver_obj['root']['intent']['backingStore']['bytes'])
		else:
			NSdata = (ns_keyed_archiver_obj["root"]["intent"]["backingStore"]["data"]["NS.data"])
		
		parsedNSData = ""
		#Default true
		if dump == True:	
			nsdata_file = outpath+'/clean/'+cfilename+'_nsdata.bin'
			binfile = open(nsdata_file, 'wb')
			if iOSversion == '13':
				binfile.write(ns_keyed_archiver_obj['root']['intent']['backingStore']['bytes'])
			else:
				binfile.write(ns_keyed_archiver_obj["root"]["intent"]["backingStore"]["data"]["NS.data"])
			binfile.close()
			messages = ParseProto(nsdata_file)
			messages_json_dump = json.dumps(messages, indent=4, sort_keys=True, ensure_ascii=False)
			parsedNSData = str(messages_json_dump).encode(encoding='UTF-8',errors='ignore')
		
		NSstartDate = ccl_bplist.convert_NSDate((ns_keyed_archiver_obj["root"]["dateInterval"]["NS.startDate"]))
		NSendDate = ccl_bplist.convert_NSDate((ns_keyed_archiver_obj["root"]["dateInterval"]["NS.endDate"]))
		NSduration = ns_keyed_archiver_obj["root"]["dateInterval"]["NS.duration"]
		Siri = ns_keyed_archiver_obj["root"]["_donatedBySiri"]
		
		h.write(cfilename)
		h.write('<br />')
		h.write('Intent Class: '+str(A))
		h.write('<br />')
		h.write('Intent Verb: '+str(B))
		h.write('<br />')
		h.write('<table>')
		
		
		h.write('<tr>')
		h.write('<th>Data type</th>')
		h.write('<th>Value</th>')
		h.write('</tr>')
		
		#Donated by Siri
		h.write('<tr>')
		h.write('<td>Siri</td>')
		h.write('<td>'+str(Siri)+'</td>')
		h.write('</tr>')
			
		#NSstartDate
		h.write('<tr>')
		h.write('<td>NSstartDate</td>')
		h.write('<td>'+str(NSstartDate)+' Z</td>')
		h.write('</tr>')
		
		#NSsendDate
		h.write('<tr>')
		h.write('<td>NSendDate</td>')
		h.write('<td>'+str(NSendDate)+' Z</td>')
		h.write('</tr>')
		
		#NSduration
		h.write('<tr>')
		h.write('<td>NSduration</td>')
		h.write('<td>'+str(NSduration)+'</td>')
		h.write('</tr>')
		
		#NSdata
		h.write('<tr>')
		h.write('<td>NSdata</td>')
		h.write('<td>'+str(NSdata)+'</td>')
		h.write('</tr>')

		#NSdata better formatting
		if parsedNSData:
			h.write('<tr>')
			h.write('<td>NSdata - Protobuf Decoded</td>')
			h.write('<td><pre id=\"json\">'+str(parsedNSData).replace('\\n', '<br>')+'</pre></td>')
			h.write('</tr>')
		else:
			#This will only run if -nd is used
			h.write('<tr>')
			h.write('<td>NSdata - Protobuf</td>')
			h.write('<td>'+str(NSdata).replace('\\n', '<br>')+'</td>')
			h.write('</tr>')	
		
		h.write('<table>')
		h.write('<br />')
		
		#logfunc(NSstartDate)
		#logfunc(NSendDate)
		#logfunc(NSduration)
		#logfunc(NSdata)
		#logfunc('')


	logfunc("")	
	logfunc("iOS - KnowledgeC ZSTRUCTUREDMETADATA bplist extractor")
	logfunc("By: @phillmoore & @AlexisBrignoni")
	logfunc("thinkdfir.com & abrignoni.com")
	logfunc("")
	logfunc("Bplists from the Z_DKINTENTMETADATAKEY__SERIALIZEDINTERACTION field.")
	logfunc("Exported bplists (dirty): "+str(dirtcount))
	logfunc("Exported bplists (clean): "+str(cleancount))
	logfunc("")
	logfunc(f'Triage report completed.')
	logfunc('Incepted bplist extractions in knowlwdgeC.db completed')
	
	logfunc(f'KnowledgeC.db App Usage executing')

	#outpath = reportfolderbase+'KnowledgeC App Use/'

	#connect sqlite databases
	db = sqlite3.connect(filefound[0])
	cursor = db.cursor()

	cursor.execute('''
	SELECT
	datetime(ZOBJECT.ZCREATIONDATE+978307200,'UNIXEPOCH', 'LOCALTIME') as "ENTRY CREATION", 
	CASE ZOBJECT.ZSTARTDAYOFWEEK 
		WHEN "1" THEN "Sunday"
		WHEN "2" THEN "Monday"
		WHEN "3" THEN "Tuesday"
		WHEN "4" THEN "Wednesday"
		WHEN "5" THEN "Thursday"
		WHEN "6" THEN "Friday"
		WHEN "7" THEN "Saturday"
	END "DAY OF WEEK",
	ZOBJECT.ZSECONDSFROMGMT/3600 AS "GMT OFFSET",
	datetime(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH', 'LOCALTIME') as "START", 
	datetime(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH', 'LOCALTIME') as "END", 
	(ZOBJECT.ZENDDATE-ZOBJECT.ZSTARTDATE) as "USAGE IN SECONDS",
	ZOBJECT.ZSTREAMNAME, 
	ZOBJECT.ZVALUESTRING
	FROM ZOBJECT
	WHERE ZSTREAMNAME IS "/app/inFocus" 
	ORDER BY "START"	''')

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	
	with open(reportfolderbase+'KnowledgeC/App Usage.html', 'w', encoding='utf8') as f:
		f.write('<html><body>')
		f.write('<h2>iOS ' + iOSversion + ' - KnowledgeC App Usage report</h2>')
		f.write(f'KnowledgeC App Usage entries: {usageentries}<br>')
		f.write(f'KnowledgeC located at: {filefound[0]}<br>')
		f.write('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
		f.write('<br/>')
		f.write('')
		f.write(f'<table>')
		f.write(f'<tr><td>Entry Creation</td><td>Day of Week</td><td>GMT Offset</td><td>Start</td><td>End</td><td>Usage in Seconds</td><td>ZSTREAMNAME</td><td>ZVALUESTRING</td></tr>')
		for row in all_rows:
			ec = row[0]
			dw = row[1]
			go = row[2]
			st = row[3]
			en = row[4]
			us = row[5]
			zs = row[6]
			zv = row[7]
			f.write(f'<tr><td>{ec}</td><td>{dw}</td><td>{go}</td><td>{st}</td><td>{en}</td><td>{us}</td><td>{zs}</td><td>{zv}</td></tr>')
		f.write(f'</table></body></html>')
	logfunc(f'KnowledgeC App Usage completed')
	logfunc(f'KnowledgeC App Activity Executing')			
	#connect sqlite databases
	db = sqlite3.connect(filefound[0])
	cursor = db.cursor()

	cursor.execute('''
	SELECT
	datetime(ZOBJECT.ZCREATIONDATE+978307200,'UNIXEPOCH', 'LOCALTIME') as "ENTRY CREATION", 
		CASE ZOBJECT.ZSTARTDAYOFWEEK 
		WHEN "1" THEN "Sunday"
		WHEN "2" THEN "Monday"
		WHEN "3" THEN "Tuesday"
		WHEN "4" THEN "Wednesday"
		WHEN "5" THEN "Thursday"
		WHEN "6" THEN "Friday"
		WHEN "7" THEN "Saturday"
	END "DAY OF WEEK",
	datetime(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH', 'LOCALTIME') as "START", 
	datetime(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH', 'LOCALTIME') as "END", 
	ZOBJECT.ZSTREAMNAME, 
	ZOBJECT.ZVALUESTRING,
	ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONACTIVITYMETADATAKEY__ACTIVITYTYPE AS "ACTIVITY TYPE",  
	ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONACTIVITYMETADATAKEY__TITLE as "TITLE", 
	datetime(ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONACTIVITYMETADATAKEY__EXPIRATIONDATE+978307200,'UNIXEPOCH', 'LOCALTIME') as "EXPIRATION DATE",
	ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONACTIVITYMETADATAKEY__ITEMRELATEDCONTENTURL as "CONTENT URL",
	datetime(ZSTRUCTUREDMETADATA.ZCOM_APPLE_CALENDARUIKIT_USERACTIVITY_DATE+978307200,'UNIXEPOCH', 'LOCALTIME')  as "CALENDAR DATE",
	datetime(ZSTRUCTUREDMETADATA.ZCOM_APPLE_CALENDARUIKIT_USERACTIVITY_ENDDATE+978307200,'UNIXEPOCH', 'LOCALTIME')  as "CALENDAR END DATE"
	FROM ZOBJECT
	left join ZSTRUCTUREDMETADATA on ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK
	left join ZSOURCE on ZOBJECT.ZSOURCE = ZSOURCE.Z_PK
	WHERE ZSTREAMNAME is "/app/activity" 
	ORDER BY "ENTRY CREATION"''')

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	
	with open(reportfolderbase+'KnowledgeC/App Activity.html', 'w', encoding='utf8') as f:
		f.write('<html><body>')
		f.write('<h2>iOS ' + iOSversion + ' - KnowledgeC App Activity report</h2>')
		f.write(f'KnowledgeC App Activity entries: {usageentries}<br>')
		f.write(f'KnowledgeC located at: {filefound[0]}<br>')
		f.write('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
		f.write('<br/>')
		f.write('')
		f.write(f'<table>')
		f.write(f'<tr><td>Entry Creation</td><td>Day of Week</td><td>Start</td><td>End</td><td>ZSTREAMNAME</td><td>ZVALUESTRING</td><td>Activity Type</td><td>Title</td><td>Expiration Date</td><td>Content URL</td><td>Calendar Date</td><td>Calendar End Date</td></tr>')
		for row in all_rows:
			ec = row[0]
			dw = row[1]
			st = row[2]
			en = row[3]
			zs = row[4]
			zv = row[5]
			tl = row[6]
			ed = row[7]
			cu = row[8]
			cd = row[9]
			ce = row[10]
			ced = row[11]
			f.write(f'<tr><td>{ec}</td><td>{dw}</td><td>{st}</td><td>{en}</td><td>{zs}</td><td>{zv}</td><td>{tl}</td><td>{ed}</td><td>{cu}</td><td>{cd}</td><td>{ce}</td><td>{ced}</td></tr>')
		f.write(f'</table></body></html>')
	logfunc(f'KnowledgeC App Activity completed')
	
	logfunc(f'KnowledgeC App in Focus executing')
	db = sqlite3.connect(filefound[0])
	cursor = db.cursor()

	cursor.execute('''
	SELECT
	ZOBJECT.ZVALUESTRING AS "BUNDLE ID", 
	(ZOBJECT.ZENDDATE-ZOBJECT.ZSTARTDATE) as "USAGE IN SECONDS",
	CASE ZOBJECT.ZSTARTDAYOFWEEK 
	    WHEN "1" THEN "Sunday"
	    WHEN "2" THEN "Monday"
	    WHEN "3" THEN "Tuesday"
	    WHEN "4" THEN "Wednesday"
	    WHEN "5" THEN "Thursday"
	    WHEN "6" THEN "Friday"
	    WHEN "7" THEN "Saturday"
	END "DAY OF WEEK",
	ZOBJECT.ZSECONDSFROMGMT/3600 AS "GMT OFFSET",
	DATETIME(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH') as "START", 
	DATETIME(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH') as "END",
	DATETIME(ZOBJECT.ZCREATIONDATE+978307200,'UNIXEPOCH') as "ENTRY CREATION",	
	ZOBJECT.Z_PK AS "ZOBJECT TABLE ID" 
	FROM ZOBJECT
	WHERE ZSTREAMNAME IS "/app/inFocus"''')

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	
	with open(reportfolderbase+'KnowledgeC/App in Focus.html', 'w', encoding='utf8') as f:
		f.write('<html><body>')
		f.write('<h2>iOS ' + iOSversion + ' - KnowledgeC App App in Focus report</h2>')
		f.write(f'KnowledgeC App in Focus entries: {usageentries}<br>')
		f.write(f'KnowledgeC located at: {filefound[0]}<br>')
		f.write('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
		f.write('<br/>')
		f.write('')
		f.write(f'<table>')
		f.write(f'<tr><td>Bundle ID</td><td>Usage in Seconds</td><td>Day of the Week</td><td>GMT Offset</td><td>Start</td><td>End</td><td>Entry Creation</td><td>ZOBJECT Table ID</td></tr>')
		for row in all_rows:
			f.write(f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td></tr>')
		f.write(f'</table></body></html>')
		logfunc(f'KnowledgeC App in Focus completed')
	
	logfunc(f'KnowledgeC App Battery Level executing')
	cursor.execute('''
	SELECT
			ZOBJECT.ZVALUEDOUBLE as "BATTERY LEVEL",
			(ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) AS "USAGE IN SECONDS", 
			CASE ZOBJECT.ZSTARTDAYOFWEEK 
				WHEN "1" THEN "Sunday"
				WHEN "2" THEN "Monday"
				WHEN "3" THEN "Tuesday"
				WHEN "4" THEN "Wednesday"
				WHEN "5" THEN "Thursday"
				WHEN "6" THEN "Friday"
				WHEN "7" THEN "Saturday"
			END "DAY OF WEEK",
			ZOBJECT.ZSECONDSFROMGMT/3600 AS "GMT OFFSET",
			DATETIME(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH') as "START", 
			DATETIME(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH') as "END",
			DATETIME(ZOBJECT.ZCREATIONDATE+978307200,'UNIXEPOCH') as "ENTRY CREATION",     
			ZOBJECT.Z_PK AS "ZOBJECT TABLE ID"
		FROM
			ZOBJECT 
			LEFT JOIN
				ZSTRUCTUREDMETADATA 
				ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK 
			LEFT JOIN
				ZSOURCE 
				ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK 
		WHERE
			ZSTREAMNAME LIKE "/device/BatteryPercentage"
	''')

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	
	with open(reportfolderbase+'KnowledgeC/Battery Level.html', 'w', encoding='utf8') as f:
		f.write('<html><body>')
		f.write('<h2>KnowledgeC Battery Level report</h2>')
		f.write(f'KnowledgeC Battery Level entries: {usageentries}<br>')
		f.write(f'KnowledgeC Battery Level located at: {filefound[0]}<br>')
		f.write('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
		f.write('<br/>')
		f.write('')
		f.write(f'<table>')
		f.write(f'<tr><td>Battery Level</td><td>Usage in Seconds</td><td>Day of the Week</td><td>GMT Offset</td><td>Start</td><td>End</td><td>Entry Creation</td><td>ZOBJECT Table ID</td></tr>')
		for row in all_rows:
			f.write(f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td></tr>')
		f.write(f'</table></body></html>')
		logfunc(f'KnowledgeC App Battery Level completed')
	
	logfunc(f'KnowledgeC Apps Installed executing')
	cursor.execute('''
	SELECT
			ZOBJECT.ZVALUESTRING AS "BUNDLE ID",
			CASE ZOBJECT.ZSTARTDAYOFWEEK 
				WHEN "1" THEN "Sunday"
				WHEN "2" THEN "Monday"
				WHEN "3" THEN "Tuesday"
				WHEN "4" THEN "Wednesday"
				WHEN "5" THEN "Thursday"
				WHEN "6" THEN "Friday"
				WHEN "7" THEN "Saturday"
			END "DAY OF WEEK",
			ZOBJECT.ZSECONDSFROMGMT/3600 AS "GMT OFFSET",
			DATETIME(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH') as "START", 
			DATETIME(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH') as "END",
			DATETIME(ZOBJECT.ZCREATIONDATE+978307200,'UNIXEPOCH') as "ENTRY CREATION",	
			ZOBJECT.Z_PK AS "ZOBJECT TABLE ID"
		FROM
		   ZOBJECT 
		   LEFT JOIN
		      ZSTRUCTUREDMETADATA 
		      ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK 
		   LEFT JOIN
		      ZSOURCE 
		      ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK 
		WHERE ZSTREAMNAME is "/app/install"
	''')

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	
	with open(reportfolderbase+'KnowledgeC/Apps Installed.html', 'w', encoding='utf8') as f:
		f.write('<html><body>')
		f.write('<h2>KnowledgeC Apps Installed report</h2>')
		f.write(f'KnowledgeC Apps Installed : {usageentries}<br>')
		f.write(f'KnowledgeC Apps Installed located at: {filefound[0]}<br>')
		f.write('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
		f.write('<br/>')
		f.write('')
		f.write(f'<table>')
		f.write(f'<tr><td>Bundle ID</td><td>Day of the Week</td><td>GMT Offset</td><td>Start</td><td>End</td><td>Entry Creation</td></tr>')
		for row in all_rows:
			f.write(f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td></tr>')
		f.write(f'</table></body></html>')
		logfunc(f'KnowledgeC Apps Installed completed')

	logfunc(f'KnowledgeC Device Locked executing')
	cursor.execute('''
	SELECT
			CASE ZOBJECT.ZVALUEINTEGER
				WHEN '0' THEN 'UNLOCKED' 
				WHEN '1' THEN 'LOCKED' 
			END "IS LOCKED",
			(ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) AS "USAGE IN SECONDS",  
			CASE ZOBJECT.ZSTARTDAYOFWEEK 
				WHEN "1" THEN "Sunday"
				WHEN "2" THEN "Monday"
				WHEN "3" THEN "Tuesday"
				WHEN "4" THEN "Wednesday"
				WHEN "5" THEN "Thursday"
				WHEN "6" THEN "Friday"
				WHEN "7" THEN "Saturday"
			END "DAY OF WEEK",
			ZOBJECT.ZSECONDSFROMGMT/3600 AS "GMT OFFSET",
			DATETIME(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH') as "START", 
			DATETIME(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH') as "END",
			DATETIME(ZOBJECT.ZCREATIONDATE+978307200,'UNIXEPOCH') as "ENTRY CREATION", 
			ZOBJECT.Z_PK AS "ZOBJECT TABLE ID" 
		FROM
			ZOBJECT 
			LEFT JOIN
				ZSTRUCTUREDMETADATA 
				ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK 
			LEFT JOIN
				ZSOURCE 
				ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK 
		WHERE
			ZSTREAMNAME LIKE "/device/isLocked"
	''')

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
		
	with open(reportfolderbase+'KnowledgeC/Device Locked.html', 'w', encoding='utf8') as f:
		f.write('<html><body>')
		f.write('<h2>KnowledgeC Device Locked report</h2>')
		f.write(f'KnowledgeC Device Locked: {usageentries}<br>')
		f.write(f'KnowledgeC Device Locked located at: {filefound[0]}<br>')
		f.write('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
		f.write('<br/>')
		f.write('')
		f.write(f'<table>')
		f.write(f'<tr><td>Is Locked?</td><td>Usage in Seconds</td><td>Day of the Week</td><td>GMT Offset</td><td>Start</td><td>End</td><td>Entry Creation</td></tr>')
		for row in all_rows:
			f.write(f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td></tr>')
		f.write(f'</table></body></html>')
		logfunc(f'KnowledgeC Device Locked completed')

	logfunc(f'KnowledgeC Plugged In executing')
	cursor.execute('''
	SELECT
			CASE
			ZOBJECT.ZVALUEINTEGER
				WHEN '0' THEN 'UNPLUGGED' 
				WHEN '1' THEN 'PLUGGED IN' 
			END "IS PLUGGED IN",
			(ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) AS "USAGE IN SECONDS",  
			CASE ZOBJECT.ZSTARTDAYOFWEEK 
				WHEN "1" THEN "Sunday"
				WHEN "2" THEN "Monday"
				WHEN "3" THEN "Tuesday"
				WHEN "4" THEN "Wednesday"
				WHEN "5" THEN "Thursday"
				WHEN "6" THEN "Friday"
				WHEN "7" THEN "Saturday"
			END "DAY OF WEEK",
			ZOBJECT.ZSECONDSFROMGMT/3600 AS "GMT OFFSET",
			DATETIME(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH') as "START", 
			DATETIME(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH') as "END",
			DATETIME(ZOBJECT.ZCREATIONDATE+978307200,'UNIXEPOCH') as "ENTRY CREATION", 
			ZOBJECT.Z_PK AS "ZOBJECT TABLE ID" 
		FROM
			ZOBJECT 
			LEFT JOIN
				ZSTRUCTUREDMETADATA 
				ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK 
			LEFT JOIN
				ZSOURCE 
				ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK 
		WHERE
			ZSTREAMNAME LIKE "/device/isPluggedIn"
	''')

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
		
	with open(reportfolderbase+'KnowledgeC/Plugged In.html', 'w', encoding='utf8') as f:
		f.write('<html><body>')
		f.write('<h2>KnowledgeC Plugged In report</h2>')
		f.write(f'KnowledgeC Device Plugged In entries: {usageentries}<br>')
		f.write(f'KnowledgeC Device Plugged In located at: {filefound[0]}<br>')
		f.write('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
		f.write('<br/>')
		f.write('')
		f.write(f'<table>')
		f.write(f'<tr><td>Is Plugged In?</td><td>Usage in Seconds</td><td>Day of the Week</td><td>GMT Offset</td><td>Start</td><td>End</td><td>Entry Creation</td></tr>')
		for row in all_rows:
			f.write(f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td></tr>')
		f.write(f'</table></body></html>')
		logfunc(f'KnowledgeC Plugged In completed')

def mib(filefound):
	logfunc(f'Mobile Installation Logs function executing.')
	#initialize counters
	counter = 0
	filescounter = 0

	#Month to numeric with leading zero when month < 10 function
	#Function call: month = month_converter(month)
	def month_converter(month):
		months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
		month = months.index(month) + 1
		if (month < 10):
			month = f"{month:02d}"
		return month

	#Day with leading zero if day < 10 function
	#Functtion call: day = day_converter(day)
	def day_converter(day):	
		day = int(day)
		if (day < 10):
			day = f"{day:02d}"
		return day
	
	#Create folders for this function
	os.makedirs(reportfolderbase+'Mobile_Installation_Logs/')
	#Create sqlite databases
	db = sqlite3.connect(reportfolderbase+'Mobile_Installation_Logs/mib.db')

	cursor = db.cursor()

	#Create table fileds for destroyed, installed, moved and made identifiers.

	cursor.execute('''

		CREATE TABLE dimm(time_stamp TEXT, action TEXT, bundle_id TEXT, 

						  path TEXT)

	''')

	db.commit()

	for filename in filefound:
		file = open(filename, 'r', encoding='utf8' )
		filescounter = filescounter + 1
		for line in file:
			counter = counter+1
			matchObj = re.search( r"(Install Successful for)", line) #Regex for installed applications
			if matchObj:
				actiondesc = "Install successful"
				matchObj1 = re.search( r"(?<= for \(Placeholder:)(.*)(?=\))", line) #Regex for bundle id
				matchObj2 = re.search( r"(?<= for \(Customer:)(.*)(?=\))", line) #Regex for bundle id	
				matchObj3 = re.search( r"(?<= for \(System:)(.*)(?=\))", line) #Regex for bundle id	
				matchObj4 = re.search( r"(?<= for \()(.*)(?=\))", line) #Regex for bundle id			
				if matchObj1:
					bundleid = matchObj1.group(1)
				elif matchObj2:
					bundleid = matchObj2.group(1)
				elif matchObj3:
					bundleid = matchObj3.group(1)
				elif matchObj4:
					bundleid = matchObj4.group(1)
					
				matchObj = re.search( r"(?<=^)(.*)(?= \[)", line) #Regex for timestamp
				if matchObj:
					timestamp = matchObj.group(1)
					weekday, month, day, time, year = (str.split(timestamp))
					day = day_converter(day)
					month = month_converter(month)
					inserttime = str(year)+ '-'+ str(month) + '-' + str(day) + ' ' + str(time)
					#logfunc(inserttime)
					#logfunc(month)
					#logfunc(day)
					#logfunc(year)
					#logfunc(time)
					#logfunc ("Timestamp: ", timestamp)
				
				#logfunc(inserttime, actiondesc, bundleid)
				
				#insert to database
				cursor = db.cursor()
				datainsert = (inserttime, actiondesc, bundleid, '' ,)
				cursor.execute('INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)', datainsert)
				db.commit()
				
				#logfunc()
					
			
			matchObj = re.search( r"(Destroying container with identifier)", line) #Regex for destroyed containers
			if matchObj:
				actiondesc = "Destroying container"
				#logfunc(actiondesc)
				#logfunc("Destroyed containers:")
				matchObj = re.search( r"(?<=identifier )(.*)(?= at )", line) #Regex for bundle id
				if matchObj:
					bundleid = matchObj.group(1)
					#logfunc ("Bundle ID: ", bundleid )
			
				matchObj = re.search( r"(?<=^)(.*)(?= \[)", line) #Regex for timestamp
				if matchObj:
					timestamp = matchObj.group(1)
					weekday, month, day, time, year = (str.split(timestamp))
					day = day_converter(day)
					month = month_converter(month)
					inserttime = str(year)+ '-'+ str(month) + '-' + str(day) + ' ' + str(time)
					#logfunc(inserttime)
					#logfunc(month)
					#logfunc(day)
					#logfunc(year)
					#logfunc(time)
					#logfunc ("Timestamp: ", timestamp)
				
				matchObj = re.search( r"(?<= at )(.*)(?=$)", line) #Regex for path
				if matchObj:
					path = matchObj.group(1)
					#logfunc ("Path: ", matchObj.group(1))
				
			
				#logfunc(inserttime, actiondesc, bundleid, path)			
				
				#insert to database
				cursor = db.cursor()
				datainsert = (inserttime, actiondesc, bundleid, path ,)
				cursor.execute('INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)', datainsert)
				db.commit()
				
				#logfunc()
				

			matchObj = re.search( r"(Data container for)", line) #Regex Moved data containers
			if matchObj:
				actiondesc = "Data container moved"
				#logfunc(actiondesc)
				#logfunc("Data container moved:")
				matchObj = re.search( r"(?<=for )(.*)(?= is now )", line) #Regex for bundle id
				if matchObj:
					bundleid = matchObj.group(1)
					#logfunc ("Bundle ID: ", bundleid )
			
				matchObj = re.search( r"(?<=^)(.*)(?= \[)", line) #Regex for timestamp
				if matchObj:
					timestamp = matchObj.group(1)
					weekday, month, day, time, year = (str.split(timestamp))
					day = day_converter(day)
					month = month_converter(month)
					inserttime = str(year)+ '-'+ str(month) + '-' + str(day) + ' ' + str(time)
					#logfunc(inserttime)
					#logfunc(month)
					#logfunc(day)
					#logfunc(year)
					#logfunc(time)
					#logfunc ("Timestamp: ", timestamp)
				
				matchObj = re.search( r"(?<= at )(.*)(?=$)", line) #Regex for path
				if matchObj:
					path = matchObj.group(1)
					#logfunc ("Path: ", matchObj.group(1))
					
				#logfunc(inserttime, actiondesc, bundleid, path)			
				
				#insert to database
				cursor = db.cursor()
				datainsert = (inserttime, actiondesc, bundleid, path ,)
				cursor.execute('INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)', datainsert)
				db.commit()
				
				#logfunc()
				
			matchObj = re.search( r"(Made container live for)", line) #Regex for made container
			if matchObj:
				actiondesc = "Made container live"
				#logfunc(actiondesc)
				#logfunc("Made container:")
				matchObj = re.search( r"(?<=for )(.*)(?= at)", line) #Regex for bundle id
				if matchObj:
					bundleid = matchObj.group(1)
					#logfunc ("Bundle ID: ", bundleid )
			
				matchObj = re.search( r"(?<=^)(.*)(?= \[)", line) #Regex for timestamp
				if matchObj:
					timestamp = matchObj.group(1)
					weekday, month, day, time, year = (str.split(timestamp))
					day = day_converter(day)
					month = month_converter(month)
					inserttime = str(year)+ '-'+ str(month) + '-' + str(day) + ' ' + str(time)
					#logfunc(inserttime)
					#logfunc(month)
					#logfunc(day)
					#logfunc(year)
					#logfunc(time)
					#logfunc ("Timestamp: ", timestamp)
				
				matchObj = re.search( r"(?<= at )(.*)(?=$)", line) #Regex for path
				if matchObj:
					path = matchObj.group(1)
					#logfunc ("Path: ", matchObj.group(1))
				#logfunc(inserttime, actiondesc, bundleid, path)			
				
				#insert to database
				cursor = db.cursor()
				datainsert = (inserttime, actiondesc, bundleid, path ,)
				cursor.execute('INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)', datainsert)
				db.commit()
				
			matchObj = re.search( r"(Uninstalling identifier )", line) #Regex for made container
			if matchObj:
				actiondesc = "Uninstalling identifier"
				#logfunc(actiondesc)
				#logfunc("Uninstalling identifier")
				matchObj = re.search( r"(?<=Uninstalling identifier )(.*)", line) #Regex for bundle id
				if matchObj:
					bundleid = matchObj.group(1)
					#logfunc ("Bundle ID: ", bundleid )
			
				matchObj = re.search( r"(?<=^)(.*)(?= \[)", line) #Regex for timestamp
				if matchObj:
					timestamp = matchObj.group(1)
					weekday, month, day, time, year = (str.split(timestamp))
					day = day_converter(day)
					month = month_converter(month)
					inserttime = str(year)+ '-'+ str(month) + '-' + str(day) + ' ' + str(time)
					#logfunc(inserttime)
					#logfunc(month)
					#logfunc(day)
					#logfunc(year)
					#logfunc(time)
					#logfunc ("Timestamp: ", timestamp)
				
				#insert to database
				cursor = db.cursor()
				datainsert = (inserttime, actiondesc, bundleid, '' ,)
				cursor.execute('INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)', datainsert)
				db.commit()

			matchObj = re.search( r"(main: Reboot detected)", line) #Regex for reboots
			if matchObj:
				actiondesc = "Reboot detected"
				#logfunc(actiondesc)		
				matchObj = re.search( r"(?<=^)(.*)(?= \[)", line) #Regex for timestamp
				if matchObj:
					timestamp = matchObj.group(1)
					weekday, month, day, time, year = (str.split(timestamp))
					day = day_converter(day)
					month = month_converter(month)
					inserttime = str(year)+ '-'+ str(month) + '-' + str(day) + ' ' + str(time)
					#logfunc(inserttime)
					#logfunc(month)
					#logfunc(day)
					#logfunc(year)
					#logfunc(time)
					#logfunc ("Timestamp: ", timestamp)
				
				#insert to database
				cursor = db.cursor()
				datainsert = (inserttime, actiondesc, '', '' ,)
				cursor.execute('INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)', datainsert)
				db.commit()			
				
			matchObj = re.search( r"(Attempting Delta patch update of )", line) #Regex for Delta patch
			if matchObj:
				actiondesc = "Attempting Delta patch"
				#logfunc(actiondesc)
				#logfunc("Made container:")
				matchObj = re.search( r"(?<=Attempting Delta patch update of )(.*)(?= from)", line) #Regex for bundle id
				if matchObj:
					bundleid = matchObj.group(1)
					#logfunc ("Bundle ID: ", bundleid )
			
				matchObj = re.search( r"(?<=^)(.*)(?= \[)", line) #Regex for timestamp
				if matchObj:
					timestamp = matchObj.group(1)
					weekday, month, day, time, year = (str.split(timestamp))
					day = day_converter(day)
					month = month_converter(month)
					inserttime = str(year)+ '-'+ str(month) + '-' + str(day) + ' ' + str(time)
					#logfunc(inserttime)
					#logfunc(month)
					#logfunc(day)
					#logfunc(year)
					#logfunc(time)
					#logfunc ("Timestamp: ", timestamp)
				
				matchObj = re.search( r"(?<= from )(.*)", line) #Regex for path
				if matchObj:
					path = matchObj.group(1)
					#logfunc ("Path: ", matchObj.group(1))
				#logfunc(inserttime, actiondesc, bundleid, path)			
				
				#insert to database
				cursor = db.cursor()
				datainsert = (inserttime, actiondesc, bundleid, path ,)
				cursor.execute('INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)', datainsert)
				db.commit()
				
				#logfunc()
	try:
		logfunc (f'Logs processed: {filescounter}')
		logfunc (f'Lines processed: {counter}')
		logfunc ('')
		file.close


		
		#Initialize counters
		totalapps = 0
		installedcount = 0
		uninstallcount = 0
		historicalcount = 0
		sysstatecount = 0
		
		#created folders for reports and sub folders for App history, App state
		os.makedirs(reportfolderbase+'Mobile_Installation_Logs/Apps_State/')
		os.makedirs(reportfolderbase+'Mobile_Installation_Logs/Apps_Historical/')
		os.makedirs(reportfolderbase+'Mobile_Installation_Logs/System_State/')
		
		#Initialize text file reports for installed and unistalled apps
		f1=open(reportfolderbase+'Mobile_Installation_Logs/Apps_State/UninstalledApps.txt', 'w+', encoding="utf8")
		f2=open(reportfolderbase+'Mobile_Installation_Logs/Apps_State/InstalledApps.txt', 'w+', encoding="utf8")
		f4=open(reportfolderbase+'Mobile_Installation_Logs/System_State/SystemState.txt', 'w+', encoding="utf8")
		
		
		#Initialize database connection
		db = sqlite3.connect(reportfolderbase+'Mobile_Installation_Logs/mib.db')
		
		cursor = db.cursor()
		
		#Query to create installed and uninstalled app reports
		cursor.execute('''SELECT distinct bundle_id from dimm''')
		all_rows = cursor.fetchall()
		for row in all_rows:
			#logfunc(row[0])
			distinctbundle = row[0]
			cursor.execute('''SELECT * from dimm where bundle_id=? order by time_stamp desc limit 1''', (distinctbundle,))
			all_rows_iu = cursor.fetchall()
			for row in all_rows_iu:
				#logfunc(row[0], row[1], row[2], row[3])
				if row[2] == '':
					continue
				elif row[1] == 'Destroying container':
					#logfunc(row[0], row[1], row[2], row[3])
					uninstallcount = uninstallcount + 1
					totalapps = totalapps + 1
					#tofile1 = row[0] + ' ' + row[1] + ' ' + row[2] + ' ' + row[3] + '\n'
					tofile1 = row[2] +  '\n'
					f1.write(tofile1)
					#logfunc()
				elif row[1] == 'Uninstalling identifier':
					#logfunc(row[0], row[1], row[2], row[3])
					uninstallcount = uninstallcount + 1
					totalapps = totalapps + 1
					#tofile1 = row[0] + ' ' + row[1] + ' ' + row[2] + ' ' + row[3] + '\n'
					tofile1 = row[2] +  '\n'
					f1.write(tofile1)
					#logfunc()
				else:
					#logfunc(row[0], row[1], row[2], row[3])
					tofile2 = row[2] + '\n'
					
					f2.write(tofile2)
					installedcount = installedcount + 1	
					totalapps = totalapps + 1
		
		f1.close()
		f2.close()
		
		list =[]
		path = reportfolderbase+'/Mobile_Installation_Logs/Apps_State/'
		files = os.listdir(path)
		for name in files:
			list.append(f'<a href = "./{name}" target="content">{name}</a>')

		filedatahtml = open(path+'/Apps State.html', mode='a+')
		filedatahtml.write('Data from Mobile Installation Logs - App State / Installed and Uninstalled Apps <br>')
		filedatahtml.write(f'Data location: {filename} <br><br>')
		list.sort()
		for items in list:
			filedatahtml.write(items)
			filedatahtml.write('<br>')
		filedatahtml.close()
				
		#Query to create historical report per app
					
		cursor.execute('''SELECT distinct bundle_id from dimm''')
		all_rows = cursor.fetchall()
		for row in all_rows:
			#logfunc(row[0])
			distinctbundle = row[0]
			if row[0] == '':
				continue
			else:
				f3=open(reportfolderbase+'Mobile_Installation_Logs/Apps_Historical/' + distinctbundle + '.txt', 'w+', encoding="utf8") #Create historical app report per app
				cursor.execute('''SELECT * from dimm where bundle_id=? order by time_stamp DESC''', (distinctbundle,)) #Query to create app history per bundle_id
				all_rows_hist = cursor.fetchall()
				for row in all_rows_hist:
					#logfunc(row[0], row[1], row[2], row[3])
					tofile3 = row[0] + ' ' + row[1] + ' ' + row[2] + ' ' + row[3] + '\n'
					f3.write(tofile3)			
			f3.close()
			historicalcount = historicalcount + 1
		
		list =[]
		path = reportfolderbase+'/Mobile_Installation_Logs/Apps_Historical/'
		files = os.listdir(path)
		for name in files:
			list.append(f'<a href = "./{name}" target="content">{name}</a>')

		filedatahtml = open(path+'Apps Historical.html', mode='a+')
		filedatahtml.write('Data from Mobile Installation Logs - Apps Historical <br>')
		filedatahtml.write(f'Data location: {filename} <br><br>')
		list.sort()
		for items in list:
			filedatahtml.write(items)
			filedatahtml.write('<br>')
		filedatahtml.close()
		
		#Query to create system events
		
		path = reportfolderbase+'/Mobile_Installation_Logs/System_State/'
		filedatahtml = open(path+'System State.html', mode='a+')
		filedatahtml.write('Data from Mobile Installation Logs - System State / Reboots <br>')
		filedatahtml.write(f'Data location: {filename} <br><br>')
					
		cursor.execute('''SELECT * from dimm where action ='Reboot detected' order by time_stamp DESC''')
		all_rows = cursor.fetchall()
		for row in all_rows:
			#logfunc(row[0])
			#logfunc(row[0], row[1], row[2], row[3])
			tofile4 = row[0] + ' ' + row[1] + ' ' + row[2] + ' ' + row[3] + '\n'
			f4.write(tofile4)
			filedatahtml.write(tofile4+'<br>')
			sysstatecount = sysstatecount + 1		
			
		filedatahtml.close()	
					
		logfunc (f'Total apps: {totalapps}')
		logfunc (f'Total installed apps: {installedcount}')
		logfunc (f'Total uninstalled apps: {uninstallcount}')
		logfunc (f'Total historical app reports: {historicalcount}')
		logfunc (f'Total system state events: {sysstatecount}')
		logfunc (f'Mobile Installation Logs function completed.')
		f1.close()
		f2.close()
		f4.close()

	except:
		logfunc(f'Log files not found in {filefound}')
	
def wireless(filefound):
	logfunc(f'Cellular Wireless files function executing')
	os.makedirs(reportfolderbase+'Cellular Wireless Info/')
	for filepath in filefound:
		basename = os.path.basename(filepath)
		if basename =='com.apple.commcenter.device_specific_nobackup.plist' or basename =='com.apple.commcenter.plist':	
			f =open(reportfolderbase+'Cellular Wireless Info/'+basename+'.html','w')
			#header html mas tabla
			f.write('<html>')
			f.write(f'<p><body><table>')
			f.write('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
			f.write(f'<tr><td colspan="2">{basename}</td></tr>')
			p = open(filepath, 'rb')
			plist = plistlib.load(p)
			for key, val in plist.items():
				f.write(f'<tr><td>{key}</td><td>{val}</td></tr>')
			f.write(f'</table></body></html>')
			f.close()
	logfunc(f'Cellular Wireless files function completed')
	
def iconstate(filefound):
	logfunc(f'Iconstate function executing.')
	os.makedirs(reportfolderbase+'Icon Positions/')
	f =open(reportfolderbase+'Icon Positions/Icon Positions.txt','w')
	g =open(reportfolderbase+'Icon Positions/Icon Positons.html','w')
	g.write('<html>')
	p = open(filefound[0], 'rb')
	plist = plistlib.load(p)
	for key, val in plist.items():
		f.write(f'{key} -> {val}{nl}')
		if key == 'buttonBar':
			bbar = val
		elif key == 'iconLists':
			icon = val
	f.close()
	for x in range(0, len(icon)):
		page = icon[x]
		g.write(f'<p><table><body>')
		g.write('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
		g.write(f'<tr> <td colspan="4"> Icons screen #{x}</td>')
		for y in range(0, len(page)):
			rows = page[y]
			if (y == 0) or (y % 4 == 0):
				g.write('</tr><tr>')			
			g.write(f'<td width = 25%>{rows}</td>')		
		g.write('</tr></table>')
	
	#do bottom bar
	g.write(f'<p><table><tr> <td colspan="4"> Icons bottom bar</td></tr><tr>')
	for x in range(0, len(bbar)):			
		g.write(f'<td width = 25%>{bbar[x]}</td>')		
	g.write('</tr></table>')
	
	g.write('</html>')
	g.close()
	
	logfunc('Screens: '+str(len(icon)))
	logfunc('Icons in bottom bar: '+str(len(bbar)))
	logfunc(f'Iconstate function completed.')
	
def lastbuild(filefound):
	global versionf
	versionnum = 0
	logfunc(f'Lastbuild function executing.')
	os.makedirs(reportfolderbase+'Build Info/')
	f =open(reportfolderbase+'Build Info/LastBuildInfo.plist.txt','w')
	p = open(filefound[0], 'rb')
	plist = plistlib.load(p)
	
	#create html headers
	filedatahtml = open(reportfolderbase+'Build Info/'+'Build_Info.html', mode='a+')
	filedatahtml.write('<html><body>')
	filedatahtml.write('<h2>Last Build Report </h2>')
	filedatahtml.write ('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
	filedatahtml.write('<table>')
	filedatahtml.write(f'<tr><td colspan = "2">{filefound[0]}</td></tr>')
	filedatahtml.write('<tr><td>Key</td><td>Value</td></tr>')
	
	
	for key, val in plist.items():
		f.write(f'{key} -> {val}{nl}')
		filedatahtml.write(f'<tr><td>{key}</td><td>{val}</td></tr>')
		if key == ('ProductVersion'):
			versionnum = val[0:2]		
			if versionnum in ('11','12','13'):
				versionf = versionnum 
				logfunc(f'iOS version is: {versionf}')
			else:
				versionf = 'Unknown'	
	f.close()
	
	#close html footer
	filedatahtml.write('</table></html>')
	filedatahtml.close()
	logfunc(f'Lastbuild function completed.')

def iOSNotifications11(filefound):
	logfunc(f'iOSNotifications 11 function executing.')
	
	count = 0
	notdircount = 0
	exportedbplistcount = 0
	unix = datetime.datetime(1970, 1, 1)  # UTC
	cocoa = datetime.datetime(2001, 1, 1)  # UTC
	delta = cocoa - unix 

	with open('NotificationParams.txt', 'r') as f:
		notiparams = [line.strip() for line in f]	
		
	pathfound = 0
	count = 0
	notdircount = 0
	exportedbplistcount = 0

	pathfound = str(filefound[0])

	if pathfound == 0:
		logfunc("No PushStore directory located")
	else:
		folder = (reportfolderbase+'iOS 11 Notifications/') #add the date thing from phill
		os.makedirs( folder )
		#logfunc("Processing:")
		for filename in glob.iglob(pathfound+'\**', recursive=True):
			if os.path.isfile(filename): # filter dirs
				file_name = os.path.splitext(os.path.basename(filename))[0]
					#get extension and iterate on those files
					#file_extension = os.path.splitext(filename)
					#logfunc(file_extension)
					#create directory
				if filename.endswith('pushstore'):
						#create directory where script is running from
					logfunc (filename) #full path
					notdircount = notdircount + 1				
						#logfunc (os.path.basename(file_name)) #filename with  no extension
					openplist = (os.path.basename(os.path.normpath(filename))) #filename with extension
						#logfunc (openplist)
						#bundlepath = (os.path.basename(os.path.dirname(filename)))#previous directory
					bundlepath = file_name
					appdirect = (folder + "\\"+ bundlepath) 
						#logfunc(appdirect)
					os.makedirs( appdirect )
						
						#open the plist
					p = open(filename, 'rb')
					plist = ccl_bplist.load(p)
					plist2 = plist["$objects"]

					long = len(plist2)
					#logfunc (long)
					h = open('./'+appdirect+'/DeliveredNotificationsReport.html', 'w') #write report
					h.write('<html><body>')
					h.write('<h2>iOS Delivered Notifications Triage Report </h2>')
					h.write(filename)
					h.write('<br/>')
					h.write ('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
					h.write('<br/>')
						
					h.write('<button onclick="hideRows()">Hide rows</button>')
					h.write('<button onclick="showRows()">Show rows</button>')
						
					f = open("script.txt")
					for line in f:
						h.write(line)
					f.close()
						
					h.write('<br>')
					h.write('<table name="hide">')
					h.write('<tr name="hide">')
					h.write('<th>Data type</th>')
					h.write('<th>Value</th>')
					h.write('</tr>')
										
					h.write('<tr name="hide">')
					h.write('<td>Plist</td>')
					h.write('<td>Initial Values</td>')
					h.write('</tr>')
						
					test = 0
					for i in range (0, long):
						try:
							if (plist2[i]['$classes']):
								h.write('<tr name="hide">')
								h.write('<td>$classes</td>')
								ob6 = str(plist2[i]['$classes'])
								h.write('<td>')
								h.write(str(ob6))
								h.write('</td>')
								h.write('</tr>')
								test = 1
						except:
							pass
						try:
							if (plist2[i]['$class']):
								h.write('<tr name="hide">')
								h.write('<td>$class</td>')
								ob5 = str(plist2[i]['$class'])
								h.write('<td>')
								h.write(str(ob5))
								h.write('</td>')
								h.write('</tr>')
								test = 1
						except:
							pass
						try:
							if (plist2[i]['NS.keys']):
								h.write('<tr name="hide">')
								h.write('<td>NS.keys</td>')
								ob0 = str(plist2[i]['NS.keys'])
								h.write('<td>')
								h.write(str(ob0))
								h.write('</td>')
								h.write('</tr>')
								test = 1
						except:
							pass
						try:
							if (plist2[i]['NS.objects']):
								ob1 = str(plist2[i]['NS.objects'])
								h.write('<tr name="hide">')
								h.write('<td>NS.objects</td>')
								h.write('<td>')
								h.write(str(ob1))
								h.write('</td>')
								h.write('</tr>')
								
								test = 1
						except:
							pass
						try:
							if (plist2[i]['NS.time']):
								dia = str(plist2[i]['NS.time'])
								dias = (dia.rsplit('.', 1)[0])
								timestamp = datetime.datetime.fromtimestamp(int(dias)) + delta
								#logfunc (timestamp)
							
								h.write('<tr>')
								h.write('<td>Time UTC</td>')
								h.write('<td>')
								h.write(str(timestamp))
								#h.write(str(plist2[i]['NS.time']))
								h.write('</td>')
								h.write('</tr>')
								
								test = 1 
						except:
							pass
						try:
							if (plist2[i]['NS.base']):
								ob2 = str(plist2[i]['NS.objects'])
								h.write('<tr name="hide">')
								h.write('<td>NS.base</td>')
								h.write('<td>')
								h.write(str(ob2))
								h.write('</td>')
								h.write('</tr>')
								
								test = 1 
						except:
							pass
						try:
							if (plist2[i]['$classname']):
								ob3 = str(plist2[i]['$classname'])
								h.write('<tr name="hide">')
								h.write('<td>$classname</td>')
								h.write('<td>')
								h.write(str(ob3))
								h.write('</td>')
								h.write('</tr>')
								
								test = 1 
						except:
							pass
						
						try:
							if test == 0:
								if (plist2[i]) == "AppNotificationMessage":
									h.write('</table>')
									h.write('<br>')
									h.write('<table>')
									h.write('<tr>')
									h.write('<th>Data type</th>')
									h.write('<th>Value</th>')
									h.write('</tr>')
								
									h.write('<tr name="hide">')
									h.write('<td>ASCII</td>')
									h.write('<td>'+str(plist2[i])+'</td>')
									h.write('</tr>')
									
									
								else:
									if plist2[i] in notiparams:
										h.write('<tr name="hide">')
										h.write('<td>ASCII</td>')
										h.write('<td>'+str(plist2[i])+'</td>')
										h.write('</tr>')
									elif plist2[i] == " ":
										h.write('<tr name="hide">')
										h.write('<td>Null</td>')
										h.write('<td>'+str(plist2[i])+'</td>')
										h.write('</tr>')
									else:
										h.write('<tr>')
										h.write('<td>ASCII</td>')
										h.write('<td>'+str(plist2[i])+'</td>')
										h.write('</tr>')
								
						except:
							pass
							
						test = 0
									
						
						#h.write('test')
					
					for dict in plist2:
						liste = dict
						types = (type(liste))
						#logfunc (types)
						try:
							for k, v in liste.items():
								if k == 'NS.data':
									chk = str(v)
									reduced = (chk[2:8])
									#logfunc (reduced)
									if reduced == "bplist":
										count = count + 1
										binfile = open('./'+appdirect+'/incepted'+str(count)+'.bplist', 'wb')
										binfile.write(v)
										binfile.close()

										procfile = open('./'+appdirect+'/incepted'+str(count)+'.bplist', 'rb')
										secondplist = ccl_bplist.load(procfile)
										secondplistint = secondplist["$objects"]
										logfunc('Bplist processed and exported.')
										exportedbplistcount = exportedbplistcount + 1
										h.write('<tr name="hide">')
										h.write('<td>NS.data</td>')
										h.write('<td>')
										h.write(str(secondplistint))
										h.write('</td>')
										h.write('</tr>')
										
										procfile.close()
										count = 0
									else:
										h.write('<tr name="hide">')
										h.write('<td>NS.data</td>')
										h.write('<td>')
										h.write(str(secondplistint))
										h.write('</td>')
										h.write('</tr>')
						except:
							pass
					h.close()
				elif 'AttachmentsList' in file_name:
					test = 0 #future development
					
	path = reportfolderbase+'/iOS 11 Notifications/'
	list =[]
	files = os.listdir(path)
	for name in files:
		list.append(f'<a href = "./{name}/DeliveredNotificationsReport.html" target="content">{name}</a>')
			
	filedatahtml = open(path+'iOS11_Notifications.html', mode='a+')
	list.sort()
	for items in list:
		filedatahtml.write(items)
		filedatahtml.write('<br>')

	logfunc("Total notification directories processed:"+str(notdircount))
	logfunc("Total exported bplists from notifications:"+str(exportedbplistcount))
	if notdircount == 0:
			logfunc('No notifications located.')
	logfunc(f'iOS 11 Notifications function completed.')
	
def iOSNotifications12(filefound):
	logfunc(f'iOS 12+ Notifications function executing')
	os.makedirs(reportfolderbase+'iOS 12 Notifications/')

	count = 0
	notdircount = 0
	exportedbplistcount = 0
	unix = datetime.datetime(1970, 1, 1)  # UTC
	cocoa = datetime.datetime(2001, 1, 1)  # UTC
	delta = cocoa - unix 
	
	#with open('NotificationParams.txt', 'r') as f:
	#	notiparams = [line.strip() for line in f]
	
	f = open('NotificationParams.txt', 'r')
	notiparams = [line.strip() for line in f]
	f.close()
	
	folder = (reportfolderbase+'iOS 12 Notifications/') 
	#logfunc("Processing:")
	pathfound = str(filefound[0])
	#logfunc(f'Posix to string is: {pathfound}')
	for filename in glob.iglob(pathfound+'/**', recursive=True):
		#create directory where script is running from
		if os.path.isfile(filename): # filter dirs
			file_name = os.path.splitext(os.path.basename(filename))[0]
			#create directory
			if 'DeliveredNotifications' in file_name:
				#create directory where script is running from
				#logfunc (filename) #full path
				notdircount = notdircount + 1				
				#logfunc (os.path.basename(file_name)) #filename with  no extension
				openplist = (os.path.basename(os.path.normpath(filename))) #filename with extension
				#logfunc (openplist)
				bundlepath = (os.path.basename(os.path.dirname(filename)))#previous directory
				appdirect = (folder + "/"+ bundlepath) 
				#logfunc(appdirect)
				os.makedirs( appdirect )
				
				#open the plist
				p = open(filename, 'rb')
				plist = ccl_bplist.load(p)
				plist2 = plist["$objects"]

				long = len(plist2)
				#logfunc (long)
				h = open('./'+appdirect+'/DeliveredNotificationsReport.html', 'w') #write report
				h.write('<html><body>')
				h.write('<h2>iOS Delivered Notifications Triage Report </h2>')
				h.write ('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
				h.write(filename)
				h.write('<br/>')
				h.write('<br/>')
				
				h.write('<button onclick="hideRows()">Hide rows</button>')
				h.write('<button onclick="showRows()">Show rows</button>')
				
				f = open("script.txt")
				for line in f:
					h.write(line)
				f.close()
				
				h.write('<br>')
				h.write('<table name="hide">')
				h.write('<tr name="hide">')
				h.write('<th>Data type</th>')
				h.write('<th>Value</th>')
				h.write('</tr>')
								
				h.write('<tr name="hide">')
				h.write('<td>Plist</td>')
				h.write('<td>Initial Values</td>')
				h.write('</tr>')
				
				test = 0
				for i in range (0, long):
					try:
						if (plist2[i]['$classes']):
							h.write('<tr name="hide">')
							h.write('<td>$classes</td>')
							ob6 = str(plist2[i]['$classes'])
							h.write('<td>')
							h.write(str(ob6))
							h.write('</td>')
							h.write('</tr>')
							test = 1
					except:
						pass
					try:
						if (plist2[i]['$class']):
							h.write('<tr name="hide">')
							h.write('<td>$class</td>')
							ob5 = str(plist2[i]['$class'])
							h.write('<td>')
							h.write(str(ob5))
							h.write('</td>')
							h.write('</tr>')
							test = 1
					except:
						pass
					try:
						if (plist2[i]['NS.keys']):
							h.write('<tr name="hide">')
							h.write('<td>NS.keys</td>')
							ob0 = str(plist2[i]['NS.keys'])
							h.write('<td>')
							h.write(str(ob0))
							h.write('</td>')
							h.write('</tr>')
							test = 1
					except:
						pass
					try:
						if (plist2[i]['NS.objects']):
							ob1 = str(plist2[i]['NS.objects'])
							h.write('<tr name="hide">')
							h.write('<td>NS.objects</td>')
							h.write('<td>')
							h.write(str(ob1))
							h.write('</td>')
							h.write('</tr>')
							
							test = 1
					except:
						pass
					try:
						if (plist2[i]['NS.time']):
							dia = str(plist2[i]['NS.time'])
							dias = (dia.rsplit('.', 1)[0])
							timestamp = datetime.datetime.fromtimestamp(int(dias)) + delta
							#logfunc (timestamp)
						
							h.write('<tr>')
							h.write('<td>Time UTC</td>')
							h.write('<td>')
							h.write(str(timestamp))
							#h.write(str(plist2[i]['NS.time']))
							h.write('</td>')
							h.write('</tr>')
							
							test = 1 
					except:
						pass
					try:
						if (plist2[i]['NS.base']):
							ob2 = str(plist2[i]['NS.objects'])
							h.write('<tr name="hide">')
							h.write('<td>NS.base</td>')
							h.write('<td>')
							h.write(str(ob2))
							h.write('</td>')
							h.write('</tr>')
							
							test = 1 
					except:
						pass
					try:
						if (plist2[i]['$classname']):
							ob3 = str(plist2[i]['$classname'])
							h.write('<tr name="hide">')
							h.write('<td>$classname</td>')
							h.write('<td>')
							h.write(str(ob3))
							h.write('</td>')
							h.write('</tr>')
							
							test = 1 
					except:
						pass
					'''
					try:
						
							h.write('<tr>')
							h.write('<td>ASCII</td>')
							h.write('<td>'+str(plist2[i])+'</td>')
							h.write('</tr>')
							
							test = 1
					except:
						pass
					'''	
					try:
						if test == 0:
							if (plist2[i]) == "AppNotificationMessage":
								h.write('</table>')
								h.write('<br>')
								h.write('<table>')
								h.write('<tr>')
								h.write('<th>Data type</th>')
								h.write('<th>Value</th>')
								h.write('</tr>')
							
								h.write('<tr name="hide">')
								h.write('<td>ASCII</td>')
								h.write('<td>'+str(plist2[i])+'</td>')
								h.write('</tr>')
								
							else:
								if plist2[i] in notiparams:
									h.write('<tr name="hide">')
									h.write('<td>ASCII</td>')
									h.write('<td>'+str(plist2[i])+'</td>')
									h.write('</tr>')
								elif plist2[i] == " ":
									h.write('<tr name="hide">')
									h.write('<td>Null</td>')
									h.write('<td>'+str(plist2[i])+'</td>')
									h.write('</tr>')
								else:
									h.write('<tr>')
									h.write('<td>ASCII</td>')
									h.write('<td>'+str(plist2[i])+'</td>')
									h.write('</tr>')
							
					except:
						pass
						
					test = 0
								
					
					#h.write('test')
				
				
				for dict in plist2:
					liste = dict
					types = (type(liste))
					#logfunc (types)
					try:
						for k, v in liste.items():
							if k == 'NS.data':
								chk = str(v)
								reduced = (chk[2:8])
								#logfunc (reduced)
								if reduced == "bplist":
									count = count + 1
									binfile = open('./'+appdirect+'/incepted'+str(count)+'.bplist', 'wb')
									binfile.write(v)
									binfile.close()

									procfile = open('./'+appdirect+'/incepted'+str(count)+'.bplist', 'rb')
									secondplist = ccl_bplist.load(procfile)
									secondplistint = secondplist["$objects"]
									logfunc('Bplist processed and exported.')
									exportedbplistcount = exportedbplistcount + 1
									h.write('<tr name="hide">')
									h.write('<td>NS.data</td>')
									h.write('<td>')
									h.write(str(secondplistint))
									h.write('</td>')
									h.write('</tr>')
									
									procfile.close()
									count = 0
								else:
									h.write('<tr name="hide">')
									h.write('<td>NS.data</td>')
									h.write('<td>')
									h.write(str(secondplistint))
									h.write('</td>')
									h.write('</tr>')
					except:
						pass
				h.close()
			elif 'AttachmentsList' in file_name:
				test = 0 #future development

	path = reportfolderbase+'/iOS 12 Notifications/'
	dict ={}
	files = os.listdir(path)
	for name in files:
		try:
			size = os.path.getsize(f'{path}{name}/DeliveredNotificationsReport.html')
			key = (f'<a href = "{name}/DeliveredNotificationsReport.html" target="content">{name}</a>')
			dict[key] = size
		except NotADirectoryError as nade:
			logfunc(nade)
			pass

	filedatahtml = open(path+'iOS12_Notifications.html', mode='a+')
	filedatahtml.write('<html><body><table><style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style><tr><td>Notifications by GUID (iOS13) or Bundle ID (iOS12) </td><td>Notification size in KB</td></tr>')
	for k, v in dict.items():
		v = v/1000
		#logfunc(f'{k} -> {v}')	
		filedatahtml.write(f'<tr><td>{k}</td><td>{v}</td></tr>')
	filedatahtml.write('</table></body></html>')
	filedatahtml.close()
	
	logfunc("Total notification directories processed:"+str(notdircount))
	logfunc("Total exported bplists from notifications:"+str(exportedbplistcount))
	if notdircount == 0:
		logfunc('No notifications located.')
	logfunc('iOS 12+ Notifications function completed.')

def ktx(filefound):
	logfunc(f'Snapshots KTX file finder function executing.')
	logfunc(f'Snapshots located: {len(filefound)}')
	outpath = reportfolderbase +'Snapshots_KTX_Files/'
	outktx = outpath+'KTX_Files/'
	os.mkdir(outpath)
	os.mkdir(outktx)
	nl = '\n'
	
	filedata = open(outpath+'_Snapshot_KTX_Files_List.csv', mode='a+')
	filewrite = csv.writer(filedata, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	filewrite.writerow([ 'Path', 'Filename'])
	filedata.close()
	
	filedatahtml = open(outpath+'KTX_Files.html', mode='a+')
	filedatahtml.write('<html><body>')
	filedatahtml.write('<h2>KTX Files Report </h2>')
	filedatahtml.write ('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
	filedatahtml.write('<br/>')
	filedatahtml.write(f'Extracted KTX files can be examined in the {outpath}KTX_Files/ directory.<br>')
	filedatahtml.write('<table>')
	filedatahtml.write('<tr><td>Path</td><td>Filename</td></tr>')

	for filename in filefound:
		p = pathlib.Path(filename)
		head1, tail1 = os.path.split(filename)
		head2, tail2 = os.path.split(head1)
		
		tail = ''
		head = ''
		fullp = ''
		for x in p.parts:
			head1, tail = os.path.split(head1)
			fullp = tail+'/'+fullp
			if tail == 'Library':
				fullpw = fullp
			
		if os.path.exists(outktx+fullpw):
			pass
		else:
			os.makedirs(outktx+fullpw)
		#get the name, filepath write to csv in outpath _KTX_Files_Report.csv

		filedata = open(outpath+'_Snapshot_KTX_Files_List.csv', mode='a+')
		filewrite = csv.writer(filedata, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		filewrite.writerow([filename, tail1])
		filedatahtml.write(f'<tr><td>{filename}</td><td>{tail1}</td></tr>')
		filedata.close()
		if os.path.exists(filename):
			shutil.copy2(filename, outktx+fullpw)
	filedatahtml.close()
	logfunc(f'Snapshots KTX file finder function completed.')	

def calhist(filefound):
	db = sqlite3.connect(filefound[0])
	cursor = db.cursor()
	cursor.execute('''
	SELECT 
			ZADDRESS AS "ADDRESS", 
			ZANSWERED AS "WAS ANSWERED", 
			ZCALLTYPE AS "CALL TYPE", 
			ZORIGINATED AS "ORIGINATED", 
			ZDURATION AS "DURATION (IN SECONDS)",
			ZISO_COUNTRY_CODE as "ISO COUNTY CODE",
			ZLOCATION AS "LOCATION", 
			ZSERVICE_PROVIDER AS "SERVICE PROVIDER",
			DATETIME(ZDATE+978307200,'UNIXEPOCH') AS "TIMESTAMP"
		FROM ZCALLRECORD ''')

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	if usageentries > 0:
		logfunc(f'Call History function executing')
		os.makedirs(reportfolderbase+'Call History/')
		with open(reportfolderbase+'Call History/Call History.html', 'w', encoding='utf8') as f:
			f.write('<html><body>')
			f.write('<h2> Call History report</h2>')
			f.write(f'Call History entries: {usageentries}<br>')
			f.write(f'Call History database located at: {filefound[0]}<br>')
			f.write('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
			f.write('<br/>')
			f.write('')
			f.write(f'<table>')
			f.write(f'<tr><td>Address</td><td>Was Answered</td><td>Call Type</td><td>Originated</td><td>Duration in Secs</td><td>ISO County Code</td><td>Location</td><td>Service Provider</td><td>Timestamp</td></tr>')
			for row in all_rows:
				an = str(row[0])
				an = (an.replace("b'", ''))
				an = (an.replace("'", ''))
				
				f.write(f'<tr><td>{an}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td></tr>')
			f.write(f'</table></body></html>')
			logfunc(f'Call History function completed')
	else:
		logfunc('No call history available')

def smschat(filefound):
	db = sqlite3.connect(filefound[0])
	cursor = db.cursor()
	try:
		cursor.execute('''
		SELECT
				CASE
					WHEN LENGTH(MESSAGE.DATE)=18 THEN DATETIME(MESSAGE.DATE/1000000000+978307200,'UNIXEPOCH')
					WHEN LENGTH(MESSAGE.DATE)=9 THEN DATETIME(MESSAGE.DATE + 978307200,'UNIXEPOCH')
					ELSE "N/A"
		    		END "MESSAGE DATE",			
				CASE 
					WHEN LENGTH(MESSAGE.DATE_DELIVERED)=18 THEN DATETIME(MESSAGE.DATE_DELIVERED/1000000000+978307200,"UNIXEPOCH")
					WHEN LENGTH(MESSAGE.DATE_DELIVERED)=9 THEN DATETIME(MESSAGE.DATE_DELIVERED+978307200,"UNIXEPOCH")
					ELSE "N/A"
				END "DATE DELIVERED",
				CASE 
					WHEN LENGTH(MESSAGE.DATE_READ)=18 THEN DATETIME(MESSAGE.DATE_READ/1000000000+978307200,"UNIXEPOCH")
					WHEN LENGTH(MESSAGE.DATE_READ)=9 THEN DATETIME(MESSAGE.DATE_READ+978307200,"UNIXEPOCH")
					ELSE "N/A"
				END "DATE READ",
				MESSAGE.TEXT as "MESSAGE",
				HANDLE.ID AS "CONTACT ID",
				MESSAGE.SERVICE AS "SERVICE",
				MESSAGE.ACCOUNT AS "ACCOUNT",
				MESSAGE.IS_DELIVERED AS "IS DELIVERED",
				MESSAGE.IS_FROM_ME AS "IS FROM ME",
				ATTACHMENT.FILENAME AS "FILENAME",
				ATTACHMENT.MIME_TYPE AS "MIME TYPE",
				ATTACHMENT.TRANSFER_NAME AS "TRANSFER TYPE",
				ATTACHMENT.TOTAL_BYTES AS "TOTAL BYTES"
			FROM MESSAGE
			LEFT OUTER JOIN MESSAGE_ATTACHMENT_JOIN ON MESSAGE.ROWID = MESSAGE_ATTACHMENT_JOIN.MESSAGE_ID
			LEFT OUTER JOIN ATTACHMENT ON MESSAGE_ATTACHMENT_JOIN.ATTACHMENT_ID = ATTACHMENT.ROWID
			LEFT OUTER JOIN HANDLE ON MESSAGE.HANDLE_ID = HANDLE.ROWID
			''')

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			logfunc(f'SMS Chat function executing')
			os.makedirs(reportfolderbase+'SMS Chat/')
			with open(reportfolderbase+'SMS Chat/SMS Chat.html', 'w', encoding='utf8') as f:
				f.write('<html><body>')
				f.write('<h2> SMS Chat report</h2>')
				f.write(f'SMS Chat entries: {usageentries}<br>')
				f.write(f'SMS Chat database located at: {filefound[0]}<br>')
				f.write('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
				f.write('<br/>')
				f.write('')
				f.write(f'<table>')
				f.write(f'<tr><td>Message Date</td><td>Date Delivered</td><td>Date Read</td><td>Message</td><td>Contact ID</td><td>Service</td><td>Account</td><td>Is Delivered</td><td>Is from Me</td><td>Filename</td><td>MIME Type</td><td>Transfer Type</td><td>Total Bytes</td></tr>')
				for row in all_rows:
					f.write(f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td><td>{row[10]}</td><td>{row[11]}</td><td>{row[12]}</td></tr>')
				f.write(f'</table></body></html>')
				logfunc(f'SMS Chat function completed')
		else:
				logfunc('No SMS Chats available')
	except:
		logfunc('Error on SMS Chat function. Possible empty database.')	
			
	db = sqlite3.connect(filefound[0])
	cursor = db.cursor()
	try:
		cursor.execute('''
		SELECT
				CASE
		 			WHEN LENGTH(MESSAGE.DATE)=18 THEN DATETIME(MESSAGE.DATE/1000000000+978307200,'UNIXEPOCH')
		 			WHEN LENGTH(MESSAGE.DATE)=9 THEN DATETIME(MESSAGE.DATE + 978307200,'UNIXEPOCH')
		 			ELSE "N/A"
				END "MESSAGE DATE",
				CASE 
					WHEN LENGTH(MESSAGE.DATE_DELIVERED)=18 THEN DATETIME(MESSAGE.DATE_DELIVERED/1000000000+978307200,"UNIXEPOCH")
					WHEN LENGTH(MESSAGE.DATE_DELIVERED)=9 THEN DATETIME(MESSAGE.DATE_DELIVERED+978307200,"UNIXEPOCH")
					ELSE "N/A"
				END "DATE DELIVERED",
				CASE 
					WHEN LENGTH(MESSAGE.DATE_READ)=18 THEN DATETIME(MESSAGE.DATE_READ/1000000000+978307200,"UNIXEPOCH")
					WHEN LENGTH(MESSAGE.DATE_READ)=9 THEN DATETIME(MESSAGE.DATE_READ+978307200,"UNIXEPOCH")
					ELSE "N/A"
				END "DATE READ",
				MESSAGE.TEXT as "MESSAGE",
				HANDLE.ID AS "CONTACT ID",
				MESSAGE.SERVICE AS "SERVICE",
				MESSAGE.ACCOUNT AS "ACCOUNT",
				MESSAGE.IS_DELIVERED AS "IS DELIVERED",
				MESSAGE.IS_FROM_ME AS "IS FROM ME",
				ATTACHMENT.FILENAME AS "FILENAME",
				ATTACHMENT.MIME_TYPE AS "MIME TYPE",
				ATTACHMENT.TRANSFER_NAME AS "TRANSFER TYPE",
				ATTACHMENT.TOTAL_BYTES AS "TOTAL BYTES"
			FROM MESSAGE
			LEFT OUTER JOIN MESSAGE_ATTACHMENT_JOIN ON MESSAGE.ROWID = MESSAGE_ATTACHMENT_JOIN.MESSAGE_ID
			LEFT OUTER JOIN ATTACHMENT ON MESSAGE_ATTACHMENT_JOIN.ATTACHMENT_ID = ATTACHMENT.ROWID
			LEFT OUTER JOIN HANDLE ON MESSAGE.HANDLE_ID = HANDLE.ROWID
			WHERE "DATE DELIVERED" IS NOT "N/A"''')

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			logfunc(f'SMS Chat Message Delivered function executing')
			with open(reportfolderbase+'SMS Chat/SMS Message Delivered.html', 'w', encoding='utf8') as f:
				f.write('<html><body>')
				f.write('<h2> SMS Chat Message Delivered report</h2>')
				f.write(f'SMS Chat Message Delivered entries: {usageentries}<br>')
				f.write(f'SMS Chat Message Delivered database located at: {filefound[0]}<br>')
				f.write('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
				f.write('<br/>')
				f.write('')
				f.write(f'<table>')
				f.write(f'<tr><td>Message Date</td><td>Date Delivered</td><td>Date Read</td><td>Message</td><td>Contact ID</td><td>Service</td><td>Account</td><td>Is Delivered</td><td>Is from Me</td><td>Filename</td><td>MIME Type</td><td>Transfer Type</td><td>Total Bytes</td></tr>')
				for row in all_rows:
					f.write(f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td><td>{row[10]}</td><td>{row[11]}</td><td>{row[12]}</td></tr>')
				f.write(f'</table></body></html>')
				logfunc(f'SMS Chat Message function completed')
		else:
			logfunc('No SMS Chat Message Delivered available')
	except:
		logfunc('Error on SMS Chat Message Delivered function. Possible empty database.')
				
	db = sqlite3.connect(filefound[0])
	cursor = db.cursor()
	try:
		cursor.execute('''
		SELECT
				CASE
		 			WHEN LENGTH(MESSAGE.DATE)=18 THEN DATETIME(MESSAGE.DATE/1000000000+978307200,'UNIXEPOCH')
		 			WHEN LENGTH(MESSAGE.DATE)=9 THEN DATETIME(MESSAGE.DATE + 978307200,'UNIXEPOCH')
		 			ELSE "N/A"
		     		END "MESSAGE DATE",
				CASE 
					WHEN LENGTH(MESSAGE.DATE_DELIVERED)=18 THEN DATETIME(MESSAGE.DATE_DELIVERED/1000000000+978307200,"UNIXEPOCH")
					WHEN LENGTH(MESSAGE.DATE_DELIVERED)=9 THEN DATETIME(MESSAGE.DATE_DELIVERED+978307200,"UNIXEPOCH")
					ELSE "N/A"
				END "DATE DELIVERED",
				CASE 
					WHEN LENGTH(MESSAGE.DATE_READ)=18 THEN DATETIME(MESSAGE.DATE_READ/1000000000+978307200,"UNIXEPOCH")
					WHEN LENGTH(MESSAGE.DATE_READ)=9 THEN DATETIME(MESSAGE.DATE_READ+978307200,"UNIXEPOCH")
					ELSE "N/A"
				END "DATE READ",
				MESSAGE.TEXT as "MESSAGE",
				HANDLE.ID AS "CONTACT ID",
				MESSAGE.SERVICE AS "SERVICE",
				MESSAGE.ACCOUNT AS "ACCOUNT",
				MESSAGE.IS_DELIVERED AS "IS DELIVERED",
				MESSAGE.IS_FROM_ME AS "IS FROM ME",
				ATTACHMENT.FILENAME AS "FILENAME",
				ATTACHMENT.MIME_TYPE AS "MIME TYPE",
				ATTACHMENT.TRANSFER_NAME AS "TRANSFER TYPE",
				ATTACHMENT.TOTAL_BYTES AS "TOTAL BYTES"
			FROM MESSAGE
			LEFT OUTER JOIN MESSAGE_ATTACHMENT_JOIN ON MESSAGE.ROWID = MESSAGE_ATTACHMENT_JOIN.MESSAGE_ID
			LEFT OUTER JOIN ATTACHMENT ON MESSAGE_ATTACHMENT_JOIN.ATTACHMENT_ID = ATTACHMENT.ROWID
			LEFT OUTER JOIN HANDLE ON MESSAGE.HANDLE_ID = HANDLE.ROWID
			WHERE "DATE READ" IS NOT "N/A"''')

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			logfunc(f'SMS Chat Message Read function executing')
			with open(reportfolderbase+'SMS Chat/SMS Message Read.html', 'w', encoding='utf8') as f:
				f.write('<html><body>')
				f.write('<h2> SMS Chat Message Read report</h2>')
				f.write(f'SMS Chat Message Read entries: {usageentries}<br>')
				f.write(f'SMS Chat Message Readdatabase located at: {filefound[0]}<br>')
				f.write('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
				f.write('<br/>')
				f.write('')
				f.write(f'<table>')
				f.write(f'<tr><td>Message Date</td><td>Date Delivered</td><td>Date Read</td><td>Message</td><td>Contact ID</td><td>Service</td><td>Account</td><td>Is Delivered</td><td>Is from Me</td><td>Filename</td><td>MIME Type</td><td>Transfer Type</td><td>Total Bytes</td></tr>')
				for row in all_rows:
					f.write(f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td><td>{row[10]}</td><td>{row[11]}</td><td>{row[12]}</td></tr>')
				f.write(f'</table></body></html>')
				logfunc(f'SMS Chat Message Read function completed')
		else:
			logfunc('No SMS Chat Message Read available')
	except:
		logfunc('Error on SMS Chat Message Read available. Posible empty database. ')
				
def safari(filefound):
	db = sqlite3.connect(filefound[0])
	cursor = db.cursor()
	try:
		cursor.execute('''
		SELECT 
				HISTORY_ITEMS.URL AS "URL",
				HISTORY_ITEMS.VISIT_COUNT AS "VISIT COUNT",
				HISTORY_VISITS.TITLE AS "TITLE",
				CASE HISTORY_VISITS.ORIGIN
					WHEN 1 THEN "ICLOUD SYNCED DEVICE"
					WHEN 0 THEN "VISTED FROM THIS DEVICE"
				END "ICLOUD SYNC",
				HISTORY_VISITS.LOAD_SUCCESSFUL AS "LOAD SUCCESSFUL",
				HISTORY_VISITS.REDIRECT_SOURCE AS "REDIRECT SOURCE",
				HISTORY_VISITS.REDIRECT_DESTINATION AS "REDIRECT DESTINATION",
				DATETIME(HISTORY_VISITS.VISIT_TIME+978307200,'UNIXEPOCH') AS "VISIT TIME",
				HISTORY_VISITS.ID AS "HISTORY ITEM ID"
			FROM HISTORY_ITEMS
			LEFT OUTER JOIN HISTORY_VISITS ON HISTORY_ITEMS.ID == HISTORY_VISITS.HISTORY_ITEM
		''')

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			logfunc(f'Safari History function executing')
			os.makedirs(reportfolderbase+'Safari/')
			with open(reportfolderbase+'Safari/Safari History.html', 'w', encoding='utf8') as f:
				f.write('<html><body>')
				f.write('<h2> Safari History report</h2>')
				f.write(f'Safari History entries: {usageentries}<br>')
				f.write(f'Safari History database located at: {filefound[0]}<br>')
				f.write('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
				f.write('<br/>')
				f.write('')
				f.write(f'<table>')
				f.write(f'<tr><td>URL</td><td>Visit Count</td><td>Title</td><td>Icloud Sync</td><td>Load Sucessful</td><td>Redirect Source</td><td>Redirect Destination</td><td>Visit Time</td><td>History Item ID</td></tr>')
				for row in all_rows:
					url = textwrap.fill(row[0])
					f.write(f'<tr><td>{url}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td></tr>')
				f.write(f'</table></body></html>')
				logfunc(f'Safari History function completed')
		else:
				logfunc('No Safari History available')
	except:
		logfunc('Error on Safari History function.')
		
def queryp(filefound):
	try:
		db = sqlite3.connect(filefound[0])
		cursor = db.cursor()
		cursor.execute('''
		select 
				content,
				isSent,
				conversationId,
				id,
				uuid,
				datetime(creationTimestamp, "UNIXEPOCH", "LOCALTIME") as START
				from messages
		''')

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			logfunc(f'Query Predictions function executing')
			os.makedirs(reportfolderbase+'Query Predictions/')
			with open(reportfolderbase+'Query Predictions/Query Predictions.html', 'w', encoding='utf8') as f:
				f.write('<html><body>')
				f.write('<h2> Query Predictions report</h2>')
				f.write(f'Query Predictions entries: {usageentries}<br>')
				f.write(f'Query Predictions database located at: {filefound[0]}<br>')
				f.write('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
				f.write('<br/>')
				f.write('')
				f.write(f'<table>')
				f.write(f'<tr><td>Content</td><td>Is Sent</td><td>Conversation ID</td><td>ID</td><td>UUID</td><td>Start</td></tr>')
				for row in all_rows:
					f.write(f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td></tr>')
				f.write(f'</table></body></html>')
				logfunc(f'Query Predictions function completed')
		else:
				logfunc('No Query Predictions available')
	except:
		logfunc('Error in the Query Predictions Section.')

def powerlog(filefound):
	os.makedirs(reportfolderbase+'Powerlog/')
	try:
		db = sqlite3.connect(filefound[0])
		cursor = db.cursor()
		cursor.execute('''
		SELECT
			   DATETIME(TIMESTAMP, 'unixepoch') AS TIMESTAMP,
			   DATETIME(START, 'unixepoch') AS "START",
			   DATETIME(END, 'unixepoch') AS "END",
			   STATE as "STATE",
			   FINISHED as "FINISHED",
			   HASERROR AS "HAS ERROR",
			   ID AS "PLXPCAGENT_EVENTPOINT_MOBILEBACKUPEVENTS TABLE ID" 
			FROM
			   PLXPCAGENT_EVENTPOINT_MOBILEBACKUPEVENTS		
		''')

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			logfunc(f'Powerlog Mobile Backup Events executing')
			with open(reportfolderbase+'Powerlog/Mobile Backup Events.html', 'w', encoding='utf8') as f:
				f.write('<html><body>')
				f.write('<h2> Powerlog Mobile Backup Events report</h2>')
				f.write(f'Mobile Backup Events entries: {usageentries}<br>')
				f.write(f'Mobile Backup Events database located at: {filefound[0]}<br>')
				f.write('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
				f.write('<br/>')
				f.write('')
				f.write(f'<table>')
				f.write(f'<tr><td>Timestamp</td><td>Start</td><td>End</td><td>State</td><td>Finished</td><td>Has Error</td><td>ID</td></tr>')
				for row in all_rows:
					f.write(f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td></tr>')
				f.write(f'</table></body></html>')
				logfunc(f'Powerlog Mobile Backup Events function completed')
		else:
				logfunc('No Powerlog Mobile Backup Events available')
	except:
		logfunc('Error in Powerlog Mobile Backup Events Section.')
		
	try:
		db = sqlite3.connect(filefound[0])
		cursor = db.cursor()
		cursor.execute('''
		SELECT
				DATETIME(WIFIPROPERTIES_TIMESTAMP + SYSTEM, 'unixepoch') AS ADJUSTED_TIMESTAMP,
				CURRENTSSID,
				CURRENTCHANNEL,
				DATETIME(TIME_OFFSET_TIMESTAMP, 'unixepoch') AS OFFSET_TIMESTAMP,
				SYSTEM AS TIME_OFFSET,
				WIFIPROPERTIES_ID AS "PLWIFIAGENT_EVENTBACKWARD_CUMULATIVEPROPERTIES TABLE ID" 
		   	FROM
		      (
				SELECT
					WIFIPROPERTIES_ID,
					WIFIPROPERTIES_TIMESTAMP,
					TIME_OFFSET_TIMESTAMP,
					MAX(TIME_OFFSET_ID) AS MAX_ID,
					CURRENTSSID,
					CURRENTCHANNEL,
					SYSTEM
				FROM
		            (
					SELECT
						PLWIFIAGENT_EVENTBACKWARD_CUMULATIVEPROPERTIES.TIMESTAMP AS WIFIPROPERTIES_TIMESTAMP,
						CURRENTSSID,
						CURRENTCHANNEL,
						PLWIFIAGENT_EVENTBACKWARD_CUMULATIVEPROPERTIES.ID AS "WIFIPROPERTIES_ID" ,
						PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
						PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
						PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM
					FROM
						PLWIFIAGENT_EVENTBACKWARD_CUMULATIVEPROPERTIES
					LEFT JOIN
						PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET 
		            )
		            AS WIFIPROPERTIES_STATE 
		        GROUP BY
					WIFIPROPERTIES_ID 
		      )	
		''')

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			logfunc(f'Powerlog WIFI Properties executing')
			with open(reportfolderbase+'Powerlog/Powerlog WIFI Properties.html', 'w', encoding='utf8') as f:
				f.write('<html><body>')
				f.write('<h2> Powerlog WIFI Properties Events report</h2>')
				f.write(f'Powerlog WIFI Properties entries: {usageentries}<br>')
				f.write(f'Powerlog WIFI Properties database located at: {filefound[0]}<br>')
				f.write('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
				f.write('<br/>')
				f.write('')
				f.write(f'<table>')
				f.write(f'<tr><td>Adj. Timestamp</td><td>Current SSID</td><td>Current Channel</td><td>Offset Timestamp</td><td>Time Offset</td><td>ID</td></tr>')
				for row in all_rows:
					f.write(f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td></tr>')
				f.write(f'</table></body></html>')
				logfunc(f'Powerlog WIFI Properties function completed')
		else:
				logfunc('No Powerlog WIFI Properties available')
	except:
		logfunc('Error in Powerlog WIFI Properties Section.')
		
	try:
		db = sqlite3.connect(filefound[0])
		cursor = db.cursor()
		cursor.execute('''
		SELECT
				DATETIME(SBAUTOLOCK_TIMESTAMP + SYSTEM, 'unixepoch') AS ADJUSTED_TIMESTAMP,
				AUTOLOCKTYPE AS "AUTO LOCK TYPE",
				DATETIME(TIME_OFFSET_TIMESTAMP, 'unixepoch') AS OFFSET_TIMESTAMP,
				SYSTEM AS TIME_OFFSET,
				SBAUTOLOCK_ID AS "PLSPRINGBOARDAGENT_EVENTPOINT_SBAUTOLOCK TABLE ID" 
			FROM
			(
				SELECT
					SBAUTOLOCK_ID,
					SBAUTOLOCK_TIMESTAMP,
					TIME_OFFSET_TIMESTAMP,
					MAX(TIME_OFFSET_ID) AS MAX_ID,
					AUTOLOCKTYPE,
					SYSTEM
				FROM
				(
				SELECT
					PLSPRINGBOARDAGENT_EVENTPOINT_SBAUTOLOCK.TIMESTAMP AS SBAUTOLOCK_TIMESTAMP,
					AUTOLOCKTYPE,
					PLSPRINGBOARDAGENT_EVENTPOINT_SBAUTOLOCK.ID AS "SBAUTOLOCK_ID" ,
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM
				FROM
					PLSPRINGBOARDAGENT_EVENTPOINT_SBAUTOLOCK
				LEFT JOIN
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET 
				)
				AS SBAUTOLOCK_STATE 
				GROUP BY
					SBAUTOLOCK_ID 
			)
		''')

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			logfunc(f'Powerlog Device Screen Autolock executing')
			with open(reportfolderbase+'Powerlog/Device Screen Autolock.html', 'w', encoding='utf8') as f:
				f.write('<html><body>')
				f.write('<h2> Powerlog Device Screen Autolock report</h2>')
				f.write(f'Powerlog Device Screen Autolock entries: {usageentries}<br>')
				f.write(f'Powerlog Device Screen Autolock located at: {filefound[0]}<br>')
				f.write('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
				f.write('<br/>')
				f.write('')
				f.write(f'<table>')
				f.write(f'<tr><td>Adj Timestamp</td><td>Auto Lock Type</td><td>Offset Timestamp</td><td>Time Offset</td><td>ID</td></tr>')
				for row in all_rows:
					f.write(f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></tr>')
				f.write(f'</table></body></html>')
				logfunc(f'Powerlog Device Screen Autolock function completed')
		else:
				logfunc('No Powerlog Device Screen Autolock available')
	except:
		logfunc('Error in Powerlog Device Screen Autolock Section.')

def delphotos(filefound):
	db = sqlite3.connect(filefound[0])
	cursor = db.cursor()
	try:
		cursor.execute('''
		Select
		z_pk,
		zfilename AS "File Name",
		zduration AS "Duration in Seconds",
		case
		when ztrashedstate = 1 then "Deleted"
		else "N/A"
		end AS "Is Deleted",
		case
		when zhidden =1 then "Hidden"
		else 'N/A'
		end AS "Is Hidden",
		datetime(ztrasheddate+978307200,'unixepoch','localtime') AS "Date Deleted",
		datetime(zaddeddate+978307200,'unixepoch','localtime') AS "Date Added",
		datetime(zdatecreated+978307200,'unixepoch','localtime') AS "Date Created",
		datetime(zmodificationdate+978307200,'unixepoch','localtime') AS "Date Modified",
		zdirectory AS "File Path"
		from zgenericasset
			''')

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			logfunc(f'Photos.sqlite metadata function executing')
			os.makedirs(reportfolderbase+'Photos.sqlite Metadata/')
			with open(reportfolderbase+'Photos.sqlite Metadata/Photos.sqLite DB.html', 'w', encoding='utf8') as f:
				f.write('<html><body>')
				f.write('<h2> Photos.sqlite Metadata report</h2>')
				f.write(f'Photos.sqlite Metadata entries: {usageentries}<br>')
				f.write(f'Photos.sqlite database located at: {filefound[0]}<br>')
				f.write('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
				f.write('<br/>')
				f.write('')
				f.write(f'<table>')
				f.write(f'<tr><td>Primary Key</td><td>File Name</td><td>Duration in seconds</td><td>Is Deleted</td><td>Is Hidden</td><td>Date Deleted</td><td>Date Added</td><td>Date Created</td><td>Date Modified</td><td>File Path</td></tr>')
				for row in all_rows:
					f.write(f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td></tr>')
				f.write(f'</table></body></html>')
				logfunc(f'Photos.sqlite Metadata function completed')
		else:
				logfunc('No Photos.sqlite Metadata available')
	except:
		logfunc('Error on Photos.sqlite function.')

def timezone(filefound):
	logfunc(f'Timezone function executing.')
	p = open(filefound[0], 'rb')
	plist = plistlib.load(p)
	
	#create html headers
	filedatahtml = open(reportfolderbase+'Build Info/TimeZone.html', mode='a+')
	filedatahtml.write('<html><body>')
	filedatahtml.write('<h2>TimeZone Report </h2>')
	filedatahtml.write(f'Timezone info located at: {filefound[0]}<br>')
	filedatahtml.write ('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style>')
	filedatahtml.write('<table>')
	#filedatahtml.write(f'<tr><td colspan = "2">{filefound[0]}</td></tr>')
	filedatahtml.write('<tr><td>Key</td><td>Value</td></tr>')

	for key, val in plist.items():
		filedatahtml.write(f'<tr><td>{key}</td><td>{val}</td></tr>')	

	filedatahtml.write('</table></html>')
	filedatahtml.close()
	logfunc(f'Timezone function completed.')

def webclips(filefound):
	logfunc('Webclips function executing')
	# Determine unique webclips
	print(filefound)
	webclip_ids = set()
	for path_val in filefound:
		path_val = path_val.split("/WebClips/")[1]
		unique_id = path_val.split(".webclip/")[0]
		if unique_id != '':
			webclip_ids.add(unique_id)
	print(webclip_ids)
	logfunc('Webclips function completed')