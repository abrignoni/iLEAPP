import sys, os, re, glob
from search_files import *
from ilapfuncs import *
import argparse
from argparse import RawTextHelpFormatter
from six.moves.configparser import RawConfigParser
from time import process_time
import  tarfile
import shutil
from report import *
import zipfile

parser = argparse.ArgumentParser(description='iLEAPP: iOS Logs, Events, and Preferences Parser.')
parser.add_argument('-o', choices=['fs','tar', 'zip'], required=True, action="store",help="Directory path, TAR, or ZIP filename and path(required).")
parser.add_argument('pathtodir',help='Path to directory')

# if len(sys.argv[1:])==0:
# 	parser.logfunc_help()
# 	parser.exit()

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
			'ktx':'*.ktx*', 'calhist':'*CallHistory.storedata',
			'smschat':'*sms.db',
			'safari':'*History.db',
			'queryp':'*query_predictions.db',
			'powerlog':'*CurrentPowerlog.PLSQL',
			'accs':'*Accounts3.sqlite',
			'medlib':'*MediaLibrary.sqlitedb',
			'datausage':'*DataUsage.sqlite',
			'delphotos':'*Photos.sqlite',
			'timezone':'*mobile/Library/Preferences/com.apple.preferences.datetime.plist'}
'''
tosearch = {'mib':'*mobile_installation.log.*', 'iconstate':'*SpringBoard/IconState.plist', 'lastbuild':'*LastBuildInfo.plist', 'iOSNotifications11':'*PushStore*', 'iOSNotifications12':'*private/var/mobile/Library/UserNotifications*',
	'wireless':'*wireless/Library/Preferences/com.apple.*','knowledgec':'*CoreDuet/Knowledge/knowledgeC.db','applicationstate':'*pplicationState.db*', 'conndevices':'*/iTunes_Control/iTunes/iTunesPrefs', 'calhist':'*CallHistory.storedata', 'smschat':'*sms.db', 'safari':'*History.db','queryp':'*query_predictions.db','powerlog':'*CurrentPowerlog.PLSQL','accs':'*Accounts3.sqlite','medlib':'*MediaLibrary.sqlitedb', 'datausage':'*DataUsage.sqlite', 'delphotos':'*Photos.sqlite', 'timezone':'*mobile/Library/Preferences/com.apple.preferences.datetime.plist', 'bkupstate':'*/com.apple.MobileBackup.plist', 'mobilact':'*mobileactivationd.log.*', 'healthdb':'*healthdb_secure.sqlite', 'datark':'*Library/Lockdown/data_ark.plist'}



tosearch = {'ktx':'*.ktx*',}
'''
	
os.makedirs(reportfolderbase)
os.makedirs(reportfolderbase+'Script Logs')

logfunc('\n--------------------------------------------------------------------------------------')
logfunc('iLEAPP: iOS Logs, Events, and Preferences Parser')
logfunc('Objective: Triage iOS Full System Extractions.')
logfunc('By: Alexis Brignoni | @AlexisBrignoni | abrignoni.com')

if extracttype == 'fs':
	
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
	
	logfunc(f'File/Directory selected: {pathto}')
	logfunc('\n--------------------------------------------------------------------------------------')
	
	log = open(reportfolderbase+'Script Logs/ProcessedFilesLog.html', 'w+', encoding='utf8')
	nl = '\n' #literal in order to have new lines in fstrings that create text files
	log.write(f'Extraction/Path selected: {pathto}<br><br>')	# tar searches and function calls
	
	for key, val in tosearch.items():
		filefound = searchtar(pathto, val, reportfolderbase)
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
		
		logfunc(f'File/Directory selected: {pathto}')
		logfunc('\n--------------------------------------------------------------------------------------')
		logfunc('')
		log = open(reportfolderbase+'Script Logs/ProcessedFilesLog.html', 'w+', encoding='utf8')
		log.write(f'Extraction/Path selected: {pathto}<br><br>')	# tar searches and function calls

		z = zipfile.ZipFile(pathto)

		for key, val in tosearch.items():
			filefound = searchzip(z, val, reportfolderbase)
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
	
