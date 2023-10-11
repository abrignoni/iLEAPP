import os
import textwrap
import datetime
import sys
import re
import string
import sqlite3
from html import escape

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows


def month_converter(month):
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    month = months.index(month) + 1
    if month < 10:
        month = f"{month:02d}"
    return month


def day_converter(day):
    day = int(day)
    if day < 10:
        day = f"{day:02d}"
    return day


def get_mobileInstall(files_found, report_folder, seeker, wrap_text, timezone_offset):
    counter = 0
    filescounter = 0
    tsv_tml_data_list = []

    mibdatabase = os.path.join(report_folder, 'mib.db')
    db = sqlite3.connect(mibdatabase)
    cursor = db.cursor()
    cursor.execute(
        """
    CREATE TABLE dimm(time_stamp TEXT, action TEXT, bundle_id TEXT, path TEXT)
    """
    )

    db.commit()

    for filename in files_found:
        file = open(filename, "r", encoding="utf8")
        filescounter = filescounter + 1
        file_datainserts = []
        for line in file:
            counter = counter + 1
            matchObj = re.search(
                r"(Install Successful for)", line
            )  # Regex for installed applications
            if matchObj:
                actiondesc = "Install successful"
                matchObj1 = re.search(
                    r"(?<= for \(Placeholder:)(.*)(?=\))", line
                )  # Regex for bundle id
                matchObj2 = re.search(
                    r"(?<= for \(Customer:)(.*)(?=\))", line
                )  # Regex for bundle id
                matchObj3 = re.search(
                    r"(?<= for \(System:)(.*)(?=\))", line
                )  # Regex for bundle id
                matchObj4 = re.search(
                    r"(?<= for \()(.*)(?=\))", line
                )  # Regex for bundle id
                if matchObj1:
                    bundleid = matchObj1.group(1)
                elif matchObj2:
                    bundleid = matchObj2.group(1)
                elif matchObj3:
                    bundleid = matchObj3.group(1)
                elif matchObj4:
                    bundleid = matchObj4.group(1)

                matchObj = re.search(r"(?<=^)(.*)(?= \[)", line)  # Regex for timestamp
                if matchObj:
                    timestamp = matchObj.group(1)
                    weekday, month, day, time, year = str.split(timestamp)
                    day = day_converter(day)
                    month = month_converter(month)
                    inserttime = (
                            str(year) + "-" + str(month) + "-" + str(day) + " " + str(time)
                    )
                    # logfunc(inserttime)
                    # logfunc(month)
                    # logfunc(day)
                    # logfunc(year)
                    # logfunc(time)
                    # logfunc ("Timestamp: ", timestamp)

                # logfunc(inserttime, actiondesc, bundleid)

                # insert to database
                cursor = db.cursor()
                datainsert = (
                    inserttime,
                    actiondesc,
                    bundleid,
                    "",
                )
                # cursor.execute(
                #     "INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)",
                #     datainsert,
                # )
                # db.commit()
                file_datainserts.append(datainsert)
                path = ''
                tsv_tml_data_list.append((inserttime, actiondesc, bundleid, path))

                # logfunc()
            
            matchObj = re.search(
                r"(Destroying container )", line
            )  # Regex for destroyed containers
            if matchObj:
                actiondesc = "Destroying container"
                # logfunc(actiondesc)
                # logfunc("Destroyed containers:")
                matchObj = re.search(
                    r"(?<=identifier )(.*)(?= at )", line
                )  # Regex for bundle id
                if matchObj:
                    bundleid = matchObj.group(1)
                    # logfunc ("Bundle ID: ", bundleid )
                  
                matchObj = re.search(r"(?<=^)(.*)(?= \[)", line)  # Regex for timestamp
                if matchObj:
                    timestamp = matchObj.group(1)
                    weekday, month, day, time, year = str.split(timestamp)
                    day = day_converter(day)
                    month = month_converter(month)
                    inserttime = (
                            str(year) + "-" + str(month) + "-" + str(day) + " " + str(time)
                    )
                    # logfunc(inserttime)
                    # logfunc(month)
                    # logfunc(day)
                    # logfunc(year)
                    # logfunc(time)
                    # logfunc ("Timestamp: ", timestamp)
                  
                matchObj = re.search(r"(?<= at )(.*)(?=$)", line)  # Regex for path
                if matchObj:
                    path = matchObj.group(1)
                    # logfunc ("Path: ", matchObj.group(1))
                  
                # logfunc(inserttime, actiondesc, bundleid, path)
                  
                # insert to database
                cursor = db.cursor()
                datainsert = (
                    inserttime,
                    actiondesc,
                    bundleid,
                    path,
                )
                # cursor.execute(
                #     "INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)",
                #     datainsert,
                # )
                # db.commit()
                file_datainserts.append(datainsert)
              
                tsv_tml_data_list.append((inserttime, actiondesc, bundleid, path))
                # logfunc()
              
            matchObj = re.search(
                r"(Destroying container with identifier)", line
            )  # Regex for destroyed containers
            if matchObj:
                actiondesc = "Destroying container"
                # logfunc(actiondesc)
                # logfunc("Destroyed containers:")
                matchObj = re.search(
                    r"(?<=identifier )(.*)(?= at )", line
                )  # Regex for bundle id
                if matchObj:
                    bundleid = matchObj.group(1)
                    # logfunc ("Bundle ID: ", bundleid )

                matchObj = re.search(r"(?<=^)(.*)(?= \[)", line)  # Regex for timestamp
                if matchObj:
                    timestamp = matchObj.group(1)
                    weekday, month, day, time, year = str.split(timestamp)
                    day = day_converter(day)
                    month = month_converter(month)
                    inserttime = (
                            str(year) + "-" + str(month) + "-" + str(day) + " " + str(time)
                    )
                    # logfunc(inserttime)
                    # logfunc(month)
                    # logfunc(day)
                    # logfunc(year)
                    # logfunc(time)
                    # logfunc ("Timestamp: ", timestamp)

                matchObj = re.search(r"(?<= at )(.*)(?=$)", line)  # Regex for path
                if matchObj:
                    path = matchObj.group(1)
                    # logfunc ("Path: ", matchObj.group(1))

                # logfunc(inserttime, actiondesc, bundleid, path)

                # insert to database
                cursor = db.cursor()
                datainsert = (
                    inserttime,
                    actiondesc,
                    bundleid,
                    path,
                )
                # cursor.execute(
                #     "INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)",
                #     datainsert,
                # )
                # db.commit()
                file_datainserts.append(datainsert)

                tsv_tml_data_list.append((inserttime, actiondesc, bundleid, path))
                # logfunc()

            matchObj = re.search(
                r"(Data container for)", line
            )  # Regex Moved data containers
            if matchObj:
                actiondesc = "Data container moved"
                # logfunc(actiondesc)
                # logfunc("Data container moved:")
                matchObj = re.search(
                    r"(?<=for )(.*)(?= is now )", line
                )  # Regex for bundle id
                if matchObj:
                    bundleid = matchObj.group(1)
                    # logfunc ("Bundle ID: ", bundleid )

                matchObj = re.search(r"(?<=^)(.*)(?= \[)", line)  # Regex for timestamp
                if matchObj:
                    timestamp = matchObj.group(1)
                    weekday, month, day, time, year = str.split(timestamp)
                    day = day_converter(day)
                    month = month_converter(month)
                    inserttime = (
                            str(year) + "-" + str(month) + "-" + str(day) + " " + str(time)
                    )
                    # logfunc(inserttime)
                    # logfunc(month)
                    # logfunc(day)
                    # logfunc(year)
                    # logfunc(time)
                    # logfunc ("Timestamp: ", timestamp)

                matchObj = re.search(r"(?<= at )(.*)(?=$)", line)  # Regex for path
                if matchObj:
                    path = matchObj.group(1)
                    # logfunc ("Path: ", matchObj.group(1))

                # logfunc(inserttime, actiondesc, bundleid, path)

                # insert to database
                cursor = db.cursor()
                datainsert = (
                    inserttime,
                    actiondesc,
                    bundleid,
                    path,
                )
                # cursor.execute(
                #     "INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)",
                #     datainsert,
                # )
                # db.commit()
                file_datainserts.append(datainsert)

                tsv_tml_data_list.append((inserttime, actiondesc, bundleid, path))
                # logfunc()

            matchObj = re.search(
                r"(Made container live for)", line
            )  # Regex for made container
            if matchObj:
                actiondesc = "Made container live"
                # logfunc(actiondesc)
                # logfunc("Made container:")
                matchObj = re.search(
                    r"(?<=for )(.*)(?= at)", line
                )  # Regex for bundle id
                if matchObj:
                    bundleid = matchObj.group(1)
                    # logfunc ("Bundle ID: ", bundleid )

                matchObj = re.search(r"(?<=^)(.*)(?= \[)", line)  # Regex for timestamp
                if matchObj:
                    timestamp = matchObj.group(1)
                    weekday, month, day, time, year = str.split(timestamp)
                    day = day_converter(day)
                    month = month_converter(month)
                    inserttime = (
                            str(year) + "-" + str(month) + "-" + str(day) + " " + str(time)
                    )
                    # logfunc(inserttime)
                    # logfunc(month)
                    # logfunc(day)
                    # logfunc(year)
                    # logfunc(time)
                    # logfunc ("Timestamp: ", timestamp)

                matchObj = re.search(r"(?<= at )(.*)(?=$)", line)  # Regex for path
                if matchObj:
                    path = matchObj.group(1)
                    # logfunc ("Path: ", matchObj.group(1))
                # logfunc(inserttime, actiondesc, bundleid, path)

                # insert to database
                cursor = db.cursor()
                datainsert = (
                    inserttime,
                    actiondesc,
                    bundleid,
                    path,
                )
                # cursor.execute(
                #     "INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)",
                #     datainsert,
                # )
                # db.commit()
                file_datainserts.append(datainsert)

                tsv_tml_data_list.append((inserttime, actiondesc, bundleid, path))

            matchObj = re.search(
                r"(Uninstalling identifier )", line
            )  # Regex for made container
            if matchObj:
                actiondesc = "Uninstalling identifier"
                # logfunc(actiondesc)
                # logfunc("Uninstalling identifier")
                matchObj = re.search(
                    r"(?<=Uninstalling identifier )(.*)", line
                )  # Regex for bundle id
                if matchObj:
                    bundleid = matchObj.group(1)
                    # logfunc ("Bundle ID: ", bundleid )

                matchObj = re.search(r"(?<=^)(.*)(?= \[)", line)  # Regex for timestamp
                if matchObj:
                    timestamp = matchObj.group(1)
                    weekday, month, day, time, year = str.split(timestamp)
                    day = day_converter(day)
                    month = month_converter(month)
                    inserttime = (
                            str(year) + "-" + str(month) + "-" + str(day) + " " + str(time)
                    )
                    # logfunc(inserttime)
                    # logfunc(month)
                    # logfunc(day)
                    # logfunc(year)
                    # logfunc(time)
                    # logfunc ("Timestamp: ", timestamp)

                # insert to database
                cursor = db.cursor()
                datainsert = (
                    inserttime,
                    actiondesc,
                    bundleid,
                    "",
                )
                # cursor.execute( 
                #     "INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)",
                #     datainsert,
                # )
                # db.commit()
                file_datainserts.append(datainsert)

                tsv_tml_data_list.append((inserttime, actiondesc, bundleid, ''))

            matchObj = re.search(r"(main: Reboot detected)", line)  # Regex for reboots
            if matchObj:
                actiondesc = "Reboot detected"
                # logfunc(actiondesc)
                matchObj = re.search(r"(?<=^)(.*)(?= \[)", line)  # Regex for timestamp
                if matchObj:
                    timestamp = matchObj.group(1)
                    weekday, month, day, time, year = str.split(timestamp)
                    day = day_converter(day)
                    month = month_converter(month)
                    inserttime = (
                            str(year) + "-" + str(month) + "-" + str(day) + " " + str(time)
                    )
                    # logfunc(inserttime)
                    # logfunc(month)
                    # logfunc(day)
                    # logfunc(year)
                    # logfunc(time)
                    # logfunc ("Timestamp: ", timestamp)

                # insert to database
                cursor = db.cursor()
                datainsert = (
                    inserttime,
                    actiondesc,
                    "",
                    "",
                )
                # cursor.execute(
                #     "INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)",
                #     datainsert,
                # )
                # db.commit()
                file_datainserts.append(datainsert)

                tsv_tml_data_list.append((inserttime, actiondesc, bundleid, path))

            matchObj = re.search(
                r"(Attempting Delta patch update of )", line
            )  # Regex for Delta patch
            if matchObj:
                actiondesc = "Attempting Delta patch"
                # logfunc(actiondesc)
                # logfunc("Made container:")
                matchObj = re.search(
                    r"(?<=Attempting Delta patch update of )(.*)(?= from)", line
                )  # Regex for bundle id
                if matchObj:
                    bundleid = matchObj.group(1)
                    # logfunc ("Bundle ID: ", bundleid )

                matchObj = re.search(r"(?<=^)(.*)(?= \[)", line)  # Regex for timestamp
                if matchObj:
                    timestamp = matchObj.group(1)
                    weekday, month, day, time, year = str.split(timestamp)
                    day = day_converter(day)
                    month = month_converter(month)
                    inserttime = (
                            str(year) + "-" + str(month) + "-" + str(day) + " " + str(time)
                    )
                    # logfunc(inserttime)
                    # logfunc(month)
                    # logfunc(day)
                    # logfunc(year)
                    # logfunc(time)
                    # logfunc ("Timestamp: ", timestamp)

                matchObj = re.search(r"(?<= from )(.*)", line)  # Regex for path
                if matchObj:
                    path = matchObj.group(1)
                    # logfunc ("Path: ", matchObj.group(1))
                # logfunc(inserttime, actiondesc, bundleid, path)

                # insert to database
                cursor = db.cursor()
                datainsert = (
                    inserttime,
                    actiondesc,
                    bundleid,
                    path,
                )
                # cursor.execute(
                #     "INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)",
                #     datainsert,
                # )
                # db.commit()
                file_datainserts.append(datainsert)

                tsv_tml_data_list.append((inserttime, actiondesc, bundleid, path))
                # logfunc()
        # end for line in file:
        if file_datainserts:
            cursor.executemany(
                "INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)",
                file_datainserts,
            )
            db.commit()
        else:
            print("Had no commits to do...")

    logfunc(f"Logs processed: {filescounter}")
    logfunc(f"Lines processed: {counter}")
    logfunc("")
    file.close

    # Initialize counters
    totalapps = 0
    installedcount = 0
    uninstallcount = 0
    historicalcount = 0
    sysstatecount = 0

    # created folders for reports for App history
    os.makedirs(os.path.join(report_folder, "Apps_Historical"))

    data_list_installed = []
    data_list_uninstalled = []

    # Initialize database connection
    db = sqlite3.connect(mibdatabase)
    cursor = db.cursor()
    # Query to create installed and uninstalled app reports
    cursor.execute("""SELECT distinct bundle_id from dimm""")
    all_rows = cursor.fetchall()
    for row in all_rows:
        # logfunc(row[0])
        distinctbundle = row[0]
        cursor.execute(
            """SELECT * from dimm where bundle_id=? order by time_stamp desc limit 1""",
            (distinctbundle,),
        )
        all_rows_iu = cursor.fetchall()
        for row in all_rows_iu:
            # logfunc(row[0], row[1], row[2], row[3])
            if row[2] == "":
                continue
            elif row[1] == "Destroying container":
                # logfunc(row[0], row[1], row[2], row[3])
                uninstallcount = uninstallcount + 1
                totalapps = totalapps + 1
                # tofile1 = row[0] + ' ' + row[1] + ' ' + row[2] + ' ' + row[3] + '\n'
                data_list_uninstalled.append((row[0], row[2],))
                # logfunc()
            elif row[1] == "Uninstalling identifier":
                # logfunc(row[0], row[1], row[2], row[3])
                uninstallcount = uninstallcount + 1
                totalapps = totalapps + 1
                # tofile1 = row[0] + ' ' + row[1] + ' ' + row[2] + ' ' + row[3] + '\n'
                data_list_uninstalled.append((row[0], row[2],))
                # logfunc()
            else:
                # logfunc(row[0], row[1], row[2], row[3])
                data_list_installed.append((row[0], row[2],))
                installedcount = installedcount + 1
                totalapps = totalapps + 1

    location = f'{filename}'
    description = 'List of Uninstalled apps.'
    report = ArtifactHtmlReport('Apps - Uninstalled')
    report.start_artifact_report(report_folder, 'Apps - Uninstalled', description)
    report.add_script()
    data_headers = ('Last Uninstalled', 'Bundle ID',)
    report.write_artifact_data_table(data_headers, data_list_uninstalled, location)
    report.end_artifact_report()

    location = f'{filename}'
    description = 'List of Installed apps.'
    report = ArtifactHtmlReport('Apps - Installed')
    report.start_artifact_report(report_folder, 'Apps - Installed', description)
    report.add_script()
    data_headers = ('Last Installed', 'Bundle ID',)
    report.write_artifact_data_table(data_headers, data_list_installed, location)
    report.end_artifact_report()

    # Query to create historical report per app

    cursor.execute("""SELECT distinct bundle_id from dimm""")
    all_rows = cursor.fetchall()
    for row in all_rows:
        # logfunc(row[0])
        distinctbundle = row[0]
        if row[0] == "":
            continue
        else:
            f3 = open(os.path.join(report_folder, "Apps_Historical", distinctbundle + ".txt"),
                      "w+",
                      encoding="utf8"
                      )  # Create historical app report per app
            cursor.execute(
                """SELECT * from dimm where bundle_id=? order by time_stamp DESC""",
                (distinctbundle,),
            )  # Query to create app history per bundle_id
            all_rows_hist = cursor.fetchall()
            for row in all_rows_hist:
                # logfunc(row[0], row[1], row[2], row[3])
                tofile3 = row[0] + " " + row[1] + " " + row[2] + " " + row[3] + "\n"
                f3.write(tofile3)
        f3.close()
        historicalcount = historicalcount + 1

    list = []
    data_list = []
    path = os.path.join(report_folder, "Apps_Historical")
    files = os.listdir(path)
    for name in files:
        bun = (f'{name}')
        appendval = (
            f'<a href = "./Mobile Installation Logs/Apps_Historical/{name}" style = "color:blue" target="content">Report</a>')
        data_list.append((bun, appendval))

    location = f'{filename}'
    description = 'Historical App report from the Mobile Installation Logs. All timestamps are in Local Time'
    report = ArtifactHtmlReport('Apps - Historical')
    report.start_artifact_report(report_folder, 'Apps - Historical', description)
    report.add_script()
    data_headers = ('Bundle ID', 'Report Link')
    tsv_data_headers = ('Bundle ID', 'Report Link')
    report.write_artifact_data_table(data_headers, data_list, location, html_escape=False)
    report.end_artifact_report()

    tsvname = 'Mobile Installation Logs - History'
    tsv(report_folder, tsv_data_headers, tsv_tml_data_list, tsvname)
    tlactivity = 'Mobile Installation Logs - History'
    tml_data_headers = ('Timestamp', 'Event', 'Bundle ID', 'Event Path')
    timeline(report_folder, tlactivity, tsv_tml_data_list, tml_data_headers)

    # All event historical in html report
    description = 'Historical App report from the Mobile Installation Logs. All timestamps are in Local Time'
    report = ArtifactHtmlReport('Apps - Historical')
    report.start_artifact_report(report_folder, 'Apps - Historical Combined', description)
    report.add_script()
    data_headers = ('Timestamp', 'Event', 'Bundle ID', 'Event Path')
    report.write_artifact_data_table(data_headers, tsv_tml_data_list, location)
    report.end_artifact_report()

    # Query to create system events
    data_list_reboots = []
    cursor.execute(
        """SELECT * from dimm where action ='Reboot detected' order by time_stamp DESC"""
    )
    all_rows = cursor.fetchall()
    for row in all_rows:
        # logfunc(row[0])
        # logfunc(row[0], row[1], row[2], row[3])
        data_list_reboots.append((row[0], row[1]))
        sysstatecount = sysstatecount + 1

    if len(all_rows) > 0:
        location = f'{filename}'
        description = 'Reboots detected in Local Time.'
        report = ArtifactHtmlReport('State - Reboots')
        report.start_artifact_report(report_folder, 'State - Reboots', description)
        report.add_script()
        data_headers_reboots = ('Timestamp (Local Time)', 'Description')
        report.write_artifact_data_table(data_headers_reboots, data_list_reboots, location)
        report.end_artifact_report()

        tsvname = 'Mobile Installation Logs - Reboots'
        tsv(report_folder, data_headers_reboots, data_list_reboots, tsvname)

    logfunc(f"Total apps: {totalapps}")
    logfunc(f"Total installed apps: {installedcount}")
    logfunc(f"Total uninstalled apps: {uninstallcount}")
    logfunc(f"Total historical app reports: {historicalcount}")
    logfunc(f"Total system state events: {sysstatecount}")

    '''
    data_headers_reboots = ('Timestamp (Local Time)', 'Description')
    tsv_data_headers = ('Timestamp (Local Time)', 'Action', 'Bundle ID', 'Path')
    
    tsvname = 'Mobile Installation Logs - Reboots'
    tsv(report_folder, data_headers_reboots, data_list_reboots, tsvname)
    
    tlactivity = 'Mobile Installation Logs - Reboots'
    timeline(report_folder, tlactivity, data_list_reboots, data_headers_reboots)
    
    tsvname = 'Mobile Installation Logs - History'
    tsv(report_folder, tsv_data_headers, tsv_tml_data_list, tsvname)
    
    tlactivity = 'Mobile Installation Logs - History'
    timeline(report_folder, tlactivity, tsv_tml_data_list, tsv_data_headers)
    '''


'''    
    
    x = 0
    data_list =[]
    for file_found in files_found:
        x = x + 1
        sx = str(x)
        journalName = os.path.basename(file_found)
        outputpath = os.path.join(report_folder, sx+'_'+journalName+'.txt') # name of file in txt
        #linkpath = os.path.basename(
        level2, level1 = (os.path.split(outputpath))
        level2 = (os.path.split(level2)[1])
        final = level2+'/'+level1
        with open(outputpath, 'w') as g:
            for s in strings(file_found):
                g.write(s)
                g.write('\n')
        
        out = (f'<a href="{final}" style = "color:blue" target="_blank">{journalName}</a>') 
        
        data_list.append((out, file_found))

    location =''
    description = 'ASCII and Unicode strings extracted from SQLite journaing files.'
    report = ArtifactHtmlReport('Strings - SQLite Journal')
    report.start_artifact_report(report_folder, 'Strings - SQLite Journal', description)
    report.add_script()
    data_headers = ('Report', 'Location')
    report.write_artifact_data_table(data_headers, data_list, location, html_escape=False)
    report.end_artifact_report()
'''

__artifacts__ = {
    "mobileInstall": (
        "Mobile Installation Logs",
        ('**/mobile_installation.log.*'),
        get_mobileInstall)
}