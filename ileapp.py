import sys, os, re, glob
from search_files import *
from ilapfuncs import *
import argparse
from argparse import RawTextHelpFormatter
from six.moves.configparser import RawConfigParser
from time import process_time
import  tarfile
import shutil


parser = argparse.ArgumentParser(description='iLEAPP: iOS Logs, Events, and Preferences Parser.')
parser.add_argument('-o', choices=['fs','tar', 'zip'], required=True, action="store",help="Directory path, TAR, or ZIP filename and path(required).")
parser.add_argument('pathtodir',help='Path to directory')

if len(sys.argv[1:])==0:
	parser.print_help()
	parser.exit()

start = process_time()
	
args = parser.parse_args()

pathto = args.pathtodir
extracttype = args.o
start = process_time()
'''	
tosearch = {'mib':'*mobile_installation.log.*', 'iconstate':'*SpringBoard/IconState.plist', 'lastbuild':'*LastBuildInfo.plist', 'iOSNotifications11':'*PushStore*', 'iOSNotifications12':'*private/var/mobile/Library/UserNotifications*',
		'wireless':'*wireless/Library/Preferences/com.apple.*','knowledgec':'*CoreDuet/Knowledge/knowledgeC.db','applicationstate':'*pplicationState.db*', 'conndevices':'*/iTunes_Control/iTunes/iTunesPrefs', 'ktx':'*.ktx*'}

'''	
tosearch = {'ktx':'*@3x.ktx*'}
'''	

	
os.makedirs(reportfolderbase)

print('\n--------------------------------------------------------------------------------------')
print('iLEAPP: iOS Logs, Events, and Preferences Parser')
print('Objective: Triage iOS Full System Extractions.')
print('By: Alexis Brignoni | @AlexisBrignoni | abrignoni.com')

if extracttype == 'fs':
	
	print(f'File/Directory selected: {pathto}')
	print('\n--------------------------------------------------------------------------------------')
	print( )

	log = open(reportfolderbase+'ProcessedFilesLog.txt', 'w+', encoding='utf8')
	nl = '\n' #literal in order to have new lines in fstrings that create text files
	log.write(f'Extraction/Path selected: {pathto}{nl}{nl}')
	
	# Search for the files per the arguments
	for key, val in tosearch.items():
		filefound = search(pathto, val)
		if not filefound:
			print()
			print(f'No files found for {key} -> {val}.')
			log.write(f'No files found for {key} -> {val}.{nl}')
		else:
			print()
			globals()[key](filefound)
			for pathh in filefound:
				log.write(f'Files for {val} located at {pathh}.{nl}')
	log.close()

elif extracttype == 'tar':
	
	print(f'File/Directory selected: {pathto}')
	print('\n--------------------------------------------------------------------------------------')
	
	log = open(reportfolderbase+'ProcessedFilesLog.txt', 'w+', encoding='utf8')
	nl = '\n' #literal in order to have new lines in fstrings that create text files
	log.write(f'Extraction/Path selected: {pathto}{nl}{nl}')	# tar searches and function calls
	
	for key, val in tosearch.items():
		filefound = searchtar(pathto, val, reportfolderbase)
		if not filefound:
			
			print()
			print(f'No files found for {key} -> {val}.')
			log.write(f'No files found for {key} -> {val}.{nl}')
		else:
			
			print()
			globals()[key](filefound)
			for pathh in filefound:
				log.write(f'Files for {val} located at {pathh}.{nl}')
	log.close()

elif extracttype == 'zip':
		
		print(f'File/Directory selected: {pathto}')
		print('\n--------------------------------------------------------------------------------------')
		print( )
		log = open(reportfolderbase+'ProcessedFilesLog.txt', 'w+', encoding='utf8')
		nl = '\n' #literal in order to have new lines in fstrings that create text files
		log.write(f'Extraction/Path selected: {pathto}{nl}{nl}')	# tar searches and function calls
		
		for key, val in tosearch.items():
			filefound = searchzip(pathto, val, reportfolderbase)
			if not filefound:
				print()
				print(f'No files found for {key} -> {val}.')
				log.write(f'No files found for {key} -> {val}.{nl}')
			else:
				
				print()
				globals()[key](filefound)
				for pathh in filefound:
					log.write(f'Files for {val} located at {pathh}.{nl}')
		log.close()

else:
	print('Error on argument -o')
	
if os.path.exists(reportfolderbase+'temp/'):
	shutil.rmtree(reportfolderbase+'temp/')		

#print(f'iOS version: {versionf} ')
print('')
print('Processes completed.')
end = process_time()
time = start - end
print("Processing time: " + str(abs(time)) )
	
