import sys, os, re, glob
from search_files import *
from ilapfuncs import *
import argparse
from argparse import RawTextHelpFormatter
from six.moves.configparser import RawConfigParser
from time import process_time
import  tarfile
import shutil
import webbrowser
from report import *
import PySimpleGUI as sg

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
	#logfunc('Selected:', values)

	if values[0] == True:
		extracttype = 'tar'
		pathto = values[3]
		#logfunc(pathto)
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

	tosearch = {'mib': '*mobile_installation.log.*',
				'iconstate': '*SpringBoard/IconState.plist',
				'webclips': '*WebClips/*.webclip/*',
				'lastbuild': '*LastBuildInfo.plist',
				'iOSNotifications11': '*PushStore*',
				'iOSNotifications12': '*private/var/mobile/Library/UserNotifications*',
				'wireless': '*wireless/Library/Preferences/com.apple.*',
				'knowledgec': '*CoreDuet/Knowledge/knowledgeC.db',
				'applicationstate': '*pplicationState.db*',
				'conndevices': '*/iTunes_Control/iTunes/iTunesPrefs',
				'ktx': '*.ktx*', 'calhist': '*CallHistory.storedata',
				'smschat': '*sms.db',
				'safari': '*History.db',
				'queryp': '*query_predictions.db',
				'powerlog': '*CurrentPowerlog.PLSQL',
				'accs': '*Accounts3.sqlite',
				'medlib': '*MediaLibrary.sqlitedb',
				'datausage': '*DataUsage.sqlite',
				'delphotos': '*Photos.sqlite',
				'timezone': '*mobile/Library/Preferences/com.apple.preferences.datetime.plist'}
	'''
	tosearch = {'mib':'*mobile_installation.log.*', 'iconstate':'*SpringBoard/IconState.plist', 'lastbuild':'*LastBuildInfo.plist', 'iOSNotifications11':'*PushStore*', 'iOSNotifications12':'*private/var/mobile/Library/UserNotifications*',
		'wireless':'*wireless/Library/Preferences/com.apple.*','knowledgec':'*CoreDuet/Knowledge/knowledgeC.db','applicationstate':'*pplicationState.db*', 'conndevices':'*/iTunes_Control/iTunes/iTunesPrefs', 'calhist':'*CallHistory.storedata', 'smschat':'*sms.db', 'safari':'*History.db','queryp':'*query_predictions.db','powerlog':'*CurrentPowerlog.PLSQL','accs':'*Accounts3.sqlite','medlib':'*MediaLibrary.sqlitedb', 'datausage':'*DataUsage.sqlite', 'delphotos':'*Photos.sqlite', 'timezone':'*mobile/Library/Preferences/com.apple.preferences.datetime.plist', 'bkupstate':'*/com.apple.MobileBackup.plist', 'mobilact':'*mobileactivationd.log.*', 'healthdb':'*healthdb_secure.sqlite','datark':'*Library/Lockdown/data_ark.plist'}
    
	tosearch = {'ktx':'*.ktx*'}
	'''
			
	os.makedirs(reportfolderbase)
	os.makedirs(reportfolderbase+'Script Logs')
	logfunc('Procesing started. Please wait. This may take a few minutes...')

	
	window.refresh()
	logfunc('\n--------------------------------------------------------------------------------------')
	logfunc('iLEAPP: iOS Logs, Events, and Preferences Parser')
	logfunc('Objective: Triage iOS Full System Extractions.')
	logfunc('By: Alexis Brignoni | @AlexisBrignoni | abrignoni.com')
	window.refresh()
	
	if extracttype == 'fs':
		
		logfunc(f'File/Directory selected: {pathto}')
		logfunc('\n--------------------------------------------------------------------------------------')
		logfunc('')
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
				logfunc('')
				logfunc(f'No files found for {key} -> {val}.')
				log.write(f'No files found for {key} -> {val}.<br><br>')
			else:
				logfunc('')
				window.refresh()
				globals()[key](filefound)
				for pathh in filefound:
					log.write(f'Files for {val} located at {pathh}.<br><br>')
		log.close()

	elif extracttype == 'tar':
		
		logfunc(f'File/Directory selected: {pathto}')
		logfunc('\n--------------------------------------------------------------------------------------')
		logfunc('')
		window.refresh()
		log = open(reportfolderbase+'Script Logs/ProcessedFilesLog.html', 'w+', encoding='utf8')
		nl = '\n' #literal in order to have new lines in fstrings that create text files
		log.write(f'Extraction/Path selected: {pathto}<br><br>')	# tar searches and function calls
		
		
		for key, val in tosearch.items():
			filefound = searchtar(pathto, val, reportfolderbase)
			window.refresh()
			if not filefound:
				window.refresh()
				logfunc('')
				logfunc(f'No files found for {key} -> {val}.')
				log.write(f'No files found for {key} -> {val}.<br><br>')
			else:
				
				logfunc('')
				window.refresh()
				globals()[key](filefound)
				for pathh in filefound:
					log.write(f'Files for {val} located at {pathh}.<br><br>')
		log.close()

	elif extracttype == 'zip':
			
			logfunc(f'File/Directory selected: {pathto}')
			logfunc('\n--------------------------------------------------------------------------------------')
			logfunc('')
			window.refresh()
			log = open(reportfolderbase+'Script Logs/ProcessedFilesLog.html', 'w+', encoding='utf8')
			nl = '\n' #literal in order to have new lines in fstrings that create text files
			log.write(f'Extraction/Path selected: {pathto}<br><br>')	# tar searches and function calls
			
			for key, val in tosearch.items():
				filefound = searchzip(pathto, val, reportfolderbase)
				window.refresh()
				if not filefound:
					window.refresh()
					logfunc('')
					logfunc(f'No files found for {key} -> {val}.')
					log.write(f'No files found for {key} -> {val}.<br><br>')
				else:
					
					logfunc('')
					window.refresh()
					globals()[key](filefound)
					for pathh in filefound:
						log.write(f'Files for {val} located at {pathh}.<br><br>')
			log.close()

	else:
		logfunc('Error on argument -o')
	
		
	#if os.path.exists(reportfolderbase+'temp/'):
	#	shutil.rmtree(reportfolderbase+'temp/')		

	#logfunc(f'iOS version: {versionf} ')
	
	logfunc('')
	logfunc('Processes completed.')
	end = process_time()
	time = start - end
	logfunc("Processing time in secs: " + str(abs(time)) )
	
	log = open(reportfolderbase+'Script Logs/ProcessedFilesLog.html', 'a', encoding='utf8')
	log.write(f'Processing time in secs: {str(abs(time))}')
	log.close()
	
	report(reportfolderbase, time, extracttype, pathto)
	locationmessage = ('Report name: '+reportfolderbase+'index.html')
	sg.Popup('Processing completed', locationmessage)
	
	basep = os.getcwd()
	webbrowser.open_new_tab('file://'+basep+base+'index.html')
	sys.exit()
