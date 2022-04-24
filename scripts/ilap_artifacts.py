# To add a new artifact module, import it here as shown below:
#     from scripts.artifacts.fruitninja import get_fruitninja
# Also add the grep search for that module using the same name
# to the 'tosearch' data structure.

import traceback

from time import process_time, gmtime, strftime

from scripts.artifacts.lastBuild import get_lastBuild, get_iTunesBackupInfo

from scripts.artifacts.routineD import get_routineD

from scripts.ilapfuncs import *

# GREP searches for each module
# Format is Key='modulename', Value=Tuple('Module Pretty Name', 'regex term')
#   regex_term can be a string or a list/tuple of strings
# Here modulename must match the get_xxxxxx function name for that module. 
# For example: If modulename='profit', function name must be get_profit(..)
# Don't forget to import the module above!!!!


tosearch = {'lastBuild': ('IOS Build', '*LastBuildInfo.plist'),
            'routineD': ('Locations', ('*/var/mobile/Library/Caches/com.apple.routined/Cache.sqlite', '*/var/mobile/Library/Caches/com.apple.routined/Local.sqlite','*/var/mobile/Library/Caches/com.apple.routined/Cloud.sqlite')),
            }

'''
#    Artifacts take long to run. Useful in specific situations only.
#    'aggDict':('Aggregate Dictionary', '*/AggregateDictionary/ADDataStore.sqlitedb')
#    'aggDictScalars':('Aggregate Dictionary', '*/AggregateDictionary/ADDataStore.sqlitedb')
'''

slash = '\\' if is_platform_windows() else '/'


def process_artifact(files_found, artifact_func, artifact_name, seeker, report_folder_base):
    ''' Perform the common setup for each artifact, ie, 
        1. Create the report folder for it
        2. Fetch the method (function) and call it
        3. Wrap processing function in a try..except block

        Args:
            files_found: list of files that matched regex

            artifact_func: method to call

            artifact_name: Pretty name of artifact

            seeker: FileSeeker object to pass to method
    '''
    start_time = process_time()
    logfunc('{} [{}] artifact executing'.format(artifact_name, artifact_func))
    report_folder = os.path.join(report_folder_base, artifact_name) + slash
    try:
        if os.path.isdir(report_folder):
            pass
        else:
            os.makedirs(report_folder)
    except Exception as ex:
        logfunc('Error creating {} report directory at path {}'.format(artifact_name, report_folder))
        logfunc('Reading {} artifact failed!'.format(artifact_name))
        logfunc('Error was {}'.format(str(ex)))
        return
    try:
        method = globals()['get_' + artifact_func]
        method(files_found, report_folder, seeker)
    except Exception as ex:
        logfunc('Reading {} artifact had errors!'.format(artifact_name))
        logfunc('Error was {}'.format(str(ex)))
        logfunc('Exception Traceback: {}'.format(traceback.format_exc()))
        return

    end_time = process_time()
    run_time_secs = end_time - start_time
    # run_time_HMS = strftime('%H:%M:%S', gmtime(run_time_secs))
    logfunc('{} [{}] artifact completed in time {} seconds'.format(artifact_name, artifact_func, run_time_secs))