import tkinter as tk
import plugin_loader
import typing
import json
import ileapp
import webbrowser
import scripts.logo_b64 as leapp_logo

from tkinter import ttk, filedialog as tk_filedialog, messagebox as tk_msgbox
from scripts.version_info import ileapp_version
from scripts.search_files import *


def pickModules():
    '''Create a list of available modules:
        - iTunesBackupInfo and lastBuild that need to be executed first are excluded
        - ones that take a long time to run are deselected by default'''
    global mlist
    global loader

    loader = plugin_loader.PluginLoader()

    for plugin in sorted(loader.plugins, key=lambda p: p.category.upper()):
        if plugin.module_name == 'iTunesBackupInfo' or plugin.module_name == 'lastBuild':
            continue
        #items that take a long time to run are deselected by default.
        enabled = not (plugin.module_name == 'photosMetadata' or plugin.module_name == 'walStrings')
        mlist[plugin] = tk.BooleanVar(value=enabled)


def get_selected_modules():
    '''Update the number and return the list of selected modules'''
    selected_modules = []

    for plugin, state in mlist.items():
        if state.get():
            selected_modules.append(plugin.name)

    selected_modules_label.config(text=f'Number of selected modules: {len(selected_modules)} / {len(mlist)}')
    return selected_modules


def select_all():
    '''Select all modules in the list of available modules and execute get_selected_modules'''
    for plugin in mlist:
        main_window.nametowidget(f'f_modules.f_list.tbox.mcb_{plugin.module_name}').select()

    get_selected_modules()


def deselect_all():
    '''Unselect all modules in the list of available modules and execute get_selected_modules'''
    for plugin in mlist:
        main_window.nametowidget(f'f_modules.f_list.tbox.mcb_{plugin.module_name}').deselect()

    get_selected_modules()


def load_profile():
    '''Select modules from a profile file'''
    global profile_filename

    destination_path = tk_filedialog.askopenfilename(parent=main_window, 
                                                     title='Load a profile', 
                                                     filetypes=(('iLEAPP Profile', '*.ilprofile'),))

    if destination_path and os.path.exists(destination_path):
        profile_load_error = None
        with open(destination_path, 'rt', encoding='utf-8') as profile_in:
            try:
                profile = json.load(profile_in)
            except:
                profile_load_error = 'File was not a valid profile file: invalid format'
        if not profile_load_error:
            if isinstance(profile, dict):
                if profile.get('leapp') != 'ileapp' or profile.get('format_version') != 1:
                    profile_load_error = 'File was not a valid profile file: incorrect LEAPP or version'
                else:
                    deselect_all()
                    ticked = set(profile.get('plugins', []))
                    for plugin in mlist:
                        if plugin.name in ticked:
                            main_window.nametowidget(f'f_modules.f_list.tbox.mcb_{plugin.module_name}').select()
                    get_selected_modules()
            else:
                profile_load_error = 'File was not a valid profile file: invalid format'
        if profile_load_error:
            tk_msgbox.showerror(title='Error', message=profile_load_error, parent=main_window)
        else:
            profile_filename = destination_path
            tk_msgbox.showinfo(title='Profile loaded', message=f'Loaded profile: {destination_path}', parent=main_window)


def save_profile():
    '''Save selected modules in a profile file'''
    destination_path = tk_filedialog.asksaveasfilename(parent=main_window, 
                                                       title='Save a profile', 
                                                       filetypes=(('iLEAPP Profile', '*.ilprofile'),))

    if destination_path:
        selected_modules = get_selected_modules()
        with open(destination_path, 'wt', encoding='utf-8') as profile_out:
            json.dump({'leapp': 'ileapp', 'format_version': 1, 'plugins': selected_modules}, profile_out)
        tk_msgbox.showinfo(title='Save a profile', message=f'Profile saved: {destination_path}', parent=main_window)


def scroll(event):
    '''Continue to scroll the list with mouse wheel when cursor hover a checkbutton'''
    parent = main_window.nametowidget(event.widget.winfo_parent())
    parent.event_generate('<MouseWheel>', delta=event.delta, when='now')
 

def ValidateInput():
    '''Returns tuple (success, extraction_type)'''
    i_path = input_entry.get() # input file/folder
    o_path = output_entry.get() # output folder
    ext_type = ''

    # check input
    if len(i_path) == 0:
        tk_msgbox.showerror(title='Error', message='No INPUT file or folder selected!', parent=main_window)
        return False, ext_type
    elif not os.path.exists(i_path):
        tk_msgbox.showerror(title='Error', message='INPUT file/folder does not exist!', parent=main_window)
        return False, ext_type
    elif os.path.isdir(i_path) and os.path.exists(os.path.join(i_path, 'Manifest.db')):
        ext_type = 'itunes'
    elif os.path.isdir(i_path):
        ext_type = 'fs'
    else:
        ext_type = Path(i_path).suffix[1:].lower() 

    # check output now
    if len(o_path) == 0 : # output folder
        tk_msgbox.showerror(title='Error', message='No OUTPUT folder selected!', parent=main_window)
        return False, ext_type

    # check if at least one module is selected
    if len(get_selected_modules()) == 0:
        tk_msgbox.showerror(title='Error', message='No module selected for processing!', parent=main_window)
        return False, ext_type

    return True, ext_type


def process(casedata):
    '''Execute selected modules and create reports'''
    #check if selections made properly; if not we will return to input form without exiting app altogether
    is_valid, extracttype = ValidateInput()

    if is_valid:
        GuiWindow.window_handle = main_window
        input_path = input_entry.get()
        output_folder = output_entry.get()

        # ios file system extractions contain paths > 260 char, which causes problems
        # This fixes the problem by prefixing \\?\ on each windows path.
        if is_platform_windows():
            if input_path[1] == ':' and extracttype =='fs': input_path = '\\\\?\\' + input_path.replace('/', '\\')
            if output_folder[1] == ':': output_folder = '\\\\?\\' + output_folder.replace('/', '\\')

        selected_modules = get_selected_modules()
        selected_modules.insert(0, 'lastbuild') # Force lastBuild as first item to be parsed
        selected_modules = [loader[module] for module in selected_modules]
        progress_bar.config(maximum=len(selected_modules))
        casedata = {key:value.get() for key, value in casedata.items()}
        out_params = OutputParameters(output_folder)
        wrap_text = True
        time_offset = timezone_set.get()
        if time_offset == '':
            time_offset = 'UTC'
        
        crunch_successful = ileapp.crunch_artifacts(
            selected_modules, extracttype, input_path, out_params, wrap_text, loader, casedata, time_offset, profile_filename)

        if crunch_successful:
            report_path = os.path.join(out_params.report_folder_base, 'index.html')
            if report_path.startswith('\\\\?\\'): # windows
                report_path = report_path[4:]
            if report_path.startswith('\\\\'): # UNC path
                report_path = report_path[2:]
            locationmessage = 'Report name: ' + report_path
            tk_msgbox.showinfo(title='Processing completed', message=locationmessage, parent=main_window)
            webbrowser.open_new_tab('file://' + report_path)
            main_window.quit()
        else:
            log_path = out_params.screen_output_file_path
            if log_path.startswith('\\\\?\\'): # windows
                log_path = log_path[4:]
            tk_msgbox.showerror(title='Error', message=f'Processing failed  :( \nSee log for error details..\nLog file located at {log_path}', parent=main_window)


def select_input(button_type):
    '''Select source and insert its path into input field'''
    if button_type == 'file':
        input_filename = tk_filedialog.askopenfilename(parent=main_window, 
                                                       title='Select a file', 
                                                       filetypes=(('tar file', '*.tar'), ('zip file', '*.zip'), ('gz file', '*.gz')))
    else:
        input_filename = tk_filedialog.askdirectory(parent=main_window, title='Select a folder')
    input_entry.delete(0, 'end')
    input_entry.insert(0, input_filename)


def select_output():
    '''Select target and insert its path into output field'''
    output_filename = tk_filedialog.askdirectory(parent=main_window, title='Select a folder')
    output_entry.delete(0, 'end')
    output_entry.insert(0, output_filename)


# GUI layout
## Case Data
def case_data():
    '''Add Case Data window'''
    global casedata
    
    def clear():
        '''Remove the contents of all fields'''
        case_number_entry.delete(0, 'end')
        case_agency_entry.delete(0, 'end')
        case_examiner_entry.delete(0, 'end')
    

    def save_case():
        '''Save case data in a Case Data file'''
        destination_path = tk_filedialog.asksaveasfilename(parent=case_window, 
                                                        title='Save a case data file', 
                                                        filetypes=(('iLEAPP Case Data', '*.lcasedata'),))

        if destination_path:
            json_casedata = {key:value.get() for key, value in casedata.items()}
            with open(destination_path, 'wt', encoding='utf-8') as case_data_out:
                json.dump({'leapp': 'case_data', 'case_data_values': json_casedata}, case_data_out)
            tk_msgbox.showinfo(title='Save Case Data', message=f'Case Data saved: {destination_path}', parent=case_window)


    def load_case():
        '''Import case data from a Case Data file'''
        destination_path = tk_filedialog.askopenfilename(parent=case_window, 
                                                     title='Load case data', 
                                                     filetypes=(('LEAPP Case Data', '*.lcasedata'),))

        if destination_path and os.path.exists(destination_path):
            case_data_load_error = None
            with open(destination_path, 'rt', encoding='utf-8') as case_data_in:
                try:
                    case_data = json.load(case_data_in)
                except:
                    case_data_load_error = 'File was not a valid case data file: invalid format'
            if not case_data_load_error:
                if isinstance(case_data, dict):
                    if case_data.get('leapp') != 'case_data':
                        case_data_load_error = 'File was not a valid case data file'
                    else:
                        casedata = case_data.get('case_data_values', {})
                        case_number_entry.delete(0, 'end')
                        case_number_entry.insert(0, casedata.get('Case Number', ''))
                        case_agency_entry.delete(0, 'end')
                        case_agency_entry.insert(0, casedata.get('Agency', ''))
                        case_examiner_entry.delete(0, 'end')
                        case_examiner_entry.insert(0, casedata.get('Examiner', ''))
                else:
                    case_data_load_error = 'File was not a valid case data file: invalid format'
            if case_data_load_error:
                tk_msgbox.showerror(title='Error', message=case_data_load_error, parent=case_window)
            else:
                tk_msgbox.showinfo(title='Load Case Data', message=f'Loaded Case Data: {destination_path}', parent=case_window)


    ### Case Data Window creation
    case_window = tk.Toplevel(main_window)
    case_window_width = 610
    case_window_height = 250

    #### Places Case Data window in the center of the screen
    screen_width = main_window.winfo_screenwidth()
    screen_height = main_window.winfo_screenheight()
    margin_width = (screen_width - case_window_width) // 2
    margin_height = (screen_height - case_window_height) // 2

    #### Case Data window properties
    case_window.geometry(f'{case_window_width}x{case_window_height}+{margin_width}+{margin_height}')
    case_window.resizable(False, False)
    case_window.configure(bg=theme_bgcolor)
    case_window.title('Add Case Data')

    #### Layout
    case_title_label = ttk.Label(case_window, text='Add Case Data', font=('Helvetica', f'{int(1.8 * font_size)}'))
    case_title_label.pack(padx=14, pady=7, anchor='w')
    case_number_frame = ttk.LabelFrame(case_window, text=' Case Number ')
    case_number_frame.pack(padx=14, pady=5, anchor='w')
    case_number_entry = ttk.Entry(case_number_frame, textvariable=casedata['Case Number'], width=casedata_entry_width)
    case_number_entry.pack(side='left', padx=5, pady=4)
    case_number_entry.focus()
    case_agency_frame = ttk.LabelFrame(case_window, text=' Agency ')
    case_agency_frame.pack(padx=14, pady=5, anchor='w')
    case_agency_entry = ttk.Entry(case_agency_frame, textvariable=casedata['Agency'], width=casedata_entry_width)
    case_agency_entry.pack(side='left', padx=5, pady=4)
    case_examiner_frame = ttk.LabelFrame(case_window, text=' Examiner ')
    case_examiner_frame.pack(padx=14, pady=5, anchor='w')
    case_examiner_entry = ttk.Entry(case_examiner_frame, textvariable=casedata['Examiner'], width=casedata_entry_width)
    case_examiner_entry.pack(side='left', padx=5, pady=4)
    modules_btn_frame = ttk.Frame(case_window)
    modules_btn_frame.pack(anchor='w', padx=14, pady=8)
    load_case_button = ttk.Button(modules_btn_frame, text='Load Case Data File', command=load_case)
    load_case_button.pack(side='left', padx=5)
    save_case_button = ttk.Button(modules_btn_frame, text='Save Case Data File', command=save_case)
    save_case_button.pack(side='left', padx=5)
    ttk.Separator(modules_btn_frame,orient='vertical').pack(side='left', fill='y', padx=20)
    clear_case_button = ttk.Button(modules_btn_frame, text='Clear', command=clear)
    clear_case_button.pack(side='left', padx=5)
    close_case_button = ttk.Button(modules_btn_frame, text='Close', command=case_window.destroy)
    close_case_button.pack(side='left', padx=5)

    case_window.grab_set()


## Main window creation
main_window = tk.Tk()
window_width = 900
window_height = 600

## Variables
loader: typing.Optional[plugin_loader.PluginLoader] = None
mlist = {}
profile_filename = None
tzvalues = ['Africa/Abidjan', 'Africa/Accra', 'Africa/Addis_Ababa', 'Africa/Algiers', 'Africa/Asmara', 'Africa/Asmera', 'Africa/Bamako', 'Africa/Bangui', 'Africa/Banjul', 'Africa/Bissau', 'Africa/Blantyre', 'Africa/Brazzaville', 'Africa/Bujumbura', 'Africa/Cairo', 'Africa/Casablanca', 'Africa/Ceuta', 'Africa/Conakry', 'Africa/Dakar', 'Africa/Dar_es_Salaam', 'Africa/Djibouti', 'Africa/Douala', 'Africa/El_Aaiun', 'Africa/Freetown', 'Africa/Gaborone', 'Africa/Harare', 'Africa/Johannesburg', 'Africa/Juba', 'Africa/Kampala', 'Africa/Khartoum', 'Africa/Kigali', 'Africa/Kinshasa', 'Africa/Lagos', 'Africa/Libreville', 'Africa/Lome', 'Africa/Luanda', 'Africa/Lubumbashi', 'Africa/Lusaka', 'Africa/Malabo', 'Africa/Maputo', 'Africa/Maseru', 'Africa/Mbabane', 'Africa/Mogadishu', 'Africa/Monrovia', 'Africa/Nairobi', 'Africa/Ndjamena', 'Africa/Niamey', 'Africa/Nouakchott', 'Africa/Ouagadougou', 'Africa/Porto-Novo', 'Africa/Sao_Tome', 'Africa/Timbuktu', 'Africa/Tripoli', 'Africa/Tunis', 'Africa/Windhoek', 'America/Adak', 'America/Anchorage', 'America/Anguilla', 'America/Antigua', 'America/Araguaina', 'America/Argentina/Buenos_Aires', 'America/Argentina/Catamarca', 'America/Argentina/ComodRivadavia', 'America/Argentina/Cordoba', 'America/Argentina/Jujuy', 'America/Argentina/La_Rioja', 'America/Argentina/Mendoza', 'America/Argentina/Rio_Gallegos', 'America/Argentina/Salta', 'America/Argentina/San_Juan', 'America/Argentina/San_Luis', 'America/Argentina/Tucuman', 'America/Argentina/Ushuaia', 'America/Aruba', 'America/Asuncion', 'America/Atikokan', 'America/Atka', 'America/Bahia', 'America/Bahia_Banderas', 'America/Barbados', 'America/Belem', 'America/Belize', 'America/Blanc-Sablon', 'America/Boa_Vista', 'America/Bogota', 'America/Boise', 'America/Buenos_Aires', 'America/Cambridge_Bay', 'America/Campo_Grande', 'America/Cancun', 'America/Caracas', 'America/Catamarca', 'America/Cayenne', 'America/Cayman', 'America/Chicago', 'America/Chihuahua', 'America/Ciudad_Juarez', 'America/Coral_Harbour', 'America/Cordoba', 'America/Costa_Rica', 'America/Creston', 'America/Cuiaba', 'America/Curacao', 'America/Danmarkshavn', 'America/Dawson', 'America/Dawson_Creek', 'America/Denver', 'America/Detroit', 'America/Dominica', 'America/Edmonton', 'America/Eirunepe', 'America/El_Salvador', 'America/Ensenada', 'America/Fort_Nelson', 'America/Fort_Wayne', 'America/Fortaleza', 'America/Glace_Bay', 'America/Godthab', 'America/Goose_Bay', 'America/Grand_Turk', 'America/Grenada', 'America/Guadeloupe', 'America/Guatemala', 'America/Guayaquil', 'America/Guyana', 'America/Halifax', 'America/Havana', 'America/Hermosillo', 'America/Indiana/Indianapolis', 'America/Indiana/Knox', 'America/Indiana/Marengo', 'America/Indiana/Petersburg', 'America/Indiana/Tell_City', 'America/Indiana/Vevay', 'America/Indiana/Vincennes', 'America/Indiana/Winamac', 'America/Indianapolis', 'America/Inuvik', 'America/Iqaluit', 'America/Jamaica', 'America/Jujuy', 'America/Juneau', 'America/Kentucky/Louisville', 'America/Kentucky/Monticello', 'America/Knox_IN', 'America/Kralendijk', 'America/La_Paz', 'America/Lima', 'America/Los_Angeles', 'America/Louisville', 'America/Lower_Princes', 'America/Maceio', 'America/Managua', 'America/Manaus', 'America/Marigot', 'America/Martinique', 'America/Matamoros', 'America/Mazatlan', 'America/Mendoza', 'America/Menominee', 'America/Merida', 'America/Metlakatla', 'America/Mexico_City', 'America/Miquelon', 'America/Moncton', 'America/Monterrey', 'America/Montevideo', 'America/Montreal', 'America/Montserrat', 'America/Nassau', 'America/New_York', 'America/Nipigon', 'America/Nome', 'America/Noronha', 'America/North_Dakota/Beulah', 'America/North_Dakota/Center', 'America/North_Dakota/New_Salem', 'America/Nuuk', 'America/Ojinaga', 'America/Panama', 'America/Pangnirtung', 'America/Paramaribo', 'America/Phoenix', 'America/Port-au-Prince', 'America/Port_of_Spain', 'America/Porto_Acre', 'America/Porto_Velho', 'America/Puerto_Rico', 'America/Punta_Arenas', 'America/Rainy_River', 'America/Rankin_Inlet', 'America/Recife', 'America/Regina', 'America/Resolute', 'America/Rio_Branco', 'America/Rosario', 'America/Santa_Isabel', 'America/Santarem', 'America/Santiago', 'America/Santo_Domingo', 'America/Sao_Paulo', 'America/Scoresbysund', 'America/Shiprock', 'America/Sitka', 'America/St_Barthelemy', 'America/St_Johns', 'America/St_Kitts', 'America/St_Lucia', 'America/St_Thomas', 'America/St_Vincent', 'America/Swift_Current', 'America/Tegucigalpa', 'America/Thule', 'America/Thunder_Bay', 'America/Tijuana', 'America/Toronto', 'America/Tortola', 'America/Vancouver', 'America/Virgin', 'America/Whitehorse', 'America/Winnipeg', 'America/Yakutat', 'America/Yellowknife', 'Antarctica/Casey', 'Antarctica/Davis', 'Antarctica/DumontDUrville', 'Antarctica/Macquarie', 'Antarctica/Mawson', 'Antarctica/McMurdo', 'Antarctica/Palmer', 'Antarctica/Rothera', 'Antarctica/South_Pole', 'Antarctica/Syowa', 'Antarctica/Troll', 'Antarctica/Vostok', 'Arctic/Longyearbyen', 'Asia/Aden', 'Asia/Almaty', 'Asia/Amman', 'Asia/Anadyr', 'Asia/Aqtau', 'Asia/Aqtobe', 'Asia/Ashgabat', 'Asia/Ashkhabad', 'Asia/Atyrau', 'Asia/Baghdad', 'Asia/Bahrain', 'Asia/Baku', 'Asia/Bangkok', 'Asia/Barnaul', 'Asia/Beirut', 'Asia/Bishkek', 'Asia/Brunei', 'Asia/Calcutta', 'Asia/Chita', 'Asia/Choibalsan', 'Asia/Chongqing', 'Asia/Chungking', 'Asia/Colombo', 'Asia/Dacca', 'Asia/Damascus', 'Asia/Dhaka', 'Asia/Dili', 'Asia/Dubai', 'Asia/Dushanbe', 'Asia/Famagusta', 'Asia/Gaza', 'Asia/Harbin', 'Asia/Hebron', 'Asia/Ho_Chi_Minh', 'Asia/Hong_Kong', 'Asia/Hovd', 'Asia/Irkutsk', 'Asia/Istanbul', 'Asia/Jakarta', 'Asia/Jayapura', 'Asia/Jerusalem', 'Asia/Kabul', 'Asia/Kamchatka', 'Asia/Karachi', 'Asia/Kashgar', 'Asia/Kathmandu', 'Asia/Katmandu', 'Asia/Khandyga', 'Asia/Kolkata', 'Asia/Krasnoyarsk', 'Asia/Kuala_Lumpur', 'Asia/Kuching', 'Asia/Kuwait', 'Asia/Macao', 'Asia/Macau', 'Asia/Magadan', 'Asia/Makassar', 'Asia/Manila', 'Asia/Muscat', 'Asia/Nicosia', 'Asia/Novokuznetsk', 'Asia/Novosibirsk', 'Asia/Omsk', 'Asia/Oral', 'Asia/Phnom_Penh', 'Asia/Pontianak', 'Asia/Pyongyang', 'Asia/Qatar', 'Asia/Qostanay', 'Asia/Qyzylorda', 'Asia/Rangoon', 'Asia/Riyadh', 'Asia/Saigon', 'Asia/Sakhalin', 'Asia/Samarkand', 'Asia/Seoul', 'Asia/Shanghai', 'Asia/Singapore', 'Asia/Srednekolymsk', 'Asia/Taipei', 'Asia/Tashkent', 'Asia/Tbilisi', 'Asia/Tehran', 'Asia/Tel_Aviv', 'Asia/Thimbu', 'Asia/Thimphu', 'Asia/Tokyo', 'Asia/Tomsk', 'Asia/Ujung_Pandang', 'Asia/Ulaanbaatar', 'Asia/Ulan_Bator', 'Asia/Urumqi', 'Asia/Ust-Nera', 'Asia/Vientiane', 'Asia/Vladivostok', 'Asia/Yakutsk', 'Asia/Yangon', 'Asia/Yekaterinburg', 'Asia/Yerevan', 'Atlantic/Azores', 'Atlantic/Bermuda', 'Atlantic/Canary', 'Atlantic/Cape_Verde', 'Atlantic/Faeroe', 'Atlantic/Faroe', 'Atlantic/Jan_Mayen', 'Atlantic/Madeira', 'Atlantic/Reykjavik', 'Atlantic/South_Georgia', 'Atlantic/St_Helena', 'Atlantic/Stanley', 'Australia/ACT', 'Australia/Adelaide', 'Australia/Brisbane', 'Australia/Broken_Hill', 'Australia/Canberra', 'Australia/Currie', 'Australia/Darwin', 'Australia/Eucla', 'Australia/Hobart', 'Australia/LHI', 'Australia/Lindeman', 'Australia/Lord_Howe', 'Australia/Melbourne', 'Australia/NSW', 'Australia/North', 'Australia/Perth', 'Australia/Queensland', 'Australia/South', 'Australia/Sydney', 'Australia/Tasmania', 'Australia/Victoria', 'Australia/West', 'Australia/Yancowinna', 'Brazil/Acre', 'Brazil/DeNoronha', 'Brazil/East', 'Brazil/West', 'CET', 'CST6CDT', 'Canada/Atlantic', 'Canada/Central', 'Canada/Eastern', 'Canada/Mountain', 'Canada/Newfoundland', 'Canada/Pacific', 'Canada/Saskatchewan', 'Canada/Yukon', 'Chile/Continental', 'Chile/EasterIsland', 'Cuba', 'EET', 'EST', 'EST5EDT', 'Egypt', 'Eire', 'Etc/GMT', 'Etc/GMT+0', 'Etc/GMT+1', 'Etc/GMT+10', 'Etc/GMT+11', 'Etc/GMT+12', 'Etc/GMT+2', 'Etc/GMT+3', 'Etc/GMT+4', 'Etc/GMT+5', 'Etc/GMT+6', 'Etc/GMT+7', 'Etc/GMT+8', 'Etc/GMT+9', 'Etc/GMT-0', 'Etc/GMT-1', 'Etc/GMT-10', 'Etc/GMT-11', 'Etc/GMT-12', 'Etc/GMT-13', 'Etc/GMT-14', 'Etc/GMT-2', 'Etc/GMT-3', 'Etc/GMT-4', 'Etc/GMT-5', 'Etc/GMT-6', 'Etc/GMT-7', 'Etc/GMT-8', 'Etc/GMT-9', 'Etc/GMT0', 'Etc/Greenwich', 'Etc/UCT', 'Etc/UTC', 'Etc/Universal', 'Etc/Zulu', 'Europe/Amsterdam', 'Europe/Andorra', 'Europe/Astrakhan', 'Europe/Athens', 'Europe/Belfast', 'Europe/Belgrade', 'Europe/Berlin', 'Europe/Bratislava', 'Europe/Brussels', 'Europe/Bucharest', 'Europe/Budapest', 'Europe/Busingen', 'Europe/Chisinau', 'Europe/Copenhagen', 'Europe/Dublin', 'Europe/Gibraltar', 'Europe/Guernsey', 'Europe/Helsinki', 'Europe/Isle_of_Man', 'Europe/Istanbul', 'Europe/Jersey', 'Europe/Kaliningrad', 'Europe/Kiev', 'Europe/Kirov', 'Europe/Kyiv', 'Europe/Lisbon', 'Europe/Ljubljana', 'Europe/London', 'Europe/Luxembourg', 'Europe/Madrid', 'Europe/Malta', 'Europe/Mariehamn', 'Europe/Minsk', 'Europe/Monaco', 'Europe/Moscow', 'Europe/Nicosia', 'Europe/Oslo', 'Europe/Paris', 'Europe/Podgorica', 'Europe/Prague', 'Europe/Riga', 'Europe/Rome', 'Europe/Samara', 'Europe/San_Marino', 'Europe/Sarajevo', 'Europe/Saratov', 'Europe/Simferopol', 'Europe/Skopje', 'Europe/Sofia', 'Europe/Stockholm', 'Europe/Tallinn', 'Europe/Tirane', 'Europe/Tiraspol', 'Europe/Ulyanovsk', 'Europe/Uzhgorod', 'Europe/Vaduz', 'Europe/Vatican', 'Europe/Vienna', 'Europe/Vilnius', 'Europe/Volgograd', 'Europe/Warsaw', 'Europe/Zagreb', 'Europe/Zaporozhye', 'Europe/Zurich', 'GB', 'GB-Eire', 'GMT', 'GMT+0', 'GMT-0', 'GMT0', 'Greenwich', 'HST', 'Hongkong', 'Iceland', 'Indian/Antananarivo', 'Indian/Chagos', 'Indian/Christmas', 'Indian/Cocos', 'Indian/Comoro', 'Indian/Kerguelen', 'Indian/Mahe', 'Indian/Maldives', 'Indian/Mauritius', 'Indian/Mayotte', 'Indian/Reunion', 'Iran', 'Israel', 'Jamaica', 'Japan', 'Kwajalein', 'Libya', 'MET', 'MST', 'MST7MDT', 'Mexico/BajaNorte', 'Mexico/BajaSur', 'Mexico/General', 'NZ', 'NZ-CHAT', 'Navajo', 'PRC', 'PST8PDT', 'Pacific/Apia', 'Pacific/Auckland', 'Pacific/Bougainville', 'Pacific/Chatham', 'Pacific/Chuuk', 'Pacific/Easter', 'Pacific/Efate', 'Pacific/Enderbury', 'Pacific/Fakaofo', 'Pacific/Fiji', 'Pacific/Funafuti', 'Pacific/Galapagos', 'Pacific/Gambier', 'Pacific/Guadalcanal', 'Pacific/Guam', 'Pacific/Honolulu', 'Pacific/Johnston', 'Pacific/Kanton', 'Pacific/Kiritimati', 'Pacific/Kosrae', 'Pacific/Kwajalein', 'Pacific/Majuro', 'Pacific/Marquesas', 'Pacific/Midway', 'Pacific/Nauru', 'Pacific/Niue', 'Pacific/Norfolk', 'Pacific/Noumea', 'Pacific/Pago_Pago', 'Pacific/Palau', 'Pacific/Pitcairn', 'Pacific/Pohnpei', 'Pacific/Ponape', 'Pacific/Port_Moresby', 'Pacific/Rarotonga', 'Pacific/Saipan', 'Pacific/Samoa', 'Pacific/Tahiti', 'Pacific/Tarawa', 'Pacific/Tongatapu', 'Pacific/Truk', 'Pacific/Wake', 'Pacific/Wallis', 'Pacific/Yap', 'Poland', 'Portugal', 'ROC', 'ROK', 'Singapore', 'Turkey', 'UCT', 'US/Alaska', 'US/Aleutian', 'US/Arizona', 'US/Central', 'US/East-Indiana', 'US/Eastern', 'US/Hawaii', 'US/Indiana-Starke', 'US/Michigan', 'US/Mountain', 'US/Pacific', 'US/Samoa', 'UTC', 'Universal', 'W-SU', 'WET', 'Zulu']
casedata = {'Case Number': tk.StringVar(), 
            'Agency': tk.StringVar(), 
            'Examiner': tk.StringVar(), 
            }
timezone_set = tk.StringVar()
pickModules()

## Places main window in the center
screen_width = main_window.winfo_screenwidth()
screen_height = main_window.winfo_screenheight()
margin_width = (screen_width - window_width) // 2
margin_height = (screen_height - window_height) // 2

## Theme properties
theme_bgcolor = '#2c2825'
theme_inputcolor = '#705e52'
theme_fgcolor = '#fdcb52'

if is_platform_macos():
    font_size = 10
    casedata_entry_width = 80
    mlist_window_width = 50
    mlist_window_height = 23
    mlist_padding = 2
    log_window_height = 28
elif is_platform_linux():
    font_size = 8
    casedata_entry_width = 100
    mlist_window_width = 44
    mlist_window_height = 18
    mlist_padding = 4
    log_window_height = 29
else:
    font_size = 8
    casedata_entry_width = 100
    mlist_window_width = 44
    mlist_window_height = 18
    mlist_padding = 2
    log_window_height = 21

theme_font = ('Helvetica', font_size)

## Main window properties
main_window.geometry(f'{window_width}x{window_height}+{margin_width}+{margin_height}')
main_window.title(f'iLEAPP version {ileapp_version}')
main_window.resizable(False, False)
main_window.configure(bg=theme_bgcolor)
logo_icon = tk.PhotoImage(data=leapp_logo.logo)
main_window.iconphoto(True, logo_icon)

## Widgets default style
style = ttk.Style()
style.theme_use('default')
style.configure('.', 
                background=theme_bgcolor, 
                foreground=theme_fgcolor, 
                font=theme_font)
style.configure('Small.TLabel', font=('Helvetica', f'{int(1.2 * font_size)}'))
style.configure('Medium.TLabel', font=('Helvetica', f'{int(1.4 * font_size)}'))
style.configure('TButton')
style.map('TButton', 
          background=[('active', 'black'), ('!disabled', theme_fgcolor)], 
          foreground=[('active', theme_fgcolor), ('!disabled', 'black')])
style.map('Error.TButton', 
          background=[('active', 'white'), ('!disabled', 'red')], 
          foreground=[('active', 'red'), ('!disabled', 'white')])
style.configure('TEntry', fieldbackground=theme_inputcolor, highlightthickness=0)
style.configure('TCombobox', selectforeground=theme_fgcolor, selectbackground=theme_inputcolor, arrowcolor=theme_fgcolor)
style.map('TCombobox', 
          fieldbackground=[('active', theme_inputcolor), ('readonly', theme_inputcolor)], 
          )
style.configure('TScrollbar', background=theme_fgcolor, arrowcolor='black', troughcolor=theme_inputcolor)
style.configure('TProgressbar', thickness=4, background='DarkGreen')

## Main Window Layout
### Top part of the window
title_frame = ttk.Frame(main_window)
title_frame.pack(padx=14, pady=6, anchor='w')
title_label = ttk.Label(title_frame, text='iOS Logs, Events, And Plists Parser', font=('Helvetica', f'{int(2.2 * font_size)}'))
title_label.pack(pady=4)
github_label = ttk.Label(title_frame, text='https://github.com/abrignoni/iLEAPP', style='Medium.TLabel')
github_label.pack(anchor='w')

### Input output selection
input_frame = ttk.LabelFrame(main_window, text=' Select the file (tar/zip/gz) or directory of the target iOS full file system extraction for parsing: ')
input_frame.pack(anchor='w', padx=14, pady=2)
input_entry = ttk.Entry(input_frame ,width=112, font=theme_font)
input_entry.pack(side='left', padx=5, pady=4)
input_file_button = ttk.Button(input_frame, text='Browse File', command=lambda: select_input('file'))
input_file_button.pack(side='left', padx=5, pady=4)
input_folder_button = ttk.Button(input_frame, text='Browse Folder', command=lambda: select_input('folder'))
input_folder_button.pack(side='left', padx=5, pady=4)

output_frame = ttk.LabelFrame(main_window, text=' Select Output Folder: ')
output_frame.pack(anchor='w', padx=14, pady=5)
output_entry = ttk.Entry(output_frame, width=126, font=theme_font)
output_entry.grid(row=0, column=0, padx=5, pady=4)
output_folder_button = ttk.Button(output_frame, text='Browse Folder', command=select_output)
output_folder_button.grid(row=0, column=1, padx=5, pady=4)

### Modules and logs
modules_frame = ttk.Frame(main_window, name='f_modules')
modules_frame.pack(padx=14, pady=1, anchor='w')

modules_btn_frame = ttk.Frame(modules_frame, name='')
modules_btn_frame.pack(anchor='w')
ttk.Label(modules_btn_frame, text='Available Modules: ').pack(anchor='w', pady=4)

####Buttons
all_button = ttk.Button(modules_btn_frame, text='Select All', command=select_all)
all_button.pack(side='left', padx=8, pady=4)
none_button = ttk.Button(modules_btn_frame, text='Deselect All', command=deselect_all)
none_button.pack(side='left', padx=8)
load_button = ttk.Button(modules_btn_frame, text='Load Profile', command=load_profile)
load_button.pack(side='left', padx=8)
save_button = ttk.Button(modules_btn_frame, text='Save Profile', command=save_profile)
save_button.pack(side='left', padx=8)
ttk.Label(modules_btn_frame, text='          ', style='Medium.TLabel').pack(side='left', padx=5)
case_data_button = ttk.Button(modules_btn_frame, text='Case Data', command=case_data)
case_data_button.pack(side='left', padx=5)
ttk.Label(modules_btn_frame, text=' | ', style='Medium.TLabel').pack(side='left', padx=5)
ttk.Label(modules_btn_frame, text='Timezone Offset: ', style='Small.TLabel').pack(side='left', padx=5)
timezone_offset = ttk.Combobox(modules_btn_frame, textvariable=timezone_set, values=tzvalues, width=20, height=20, font=theme_font, state='readonly')
timezone_offset.master.option_add( '*TCombobox*Listbox.background', theme_inputcolor)
timezone_offset.master.option_add( '*TCombobox*Listbox.foreground', theme_fgcolor)
timezone_offset.master.option_add( '*TCombobox*Listbox.selectBackground', theme_fgcolor)
timezone_offset.master.option_add( '*TCombobox*Listbox.font', theme_font)
timezone_offset.pack(side='left')

#### Modules list
mlist_frame = ttk.Frame(modules_frame, name='f_list')
mlist_frame.pack(anchor='w', side='left', padx=7)
x = ttk.Scrollbar(mlist_frame, orient='horizontal')
x.pack(side='bottom', fill='x')
v = ttk.Scrollbar(mlist_frame, orient='vertical')
v.pack(side='right', fill='y')
mlist_text = tk.Text(mlist_frame, name='tbox', width=mlist_window_width, height=mlist_window_height, 
                     bg=theme_bgcolor, highlightthickness=0, 
                     xscrollcommand=x.set, yscrollcommand=v.set)
mlist_text.pack(anchor='w')
v.config(command=mlist_text.yview)
x.config(command=mlist_text.xview)
for plugin, enabled in mlist.items():
    cb = tk.Checkbutton(mlist_text, name=f'mcb_{plugin.module_name}', 
                        text=f'{plugin.category} [{plugin.name} - {plugin.module_name}.py]', 
                        variable=enabled, onvalue=True, offvalue=False, command=get_selected_modules)
    cb.config(background=theme_bgcolor, fg=theme_fgcolor, font=theme_font, selectcolor=theme_inputcolor, 
              highlightthickness=0, activebackground=theme_bgcolor, activeforeground=theme_fgcolor, 
              pady=mlist_padding)
    mlist_text.window_create('insert', window=cb)
    mlist_text.insert('end', '\n')
main_window.bind_class('Checkbutton', '<MouseWheel>', scroll)
main_window.bind_class('Checkbutton', '<Button-4>', scroll)
main_window.bind_class('Checkbutton', '<Button-5>', scroll)

#### Logs
logtext_frame = ttk.Frame(modules_frame, name='logs_frame')
logtext_frame.pack(anchor='w', side='left', padx=1, pady=5)
vlog = ttk.Scrollbar(logtext_frame, orient='vertical')
vlog.pack(side='right', fill='y')
log_text = tk.Text(logtext_frame, name='log_text', height=log_window_height, 
                   bg=theme_inputcolor, font=theme_font, fg=theme_fgcolor, highlightthickness=1, 
                   yscrollcommand=vlog.set)
log_text.pack(anchor='w', side='left')
vlog.config(command=log_text.yview)

### Progress bar
progress_bar = ttk.Progressbar(main_window, orient='horizontal', length = 860)
progress_bar.pack(pady=2)

### Process / Close
bottom_frame = ttk.Frame(main_window)
bottom_frame.pack(padx=16, pady=5, anchor='w')
process_button = ttk.Button(bottom_frame, text='Process', command=lambda: process(casedata))
process_button.pack(side='left', padx=5)
close_button = ttk.Button(bottom_frame, text='Close', command=main_window.quit)
close_button.pack(side='left', padx=5)
selected_modules_label = ttk.Label(bottom_frame, text='Number of selected modules: ', style='Small.TLabel', padding= (30,4))
selected_modules_label.pack()
get_selected_modules()

main_window.mainloop()