#!/usr/bin/env python3

import tkinter as tk
import typing
import json
import ileapp
import webbrowser
import base64

import scripts.plugin_loader as plugin_loader
import leapp_functions.app.history as history

from PIL import Image, ImageTk
from tkinter import ttk, filedialog as tk_filedialog, messagebox as tk_msgbox
from scripts.version_info import leapp_name, leapp_version
from scripts.search_files import *
from scripts.ilapfuncs import *
from scripts.tz_offset import tzvalues
from scripts.modules_to_exclude import modules_to_exclude
from scripts.lavafuncs import *
from leapp_functions.lava_launcher import (
    LAVA_WEBSITE,
    find_lava_launcher,
    open_lava_project,
    open_output_folder,
)
from leapp_functions.app.platform import sanitize_file_name
from leapp_functions.app.output import default_output_folder_name, validate_output_folder_available
from scripts.context import Context
from scripts.lavafuncs import lava_json_name


def allow_output_folder_name_chars(proposed):
    return sanitize_file_name(proposed) == proposed


def show_history_menu(button, path_type):
    """
    Displays a popup menu with recently used paths.
    """
    menu = tk.Menu(main_window, tearoff=0)

    if not history.is_history_enabled():
        menu.add_command(label="(History Disabled - Enable in Settings)", state="disabled")
    else:
        paths = history.get_input_paths() if path_type == 'input' else history.get_output_paths()
        if not paths:
            menu.add_command(label="(No recent paths)", state="disabled")
        for path in paths:
            def set_path(p=path):
                if path_type == 'input':
                    input_entry.delete(0, tk.END)
                    input_entry.insert(0, p)
                else:
                    output_entry.delete(0, tk.END)
                    output_entry.insert(0, p)
            menu.add_command(label=history.format_path_for_display(path), command=set_path)
    x = input_entry.winfo_rootx()
    y = button.winfo_rooty() + button.winfo_height()
    menu.post(x, y)


def pickModules():
    '''Create a list of available modules:
        - itunes_backup_info, itunes_backup_installed_applications, last_build and Ph100-UFED-device-values-Plist that need
        to be executed first are excluded
        - logarchive_artifacts is also excluded as it uses the LAVA SQLite database to extract
        relevant event messages from the logarchive table and must be executed only if logarchive
        module has been already executed
        - ones that take a long time to run are deselected by default'''
    global mlist
    for plugin in sorted(loader.plugins, key=lambda p: p.category.upper()):
        if (plugin.module_name == 'iTunesBackupInfo'
                or plugin.name == 'last_build'
                or plugin.module_name == 'logarchive' and plugin.name != 'logarchive'):
            continue
        # Items that take a long time to execute are deselected by default
        # and referenced in the modules_to_exclude list in an external file (modules_to_exclude.py).
        plugin_enabled = tk.BooleanVar(value=False) if plugin.module_name in modules_to_exclude else tk.BooleanVar(value=True)
        plugin_module_name = plugin.artifact_info.get('name', plugin.name) if hasattr(plugin, 'artifact_info') else plugin.name
        mlist[plugin.name] = [plugin.category, plugin_module_name, plugin.module_name, plugin_enabled]


def get_selected_modules():
    '''Update the number and return the list of selected modules'''
    selected_modules = []

    for artifact_name, module_infos in mlist.items():
        if module_infos[-1].get():
            selected_modules.append(artifact_name)

    selected_modules_label.config(text=f'Number of selected modules: {len(selected_modules)} / {len(mlist)}')
    return selected_modules


def select_all():
    '''Select all modules in the list of available modules and execute get_selected_modules'''
    for module_infos in mlist.values():
        module_infos[-1].set(True)

    get_selected_modules()


def deselect_all():
    '''Unselect all modules in the list of available modules and execute get_selected_modules'''
    for module_infos in mlist.values():
        module_infos[-1].set(False)

    get_selected_modules()


def filter_modules(*args):
    mlist_text.config(state='normal')
    filter_term = modules_filter_var.get().lower()

    mlist_text.delete('0.0', tk.END)

    for artifact_name, module_infos in mlist.items():
        filter_modules_info = f"{module_infos[0]} {module_infos[1]}".lower()
        if filter_term in filter_modules_info:
            cb = tk.Checkbutton(mlist_text, name=f'mcb_{artifact_name}',
                                text=f'{module_infos[0]} [{module_infos[1]} | {module_infos[2]}.py]',
                                variable=module_infos[-1], onvalue=True, offvalue=False, command=get_selected_modules)
            cb.config(background=theme_bgcolor, fg=theme_fgcolor, selectcolor=theme_inputcolor,
                    highlightthickness=0, activebackground=theme_bgcolor, activeforeground=theme_fgcolor)
            mlist_text.window_create('insert', window=cb)
            mlist_text.insert('end', '\n')
    mlist_text.config(state='disabled')

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
                    for artifact_name, module_infos in mlist.items():
                        if artifact_name in ticked:
                            module_infos[-1].set(True)
                    get_selected_modules()
            else:
                profile_load_error = 'File was not a valid profile file: invalid format'
        if profile_load_error:
            tk_msgbox.showerror(title='Error', message=profile_load_error, parent=main_window)
        else:
            profile_filename = destination_path
            tk_msgbox.showinfo(
                title='Profile loaded', message=f'Loaded profile: {destination_path}', parent=main_window)


def save_profile():
    '''Save selected modules in a profile file'''
    destination_path = tk_filedialog.asksaveasfilename(parent=main_window,
                                                       title='Save a profile',
                                                       filetypes=(('iLEAPP Profile', '*.ilprofile'),),
                                                       defaultextension='.ilprofile')

    if destination_path:
        selected_modules = get_selected_modules()
        with open(destination_path, 'wt', encoding='utf-8') as profile_out:
            json.dump({'leapp': 'ileapp', 'format_version': 1, 'plugins': selected_modules}, profile_out)
        tk_msgbox.showinfo(
            title='Save a profile', message=f'Profile saved: {destination_path}', parent=main_window)


def scroll(event):
    '''Continue to scroll the list with mouse wheel when cursor hover a checkbutton'''
    parent = main_window.nametowidget(event.widget.winfo_parent())
    parent.event_generate('<MouseWheel>', delta=event.delta, when='now')


def ValidateInput():
    '''Returns tuple (success, extraction_type)'''
    i_path = input_entry.get()  # input file/folder
    o_path = output_entry.get()  # output folder
    ext_type = ''

    # check input
    if len(i_path) == 0:
        tk_msgbox.showerror(title='Error', message='No INPUT file or folder selected!', parent=main_window)
        return False, ext_type, None
    elif not os.path.exists(i_path):
        tk_msgbox.showerror(title='Error', message='INPUT file/folder does not exist!', parent=main_window)
        return False, ext_type, None
    elif os.path.isdir(i_path):
        itunes_backup_type = get_itunes_backup_type(i_path)
        if itunes_backup_type:
            supported, encrypted, message = check_itunes_backup_status(
                i_path, itunes_backup_type)
            if not supported:
                tk_msgbox.showerror(title='Error', message=message,
                                    parent=main_window)
                return False, ext_type, None
            else:
                if encrypted:
                    decryption_keys = None
                    while not decryption_keys:
                        password = tk.simpledialog.askstring(
                            "Detected encrypted iTunes backup",
                            "iTunes Backup password:",
                            show='*',
                            parent=main_window)
                        decryption_keys, message = decrypt_itunes_backup(i_path, password)
                        if not decryption_keys:
                            tk_msgbox.showerror(title='Error', message=message,
                                                parent=main_window)
                            return False, ext_type, decryption_keys
                        else:
                            return True, 'itunes', decryption_keys
            ext_type = 'itunes'
        else:
            ext_type = 'fs'
    else:
        ext_type = Path(i_path).suffix[1:].lower()

    # check output now
    if len(o_path) == 0:  # output path
        tk_msgbox.showerror(title='Error', message='No output path provided!', parent=main_window)
        return False, ext_type, None

    folder_name = output_folder_name_entry.get().strip()
    if not folder_name:
        tk_msgbox.showerror(title='Error', message='Output folder name cannot be empty!', parent=main_window)
        return False, ext_type, None
    folder_name_valid, folder_name_error = validate_output_folder_available(o_path, folder_name)
    if not folder_name_valid:
        tk_msgbox.showerror(title='Error', message=folder_name_error, parent=main_window)
        return False, ext_type, None

    # check if at least one module is selected
    if len(get_selected_modules()) == 0:
        tk_msgbox.showerror(title='Error', message='No module selected for processing!', parent=main_window)
        return False, ext_type, None

    return True, ext_type, None


def open_report(report_path):
    '''Open report and Quit after processing completed'''
    webbrowser.open_new_tab('file://' + report_path)
    main_window.quit()


def open_lava(project_path, launcher):
    '''Open the generated project in LAVA and quit after processing completed.'''
    try:
        open_lava_project(project_path, launcher, logfunc)
    except (OSError, ValueError) as ex:
        tk_msgbox.showerror(
            title='Unable to open LAVA',
            message=f'iLEAPP could not open the project in LAVA:\n{ex}',
            parent=main_window)
        return
    main_window.quit()


def explore_lava():
    '''Open the LAVA website.'''
    webbrowser.open_new_tab(LAVA_WEBSITE)


def open_folder(output_path):
    '''Open the generated output folder.'''
    try:
        open_output_folder(output_path)
    except OSError as ex:
        tk_msgbox.showerror(
            title='Unable to open output folder',
            message=f'iLEAPP could not open the output folder:\n{ex}',
            parent=main_window)


def open_website(url):
    webbrowser.open_new_tab(url)


def open_settings_window():
    '''Open Settings modal window'''
    settings_window = tk.Toplevel(main_window)
    settings_window.transient(main_window)
    settings_window_width = 400
    settings_window_height = 260

    #### Places Case Data window in the center of the main window
    main_window.update_idletasks()
    main_x = main_window.winfo_x()
    main_y = main_window.winfo_y()
    main_w = main_window.winfo_width()
    main_h = main_window.winfo_height()

    margin_width = main_x + (main_w - settings_window_width) // 2
    margin_height = main_y + (main_h - settings_window_height) // 2

    settings_window.geometry(f'{settings_window_width}x{settings_window_height}+{margin_width}+{margin_height}')
    settings_window.resizable(False, False)
    settings_window.configure(bg=theme_bgcolor)
    settings_window.title('Settings')
    settings_window.grid_columnconfigure(0, weight=1)

    def on_main_focus(event):
        if settings_window.winfo_exists():
            settings_window.bell()
            settings_window.lift()
            settings_window.focus_force()

    main_window.bind("<FocusIn>", on_main_focus)

    def close_settings_window():
        main_window.unbind("<FocusIn>")
        settings_window.destroy()

    settings_window.protocol("WM_DELETE_WINDOW", close_settings_window)

    settings_title_label = ttk.Label(settings_window, text='Settings', font='Helvetica 18')
    settings_title_label.grid(row=0, column=0, padx=14, pady=7, sticky='w')

    history_enabled_var = tk.BooleanVar(value=history.is_history_enabled())

    def toggle_history():
        history.set_history_enabled(history_enabled_var.get())

    def update_clear_history_button():
        state = tk.NORMAL if history.has_history() else tk.DISABLED
        clear_history_btn.config(state=state)

    def open_clear_history_window():
        clear_window = tk.Toplevel(settings_window)
        clear_window.transient(settings_window)
        clear_window_width = 460
        clear_window_height = 220

        settings_window.update_idletasks()
        settings_x = settings_window.winfo_x()
        settings_y = settings_window.winfo_y()
        settings_w = settings_window.winfo_width()
        settings_h = settings_window.winfo_height()

        margin_width = settings_x + (settings_w - clear_window_width) // 2
        margin_height = settings_y + (settings_h - clear_window_height) // 2

        clear_window.geometry(f'{clear_window_width}x{clear_window_height}+{margin_width}+{margin_height}')
        clear_window.resizable(False, False)
        clear_window.configure(bg=theme_bgcolor)
        clear_window.title('Clear History')
        clear_window.grid_columnconfigure(0, weight=1)

        def on_settings_focus(event):
            if clear_window.winfo_exists():
                clear_window.bell()
                clear_window.lift()
                clear_window.focus_force()

        settings_window.bind("<FocusIn>", on_settings_focus)

        def close_clear_window():
            settings_window.unbind("<FocusIn>")
            clear_window.destroy()

        clear_window.protocol("WM_DELETE_WINDOW", close_clear_window)

        clear_title_label = ttk.Label(clear_window, text='Clear History', font='Helvetica 18')
        clear_title_label.grid(row=0, column=0, padx=14, pady=7, sticky='w')

        clear_message = (
            'History is stored in shared LEAPP files. Input and output paths are shared by all '
            'LEAPP tools, while recent runs are tagged by tool.'
        )
        clear_message_label = ttk.Label(clear_window, text=clear_message, wraplength=420)
        clear_message_label.grid(row=1, column=0, padx=14, pady=10, sticky='w')

        button_frame = ttk.Frame(clear_window)
        button_frame.grid(row=2, column=0, padx=14, pady=18, sticky='e')

        def clear_single_leapp_history():
            if not tk_msgbox.askyesno(
                    title=f'Clear {leapp_name} history',
                    message=(
                        f'Clear shared recent input/output paths and '
                        f'{leapp_name} recent run entries?'
                    ),
                    parent=clear_window):
                return
            history.clear_single_leapp_history(leapp_name.lower())
            update_clear_history_button()
            close_clear_window()

        def clear_all_history():
            if not tk_msgbox.askyesno(
                    title='Clear all LEAPP history',
                    message='Clear all shared LEAPP history, including recent input and output paths?',
                    parent=clear_window):
                return
            history.clear_history()
            update_clear_history_button()
            close_clear_window()

        clear_single_leapp_btn = ttk.Button(
            button_frame,
            text=f'Clear {leapp_name} History',
            command=clear_single_leapp_history)
        clear_single_leapp_btn.pack(side='left', padx=5)
        if not history.has_single_leapp_history(leapp_name.lower()):
            clear_single_leapp_btn.config(state=tk.DISABLED)

        clear_all_btn = ttk.Button(
            button_frame,
            text='Clear All History',
            command=clear_all_history)
        clear_all_btn.pack(side='left', padx=5)

        cancel_btn = ttk.Button(button_frame, text='Cancel', command=close_clear_window)
        cancel_btn.pack(side='left', padx=5)

        if is_platform_macos():
            clear_window.grab_set_global()
        else:
            clear_window.grab_set()

    history_check = tk.Checkbutton(
        settings_window,
        text='Enable saving paths as recent history',
        variable=history_enabled_var,
        command=toggle_history,
        background=theme_bgcolor,
        fg=theme_fgcolor,
        selectcolor=theme_inputcolor,
        activebackground=theme_bgcolor,
        activeforeground=theme_fgcolor,
        highlightthickness=0,
    )
    history_check.grid(row=1, column=0, padx=14, pady=20, sticky='w')

    clear_history_btn = ttk.Button(
        settings_window,
        text='Clear History',
        command=open_clear_history_window)
    clear_history_btn.grid(row=2, column=0, padx=14, pady=10, sticky='w')
    update_clear_history_button()

    close_btn = ttk.Button(settings_window, text='Close', command=close_settings_window)
    close_btn.grid(row=3, column=0, padx=14, pady=20, sticky='e')

    if is_platform_macos():
        settings_window.grab_set_global()
    else:
        settings_window.grab_set()


def resource_path(filename):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, 'assets', filename)


def process(casedata):
    '''Execute selected modules and create reports'''
    # check if selections made properly; if not we will return to input form without exiting app altogether
    is_valid, extracttype, decryption_keys = ValidateInput()

    if is_valid:
        GuiWindow.window_handle = main_window
        input_path = input_entry.get()
        output_folder = output_entry.get()

        # ios file system extractions contain paths > 260 char, which causes problems
        # This fixes the problem by prefixing \\?\ on each windows path.
        if is_platform_windows():
            if input_path[1] == ':' and extracttype == 'fs': input_path = '\\\\?\\' + input_path.replace('/', '\\')
            if output_folder[1] == ':': output_folder = '\\\\?\\' + output_folder.replace('/', '\\')

        # re-create modules list based on user selection
        selected_modules = get_selected_modules()
        selected_modules = [loader[module] for module in selected_modules]
        progress_bar.config(maximum=len(selected_modules))
        casedata = {key: value.get() for key, value in casedata.items()}
        out_params = OutputParameters(output_folder, output_folder_name_entry.get().strip())
        Context.set_output_params(out_params)
        wrap_text = True
        time_offset = timezone_set.get()
        if time_offset == '':
            time_offset = 'UTC'

        bottom_frame.pack_forget()
        mlist_frame.pack_forget()
        output_frame.pack_forget()
        input_frame.pack_forget()
        logtext_frame.pack(padx=8, pady=4, expand=True, fill='both')
        progress_bar_frame.pack(padx=2, pady=2, ipady=2, fill='x')

        initialize_lava(input_path, out_params.output_folder_base, extracttype)

        # Record history if enabled
        history.record_input_path(input_path)
        history.record_output_path(output_folder)

        crunch_successful = ileapp.crunch_artifacts(
            selected_modules, extracttype, input_path, out_params, wrap_text,
            loader, casedata, time_offset, profile_filename, None, decryption_keys)

        lava_finalize_output(out_params.output_folder_base)

        if crunch_successful:
            # Record the run in history
            report_path = os.path.join(out_params.output_folder_base, 'index.html')
            lava_project_path = os.path.join(out_params.output_folder_base, lava_json_name)
            history.record_recent_run(leapp_name.lower(), leapp_version, lava_project_path)

            output_folder_path = out_params.output_folder_base
            if report_path.startswith('\\\\?\\'):  # windows
                report_path = report_path[4:]
                lava_project_path = lava_project_path[4:]
                output_folder_path = output_folder_path[4:]
            if report_path.startswith('\\\\'):  # UNC path
                report_path = report_path[2:]
                lava_project_path = lava_project_path[2:]
                output_folder_path = output_folder_path[2:]
            if lava_only_artifacts:
                message = "You have selected artifacts that are likely to return too much data "
                message += "to be viewed in a Web browser.\n\n"
                message += "Please see the 'LAVA only artifacts' tab in the HTML report for a list of these artifacts "
                message += "and instructions on how to view them."
                tk_msgbox.showwarning(
                    title="Important information",
                    message=message,
                    parent=main_window)
            progress_bar.pack_forget()
            completion_button_frame = ttk.Frame(progress_bar_frame)
            completion_button_frame.place(relx=0.5, rely=0.5, anchor='center')
            open_report_button = ttk.Button(
                completion_button_frame,
                text='Open HTML in Browser & Close',
                command=lambda: open_report(report_path))
            open_report_button.pack(side='left', padx=5)

            lava_launcher = find_lava_launcher(lava_project_path)
            if lava_launcher:
                lava_button = ttk.Button(
                    completion_button_frame,
                    text='Open Project in LAVA & Close',
                    command=lambda: open_lava(lava_project_path, lava_launcher))
            else:
                lava_button = ttk.Button(
                    completion_button_frame,
                    text='Explore LAVA',
                    command=explore_lava)
            lava_button.pack(side='left', padx=5)

            open_folder_button = ttk.Button(
                completion_button_frame,
                text='Open Output Folder',
                command=lambda: open_folder(output_folder_path))
            open_folder_button.pack(side='left', padx=5)
        else:
            log_path = out_params.screen_output_file_path
            if log_path.startswith('\\\\?\\'):  # windows
                log_path = log_path[4:]
            tk_msgbox.showerror(
                title='Error',
                message=f'Processing failed  :( \nSee log for error details..\nLog file located at {log_path}',
                parent=main_window)


def select_input(button_type):
    '''Select source and insert its path into input field'''
    if button_type == 'file':
        input_filename = tk_filedialog.askopenfilename(parent=main_window,
                                                       title='Select a file',
                                                       filetypes=(('All supported files', '*.tar *.zip *.gz'),
                                                                  ('tar file', '*.tar'), ('zip file', '*.zip'),
                                                                  ('gz file', '*.gz')))
    else:
        input_filename = tk_filedialog.askdirectory(parent=main_window, title='Select a folder')
    input_entry.delete(0, 'end')
    input_entry.insert(0, input_filename)
    if input_filename:
        history.record_input_path(input_filename)


def select_output():
    '''Select target and insert its path into output field'''
    output_filename = tk_filedialog.askdirectory(parent=main_window, title='Select a folder')
    output_entry.delete(0, 'end')
    output_entry.insert(0, output_filename)
    if output_filename:
        history.record_output_path(output_filename)


def case_data():
    # GUI layout
    ## Case Data
    '''Add Case Data window'''
    global casedata

    def clear():
        '''Remove the contents of all fields'''
        case_number_entry.delete(0, 'end')
        case_agency_name_entry.delete(0, 'end')
        case_agency_logo_path_entry.delete(0, 'end')
        case_agency_logo_mimetype.delete(0, 'end')
        case_agency_logo_b64.delete(0, 'end')
        case_examiner_entry.delete(0, 'end')

    def save_case():
        '''Save case data in a Case Data file'''
        destination_path = tk_filedialog.asksaveasfilename(parent=case_window,
                                                           title='Save a case data file',
                                                           filetypes=(('LEAPP Case Data', '*.lcasedata'),),
                                                           defaultextension='.lcasedata')

        if destination_path:
            json_casedata = {key: value.get() for key, value in casedata.items()}
            with open(destination_path, 'wt', encoding='utf-8') as case_data_out:
                json.dump({'leapp': 'case_data', 'case_data_values': json_casedata}, case_data_out)
            tk_msgbox.showinfo(
                title='Save Case Data', message=f'Case Data saved: {destination_path}', parent=case_window)

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
                        case_agency_name_entry.delete(0, 'end')
                        case_agency_name_entry.insert(0, casedata.get('Agency', ''))
                        case_agency_logo_path_entry.delete(0, 'end')
                        case_agency_logo_path_entry.insert(0, casedata.get('Agency Logo Path', ''))
                        case_agency_logo_mimetype.delete(0, 'end')
                        case_agency_logo_mimetype.insert(0, casedata.get('Agency Logo mimetype', ''))
                        case_agency_logo_b64.delete(0, 'end')
                        case_agency_logo_b64.insert(0, casedata.get('Agency Logo base64', ''))
                        case_examiner_entry.delete(0, 'end')
                        case_examiner_entry.insert(0, casedata.get('Examiner', ''))
                else:
                    case_data_load_error = 'File was not a valid case data file: invalid format'
            if case_data_load_error:
                tk_msgbox.showerror(title='Error', message=case_data_load_error, parent=case_window)
            else:
                tk_msgbox.showinfo(
                    title='Load Case Data', message=f'Loaded Case Data: {destination_path}', parent=case_window)

    def add_agency_logo():
        '''Import image file and covert it into base64'''
        logo_path = tk_filedialog.askopenfilename(parent=case_window,
                                                         title='Add agency logo',
                                                         filetypes=(('All supported files', '*.png *.jpg *.gif'), ))

        if logo_path and os.path.exists(logo_path):
            agency_logo_load_error = None
            with open(logo_path, 'rb') as agency_logo_file:
                agency_logo_mimetype = guess_mime(agency_logo_file)
                if agency_logo_mimetype and 'image' in agency_logo_mimetype:
                    try:
                        agency_logo_base64_encoded = base64.b64encode(agency_logo_file.read())
                    except:
                        agency_logo_load_error = 'Unable to encode the selected file in base64.'
                else:
                    agency_logo_load_error = 'Selected file is not a valid picture file.'
            if agency_logo_load_error:
                tk_msgbox.showerror(title='Error', message=agency_logo_load_error, parent=case_window)
            else:
                case_agency_logo_path_entry.delete(0, 'end')
                case_agency_logo_path_entry.insert(0, logo_path)
                case_agency_logo_mimetype.delete(0, 'end')
                case_agency_logo_mimetype.insert(0, agency_logo_mimetype)
                case_agency_logo_b64.delete(0, 'end')
                case_agency_logo_b64.insert(0, agency_logo_base64_encoded)
                tk_msgbox.showinfo(
                    title='Add agency logo', message=f'{logo_path} was added as Agency logo', parent=case_window)

    ### Case Data Window creation
    case_window = tk.Toplevel(main_window)
    case_window.transient(main_window)
    case_window_width = 560
    if is_platform_linux():
        case_window_height = 325
    elif is_platform_macos():
        case_window_height = 317
    else:
        case_window_height = 305

    #### Places Case Data window in the center of the main window
    main_window.update_idletasks()
    main_x = main_window.winfo_x()
    main_y = main_window.winfo_y()
    main_w = main_window.winfo_width()
    main_h = main_window.winfo_height()

    margin_width = main_x + (main_w - case_window_width) // 2
    margin_height = main_y + (main_h - case_window_height) // 2

    #### Case Data window properties
    case_window.geometry(
        f'{case_window_width}x{case_window_height}'
        f'{geometry_offset(margin_width)}{geometry_offset(margin_height)}')
    case_window.resizable(False, False)
    case_window.configure(bg=theme_bgcolor)
    case_window.title('Add Case Data')
    case_window.grid_columnconfigure(0, weight=1)

    def on_main_focus(event):
        if case_window.winfo_exists():
            case_window.bell()
            case_window.lift()
            case_window.focus_force()

    main_window.bind("<FocusIn>", on_main_focus)

    def close_case_window():
        main_window.unbind("<FocusIn>")
        case_window.destroy()

    case_window.protocol("WM_DELETE_WINDOW", close_case_window)

    #### Layout
    case_title_label = ttk.Label(case_window, text='Add Case Data', font=('Helvetica 18'))
    case_title_label.grid(row=0, column=0, padx=14, pady=7, sticky='w')
    case_number_frame = ttk.LabelFrame(case_window, text=' Case Number ')
    case_number_frame.grid(row=1, column=0, padx=14, pady=5, sticky='we')
    case_number_entry = ttk.Entry(case_number_frame, textvariable=casedata['Case Number'])
    case_number_entry.pack(padx=5, pady=4, fill='x')
    case_number_entry.focus()
    case_agency_frame = ttk.LabelFrame(case_window, text=' Agency ')
    case_agency_frame.grid(row=2, column=0, padx=14, pady=5, sticky='we')
    case_agency_frame.grid_columnconfigure(1, weight=1)
    case_agency_name_label = ttk.Label(case_agency_frame, text="Name:")
    case_agency_name_label.grid(row=0, column=0, padx=5, pady=4, sticky='w')
    case_agency_name_entry = ttk.Entry(case_agency_frame, textvariable=casedata['Agency'])
    case_agency_name_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=4, sticky='we')
    case_agency_logo_label = ttk.Label(case_agency_frame, text="Logo:")
    case_agency_logo_label.grid(row=1, column=0, padx=5, pady=6, sticky='w')
    case_agency_logo_path_entry = ttk.Entry(case_agency_frame, textvariable=casedata['Agency Logo Path'])
    case_agency_logo_mimetype = ttk.Entry(case_agency_frame, textvariable=casedata['Agency Logo mimetype'])
    case_agency_logo_b64 = ttk.Entry(case_agency_frame, textvariable=casedata['Agency Logo base64'])
    case_agency_logo_path_entry.grid(row=1, column=1, padx=5, pady=6, sticky='we')
    case_agency_logo_button = ttk.Button(case_agency_frame, text='Add File', command=add_agency_logo)
    case_agency_logo_button.grid(row=1, column=2, padx=5, pady=6)
    case_examiner_frame = ttk.LabelFrame(case_window, text=' Examiner ')
    case_examiner_frame.grid(row=3, column=0, padx=14, pady=5, sticky='we')
    case_examiner_entry = ttk.Entry(case_examiner_frame, textvariable=casedata['Examiner'])
    case_examiner_entry.pack(padx=5, pady=4, fill='x')
    modules_btn_frame = ttk.Frame(case_window)
    modules_btn_frame.grid(row=4, column=0, padx=14, pady=16, sticky='we')
    modules_btn_frame.grid_columnconfigure(2, weight=1)
    load_case_button = ttk.Button(modules_btn_frame, text='Load Case Data File', command=load_case)
    load_case_button.grid(row=0, column=0, padx=5)
    save_case_button = ttk.Button(modules_btn_frame, text='Save Case Data File', command=save_case)
    save_case_button.grid(row=0, column=1, padx=5)
    ttk.Separator(modules_btn_frame, orient='vertical').grid(row=0, column=2, padx=20, sticky='ns')
    clear_case_button = ttk.Button(modules_btn_frame, text='Clear', command=clear)
    clear_case_button.grid(row=0, column=3, padx=5)
    close_case_button = ttk.Button(modules_btn_frame, text='Close', command=close_case_window)
    close_case_button.grid(row=0, column=4, padx=5)

    if is_platform_macos():
        case_window.grab_set_global()
    else:
        case_window.grab_set()


## Main window creation
main_window = tk.Tk()
icon = resource_path('icon.png')
loader: typing.Optional[plugin_loader.PluginLoader] = None
loader = plugin_loader.PluginLoader()
mlist = {}
profile_filename = None
casedata = {'Case Number': tk.StringVar(),
            'Agency': tk.StringVar(),
            'Agency Logo Path': tk.StringVar(),
            'Agency Logo mimetype': tk.StringVar(),
            'Agency Logo base64': tk.StringVar(),
            'Examiner': tk.StringVar(),
            }
timezone_set = tk.StringVar()
modules_filter_var = tk.StringVar()
modules_filter_var.trace_add("write", filter_modules)  # Trigger filtering on input change
pickModules()

## Theme properties
theme_bgcolor = '#2c2825'
theme_inputcolor = '#705e52'
theme_fgcolor = '#fdcb52'

## Main window properties
main_window.minsize(890, 690)
main_window.title(f'iLEAPP version {leapp_version}')
main_window.configure(bg=theme_bgcolor)
logo_icon = tk.PhotoImage(file=icon)
main_window.iconphoto(True, logo_icon)
main_window.grid_columnconfigure(0, weight=1)
main_window.option_add('*TkChooseDir*foreground', 'black')
main_window.option_add('*TkFDialog*foreground', 'black')

## Widgets default style
style = ttk.Style()
style.theme_use('default')
style.configure('.',
                background=theme_bgcolor,
                foreground=theme_fgcolor)
style.configure('TButton')
style.map('TButton',
          background=[('active', 'black'), ('!disabled', theme_fgcolor)],
          foreground=[('active', theme_fgcolor), ('!disabled', 'black')])
style.configure('TEntry', fieldbackground=theme_inputcolor, highlightthickness=0)
style.configure(
    'TCombobox', selectforeground=theme_fgcolor,
    selectbackground=theme_inputcolor, arrowcolor=theme_fgcolor)
style.map('TCombobox',
          fieldbackground=[('active', theme_inputcolor), ('readonly', theme_inputcolor)],
          )
style.configure('TScrollbar', background=theme_fgcolor, arrowcolor='black', troughcolor=theme_inputcolor)
style.configure('TProgressbar', thickness=4, background='DarkGreen')

## Main Window Layout
### Top part of the window
title_frame = ttk.Frame(main_window)
title_frame.pack(padx=14, pady=8, fill='x')
ileapp_logo = ImageTk.PhotoImage(file=resource_path("iLEAPP_logo.png"))
ileapp_logo_label = ttk.Label(title_frame, image=ileapp_logo)
ileapp_logo_label.pack(side='left')

settings_icon = ImageTk.PhotoImage(Image.open(resource_path("settings.png")).resize((32, 32)))
settings_label = ttk.Label(title_frame, image=settings_icon, cursor="hand2")
settings_label.pack(side='right', padx=(10, 0))
settings_label.bind("<Button-1>", lambda e: open_settings_window())

leapps_logo = ImageTk.PhotoImage(Image.open(resource_path("leapps_i_logo.png")).resize((110, 51)))
leapps_logo_label = ttk.Label(title_frame, image=leapps_logo, cursor="target")
leapps_logo_label.pack(side='right')
leapps_logo_label.bind("<Button-1>", lambda e: open_website("https://leapps.org"))

### Input output selection
input_frame = ttk.LabelFrame(
    main_window,
    text=' Select the file (tar/zip/gz) or directory of the target iOS full file system extraction for parsing: ')
input_frame.pack(padx=14, pady=2, fill='x')
input_entry = ttk.Entry(input_frame)
input_entry.pack(side='left', padx=5, pady=4, fill='x', expand=True)
input_history_button = ttk.Button(input_frame, text='▼', width=3,
                                command=lambda: show_history_menu(input_history_button, 'input'))
input_history_button.pack(side='left', padx=2, pady=4)
input_file_button = ttk.Button(input_frame, text='Browse File', command=lambda: select_input('file'))
input_file_button.pack(side='left', padx=5, pady=4)
input_folder_button = ttk.Button(input_frame, text='Browse Folder', command=lambda: select_input('folder'))
input_folder_button.pack(side='left', padx=5, pady=4)

output_frame = ttk.LabelFrame(main_window, text=' Select Output Path ')
output_frame.pack(padx=14, pady=5, fill='x')
output_path_row = ttk.Frame(output_frame)
output_path_row.pack(fill='x')
output_entry = ttk.Entry(output_path_row)
output_entry.pack(side='left', padx=5, pady=4, fill='x', expand=True)
output_history_button = ttk.Button(output_path_row, text='▼', width=3,
                                 command=lambda: show_history_menu(output_history_button, 'output'))
output_history_button.pack(side='left', padx=2, pady=4)
output_folder_button = ttk.Button(output_path_row, text='Browse Folder', command=select_output)
output_folder_button.pack(side='left', padx=5, pady=4)
output_folder_name_row = ttk.Frame(output_frame)
output_folder_name_row.pack(fill='x', padx=5, pady=(0, 4))
ttk.Label(output_folder_name_row, text='Folder name:').pack(side='left', padx=(0, 5))
output_folder_name_entry = ttk.Entry(output_folder_name_row)
output_folder_name_entry.insert(0, default_output_folder_name())
output_folder_name_entry.configure(
    validate='key',
    validatecommand=(main_window.register(allow_output_folder_name_chars), '%P'))
output_folder_name_entry.pack(side='left', fill='x', expand=True)

mlist_frame = ttk.LabelFrame(main_window, text=' Available Modules: ', name='f_list')
mlist_frame.pack(padx=14, pady=5, expand=True, fill='both')

button_frame = ttk.Frame(mlist_frame)
button_frame.pack(pady=4, fill='x')

if is_platform_macos():
    modules_filter_icon = ttk.Label(button_frame, text="\U0001F50E")
else:
    modules_filter_img = ImageTk.PhotoImage(file=resource_path("magnif_glass.png"))
    modules_filter_icon = ttk.Label(button_frame, image=modules_filter_img)
modules_filter_icon.pack(padx=4, side='left')
modules_filter_entry = ttk.Entry(button_frame, textvariable=modules_filter_var)
modules_filter_entry.pack(padx=2, fill='x', expand=True, side='left')
ttk.Separator(button_frame, orient='vertical').pack(padx=10, side='left', fill='y')
all_button = ttk.Button(button_frame, text='Select All', command=select_all)
all_button.pack(padx=5, side='left')
none_button = ttk.Button(button_frame, text='Deselect All', command=deselect_all)
none_button.pack(padx=5, side='left')
ttk.Separator(button_frame, orient='vertical').pack(padx=10, side='left', fill='y')
load_button = ttk.Button(button_frame, text='Load Profile', command=load_profile)
load_button.pack(padx=5, side='left')
save_button = ttk.Button(button_frame, text='Save Profile', command=save_profile)
save_button.pack(padx=5, side='left')
module_list_frame = ttk.Frame(mlist_frame)
module_list_frame.pack(expand=True, fill='both')
mlist_text = tk.Text(module_list_frame, name='tbox', bg=theme_bgcolor, highlightthickness=0)
mlist_text.pack(expand=True, fill='both', padx=4)
mlist_text_scrollbar = ttk.Scrollbar(module_list_frame, orient='vertical', command=mlist_text.yview)
mlist_text.config(yscrollcommand=mlist_text_scrollbar.set)
mlist_text_scrollbar.place(relx=1, rely=0, relheight=1, anchor='ne')
filter_modules()
mlist_text.config(state='disabled')
main_window.bind_class('Checkbutton', '<MouseWheel>', scroll)
main_window.bind_class('Checkbutton', '<Button-4>', scroll)
main_window.bind_class('Checkbutton', '<Button-5>', scroll)
main_window.bind("<Control-f>", lambda event: modules_filter_entry.focus_set()) # Focus on The Filter Field
main_window.bind("<Control-i>", lambda event: input_entry.focus_set()) # Focus on the Input Field
main_window.bind("<Control-o>", lambda event: output_entry.focus_set()) # Focus on the Output Field

### Process
bottom_frame = ttk.Frame(main_window)
bottom_frame.pack(padx=16, pady=6, fill='x')
process_button = ttk.Button(bottom_frame, text='Process', command=lambda: process(casedata))
process_button.pack(side='left', padx=5)
close_button = ttk.Button(bottom_frame, text='Close', command=main_window.quit)
close_button.pack(side='left', padx=5)
# ttk.Separator(bottom_frame, orient='vertical').pack(padx=10, side='left', expand=True, fill='both')
case_data_button_frame = ttk.Frame(bottom_frame)
case_data_button_frame.pack(side='left', expand=True, fill='x')
case_data_button = ttk.Button(case_data_button_frame, text='Case Data', command=case_data)
case_data_button.pack(padx=5)
# ttk.Separator(bottom_frame, orient='vertical').pack(padx=10, side='left', expand=True, fill='both')
selected_modules_frame = ttk.Frame(bottom_frame)
selected_modules_frame.pack(side='right', padx=5)
selected_modules_label = ttk.Label(selected_modules_frame, text='Number of selected modules: ')
selected_modules_label.pack(anchor='e')
auto_unselected_modules_label = ttk.Label(
    selected_modules_frame,
    text='(Modules making some time to run were automatically unselected)',
    font='Helvetica 10')
auto_unselected_modules_label.pack(anchor='e')
get_selected_modules()

#### Logs
logtext_frame = ttk.Frame(main_window, name='logs_frame')
log_text = tk.Text(
    logtext_frame, name='log_text', bg=theme_inputcolor, fg=theme_fgcolor, highlightthickness=1)
log_text.pack(expand=True, fill='both')
log_text_scrollbar = ttk.Scrollbar(logtext_frame, orient='vertical', command=log_text.yview)
log_text.config(yscrollcommand=log_text_scrollbar.set)
log_text_scrollbar.place(relx=1, rely=0, relheight=1, anchor='ne')

### Progress bar
progress_bar_frame = ttk.Frame(main_window, name='progress_bar_frame')
progress_bar = ttk.Progressbar(progress_bar_frame, name='progress_bar', orient='horizontal')
progress_bar.pack(padx=16, pady=20, fill='x')

### Push main window on top
def OnFocusIn(event):
    if type(event.widget).__name__ == 'Tk':
        event.widget.attributes('-topmost', False)

def geometry_offset(value):
    return f'+{value}' if value >= 0 else str(value)

def center_main_window_macos(window, width, height):
    """ 
    MacOS: Determine full desktop dimensions and which monitor the mouse is on, 
    then center the window within those specific monitor boundaries.
    """
    window.update_idletasks()
    mx, my = window.winfo_pointerxy()

    # 1. Get primary monitor dimensions (always starts at 0,0 on macOS)
    window.geometry("+0+0")
    window.update_idletasks()
    pw = window.winfo_screenwidth()
    ph = window.winfo_screenheight()

    # 2. Move to mouse position to get the second monitor's dimensions
    window.geometry(f'{geometry_offset(mx)}{geometry_offset(my)}')
    window.update_idletasks()
    sw = window.winfo_screenwidth()
    sh = window.winfo_screenheight()

    # 3. Get virtual desktop bounds to handle monitors to the left/right
    vx = window.winfo_vrootx()

    # 4. Determine the actual boundaries of the monitor the mouse is on
    if mx < 0: # Monitor is to the left of primary
        mon_x, mon_y, mon_w, mon_h = vx, 0, abs(vx), sh
    elif mx >= pw: # Monitor is to the right of primary
        mon_x, mon_y, mon_w, mon_h = pw, 0, sw, sh
    else: # Mouse is on the primary monitor
        mon_x, mon_y, mon_w, mon_h = 0, 0, pw, ph

    # 5. Center the window within those specific monitor boundaries
    start_x = mon_x + (mon_w - width) // 2
    start_y = mon_y + (mon_h - height) // 2

    window.geometry(f'{width}x{height}{geometry_offset(start_x)}{geometry_offset(start_y)}')

main_window.attributes('-topmost', True)
main_window.focus_force()
main_window.bind('<FocusIn>', OnFocusIn)

if is_platform_macos():
    center_main_window_macos(main_window, 890, 690)
main_window.mainloop()
