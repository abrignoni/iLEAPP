import argparse
import io
import os
import scripts.report as report
import shutil
import traceback

from scripts.search_files import *
from scripts.ilapfuncs import *
from scripts.ilap_artifacts import *
from scripts.version_info import aleapp_version
from time import process_time, gmtime, strftime

def main():
    parser = argparse.ArgumentParser(description='iLEAPP: iOS Logs, Events, and Plists Parser.')
    parser.add_argument('-t', choices=['fs','tar','zip', 'gz', 'itunes'], required=False, action="store", help="Input type (fs = extracted to file system folder)")
    parser.add_argument('-o', '--output_path', required=False, action="store", help='Output folder path')
    parser.add_argument('-i', '--input_path', required=False, action="store", help='Path to input file/folder')
    parser.add_argument('-p', '--artifact_paths', required=False, action="store_true", help='Text file list of artifact paths')
        
    args = parser.parse_args()
    
    if args.artifact_paths == True:
        print('Artifact path list generation started.')
        print('')
        with open('path_list.txt', 'a') as paths:
            for key, value in tosearch.items():
                if type(value[1]) is tuple:
                    for x in value[1]:
                        paths.write(x+'\n')
                        print(x)
                else:
                    paths.write(value[1]+'\n')
                    print(value[1])
        print('')
        print('Artifact path list generation completed')    
        return

    else:
        input_path = args.input_path
        extracttype = args.t
        
        if args.output_path == None:
            parser.error('No OUTPUT folder path provided')
            return
        else:
            output_path = os.path.abspath(args.output_path)
        
        if output_path == None:
            parser.error('No OUTPUT folder selected. Run the program again.')
            return
            
        if input_path == None:
            parser.error('No INPUT file or folder selected. Run the program again.')
            return
        
        if args.t == None:
            parser.error('No INPUT file or folder selected. Run the program again.')
            return

        if not os.path.exists(input_path):
            parser.error('INPUT file/folder does not exist! Run the program again.')
            return
        
        if not os.path.exists(output_path):
            parser.error('OUTPUT folder does not exist! Run the program again.')
            return  

        # ios file system extractions contain paths > 260 char, which causes problems
        # This fixes the problem by prefixing \\?\ on each windows path.
        if is_platform_windows():
            if input_path[1] == ':' and extracttype =='fs': input_path = '\\\\?\\' + input_path.replace('/', '\\')
            if output_path[1] == ':': output_path = '\\\\?\\' + output_path.replace('/', '\\')

        out_params = OutputParameters(output_path)

        crunch_artifacts(tosearch, extracttype, input_path, out_params, 1)

def crunch_artifacts(search_list, extracttype, input_path, out_params, ratio):
    '''Returns true/false on success/failure'''
    start = process_time()

    logfunc('Procesing started. Please wait. This may take a few minutes...')

    logfunc('\n--------------------------------------------------------------------------------------')
    logfunc(f'iLEAPP v{aleapp_version}: iLEAPP Logs, Events, and Properties Parser')
    logfunc('Objective: Triage iOS Full System Extractions.')
    logfunc('By: Alexis Brignoni | @AlexisBrignoni | abrignoni.com')
    logfunc('By: Yogesh Khatri   | @SwiftForensics | swiftforensics.com')
    logdevinfo()
    
    seeker = None
    try:
        if extracttype == 'fs':
            seeker = FileSeekerDir(input_path)

        elif extracttype in ('tar', 'gz'):
            seeker = FileSeekerTar(input_path, out_params.temp_folder)

        elif extracttype == 'zip':
            seeker = FileSeekerZip(input_path, out_params.temp_folder)

        elif extracttype == 'itunes':
            seeker = FileSeekerItunes(input_path, out_params.temp_folder)

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
    logfunc(f'Artifact categories to parse: {str(len(search_list))}')
    logfunc(f'File/Directory selected: {input_path}')
    logfunc('\n--------------------------------------------------------------------------------------')

    log = open(os.path.join(out_params.report_folder_base, 'Script Logs', 'ProcessedFilesLog.html'), 'w+', encoding='utf8')
    nl = '\n' #literal in order to have new lines in fstrings that create text files
    log.write(f'Extraction/Path selected: {input_path}<br><br>')
    
    categories_searched = 0
    # Special processing for iTunesBackup Info.plist as it is a seperate entity, not part of the Manifest.db. Seeker won't find it
    if extracttype == 'itunes':
        info_plist_path = os.path.join(input_path, 'Info.plist')
        if os.path.exists(info_plist_path):
            process_artifact([info_plist_path], 'iTunesBackupInfo', 'Device Info', seeker, out_params.report_folder_base)
            del search_list['lastBuild'] # removing lastBuild as this takes its place
        else:
            logfunc('Info.plist not found for iTunes Backup!')
            log.write('Info.plist not found for iTunes Backup!')
        categories_searched += 1
        GuiWindow.SetProgressBar(categories_searched * ratio)

    # Search for the files per the arguments
    for key, val in search_list.items():
        search_regexes = []
        artifact_pretty_name = val[0]
        if isinstance(val[1], list) or isinstance(val[1], tuple):
            search_regexes = val[1]
        else:
            search_regexes.append(val[1])
        files_found = []
        for artifact_search_regex in search_regexes:
            found = seeker.search(artifact_search_regex)
            if not found:
                logfunc()
                logfunc(f'No files found for {key} -> {artifact_search_regex}')
                log.write(f'No files found for {key} -> {artifact_search_regex}<br><br>')
            else:
                files_found.extend(found)
        if files_found:
            logfunc()
            process_artifact(files_found, key, artifact_pretty_name, seeker, out_params.report_folder_base)
            for pathh in files_found:
                if pathh.startswith('\\\\?\\'):
                    pathh = pathh[4:]
                log.write(f'Files for {artifact_search_regex} located at {pathh}<br><br>')
        categories_searched += 1
        GuiWindow.SetProgressBar(categories_searched * ratio)
    log.close()

    logfunc('')
    logfunc('Processes completed.')
    end = process_time()
    run_time_secs =  end - start
    run_time_HMS = strftime('%H:%M:%S', gmtime(run_time_secs))
    logfunc("Processing time = {}".format(run_time_HMS))

    logfunc('')
    logfunc('Report generation started.')
    # remove the \\?\ prefix we added to input and output paths, so it does not reflect in report
    if is_platform_windows(): 
        if out_params.report_folder_base.startswith('\\\\?\\'):
            out_params.report_folder_base = out_params.report_folder_base[4:]
        if input_path.startswith('\\\\?\\'):
            input_path = input_path[4:]
    report.generate_report(out_params.report_folder_base, run_time_secs, run_time_HMS, extracttype, input_path)
    logfunc('Report generation Completed.')
    logfunc('')
    logfunc(f'Report location: {out_params.report_folder_base}')
    return True

if __name__ == '__main__':
    main()
