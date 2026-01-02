#!/usr/bin/env python3

import pathlib
import json
import argparse
import io
import pytz
import os.path
import typing
import scripts.report as report
import traceback
import sys
import multiprocessing
import signal
import time as time_module
import json as _agent_json

import scripts.plugin_loader as plugin_loader
import leapp_functions.app.history as history
import scripts.lavafuncs as lavafuncs

from shutil import copy2
from getpass import getpass
from scripts.search_files import *  # pylint: disable=wildcard-import,unused-wildcard-import
from scripts.ilapfuncs import *  # pylint: disable=wildcard-import,unused-wildcard-import
from leapp_functions.app.output import validate_output_folder_available
from scripts.version_info import leapp_name, leapp_version, check_runtime_dependencies
from time import process_time, gmtime, strftime, perf_counter
from scripts.lavafuncs import *  # pylint: disable=wildcard-import,unused-wildcard-import
from scripts.context import Context
from scripts.ios_keychain import report_supplied_keychain
from scripts.lavafuncs import lava_json_name
from scripts.mp_plugin_runner import run_one_plugin

def validate_args(args):
    if args.artifact_paths or args.create_profile_casedata:
        return  # Skip further validation if --artifact_paths is used

    # Ensure other arguments are provided
    mandatory_args = ['input_path', 'output_path', 't']
    for arg in mandatory_args:
        value = getattr(args, arg)
        if value is None:
            raise argparse.ArgumentError(None, f'No {arg.upper()} provided. Run the program again.')

    # Check existence of paths
    if not os.path.exists(args.input_path):
        raise argparse.ArgumentError(None, f'INPUT path \'{args.input_path}\' does not exist! Run the program again.')

    if not os.path.exists(args.output_path):
        raise argparse.ArgumentError(None, 'OUTPUT path \'{args.output_path}\' does not exist! Run the program again.')
    if not os.path.isdir(os.path.abspath(args.output_path)):
        raise argparse.ArgumentError(None, f'OUTPUT path \'{args.output_path}\' must be a directory! Run the program again.')

    # Validate new folder name for output path
    output_folder_valid, output_folder_error = validate_output_folder_available(
        os.path.abspath(args.output_path), args.custom_output_folder)
    if not output_folder_valid:
        raise argparse.ArgumentError(None, output_folder_error)

    # Validate input_path based on type
    abs_input_path = os.path.abspath(args.input_path)
    if args.t == 'fs': # Filesystem input type
        # Check if input path is a directory
        if not os.path.isdir(abs_input_path):
            raise argparse.ArgumentError(None, f'INPUT path \'{args.input_path}\' is not a directory. Type "fs" requires '
                                               f'a directory input. Run the program again.')
        # Check if directory is empty
        if not os.listdir(abs_input_path):
            raise argparse.ArgumentError(None, f'Input directory \'{args.input_path}\' is empty. Run the program again.')
    elif args.t == 'file': # Single file input type
        if not os.path.isfile(abs_input_path):
            raise argparse.ArgumentError(None, f'INPUT path \'{args.input_path}\' is not a file. Type "file" requires a '
                                               f'single file input. Run the program again.')

    if args.load_case_data and not os.path.exists(args.load_case_data):
        raise argparse.ArgumentError(None, 'LEAPP Case Data file not found! Run the program again.')

    if args.load_profile and not os.path.exists(args.load_profile):
        raise argparse.ArgumentError(None, 'iLEAPP Profile file not found! Run the program again.')

    if args.keychain and not os.path.isfile(args.keychain):
        raise argparse.ArgumentError(None, 'Keychain file not found! Run the program again.')

    try:
        pytz.timezone(args.timezone)
    except pytz.UnknownTimeZoneError as ex:
        raise argparse.ArgumentError(
            None, 'Unknown timezone! Run the program again.') from ex


def create_profile(plugins, path):
    available_modules = [(module_data.category, module_data.name) for module_data in plugins]
    available_modules.sort()
    modules_in_profile = {}

    user_choice = ''
    print('--- iLEAPP Profile file creation ---\n')
    instructions = 'You can type:\n'
    instructions += '   - \'a\' to add or remove modules in the profile file\n'
    instructions += '   - \'l\' to display the list of all available modules with their number\n'
    instructions += '   - \'p\' to display the modules added into the profile file\n'
    instructions += '   - \'q\' to quit and save\n'
    while not user_choice:
        print(instructions)
        user_choice = input('Please enter your choice: ').lower()
        print()
        if user_choice == "l":
            print('Available modules:')
            for number, available_module in enumerate(available_modules):
                print(number + 1, available_module)
            print()
            user_choice = ''
        elif user_choice == "p":
            if modules_in_profile:
                for number, module in modules_in_profile.items():
                    print(number, module)
                print()
            else:
                print('No module added to the profile file\n')
            user_choice = ''
        elif user_choice == 'a':
            modules_numbers = input('Enter the numbers of modules, seperated by a comma, to add or remove in the profile file: ')
            modules_numbers = modules_numbers.split(',')
            modules_numbers = [module_number.strip() for module_number in modules_numbers]
            for module_number in modules_numbers:
                if module_number.isdigit():
                    module_number = int(module_number)
                    if module_number > 0 and module_number <= len(available_modules):
                        if module_number not in modules_in_profile:
                            module_to_add = available_modules[module_number - 1]
                            modules_in_profile[module_number] = module_to_add
                            print(f'module number {module_number} {module_to_add} was added')
                        else:
                            module_to_remove = modules_in_profile[module_number]
                            print(f'module number {module_number} {module_to_remove} was removed')
                            del modules_in_profile[module_number]
                    else:
                        print('Please enter the number of a module!!!\n')
            print()
            user_choice = ''
        elif user_choice == "q":
            if modules_in_profile:
                modules = [module_info[1] for module_info in modules_in_profile.values()]
                profile_filename = ''
                while not profile_filename:
                    profile_filename = input('Enter the name of the profile: ')
                profile_filename += '.ilprofile'
                filename = os.path.join(path, profile_filename)
                with open(filename, "wt", encoding="utf-8") as profile_file:
                    json.dump({"leapp": "ileapp", "format_version": 1, "plugins": modules}, profile_file)
                print('\nProfile saved:', filename)
                print()
            else:
                print('No module added. The profile file was not created.\n')
                print()
            return
        else:
            print('Please enter a valid choice!!!\n')
            user_choice = ''

def create_casedata(path):
    case_data_values = {}
    print('--- LEAPP Case Data file creation ---\n')
    print('Enter the following information:')
    case_data_values['Case Number'] = input("Case Number: ")
    case_data_values['Agency'] = input("Agency: ")
    case_data_values['Examiner'] = input("Examiner : ")
    print()
    case_data_filename = ''
    while not case_data_filename:
        case_data_filename = input('Enter the name of the Case Data file: ')
    case_data_filename += '.lcasedata'
    filename = os.path.join(path, case_data_filename)
    with open(filename, "wt", encoding="utf-8") as case_data_file:
        json.dump({"leapp": "case_data", "case_data_values": case_data_values}, case_data_file)
    print('\nCase Data file saved:', filename)
    print()
    return

def main():
    check_runtime_dependencies()
    parser = argparse.ArgumentParser(description=f'iLEAPP v{leapp_version}: iOS Logs, Events, And Plists Parser.')
    parser.add_argument('-t', choices=['fs', 'tar', 'zip', 'gz', 'itunes', 'file'], required=False, action="store",
                        help=("Specify the input type. "
                              "'fs' for a folder containing extracted files with normal paths and names, "
                              "'tar', 'zip', or 'gz' for compressed packages containing files with normal names, "
                              "'itunes' for a folder containing a raw iTunes backup with hashed paths and names, "
                              "'file' for a single file input."))
    parser.add_argument('-o', '--output_path', required=False, action="store",
                        help='Path to base output folder (this must exist)')
    parser.add_argument('-i', '--input_path', required=False, action="store", help='Path to input file/folder')
    parser.add_argument('-tz', '--timezone', required=False, action="store", default='UTC', type=str, help="Timezone name (e.g., 'America/New_York')")
    parser.add_argument('-w', '--wrap_text', required=False, action="store_false", default=True,
                        help='Do not wrap text for output of data files')
    parser.add_argument('-m', '--load_profile', required=False, action="store", help="Path to iLEAPP Profile file (.ilprofile).")
    parser.add_argument('-d', '--load_case_data', required=False, action="store", help="Path to LEAPP Case Data file (.lcasedata).")
    parser.add_argument('-c', '--create_profile_casedata', required=False, action="store",
                        help=("Generate an iLEAPP Profile file (.ilprofile) or LEAPP Case Data file (.lcasedata) into the specified path. "
                              "This argument is meant to be used alone, without any other arguments."))
    parser.add_argument('-p', '--artifact_paths', required=False, action="store_true",
                        help=("Generate a text file list of artifact paths. "
                              "This argument is meant to be used alone, without any other arguments."))
    parser.add_argument('--custom_output_folder', required=False, action="store", help="Custom name for the output folder")
    parser.add_argument('--custom_artifacts_path', required=False, action="store", help="Additional path to load artifacts from (e.g., scripts/alternate_artifacts)")
    parser.add_argument('--itunes_password', required=False, action="store", help="Password used for encrypted iTunes backup")
    parser.add_argument('--keychain', required=False, action="store",
                        help=("Path to a keychain file captured from the device. Some apps keep "
                              "their database key in the keychain, which is collected separately "
                              "from the file system extraction."))
    parser.add_argument('--mp_per_plugin', required=False, action="store_true", default=False,
                        help=("EXPERIMENTAL: Run each plugin in its own subprocess (spawn). "
                              "This enables skipping a long-running plugin (planned) without stopping the whole run."))

    # Check if no arguments were provided
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit()

    args = parser.parse_args()

    available_plugins = []
    loader_paths = [plugin_loader.PLUGINPATH]
    if args.custom_artifacts_path:
        loader_paths.append(pathlib.Path(args.custom_artifacts_path))
    loader = plugin_loader.PluginLoader(plugin_paths=loader_paths)
    for plugin in sorted(loader.plugins, key=lambda p: p.category):
        if (plugin.module_name == 'iTunesBackupInfo'
                or plugin.name == 'last_build'
                or plugin.module_name == 'logarchive' and plugin.name != 'logarchive'):
            continue
        else:
            available_plugins.append(plugin)
    selected_plugins = available_plugins.copy()
    profile_filename = None
    casedata = {}

    extracttype = args.t

    try:
        validate_args(args)
    except argparse.ArgumentError as e:
        parser.error(str(e))

    if args.artifact_paths:
        print('Artifact path list generation started.')
        print('')
        path_list = set()
        for plugin in loader.plugins:
            if plugin.module_name == 'logarchive':
                continue
            if isinstance(plugin.search, tuple):
                for x in plugin.search:
                    path_list.add(x)
            elif isinstance(plugin.search, str):
                path_list.add(plugin.search)
            else:
                continue
        with open('path_list.txt', 'w', encoding='utf-8') as paths:
            for path in sorted(path_list):
                paths.write(f'{path}\n')
                print(path)
        print('')
        print('Artifact path list generation completed')
        return

    if args.create_profile_casedata:
        if os.path.isdir(args.create_profile_casedata):
            create_choice = ''
            print('-' * 55)
            print('Welcome to iLEAPP Profile or Case Data file creation\n')
            instructions = 'You can type:\n'
            instructions += '   - \'1\' to create an iLEAPP Profile file (.ilprofile)\n'
            instructions += '   - \'2\' to create a LEAPP Case Data file (.lcasedata)\n'
            instructions += '   - \'q\' to quit\n'
            while not create_choice:
                print(instructions)
                create_choice = input('Please enter your choice: ').lower()
                print()
                if create_choice == '1':
                    create_profile(available_plugins, args.create_profile_casedata)
                    create_choice = ''
                elif create_choice == '2':
                    create_casedata(args.create_profile_casedata)
                    create_choice = ''
                elif create_choice == 'q':
                    return
                else:
                    print('Please enter a valid choice!!!\n')
                    create_choice = ''
        else:
            print('OUTPUT folder for storing iLEAPP Profile file does not exist!\nRun the program again.')
            return

    if args.load_case_data:
        case_data_filename = args.load_case_data
        case_data_load_error = None
        with open(case_data_filename, "rt", encoding="utf-8") as case_data_file:
            try:
                case_data = json.load(case_data_file)
            except (ValueError, TypeError):
                case_data_load_error = "File was not a valid case data file: invalid format"
                print(case_data_load_error)
                return

        if not case_data_load_error:
            if isinstance(case_data, dict):
                if case_data.get("leapp") != "case_data":
                    case_data_load_error = "File was not a valid case data file"
                    print(case_data_load_error)
                    return
                else:
                    print(f'Case Data loaded: {case_data_filename}')
                    casedata = case_data.get('case_data_values', {})
            else:
                case_data_load_error = "File was not a valid case data file: invalid format"
                print(case_data_load_error)
                return

    if args.load_profile:
        profile_filename = args.load_profile
        profile_load_error = None
        with open(profile_filename, "rt", encoding="utf-8") as profile_file:
            try:
                profile = json.load(profile_file)
            except (ValueError, TypeError):
                profile_load_error = "File was not a valid case data file: invalid format"
                print(profile_load_error)
                return

        if not profile_load_error:
            if isinstance(profile, dict):
                if profile.get("leapp") != "ileapp" or profile.get("format_version") != 1:
                    profile_load_error = "File was not a valid profile file: incorrect LEAPP or version"
                    print(profile_load_error)
                    return
                else:
                    profile_plugins = set(profile.get("plugins", []))
                    selected_plugins = [selected_plugin for selected_plugin in available_plugins
                                        if selected_plugin.name in profile_plugins]
            else:
                profile_load_error = "File was not a valid profile file: invalid format"
                print(profile_load_error)
                return

    input_path = args.input_path
    wrap_text = args.wrap_text
    output_path = os.path.abspath(args.output_path)
    time_offset = args.timezone
    custom_output_folder = args.custom_output_folder
    itunes_backup_password = args.itunes_password
    Context.set_keychain_path(args.keychain)

    # ios file system extractions contain paths > 260 char, which causes problems
    # This fixes the problem by prefixing \\?\ on each windows path.
    if is_platform_windows():
        if input_path[1] == ':' and extracttype =='fs': input_path = '\\\\?\\' + input_path.replace('/', '\\')
        if output_path[1] == ':': output_path = '\\\\?\\' + output_path.replace('/', '\\')

    out_params = OutputParameters(output_path, custom_output_folder)
    Context.set_output_params(out_params)

    if args.mp_per_plugin:
        logfunc("EXPERIMENTAL MODE ENABLED: --mp_per_plugin (per-plugin subprocess execution)")

    initialize_lava(input_path, out_params.output_folder_base, extracttype)
    if args.mp_per_plugin:
        # Parent does not need an open connection while children write to the DB.
        lava_close_db()

    # Record history if enabled
    history.record_input_path(input_path)
    history.record_output_path(output_path)

    crunch_artifacts(selected_plugins, extracttype, input_path, out_params, wrap_text, loader, casedata, time_offset,
        profile_filename, itunes_backup_password, decryption_keys=None, mp_per_plugin=args.mp_per_plugin)

    lava_finalize_output(out_params.output_folder_base)

def crunch_artifacts(
        plugins: typing.Sequence[plugin_loader.PluginSpec], extracttype, input_path, out_params, wrap_text,
        loader: plugin_loader.PluginLoader, casedata, time_offset, profile_filename,
        itunes_backup_password=None, decryption_keys=None, mp_per_plugin: bool = False):
    start = process_time()
    start_wall = perf_counter()

    logfunc('Processing started. Please wait. This may take a few minutes...')

    logfunc('\n--------------------------------------------------------------------------------------')
    logfunc(f'iLEAPP v{leapp_version}: iOS Logs, Events, And Plists Parser')
    logfunc('Objective: Triage iOS Full File System and iTunes Backup Extractions.')
    logfunc('By: Alexis Brignoni | @AlexisBrignoni | abrignoni.com')
    logfunc('By: Yogesh Khatri   | @SwiftForensics | swiftforensics.com\n')
    logdevinfo()
    report_supplied_keychain()
    seeker = None
    password = itunes_backup_password
    try:
        if extracttype == 'fs':
            seeker = FileSeekerDir(input_path, out_params.data_folder)

        elif extracttype == 'file':
            seeker = FileSeekerFile(input_path, out_params.data_folder)

        elif extracttype in ('tar', 'gz'):
            seeker = FileSeekerTar(input_path, out_params.data_folder)

        elif extracttype == 'zip':
            seeker = FileSeekerZip(input_path, out_params.data_folder)

        elif extracttype == 'itunes':
            itunes_backup_type = get_itunes_backup_type(input_path)
            if itunes_backup_type:
                supported, encrypted, message = check_itunes_backup_status(
                    input_path, itunes_backup_type)
                if not supported:
                    logfunc(message)
                    return False
                else:
                    if encrypted:
                        while not decryption_keys:
                            if not password:
                                password = getpass("iTunes Backup password: ")
                            decryption_keys, _ = decrypt_itunes_backup(input_path, password)
                            if not decryption_keys:
                                return False
            else:
                logfunc('Input folder is not a valid iTunes backup!')
                return False
            seeker = FileSeekerItunes(input_path, out_params.data_folder,
                                    itunes_backup_type, decryption_keys)

        else:
            logfunc('Error on argument -o (input type)')
            return False
    except Exception:  # pylint: disable=broad-exception-caught
        logfunc('Had an exception in Seeker - see details below. Terminating Program!')
        temp_file = io.StringIO()
        traceback.print_exc(file=temp_file)
        logfunc(temp_file.getvalue())
        temp_file.close()
        return False

    # Now ready to run
    # add last_build at the start except for iTunes backups
    if extracttype != 'itunes':
        plugins.insert(0, loader["last_build"])

    logfunc(f'Info: {len(loader) - 2} modules loaded.') # excluding last_build and iTunesBackupInfo
    if profile_filename:
        logfunc(f'Loaded profile: {profile_filename}')
    logfunc(f'Artifact to parse: {len(plugins)}')
    logfunc(f'File/Directory selected: {input_path}')
    logfunc('\n--------------------------------------------------------------------------------------')

    log = open(os.path.join(out_params.output_folder_base, '_HTML', '_Script_Logs', 'ProcessedFilesLog.html'), 'w+', encoding='utf8')
    log.write(f'Extraction/Path selected: {input_path}<br><br>')
    log.write(f'Timezone selected: {time_offset}<br><br>')

    ctx_mp = multiprocessing.get_context("spawn") if mp_per_plugin else None
    installed_os_version = ''
    current_proc = None
    last_interrupt_ts = 0.0
    subprocess_phase = "idle"

    #region agent log
    def _agent_log(hypothesis_id: str, location: str, message: str, data: dict):
        try:
            payload = {
                "sessionId": "debug-session",
                "runId": "hang1",
                "hypothesisId": hypothesis_id,
                "location": location,
                "message": message,
                "data": data,
                "timestamp": int(time_module.time() * 1000),
            }
            with open("/Users/pl-2134/Development/iLEAPP/.cursor/debug.log", "a", encoding="utf-8") as f:
                f.write(_agent_json.dumps(payload, ensure_ascii=False) + "\n")
        except Exception:
            pass
    #endregion agent log
    seeker_all_files = []
    try:
        # For iTunes backups, seeker._all_files is a dict keyed by "virtual paths" in backup
        # (eg. private/var/mobile/Library/...).
        if hasattr(seeker, "_all_files") and isinstance(seeker._all_files, dict):
            seeker_all_files = list(seeker._all_files.keys())
        elif hasattr(seeker, "_all_files") and isinstance(seeker._all_files, list):
            seeker_all_files = list(seeker._all_files)
    except Exception:
        seeker_all_files = []

    def _terminate_current_plugin_proc(reason: str):
        nonlocal current_proc
        if current_proc is not None and current_proc.is_alive():
            logfunc(f"Skip requested ({reason}). Terminating current plugin subprocess (pid={current_proc.pid}) ...")
            try:
                current_proc.terminate()
            except Exception:
                pass

    def _interrupt_handler(signum, frame):
        """
        Ctrl+C / Ctrl+Break handling for mp mode:
        - first press: terminate current plugin process and continue
        - second press within 2 seconds: abort run
        """
        nonlocal last_interrupt_ts
        nonlocal subprocess_phase
        # IMPORTANT: use time module explicitly; `time` can be shadowed by datetime.time via star-imports.
        now = time_module.time()
        #region agent log
        _agent_log(
            "A",
            "ileapp.py:_interrupt_handler",
            "signal received",
            {
                "signum": int(signum),
                "phase": subprocess_phase,
                "has_proc": bool(current_proc is not None),
                "proc_pid": getattr(current_proc, "pid", None),
                "proc_alive": bool(current_proc.is_alive()) if current_proc is not None else None,
                "since_last_s": round(now - last_interrupt_ts, 3),
            },
        )
        #endregion agent log
        if now - last_interrupt_ts < 2.0:
            logfunc("Second interrupt received. Aborting run.")
            raise KeyboardInterrupt
        last_interrupt_ts = now
        _terminate_current_plugin_proc("SIGINT/SIGBREAK")

    if mp_per_plugin:
        # Register interrupt handler (cross-platform):
        # - SIGINT is Ctrl+C everywhere
        # - SIGBREAK is Ctrl+Break on Windows (if present)
        signal.signal(signal.SIGINT, _interrupt_handler)
        if hasattr(signal, "SIGBREAK"):
            signal.signal(signal.SIGBREAK, _interrupt_handler)

    def _run_plugin_subprocess(plugin_key: str, files_found: list, category_folder: str, file_infos_subset: dict | None = None):
        """Run a plugin in a spawned subprocess and merge returned deltas into parent globals."""
        nonlocal installed_os_version
        nonlocal current_proc
        nonlocal subprocess_phase
        q = ctx_mp.SimpleQueue()
        payload = {
            "plugin_key": plugin_key,
            "files_found": files_found,
            "category_folder": category_folder,
            "wrap_text": wrap_text,
            "time_offset": time_offset,
            "output_folder_base": out_params.output_folder_base,
            "input_path": input_path,
            "extracttype": extracttype,
            "file_infos_subset": file_infos_subset or {},
            "installed_os_version": installed_os_version,
            "seeker_all_files": seeker_all_files,
        }
        #region agent log
        _agent_log(
            "A",
            "ileapp.py:_run_plugin_subprocess",
            "spawn child",
            {
                "plugin_key": plugin_key,
                "ctx_start_method": getattr(ctx_mp, "get_start_method", lambda: None)(),
                "global_start_method": multiprocessing.get_start_method(allow_none=True),
                "files_found_len": len(files_found or []),
                "file_infos_subset_len": len(file_infos_subset or {}),
                "seeker_all_files_len": len(seeker_all_files or []),
            },
        )
        #endregion agent log
        proc = ctx_mp.Process(target=run_one_plugin, args=(payload, q))
        current_proc = proc
        proc.start()
        #region agent log
        _agent_log(
            "B",
            "ileapp.py:_run_plugin_subprocess",
            "child started",
            {"plugin_key": plugin_key, "pid": proc.pid},
        )
        #endregion agent log

        # Join in a loop so we can react to Ctrl+C and treat it as "skip current plugin"
        subprocess_phase = "join_loop"
        while proc.is_alive():
            proc.join(timeout=0.25)
        subprocess_phase = "post_join"
        #region agent log
        _agent_log(
            "B",
            "ileapp.py:_run_plugin_subprocess",
            "child exited",
            {"plugin_key": plugin_key, "pid": proc.pid, "exitcode": proc.exitcode},
        )
        #endregion agent log

        result = None
        try:
            # multiprocessing.SimpleQueue.get() has no timeout; guard with empty() to avoid blocking.
            subprocess_phase = "queue_check"
            empty_val = None
            try:
                empty_val = bool(q.empty())
            except Exception:
                empty_val = None
            #region agent log
            _agent_log(
                "A",
                "ileapp.py:_run_plugin_subprocess",
                "queue check",
                {"plugin_key": plugin_key, "queue_empty": empty_val},
            )
            #endregion agent log
            if empty_val is False:
                subprocess_phase = "queue_get"
                result = q.get()
                subprocess_phase = "post_queue_get"
        except Exception:
            result = None
        #region agent log
        _agent_log(
            "A",
            "ileapp.py:_run_plugin_subprocess",
            "queue result",
            {"plugin_key": plugin_key, "got_result": bool(result is not None), "result_ok": (result or {}).get("ok") if result else None},
        )
        #endregion agent log
        if not result or not result.get("ok"):
            # If we killed the process due to interrupt/skip, treat it as a skip and keep going.
            if proc.exitcode is not None and proc.exitcode < 0:
                logfunc(f"Plugin {plugin_key} was interrupted (exitcode={proc.exitcode}). Skipping.")
                current_proc = None
                return {"ok": True, "plugin_key": plugin_key, "skipped": True}
            err = (result or {}).get("error") if result else "Child process failed without result"
            tb = (result or {}).get("traceback") if result else ""
            raise RuntimeError(f"Subprocess plugin run failed for {plugin_key}: {err}\n{tb}")

        icons_delta = result.get("icons_delta") or {}
        for cat, icon_map in icons_delta.items():
            icons.setdefault(cat, {}).update(icon_map)

        lava_meta_delta = result.get("lava_meta_delta")
        if lava_meta_delta:
            # IMPORTANT: use module global, not the `lava_data` name imported into this module.
            lavafuncs.lava_merge_meta_delta(lavafuncs.lava_data, lava_meta_delta)

        for item in (result.get("lava_only_delta") or []):
            try:
                lava_only_info(item["category"], item["artifact_name"], item["table_name"], item["records"])
            except Exception:
                pass

        # Keep installed OS version in parent so we can pass it to future subprocesses
        discovered_os_version = result.get("installed_os_version") or ''
        if discovered_os_version:
            installed_os_version = discovered_os_version
            try:
                iOS.set_version(discovered_os_version)
                Context.set_installed_os_version(discovered_os_version)
            except Exception:
                pass

        return result

    # Special processing for iTunesBackup Info.plist as it is a seperate entity, not part of the Manifest.db. Seeker won't find it
    if extracttype == 'itunes':
        info_plist_path = os.path.join(input_path, 'Info.plist')
        if os.path.exists(info_plist_path):
            # process_artifact([info_plist_path], 'iTunesBackupInfo', 'Device Info', seeker, out_params.output_folder_base)
            #plugin.method([info_plist_path], out_params.output_folder_base, seeker, wrap_text)
            report_folder = os.path.join(out_params.output_folder_base, '_HTML', 'iTunes Backup')
            if not os.path.exists(report_folder):
                try:
                    os.makedirs(report_folder)
                except (FileExistsError, FileNotFoundError) as ex:
                    logfunc('Error creating report directory at path {}'.format(report_folder))
                    logfunc('Error was {}'.format(str(ex)))
            if not mp_per_plugin:
                loader["itunes_backup_info"].method([info_plist_path], report_folder, seeker, wrap_text, time_offset)
            else:
                _run_plugin_subprocess("itunes_backup_info", [info_plist_path], report_folder)
            report_folder = os.path.join(out_params.output_folder_base, '_HTML', 'Installed Apps')
            if not os.path.exists(report_folder):
                try:
                    os.makedirs(report_folder)
                except (FileExistsError, FileNotFoundError) as ex:
                    logfunc('Error creating report directory at path {}'.format(report_folder))
                    logfunc('Error was {}'.format(str(ex)))
            if not mp_per_plugin:
                loader["itunes_backup_installed_applications"].method([info_plist_path], report_folder, seeker, wrap_text, time_offset)
            else:
                _run_plugin_subprocess("itunes_backup_installed_applications", [info_plist_path], report_folder)
            #del search_list['last_build'] # removing last_build as this takes its place
            print([info_plist_path])  # Future: remove special consideration for itunes? Merge into main search
        else:
            logfunc('Info.plist not found for iTunes Backup!')
            log.write('Info.plist not found for iTunes Backup!')

    # Search for the files per the arguments
    parsed_modules = 0
    lava_only = False
    artifact_search_pattern_id = 0
    file_path_ids = set()

    for plugin_number, plugin in enumerate(plugins, start=1):
        logfunc()
        logfunc('[{}/{}] {} [{}] artifact started'.format(plugin_number, len(plugins),
                                                              plugin.name, plugin.module_name))
        output_types = plugin.artifact_info.get('output_types', '')
        if isinstance(plugin.search, list) or isinstance(plugin.search, tuple):
            search_regexes = plugin.search
        elif plugin.search is None:
            search_regexes = plugin.search
        else:
            search_regexes = [plugin.search]
        files_found = []
        log.write(f'<b>For {plugin.name} artifact</b>')
        if search_regexes is None:
            log.write(f'<ul><li>No search regexes provided for {plugin.name} artifact.')
            log.write("<ul><li><i>'_lava_artifacts.db'</i> used as source file.</li></ul></li></ul>")
            files_found = [os.path.join(out_params.output_folder_base, '_lava_artifacts.db')]
        else:
            for artifact_search_regex in search_regexes:
                artifact_search_pattern_id += 1
                lava_insert_sqlite_artifact_search_pattern(
                    artifact_search_pattern_id, plugin.module_name, plugin.name, artifact_search_regex)
                pattern_already_searched = artifact_search_regex in seeker.searched
                found = seeker.search(artifact_search_regex)
                if not found:
                    if plugin.name == 'logarchive' and extracttype != 'fs' and extracttype != 'file':
                        src = os.path.join(os.path.dirname(input_path), "logarchive.json")
                        dst = os.path.join(out_params.data_folder, "logarchive.json")
                        # The artifact declares several search patterns, so this branch is
                        # reached once per pattern that misses; only pick the export up once.
                        if os.path.exists(src) and dst not in files_found:
                            copy2(src, dst)
                            files_found.append(dst)
                    log.write(f'<ul><li>No file found for regex <i>{artifact_search_regex}</i></li></ul>')
                else:
                    log.write(f'<ul><li>{len(found)} {"files" if len(found) > 1 else "file"} for regex <i>{artifact_search_regex}</i> located at:')
                    for pathh in found:
                        # Strip \\?\ only for log display; file_infos is keyed with the
                        # original long-path form on Windows.
                        display_path = pathh[4:] if pathh.startswith('\\\\?\\') else pathh
                        log.write(f'<ul><li>{display_path}</li></ul>')
                        if seeker.file_infos.get(pathh):
                            file_path_id = id(seeker.file_infos.get(pathh))
                            if not pattern_already_searched and file_path_id not in file_path_ids:
                                lava_insert_sqlite_file_path(file_path_id, seeker.file_infos.get(pathh).source_path)
                                file_path_ids.add(file_path_id)
                            lava_insert_sqlite_artifact_link_pattern_to_file(artifact_search_pattern_id, file_path_id)
                    log.write('</li></ul>')
                    files_found.extend(found)
        if files_found:
            if not lava_only and 'lava_only' in output_types:
                lava_only = True
            category_folder = os.path.join(out_params.output_folder_base, '_HTML',
                                           sanitize_report_name(plugin.category, 'category'))
            if not os.path.exists(category_folder):
                try:
                    os.makedirs(category_folder)
                except (FileExistsError, FileNotFoundError) as ex:
                    logfunc('Error creating {} report directory at path {}'.format(plugin.name, category_folder))
                    logfunc('Error was {}'.format(str(ex)))
                    continue  # cannot do work
            try:
                if not mp_per_plugin:
                    plugin.method(files_found, category_folder, seeker, wrap_text, time_offset)
                else:
                    file_infos_subset = {}
                    try:
                        for pth in files_found:
                            fi = getattr(seeker, "file_infos", {}).get(pth)
                            if fi:
                                file_infos_subset[pth] = (fi.source_path, fi.creation_date, fi.modification_date)
                    except Exception:
                        file_infos_subset = {}
                    _run_plugin_subprocess(plugin.name, files_found, category_folder, file_infos_subset)

                if plugin.name == 'logarchive':
                    lava_db_path = os.path.join(out_params.output_folder_base, '_lava_artifacts.db')
                    if does_table_exist_in_db(lava_db_path, 'logarchive'):
                        if not mp_per_plugin:
                            loader["logarchive_artifacts"].method([lava_db_path], category_folder, seeker, wrap_text, time_offset)
                        else:
                            _run_plugin_subprocess("logarchive_artifacts", [lava_db_path], category_folder, {})
                    if does_table_exist_in_db(lava_db_path, 'logarchive_artifacts'):
                        unifed_logs_artifacts = []
                        unifed_logs_artifacts = [plugin.name for plugin in loader.plugins
                                                 if plugin.module_name=='logarchive'
                                                 and plugin.name != 'logarchive'
                                                 and plugin.name != 'logarchive_artifacts']
                        for unifed_log_artifact in unifed_logs_artifacts:
                            if not mp_per_plugin:
                                loader[unifed_log_artifact].method([lava_db_path], category_folder, seeker, wrap_text, time_offset)
                            else:
                                _run_plugin_subprocess(unifed_log_artifact, [lava_db_path], category_folder, {})
            except Exception as ex:  # pylint: disable=broad-exception-caught
                logfunc('Reading {} artifact had errors!'.format(plugin.name))
                logfunc('Error was {}'.format(str(ex)))
                logfunc('Exception Traceback: {}'.format(traceback.format_exc()))
                continue  # nope
        else:
            logfunc("No file found")
        logfunc('{} [{}] artifact completed'.format(plugin.name, plugin.module_name))
        parsed_modules += 1
        GuiWindow.SetProgressBar(parsed_modules, len(plugins))
        log.flush()
    log.close()

    write_device_info()
    if lava_only:
        write_lava_only_log()
    logfunc('')
    logfunc('Processes completed.')
    end = process_time()
    end_wall = perf_counter()
    run_time_secs =  end - start
    run_time_HMS = strftime('%H:%M:%S', gmtime(run_time_secs))
    logfunc("Processing time = {}".format(run_time_HMS))
    run_time_secs =  end_wall - start_wall
    run_time_HMS = strftime('%H:%M:%S', gmtime(run_time_secs))
    logfunc("Processing time (wall)= {}".format(run_time_HMS))

    logfunc('')
    logfunc('Report generation started.')
    # remove the \\?\ prefix we added to input and output paths, so it does not reflect in report
    if is_platform_windows():
        if out_params.output_folder_base.startswith('\\\\?\\'):
            out_params.output_folder_base = out_params.output_folder_base[4:]
        if input_path.startswith('\\\\?\\'):
            input_path = input_path[4:]

    report.generate_report(out_params.output_folder_base, run_time_secs, run_time_HMS, extracttype, input_path, casedata, profile_filename, icons, lava_only)
    logfunc('Report generation Completed.')

    # Record the run in history
    lava_project_path = os.path.join(out_params.output_folder_base, lava_json_name)
    history.record_recent_run(leapp_name.lower(), leapp_version, lava_project_path)

    logfunc('')
    logfunc(f'Report location: {out_params.output_folder_base}')

    return True

if __name__ == '__main__':
    main()
