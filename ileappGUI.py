import json
import pathlib
import typing
import ileapp
from icecream import ic
import PySimpleGUI as sg
import webbrowser
import plugin_loader
from scripts.ilapfuncs import *
from scripts.version_info import aleapp_version
from time import process_time, gmtime, strftime
from scripts.search_files import *

MODULE_START_INDEX = 1000

def ValidateInput(values, window):
    '''Returns tuple (success, extraction_type)'''
    global module_end_index

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
    for x in range(1000, module_end_index):
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
    global module_end_index
    global mlist
    global loader

    loader = plugin_loader.PluginLoader()

    module_end_index = MODULE_START_INDEX     # arbitrary number to not interfere with other controls
    for plugin in sorted(loader.plugins, key=lambda p: p.category.upper()):
        disabled = plugin.module_name == 'usagestatsVersion'
        mlist.append(CheckList(f'{plugin.category} [{plugin.name} - {plugin.module_name}.py]', module_end_index, plugin.name, disabled))
        module_end_index = module_end_index + 1
        
sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.

normal_font = ("Helvetica", 12)
loader: typing.Optional[plugin_loader.PluginLoader] = None
mlist = []
# go through list of available modules and confirm they exist on the disk
pickModules()
GuiWindow.progress_bar_total = len(loader)


layout = [  [sg.Text('iOS Logs, Events, And Plists Parser', font=("Helvetica", 22))],
            [sg.Text('https://github.com/abrignoni/iLEAPP', font=("Helvetica", 14))],
            [sg.Frame(layout=[
                    [sg.Input(size=(97,1)), 
                     sg.FileBrowse(font=normal_font, button_text='Browse File', key='INPUTFILEBROWSE'),
                     sg.FolderBrowse(font=normal_font, button_text='Browse Folder', target=(sg.ThisRow, -2), key='INPUTFOLDERBROWSE')
                    ]
                ],
                title='Select the file (tar/zip/gz) or directory of the target iOS full file system extraction for parsing:')],
            [sg.Frame(layout=[
                    [sg.Input(size=(112,1)), sg.FolderBrowse(font=normal_font, button_text='Browse Folder')]
                ], 
                    title='Select Output Folder:')],
            [sg.Text('Available Modules')],
            [sg.Button('Select All', key='SELECT ALL'), sg.Button('Deselect All', key='DESELECT ALL'),
             sg.Button('Load Profile', key='LOAD PROFILE'), sg.Button('Save Profile', key='SAVE PROFILE'),
             # sg.FileBrowse(
             #     button_text='Load Profile', key='LOADPROFILE', enable_events=True, target='LOADPROFILE',
             #     file_types=(('ALEAPP Profile (*.alprofile)', '*.alprofile'), ('All Files', '*'))),
             # sg.FileSaveAs(
             #     button_text='Save Profile', key='SAVEPROFILE', enable_events=True, target='SAVEPROFILE',
             #     file_types=(('ALEAPP Profile (*.alprofile)', '*.alprofile'), ('All Files', '*')),
             #     default_extension='.alprofile')
            sg.Text('  |', font=("Helvetica", 14)),
            sg.Button('Load Case Data', key='LOAD CASE DATA'),
            sg.Text('  |', font=("Helvetica", 14)),
            sg.Text('Timezone Offset:', font=("Helvetica", 14)),
            sg.Slider(range=(-12,14),
                        default_value=0,
                        size=(20,15),
                        orientation='horizontal',
                        font=('Helvetica', 14))
            ],
            [sg.Column(mlist, size=(300,310), scrollable=True),  sg.Output(size=(85,20))] ,
            [sg.ProgressBar(max_value=GuiWindow.progress_bar_total, orientation='h', size=(86, 7), key='PROGRESSBAR', bar_color=('DarkGreen', 'White'))],
            [sg.Submit('Process', font=normal_font), sg.Button('Close', font=normal_font)] ]
            
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
        for x in range(MODULE_START_INDEX, module_end_index):
            window[x].Update(True)
    if event == "DESELECT ALL":  
         # none modules
        for x in range(MODULE_START_INDEX, module_end_index):
            window[x].Update(False if window[x].metadata != 'lastBuild' else True)  # lastBuild.py is REQUIRED
    if event == "SAVE PROFILE":
        destination_path = sg.popup_get_file(
            "Save a profile", save_as=True,
            file_types=(('ALEAPP Profile (*.alprofile)', '*.alprofile'),),
            default_extension='.alprofile', no_window=True)

        if destination_path:
            ticked = []
            for x in range(MODULE_START_INDEX, module_end_index):
                if window.FindElement(x).Get():
                    key = window[x].metadata
                    ticked.append(key)
            with open(destination_path, "wt", encoding="utf-8") as profile_out:
                json.dump({"leapp": "aleapp", "format_version": 1, "plugins": ticked}, profile_out)
            sg.Popup(f"Profile saved: {destination_path}")

    if event == "LOAD PROFILE":
        destination_path = sg.popup_get_file(
            "Load a profile", save_as=False,
            file_types=(('ALEAPP Profile (*.alprofile)', '*.alprofile'), ('All Files', '*')),
            default_extension='.alprofile', no_window=True)

        if destination_path and os.path.exists(destination_path):
            profile_load_error = None
            with open(destination_path, "rt", encoding="utf-8") as profile_in:
                try:
                    profile = json.load(profile_in)
                except json.JSONDecodeError as json_ex:
                    profile_load_error = f"File was not a valid profile file: {json_ex}"

            if not profile_load_error:
                if isinstance(profile, dict):
                    if profile.get("leapp") != "aleapp" or profile.get("format_version") != 1:
                        profile_load_error = "File was not a valid profile file: incorrect LEAPP or version"
                    else:
                        ticked = set(profile.get("plugins", []))
                        ticked.add("lastbuild")  # always
                        for x in range(MODULE_START_INDEX, module_end_index):
                            if window[x].metadata in ticked:
                                window[x].update(True)
                            else:
                                window[x].update(False)
                else:
                    profile_load_error = "File was not a valid profile file: invalid format"

            if profile_load_error:
                sg.popup(profile_load_error)
            else:
                sg.popup(f"Loaded profile: {destination_path}")
    
    if event == 'LOAD CASE DATA':
        destination_path = sg.popup_get_file(
            "Load a case data", save_as=False,
            file_types=(('ALEAPP Profile (*.alprofile)', '*.alprofile'), ('All Files', '*')),
            default_extension='.alprofile', no_window=True)
        
        if destination_path and os.path.exists(destination_path):
            profile_load_error = None
            with open(destination_path, "rt", encoding="utf-8") as profile_in:
                try:
                    profile = json.load(profile_in)
                except json.JSONDecodeError as json_ex:
                    profile_load_error = f"File was not a valid profile file: {json_ex}"
                    
            if not profile_load_error:
                if isinstance(profile, dict):
                    casedata = profile
                else:
                    profile_load_error = "File was not a valid profile file: invalid format"
            
            if profile_load_error:
                sg.popup(profile_load_error)
            else:
                sg.popup(f"Loaded Case Data: {destination_path}")
    
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
            # search_list = { 'lastBuild' : tosearch['lastBuild'] } # hardcode lastBuild as first item
            search_list = [loader['lastbuild']] # hardcode lastBuild as first item

            s_items = 0
            for x in range(MODULE_START_INDEX, module_end_index):
                if window.FindElement(x).Get():
                    key = window[x].metadata
                    if key in loader and key != 'lastbuild':
                        search_list.append(loader[key])
                    s_items = s_items + 1 # for progress bar
                
                # no more selections allowed
                window[x].Update(disabled=True)

            window['SELECT ALL'].update(disabled=True)
            window['DESELECT ALL'].update(disabled=True)

            GuiWindow.window_handle = window
            out_params = OutputParameters(output_folder)
            wrap_text = True
            time_offset = values[2]
            
            try:
                casedata
            except NameError:
                casedata = {}
            
            crunch_successful = ileapp.crunch_artifacts(
                search_list, extracttype, input_path, out_params, len(loader)/s_items, wrap_text, loader, casedata, time_offset)
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
