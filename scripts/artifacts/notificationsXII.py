import os
import glob
import nska_deserialize as nd

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

def get_bundle_id_and_names_from_plist(library_plist_file_path):
    '''Parses Library.plist and returns a dictionary where Key=Bundle_ID, Value=Bundle_Name'''
    bundle_info = {}
    f = open(library_plist_file_path, 'rb')
    plist = nd.deserialize_plist(f)
    for k, v in plist.items():
        bundle_info[v] = k
    f.close()
    return bundle_info

def get_bundle_info(files_found):

    for file_path in files_found:
        file_path = str(file_path)
        if file_path.endswith('Library.plist') and os.path.dirname(file_path).endswith('UserNotificationsServer'):
            bundle_info = get_bundle_id_and_names_from_plist(file_path)
            return bundle_info
        # If this is fs search, then only top level folder will be present, so append path and search it too
        if file_path.endswith('UserNotificationsServer'):
            plist_file_path = os.path.join(file_path, 'Library.plist')
            if os.path.exists(plist_file_path):
                bundle_info = get_bundle_id_and_names_from_plist(plist_file_path)
                return bundle_info
    return {}

def get_notificationsXII(files_found, report_folder, seeker, wrap_text, timezone_offset):

    bundle_info = get_bundle_info(files_found)
    data_list = []
    exportedbplistcount = 0

    pathfound = str(files_found[0])
    # logfunc(f'Posix to string is: {pathfound}')
    for filepath in glob.iglob(pathfound + "/**", recursive=True):
        # create directory where script is running from
        if os.path.isfile(filepath):  # filter dirs
            file_name = os.path.splitext(os.path.basename(filepath))[0]
            # create directory
            if filepath.endswith('DeliveredNotifications.plist'):
                bundle_id = os.path.basename(os.path.dirname(filepath))
                # open the plist
                p = open(filepath, "rb")
                plist = nd.deserialize_plist(p)
                
                # Empty plist will be { 'root': None }
                if isinstance(plist, dict):
                    continue # skip it, it's empty
                
                # Good plist will be a list of dicts
                for item in plist:
                    creation_date = ''
                    title = ''
                    subtitle = ''
                    message = ''
                    other_dict = {}
                    bundle_name = bundle_info.get(bundle_id, bundle_id)
                    #if bundle_name == 'com.apple.ScreenTimeNotifications':
                    #    pass # has embedded plist!
                    for k, v in item.items():
                        if k == 'AppNotificationCreationDate': creation_date = str(v)
                        elif k == 'AppNotificationMessage': message = v
                        elif k == 'AppNotificationTitle': title = v
                        elif k == 'AppNotificationSubtitle': subtitle = v
                        else:
                            if isinstance(v, bytes):
                                logfunc(f'Found binary data, look into this one later k={k}!')
                            elif isinstance(v, dict):
                                pass # recurse look for plists #TODO
                            elif isinstance(v, list):
                                pass # recurse look for plists #TODO
                            other_dict[k] = str(v)
                    if subtitle:
                        title += f'[{subtitle}]'
                    data_list.append((creation_date, bundle_name, title, message, str(other_dict)))
                p.close()
                
            elif "AttachmentsList" in file_name:
                pass  # future development

    description = 'iOS > 12 Notifications'
    report = ArtifactHtmlReport('iOS Notificatons')
    report.start_artifact_report(report_folder, 'iOS Notifications', description)
    report.add_script()
    data_headers = ('Creation Time', 'Bundle', 'Title[Subtitle]', 'Message', 'Other Details')
    report.write_artifact_data_table(data_headers, data_list, filepath)
    report.end_artifact_report()

    logfunc("Total notifications processed:" + str(len(data_list)))
    #logfunc("Total exported bplists from notifications:" + str(exportedbplistcount))
    
    tsvname = 'Notifications'
    tsv(report_folder, data_headers, data_list, tsvname)

    tlactivity = 'Notifications'
    timeline(report_folder, tlactivity, data_list, data_headers)
    if len(data_list) == 0:
        logfunc("No notifications found.")

__artifacts__ = {
    "notificationsXII": (
        "Notifications",
        ('*/mobile/Library/UserNotifications*'),
        get_notificationsXII)
}