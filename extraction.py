import os
import tarfile
from tarfile import TarFile
from zipfile import ZipFile

import filetype

from ilapfuncs import *
from report import *
from search_files import *
from settings import report_folder_base


SUPPORTED_EXTENSIONS = ["fs", "zip", "tar"]

tosearch = {
    "mib": "*mobile_installation.log.*",
    "iconstate": "*SpringBoard/IconState.plist",
    "webclips": "*WebClips/*.webclip/*",
    "lastbuild": "*LastBuildInfo.plist",
    "iOSNotifications11": "*PushStore*",
    "iOSNotifications12": "*private/var/mobile/Library/UserNotifications/",
    "wireless": "*wireless/Library/Preferences/com.apple.*",
    "knowledgec": "*CoreDuet/Knowledge/knowledgeC.db",
    "applicationstate": "*pplicationState.db*",
    "conndevices": "*/iTunes_Control/iTunes/iTunesPrefs",
    "calhist": "*CallHistory.storedata",
    "smschat": "*sms.db",
    "safari": "*History.db",
    "queryp": "*query_predictions.db",
    "powerlog": "*CurrentPowerlog.PLSQL",
    "accs": "*Accounts3.sqlite",
    "medlib": "*MediaLibrary.sqlitedb",
    "datausage": "*DataUsage.sqlite",
    "delphotos": "*Photos.sqlite",
    "timezone": "*mobile/Library/Preferences/com.apple.preferences.datetime.plist",
    "bkupstate": "*/com.apple.MobileBackup.plist",
    "mobilact": "*mobileactivationd.log.*",
    "healthdb": "*healthdb_secure.sqlite",
    "datark": "*Library/Lockdown/data_ark.plist",
    "wiloc": "*cache_encryptedB.db",
    "aggdict": "*AggregateDictionary/ADDataStore.sqlitedb",
    "dbbuff": "*AggregateDictionary/dbbuffer",
    "confaccts": "*com.apple.accounts.exists.plist",
    "calendar": "*Calendar.sqlitedb",
    "mailprotect": "*private/var/mobile/Library/Mail/* Index*",
    "screentime": "*/Library/Application Support/com.apple.remotemanagementd/RMAdminStore*",
    "bluetooths": "*/Library/Database/com.apple.MobileBluetooth*",
    "whatsapp": "*ChatStorage.sqlite",
    "ipscl": "*.ips",
    "wapcontact": "*ContactsV2.sqlite",
    "actrec": "*activation_record.plist",
    "DHCPhp": "*private/var/db/dhcpd_leases*",
    "DHCPL": "*private/var/db/dhcpclient/leases/en*",
    "redditusers": "*Data/Application/*/Documents/*/accounts/*",
    "redditchats": "*Data/Application/*/Documents/*/accountData/*/chat/*/chat.sqlite",
    "interactionc": "*interactionC.db",
}


class UnsupportedFileType(Exception):
    pass


def get_filetype(fpath: str) -> str:
    """
    Returns a string with the extension of the library received.

    Raises:
       UnsupportedFileType: if the file type is not supported by iLEAPP
            or cannot be guessed.

    Leverages the `filetype` library:
        https://github.com/h2non/filetype.py
    """
    if not os.path.isdir(fpath):
        try:
            inferred_filetype = filetype.guess(fpath)

        except Exception as e:
            raise e

        if inferred_filetype is None:
            raise UnsupportedFileType(f"Could not detect file type for {fpath}")

        extension = inferred_filetype.extension

        if extension not in SUPPORTED_EXTENSIONS:
            raise UnsupportedFileType(
                f"Detected file type {extension} for file {fpath} not supported"
                f" by iLEAPP.\nFile types supported are: {SUPPORTED_EXTENSIONS}"
            )

        return extension
    else:
        return "fs"


def extract_and_process(pathto, extraction_type, tosearch, log, gui_window=None):
    if extraction_type != "fs":
        search_func = search_archive
    else:
        search_func = search

    if extraction_type == "tar":
        pathto = TarFile(pathto)

    if extraction_type == "zip":
        pathto = ZipFile(pathto)

    for key, val in tosearch.items():
        filefound = search_func(pathto, val)
        process_file_found(filefound, key, val, log, gui_window)

    if extraction_type == "zip":
        pathto.close()

    log.close()


def pre_extraction(pathto, gui_window=None):
    os.makedirs(report_folder_base)
    os.makedirs(report_folder_base + "Script Logs")
    logfunc("Procesing started. Please wait. This may take a few minutes...")

    if gui_window is not None:
        gui_window.refresh()

    logfunc(
        "\n--------------------------------------------------------------------------------------"
    )
    logfunc("iLEAPP: iOS Logs, Events, and Preferences Parser")
    logfunc("Objective: Triage iOS Full System Extractions.")
    logfunc("By: Agam Dua | @loopbackdev | loopback.dev")
    logfunc("By: Alexis Brignoni | @AlexisBrignoni | abrignoni.com")

    logfunc(f"Artifact categories to parse: {str(len(tosearch))}")
    logfunc(f"File/Directory selected: {pathto}")
    logfunc(
        "\n--------------------------------------------------------------------------------------"
    )
    logfunc()

    if gui_window is not None:
        gui_window.refresh()

    log = open(
        report_folder_base + "Script Logs/ProcessedFilesLog.html", "w+", encoding="utf8"
    )
    nl = "\n"  # literal in order to have new lines in fstrings that create text files
    log.write(f"Extraction/Path selected: {pathto}<br><br>")
    return log


def process_file_found(filefound, key, val, log, gui_window=None):
    if not filefound:
        if gui_window is not None:
            gui_window.refresh()
        logfunc()
        logfunc(f"No files found for {key} -> {val}.")
        log.write(f"No files found for {key} -> {val}.<br>")
        return

    logfunc()

    if gui_window is not None:
        gui_window.refresh()

    globals()[key](filefound)

    for path in filefound:
        log.write(f"Files for {val} located at {path}.<br>")


def calculate_time(start_time):
    end_time = process_time()
    time_difference = start_time - end_time
    logfunc("Processing time: " + str(abs(time_difference)))
    return time_difference


def generate_report(report_folder_base, running_time, extracttype, pathto):
    logfunc("")
    logfunc("Report generation started.")

    report(report_folder_base, running_time, extracttype, pathto)

    logfunc("Report generation Completed.")
    logfunc("")
    logfunc(f"Report name: {report_folder_base}")


def post_extraction(start_time, extracttype, pathto):
    logfunc("")
    logfunc("Processes completed.")

    running_time = calculate_time(start_time)

    fname = os.path.join(report_folder_base, "Script Logs", "ProcessedFilesLog.html")

    with open(fname, "a", encoding="utf8") as processed_file_log:
        processed_file_log.write(f"Processing time in secs: {str(abs(running_time))}")

    generate_report(report_folder_base, running_time, extracttype, pathto)
