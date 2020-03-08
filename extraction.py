from common import logfunc

tosearch = {
    "mib": "*mobile_installation.log.*",
    "iconstate": "*SpringBoard/IconState.plist",
    "webclips": "*WebClips/*.webclip/*",
    "lastbuild": "*LastBuildInfo.plist",
    "iOSNotifications11": "*PushStore*",
    "iOSNotifications12": "*private/var/mobile/Library/UserNotifications*",
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

def pre_extraction():
    logfunc(
        "\n--------------------------------------------------------------------------------------"
    )
    logfunc("iLEAPP: iOS Logs, Events, and Preferences Parser")
    logfunc("Objective: Triage iOS Full System Extractions.")
    logfunc("By: Alexis Brignoni | @AlexisBrignoni | abrignoni.com")

    logfunc(f"Artifact categories to parse: {str(len(tosearch))}")
    logfunc(f"File/Directory selected: {pathto}")
    logfunc(
        "\n--------------------------------------------------------------------------------------"
    )
    logfunc()

    log = open(
        reportfolderbase + "Script Logs/ProcessedFilesLog.html", "w+", encoding="utf8"
    )
    nl = "\n"  # literal in order to have new lines in fstrings that create text files
    log.write(f"Extraction/Path selected: {pathto}<br><br>")
    return log

def process_file_found(filefound, key, val):
    if not filefound:
        logfunc()
        logfunc(f"No files found for {key} -> {val}.")
        log.write(f"No files found for {key} -> {val}.<br>")
        return

    logfunc()

    globals()[key](filefound)

    for pathh in filefound:
        log.write(f"Files for {val} located at {pathh}.<br>")


def calculate_time(start_time):
    end = process_time()
    time = start - end
    logfunc("Processing time: " + str(abs(time)))
    return time

def post_extraction(start_time):
    logfunc("")
    logfunc("Processes completed.")

    calculate_time(start_time)

    fname = os.path.join(report_folder_base, "Script Logs","ProcessedFilesLog.html")

    with open(fname, "a", encoding="utf8") as processed_file_log:
        processed_file_log.write(f"Processing time in secs: {str(abs(time))}")

    logfunc("")
    logfunc("Report generation started.")

    report(reportfolderbase, time, extracttype, pathto)

    logfunc("Report generation Completed.")
    logfunc("")
    logfunc(f"Report name: {reportfolderbase}")

