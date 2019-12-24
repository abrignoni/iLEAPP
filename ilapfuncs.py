import sqlite3
import sys, os, re
import glob
import ccl_bplist
import datetime
import plistlib
from time import process_time

nl = '\n' 
now = datetime.datetime.now()
currenttime = str(now.strftime('%Y-%m-%d_%A_%H%M%S'))
reportfolderbase = './ILAP_Reports_'+currenttime+'/'
temp = reportfolderbase+'temp/'
#Create run directory 



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
'''
def devicespecific(filefound):
	print(f'Device Specific (IMEI, Phone number) function executing.')
	os.makedirs(reportfolderbase+'Device_Specific/')
	f =open(reportfolderbase+'Device_Specific/com.apple.commcenter.device_specific_nobackup.plist.txt','w')
	p = open(filefound[0], 'rb')
	plist = plistlib.load(p)
	for key, val in plist.items():
		f.write(f'{key} -> {val}{nl}')
	f.close()
	print(f'Device Specific function completed.')
'''	
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
	print(f'Lastbuild function executing.')
	os.makedirs(reportfolderbase+'LastBuildInfo_Plist/')
	f =open(reportfolderbase+'LastBuildInfo_Plist/ LastBuildInfo.plist.txt','w')
	p = open(filefound[0], 'rb')
	plist = plistlib.load(p)
	for key, val in plist.items():
		f.write(f'{key} -> {val}{nl}')
	f.close()
	print(f'Lastbuild function completed.')

def iOSNotifications11(filefound):
	print(f'iOSNotifications 11 function executed.')
	os.makedirs(reportfolderbase+'iOS_11_Notifications/')

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
	print('iOS 12 & 13 Notifications function completed.')
