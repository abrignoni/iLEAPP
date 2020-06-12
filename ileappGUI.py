import ileapp
import os
import PySimpleGUI as sg
import sys
import webbrowser

from scripts.ilapfuncs import *
from scripts.version_info import aleapp_version
from time import process_time, gmtime, strftime
from scripts.ilap_artifacts import *
from scripts.search_files import *

def ValidateInput(values, window):
    '''Returns tuple (success, extraction_type)'''
    global indx

    i_path = values[0] # input file/folder
    o_path = values[1] # output folder
    ext_type = ''

    if len(i_path) == 0:
        sg.PopupError('No INPUT file or folder selected!')
        return False, ext_type
    elif not os.path.exists(i_path):
        sg.PopupError('INPUT file/folder does not exist!')
        return False, ext_type
    elif os.path.isdir(i_path):
        ext_type = 'fs'
    else: # must be an existing file then
        if not i_path.lower().endswith('.tar') and not i_path.lower().endswith('.zip'):
            sg.PopupError('Input file is not a supported archive! ', i_path)
            return False, ext_type
        else:
            ext_type = Path(i_path).suffix[1:].lower() 
    
    # check output now
    if len(o_path) == 0 : # output folder
        sg.PopupError('No OUTPUT folder selected!')
        return False, ext_type

    one_element_is_selected = False
    for x in range(1000, indx):
        if window.FindElement(x).Get():
            one_element_is_selected = True
            break
    if not one_element_is_selected:
        sg.PopupError('No module selected for processing!')
        return False, ext_type

    return True, ext_type

# initialize CheckBox control with module name   
def CheckList(mtxt, lkey, mdstring):
    return [sg.CBox(mtxt, default=True, key=lkey, metadata=mdstring)]

# verify module (.py) file exists; only then add it to the "list"
def pickModules():
    global indx
    global mlist
    
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts', 'artifacts')

    indx = 1000     # arbitrary number to not interfere with other controls
    for key, val in tosearch.items():
        plugin_path = os.path.join(script_path, key + '.py')
        mlist.append( CheckList(key + '.py [' + val[0] + ']', indx, key) )
        indx = indx + 1
        
sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.

normal_font = ("Helvetica", 12)
mlist = []
# go through list of available modules and confirm they exist on the disk
pickModules()
GuiWindow.progress_bar_total = len(ileapp.tosearch)


layout = [  [sg.Text('iOS Logs, Events, And Properties Parser', font=("Helvetica", 22))],
            [sg.Text('https://github.com/abrignoni/iLEAPP', font=("Helvetica", 14))],
            [sg.Frame(layout=[
                    [sg.Input(size=(97,1)), 
                     sg.FileBrowse(font=normal_font, button_text='Browse File', key='INPUTFILEBROWSE'),
                     sg.FolderBrowse(font=normal_font, button_text='Browse Folder', target=(sg.ThisRow, -2), key='INPUTFOLDERBROWSE')
                    ]
                ],
                title='Select the file type or directory of the target iOS full file system extraction for parsing:')],
            [sg.Frame(layout=[
                    [sg.Input(size=(112,1)), sg.FolderBrowse(font=normal_font, button_text='Browse Folder')]
                ], 
                    title='Select Output Folder:')],
            [sg.Text('Available Modules')],
            [sg.Button('SELECT ALL'), sg.Button('DESELECT ALL')], 
            [sg.Column(mlist, size=(300,310), scrollable=True),  sg.Output(size=(85,20))] ,
            [sg.ProgressBar(max_value=GuiWindow.progress_bar_total, orientation='h', size=(86, 7), key='PROGRESSBAR', bar_color=('Red', 'White'))],
            [sg.Submit('Process',font=normal_font), sg.Button('Close', font=normal_font)] ]
            
# Create the Window
window = sg.Window(f'iLEAPP version {aleapp_version}', layout)
GuiWindow.progress_bar_handle = window['PROGRESSBAR']


# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event in (None, 'Close'):   # if user closes window or clicks cancel
        break

    if event == "SELECT ALL":  
        # mark all modules
        for x in range(1000,indx):
            window[x].Update(True)
    if event == "DESELECT ALL":  
         # none modules
        for x in range(1000,indx):
            window[x].Update(False) 
    if event == 'Process':
        #check is selections made properly; if not we will return to input form without exiting app altogether
        is_valid, extracttype = ValidateInput(values, window)
        if is_valid:
            GuiWindow.window_handle = window
            input_path = values[0]
            output_folder = values[1]
            
            # re-create modules list based on user selection
            search_list = {}
            s_items = 0
            for x in range(1000,indx):
                if window.FindElement(x).Get():
                    if window[x].metadata in tosearch:
                        search_list[window[x].metadata] = tosearch[window[x].metadata]
                        s_items = s_items + 1 #for progress bar
                
            # no more selections allowed
            window[x].Update(disabled = True)
                
            window['SELECT ALL'].update(disabled=True)
            window['DESELECT ALL'].update(disabled=True)
        
            GuiWindow.window_handle = window
            out_params = OutputParameters(output_folder)
            ileapp.crunch_artifacts(search_list, extracttype, input_path, out_params, len(ileapp.tosearch)/s_items)
            
            '''
            if values[5] == True:
                start = process_time()
                logfunc('')
                logfunc(f'CSV export starting. This might take a while...')
                html2csv(out_params.report_folder_base) 
                end = process_time()
                csv_time_secs =  end - start
                csv_time_HMS = strftime('%H:%M:%S', gmtime(csv_time_secs))
                logfunc("CSV processing time = {}".format(csv_time_HMS))
            '''
            report_path = os.path.join(out_params.report_folder_base, 'index.html')
            locationmessage = 'Report name: ' + report_path
            sg.Popup('Processing completed', locationmessage)
            
            if report_path.startswith('\\\\'): # UNC path
                report_path = report_path[2:]
            webbrowser.open_new_tab('file://' + report_path)
            break
window.close()