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
from time import process_time

nl = '\n' 
now = datetime.datetime.now()
currenttime = str(now.strftime('%Y-%m-%d_%A_%H%M%S'))
reportfolderbase = './ILAP_Reports_'+currenttime+'/'
temp = reportfolderbase+'temp/'
#Create run directory 

def applicationstate(filefound):
	print(f'ApplicationState.db queries executing.')
	outpath = reportfolderbase +'ApplicationState_data/'
	
	try: 
		os.mkdir(outpath)
		os.mkdir(outpath+"exported-dirty/")
		os.mkdir(outpath+"exported-clean/")
	except OSError:  
		print("Error making directories")
	
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
		
	for filename in glob.glob(outpath+'exported-clean/*.bplist'):	
		p = open(filename, 'rb')
		#cfilename = os.path.basename(filename)
		plist = ccl_bplist.load(p)
		ns_keyed_archiver_obj = ccl_bplist.deserialise_NsKeyedArchiver(plist, parse_whole_structure=False)#deserialize clean
		#print(cfilename)
		bid = (ns_keyed_archiver_obj['bundleIdentifier'])
		bpath = (ns_keyed_archiver_obj['bundlePath'])
		bcontainer = (ns_keyed_archiver_obj['bundleContainerPath'])
		bsandbox = (ns_keyed_archiver_obj['sandboxPath'])
		
		
		with open(outpath+'ApplicationState_InstalledAppInfo.csv', mode='a+') as filedata:
			filewrite = csv.writer(filedata, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			filewrite.writerow([bid, bpath, bcontainer, bsandbox])
			count = count + 1
		
	if os.path.exists(outpath+'exported-clean/'):
		shutil.rmtree(outpath+'exported-clean/')	
	if os.path.exists(outpath+'exported-dirty/'):
		shutil.rmtree(outpath+'exported-dirty/')
			
	print(f'Installed app GUIDs and app locations processed: {count}')
	print(f'ApplicationState.db queries completed.')
	
def knowledgec(filefound):
	print(f'Incepted bplist extractions in knowlwdgeC.db executing.')

	iOSversion = versionf

	supportediOS = ['11', '12']

	if iOSversion not in supportediOS:
		print ("Unsupported version"+iOSversion)
		return()
		
	extension = '.bplist'
	dump = True
	#create directories
	outpath = reportfolderbase+'knowledgeC_incepton_bplist/'


	try: 
		os.mkdir(outpath)
		os.mkdir(outpath+"clean/")
		os.mkdir(outpath+"/dirty")
	except OSError:  
		print("Error making directories")
		
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

	h = open(outpath+'/Report.html', 'w')	
	h.write('<html><body>')
	h.write('<h2>iOS ' + iOSversion + ' - KnowledgeC ZSTRUCTUREDMETADATA bplist report</h2>')
	h.write ('<style> table, th, td {border: 1px solid black; border-collapse: collapse;}</style>')
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
		
		#print some values from clean bplist
		NSdata = (ns_keyed_archiver_obj["root"]["intent"]["backingStore"]["data"]["NS.data"])
		
		parsedNSData = ""
		#Default true
		if dump == True:	
			nsdata_file = outpath+'/clean/'+cfilename+'_nsdata.bin'
			binfile = open(nsdata_file, 'wb')
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
		
		#print(NSstartDate)
		#print(NSendDate)
		#print(NSduration)
		#print(NSdata)
		#print('')


	print("")	
	print("iOS - KnowledgeC ZSTRUCTUREDMETADATA bplist extractor")
	print("By: @phillmoore & @AlexisBrignoni")
	print("thinkdfir.com & abrignoni.com")
	print("")
	print("Bplists from the Z_DKINTENTMETADATAKEY__SERIALIZEDINTERACTION field.")
	print("Exported bplists (dirty): "+str(dirtcount))
	print("Exported bplists (clean): "+str(cleancount))
	print("")
	print(f'Triage report completed. See Reports.html.')
	print('Incepted bplist extractions in knowlwdgeC.db completed')
re

def mib(filefound):
	print(f'Mobile Installation Logs function executing.')
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
				matchObj = re.search( r"(?<=for \()(.*)(?=\))", line) #Regex for bundle id
				if matchObj:
					bundleid = matchObj.group(1)
				
				matchObj = re.search( r"(?<=^)(.*)(?= \[)", line) #Regex for timestamp
				if matchObj:
					timestamp = matchObj.group(1)
					weekday, month, day, time, year = (str.split(timestamp))
					day = day_converter(day)
					month = month_converter(month)
					inserttime = str(year)+ '-'+ str(month) + '-' + str(day) + ' ' + str(time)
					#print(inserttime)
					#print(month)
					#print(day)
					#print(year)
					#print(time)
					#print ("Timestamp: ", timestamp)
				
				#print(inserttime, actiondesc, bundleid)
				
				#insert to database
				cursor = db.cursor()
				datainsert = (inserttime, actiondesc, bundleid, '' ,)
				cursor.execute('INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)', datainsert)
				db.commit()
				
				#print()
					
			
			matchObj = re.search( r"(Destroying container with identifier)", line) #Regex for destroyed containers
			if matchObj:
				actiondesc = "Destroying container"
				#print(actiondesc)
				#print("Destroyed containers:")
				matchObj = re.search( r"(?<=identifier )(.*)(?= at )", line) #Regex for bundle id
				if matchObj:
					bundleid = matchObj.group(1)
					#print ("Bundle ID: ", bundleid )
			
				matchObj = re.search( r"(?<=^)(.*)(?= \[)", line) #Regex for timestamp
				if matchObj:
					timestamp = matchObj.group(1)
					weekday, month, day, time, year = (str.split(timestamp))
					day = day_converter(day)
					month = month_converter(month)
					inserttime = str(year)+ '-'+ str(month) + '-' + str(day) + ' ' + str(time)
					#print(inserttime)
					#print(month)
					#print(day)
					#print(year)
					#print(time)
					#print ("Timestamp: ", timestamp)
				
				matchObj = re.search( r"(?<= at )(.*)(?=$)", line) #Regex for path
				if matchObj:
					path = matchObj.group(1)
					#print ("Path: ", matchObj.group(1))
				
			
				#print(inserttime, actiondesc, bundleid, path)			
				
				#insert to database
				cursor = db.cursor()
				datainsert = (inserttime, actiondesc, bundleid, path ,)
				cursor.execute('INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)', datainsert)
				db.commit()
				
				#print()
				

			matchObj = re.search( r"(Data container for)", line) #Regex Moved data containers
			if matchObj:
				actiondesc = "Data container moved"
				#print(actiondesc)
				#print("Data container moved:")
				matchObj = re.search( r"(?<=for )(.*)(?= is now )", line) #Regex for bundle id
				if matchObj:
					bundleid = matchObj.group(1)
					#print ("Bundle ID: ", bundleid )
			
				matchObj = re.search( r"(?<=^)(.*)(?= \[)", line) #Regex for timestamp
				if matchObj:
					timestamp = matchObj.group(1)
					weekday, month, day, time, year = (str.split(timestamp))
					day = day_converter(day)
					month = month_converter(month)
					inserttime = str(year)+ '-'+ str(month) + '-' + str(day) + ' ' + str(time)
					#print(inserttime)
					#print(month)
					#print(day)
					#print(year)
					#print(time)
					#print ("Timestamp: ", timestamp)
				
				matchObj = re.search( r"(?<= at )(.*)(?=$)", line) #Regex for path
				if matchObj:
					path = matchObj.group(1)
					#print ("Path: ", matchObj.group(1))
					
				#print(inserttime, actiondesc, bundleid, path)			
				
				#insert to database
				cursor = db.cursor()
				datainsert = (inserttime, actiondesc, bundleid, path ,)
				cursor.execute('INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)', datainsert)
				db.commit()
				
				#print()
				
			matchObj = re.search( r"(Made container live for)", line) #Regex for made container
			if matchObj:
				actiondesc = "Made container live"
				#print(actiondesc)
				#print("Made container:")
				matchObj = re.search( r"(?<=for )(.*)(?= at)", line) #Regex for bundle id
				if matchObj:
					bundleid = matchObj.group(1)
					#print ("Bundle ID: ", bundleid )
			
				matchObj = re.search( r"(?<=^)(.*)(?= \[)", line) #Regex for timestamp
				if matchObj:
					timestamp = matchObj.group(1)
					weekday, month, day, time, year = (str.split(timestamp))
					day = day_converter(day)
					month = month_converter(month)
					inserttime = str(year)+ '-'+ str(month) + '-' + str(day) + ' ' + str(time)
					#print(inserttime)
					#print(month)
					#print(day)
					#print(year)
					#print(time)
					#print ("Timestamp: ", timestamp)
				
				matchObj = re.search( r"(?<= at )(.*)(?=$)", line) #Regex for path
				if matchObj:
					path = matchObj.group(1)
					#print ("Path: ", matchObj.group(1))
				#print(inserttime, actiondesc, bundleid, path)			
				
				#insert to database
				cursor = db.cursor()
				datainsert = (inserttime, actiondesc, bundleid, path ,)
				cursor.execute('INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)', datainsert)
				db.commit()
				
			matchObj = re.search( r"(Uninstalling identifier )", line) #Regex for made container
			if matchObj:
				actiondesc = "Uninstalling identifier"
				#print(actiondesc)
				#print("Uninstalling identifier")
				matchObj = re.search( r"(?<=Uninstalling identifier )(.*)", line) #Regex for bundle id
				if matchObj:
					bundleid = matchObj.group(1)
					#print ("Bundle ID: ", bundleid )
			
				matchObj = re.search( r"(?<=^)(.*)(?= \[)", line) #Regex for timestamp
				if matchObj:
					timestamp = matchObj.group(1)
					weekday, month, day, time, year = (str.split(timestamp))
					day = day_converter(day)
					month = month_converter(month)
					inserttime = str(year)+ '-'+ str(month) + '-' + str(day) + ' ' + str(time)
					#print(inserttime)
					#print(month)
					#print(day)
					#print(year)
					#print(time)
					#print ("Timestamp: ", timestamp)
				
				#insert to database
				cursor = db.cursor()
				datainsert = (inserttime, actiondesc, bundleid, '' ,)
				cursor.execute('INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)', datainsert)
				db.commit()

			matchObj = re.search( r"(main: Reboot detected)", line) #Regex for reboots
			if matchObj:
				actiondesc = "Reboot detected"
				#print(actiondesc)		
				matchObj = re.search( r"(?<=^)(.*)(?= \[)", line) #Regex for timestamp
				if matchObj:
					timestamp = matchObj.group(1)
					weekday, month, day, time, year = (str.split(timestamp))
					day = day_converter(day)
					month = month_converter(month)
					inserttime = str(year)+ '-'+ str(month) + '-' + str(day) + ' ' + str(time)
					#print(inserttime)
					#print(month)
					#print(day)
					#print(year)
					#print(time)
					#print ("Timestamp: ", timestamp)
				
				#insert to database
				cursor = db.cursor()
				datainsert = (inserttime, actiondesc, '', '' ,)
				cursor.execute('INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)', datainsert)
				db.commit()			
				
			matchObj = re.search( r"(Attempting Delta patch update of )", line) #Regex for Delta patch
			if matchObj:
				actiondesc = "Attempting Delta patch"
				#print(actiondesc)
				#print("Made container:")
				matchObj = re.search( r"(?<=Attempting Delta patch update of )(.*)(?= from)", line) #Regex for bundle id
				if matchObj:
					bundleid = matchObj.group(1)
					#print ("Bundle ID: ", bundleid )
			
				matchObj = re.search( r"(?<=^)(.*)(?= \[)", line) #Regex for timestamp
				if matchObj:
					timestamp = matchObj.group(1)
					weekday, month, day, time, year = (str.split(timestamp))
					day = day_converter(day)
					month = month_converter(month)
					inserttime = str(year)+ '-'+ str(month) + '-' + str(day) + ' ' + str(time)
					#print(inserttime)
					#print(month)
					#print(day)
					#print(year)
					#print(time)
					#print ("Timestamp: ", timestamp)
				
				matchObj = re.search( r"(?<= from )(.*)", line) #Regex for path
				if matchObj:
					path = matchObj.group(1)
					#print ("Path: ", matchObj.group(1))
				#print(inserttime, actiondesc, bundleid, path)			
				
				#insert to database
				cursor = db.cursor()
				datainsert = (inserttime, actiondesc, bundleid, path ,)
				cursor.execute('INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)', datainsert)
				db.commit()
				
				#print()
	try:
		print ('Logs processed: ', filescounter)
		print ('Lines processed: ', counter)
		print ()
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
			#print(row[0])
			distinctbundle = row[0]
			cursor.execute('''SELECT * from dimm where bundle_id=? order by time_stamp desc limit 1''', (distinctbundle,))
			all_rows_iu = cursor.fetchall()
			for row in all_rows_iu:
				#print(row[0], row[1], row[2], row[3])
				if row[2] == '':
					continue
				elif row[1] == 'Destroying container':
					#print(row[0], row[1], row[2], row[3])
					uninstallcount = uninstallcount + 1
					totalapps = totalapps + 1
					#tofile1 = row[0] + ' ' + row[1] + ' ' + row[2] + ' ' + row[3] + '\n'
					tofile1 = row[2] +  '\n'
					f1.write(tofile1)
					#print()
				elif row[1] == 'Uninstalling identifier':
					#print(row[0], row[1], row[2], row[3])
					uninstallcount = uninstallcount + 1
					totalapps = totalapps + 1
					#tofile1 = row[0] + ' ' + row[1] + ' ' + row[2] + ' ' + row[3] + '\n'
					tofile1 = row[2] +  '\n'
					f1.write(tofile1)
					#print()
				else:
					#print(row[0], row[1], row[2], row[3])
					tofile2 = row[2] + '\n'
					
					f2.write(tofile2)
					installedcount = installedcount + 1	
					totalapps = totalapps + 1
		
		f1.close()
		f2.close()
		
		#Query to create historical report per app
					
		cursor.execute('''SELECT distinct bundle_id from dimm''')
		all_rows = cursor.fetchall()
		for row in all_rows:
			#print(row[0])
			distinctbundle = row[0]
			if row[0] == '':
				continue
			else:
				f3=open(reportfolderbase+'Mobile_Installation_Logs/Apps_Historical/' + distinctbundle + '.txt', 'w+', encoding="utf8") #Create historical app report per app
				cursor.execute('''SELECT * from dimm where bundle_id=? order by time_stamp DESC''', (distinctbundle,)) #Query to create app history per bundle_id
				all_rows_hist = cursor.fetchall()
				for row in all_rows_hist:
					#print(row[0], row[1], row[2], row[3])
					tofile3 = row[0] + ' ' + row[1] + ' ' + row[2] + ' ' + row[3] + '\n'
					f3.write(tofile3)			
			f3.close()
			historicalcount = historicalcount + 1
		
		#Query to create system events
					
		cursor.execute('''SELECT * from dimm where action ='Reboot detected' order by time_stamp DESC''')
		all_rows = cursor.fetchall()
		for row in all_rows:
			#print(row[0])
			#print(row[0], row[1], row[2], row[3])
			tofile4 = row[0] + ' ' + row[1] + ' ' + row[2] + ' ' + row[3] + '\n'
			f4.write(tofile4)
			sysstatecount = sysstatecount + 1		
			
		
			
					
		print ('Total apps: ', totalapps)
		print ('Total installed apps: ', installedcount)
		print ('Total uninstalled apps: ', uninstallcount)
		print ('Total historical app reports: ', historicalcount)
		print ('Total system state events: ', sysstatecount)
		print ('Mobile Installation Logs function completed.')
		f1.close()
		f2.close()
		f4.close()

	except:
		print("Log files not found in "+input_path)
	
def wireless(filefound):
	print(f'Cellular Wireless files function executing')
	os.makedirs(reportfolderbase+'Cellular_Wireless_Info/')
	for filepath in filefound:
		basename = os.path.basename(filepath)
		if basename.endswith('.plist'):	
			f =open(reportfolderbase+'Cellular_Wireless_Info/'+basename+'.txt','w')
			p = open(filepath, 'rb')
			plist = plistlib.load(p)
			for key, val in plist.items():
				f.write(f'{key} -> {val}{nl}')
			f.close()
	print(f'Cellular Wireless files function completed')
	
def iconstate(filefound):
	print(f'Iconstate function executing.')
	os.makedirs(reportfolderbase+'IconState_Plist/')
	f =open(reportfolderbase+'IconState_Plist/ IconState.plist.txt','w')
	p = open(filefound[0], 'rb')
	plist = plistlib.load(p)
	for key, val in plist.items():
		f.write(f'{key} -> {val}{nl}')
	f.close()
	print(f'Iconstate function completed.')
	
def lastbuild(filefound):
	global versionf
	print(f'Lastbuild function executing.')
	os.makedirs(reportfolderbase+'LastBuildInfo_Plist/')
	f =open(reportfolderbase+'LastBuildInfo_Plist/ LastBuildInfo.plist.txt','w')
	p = open(filefound[0], 'rb')
	plist = plistlib.load(p)
	for key, val in plist.items():
		f.write(f'{key} -> {val}{nl}')
		versionnum = val[0:2]
		if versionnum in ('11','12','13'):
			versionf = versionnum 
			print(f'iOS version is: {versionf}')
	f.close()
	print(f'Lastbuild function completed.')

def iOSNotifications11(filefound):
	print(f'iOSNotifications 11 function executing.')
	
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
		print("No PushStore directory located")
	else:
		folder = (reportfolderbase+'iOS_11_Notifications/') #add the date thing from phill
		os.makedirs( folder )
		#print("Processing:")
		for filename in glob.iglob(pathfound+'\**', recursive=True):
			if os.path.isfile(filename): # filter dirs
				file_name = os.path.splitext(os.path.basename(filename))[0]
					#get extension and iterate on those files
					#file_extension = os.path.splitext(filename)
					#print(file_extension)
					#create directory
				if filename.endswith('pushstore'):
						#create directory where script is running from
					print (filename) #full path
					notdircount = notdircount + 1				
						#print (os.path.basename(file_name)) #filename with  no extension
					openplist = (os.path.basename(os.path.normpath(filename))) #filename with extension
						#print (openplist)
						#bundlepath = (os.path.basename(os.path.dirname(filename)))#previous directory
					bundlepath = file_name
					appdirect = (folder + "\\"+ bundlepath) 
						#print(appdirect)
					os.makedirs( appdirect )
						
						#open the plist
					p = open(filename, 'rb')
					plist = ccl_bplist.load(p)
					plist2 = plist["$objects"]

					long = len(plist2)
					#print (long)
					h = open('./'+appdirect+'/DeliveredNotificationsReport.html', 'w') #write report
					h.write('<html><body>')
					h.write('<h2>iOS Delivered Notifications Triage Report </h2>')
					h.write(filename)
					h.write('<br/>')
					h.write ('<style> table, th, td {border: 1px solid black; border-collapse: collapse;}</style>')
					h.write('<br/>')
						
					h.write('<button onclick="hideRows()">Hide rows</button>')
					h.write('<button onclick="showRows()">Show rows</button>')
						
					with open("script.txt") as f:
						for line in f:
							h.write(line)
						
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
								#print (timestamp)
							
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
						#print (types)
						try:
							for k, v in liste.items():
								if k == 'NS.data':
									chk = str(v)
									reduced = (chk[2:8])
									#print (reduced)
									if reduced == "bplist":
										count = count + 1
										binfile = open('./'+appdirect+'/incepted'+str(count)+'.bplist', 'wb')
										binfile.write(v)
										binfile.close()

										procfile = open('./'+appdirect+'/incepted'+str(count)+'.bplist', 'rb')
										secondplist = ccl_bplist.load(procfile)
										secondplistint = secondplist["$objects"]
										print('Bplist processed and exported.')
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


	print("Total notification directories processed:"+str(notdircount))
	print("Total exported bplists from notifications:"+str(exportedbplistcount))
	if notdircount == 0:
			print('No notifications located.')
	print(f'iOSNotifications 11 function completed.')
	
def iOSNotifications12(filefound):
	print(f'iOS 12 & 13 Notifications function executing')
	os.makedirs(reportfolderbase+'iOS_12+13_Notifications/')

	count = 0
	notdircount = 0
	exportedbplistcount = 0
	unix = datetime.datetime(1970, 1, 1)  # UTC
	cocoa = datetime.datetime(2001, 1, 1)  # UTC
	delta = cocoa - unix 
	
	with open('NotificationParams.txt', 'r') as f:
		notiparams = [line.strip() for line in f]
	
	folder = (reportfolderbase+'iOS_12+13_Notifications/') 
	#print("Processing:")
	pathfound = str(filefound[0])
	#print(f'Posix to string is: {pathfound}')
	for filename in glob.iglob(pathfound+'/**', recursive=True):
		#create directory where script is running from
		if os.path.isfile(filename): # filter dirs
			file_name = os.path.splitext(os.path.basename(filename))[0]
			#create directory
			if 'DeliveredNotifications' in file_name:
				#create directory where script is running from
				#print (filename) #full path
				notdircount = notdircount + 1				
				#print (os.path.basename(file_name)) #filename with  no extension
				openplist = (os.path.basename(os.path.normpath(filename))) #filename with extension
				#print (openplist)
				bundlepath = (os.path.basename(os.path.dirname(filename)))#previous directory
				appdirect = (folder + "/"+ bundlepath) 
				#print(appdirect)
				os.makedirs( appdirect )
				
				#open the plist
				p = open(filename, 'rb')
				plist = ccl_bplist.load(p)
				plist2 = plist["$objects"]

				long = len(plist2)
				#print (long)
				h = open('./'+appdirect+'/DeliveredNotificationsReport.html', 'w') #write report
				h.write('<html><body>')
				h.write('<h2>iOS Delivered Notifications Triage Report </h2>')
				h.write ('<style> table, th, td {border: 1px solid black; border-collapse: collapse;}</style>')
				h.write(filename)
				h.write('<br/>')
				h.write('<br/>')
				
				h.write('<button onclick="hideRows()">Hide rows</button>')
				h.write('<button onclick="showRows()">Show rows</button>')
				
				with open("script.txt") as f:
					for line in f:
						h.write(line)
				
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
							#print (timestamp)
						
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
					#print (types)
					try:
						for k, v in liste.items():
							if k == 'NS.data':
								chk = str(v)
								reduced = (chk[2:8])
								#print (reduced)
								if reduced == "bplist":
									count = count + 1
									binfile = open('./'+appdirect+'/incepted'+str(count)+'.bplist', 'wb')
									binfile.write(v)
									binfile.close()

									procfile = open('./'+appdirect+'/incepted'+str(count)+'.bplist', 'rb')
									secondplist = ccl_bplist.load(procfile)
									secondplistint = secondplist["$objects"]
									print('Bplist processed and exported.')
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

	print("Total notification directories processed:"+str(notdircount))
	print("Total exported bplists from notifications:"+str(exportedbplistcount))
	if notdircount == 0:
		print('No notifications located.')
	print('iOS 12 & 13 Notifications function completed.')
