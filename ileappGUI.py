import ileapp
import os
import PySimpleGUI as sg
import sys
import webbrowser

from scripts.ilapfuncs import *
from scripts.version_info import aleapp_version
from time import process_time, gmtime, strftime

sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.

normal_font = ("Helvetica", 12)

layout = [  [sg.Text('iOS Logs, Events, And Protobuf Parser', font=("Helvetica", 22))],
            [sg.Text('https://github.com/abrignoni/iLEAPP', font=("Helvetica", 14))],
            [sg.Text('Select the file type or directory of the target iOS full file system extraction for parsing.', font=normal_font)],
            [sg.Radio('.Tar', "rad1", default=True, font=normal_font), sg.Radio('Directory', "rad1", font=normal_font), sg.Radio('.Zip', "rad1", font=normal_font)],
            [sg.Text('Input File', size=(12, 1), font=normal_font), sg.Input(), sg.FileBrowse(font=normal_font)],
            [sg.Text('Input Folder', size=(12, 1), font=normal_font), sg.Input(), sg.FolderBrowse(font=normal_font)],
            [sg.Text('Output Folder', size=(12, 1), font=normal_font), sg.Input(), sg.FolderBrowse(font=normal_font)],
            [sg.Checkbox('Generate CSV output (Additional processing time)', size=(50, 1), default=False, font=normal_font)],
            [sg.Output(size=(104,20))], #changed size from (88,20)
            [sg.Submit('Process',font=normal_font), sg.Button('Close', font=normal_font)] ]
            
# Create the Window
window = sg.Window(f'iLEAPP version {aleapp_version}', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event in (None, 'Close'):   # if user closes window or clicks cancel
        break
      
    output_folder = values[5]
    if values[1] == True:
        input_path = values[4]
    else:
        input_path = values[3]

    if len(output_folder) == 0:
        sg.PopupError('No OUTPUT folder selected. Run the program again.')
        sys.exit()

    if len(input_path) == 0:
        sg.PopupError('No INPUT file or folder selected. Run the program again.')
        sys.exit()

    if not os.path.exists(input_path):
        sg.PopupError('INPUT file/folder does not exist! Run the program again.')
        sys.exit()

    output_folder = os.path.abspath(output_folder)
    
    if event == 'Process':
        if values[0] == True:
            extracttype = 'tar'
            if not input_path.lower().endswith('.tar'):
                sg.PopupError('Input file does not have .tar extension! Run the program again.', input_path)
                sys.exit()   
                
        elif values[1] == True:
            extracttype = 'fs'
            if not os.path.isdir(input_path):
                sg.PopupError('Input path is not a valid folder. Run the program again.', input_path)
                sys.exit()
        
        elif values[2] == True:
            extracttype = 'zip'
            if not input_path.lower().endswith('.zip'):
                sg.PopupError('No file or no .zip extension selected. Run the program again.', input_path)
                sys.exit()
                
        GuiWindow.window_handle = window
        out_params = OutputParameters(output_folder)
        ileapp.crunch_artifacts(extracttype, input_path, out_params)
        
        if values[6] == True:
            start = process_time()
            logfunc('')
            logfunc(f'CSV export starting. This might take a while...')
            html2csv(out_params.report_folder_base) 
            end = process_time()
            csv_time_secs =  end - start
            csv_time_HMS = strftime('%H:%M:%S', gmtime(csv_time_secs))
            logfunc("CSV processing time = {}".format(csv_time_HMS))

        report_path = os.path.join(out_params.report_folder_base, 'index.html')
        locationmessage = 'Report name: ' + report_path
        sg.Popup('Processing completed', locationmessage)
        
        #basep = os.getcwd()
        if report_path.startswith('\\\\'): # UNC path
            report_path = report_path[2:]
        webbrowser.open_new_tab('file://' + report_path)
        break
window.close()