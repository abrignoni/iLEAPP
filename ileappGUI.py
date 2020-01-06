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
import PySimpleGUI as sg

'''
parser = argparse.ArgumentParser(description='iLEAPP: iOS Logs, Events, and Preferences Parser.')
parser.add_argument('-o', choices=['fs','tar'], required=True, action="store",help="Directory path or TAR filename and path(required).")
parser.add_argument('pathtodir',help='Path to directory')

if len(sys.argv[1:])==0:
	parser.print_help()
	parser.exit()

start = process_time()
	
args = parser.parse_args()
'''

sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.

layout = [  [sg.Text('iOS Logs, Events, And Properties Parser.', font=("Helvetica", 25))], #added font type and font size
			[sg.Text('https://github.com/abrignoni/iLEAPP', font=("Helvetica", 18))],#added font type and font size
			[sg.Text('Select the file type or directory of the target iOS full file system extraction for parsing.', font=("Helvetica", 16))],#added font type and font size
			[sg.Radio('.Tar', "rad1", default=True, font=("Helvetica", 14)), sg.Radio('Directory', "rad1", font=("Helvetica", 14)), sg.Radio('.Zip', "rad1", font=("Helvetica", 14))], #added font type and font size
			[sg.Text('File:', size=(8, 1), font=("Helvetica", 14)), sg.Input(), sg.FileBrowse(font=("Helvetica", 12))], #added font type and font size
			[sg.Text('Directory:', size=(8, 1), font=("Helvetica", 14)), sg.Input(), sg.FolderBrowse(font=("Helvetica", 12))], #added font type and font size
			[sg.Output(size=(100,40))], #changed size from (88,20)
			[sg.Submit('Process',font=("Helvetica", 14)), sg.Button('Close', font=("Helvetica", 14))] ] #added font type and font size
			

# Create the Window
window = sg.Window('iLEAPP', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
	event, values = window.read()
	if event in (None, 'Close'):   # if user closes window or clicks cancel
		break
	#print('Selected:', values)
	print('Procesing started. Please wait. This may take a few minutes...')


	if values[0] == True:
		extracttype = 'tar'
		pathto = values[3]
		#print(pathto)
		if pathto.endswith('.tar'):
			pass
		else:
			sg.PopupError('No file or no .tar extension selected. Run the program again.')
			sys.exit()	
			
	elif values[1] == True:
		extracttype = 'fs'
		pathto = values[4]
		if os.path.isdir(pathto):
			pass
		else:
			sg.PopupError('No path or the one selected is invalid. Run the program again.', pathto)
			sys.exit()
	
	elif values[2] == True:
			extracttype = 'zip'
			pathto = values[3]
			if pathto.endswith('.zip'):
				pass
			else:
				sg.PopupError('No file or no .zip extension selected. Run the program again.', pathto)
				sys.exit()
	
	start = process_time()
	
	tosearch = {'mib':'*mobile_installation.log.*', 'iconstate':'*SpringBoard/IconState.plist', 'lastbuild':'*LastBuildInfo.plist', 'iOSNotifications11':'*PushStore*', 'iOSNotifications12':'*private/var/mobile/Library/UserNotifications*',
		'wireless':'*wireless/Library/Preferences/com.apple.*','knowledgec':'*CoreDuet/Knowledge/knowledgeC.db','applicationstate':'*pplicationState.db*', 'conndevices':'*/iTunes_Control/iTunes/iTunesPrefs', 'ktx':'*.ktx*', 'calhist':'*CallHistory.storedata', 'smschat':'*sms.db', 'safari':'*History.db','queryp':'*query_predictions.db','powerlog':'*CurrentPowerlog.PLSQL'}

			
	os.makedirs(reportfolderbase)
	os.makedirs(reportfolderbase+'Script Logs')

	
	window.refresh()
	print('\n--------------------------------------------------------------------------------------')
	print('iLEAPP: iOS Logs, Events, and Preferences Parser')
	print('Objective: Triage iOS Full System Extractions.')
	print('By: Alexis Brignoni | @AlexisBrignoni | abrignoni.com')
	window.refresh()
	
	if extracttype == 'fs':
		
		print(f'File/Directory selected: {pathto}')
		print('\n--------------------------------------------------------------------------------------')
		print('')
		window.refresh()
		log = open(reportfolderbase+'Script Logs/ProcessedFilesLog.html', 'w+', encoding='utf8')
		nl = '\n' #literal in order to have new lines in fstrings that create text files
		log.write(f'Extraction/Path selected: {pathto}<br><br>')
		
		# Search for the files per the arguments
		for key, val in tosearch.items():
			filefound = search(pathto, val)
			window.refresh()
			if not filefound:
				window.refresh()
				print()
				print(f'No files found for {key} -> {val}.')
				log.write(f'No files found for {key} -> {val}.<br><br>')
			else:
				print()
				window.refresh()
				globals()[key](filefound)
				for pathh in filefound:
					log.write(f'Files for {val} located at {pathh}.<br><br>')
		log.close()

	elif extracttype == 'tar':
		
		print(f'File/Directory selected: {pathto}')
		print('\n--------------------------------------------------------------------------------------')
		print('')
		window.refresh()
		log = open(reportfolderbase+'Script Logs/ProcessedFilesLog.html', 'w+', encoding='utf8')
		nl = '\n' #literal in order to have new lines in fstrings that create text files
		log.write(f'Extraction/Path selected: {pathto}<br><br>')	# tar searches and function calls
		
		
		for key, val in tosearch.items():
			filefound = searchtar(pathto, val, reportfolderbase)
			window.refresh()
			if not filefound:
				window.refresh()
				print()
				print(f'No files found for {key} -> {val}.')
				log.write(f'No files found for {key} -> {val}.<br><br>')
			else:
				
				print()
				window.refresh()
				globals()[key](filefound)
				for pathh in filefound:
					log.write(f'Files for {val} located at {pathh}.<br><br>')
		log.close()

	elif extracttype == 'zip':
			
			print(f'File/Directory selected: {pathto}')
			print('\n--------------------------------------------------------------------------------------')
			print('')
			window.refresh()
			log = open(reportfolderbase+'Script Logs/ProcessedFilesLog.html', 'w+', encoding='utf8')
			nl = '\n' #literal in order to have new lines in fstrings that create text files
			log.write(f'Extraction/Path selected: {pathto}<br><br>')	# tar searches and function calls
			
			for key, val in tosearch.items():
				filefound = searchzip(pathto, val, reportfolderbase)
				window.refresh()
				if not filefound:
					window.refresh()
					print()
					print(f'No files found for {key} -> {val}.')
					log.write(f'No files found for {key} -> {val}.<br><br>')
				else:
					
					print()
					window.refresh()
					globals()[key](filefound)
					for pathh in filefound:
						log.write(f'Files for {val} located at {pathh}.<br><br>')
			log.close()

	else:
		print('Error on argument -o')
		
	#if os.path.exists(reportfolderbase+'temp/'):
	#	shutil.rmtree(reportfolderbase+'temp/')		

	#print(f'iOS version: {versionf} ')
	
	print('')
	print('Processes completed.')
	end = process_time()
	time = start - end
	print("Processing time in secs: " + str(abs(time)) )
	
	log = open(reportfolderbase+'Script Logs/ProcessedFilesLog.html', 'a', encoding='utf8')
	log.write(f'Processing time in secs: {str(abs(time))}')
	log.close()
	
	report(reportfolderbase, time, extracttype, pathto)
	locationmessage = ('Report name: '+reportfolderbase)
	sg.Popup('Processing completed', locationmessage)
	sys.exit()
