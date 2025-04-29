import json
import argparse
import io
import pytz
import os.path
import typing
import scripts.report as report
import traceback
import sys

import scripts.plugin_loader as plugin_loader

from scripts.search_files import *
from scripts.ilapfuncs import *
from scripts.version_info import ileapp_version
from time import process_time, gmtime, strftime, perf_counter
from scripts.lavafuncs import *

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
        raise argparse.ArgumentError(None, 'INPUT file/folder does not exist! Run the program again.')

    if not os.path.exists(args.output_path):
        raise argparse.ArgumentError(None, 'OUTPUT folder does not exist! Run the program again.')

    if args.load_case_data and not os.path.exists(args.load_case_data):
        raise argparse.ArgumentError(None, 'LEAPP Case Data file not found! Run the program again.')

    if args.load_profile and not os.path.exists(args.load_profile):
        raise argparse.ArgumentError(None, 'iLEAPP Profile file not found! Run the program again.')

    try:
        timezone = pytz.timezone(args.timezone)
    except pytz.UnknownTimeZoneError:
      raise argparse.ArgumentError(None, 'Unknown timezone! Run the program again.')
        

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
    parser = argparse.ArgumentParser(description='iLEAPP: iOS Logs, Events, And Plists Parser.')
    parser.add_argument('-t', choices=['fs', 'tar', 'zip', 'gz', 'itunes'], required=False, action="store",
                        help=("Specify the input type. "
                              "'fs' for a folder containing extracted files with normal paths and names, "
                              "'tar', 'zip', or 'gz' for compressed packages containing files with normal names, "
                              "'itunes' for a folder containing a raw iTunes backup with hashed paths and names."))
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

    loader = plugin_loader.PluginLoader()
    available_plugins = list(loader.plugins)
    profile_filename = None
    casedata = {}

    # Check if no arguments were provided
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit()

    args = parser.parse_args()

    extracttype = args.t

    plugins = []
    plugins_parsed_first = []

    for plugin in available_plugins:
        if plugin.module_name == 'lastBuild':
            if extracttype == 'itunes':
                continue
            else:
                plugins_parsed_first.append(plugin)
        elif plugin.module_name != 'iTunesBackupInfo':
            plugins.append(plugin)

    selected_plugins = plugins.copy()

    try:
        validate_args(args)
    except argparse.ArgumentError as e:
        parser.error(str(e))

    if args.artifact_paths:
        print('Artifact path list generation started.')
        print('')
        with open('path_list.txt', 'a') as paths:
            for plugin in loader.plugins:
                if isinstance(plugin.search, tuple):
                    for x in plugin.search:
                        paths.write(x + '\n')
                        print(x)
                else:  # TODO check that this is actually a string?
                    paths.write(plugin.search + '\n')
                    print(plugin.search)
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
                    create_profile(plugins, args.create_profile_casedata)
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
            except:
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
            except:
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
                    selected_plugins = [selected_plugin for selected_plugin in plugins 
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

    # ios file system extractions contain paths > 260 char, which causes problems
    # This fixes the problem by prefixing \\?\ on each windows path.
    if is_platform_windows():
        if input_path[1] == ':' and extracttype =='fs': input_path = '\\\\?\\' + input_path.replace('/', '\\')
        if output_path[1] == ':': output_path = '\\\\?\\' + output_path.replace('/', '\\')

    out_params = OutputParameters(output_path, custom_output_folder)

    selected_plugins = plugins_parsed_first + selected_plugins
    
    initialize_lava(input_path, out_params.report_folder_base, extracttype)

    crunch_artifacts(selected_plugins, extracttype, input_path, out_params, wrap_text, loader, casedata, time_offset, profile_filename)

    lava_finalize_output(out_params.report_folder_base)

def crunch_artifacts(
        plugins: typing.Sequence[plugin_loader.PluginSpec], extracttype, input_path, out_params, wrap_text,
        loader: plugin_loader.PluginLoader, casedata, time_offset, profile_filename):
    start = process_time()
    start_wall = perf_counter()
 
    logfunc('Processing started. Please wait. This may take a few minutes...')

    logfunc('\n--------------------------------------------------------------------------------------')
    logfunc(f'iLEAPP v{ileapp_version}: iOS Logs, Events, And Plists Parser')
    logfunc('Objective: Triage iOS Full File System and iTunes Backup Extractions.')
    logfunc('By: Alexis Brignoni | @AlexisBrignoni | abrignoni.com')
    logfunc('By: Yogesh Khatri   | @SwiftForensics | swiftforensics.com\n')
    logdevinfo()
    
    seeker = None
    try:
        if extracttype == 'fs':
            seeker = FileSeekerDir(input_path, out_params.data_folder)

        elif extracttype in ('tar', 'gz'):
            seeker = FileSeekerTar(input_path, out_params.data_folder)

        elif extracttype == 'zip':
            seeker = FileSeekerZip(input_path, out_params.data_folder)

        elif extracttype == 'itunes':
            seeker = FileSeekerItunes(input_path, out_params.data_folder)

        else:
            logfunc('Error on argument -o (input type)')
            return False
    except Exception as ex:
        logfunc('Had an exception in Seeker - see details below. Terminating Program!')
        temp_file = io.StringIO()
        traceback.print_exc(file=temp_file)
        logfunc(temp_file.getvalue())
        temp_file.close()
        return False

    # Now ready to run
    logfunc(f'Info: {len(loader) - 2} modules loaded.') # excluding lastbuild and iTunesBackupInfo
    if profile_filename:
        logfunc(f'Loaded profile: {profile_filename}')
    artifact_to_parse = len(plugins) - 1 if extracttype != 'itunes' else len(plugins) 
    logfunc(f'Artifact to parse: {artifact_to_parse}')
    logfunc(f'File/Directory selected: {input_path}')
    logfunc('\n--------------------------------------------------------------------------------------')

    log = open(os.path.join(out_params.report_folder_base, 'Script Logs', 'ProcessedFilesLog.html'), 'w+', encoding='utf8')
    log.write(f'Extraction/Path selected: {input_path}<br><br>')
    log.write(f'Timezone selected: {time_offset}<br><br>')
    
    parsed_modules = 0
    # Special processing for iTunesBackup Info.plist as it is a seperate entity, not part of the Manifest.db. Seeker won't find it
    if extracttype == 'itunes':
        info_plist_path = os.path.join(input_path, 'Info.plist')
        if os.path.exists(info_plist_path):
            # process_artifact([info_plist_path], 'iTunesBackupInfo', 'Device Info', seeker, out_params.report_folder_base)
            #plugin.method([info_plist_path], out_params.report_folder_base, seeker, wrap_text)
            report_folder = os.path.join(out_params.report_folder_base, '_HTML', 'iTunes Backup')
            if not os.path.exists(report_folder):
                try:
                    os.makedirs(report_folder)
                except (FileExistsError, FileNotFoundError) as ex:
                    logfunc('Error creating report directory at path {}'.format(report_folder))
                    logfunc('Error was {}'.format(str(ex)))
            loader["iTunesBackupInfo"].method([info_plist_path], report_folder, seeker, wrap_text, time_offset)
            report_folder = os.path.join(out_params.report_folder_base, '_HTML', 'Installed Apps')
            if not os.path.exists(report_folder):
                try:
                    os.makedirs(report_folder)
                except (FileExistsError, FileNotFoundError) as ex:
                    logfunc('Error creating report directory at path {}'.format(report_folder))
                    logfunc('Error was {}'.format(str(ex)))
            loader["iTunesBackupInstalledApplications"].method([info_plist_path], report_folder, seeker, wrap_text, time_offset)
            #del search_list['lastBuild'] # removing lastBuild as this takes its place
            print([info_plist_path])  # TODO Remove special consideration for itunes? Merge into main search
        else:
            logfunc('Info.plist not found for iTunes Backup!')
            log.write('Info.plist not found for iTunes Backup!')

    # Search for the files per the arguments
    for plugin in plugins:
        logfunc()
        logfunc('{} [{}] artifact started'.format(plugin.name, plugin.module_name))
        if isinstance(plugin.search, list) or isinstance(plugin.search, tuple):
            search_regexes = plugin.search
        else:
            search_regexes = [plugin.search]
        parsed_modules += 1
        GuiWindow.SetProgressBar(parsed_modules, len(plugins))
        files_found = []
        log.write(f'<b>For {plugin.name} module</b>')
        for artifact_search_regex in search_regexes:
            found = seeker.search(artifact_search_regex)
            if not found:
                log.write(f'<ul><li>No file found for regex <i>{artifact_search_regex}</i></li></ul>')
            else:
                log.write(f'<ul><li>{len(found)} {"files" if len(found) > 1 else "file"} for regex <i>{artifact_search_regex}</i> located at:')
                for pathh in found:
                    if pathh.startswith('\\\\?\\'):
                        pathh = pathh[4:]
                    log.write(f'<ul><li>{pathh}</li></ul>')
                log.write(f'</li></ul>')
                files_found.extend(found)
        if files_found:
            category_folder = os.path.join(out_params.report_folder_base, '_HTML', plugin.category)
            if not os.path.exists(category_folder):
                try:
                    os.makedirs(category_folder)
                except (FileExistsError, FileNotFoundError) as ex:
                    logfunc('Error creating {} report directory at path {}'.format(plugin.name, category_folder))
                    logfunc('Error was {}'.format(str(ex)))
                    continue  # cannot do work
            try:
                artifact_data = plugin.method(files_found, category_folder, seeker, wrap_text, time_offset)
            except Exception as ex:
                logfunc('Reading {} artifact had errors!'.format(plugin.name))
                logfunc('Error was {}'.format(str(ex)))
                logfunc('Exception Traceback: {}'.format(traceback.format_exc()))
                continue  # nope
        else:
            logfunc(f"No file found")
        logfunc('{} [{}] artifact completed'.format(plugin.name, plugin.module_name))
    log.close()

    write_device_info()
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
        if out_params.report_folder_base.startswith('\\\\?\\'):
            out_params.report_folder_base = out_params.report_folder_base[4:]
        if input_path.startswith('\\\\?\\'):
            input_path = input_path[4:]
    
    report.generate_report(out_params.report_folder_base, run_time_secs, run_time_HMS, extracttype, input_path, casedata, profile_filename, icons)
    logfunc('Report generation Completed.')
    logfunc('')
    logfunc(f'Report location: {out_params.report_folder_base}')

    return True

if __name__ == '__main__':
    main()
    
