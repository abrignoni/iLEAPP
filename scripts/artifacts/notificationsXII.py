import os
import glob
import nska_deserialize as nd

from scripts.ilapfuncs import logfunc, artifact_processor


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


@artifact_processor
def get_notificationsXII(files_found, report_folder, seeker, wrap_text, timezone_offset):

    bundle_info = get_bundle_info(files_found)
    data_list = []

    pathfound = str(files_found[0])
    filepath = pathfound
    for filepath in glob.iglob(pathfound + "/**", recursive=True):
        if os.path.isfile(filepath):
            if filepath.endswith('DeliveredNotifications.plist'):
                bundle_id = os.path.basename(os.path.dirname(filepath))
                p = open(filepath, "rb")
                plist = nd.deserialize_plist(p)

                # Empty plist will be { 'root': None }
                if isinstance(plist, dict):
                    p.close()
                    continue

                # Good plist will be a list of dicts
                bundle_name = bundle_info.get(bundle_id, bundle_id)
                for item in plist:
                    creation_date = ''
                    title = ''
                    subtitle = ''
                    message = ''
                    other_dict = {}
                    for k, v in item.items():
                        if k == 'AppNotificationCreationDate':
                            creation_date = str(v)
                        elif k == 'AppNotificationMessage':
                            message = v
                        elif k == 'AppNotificationTitle':
                            title = v
                        elif k == 'AppNotificationSubtitle':
                            subtitle = v
                        else:
                            if isinstance(v, bytes):
                                logfunc(f'Found binary data, look into this one later k={k}!')
                            other_dict[k] = str(v)
                    if subtitle:
                        title += f'[{subtitle}]'
                    data_list.append((creation_date, bundle_name, title, message, str(other_dict)))
                p.close()

    data_headers = ('Creation Time', 'Bundle', 'Title[Subtitle]', 'Message', 'Other Details')
    return data_headers, data_list, pathfound

__artifacts_v2__ = {
    "get_notificationsXII": {
        "name": "Notifications iOS 12+",
        "description": "iOS 12+ delivered notifications.",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Notifications",
        "notes": "",
        "paths": ('*/mobile/Library/UserNotifications*',),
        "output_types": "standard",
        "artifact_icon": "bell"
    }
}
