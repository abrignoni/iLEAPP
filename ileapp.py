import argparse
import glob
import os
import re
import shutil
import sys
import tarfile
from argparse import RawTextHelpFormatter
from tarfile import TarFile
from time import process_time
from zipfile import ZipFile

from six.moves.configparser import RawConfigParser

from ilapfuncs import *
from report import *
from search_files import *


parser = argparse.ArgumentParser(description='iLEAPP: iOS Logs, Events, and Preferences Parser.')
parser.add_argument('-o', choices=['fs','tar', 'zip'], required=True, action="store",help="Directory path, TAR, or ZIP filename and path(required).")
parser.add_argument('pathtodir',help='Path to directory')

start = process_time()
	
args = parser.parse_args()

pathto = args.pathtodir
extracttype = args.o
start = process_time()


tosearch = {'mib':'*mobile_installation.log.*',
			'iconstate':'*SpringBoard/IconState.plist',
			'webclips': '*WebClips/*.webclip/*',
			'lastbuild':'*LastBuildInfo.plist',
			'iOSNotifications11':'*PushStore*',
			'iOSNotifications12':'*private/var/mobile/Library/UserNotifications*',
			'wireless':'*wireless/Library/Preferences/com.apple.*',
			'knowledgec':'*CoreDuet/Knowledge/knowledgeC.db',
			'applicationstate':'*pplicationState.db*',
			'conndevices':'*/iTunes_Control/iTunes/iTunesPrefs',
			'calhist':'*CallHistory.storedata',
			'smschat':'*sms.db',
			'safari':'*History.db',
			'queryp':'*query_predictions.db',
			'powerlog':'*CurrentPowerlog.PLSQL',
			'accs':'*Accounts3.sqlite',
			'medlib':'*MediaLibrary.sqlitedb',
			'datausage':'*DataUsage.sqlite',
			'delphotos':'*Photos.sqlite',
			'timezone':'*mobile/Library/Preferences/com.apple.preferences.datetime.plist',
			'bkupstate':'*/com.apple.MobileBackup.plist',
			'mobilact':'*mobileactivationd.log.*', 
			'healthdb':'*healthdb_secure.sqlite', 
			'datark':'*Library/Lockdown/data_ark.plist',
			'wiloc':'*cache_encryptedB.db',
			'aggdict':'*AggregateDictionary/ADDataStore.sqlitedb',
			'dbbuff':'*AggregateDictionary/dbbuffer',
			'confaccts':'*com.apple.accounts.exists.plist',
			'calendar':'*Calendar.sqlitedb',
			'mailprotect':'*private/var/mobile/Library/Mail/* Index*',
			'screentime': '*/Library/Application Support/com.apple.remotemanagementd/RMAdminStore*',
			'bluetooths': '*/Library/Database/com.apple.MobileBluetooth*',
			'whatsapp':'*ChatStorage.sqlite',
			'ipscl':'*.ips',
			'wapcontact':'*ContactsV2.sqlite',
			'actrec':'*activation_record.plist',
			'DHCPhp':'*private/var/db/dhcpd_leases*',
			'DHCPL':'*private/var/db/dhcpclient/leases/en*',
			'redditusers':'*Data/Application/*/Documents/*/accounts/*',
			'redditchats':'*Data/Application/*/Documents/*/accountData/*/chat/*/chat.sqlite',
			'interactionc':'*interactionC.db'}

os.makedirs(reportfolderbase)
os.makedirs(reportfolderbase+'Script Logs')

logfunc('\n--------------------------------------------------------------------------------------')
logfunc('iLEAPP: iOS Logs, Events, and Preferences Parser')
logfunc('Objective: Triage iOS Full System Extractions.')
logfunc('By: Alexis Brignoni | @AlexisBrignoni | abrignoni.com')

if extracttype == 'fs':
	
	logfunc(f'Artifact categories to parse: {str(len(tosearch))}')
	logfunc(f'File/Directory selected: {pathto}')
	logfunc('\n--------------------------------------------------------------------------------------')
	logfunc( )

	log = open(reportfolderbase+'Script Logs/ProcessedFilesLog.html', 'w+', encoding='utf8')
	nl = '\n' #literal in order to have new lines in fstrings that create text files
	log.write(f'Extraction/Path selected: {pathto}<br><br>')
	
	# Search for the files per the arguments
	for key, val in tosearch.items():
		filefound = search(pathto, val)
		if not filefound:
			logfunc()
			logfunc(f'No files found for {key} -> {val}.')
			log.write(f'No files found for {key} -> {val}.<br>')
		else:
			logfunc()
			globals()[key](filefound)
			for pathh in filefound:
				log.write(f'Files for {val} located at {pathh}.<br>')
	log.close()

elif extracttype == 'tar':
	
	logfunc(f'Artifact categories to parse: {str(len(tosearch))}')
	logfunc(f'File/Directory selected: {pathto}')
	logfunc('\n--------------------------------------------------------------------------------------')
	
	log = open(reportfolderbase+'Script Logs/ProcessedFilesLog.html', 'w+', encoding='utf8')
	nl = '\n' #literal in order to have new lines in fstrings that create text files
	log.write(f'Extraction/Path selected: {pathto}<br><br>')	# tar searches and function calls

	t = TarFile(pathto)

	for key, val in tosearch.items():
		filefound = searchtar(t, val, reportfolderbase)
		if not filefound:
			
			logfunc()
			logfunc(f'No files found for {key} -> {val}.')
			log.write(f'No files found for {key} -> {val}.<br>')
		else:
			
			logfunc()
			globals()[key](filefound)
			for pathh in filefound:
				log.write(f'Files for {val} located at {pathh}.<br>')
	log.close()

elif extracttype == 'zip':
		
		logfunc(f'Artifact categories to parse: {str(len(tosearch))}')
		logfunc(f'File/Directory selected: {pathto}')
		logfunc('\n--------------------------------------------------------------------------------------')
		logfunc('')
		log = open(reportfolderbase+'Script Logs/ProcessedFilesLog.html', 'w+', encoding='utf8')
		log.write(f'Extraction/Path selected: {pathto}<br><br>')	# tar searches and function calls

		z = ZipFile(pathto)
		name_list = z.namelist()
		for key, val in tosearch.items():
			filefound = searchzip(z, name_list, val, reportfolderbase)
			if not filefound:
				logfunc('')
				logfunc(f'No files found for {key} -> {val}.')
				log.write(f'No files found for {key} -> {val}.<br>')
			else:
				
				logfunc('')
				globals()[key](filefound)
				for pathh in filefound:
					log.write(f'Files for {val} located at {pathh}.<br>')
		log.close()

		z.close()

else:
	logfunc('Error on argument -o')
'''	
if os.path.exists(reportfolderbase+'temp/'):
	shutil.rmtree(reportfolderbase+'temp/')
	#call reporting script		
'''
#logfunc(f'iOS version: {versionf} ')


logfunc('')
logfunc('Processes completed.')
end = process_time()
time = start - end
logfunc("Processing time: " + str(abs(time)) )

log = open(reportfolderbase+'Script Logs/ProcessedFilesLog.html', 'a', encoding='utf8')
log.write(f'Processing time in secs: {str(abs(time))}')
log.close()

logfunc('')
logfunc('Report generation started.')
report(reportfolderbase, time, extracttype, pathto)
logfunc('Report generation Completed.')
logfunc('')
logfunc(f'Report name: {reportfolderbase}')
	
