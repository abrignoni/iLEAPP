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
    elif os.path.isdir(i_path) and os.path.exists(os.path.join(i_path, "Manifest.db")):
        ext_type = 'itunes'
    elif os.path.isdir(i_path):
        ext_type = 'fs'
    else: # must be an existing file then
        if not i_path.lower().endswith('.tar') and not i_path.lower().endswith('.zip') and not i_path.lower().endswith('.gz'):
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
def CheckList(mtxt, lkey, mdstring, disable=False):
    if mdstring == 'photosMetadata' or mdstring == 'journalStrings' or mdstring == 'walStrings': #items in the if are modules that take a long time to run. Deselects them by default.
        dstate = False
    else:
        dstate = True
    return [sg.CBox(mtxt, default=dstate, key=lkey, metadata=mdstring, disabled=disable)]

def pickModules():
    global indx
    global mlist
    
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts', 'artifacts')

    # Create sorted dict from 'tosearch' dictionary based on plugin category
    sorted_tosearch = {k: v for k, v in sorted(tosearch.items(), key=lambda item: item[1][0].upper())}

    indx = 1000     # arbitrary number to not interfere with other controls
    for key, val in sorted_tosearch.items():
        disabled = False if key != 'lastBuild' else True # lastBuild is REQUIRED
        mlist.append( CheckList(val[0] + f' [{key}]', indx, key, disabled) )
        indx = indx + 1
        
sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.

normal_font = ("Helvetica", 12)
mlist = []
# go through list of available modules and confirm they exist on the disk
pickModules()
GuiWindow.progress_bar_total = len(ileapp.tosearch)


layout = [  [sg.Text('iOS Logs, Events, And Plists Parser', font=("Helvetica", 22))],
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
            window[x].Update(False if window[x].metadata != 'lastBuild' else True)  # lastBuild.py is REQUIRED
    if event == 'Process':
        #check is selections made properly; if not we will return to input form without exiting app altogether
        is_valid, extracttype = ValidateInput(values, window)
        if is_valid:
            GuiWindow.window_handle = window
            input_path = values[0]
            output_folder = values[1]

            # ios file system extractions contain paths > 260 char, which causes problems
            # This fixes the problem by prefixing \\?\ on each windows path.
            if is_platform_windows():
                if input_path[1] == ':' and extracttype =='fs': input_path = '\\\\?\\' + input_path.replace('/', '\\')
                if output_folder[1] == ':': output_folder = '\\\\?\\' + output_folder.replace('/', '\\')

            # re-create modules list based on user selection
            search_list = { 'lastBuild' : tosearch['lastBuild'] } # hardcode lastBuild as first item
            s_items = 0
            for x in range(1000,indx):
                if window.FindElement(x).Get():
                    key = window[x].metadata
                    if (key in tosearch) and (key != 'lastBuild'):
                        search_list[key] = tosearch[key]
                    s_items = s_items + 1 # for progress bar
                
                # no more selections allowed
                window[x].Update(disabled = True)

            window['SELECT ALL'].update(disabled=True)
            window['DESELECT ALL'].update(disabled=True)

            GuiWindow.window_handle = window
            out_params = OutputParameters(output_folder)
            crunch_successful = ileapp.crunch_artifacts(search_list, extracttype, input_path, out_params, len(ileapp.tosearch)/s_items)
            if crunch_successful:
                report_path = os.path.join(out_params.report_folder_base, 'index.html')
                
                if report_path.startswith('\\\\?\\'): # windows
                    report_path = report_path[4:]
                if report_path.startswith('\\\\'): # UNC path
                    report_path = report_path[2:]
                locationmessage = 'Report name: ' + report_path
                sg.Popup('Processing completed', locationmessage)
                webbrowser.open_new_tab('file://' + report_path)
            else:
                log_path = out_params.screen_output_file_path
                if log_path.startswith('\\\\?\\'): # windows
                    log_path = log_path[4:]
                sg.Popup('Processing failed    :( ', f'See log for error details..\nLog file located at {log_path}')
            break
window.close()
