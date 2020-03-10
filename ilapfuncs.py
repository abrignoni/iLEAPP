# ileapp
import base64
import codecs
import csv
import datetime
import glob
import io
import json
import os
import pathlib
import plistlib
import re
import shutil
import sqlite3
import sys
import textwrap
from time import process_time

from bs4 import BeautifulSoup
from packaging import version

from common import logfunc
from contrib.accounts.main import accs, confaccts
from contrib.aggregated_dictionary import aggdict, dbbuff
from contrib.application_state.main import applicationstate
from contrib.connected_devices.main import conndevices
from contrib.data_usage.main import datausage
from contrib.media_library.main import medlib
from contrib.system_diagnosis import bkupstate, mobilact
from settings import *
from vendor import ccl_bplist
from vendor.parse3 import ParseProto


# from parse3 import ParseProto


def datark(filefound):
    logfunc(f"Data_ark.plist function executing")
    deviceinfo()
    try:
        os.makedirs(os.path.join(reportfolderbase, "Data_Ark/"))
        with open(os.path.join(reportfolderbase, "Data_Ark/Data Ark.html"), "w") as f:
            f.write("<html><body>")
            f.write("<h2>Mobile Activation Report</h2>")
            f.write(f"Data_ark.plist located at {filefound[0]}<br>")
            f.write(
                "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
            )
            f.write("<br/>")
            f.write("")
            f.write(f'<table class="table sticky">')
            f.write(f"<tr><th>Key</th><th>Values</th></tr>")
            with open(filefound[0], "rb") as fp:
                pl = plistlib.load(fp)
                for key, val in pl.items():
                    f.write(f"<tr><td>{key}</td><td>{val}</td></tr>")
                    if key == "-DeviceName":
                        ordes = 1
                        kas = "Device Name"
                        vas = val
                        sources = filefound[0]
                        deviceinfoin(ordes, kas, vas, sources)
                    if key == "-TimeZone":
                        ordes = 9
                        kas = "Detected Time Zone"
                        vas = val
                        sources = filefound[0]
                        deviceinfoin(ordes, kas, vas, sources)

            f.write(f"</table></body></html>")
            logfunc(f"Data_ark.plist function completed")
    except:
        logfunc("Error in Sys Diagnose Network Preferences function.")


def conndevices(filefound):
    with open(filefound[0], "rb") as f:
        data = f.read()

    logfunc(f"Connected devices function executing")
    outpath = os.path.join(reportfolderbase, "Devices Connected/")
    os.mkdir(outpath)
    nl = "\n"

    userComps = ""

    logfunc("Data being interpreted for FRPD is of type: " + str(type(data)))
    x = type(data)
    byteArr = bytearray(data)
    userByteArr = bytearray()

    magicOffset = byteArr.find(b"\x01\x01\x80\x00\x00")
    magic = byteArr[magicOffset : magicOffset + 5]

    flag = 0

    if magic == b"\x01\x01\x80\x00\x00":
        logfunc(
            "Found magic bytes in iTunes Prefs FRPD... Finding Usernames and Desktop names now"
        )
        f = open(outpath + "DevicesConnected.html", "w")
        f.write("<html>")
        f.write(f"Artifact name and path: {filefound[0]}<br>")
        f.write(f"Usernames and Computer names:<br><br>")
        for x in range(int(magicOffset + 92), len(data)):
            if (data[x]) == 0:
                x = int(magicOffset) + 157
                if userByteArr.decode() == "":
                    continue
                else:
                    if flag == 0:
                        userComps += userByteArr.decode() + " - "
                        flag = 1
                    else:
                        userComps += userByteArr.decode() + "\n"
                        flag = 0
                    userByteArr = bytearray()
                    continue
            else:
                char = data[x]
                userByteArr.append(char)

        logfunc(f"{userComps}{nl}")
        f.write(f"{userComps}<br>")
    f.write(f"</html>")
    f.close()
    logfunc(f"Connected devices function completed. ")


def applicationstate(filefound):
    # iOSversion = versionf
    logfunc(f"ApplicationState.db queries executing")
    outpath = os.path.join(reportfolderbase, "Application State/")

    try:
        os.mkdir(outpath)
        os.mkdir(outpath + "exported-dirty/")
        os.mkdir(outpath + "exported-clean/")
    except OSError:
        logfunc("Error making directories")

    freepath = 1

    for pathfile in filefound:
        if isinstance(pathfile, pathlib.PurePath):
            freepath = os.path.abspath(pathfile)
            if freepath.endswith(".db"):
                apstatefiledb = freepath
        elif pathfile.endswith(".db"):
            apstatefiledb = pathfile

    # connect sqlite databases
    db = sqlite3.connect(apstatefiledb)
    cursor = db.cursor()

    cursor.execute(
        """
		select
		application_identifier_tab.[application_identifier],
		kvs.[value]
		from kvs, key_tab,application_identifier_tab
		where 
		key_tab.[key]='compatibilityInfo' and kvs.[key] = key_tab.[id]
		and application_identifier_tab.[id] = kvs.[application_identifier]
		order by application_identifier_tab.[id]
		"""
    )

    all_rows = cursor.fetchall()

    # poner un try except por si acaso
    extension = ".bplist"
    count = 0

    for row in all_rows:
        bundleid = str(row[0])
        bundleidplist = bundleid + ".bplist"
        f = row[1]
        output_file = open(
            outpath + "/exported-dirty/" + bundleidplist, "wb"
        )  # export dirty from DB
        output_file.write(f)
        output_file.close()

        g = open(outpath + "/exported-dirty/" + bundleidplist, "rb")
        # plist = plistlib.load(g)

        plist = ccl_bplist.load(g)

        output_file = open(outpath + "exported-clean/" + bundleidplist, "wb")
        output_file.write(plist)
        output_file.close()

    # create html headers
    filedatahtml = open(outpath + "Application State.html", mode="a+")
    filedatahtml.write("<html><body>")
    filedatahtml.write("<h2>iOS ApplicationState.db Report </h2>")
    filedatahtml.write(
        "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
    )
    filedatahtml.write("<br/>")
    filedatahtml.write('<table class="table sticky">')
    filedatahtml.write(f'<tr><td colspan = "4">{apstatefiledb}</td></tr>')
    filedatahtml.write(
        "<tr><th>Bundle ID</th><th>Bundle Path</th><th>Sandbox Path</th></tr>"
    )

    for filename in glob.glob(outpath + "exported-clean/*.bplist"):
        p = open(filename, "rb")
        # cfilename = os.path.basename(filename)
        plist = ccl_bplist.load(p)
        ns_keyed_archiver_obj = ccl_bplist.deserialise_NsKeyedArchiver(
            plist, parse_whole_structure=False
        )  # deserialize clean
        # logfunc(ns_keyed_archiver_obj)
        bid = ns_keyed_archiver_obj["bundleIdentifier"]
        bpath = ns_keyed_archiver_obj["bundlePath"]
        bcontainer = ns_keyed_archiver_obj["bundleContainerPath"]
        bsandbox = ns_keyed_archiver_obj["sandboxPath"]

        if bsandbox == "$null":
            bsandbox = ""
        if bcontainer == "$null":
            bcontainer = ""

        # csv report
        filedata = open(outpath + "ApplicationState_InstalledAppInfo.csv", mode="a+")
        filewrite = csv.writer(
            filedata, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        filewrite.writerow([bid, bpath, bcontainer, bsandbox])
        count = count + 1
        filedata.close()

        # html report
        filedatahtml.write(
            f"<tr><td>{bid}</td><td>{bpath}</td><td>{bsandbox}</td></tr>"
        )

        filemetadata = open(
            outpath + "ApplicationState_InstalledAppInfo_Path.txt", mode="w"
        )
        filemetadata.write(f"Artifact name and file path: {apstatefiledb} ")
        filemetadata.close()

    # close html footer
    filedatahtml.write("</table></html>")
    filedatahtml.close()

    logfunc(f"Installed app GUIDs and app locations processed: {count}")
    logfunc(f"ApplicationState.db queries completed.")


def knowledgec(filefound):
    logfunc(f"Incepted bplist extractions in KnowledgeC.db executing")

    iOSversion = versionf
    if version.parse(iOSversion) < version.parse("11"):
        logfunc("Unsupported version" + iOSversion)
        return ()

    extension = ".bplist"
    dump = True
    # create directories
    outpath = reportfolderbase + "KnowledgeC/"

    try:
        os.mkdir(outpath)
        os.mkdir(outpath + "clean/")
        os.mkdir(outpath + "/dirty")
    except OSError:
        logfunc("Error making directories")

    # connect sqlite databases
    db = sqlite3.connect(filefound[0])
    cursor = db.cursor()

    # variable initializations
    dirtcount = 0
    cleancount = 0
    intentc = {}
    intentv = {}

    cursor.execute(
        """
	SELECT
	Z_PK,
	Z_DKINTENTMETADATAKEY__SERIALIZEDINTERACTION,
	Z_DKINTENTMETADATAKEY__INTENTCLASS,
	Z_DKINTENTMETADATAKEY__INTENTVERB
	FROM ZSTRUCTUREDMETADATA
	WHERE Z_DKINTENTMETADATAKEY__SERIALIZEDINTERACTION is not null
	"""
    )

    all_rows = cursor.fetchall()

    for row in all_rows:
        pkv = str(row[0])
        pkvplist = pkv + extension
        f = row[1]
        intentclass = str(row[2])
        intententverb = str(row[3])
        output_file = open(
            outpath + "/dirty/D_Z_PK" + pkvplist, "wb"
        )  # export dirty from DB
        output_file.write(f)
        output_file.close()

        g = open(outpath + "/dirty/D_Z_PK" + pkvplist, "rb")
        plistg = ccl_bplist.load(g)

        if version.parse(iOSversion) < version.parse("12"):
            ns_keyed_archiver_objg = ccl_bplist.deserialise_NsKeyedArchiver(plistg)
            newbytearray = ns_keyed_archiver_objg
        else:
            ns_keyed_archiver_objg = ccl_bplist.deserialise_NsKeyedArchiver(plistg)
            newbytearray = ns_keyed_archiver_objg["NS.data"]

        dirtcount = dirtcount + 1

        binfile = open(outpath + "/clean/C_Z_PK" + pkvplist, "wb")
        binfile.write(newbytearray)
        binfile.close()

        # add to dictionaries
        intentc["C_Z_PK" + pkvplist] = intentclass
        intentv["C_Z_PK" + pkvplist] = intententverb

        cleancount = cleancount + 1

    h = open(outpath + "/StrucMetadata.html", "w")
    h.write("<html><body>")
    h.write(
        "<h2>iOS " + iOSversion + " - KnowledgeC ZSTRUCTUREDMETADATA bplist report</h2>"
    )
    h.write(
        "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
    )
    h.write("<br/>")

    for filename in glob.glob(outpath + "/clean/*" + extension):
        p = open(filename, "rb")
        cfilename = os.path.basename(filename)
        plist = ccl_bplist.load(p)
        ns_keyed_archiver_obj = ccl_bplist.deserialise_NsKeyedArchiver(
            plist, parse_whole_structure=True
        )  # deserialize clean
        # Get dictionary values
        A = intentc.get(cfilename)
        B = intentv.get(cfilename)

        if A is None:
            A = "No value"
        if B is None:
            A = "No value"

        # logfunc some values from clean bplist
        if version.parse(iOSversion) >= version.parse("13"):
            try:
                NSdata = ns_keyed_archiver_obj["root"]["intent"]["backingStore"][
                    "bytes"
                ]
            except:
                NSdata = ns_keyed_archiver_obj["root"]["intent"]["backingStore"][
                    "data"
                ]["NS.data"]
                pass
        else:
            NSdata = ns_keyed_archiver_obj["root"]["intent"]["backingStore"]["data"][
                "NS.data"
            ]
            # logfunc(str(NSdata))

        parsedNSData = ""
        # Default true
        if dump == True:
            nsdata_file = outpath + "/clean/" + cfilename + "_nsdata.bin"
            binfile = open(nsdata_file, "wb")
            if version.parse(iOSversion) >= version.parse("13"):
                try:
                    binfile.write(
                        ns_keyed_archiver_obj["root"]["intent"]["backingStore"]["bytes"]
                    )
                except:
                    binfile.write(
                        ns_keyed_archiver_obj["root"]["intent"]["backingStore"]["data"][
                            "NS.data"
                        ]
                    )
                    pass
            else:
                binfile.write(
                    ns_keyed_archiver_obj["root"]["intent"]["backingStore"]["data"][
                        "NS.data"
                    ]
                )
            binfile.close()
            messages = ParseProto(nsdata_file)
            messages_json_dump = json.dumps(
                messages, indent=4, sort_keys=True, ensure_ascii=False
            )
            parsedNSData = str(messages_json_dump).encode(
                encoding="UTF-8", errors="ignore"
            )

        NSstartDate = ccl_bplist.convert_NSDate(
            (ns_keyed_archiver_obj["root"]["dateInterval"]["NS.startDate"])
        )
        NSendDate = ccl_bplist.convert_NSDate(
            (ns_keyed_archiver_obj["root"]["dateInterval"]["NS.endDate"])
        )
        NSduration = ns_keyed_archiver_obj["root"]["dateInterval"]["NS.duration"]
        Siri = ns_keyed_archiver_obj["root"]["_donatedBySiri"]

        h.write(cfilename)
        h.write("<br />")
        h.write("Intent Class: " + str(A))
        h.write("<br />")
        h.write("Intent Verb: " + str(B))
        h.write("<br />")
        h.write("<table>")

        h.write("<tr>")
        h.write("<th>Data type</th>")
        h.write("<th>Value</th>")
        h.write("</tr>")

        # Donated by Siri
        h.write("<tr>")
        h.write("<td>Siri</td>")
        h.write("<td>" + str(Siri) + "</td>")
        h.write("</tr>")

        # NSstartDate
        h.write("<tr>")
        h.write("<td>NSstartDate</td>")
        h.write("<td>" + str(NSstartDate) + " Z</td>")
        h.write("</tr>")

        # NSsendDate
        h.write("<tr>")
        h.write("<td>NSendDate</td>")
        h.write("<td>" + str(NSendDate) + " Z</td>")
        h.write("</tr>")

        # NSduration
        h.write("<tr>")
        h.write("<td>NSduration</td>")
        h.write("<td>" + str(NSduration) + "</td>")
        h.write("</tr>")

        # NSdata
        h.write("<tr>")
        h.write("<td>NSdata</td>")
        h.write("<td>" + str(NSdata) + "</td>")
        h.write("</tr>")

        # NSdata better formatting
        if parsedNSData:
            h.write("<tr>")
            h.write("<td>NSdata - Protobuf Decoded</td>")
            h.write(
                '<td><pre id="json">'
                + str(parsedNSData).replace("\\n", "<br>")
                + "</pre></td>"
            )
            h.write("</tr>")
        else:
            # This will only run if -nd is used
            h.write("<tr>")
            h.write("<td>NSdata - Protobuf</td>")
            h.write("<td>" + str(NSdata).replace("\\n", "<br>") + "</td>")
            h.write("</tr>")

        h.write("<table>")
        h.write("<br />")

        # logfunc(NSstartDate)
        # logfunc(NSendDate)
        # logfunc(NSduration)
        # logfunc(NSdata)
        # logfunc('')

    logfunc("")
    logfunc("iOS - KnowledgeC ZSTRUCTUREDMETADATA bplist extractor")
    logfunc("By: @phillmoore & @AlexisBrignoni")
    logfunc("thinkdfir.com & abrignoni.com")
    logfunc("")
    logfunc("Bplists from the Z_DKINTENTMETADATAKEY__SERIALIZEDINTERACTION field.")
    logfunc("Exported bplists (dirty): " + str(dirtcount))
    logfunc("Exported bplists (clean): " + str(cleancount))
    logfunc("")
    logfunc(f"Triage report completed.")
    logfunc("Incepted bplist extractions in KnowledgeC.db completed")
    logfunc("")
    logfunc(f"KnowledgeC App Usage executing")

    # outpath = reportfolderbase+'KnowledgeC App Use/'

    # connect sqlite databases
    db = sqlite3.connect(filefound[0])
    cursor = db.cursor()

    cursor.execute(
        """
	SELECT
	datetime(ZOBJECT.ZCREATIONDATE+978307200,'UNIXEPOCH', 'LOCALTIME') as "ENTRY CREATION", 
	CASE ZOBJECT.ZSTARTDAYOFWEEK 
		WHEN "1" THEN "Sunday"
		WHEN "2" THEN "Monday"
		WHEN "3" THEN "Tuesday"
		WHEN "4" THEN "Wednesday"
		WHEN "5" THEN "Thursday"
		WHEN "6" THEN "Friday"
		WHEN "7" THEN "Saturday"
	END "DAY OF WEEK",
	ZOBJECT.ZSECONDSFROMGMT/3600 AS "GMT OFFSET",
	datetime(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH', 'LOCALTIME') as "START", 
	datetime(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH', 'LOCALTIME') as "END", 
	(ZOBJECT.ZENDDATE-ZOBJECT.ZSTARTDATE) as "USAGE IN SECONDS",
	ZOBJECT.ZSTREAMNAME, 
	ZOBJECT.ZVALUESTRING
	FROM ZOBJECT
	WHERE ZSTREAMNAME IS "/app/inFocus" 
	ORDER BY "START"	"""
    )

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)

    with open(
        reportfolderbase + "KnowledgeC/App Usage.html", "w", encoding="utf8"
    ) as f:
        f.write("<html><body>")
        f.write("<h2>iOS " + iOSversion + " - KnowledgeC App Usage report</h2>")
        f.write(f"KnowledgeC App Usage entries: {usageentries}<br>")
        f.write(f"KnowledgeC located at: {filefound[0]}<br>")
        f.write(
            "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
        )
        f.write("<br/>")
        f.write("")
        f.write(f'<table class="table sticky">')
        f.write(
            f"<tr><th>Entry Creation</th><th>Day of Week</th><th>GMT Offset</th><th>Start</th><th>End</th><th>Usage in Seconds</th><th>ZSTREAMNAME</th><th>ZVALUESTRING</th></tr>"
        )
        for row in all_rows:
            ec = row[0]
            dw = row[1]
            go = row[2]
            st = row[3]
            en = row[4]
            us = row[5]
            zs = row[6]
            zv = row[7]
            f.write(
                f"<tr><td>{ec}</td><td>{dw}</td><td>{go}</td><td>{st}</td><td>{en}</td><td>{us}</td><td>{zs}</td><td>{zv}</td></tr>"
            )
        f.write(f"</table></body></html>")
    logfunc(f"KnowledgeC App Usage completed")
    logfunc(f"KnowledgeC App Activity Executing")
    # connect sqlite databases
    db = sqlite3.connect(filefound[0])
    cursor = db.cursor()

    cursor.execute(
        '''
	SELECT
	datetime(ZOBJECT.ZCREATIONDATE+978307200,'UNIXEPOCH', 'LOCALTIME') as "ENTRY CREATION", 
		CASE ZOBJECT.ZSTARTDAYOFWEEK 
		WHEN "1" THEN "Sunday"
		WHEN "2" THEN "Monday"
		WHEN "3" THEN "Tuesday"
		WHEN "4" THEN "Wednesday"
		WHEN "5" THEN "Thursday"
		WHEN "6" THEN "Friday"
		WHEN "7" THEN "Saturday"
	END "DAY OF WEEK",
	datetime(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH', 'LOCALTIME') as "START", 
	datetime(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH', 'LOCALTIME') as "END", 
	ZOBJECT.ZSTREAMNAME, 
	ZOBJECT.ZVALUESTRING,
	ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONACTIVITYMETADATAKEY__ACTIVITYTYPE AS "ACTIVITY TYPE",  
	ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONACTIVITYMETADATAKEY__TITLE as "TITLE", 
	datetime(ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONACTIVITYMETADATAKEY__EXPIRATIONDATE+978307200,'UNIXEPOCH', 'LOCALTIME') as "EXPIRATION DATE",
	ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONACTIVITYMETADATAKEY__ITEMRELATEDCONTENTURL as "CONTENT URL",
	datetime(ZSTRUCTUREDMETADATA.ZCOM_APPLE_CALENDARUIKIT_USERACTIVITY_DATE+978307200,'UNIXEPOCH', 'LOCALTIME')  as "CALENDAR DATE",
	datetime(ZSTRUCTUREDMETADATA.ZCOM_APPLE_CALENDARUIKIT_USERACTIVITY_ENDDATE+978307200,'UNIXEPOCH', 'LOCALTIME')  as "CALENDAR END DATE"
	FROM ZOBJECT
	left join ZSTRUCTUREDMETADATA on ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK
	left join ZSOURCE on ZOBJECT.ZSOURCE = ZSOURCE.Z_PK
	WHERE ZSTREAMNAME is "/app/activity" 
	ORDER BY "ENTRY CREATION"'''
    )

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)

    with open(
        reportfolderbase + "KnowledgeC/App Activity.html", "w", encoding="utf8"
    ) as f:
        f.write("<html><body>")
        f.write("<h2>iOS " + iOSversion + " - KnowledgeC App Activity report</h2>")
        f.write(f"KnowledgeC App Activity entries: {usageentries}<br>")
        f.write(f"KnowledgeC located at: {filefound[0]}<br>")
        f.write(
            "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
        )
        f.write("<br/>")
        f.write("")
        f.write(f'<table class="table sticky">')
        f.write(
            f"<tr><th>Entry Creation</th><th>Day of Week</th><th>Start</th><th>End</th><th>ZSTREAMNAME</th><th>ZVALUESTRING</th><th>Activity Type</th><th>Title</th><th>Expiration Date</th><th>Content URL</th><th>Calendar Date</th><th>Calendar End Date</th></tr>"
        )
        for row in all_rows:
            ec = row[0]
            dw = row[1]
            st = row[2]
            en = row[3]
            zs = row[4]
            zv = row[5]
            tl = row[6]
            ed = row[7]
            cu = row[8]
            cd = row[9]
            ce = row[10]
            ced = row[11]
            f.write(
                f"<tr><td>{ec}</td><td>{dw}</td><td>{st}</td><td>{en}</td><td>{zs}</td><td>{zv}</td><td>{tl}</td><td>{ed}</td><td>{cu}</td><td>{cd}</td><td>{ce}</td><td>{ced}</td></tr>"
            )
        f.write(f"</table></body></html>")
    logfunc(f"KnowledgeC App Activity completed")

    logfunc(f"KnowledgeC App in Focus executing")
    db = sqlite3.connect(filefound[0])
    cursor = db.cursor()

    cursor.execute(
        '''
	SELECT
	ZOBJECT.ZVALUESTRING AS "BUNDLE ID", 
	(ZOBJECT.ZENDDATE-ZOBJECT.ZSTARTDATE) as "USAGE IN SECONDS",
	CASE ZOBJECT.ZSTARTDAYOFWEEK 
	    WHEN "1" THEN "Sunday"
	    WHEN "2" THEN "Monday"
	    WHEN "3" THEN "Tuesday"
	    WHEN "4" THEN "Wednesday"
	    WHEN "5" THEN "Thursday"
	    WHEN "6" THEN "Friday"
	    WHEN "7" THEN "Saturday"
	END "DAY OF WEEK",
	ZOBJECT.ZSECONDSFROMGMT/3600 AS "GMT OFFSET",
	DATETIME(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH') as "START", 
	DATETIME(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH') as "END",
	DATETIME(ZOBJECT.ZCREATIONDATE+978307200,'UNIXEPOCH') as "ENTRY CREATION",	
	ZOBJECT.Z_PK AS "ZOBJECT TABLE ID" 
	FROM ZOBJECT
	WHERE ZSTREAMNAME IS "/app/inFocus"'''
    )

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)

    with open(
        reportfolderbase + "KnowledgeC/App in Focus.html", "w", encoding="utf8"
    ) as f:
        f.write("<html><body>")
        f.write("<h2>iOS " + iOSversion + " - KnowledgeC App App in Focus report</h2>")
        f.write(f"KnowledgeC App in Focus entries: {usageentries}<br>")
        f.write(f"KnowledgeC located at: {filefound[0]}<br>")
        f.write(
            "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
        )
        f.write("<br/>")
        f.write("")
        f.write(f'<table class="table sticky">')
        f.write(
            f"<tr><th>Bundle ID</th><th>Usage in Seconds</th><th>Day of the Week</th><th>GMT Offset</th><th>Start</th><th>End</th><th>Entry Creation</th><th>ZOBJECT Table ID</th></tr>"
        )
        for row in all_rows:
            f.write(
                f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td></tr>"
            )
        f.write(f"</table></body></html>")
        logfunc(f"KnowledgeC App in Focus completed")

    logfunc(f"KnowledgeC App Battery Level executing")
    cursor.execute(
        """
	SELECT
			ZOBJECT.ZVALUEDOUBLE as "BATTERY LEVEL",
			(ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) AS "USAGE IN SECONDS", 
			CASE ZOBJECT.ZSTARTDAYOFWEEK 
				WHEN "1" THEN "Sunday"
				WHEN "2" THEN "Monday"
				WHEN "3" THEN "Tuesday"
				WHEN "4" THEN "Wednesday"
				WHEN "5" THEN "Thursday"
				WHEN "6" THEN "Friday"
				WHEN "7" THEN "Saturday"
			END "DAY OF WEEK",
			ZOBJECT.ZSECONDSFROMGMT/3600 AS "GMT OFFSET",
			DATETIME(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH') as "START", 
			DATETIME(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH') as "END",
			DATETIME(ZOBJECT.ZCREATIONDATE+978307200,'UNIXEPOCH') as "ENTRY CREATION",     
			ZOBJECT.Z_PK AS "ZOBJECT TABLE ID"
		FROM
			ZOBJECT 
			LEFT JOIN
				ZSTRUCTUREDMETADATA 
				ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK 
			LEFT JOIN
				ZSOURCE 
				ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK 
		WHERE
			ZSTREAMNAME LIKE "/device/BatteryPercentage"
	"""
    )

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)

    with open(
        reportfolderbase + "KnowledgeC/Battery Level.html", "w", encoding="utf8"
    ) as f:
        f.write("<html><body>")
        f.write("<h2>KnowledgeC Battery Level report</h2>")
        f.write(f"KnowledgeC Battery Level entries: {usageentries}<br>")
        f.write(f"KnowledgeC Battery Level located at: {filefound[0]}<br>")
        f.write(
            "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
        )
        f.write("<br/>")
        f.write("")
        f.write(f'<table class="table sticky">')
        f.write(
            f"<tr><th>Battery Level</th><th>Usage in Seconds</th><th>Day of the Week</th><th>GMT Offset</th><th>Start</th><th>End</th><th>Entry Creation</th><th>ZOBJECT Table ID</th></tr>"
        )
        for row in all_rows:
            f.write(
                f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td></tr>"
            )
        f.write(f"</table></body></html>")
        logfunc(f"KnowledgeC App Battery Level completed")

    logfunc(f"KnowledgeC Apps Installed executing")
    cursor.execute(
        """
	SELECT
			ZOBJECT.ZVALUESTRING AS "BUNDLE ID",
			CASE ZOBJECT.ZSTARTDAYOFWEEK 
				WHEN "1" THEN "Sunday"
				WHEN "2" THEN "Monday"
				WHEN "3" THEN "Tuesday"
				WHEN "4" THEN "Wednesday"
				WHEN "5" THEN "Thursday"
				WHEN "6" THEN "Friday"
				WHEN "7" THEN "Saturday"
			END "DAY OF WEEK",
			ZOBJECT.ZSECONDSFROMGMT/3600 AS "GMT OFFSET",
			DATETIME(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH') as "START", 
			DATETIME(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH') as "END",
			DATETIME(ZOBJECT.ZCREATIONDATE+978307200,'UNIXEPOCH') as "ENTRY CREATION",	
			ZOBJECT.Z_PK AS "ZOBJECT TABLE ID"
		FROM
		   ZOBJECT 
		   LEFT JOIN
		      ZSTRUCTUREDMETADATA 
		      ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK 
		   LEFT JOIN
		      ZSOURCE 
		      ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK 
		WHERE ZSTREAMNAME is "/app/install"
	"""
    )

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)

    with open(
        reportfolderbase + "KnowledgeC/Apps Installed.html", "w", encoding="utf8"
    ) as f:
        f.write("<html><body>")
        f.write("<h2>KnowledgeC Apps Installed report</h2>")
        f.write(f"KnowledgeC Apps Installed : {usageentries}<br>")
        f.write(f"KnowledgeC Apps Installed located at: {filefound[0]}<br>")
        f.write(
            "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
        )
        f.write("<br/>")
        f.write("")
        f.write(f'<table class="table sticky">')
        f.write(
            f"<tr><th>Bundle ID</th><th>Day of the Week</th><th>GMT Offset</th><th>Start</th><th>End</th><th>Entry Creation</th></tr>"
        )
        for row in all_rows:
            f.write(
                f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td></tr>"
            )
        f.write(f"</table></body></html>")
        logfunc(f"KnowledgeC Apps Installed completed")

    logfunc(f"KnowledgeC Device Locked executing")
    cursor.execute(
        """
	SELECT
			CASE ZOBJECT.ZVALUEINTEGER
				WHEN '0' THEN 'UNLOCKED' 
				WHEN '1' THEN 'LOCKED' 
			END "IS LOCKED",
			(ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) AS "USAGE IN SECONDS",  
			CASE ZOBJECT.ZSTARTDAYOFWEEK 
				WHEN "1" THEN "Sunday"
				WHEN "2" THEN "Monday"
				WHEN "3" THEN "Tuesday"
				WHEN "4" THEN "Wednesday"
				WHEN "5" THEN "Thursday"
				WHEN "6" THEN "Friday"
				WHEN "7" THEN "Saturday"
			END "DAY OF WEEK",
			ZOBJECT.ZSECONDSFROMGMT/3600 AS "GMT OFFSET",
			DATETIME(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH') as "START", 
			DATETIME(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH') as "END",
			DATETIME(ZOBJECT.ZCREATIONDATE+978307200,'UNIXEPOCH') as "ENTRY CREATION", 
			ZOBJECT.Z_PK AS "ZOBJECT TABLE ID" 
		FROM
			ZOBJECT 
			LEFT JOIN
				ZSTRUCTUREDMETADATA 
				ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK 
			LEFT JOIN
				ZSOURCE 
				ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK 
		WHERE
			ZSTREAMNAME LIKE "/device/isLocked"
	"""
    )

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)

    with open(
        reportfolderbase + "KnowledgeC/Device Locked.html", "w", encoding="utf8"
    ) as f:
        f.write("<html><body>")
        f.write("<h2>KnowledgeC Device Locked report</h2>")
        f.write(f"KnowledgeC Device Locked: {usageentries}<br>")
        f.write(f"KnowledgeC Device Locked located at: {filefound[0]}<br>")
        f.write(
            "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
        )
        f.write("<br/>")
        f.write("")
        f.write(f'<table class="table sticky">')
        f.write(
            f"<tr><th>Is Locked?</th><th>Usage in Seconds</th><th>Day of the Week</th><th>GMT Offset</th><th>Start</th><th>End</th><th>Entry Creation</th></tr>"
        )
        for row in all_rows:
            f.write(
                f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td></tr>"
            )
        f.write(f"</table></body></html>")
        logfunc(f"KnowledgeC Device Locked completed")

    logfunc(f"KnowledgeC Plugged In executing")

    cursor.execute(
        """
	SELECT
			CASE
			ZOBJECT.ZVALUEINTEGER
				WHEN '0' THEN 'UNPLUGGED' 
				WHEN '1' THEN 'PLUGGED IN' 
			END "IS PLUGGED IN",
			(ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) AS "USAGE IN SECONDS",  
			CASE ZOBJECT.ZSTARTDAYOFWEEK 
				WHEN "1" THEN "Sunday"
				WHEN "2" THEN "Monday"
				WHEN "3" THEN "Tuesday"
				WHEN "4" THEN "Wednesday"
				WHEN "5" THEN "Thursday"
				WHEN "6" THEN "Friday"
				WHEN "7" THEN "Saturday"
			END "DAY OF WEEK",
			ZOBJECT.ZSECONDSFROMGMT/3600 AS "GMT OFFSET",
			DATETIME(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH') as "START", 
			DATETIME(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH') as "END",
			DATETIME(ZOBJECT.ZCREATIONDATE+978307200,'UNIXEPOCH') as "ENTRY CREATION", 
			ZOBJECT.Z_PK AS "ZOBJECT TABLE ID" 
		FROM
			ZOBJECT 
			LEFT JOIN
				ZSTRUCTUREDMETADATA 
				ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK 
			LEFT JOIN
				ZSOURCE 
				ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK 
		WHERE
			ZSTREAMNAME LIKE "/device/isPluggedIn"
	"""
    )

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)

    with open(
        reportfolderbase + "KnowledgeC/Plugged In.html", "w", encoding="utf8"
    ) as f:
        f.write("<html><body>")
        f.write("<h2>KnowledgeC Plugged In report</h2>")
        f.write(f"KnowledgeC Device Plugged In entries: {usageentries}<br>")
        f.write(f"KnowledgeC Device Plugged In located at: {filefound[0]}<br>")
        f.write(
            "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
        )
        f.write("<br/>")
        f.write("")
        f.write(f'<table class="table sticky">')
        f.write(
            f"<tr><th>Is Plugged In?</th><th>Usage in Seconds</th><th>Day of the Week</th><th>GMT Offset</th><th>Start</th><th>End</th><th>Entry Creation</th></tr>"
        )
        for row in all_rows:
            f.write(
                f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td></tr>"
            )
        f.write(f"</table></body></html>")
        logfunc(f"KnowledgeC Plugged In completed")

    if iOSversion == ("13") or ("12"):
        logfunc(f"KnowledgeC Serialized Interaction executing")

        cursor.execute(
            """
		select 
		ZSTRUCTUREDMETADATA.Z_PK  as ID,
		ZSTRUCTUREDMETADATA.Z_DKINTENTMETADATAKEY__INTENTCLASS,
		ZSTRUCTUREDMETADATA.Z_DKINTENTMETADATAKEY__INTENTVERB,
		datetime(ZOBJECT.ZSTARTDATE+ 978307200, 'UNIXEPOCH')  as timestam,
		ZOBJECT.ZVALUESTRING,
		ZOBJECT.ZSTREAMNAME,
		ZSTRUCTUREDMETADATA.Z_DKINTENTMETADATAKEY__SERIALIZEDINTERACTION
		from ZSTRUCTUREDMETADATA, ZOBJECT
		where ZSTRUCTUREDMETADATA.Z_DKINTENTMETADATAKEY__SERIALIZEDINTERACTION not NULL
		and ZSTRUCTUREDMETADATA.Z_PK = ZOBJECT.ZSTRUCTUREDMETADATA
		"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            os.mkdir(reportfolderbase + "KnowledgeC/expbplists/")
            with open(
                reportfolderbase + "KnowledgeC/StrucMetadataCombined.html",
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2>KnowledgeC Serialize Intents Bplists report</h2>")
                f.write(
                    f"KnowledgeC Serialize Intents Bplists entries: {usageentries}<br>"
                )
                f.write(
                    f"KnowledgeC Serialize Intents Bplists located at: {filefound[0]}<br>"
                )
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>ID</th><th>Intent Class</th><th>Intent Verb</th><th>Timestamp</th><th>String</th><th>Stream</th><th>Serialized Interaction bplist</th></tr>"
                )
                for row in all_rows:
                    binfile = (
                        outpath + "/clean/C_Z_PK" + str(row[0]) + ".bplist_nsdata.bin"
                    )
                    if os.path.isfile(binfile):
                        messages = ParseProto(binfile)
                        messages_json_dump = json.dumps(
                            messages, indent=4, sort_keys=True, ensure_ascii=False
                        )
                        parsedNSData = str(messages_json_dump).encode(
                            encoding="UTF-8", errors="ignore"
                        )
                    else:
                        parsedNSData = str(row[6])

                    f.write(
                        f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td><pre id="json">'
                        + str(parsedNSData).replace("\\n", "<br>")
                        + "</pre></td></tr>"
                    )
                f.write(f"</table></body></html>")
            logfunc(f"KnowledgeC Serialized Interaction completed")
        else:
            logfunc(f"No KnowledgeC Serialized Interaction files available")

    logfunc(f"KnowledgeC Siri Usage executing")
    cursor.execute(
        """
	SELECT
	  ZOBJECT.ZVALUESTRING AS "APP NAME",  
		CASE ZOBJECT.ZSTARTDAYOFWEEK 
			WHEN "1" THEN "Sunday"
			WHEN "2" THEN "Monday"
			WHEN "3" THEN "Tuesday"
			WHEN "4" THEN "Wednesday"
			WHEN "5" THEN "Thursday"
			WHEN "6" THEN "Friday"
			WHEN "7" THEN "Saturday"
		END "DAY OF WEEK",
		ZOBJECT.ZSECONDSFROMGMT/3600 AS "GMT OFFSET",
		DATETIME(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH') AS "START", 
		DATETIME(ZOBJECT.ZCREATIONDATE+978307200,'UNIXEPOCH') AS "ENTRY CREATION",
		ZOBJECT.ZUUID AS "UUID", 
		ZOBJECT.Z_PK AS "ZOBJECT TABLE ID" 
	FROM
		ZOBJECT 
		LEFT JOIN
			ZSTRUCTUREDMETADATA 
			ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK 
		LEFT JOIN
			ZSOURCE 
			ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK 
	WHERE
		ZSTREAMNAME =  "/siri/ui" 
	"""
    )

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        with open(
            reportfolderbase + "KnowledgeC/Siri Usage.html", "w", encoding="utf8"
        ) as f:
            f.write("<html><body>")
            f.write("<h2>KnowledgeC Siri Usage report</h2>")
            f.write(f"KnowledgeC Siri Usage entries: {usageentries}<br>")
            f.write(f"KnowledgeC Siri Usage located at: {filefound[0]}<br>")
            f.write(
                "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
            )
            f.write("<br/>")
            f.write("")
            f.write(f'<table class="table sticky">')
            f.write(
                f"<tr><th>App Name</th><th>Weekday</th><th>GMT Offset</th><th>Start</th><th>Entry Creation</th><th>UUID</th><th>Table ID</th></tr>"
            )
            for row in all_rows:
                f.write(
                    f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td></tr>"
                )
            f.write(f"</table></body></html>")
        logfunc(f"KnowledgeC Siri Usage completed")
    else:
        logfunc(f"No KnowledgeC Siri Usage files available")


def mib(filefound):
    logfunc(f"Mobile Installation Logs function executing")
    # initialize counters
    counter = 0
    filescounter = 0

    # Month to numeric with leading zero when month < 10 function
    # Function call: month = month_converter(month)
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

    # Day with leading zero if day < 10 function
    # Functtion call: day = day_converter(day)
    def day_converter(day):
        day = int(day)
        if day < 10:
            day = f"{day:02d}"
        return day

    # Create folders for this function
    os.makedirs(
        os.path.join(reportfolderbase, "Mobile_Installation_Logs")
    )  # '.', 'ILEAPP_Reports_' + currenttime)
    # Create sqlite databases
    db = sqlite3.connect(
        os.path.join(reportfolderbase, "Mobile_Installation_Logs/mib.db")
    )

    cursor = db.cursor()

    # Create table fileds for destroyed, installed, moved and made identifiers.

    cursor.execute(
        """

		CREATE TABLE dimm(time_stamp TEXT, action TEXT, bundle_id TEXT, 

						  path TEXT)

	"""
    )

    db.commit()

    for filename in filefound:
        file = open(filename, "r", encoding="utf8")
        filescounter = filescounter + 1
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
                cursor.execute(
                    "INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)",
                    datainsert,
                )
                db.commit()

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
                cursor.execute(
                    "INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)",
                    datainsert,
                )
                db.commit()

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
                cursor.execute(
                    "INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)",
                    datainsert,
                )
                db.commit()

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
                cursor.execute(
                    "INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)",
                    datainsert,
                )
                db.commit()

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
                cursor.execute(
                    "INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)",
                    datainsert,
                )
                db.commit()

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
                cursor.execute(
                    "INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)",
                    datainsert,
                )
                db.commit()

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
                cursor.execute(
                    "INSERT INTO dimm (time_stamp, action, bundle_id, path)  VALUES(?,?,?,?)",
                    datainsert,
                )
                db.commit()

                # logfunc()
    try:
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

        # created folders for reports and sub folders for App history, App state
        os.makedirs(reportfolderbase + "Mobile_Installation_Logs/Apps_State/")
        os.makedirs(reportfolderbase + "Mobile_Installation_Logs/Apps_Historical/")
        os.makedirs(reportfolderbase + "Mobile_Installation_Logs/System_State/")

        # Initialize text file reports for installed and unistalled apps
        f1 = open(
            reportfolderbase
            + "Mobile_Installation_Logs/Apps_State/UninstalledApps.txt",
            "w+",
            encoding="utf8",
        )
        f2 = open(
            reportfolderbase + "Mobile_Installation_Logs/Apps_State/InstalledApps.txt",
            "w+",
            encoding="utf8",
        )
        f4 = open(
            reportfolderbase + "Mobile_Installation_Logs/System_State/SystemState.txt",
            "w+",
            encoding="utf8",
        )

        # Initialize database connection
        db = sqlite3.connect(reportfolderbase + "Mobile_Installation_Logs/mib.db")

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
                    tofile1 = row[2] + "\n"
                    f1.write(tofile1)
                    # logfunc()
                elif row[1] == "Uninstalling identifier":
                    # logfunc(row[0], row[1], row[2], row[3])
                    uninstallcount = uninstallcount + 1
                    totalapps = totalapps + 1
                    # tofile1 = row[0] + ' ' + row[1] + ' ' + row[2] + ' ' + row[3] + '\n'
                    tofile1 = row[2] + "\n"
                    f1.write(tofile1)
                    # logfunc()
                else:
                    # logfunc(row[0], row[1], row[2], row[3])
                    tofile2 = row[2] + "\n"

                    f2.write(tofile2)
                    installedcount = installedcount + 1
                    totalapps = totalapps + 1

        f1.close()
        f2.close()

        list = []
        path = reportfolderbase + "/Mobile_Installation_Logs/Apps_State/"
        files = os.listdir(path)
        for name in files:
            list.append(f'<a href = "./{name}" target="content">{name}</a>')

        filedatahtml = open(path + "/Apps State.html", mode="a+")
        filedatahtml.write(
            "Data from Mobile Installation Logs - App State / Installed and Uninstalled Apps <br>"
        )
        filedatahtml.write(f"Data location: {filename} <br><br>")
        list.sort()
        for items in list:
            filedatahtml.write(items)
            filedatahtml.write("<br>")
        filedatahtml.close()

        # Query to create historical report per app

        cursor.execute("""SELECT distinct bundle_id from dimm""")
        all_rows = cursor.fetchall()
        for row in all_rows:
            # logfunc(row[0])
            distinctbundle = row[0]
            if row[0] == "":
                continue
            else:
                f3 = open(
                    reportfolderbase
                    + "Mobile_Installation_Logs/Apps_Historical/"
                    + distinctbundle
                    + ".txt",
                    "w+",
                    encoding="utf8",
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
        path = reportfolderbase + "/Mobile_Installation_Logs/Apps_Historical/"
        files = os.listdir(path)
        for name in files:
            list.append(f'<a href = "./{name}" target="content">{name}</a>')

        filedatahtml = open(path + "Apps Historical.html", mode="a+")
        filedatahtml.write("Data from Mobile Installation Logs - Apps Historical <br>")
        filedatahtml.write(f"Data location: {filename} <br><br>")
        list.sort()
        for items in list:
            filedatahtml.write(items)
            filedatahtml.write("<br>")
        filedatahtml.close()

        # Query to create system events

        path = reportfolderbase + "/Mobile_Installation_Logs/System_State/"
        filedatahtml = open(path + "System State.html", mode="a+")
        filedatahtml.write(
            "Data from Mobile Installation Logs - System State / Reboots <br>"
        )
        filedatahtml.write(f"Data location: {filename} <br><br>")

        cursor.execute(
            """SELECT * from dimm where action ='Reboot detected' order by time_stamp DESC"""
        )
        all_rows = cursor.fetchall()
        for row in all_rows:
            # logfunc(row[0])
            # logfunc(row[0], row[1], row[2], row[3])
            tofile4 = row[0] + " " + row[1] + " " + row[2] + " " + row[3] + "\n"
            f4.write(tofile4)
            filedatahtml.write(tofile4 + "<br>")
            sysstatecount = sysstatecount + 1

        filedatahtml.close()

        logfunc(f"Total apps: {totalapps}")
        logfunc(f"Total installed apps: {installedcount}")
        logfunc(f"Total uninstalled apps: {uninstallcount}")
        logfunc(f"Total historical app reports: {historicalcount}")
        logfunc(f"Total system state events: {sysstatecount}")
        logfunc(f"Mobile Installation Logs function completed.")
        f1.close()
        f2.close()
        f4.close()

    except:
        logfunc(f"Log files not found in {filefound}")


def wireless(filefound):
    logfunc(f"Cellular Wireless files function executing")
    try:
        deviceinfo()
        os.makedirs(reportfolderbase + "Cellular Wireless Info/")
        for filepath in filefound:
            basename = os.path.basename(filepath)
            if (
                basename == "com.apple.commcenter.device_specific_nobackup.plist"
                or basename == "com.apple.commcenter.plist"
            ):
                f = open(
                    reportfolderbase + "Cellular Wireless Info/" + basename + ".html",
                    "w",
                )
                # header html mas tabla
                f.write("<html>")
                f.write(f"<p><body><table>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write(f'<tr><td colspan="2">{basename}</td></tr>')
                p = open(filepath, "rb")
                plist = plistlib.load(p)
                for key, val in plist.items():
                    f.write(f"<tr><td>{key}</td><td>{val}</td></tr>")
                    if key == "ReportedPhoneNumber":
                        ordes = 2
                        kas = "Reported Phone Number"
                        vas = val
                        sources = filefound[0]
                        deviceinfoin(ordes, kas, vas, sources)
                f.write(f"</table></body></html>")
                f.close()
    except:
        logfunc(f"Error in Celullar Wireless files function")
    logfunc(f"Cellular Wireless files function completed")


def iconstate(filefound):
    logfunc(f"Iconstate function executing")
    os.makedirs(reportfolderbase + "Icon Positions/")
    f = open(reportfolderbase + "Icon Positions/Icon Positions.txt", "w")
    g = open(reportfolderbase + "Icon Positions/Icon Positons.html", "w")
    g.write("<html>")
    p = open(filefound[0], "rb")
    plist = plistlib.load(p)
    for key, val in plist.items():
        f.write(f"{key} -> {val}{nl}")
        if key == "buttonBar":
            bbar = val
        elif key == "iconLists":
            icon = val
    f.close()
    for x in range(0, len(icon)):
        page = icon[x]
        g.write(f"<p><table><table>")
        g.write(
            "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
        )
        g.write(f'<tr> <td colspan="4"> Icons screen #{x}</td>')
        for y in range(0, len(page)):
            rows = page[y]
            if (y == 0) or (y % 4 == 0):
                g.write("</tr><tr>")
            g.write(f"<td width = 25%>{rows}</td>")
        g.write("</tr></table>")

    # do bottom bar
    g.write(f'<p><table><tr> <td colspan="4"> Icons bottom bar</td></tr><tr>')
    for x in range(0, len(bbar)):
        g.write(f"<td width = 25%>{bbar[x]}</td>")
    g.write("</tr></table>")

    g.write("</html>")
    g.close()

    logfunc("Screens: " + str(len(icon)))
    logfunc("Icons in bottom bar: " + str(len(bbar)))
    logfunc(f"Iconstate function completed.")


def lastbuild(filefound):
    deviceinfo()
    global versionf
    versionnum = 0
    logfunc(f"Lastbuild function executing")
    os.makedirs(reportfolderbase + "Build Info/")
    f = open(reportfolderbase + "Build Info/LastBuildInfo.plist.txt", "w")
    p = open(filefound[0], "rb")
    plist = plistlib.load(p)

    # create html headers
    filedatahtml = open(reportfolderbase + "Build Info/" + "Build_Info.html", mode="a+")
    filedatahtml.write("<html><body>")
    filedatahtml.write("<h2>Last Build Report </h2>")
    filedatahtml.write(
        "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
    )
    filedatahtml.write("<table>")
    filedatahtml.write(f'<tr><td colspan = "2">{filefound[0]}</td></tr>')
    filedatahtml.write("<tr><td>Key</td><td>Value</td></tr>")

    for key, val in plist.items():
        f.write(f"{key} -> {val}{nl}")
        filedatahtml.write(f"<tr><td>{key}</td><td>{val}</td></tr>")
        if key == ("ProductVersion"):
            ordes = 7
            kas = "Product Version"
            vas = val
            sources = filefound[0]
            deviceinfoin(ordes, kas, vas, sources)

            versionf = val
            logfunc(f"iOS version is: {versionf}")

        if key == "ProductBuildVersion":
            ordes = 8
            kas = "Build Version"
            vas = val
            sources = filefound[0]
            deviceinfoin(ordes, kas, vas, sources)

    f.close()

    # close html footer
    filedatahtml.write("</table></html>")
    filedatahtml.close()
    logfunc(f"Lastbuild function completed.")


def iOSNotifications11(filefound):
    logfunc(f"iOSNotifications 11 function executing")

    count = 0
    notdircount = 0
    exportedbplistcount = 0
    unix = datetime.datetime(1970, 1, 1)  # UTC
    cocoa = datetime.datetime(2001, 1, 1)  # UTC
    delta = cocoa - unix

    with open("NotificationParams.txt", "r") as f:
        notiparams = [line.strip() for line in f]

    pathfound = 0
    count = 0
    notdircount = 0
    exportedbplistcount = 0

    pathfound = str(filefound[0])

    if pathfound == 0:
        logfunc("No PushStore directory located")
    else:
        folder = (
            reportfolderbase + "iOS 11 Notifications/"
        )  # add the date thing from phill
        os.makedirs(folder)
        # logfunc("Processing:")
        for filename in glob.iglob(pathfound + "\**", recursive=True):
            if os.path.isfile(filename):  # filter dirs
                file_name = os.path.splitext(os.path.basename(filename))[0]
                # get extension and iterate on those files
                # file_extension = os.path.splitext(filename)
                # logfunc(file_extension)
                # create directory
                if filename.endswith("pushstore"):
                    # create directory where script is running from
                    logfunc(filename)  # full path
                    notdircount = notdircount + 1
                    # logfunc (os.path.basename(file_name)) #filename with  no extension
                    openplist = os.path.basename(
                        os.path.normpath(filename)
                    )  # filename with extension
                    # logfunc (openplist)
                    # bundlepath = (os.path.basename(os.path.dirname(filename)))#previous directory
                    bundlepath = file_name
                    appdirect = folder + "\\" + bundlepath
                    # logfunc(appdirect)
                    os.makedirs(appdirect)

                    # open the plist
                    p = open(filename, "rb")
                    plist = ccl_bplist.load(p)
                    plist2 = plist["$objects"]

                    long = len(plist2)
                    # logfunc (long)
                    h = open(
                        "./" + appdirect + "/DeliveredNotificationsReport.html", "w"
                    )  # write report
                    h.write("<html><body>")
                    h.write("<h2>iOS Delivered Notifications Triage Report </h2>")
                    h.write(filename)
                    h.write("<br/>")
                    h.write(
                        "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                    )
                    h.write("<br/>")

                    h.write('<button onclick="hideRows()">Hide rows</button>')
                    h.write('<button onclick="showRows()">Show rows</button>')

                    f = open("script.txt")
                    for line in f:
                        h.write(line)
                    f.close()

                    h.write("<br>")
                    h.write('<table name="hide">')
                    h.write('<tr name="hide">')
                    h.write("<th>Data type</th>")
                    h.write("<th>Value</th>")
                    h.write("</tr>")

                    h.write('<tr name="hide">')
                    h.write("<td>Plist</td>")
                    h.write("<td>Initial Values</td>")
                    h.write("</tr>")

                    test = 0
                    for i in range(0, long):
                        try:
                            if plist2[i]["$classes"]:
                                h.write('<tr name="hide">')
                                h.write("<td>$classes</td>")
                                ob6 = str(plist2[i]["$classes"])
                                h.write("<td>")
                                h.write(str(ob6))
                                h.write("</td>")
                                h.write("</tr>")
                                test = 1
                        except:
                            pass
                        try:
                            if plist2[i]["$class"]:
                                h.write('<tr name="hide">')
                                h.write("<td>$class</td>")
                                ob5 = str(plist2[i]["$class"])
                                h.write("<td>")
                                h.write(str(ob5))
                                h.write("</td>")
                                h.write("</tr>")
                                test = 1
                        except:
                            pass
                        try:
                            if plist2[i]["NS.keys"]:
                                h.write('<tr name="hide">')
                                h.write("<td>NS.keys</td>")
                                ob0 = str(plist2[i]["NS.keys"])
                                h.write("<td>")
                                h.write(str(ob0))
                                h.write("</td>")
                                h.write("</tr>")
                                test = 1
                        except:
                            pass
                        try:
                            if plist2[i]["NS.objects"]:
                                ob1 = str(plist2[i]["NS.objects"])
                                h.write('<tr name="hide">')
                                h.write("<td>NS.objects</td>")
                                h.write("<td>")
                                h.write(str(ob1))
                                h.write("</td>")
                                h.write("</tr>")

                                test = 1
                        except:
                            pass
                        try:
                            if plist2[i]["NS.time"]:
                                dia = str(plist2[i]["NS.time"])
                                dias = dia.rsplit(".", 1)[0]
                                timestamp = (
                                    datetime.datetime.fromtimestamp(int(dias)) + delta
                                )
                                # logfunc (timestamp)

                                h.write("<tr>")
                                h.write("<td>Time UTC</td>")
                                h.write("<td>")
                                h.write(str(timestamp))
                                # h.write(str(plist2[i]['NS.time']))
                                h.write("</td>")
                                h.write("</tr>")

                                test = 1
                        except:
                            pass
                        try:
                            if plist2[i]["NS.base"]:
                                ob2 = str(plist2[i]["NS.objects"])
                                h.write('<tr name="hide">')
                                h.write("<td>NS.base</td>")
                                h.write("<td>")
                                h.write(str(ob2))
                                h.write("</td>")
                                h.write("</tr>")

                                test = 1
                        except:
                            pass
                        try:
                            if plist2[i]["$classname"]:
                                ob3 = str(plist2[i]["$classname"])
                                h.write('<tr name="hide">')
                                h.write("<td>$classname</td>")
                                h.write("<td>")
                                h.write(str(ob3))
                                h.write("</td>")
                                h.write("</tr>")

                                test = 1
                        except:
                            pass

                        try:
                            if test == 0:
                                if (plist2[i]) == "AppNotificationMessage":
                                    h.write("</table>")
                                    h.write("<br>")
                                    h.write("<table>")
                                    h.write("<tr>")
                                    h.write("<th>Data type</th>")
                                    h.write("<th>Value</th>")
                                    h.write("</tr>")

                                    h.write('<tr name="hide">')
                                    h.write("<td>ASCII</td>")
                                    h.write("<td>" + str(plist2[i]) + "</td>")
                                    h.write("</tr>")

                                else:
                                    if plist2[i] in notiparams:
                                        h.write('<tr name="hide">')
                                        h.write("<td>ASCII</td>")
                                        h.write("<td>" + str(plist2[i]) + "</td>")
                                        h.write("</tr>")
                                    elif plist2[i] == " ":
                                        h.write('<tr name="hide">')
                                        h.write("<td>Null</td>")
                                        h.write("<td>" + str(plist2[i]) + "</td>")
                                        h.write("</tr>")
                                    else:
                                        h.write("<tr>")
                                        h.write("<td>ASCII</td>")
                                        h.write("<td>" + str(plist2[i]) + "</td>")
                                        h.write("</tr>")

                        except:
                            pass

                        test = 0

                        # h.write('test')

                    for dict in plist2:
                        liste = dict
                        types = type(liste)
                        # logfunc (types)
                        try:
                            for k, v in liste.items():
                                if k == "NS.data":
                                    chk = str(v)
                                    reduced = chk[2:8]
                                    # logfunc (reduced)
                                    if reduced == "bplist":
                                        count = count + 1
                                        binfile = open(
                                            "./"
                                            + appdirect
                                            + "/incepted"
                                            + str(count)
                                            + ".bplist",
                                            "wb",
                                        )
                                        binfile.write(v)
                                        binfile.close()

                                        procfile = open(
                                            "./"
                                            + appdirect
                                            + "/incepted"
                                            + str(count)
                                            + ".bplist",
                                            "rb",
                                        )
                                        secondplist = ccl_bplist.load(procfile)
                                        secondplistint = secondplist["$objects"]
                                        logfunc("Bplist processed and exported.")
                                        exportedbplistcount = exportedbplistcount + 1
                                        h.write('<tr name="hide">')
                                        h.write("<td>NS.data</td>")
                                        h.write("<td>")
                                        h.write(str(secondplistint))
                                        h.write("</td>")
                                        h.write("</tr>")

                                        procfile.close()
                                        count = 0
                                    else:
                                        h.write('<tr name="hide">')
                                        h.write("<td>NS.data</td>")
                                        h.write("<td>")
                                        h.write(str(secondplistint))
                                        h.write("</td>")
                                        h.write("</tr>")
                        except:
                            pass
                    h.close()
                elif "AttachmentsList" in file_name:
                    test = 0  # future development

    path = reportfolderbase + "/iOS 11 Notifications/"
    list = []
    files = os.listdir(path)
    for name in files:
        list.append(
            f'<a href = "./{name}/DeliveredNotificationsReport.html" target="content">{name}</a>'
        )

    filedatahtml = open(path + "iOS11_Notifications.html", mode="a+")
    list.sort()
    for items in list:
        filedatahtml.write(items)
        filedatahtml.write("<br>")

    logfunc("Total notification directories processed:" + str(notdircount))
    logfunc("Total exported bplists from notifications:" + str(exportedbplistcount))
    if notdircount == 0:
        logfunc("No notifications located.")
    logfunc(f"iOS 11 Notifications function completed.")


def iOSNotifications12(filefound):
    logfunc(f"iOS 12+ Notifications function executing")
    os.makedirs(reportfolderbase + "iOS 12 Notifications/")

    count = 0
    notdircount = 0
    exportedbplistcount = 0
    unix = datetime.datetime(1970, 1, 1)  # UTC
    cocoa = datetime.datetime(2001, 1, 1)  # UTC
    delta = cocoa - unix

    # with open('NotificationParams.txt', 'r') as f:
    # 	notiparams = [line.strip() for line in f]

    f = open("NotificationParams.txt", "r")
    notiparams = [line.strip() for line in f]
    f.close()

    folder = reportfolderbase + "iOS 12 Notifications/"
    # logfunc("Processing:")
    pathfound = str(filefound[0])
    # logfunc(f'Posix to string is: {pathfound}')
    for filename in glob.iglob(pathfound + "/**", recursive=True):
        # create directory where script is running from
        if os.path.isfile(filename):  # filter dirs
            file_name = os.path.splitext(os.path.basename(filename))[0]
            # create directory
            if "DeliveredNotifications" in file_name:
                # create directory where script is running from
                # logfunc (filename) #full path
                notdircount = notdircount + 1
                # logfunc (os.path.basename(file_name)) #filename with  no extension
                openplist = os.path.basename(
                    os.path.normpath(filename)
                )  # filename with extension
                # logfunc (openplist)
                bundlepath = os.path.basename(
                    os.path.dirname(filename)
                )  # previous directory
                appdirect = folder + "/" + bundlepath
                # logfunc(appdirect)
                os.makedirs(appdirect)

                # open the plist
                p = open(filename, "rb")
                plist = ccl_bplist.load(p)
                plist2 = plist["$objects"]

                long = len(plist2)
                # logfunc (long)
                h = open(
                    "./" + appdirect + "/DeliveredNotificationsReport.html", "w"
                )  # write report
                h.write("<html><body>")
                h.write("<h2>iOS Delivered Notifications Triage Report </h2>")
                h.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                h.write(filename)
                h.write("<br/>")
                h.write("<br/>")

                h.write('<button onclick="hideRows()">Hide rows</button>')
                h.write('<button onclick="showRows()">Show rows</button>')

                f = open("script.txt")
                for line in f:
                    h.write(line)
                f.close()

                h.write("<br>")
                h.write('<table name="hide">')
                h.write('<tr name="hide">')
                h.write("<th>Data type</th>")
                h.write("<th>Value</th>")
                h.write("</tr>")

                h.write('<tr name="hide">')
                h.write("<td>Plist</td>")
                h.write("<td>Initial Values</td>")
                h.write("</tr>")

                test = 0
                for i in range(0, long):
                    try:
                        if plist2[i]["$classes"]:
                            h.write('<tr name="hide">')
                            h.write("<td>$classes</td>")
                            ob6 = str(plist2[i]["$classes"])
                            h.write("<td>")
                            h.write(str(ob6))
                            h.write("</td>")
                            h.write("</tr>")
                            test = 1
                    except:
                        pass
                    try:
                        if plist2[i]["$class"]:
                            h.write('<tr name="hide">')
                            h.write("<td>$class</td>")
                            ob5 = str(plist2[i]["$class"])
                            h.write("<td>")
                            h.write(str(ob5))
                            h.write("</td>")
                            h.write("</tr>")
                            test = 1
                    except:
                        pass
                    try:
                        if plist2[i]["NS.keys"]:
                            h.write('<tr name="hide">')
                            h.write("<td>NS.keys</td>")
                            ob0 = str(plist2[i]["NS.keys"])
                            h.write("<td>")
                            h.write(str(ob0))
                            h.write("</td>")
                            h.write("</tr>")
                            test = 1
                    except:
                        pass
                    try:
                        if plist2[i]["NS.objects"]:
                            ob1 = str(plist2[i]["NS.objects"])
                            h.write('<tr name="hide">')
                            h.write("<td>NS.objects</td>")
                            h.write("<td>")
                            h.write(str(ob1))
                            h.write("</td>")
                            h.write("</tr>")

                            test = 1
                    except:
                        pass
                    try:
                        if plist2[i]["NS.time"]:
                            dia = str(plist2[i]["NS.time"])
                            dias = dia.rsplit(".", 1)[0]
                            timestamp = (
                                datetime.datetime.fromtimestamp(int(dias)) + delta
                            )
                            # logfunc (timestamp)

                            h.write("<tr>")
                            h.write("<td>Time UTC</td>")
                            h.write("<td>")
                            h.write(str(timestamp))
                            # h.write(str(plist2[i]['NS.time']))
                            h.write("</td>")
                            h.write("</tr>")

                            test = 1
                    except:
                        pass
                    try:
                        if plist2[i]["NS.base"]:
                            ob2 = str(plist2[i]["NS.objects"])
                            h.write('<tr name="hide">')
                            h.write("<td>NS.base</td>")
                            h.write("<td>")
                            h.write(str(ob2))
                            h.write("</td>")
                            h.write("</tr>")

                            test = 1
                    except:
                        pass
                    try:
                        if plist2[i]["$classname"]:
                            ob3 = str(plist2[i]["$classname"])
                            h.write('<tr name="hide">')
                            h.write("<td>$classname</td>")
                            h.write("<td>")
                            h.write(str(ob3))
                            h.write("</td>")
                            h.write("</tr>")

                            test = 1
                    except:
                        pass
                    """
					try:
						
							h.write('<tr>')
							h.write('<td>ASCII</td>')
							h.write('<td>'+str(plist2[i])+'</td>')
							h.write('</tr>')
							
							test = 1
					except:
						pass
					"""
                    try:
                        if test == 0:
                            if (plist2[i]) == "AppNotificationMessage":
                                h.write("</table>")
                                h.write("<br>")
                                h.write("<table>")
                                h.write("<tr>")
                                h.write("<th>Data type</th>")
                                h.write("<th>Value</th>")
                                h.write("</tr>")

                                h.write('<tr name="hide">')
                                h.write("<td>ASCII</td>")
                                h.write("<td>" + str(plist2[i]) + "</td>")
                                h.write("</tr>")

                            else:
                                if plist2[i] in notiparams:
                                    h.write('<tr name="hide">')
                                    h.write("<td>ASCII</td>")
                                    h.write("<td>" + str(plist2[i]) + "</td>")
                                    h.write("</tr>")
                                elif plist2[i] == " ":
                                    h.write('<tr name="hide">')
                                    h.write("<td>Null</td>")
                                    h.write("<td>" + str(plist2[i]) + "</td>")
                                    h.write("</tr>")
                                else:
                                    h.write("<tr>")
                                    h.write("<td>ASCII</td>")
                                    h.write("<td>" + str(plist2[i]) + "</td>")
                                    h.write("</tr>")

                    except:
                        pass

                    test = 0

                    # h.write('test')

                for dict in plist2:
                    liste = dict
                    types = type(liste)
                    # logfunc (types)
                    try:
                        for k, v in liste.items():
                            if k == "NS.data":
                                chk = str(v)
                                reduced = chk[2:8]
                                # logfunc (reduced)
                                if reduced == "bplist":
                                    count = count + 1
                                    binfile = open(
                                        "./"
                                        + appdirect
                                        + "/incepted"
                                        + str(count)
                                        + ".bplist",
                                        "wb",
                                    )
                                    binfile.write(v)
                                    binfile.close()

                                    procfile = open(
                                        "./"
                                        + appdirect
                                        + "/incepted"
                                        + str(count)
                                        + ".bplist",
                                        "rb",
                                    )
                                    secondplist = ccl_bplist.load(procfile)
                                    secondplistint = secondplist["$objects"]
                                    logfunc("Bplist processed and exported.")
                                    exportedbplistcount = exportedbplistcount + 1
                                    h.write('<tr name="hide">')
                                    h.write("<td>NS.data</td>")
                                    h.write("<td>")
                                    h.write(str(secondplistint))
                                    h.write("</td>")
                                    h.write("</tr>")

                                    procfile.close()
                                    count = 0
                                else:
                                    h.write('<tr name="hide">')
                                    h.write("<td>NS.data</td>")
                                    h.write("<td>")
                                    h.write(str(secondplistint))
                                    h.write("</td>")
                                    h.write("</tr>")
                    except:
                        pass
                h.close()
            elif "AttachmentsList" in file_name:
                test = 0  # future development

    path = reportfolderbase + "/iOS 12 Notifications/"
    dict = {}
    files = os.listdir(path)
    for name in files:
        try:
            size = os.path.getsize(f"{path}{name}/DeliveredNotificationsReport.html")
            key = f'<a href = "{name}/DeliveredNotificationsReport.html" target="content">{name}</a>'
            dict[key] = size
        except NotADirectoryError as nade:
            logfunc(nade)
            pass

    filedatahtml = open(path + "iOS12_Notifications.html", mode="a+")
    filedatahtml.write(
        '<html><body><table class="table sticky"><style> table, th, td {border: 1px solid black; border-collapse: collapse;} tr:nth-child(even) {background-color: #f2f2f2;} </style><tr><th>Notifications by GUID (iOS13) or Bundle ID (iOS12) </th><th>Notification size in KB</th></tr>'
    )
    for k, v in dict.items():
        v = v / 1000
        # logfunc(f'{k} -> {v}')
        filedatahtml.write(f"<tr><td>{k}</td><td>{v}</td></tr>")
    filedatahtml.write("</table></body></html>")
    filedatahtml.close()

    logfunc("Total notification directories processed:" + str(notdircount))
    logfunc("Total exported bplists from notifications:" + str(exportedbplistcount))
    if notdircount == 0:
        logfunc("No notifications located.")
    logfunc("iOS 12+ Notifications function completed.")


def ktx(filefound):
    logfunc(f"Snapshots KTX file finder function executing")
    logfunc(f"Snapshots located: {len(filefound)}")
    outpath = reportfolderbase + "Snapshots_KTX_Files/"
    outktx = outpath + "KTX_Files/"
    os.mkdir(outpath)
    os.mkdir(outktx)
    nl = "\n"

    filedata = open(
        outpath + "_Snapshot_KTX_Files_List.csv", mode="a+", encoding="utf8"
    )
    filewrite = csv.writer(
        filedata, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
    )
    filewrite.writerow(["Path", "Filename"])
    filedata.close()

    filedatahtml = open(outpath + "KTX_Files.html", mode="a+")
    filedatahtml.write("<html><body>")
    filedatahtml.write("<h2>KTX Files Report </h2>")
    filedatahtml.write(
        "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
    )
    filedatahtml.write("<br/>")
    filedatahtml.write(
        f"Extracted KTX files can be examined in the {outpath}KTX_Files/ directory.<br>"
    )
    filedatahtml.write('<table class="table sticky">')
    filedatahtml.write("<tr><th>Path</th><th>Filename</th></tr>")

    for filename in filefound:
        p = pathlib.Path(filename)
        head1, tail1 = os.path.split(filename)
        head2, tail2 = os.path.split(head1)

        tail = ""
        head = ""
        fullp = ""
        for x in p.parts:
            head1, tail = os.path.split(head1)
            fullp = tail + "/" + fullp
            if tail == "Library":
                fullpw = fullp

        if os.path.exists(outktx + fullpw):
            pass
        else:
            os.makedirs(outktx + fullpw)
        # get the name, filepath write to csv in outpath _KTX_Files_Report.csv

        filedata = open(
            outpath + "_Snapshot_KTX_Files_List.csv", mode="a+", encoding="utf8"
        )
        filewrite = csv.writer(
            filedata, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        filewrite.writerow([filename, tail1])
        filedatahtml.write(f"<tr><td>{filename}</td><td>{tail1}</td></tr>")
        filedata.close()
        if os.path.exists(filename):
            shutil.copy2(filename, outktx + fullpw)
    filedatahtml.close()
    logfunc(f"Snapshots KTX file finder function completed.")


def calhist(filefound):
    db = sqlite3.connect(filefound[0])
    cursor = db.cursor()
    cursor.execute(
        """
	SELECT 
			ZADDRESS AS "ADDRESS", 
			ZANSWERED AS "WAS ANSWERED", 
			ZCALLTYPE AS "CALL TYPE", 
			ZORIGINATED AS "ORIGINATED", 
			ZDURATION AS "DURATION (IN SECONDS)",
			ZISO_COUNTRY_CODE as "ISO COUNTY CODE",
			ZLOCATION AS "LOCATION", 
			ZSERVICE_PROVIDER AS "SERVICE PROVIDER",
			DATETIME(ZDATE+978307200,'UNIXEPOCH') AS "TIMESTAMP"
		FROM ZCALLRECORD """
    )

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Call History function executing")
        os.makedirs(reportfolderbase + "Call History/")
        with open(
            reportfolderbase + "Call History/Call History.html", "w", encoding="utf8"
        ) as f:
            f.write("<html><body>")
            f.write("<h2> Call History report</h2>")
            f.write(f"Call History entries: {usageentries}<br>")
            f.write(f"Call History database located at: {filefound[0]}<br>")
            f.write(
                "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
            )
            f.write("<br/>")
            f.write("")
            f.write(f'<table class="table sticky">')
            f.write(
                f"<tr><th>Address</th><th>Was Answered</th><th>Call Type</th><th>Originated</th><th>Duration in Secs</th><th>ISO County Code</th><th>Location</th><th>Service Provider</th><th>Timestamp</th></tr>"
            )
            for row in all_rows:
                an = str(row[0])
                an = an.replace("b'", "")
                an = an.replace("'", "")

                f.write(
                    f"<tr><td>{an}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td></tr>"
                )
            f.write(f"</table></body></html>")
            logfunc(f"Call History function completed")
    else:
        logfunc("No call history available")


def smschat(filefound):
    db = sqlite3.connect(filefound[0])
    cursor = db.cursor()
    try:
        cursor.execute(
            """
		SELECT
				CASE
					WHEN LENGTH(MESSAGE.DATE)=18 THEN DATETIME(MESSAGE.DATE/1000000000+978307200,'UNIXEPOCH')
					WHEN LENGTH(MESSAGE.DATE)=9 THEN DATETIME(MESSAGE.DATE + 978307200,'UNIXEPOCH')
					ELSE "N/A"
		    		END "MESSAGE DATE",			
				CASE 
					WHEN LENGTH(MESSAGE.DATE_DELIVERED)=18 THEN DATETIME(MESSAGE.DATE_DELIVERED/1000000000+978307200,"UNIXEPOCH")
					WHEN LENGTH(MESSAGE.DATE_DELIVERED)=9 THEN DATETIME(MESSAGE.DATE_DELIVERED+978307200,"UNIXEPOCH")
					ELSE "N/A"
				END "DATE DELIVERED",
				CASE 
					WHEN LENGTH(MESSAGE.DATE_READ)=18 THEN DATETIME(MESSAGE.DATE_READ/1000000000+978307200,"UNIXEPOCH")
					WHEN LENGTH(MESSAGE.DATE_READ)=9 THEN DATETIME(MESSAGE.DATE_READ+978307200,"UNIXEPOCH")
					ELSE "N/A"
				END "DATE READ",
				MESSAGE.TEXT as "MESSAGE",
				HANDLE.ID AS "CONTACT ID",
				MESSAGE.SERVICE AS "SERVICE",
				MESSAGE.ACCOUNT AS "ACCOUNT",
				MESSAGE.IS_DELIVERED AS "IS DELIVERED",
				MESSAGE.IS_FROM_ME AS "IS FROM ME",
				ATTACHMENT.FILENAME AS "FILENAME",
				ATTACHMENT.MIME_TYPE AS "MIME TYPE",
				ATTACHMENT.TRANSFER_NAME AS "TRANSFER TYPE",
				ATTACHMENT.TOTAL_BYTES AS "TOTAL BYTES"
			FROM MESSAGE
			LEFT OUTER JOIN MESSAGE_ATTACHMENT_JOIN ON MESSAGE.ROWID = MESSAGE_ATTACHMENT_JOIN.MESSAGE_ID
			LEFT OUTER JOIN ATTACHMENT ON MESSAGE_ATTACHMENT_JOIN.ATTACHMENT_ID = ATTACHMENT.ROWID
			LEFT OUTER JOIN HANDLE ON MESSAGE.HANDLE_ID = HANDLE.ROWID
			"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"SMS Chat function executing")
            os.makedirs(reportfolderbase + "SMS Chat/")
            with open(
                reportfolderbase + "SMS Chat/SMS Chat.html", "w", encoding="utf8"
            ) as f:
                f.write("<html><body>")
                f.write("<h2> SMS Chat report</h2>")
                f.write(f"SMS Chat entries: {usageentries}<br>")
                f.write(f"SMS Chat database located at: {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Message Date</th><th>Date Delivered</th><th>Date Read</th><th>Message</th><th>Contact ID</th><th>Service</th><th>Account</th><th>Is Delivered</th><th>Is from Me</th><th>Filename</th><th>MIME Type</th><th>Transfer Type</th><th>Total Bytes</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td><td>{row[10]}</td><td>{row[11]}</td><td>{row[12]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"SMS Chat function completed")
        else:
            logfunc("No SMS Chats available")
    except:
        logfunc("Error on SMS Chat function. Possible empty database.")

    db = sqlite3.connect(filefound[0])
    cursor = db.cursor()
    try:
        cursor.execute(
            '''
		SELECT
				CASE
		 			WHEN LENGTH(MESSAGE.DATE)=18 THEN DATETIME(MESSAGE.DATE/1000000000+978307200,'UNIXEPOCH')
		 			WHEN LENGTH(MESSAGE.DATE)=9 THEN DATETIME(MESSAGE.DATE + 978307200,'UNIXEPOCH')
		 			ELSE "N/A"
				END "MESSAGE DATE",
				CASE 
					WHEN LENGTH(MESSAGE.DATE_DELIVERED)=18 THEN DATETIME(MESSAGE.DATE_DELIVERED/1000000000+978307200,"UNIXEPOCH")
					WHEN LENGTH(MESSAGE.DATE_DELIVERED)=9 THEN DATETIME(MESSAGE.DATE_DELIVERED+978307200,"UNIXEPOCH")
					ELSE "N/A"
				END "DATE DELIVERED",
				CASE 
					WHEN LENGTH(MESSAGE.DATE_READ)=18 THEN DATETIME(MESSAGE.DATE_READ/1000000000+978307200,"UNIXEPOCH")
					WHEN LENGTH(MESSAGE.DATE_READ)=9 THEN DATETIME(MESSAGE.DATE_READ+978307200,"UNIXEPOCH")
					ELSE "N/A"
				END "DATE READ",
				MESSAGE.TEXT as "MESSAGE",
				HANDLE.ID AS "CONTACT ID",
				MESSAGE.SERVICE AS "SERVICE",
				MESSAGE.ACCOUNT AS "ACCOUNT",
				MESSAGE.IS_DELIVERED AS "IS DELIVERED",
				MESSAGE.IS_FROM_ME AS "IS FROM ME",
				ATTACHMENT.FILENAME AS "FILENAME",
				ATTACHMENT.MIME_TYPE AS "MIME TYPE",
				ATTACHMENT.TRANSFER_NAME AS "TRANSFER TYPE",
				ATTACHMENT.TOTAL_BYTES AS "TOTAL BYTES"
			FROM MESSAGE
			LEFT OUTER JOIN MESSAGE_ATTACHMENT_JOIN ON MESSAGE.ROWID = MESSAGE_ATTACHMENT_JOIN.MESSAGE_ID
			LEFT OUTER JOIN ATTACHMENT ON MESSAGE_ATTACHMENT_JOIN.ATTACHMENT_ID = ATTACHMENT.ROWID
			LEFT OUTER JOIN HANDLE ON MESSAGE.HANDLE_ID = HANDLE.ROWID
			WHERE "DATE DELIVERED" IS NOT "N/A"'''
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"SMS Chat Message Delivered function executing")
            with open(
                reportfolderbase + "SMS Chat/SMS Message Delivered.html",
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2> SMS Chat Message Delivered report</h2>")
                f.write(f"SMS Chat Message Delivered entries: {usageentries}<br>")
                f.write(
                    f"SMS Chat Message Delivered database located at: {filefound[0]}<br>"
                )
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Message Date</th><th>Date Delivered</th><th>Date Read</th><th>Message</th><th>Contact ID</th><th>Service</th><th>Account</th><th>Is Delivered</th><th>Is from Me</th><th>Filename</th><th>MIME Type</th><th>Transfer Type</th><th>Total Bytes</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td><td>{row[10]}</td><td>{row[11]}</td><td>{row[12]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"SMS Chat Message function completed")
        else:
            logfunc("No SMS Chat Message Delivered available")
    except:
        logfunc(
            "Error on SMS Chat Message Delivered function. Possible empty database."
        )

    db = sqlite3.connect(filefound[0])
    cursor = db.cursor()
    try:
        cursor.execute(
            '''
		SELECT
				CASE
		 			WHEN LENGTH(MESSAGE.DATE)=18 THEN DATETIME(MESSAGE.DATE/1000000000+978307200,'UNIXEPOCH')
		 			WHEN LENGTH(MESSAGE.DATE)=9 THEN DATETIME(MESSAGE.DATE + 978307200,'UNIXEPOCH')
		 			ELSE "N/A"
		     		END "MESSAGE DATE",
				CASE 
					WHEN LENGTH(MESSAGE.DATE_DELIVERED)=18 THEN DATETIME(MESSAGE.DATE_DELIVERED/1000000000+978307200,"UNIXEPOCH")
					WHEN LENGTH(MESSAGE.DATE_DELIVERED)=9 THEN DATETIME(MESSAGE.DATE_DELIVERED+978307200,"UNIXEPOCH")
					ELSE "N/A"
				END "DATE DELIVERED",
				CASE 
					WHEN LENGTH(MESSAGE.DATE_READ)=18 THEN DATETIME(MESSAGE.DATE_READ/1000000000+978307200,"UNIXEPOCH")
					WHEN LENGTH(MESSAGE.DATE_READ)=9 THEN DATETIME(MESSAGE.DATE_READ+978307200,"UNIXEPOCH")
					ELSE "N/A"
				END "DATE READ",
				MESSAGE.TEXT as "MESSAGE",
				HANDLE.ID AS "CONTACT ID",
				MESSAGE.SERVICE AS "SERVICE",
				MESSAGE.ACCOUNT AS "ACCOUNT",
				MESSAGE.IS_DELIVERED AS "IS DELIVERED",
				MESSAGE.IS_FROM_ME AS "IS FROM ME",
				ATTACHMENT.FILENAME AS "FILENAME",
				ATTACHMENT.MIME_TYPE AS "MIME TYPE",
				ATTACHMENT.TRANSFER_NAME AS "TRANSFER TYPE",
				ATTACHMENT.TOTAL_BYTES AS "TOTAL BYTES"
			FROM MESSAGE
			LEFT OUTER JOIN MESSAGE_ATTACHMENT_JOIN ON MESSAGE.ROWID = MESSAGE_ATTACHMENT_JOIN.MESSAGE_ID
			LEFT OUTER JOIN ATTACHMENT ON MESSAGE_ATTACHMENT_JOIN.ATTACHMENT_ID = ATTACHMENT.ROWID
			LEFT OUTER JOIN HANDLE ON MESSAGE.HANDLE_ID = HANDLE.ROWID
			WHERE "DATE READ" IS NOT "N/A"'''
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"SMS Chat Message Read function executing")
            with open(
                reportfolderbase + "SMS Chat/SMS Message Read.html",
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2> SMS Chat Message Read report</h2>")
                f.write(f"SMS Chat Message Read entries: {usageentries}<br>")
                f.write(f"SMS Chat Message Readdatabase located at: {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Message Date</th><th>Date Delivered</th><th>Date Read</th><th>Message</th><th>Contact ID</th><th>Service</th><th>Account</th><th>Is Delivered</th><th>Is from Me</th><th>Filename</th><th>MIME Type</th><th>Transfer Type</th><th>Total Bytes</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td><td>{row[10]}</td><td>{row[11]}</td><td>{row[12]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"SMS Chat Message Read function completed")
        else:
            logfunc("No SMS Chat Message Read available")
    except:
        logfunc("Error on SMS Chat Message Read available. Posible empty database. ")


def safari(filefound):
    db = sqlite3.connect(filefound[0])
    cursor = db.cursor()
    try:
        cursor.execute(
            """
		SELECT 
				HISTORY_ITEMS.URL AS "URL",
				HISTORY_ITEMS.VISIT_COUNT AS "VISIT COUNT",
				HISTORY_VISITS.TITLE AS "TITLE",
				CASE HISTORY_VISITS.ORIGIN
					WHEN 1 THEN "ICLOUD SYNCED DEVICE"
					WHEN 0 THEN "VISTED FROM THIS DEVICE"
				END "ICLOUD SYNC",
				HISTORY_VISITS.LOAD_SUCCESSFUL AS "LOAD SUCCESSFUL",
				HISTORY_VISITS.REDIRECT_SOURCE AS "REDIRECT SOURCE",
				HISTORY_VISITS.REDIRECT_DESTINATION AS "REDIRECT DESTINATION",
				DATETIME(HISTORY_VISITS.VISIT_TIME+978307200,'UNIXEPOCH') AS "VISIT TIME",
				HISTORY_VISITS.ID AS "HISTORY ITEM ID"
			FROM HISTORY_ITEMS
			LEFT OUTER JOIN HISTORY_VISITS ON HISTORY_ITEMS.ID == HISTORY_VISITS.HISTORY_ITEM
		"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Safari History function executing")
            os.makedirs(reportfolderbase + "Safari/")
            with open(
                reportfolderbase + "Safari/Safari History.html", "w", encoding="utf8"
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Safari History report</h2>")
                f.write(f"Safari History entries: {usageentries}<br>")
                f.write(f"Safari History database located at: {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>URL</th><th>Visit Count</th><th>Title</th><th>Icloud Sync</th><th>Load Sucessful</th><th>Redirect Source</th><th>Redirect Destination</th><th>Visit Time</th><th>History Item ID</th></tr>"
                )
                for row in all_rows:
                    url = textwrap.fill(row[0])
                    f.write(
                        f"<tr><td>{url}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"Safari History function completed")
        else:
            logfunc("No Safari History available")
    except:
        logfunc("Error on Safari History function.")


def queryp(filefound):
    try:
        db = sqlite3.connect(filefound[0])
        cursor = db.cursor()
        cursor.execute(
            """
		select 
				content,
				isSent,
				conversationId,
				id,
				uuid,
				datetime(creationTimestamp, "UNIXEPOCH", "LOCALTIME") as START
				from messages
		"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Query Predictions function executing")
            os.makedirs(reportfolderbase + "Query Predictions/")
            with open(
                reportfolderbase + "Query Predictions/Query Predictions.html",
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Query Predictions report</h2>")
                f.write(f"Query Predictions entries: {usageentries}<br>")
                f.write(f"Query Predictions database located at: {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Content</th><th>Is Sent</th><th>Conversation ID</th><th>ID</th><th>UUID</th><th>Start</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"Query Predictions function completed")
        else:
            logfunc("No Query Predictions available")
    except:
        logfunc("Error in the Query Predictions Section.")


def powerlog(filefound):
    os.makedirs(reportfolderbase + "Powerlog/")
    logfunc("Powerlog function executing")
    try:
        db = sqlite3.connect(filefound[0])
        cursor = db.cursor()
        cursor.execute(
            """
		SELECT
			   DATETIME(TIMESTAMP, 'unixepoch') AS TIMESTAMP,
			   DATETIME(START, 'unixepoch') AS "START",
			   DATETIME(END, 'unixepoch') AS "END",
			   STATE as "STATE",
			   FINISHED as "FINISHED",
			   HASERROR AS "HAS ERROR",
			   ID AS "PLXPCAGENT_EVENTPOINT_MOBILEBACKUPEVENTS TABLE ID" 
			FROM
			   PLXPCAGENT_EVENTPOINT_MOBILEBACKUPEVENTS		
		"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Powerlog Mobile Backup Events executing")
            with open(
                reportfolderbase + "Powerlog/Mobile Backup Events.html",
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Powerlog Mobile Backup Events report</h2>")
                f.write(f"Mobile Backup Events entries: {usageentries}<br>")
                f.write(f"Mobile Backup Events database located at: {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Timestamp</th><th>Start</th><th>End</th><th>State</th><th>Finished</th><th>Has Error</th><th>ID</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"Powerlog Mobile Backup Events function completed")
        else:
            logfunc("No Powerlog Mobile Backup Events available")
    except:
        logfunc("Error in Powerlog Mobile Backup Events Section.")

    try:
        db = sqlite3.connect(filefound[0])
        cursor = db.cursor()
        cursor.execute(
            """
		SELECT
				DATETIME(WIFIPROPERTIES_TIMESTAMP + SYSTEM, 'unixepoch') AS ADJUSTED_TIMESTAMP,
				CURRENTSSID,
				CURRENTCHANNEL,
				DATETIME(TIME_OFFSET_TIMESTAMP, 'unixepoch') AS OFFSET_TIMESTAMP,
				SYSTEM AS TIME_OFFSET,
				WIFIPROPERTIES_ID AS "PLWIFIAGENT_EVENTBACKWARD_CUMULATIVEPROPERTIES TABLE ID" 
		   	FROM
		      (
				SELECT
					WIFIPROPERTIES_ID,
					WIFIPROPERTIES_TIMESTAMP,
					TIME_OFFSET_TIMESTAMP,
					MAX(TIME_OFFSET_ID) AS MAX_ID,
					CURRENTSSID,
					CURRENTCHANNEL,
					SYSTEM
				FROM
		            (
					SELECT
						PLWIFIAGENT_EVENTBACKWARD_CUMULATIVEPROPERTIES.TIMESTAMP AS WIFIPROPERTIES_TIMESTAMP,
						CURRENTSSID,
						CURRENTCHANNEL,
						PLWIFIAGENT_EVENTBACKWARD_CUMULATIVEPROPERTIES.ID AS "WIFIPROPERTIES_ID" ,
						PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
						PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
						PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM
					FROM
						PLWIFIAGENT_EVENTBACKWARD_CUMULATIVEPROPERTIES
					LEFT JOIN
						PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET 
		            )
		            AS WIFIPROPERTIES_STATE 
		        GROUP BY
					WIFIPROPERTIES_ID 
		      )	
		"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Powerlog WIFI Properties executing")
            with open(
                reportfolderbase + "Powerlog/Powerlog WIFI Properties.html",
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Powerlog WIFI Properties Events report</h2>")
                f.write(f"Powerlog WIFI Properties entries: {usageentries}<br>")
                f.write(
                    f"Powerlog WIFI Properties database located at: {filefound[0]}<br>"
                )
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Adj. Timestamp</th><th>Current SSID</th><th>Current Channel</th><th>Offset Timestamp</th><th>Time Offset</th><th>ID</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"Powerlog WIFI Properties function completed")
        else:
            logfunc("No Powerlog WIFI Properties available")
    except:
        logfunc("Error in Powerlog WIFI Properties Section.")

    try:
        db = sqlite3.connect(filefound[0])
        cursor = db.cursor()
        cursor.execute(
            """
		SELECT
				DATETIME(SBAUTOLOCK_TIMESTAMP + SYSTEM, 'unixepoch') AS ADJUSTED_TIMESTAMP,
				AUTOLOCKTYPE AS "AUTO LOCK TYPE",
				DATETIME(TIME_OFFSET_TIMESTAMP, 'unixepoch') AS OFFSET_TIMESTAMP,
				SYSTEM AS TIME_OFFSET,
				SBAUTOLOCK_ID AS "PLSPRINGBOARDAGENT_EVENTPOINT_SBAUTOLOCK TABLE ID" 
			FROM
			(
				SELECT
					SBAUTOLOCK_ID,
					SBAUTOLOCK_TIMESTAMP,
					TIME_OFFSET_TIMESTAMP,
					MAX(TIME_OFFSET_ID) AS MAX_ID,
					AUTOLOCKTYPE,
					SYSTEM
				FROM
				(
				SELECT
					PLSPRINGBOARDAGENT_EVENTPOINT_SBAUTOLOCK.TIMESTAMP AS SBAUTOLOCK_TIMESTAMP,
					AUTOLOCKTYPE,
					PLSPRINGBOARDAGENT_EVENTPOINT_SBAUTOLOCK.ID AS "SBAUTOLOCK_ID" ,
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM
				FROM
					PLSPRINGBOARDAGENT_EVENTPOINT_SBAUTOLOCK
				LEFT JOIN
					PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET 
				)
				AS SBAUTOLOCK_STATE 
				GROUP BY
					SBAUTOLOCK_ID 
			)
		"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Powerlog Device Screen Autolock executing")
            with open(
                reportfolderbase + "Powerlog/Device Screen Autolock.html",
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Powerlog Device Screen Autolock report</h2>")
                f.write(f"Powerlog Device Screen Autolock entries: {usageentries}<br>")
                f.write(
                    f"Powerlog Device Screen Autolock located at: {filefound[0]}<br>"
                )
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Adj Timestamp</th><th>Auto Lock Type</th><th>Offset Timestamp</th><th>Time Offset</th><th>ID</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"Powerlog Device Screen Autolock function completed")
        else:
            logfunc("No Powerlog Device Screen Autolock available")
    except:
        logfunc("Error in Powerlog Device Screen Autolock Section.")

    try:
        db = sqlite3.connect(filefound[0])
        cursor = db.cursor()
        cursor.execute(
            """
		SELECT
				DATETIME(APPDELETEDDATE, 'unixepoch') AS "APP DELETED DATE",
				DATETIME(TIMESTAMP, 'unixepoch') AS TIMESTAMP,
				APPNAME AS "APP NAME",
				APPEXECUTABLE AS "APP EXECUTABLE NAME",
				APPBUNDLEID AS "BUNDLE ID",
				APPBUILDVERSION AS "APP BUILD VERSION",
				APPBUNDLEVERSION AS "APP BUNDLE VERSION",
				APPTYPE AS "APP TYPE",
				ID AS "PLAPPLICATIONAGENT_EVENTNONE_ALLAPPS TABLE ID" 
			FROM
				PLAPPLICATIONAGENT_EVENTNONE_ALLAPPS 
			WHERE
				APPDELETEDDATE > 0	
		"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Powerlog App Deletion Events executing")
            with open(
                reportfolderbase + "Powerlog/App Deletion.html", "w", encoding="utf8"
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Powerlog App Deletion Events report</h2>")
                f.write(f"Powerlog App Deletion  Events entries: {usageentries}<br>")
                f.write(
                    f"Powerlog App Deletion  Events database located at: {filefound[0]}<br>"
                )
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>App Deleted Date</th><th>Timestamp</th><th>App Name</td><td>Executable Name</td><td>Bundle ID</td><td>App Build Version</td><td>App Bundle Version</td><td>App Type</td><td>ID</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"Powerlog App DeletionEvents function completed")
        else:
            logfunc("No Powerlog App Deletion Events available")
    except:
        logfunc("Error in Powerlog App Deletion Events Section.")

    try:
        db = sqlite3.connect(filefound[0])
        cursor = db.cursor()
        cursor.execute(
            """select 
		ID,
		datetime(timestamp, 'UNIXEPOCH', 'LOCALTIME') as timestart,
		datetime(timestampEnd, 'UNIXEPOCH', 'LOCALTIME') as timeend,
		ProcessName,
		CellIn,
		CellOut,
		WifiIn,
		WifiOut
		FROM
		PLProcessNetworkAgent_EventInterval_UsageDiff
		"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Powerlog Network Data executing")
            with open(
                reportfolderbase + "Powerlog/Network Data.html", "w", encoding="utf8"
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Powerlog Network Data report</h2>")
                f.write(f"Powerlog Network Data entries: {usageentries}<br>")
                f.write(
                    f"Powerlog Network Data database located at: {filefound[0]}<br>"
                )
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>ID</th><th>Time Start</th><th>Time End</th><th>Process Name</th><th>Mobile Bytes In</th><th>Mobile Bytes Out</th><th>WiFi Bytes In</th><th>WiFi Out</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"Powerlog Network Data function completed")
        else:
            logfunc("No Powerlog Network Data available")
    except:
        logfunc("Error in Powerlog Network Data Section.")
    logfunc("Powerlog function completed.")


def delphotos(filefound):
    db = sqlite3.connect(filefound[0])
    cursor = db.cursor()
    try:
        cursor.execute(
            """
		Select
		z_pk,
		zfilename AS "File Name",
		zduration AS "Duration in Seconds",
		case
		when ztrashedstate = 1 then "Deleted"
		else "N/A"
		end AS "Is Deleted",
		case
		when zhidden =1 then "Hidden"
		else 'N/A'
		end AS "Is Hidden",
		datetime(ztrasheddate+978307200,'unixepoch','localtime') AS "Date Deleted",
		datetime(zaddeddate+978307200,'unixepoch','localtime') AS "Date Added",
		datetime(zdatecreated+978307200,'unixepoch','localtime') AS "Date Created",
		datetime(zmodificationdate+978307200,'unixepoch','localtime') AS "Date Modified",
		zdirectory AS "File Path"
		from zgenericasset
			"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Photos.sqlite metadata function executing")
            os.makedirs(reportfolderbase + "Photos.sqlite Metadata/")
            with open(
                reportfolderbase + "Photos.sqlite Metadata/Photos.sqLite DB.html",
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Photos.sqlite Metadata report</h2>")
                f.write(f"Photos.sqlite Metadata entries: {usageentries}<br>")
                f.write(f"Photos.sqlite database located at: {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Primary Key</th><th>File Name</th><th>Duration in seconds</th><th>Is Deleted</th><th>Is Hidden</th><th>Date Deleted</th><th>Date Added</th><th>Date Created</th><th>Date Modified</th><th>File Path</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"Photos.sqlite Metadata function completed")
        else:
            logfunc("No Photos.sqlite Metadata available")
    except:
        logfunc("Error on Photos.sqlite function.")


def timezone(filefound):
    logfunc(f"Timezone function executing")
    p = open(filefound[0], "rb")
    plist = plistlib.load(p)

    # create html headers
    filedatahtml = open(reportfolderbase + "Build Info/TimeZone.html", mode="a+")
    filedatahtml.write("<html><body>")
    filedatahtml.write("<h2>TimeZone Report </h2>")
    filedatahtml.write(f"Timezone info located at: {filefound[0]}<br>")
    filedatahtml.write(
        "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
    )
    filedatahtml.write("<table>")
    # filedatahtml.write(f'<tr><td colspan = "2">{filefound[0]}</td></tr>')
    filedatahtml.write("<tr><td>Key</td><td>Value</td></tr>")

    for key, val in plist.items():
        filedatahtml.write(f"<tr><td>{key}</td><td>{val}</td></tr>")

    filedatahtml.write("</table></html>")
    filedatahtml.close()
    logfunc(f"Timezone function completed.")


def webclips(filefound):
    logfunc("Webclips function executing")
    try:
        webclip_data = {}
        for path_val in filefound:
            # Extract the unique identifier
            pathstr = str(path_val).replace("\\", "/")

            unique_id = pathstr.split("/WebClips/")[1].split(".webclip/")[0]
            if unique_id != "" and unique_id not in webclip_data:
                webclip_data[unique_id] = {
                    "Info": "",
                    "Icon_path": "",
                    "Icon_data": "",
                    "Title": "",
                    "URL": "",
                }

            # Is this the path to the info.plist?
            if "Info.plist" in pathstr:
                webclip_data[unique_id]["Info"] = path_val

            # Is this the path to the icon?
            if "icon.png" in pathstr:
                webclip_data[unique_id]["Icon_path"] = path_val

        logfunc(f"Webclips found: {len(webclip_data)} ")

        for unique_id, data in webclip_data.items():
            # Info plist information
            info_plist_raw = open(data["Info"], "rb")
            info_plist = plistlib.load(info_plist_raw)
            webclip_data[unique_id]["Title"] = info_plist["Title"]
            webclip_data[unique_id]["URL"] = info_plist["URL"]
            info_plist_raw.close()

            # Open and convert icon into b64 for serialisation in report
            icon_data_raw = open(data["Icon_path"], "rb")
            icon_data = base64.b64encode(icon_data_raw.read()).decode("utf-8")
            webclip_data[unique_id]["Icon_data"] = icon_data
            icon_data_raw.close()

        # Create the report
        g = open(reportfolderbase + "Icon Positions/WebClips.html", "w")
        g.write("<html>")
        g.write(f"<p><table><body>")
        g.write(
            "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
        )
        for unique_id, data in webclip_data.items():
            g.write("<tr>")
            g.write(f'<td><img src="data:image/png;base64,{data["Icon_data"]}"></td>')
            g.write(
                f"<td><b>UID:{unique_id}</b><br>"
                f'Title: {data["Title"]}<br>'
                f'URL: {data["URL"]}</td>'
            )
            g.write("</tr>")
        g.write("</table></html>")
        g.close()
    except Exception:
        logfunc("Error on Webclips function.")
    logfunc("Webclips function completed")


def healthdb(filefound):
    db = sqlite3.connect(filefound[0])
    cursor = db.cursor()
    try:
        cursor.execute(
            """
		Select
		datetime(samples.start_date+978307200,'unixepoch','localtime') as "Start Date",
		datetime(samples.end_date+978307200,'unixepoch','localtime') as "End Date",
		samples.data_id, 
		case
		when samples.data_type = 3 then "weight"
		when samples.data_type = 7 then "steps"
		when samples.data_type = 8 then "dist in m"
		when samples.data_type = 9 then "resting energy"
		when samples.data_type = 10 then "active energy"
		when samples.data_type = 12 then "flights climbed"
		when samples.data_type = 67 then "weekly calorie goal"
		when samples.data_type = 70 then "watch on"
		when samples.data_type = 75 then "stand"
		when samples.data_type = 76 then "activity"
		when samples.data_type = 79 then "workout"
		when samples.data_type = 83 then "some workouts"
		end as "activity type",
		quantity,
		original_quantity,
		unit_strings.unit_string,
		original_unit,
		correlations.correlation,
		correlations.object,
		correlations.provenance
		string_value,
		metadata_values.data_value,
		metadata_values.numerical_value,
		metadata_values.value_type,
		metadata_keys.key
		from samples
		left outer join quantity_samples on samples.data_id = quantity_samples.data_id
		left outer join unit_strings on quantity_samples.original_unit = unit_strings.RowID
		left outer join correlations on samples.data_id = correlations.object
		left outer join metadata_values on metadata_values.object_id = samples.data_id
		left outer join metadata_keys on metadata_keys.ROWID = metadata_values.key_id
		order by "Start Date" desc
		"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Healthdb_secure.sqlite function executing")
            os.makedirs(reportfolderbase + "HealthDB/")
            with open(
                reportfolderbase + "HealthDB/Healthdb_secure.html", "w", encoding="utf8"
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Healthdb_secure.sqlite report</h2>")
                f.write(f"Healthdb_secure.sqlite entries: {usageentries}<br>")
                f.write(
                    f"Healthdb_secure.sqlite database located at: {filefound[0]}<br>"
                )
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Start Date</th><th>End Date</th><th>Activity Type</th><th>Quantity</th><th>Original Quantity</th><th>Unit String</th><th>Original Unit</th><th>Correlation</th><th>String Value</th><th>Data Value</th><th>Numerical Value</th><th>Value Type</th><th>Key</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td><td>{row[10]}</td><td>{row[11]}</td><td>{row[12]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"Healthdb_secure.sqlite function completed")
        else:
            logfunc("No Healthdb_secure.sqlite available")
    except:
        logfunc("Error on Healthdb_secure.sqlite function.")


def wiloc(filefound):
    logfunc("Wireless Locations function executing")
    os.makedirs(reportfolderbase + "Wireless Locations/")
    try:
        db = sqlite3.connect(filefound[0])
        cursor = db.cursor()
        cursor.execute(
            """SELECT
				MCC AS "MCC",
				MNC AS "MNC",
				CI AS "CI",
				UARFCN AS "UARFCN",
				PID AS "PID",
				ALTITUDE AS "ALTITUDE",
				SPEED AS "SPEED",
				COURSE AS "COURSE",
				CONFIDENCE AS "CONFIDENCE",
				HORIZONTALACCURACY AS "HORIZONTAL ACCURACY",
				VERTICALACCURACY AS "VERTICAL ACCURACY",
				LATITUDE AS "LATITUDE",
				LONGITUDE AS "LONGITUDE",
				DATETIME(TIMESTAMP + 978307200,'UNIXEPOCH') AS "TIMESTAMP"
			FROM LteCellLocation"""
        )
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"LTE cell locations function executing")
            with open(
                reportfolderbase + "Wireless Locations/LTE cell locations.html",
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2> LTE cell locations report</h2>")
                f.write(f"LTE cell locations entries: {usageentries}<br>")
                f.write(f"LTE cell locations database located at: {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>MCC</th><th>MNC</th><th>CI</th><th>UARFCN</th><th>PID</th><th>Altitude</th><th>Speed</th><th>Course</th><th>Confidence</th><th>Hoz. Acc.</th><th>Vert. Acc.</th><th>Latitude</th><th>Longitude</th><th>Timestamp</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td><td>{row[10]}</td><td>{row[11]}</td><td>{row[12]}</td><td>{row[13]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"LTE cell locations function completed")
        else:
            logfunc("No LTE cell locations available")
    except:
        logfunc("Error on LTE cell locations function.")

    try:
        db = sqlite3.connect(filefound[0])
        cursor = db.cursor()
        cursor.execute(
            """SELECT
				MCC AS "MCC",
				SID AS "SID",
				NID AS "NID",
				BSID AS "BSID",
				ZONEID AS "ZONEID",
				BANDCLASS AS "BANDCLASS",
				CHANNEL AS "CHANNEL",
				PNOFFSET AS "PNOFFSET",
				ALTITUDE AS "ALTITUDE",
				SPEED AS "SPEED",
				COURSE AS "COURSE",
				CONFIDENCE AS "CONFIDENCE",
				HORIZONTALACCURACY AS "HORIZONTAL ACCURACY",
				VERTICALACCURACY AS "VERTICAL ACCURACY",
				LATITUDE AS "LATITUDE",
				LONGITUDE AS "LONGITUDE",
				DATETIME(TIMESTAMP + 978307200,'UNIXEPOCH') AS "TIMESTAMP"
			FROM CdmaCellLocation"""
        )
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"CDMA cell locations function executing")
            with open(
                reportfolderbase + "Wireless Locations/CDMA cell locations.html",
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2> CDMA cell locations report</h2>")
                f.write(f"CDMA cell locations entries: {usageentries}<br>")
                f.write(f"CDMA cell locations database located at: {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>MCC</th><th>SID</th><th>NID</th><th>BSID</th><th>Zone ID</th><th>Band Class</th><th>Channel</th><th>PNOFFSET</th><th>Altitude</th><th>Speed</th><th>Course</th><th>Confidence</th><th>Hoz. Acc.</th><th>Vert. Acc.</th><th>Latitude</th><th>Longitude</th><th>Timestamp</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td><td>{row[10]}</td><td>{row[11]}</td><td>{row[12]}</td><td>{row[13]}</td><td>{row[14]}</td><td>{row[15]}</td><td>{row[16]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"CDMA cell locations function completed")
        else:
            logfunc("No CDMA cell locations available")
    except:
        logfunc("Error on CDMA cell locations function.")

    try:
        db = sqlite3.connect(filefound[0])
        cursor = db.cursor()
        cursor.execute(
            """SELECT
				MAC AS "Base10 MAC",
				CHANNEL AS "CHANNEL",
				INFOMASK AS "INFOMASK",
				SPEED AS "SPEED",
				COURSE AS "COURSE",
				CONFIDENCE AS "CONFIDENCE",
				SCORE AS "SCORE",
				REACH AS "REACH",
				HORIZONTALACCURACY AS "HORIZONTAL ACCURACY",
				VERTICALACCURACY AS "VERTICAL ACCURACY",
				LATITUDE AS "LATITUDE",
				LONGITUDE AS "LONGITUDE",
				DATETIME(TIMESTAMP + 978307200,'UNIXEPOCH') AS "TIMESTAMP"
			FROM WifiLocation"""
        )
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"WiFi cell locations function executing")
            with open(
                reportfolderbase + "Wireless Locations/WiFi locations.html",
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2> WiFi locations report</h2>")
                f.write(f"WiFi locations entries: {usageentries}<br>")
                f.write(f"WiFi ocations database located at: {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Base10 MAC</th><th>Channel</th><th>Infomask</th><th>Speed</th><th>Course</th><th>Confidence</th><th>Score</th><th>Reach</th><th>Hoz. Acc.</th><th>Vert. Acc.</th><th>Latitude</th><th>Longitude</th><th>Timestamp</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td><td>{row[10]}</td><td>{row[11]}</td><td>{row[12]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"WiFi locations function completed")
        else:
            logfunc("No WiFi locations available")
    except:
        logfunc("Error on WiFi locations function.")


def calendar(filefound):
    logfunc("Calendar function executing")
    os.makedirs(reportfolderbase + "Calendars/")
    try:
        db = sqlite3.connect(filefound[0])
        cursor = db.cursor()
        cursor.execute(
            """
		select 
		title,
		flags,
		color,
		symbolic_color_name,
		external_id,
		self_identity_email
		from Calendar
		"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Calendar List function executing")
            with open(
                reportfolderbase + "Calendars/Calendar List.html", "w", encoding="utf8"
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Calendars List report</h2>")
                f.write(f"Calendar List entries: {usageentries}<br>")
                f.write(f"Calendar List database located at: {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Title</th><th>Flags</th><th>Color</th><th>Color Name</th><th>Ext. ID</th><th>Self ID Email</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"Calendar List function completed")
        else:
            logfunc("No Calendar List available")
    except:
        logfunc("Error on Calendar List function.")

    try:
        db = sqlite3.connect(filefound[0])
        cursor = db.cursor()
        cursor.execute(
            """
		Select
		summary,
		start_date,
		DATETIME(start_date + 978307200, 'UNIXEPOCH') as startdate,
		start_tz,
		end_date,
		DATETIME(end_date + 978307200, 'UNIXEPOCH') as enddate,
		end_tz,
		all_day,
		calendar_id,
		last_modified,
		DATETIME(last_modified+ 978307200, 'UNIXEPOCH') as lastmod
		from CalendarItem
		"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Calendar Items function executing")
            with open(
                reportfolderbase + "Calendars/Calendar Items.html", "w", encoding="utf8"
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Calendar Items report</h2>")
                f.write(f"Calendars Items entries: {usageentries}<br>")
                f.write(f"Calendars Items database located at: {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Summary</th><th>Start Date</th><th>Start Date Conv</th><th>Start TZ</th><th>End Date</th><th>End Date Conv</th><th>End TZ</th><th>All Day</th><th>Calendar ID</th><th>Last Mod Date</th><th>Mod Date Conv</th></tr>"
                )
                for row in all_rows:
                    if row[1] < 0:
                        f.write(
                            f"<tr><td>{row[0]}</td><td>{row[1]}</td><td> </td><td>{row[3]}</td><td>{row[4]}</td><td> </td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td><td>{row[10]}</td></tr>"
                        )
                    else:
                        f.write(
                            f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td><td>{row[10]}</td></tr>"
                        )
                f.write(f"</table></body></html>")
                logfunc(f"Calendar Items function completed")
        else:
            logfunc("No Calendar Items available")
    except:
        logfunc("Error on Calendar Items function.")

    try:
        db = sqlite3.connect(filefound[0])
        cursor = db.cursor()
        cursor.execute(
            """
		SELECT
		display_name,
		address,
		first_name,
		last_name
		from Identity
		"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Calendar Identity function executing")
            with open(
                reportfolderbase + "Calendars/Calendar Identity.html",
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Calendar Identity report</h2>")
                f.write(f"Calendars Identity entries: {usageentries}<br>")
                f.write(f"Calendars Identity database located at: {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Display Name</th><th>Address</th><th>First Name</th><th>Last Name</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"Calendar Identity function completed")
        else:
            logfunc("No Calendar Identity data available")
    except:
        logfunc("Error on Calendar Identity function.")
    logfunc("Calendar function completed.")


def mailprotect(filefound):
    logfunc("Protected Index Envelope emails function executing")

    iOSversion = versionf

    logfunc(f"iOS version: {iOSversion}")

    if version.parse(iOSversion) < version.parse("12"):
        logfunc("Unsupported version" + iOSversion)
        return ()

    if version.parse(iOSversion) < version.parse("13"):
        try:
            if os.path.isdir(reportfolderbase + "Emails/"):
                pass
            else:
                os.makedirs(reportfolderbase + "Emails/")
        except:
            logfunc("Error creating mailprotect() report directory")

        try:
            tempf, end = os.path.split(filefound[0])

            if os.path.isfile(tempf + "/emails.db"):
                os.remove(tempf + "/emails.db")

            db = sqlite3.connect(tempf + "/emails.db")
            cursor = db.cursor()
            cursor.execute(
                """
			create table email1(rowid int, ds text, dr text, size int, sender text, messid int, subject text, receipt text, cc text, bcc text)
			"""
            )
            db.commit()

            cursor.execute(
                """
			create table email2(rowid int, data text)
			"""
            )
            db.commit()

            db = sqlite3.connect(tempf + "/Envelope Index")
            db.execute(f'ATTACH DATABASE "{tempf}/Protected Index" AS PI')
            db.execute(f'ATTACH DATABASE "{tempf}/emails.db" AS emails')

            cursor = db.cursor()
            cursor.execute(
                """
			select  
			main.messages.ROWID,
			main.messages.date_sent,
			main.messages.date_received,
			main.messages.size,
			PI.messages.sender,
			PI.messages.message_id,
			PI.messages.subject,
			PI.messages._to,
			PI.messages.cc,
			PI.messages.bcc
			from main.messages, PI.messages
			where main.messages.ROWID =  PI.messages.message_id 
			"""
            )

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                print(f"Total emails {str(usageentries)}")
                usageentries1 = str(usageentries)
                for row in all_rows:
                    # print(row)
                    datainsert = (
                        row[0],
                        row[1],
                        row[2],
                        row[3],
                        row[4],
                        row[5],
                        row[6],
                        row[7],
                        row[8],
                        row[9],
                    )
                    cursor.execute(
                        "INSERT INTO emails.email1 (rowid, ds, dr, size, sender, messid, subject, receipt, cc, bcc)  VALUES(?,?,?,?,?,?,?,?,?,?)",
                        datainsert,
                    )
                    db.commit()
            else:
                print("Zero rows")

            cursor = db.cursor()
            cursor.execute(
                """
			select  
			main.messages.ROWID,
			PI.message_data.data
			from main.message_data, main.messages, PI.messages, PI.message_data
			where main.messages.ROWID = main.message_data.message_id and PI.messages.message_id = main.message_data.message_id 
			and PI.message_data.message_data_id = main.message_data.ROWID
			"""
            )

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                print(f"Total emails with message data {str(usageentries)}")
                usageentries2 = str(usageentries)
                for row in all_rows:
                    datainsert = (
                        row[0],
                        row[1],
                    )
                    cursor.execute(
                        "INSERT INTO emails.email2 (rowid, data)  VALUES(?,?)",
                        datainsert,
                    )
                    db.commit()
            else:
                print("Zero rows")

            cursor.execute(
                """
			select 
			email1.rowid,
			datetime(email1.ds, 'unixepoch', 'localtime') as ds,
			datetime(email1.dr, 'unixepoch', 'localtime') as dr,
			email1.sender, 
			email1.messid, 
			email1.subject, 
			email1.receipt, 
			email1.cc,
			email1.bcc,
			email2.data 
			from email1
			left outer join email2
			on email2.rowid = email1.rowid
			"""
            )

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                with open(
                    reportfolderbase + "Emails/Protected Index Env.html",
                    "w",
                    encoding="utf8",
                ) as f:
                    f.write("<html><body>")
                    f.write("<h2> Protected Index and Envelope report</h2>")
                    f.write(
                        f"Protected Index and Envelope emails total: {usageentries1}<br>"
                    )
                    f.write(
                        f"Protected Index and Envelope emails with attachments: {usageentries2}<br>"
                    )
                    f.write(
                        f"Protected Index and Envelope emails location: {tempf} -> Protected Envelope and Protected Index sqlite databases<br>"
                    )
                    f.write(f"Timestamps are LOCALTIME<br>")
                    f.write(
                        "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                    )
                    f.write("<br/>")
                    f.write("")
                    f.write(f'<table class="table sticky">')
                    f.write(
                        f"<tr><th>Row ID</th><th>Date Sent</th><th>Date Received</th><th>Sender</th><th>Message ID</th><th>Subject</th><th>Recepient</th><th>CC</th><th>BCC</th><th>Message</th></tr>"
                    )
                    for row in all_rows:
                        f.write(
                            f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td></tr>"
                        )
                    f.write(f"</table></body></html>")
            else:
                logfunc("No Protected Index Envelope emails available")
        except:
            logfunc("Error on Protected Index Envelope emails function")

    if version.parse(iOSversion) < version.parse("14"):
        try:
            if os.path.isdir(reportfolderbase + "Emails/"):
                pass
            else:
                os.makedirs(reportfolderbase + "Emails/")
        except:
            logfunc("Error creating mailprotect() report directory")

        try:
            tempf, end = os.path.split(filefound[0])

            db = sqlite3.connect(tempf + "/Envelope Index")
            db.execute(f'ATTACH DATABASE "{tempf}/Protected Index" AS PI')

            cursor = db.cursor()
            cursor.execute(
                """
			SELECT
			datetime(main.messages.date_sent, 'UNIXEPOCH', 'localtime') as datesent,
			datetime(main.messages.date_received, 'UNIXEPOCH', 'localtime') as datereceived,
			PI.addresses.address,
			PI.addresses.comment,
			PI.subjects.subject,
			PI.summaries.summary,
			main.messages.read,
			main.messages.flagged,
			main.messages.deleted,
			main.mailboxes.url
			from main.mailboxes, main.messages, PI.subjects, PI.addresses, PI.summaries
			where main.messages.subject = PI.subjects.ROWID 
			and main.messages.sender = PI.addresses.ROWID 
			and main.messages.summary = PI.summaries.ROWID
			and main.mailboxes.ROWID = main.messages.mailbox
			"""
            )

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                with open(
                    reportfolderbase + "Emails/Protected Index Env.html",
                    "w",
                    encoding="utf8",
                ) as f:
                    f.write("<html><body>")
                    f.write("<h2> Protected Index and Envelope report</h2>")
                    f.write(
                        f"Protected Index and Envelope emails total: {usageentries}<br>"
                    )
                    f.write(
                        f"Protected Index and Envelope emails location: {tempf} -> Protected Envelope and Protected Index sqlite databases<br>"
                    )
                    f.write(f"Timestamps are LOCALTIME<br>")
                    f.write(
                        "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                    )
                    f.write("<br/>")
                    f.write("")
                    f.write(f'<table class="table sticky">')
                    f.write(
                        f"<tr><th>Date Sent</th><th>Date Received</th><th>Address</th><th>Comment</th><th>Subject</th><th>Summary</th><th>Read?</th><th>Flagged?</th><th>Deleted?</th><th>Mailbox</th></tr>"
                    )
                    for row in all_rows:
                        f.write(
                            f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td></tr>"
                        )
                    f.write(f"</table></body></html>")
            else:
                logfunc("No Protected Index Envelope emails available")
        except:
            logfunc("Error on Protected Index Envelope emails function")

    logfunc(f"Protected Index Envelope emails function completed")


def screentime(filefound):
    try:
        if os.path.isdir(reportfolderbase + "Screen Time/"):
            pass
        else:
            os.makedirs(reportfolderbase + "Screen Time/")
    except:
        logfunc("Error creating screentime() report directory")

    logfunc(f"Screen Time function executing")
    try:
        tempf, end = os.path.split(filefound[0])
        db = sqlite3.connect(tempf + "/RMAdminStore-Local.sqlite")
        cursor = db.cursor()

        cursor.execute(
            """SELECT
			ZUSAGETIMEDITEM.ZBUNDLEIDENTIFIER,
			ZUSAGETIMEDITEM.ZDOMAIN,
			ZUSAGETIMEDITEM.ZTOTALTIMEINSECONDS,
			DATETIME(ZUSAGEBLOCK.ZSTARTDATE + 978307200, 'UNIXEPOCH', 'localtime') as startdate,
			DATETIME(ZUSAGEBLOCK.ZLASTEVENTDATE + 978307200, 'UNIXEPOCH', 'localtime') as endate
			from ZUSAGEBLOCK, ZUSAGETIMEDITEM, ZUSAGECATEGORY
			where ZUSAGEBLOCK.Z_PK = ZUSAGECATEGORY.ZBLOCK and 
			ZUSAGECATEGORY.Z_PK = ZUSAGETIMEDITEM.ZCATEGORY
			order by ZBUNDLEIDENTIFIER
			"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Screen Time App Usage function executing")
            with open(
                reportfolderbase + "Screen Time/App Usage.html", "w", encoding="utf8"
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Screen Time App Usage report</h2>")
                f.write(f"Screen Time App Usage total: {usageentries}<br>")
                f.write(
                    f"Screen Time App Usage  location: {tempf}/RMAdminStore-Local.sqlite <br>"
                )
                f.write(f"Timestamps are LOCALTIME<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Bundle ID</th><th>Domain</th><th>Total Time Secs</th><th>Start Date</th><th>End Date</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
        else:
            logfunc("No Screen Time App Usage available")
        logfunc(f"Screen Time App Usage function completed")
    except:
        logfunc("Error on Screen Time App Usage function")

    try:
        tempf, end = os.path.split(filefound[0])
        db = sqlite3.connect(tempf + "/RMAdminStore-Local.sqlite")
        cursor = db.cursor()

        cursor.execute(
            """SELECT
			ZBUNDLEIDENTIFIER,
			ZUNIQUEIDENTIFIER
			from ZINSTALLEDAPP
			"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Screen Time Installed Apps function executing")
            with open(
                reportfolderbase + "Screen Time/Installed Apps.html",
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Screen Time Installed Apps report</h2>")
                f.write(f"Screen Time Installed Apps total: {usageentries}<br>")
                f.write(
                    f"Screen Time Installed Apps location: {tempf}/RMAdminStore-Local.sqlite <br>"
                )
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(f"<tr><th>Bundle ID</th><th>Unique ID</th></tr>")
                for row in all_rows:
                    f.write(f"<tr><td>{row[0]}</td><td>{row[1]}</td></tr>")
                f.write(f"</table></body></html>")
        else:
            logfunc("No Screen Time Installed Apps available")
        logfunc(f"Screen Time Installed Apps function completed")
    except:
        logfunc("Error on Screen Time App Usage function")

    try:
        tempf, end = os.path.split(filefound[0])
        db = sqlite3.connect(tempf + "/RMAdminStore-Local.sqlite")
        cursor = db.cursor()

        cursor.execute(
            """SELECT
		ZAPPLEID,
		ZFAMILYNAME,
		ZGIVENNAME,
		ZFAMILYMEMBERTYPE,
		ZISPARENT,
		ZISFAMILYORGANIZER
		from ZCOREUSER
			"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Screen Time Core User function executing")
            with open(
                reportfolderbase + "Screen Time/Core User.html", "w", encoding="utf8"
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Screen Time Core User report</h2>")
                f.write(f"Screen Time Core User total: {usageentries}<br>")
                f.write(
                    f"Screen Time Core User location: {tempf}/RMAdminStore-Local.sqlite <br>"
                )
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Apple ID</th><th>Family Name</th><th>Given Name</th><th>Family Member Type</th><th>Is Parent</th><th>Is Fam Organizer</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
        else:
            logfunc("No Screen Time Core User available")
        logfunc(f"Screen Time Core User function completed")
    except:
        logfunc("Error on Screen Time Core User function")

    try:
        tempf, end = os.path.split(filefound[0])
        db = sqlite3.connect(tempf + "/RMAdminStore-Local.sqlite")
        cursor = db.cursor()

        cursor.execute(
            """SELECT
		ZNAME,
		ZIDENTIFIER
		FROM ZCOREDEVICE
			"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Screen Time Core Device function executing")
            with open(
                reportfolderbase + "Screen Time/Core Device.html", "w", encoding="utf8"
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Screen Time Core Device report</h2>")
                f.write(f"Screen Time Core Device total: {usageentries}<br>")
                f.write(
                    f"Screen Time Core Device location: {tempf}/RMAdminStore-Local.sqlite <br>"
                )
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(f"<tr><th>Name</th><th>Identifier</th></tr>")
                for row in all_rows:
                    f.write(f"<tr><td>{row[0]}</td><td>{row[1]}</td></tr>")
                f.write(f"</table></body></html>")
        else:
            logfunc("No Screen Time Core Device available")
        logfunc(f"Screen Time Core Device function completed")
    except:
        logfunc("Error on Screen Time Core Device function")

    try:
        tempf, end = os.path.split(filefound[0])
        db = sqlite3.connect(tempf + "/RMAdminStore-Local.sqlite")
        cursor = db.cursor()

        cursor.execute(
            """SELECT
		ZCLOUDSYNCENABLED,
		ZSCREENTIMEENABLED
		FROM
		ZSCREENTIMESETTINGS
			"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Screen Time Core Enabled Settings executing")
            with open(
                reportfolderbase + "Screen Time/Core Enabled Settings.html",
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Screen Time Enabled Settings report</h2>")
                f.write(f"Screen Time Enabled Settings total: {usageentries}<br>")
                f.write(
                    f"Screen Time Enabled Settings data location: {tempf}/RMAdminStore-Local.sqlite <br>"
                )
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(f"<tr><th>Is Cloud Sync?</th><th>Is Screen Time?</th></tr>")
                for row in all_rows:
                    f.write(f"<tr><td>{row[0]}</td><td>{row[1]}</td></tr>")
                f.write(f"</table></body></html>")
            logfunc(f"Screen Time Enabled Settings function completed")
        else:
            logfunc("No Screen Time Core Enabled Settings available")
    except:
        logfunc("Error on Screen Time Enabled Settings function")
    logfunc(f"Screen Time function completed")


def bluetooths(filefound):
    try:
        if os.path.isdir(reportfolderbase + "Bluetooth/"):
            pass
        else:
            os.makedirs(reportfolderbase + "Bluetooth/")
    except:
        logfunc("Error creating bluetooths() report directory")

    logfunc(f"Bluetooth function executing")
    try:
        tempf, end = os.path.split(filefound[0])
        db = sqlite3.connect(tempf + "/com.apple.MobileBluetooth.ledevices.paired.db")
        cursor = db.cursor()

        cursor.execute(
            """select 
		Uuid,
		Name,
		NameOrigin,
		Address,
		ResolvedAddress,
		LastSeenTime,
		LastConnectionTime
		from 
		PairedDevices
			"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Bluetooth Paired Devices function executing")
            with open(
                reportfolderbase + "Bluetooth/Bluetooth Paired.html",
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Bluetooth Paired Devices report</h2>")
                f.write(f"Bluetooth Paired Devices total: {usageentries}<br>")
                f.write(
                    f"Bluetooth Paired Devices location: {tempf}/com.apple.MobileBluetooth.ledevices.paired.db<br>"
                )
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>UUID</th><th>Name</th><th>Name Origin</th><th>Address</th><th>Resolved Address</th><th>Last Seen Time</th><th>Last Connection Time</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
            logfunc(f"Bluetooth Paired Devices function completed")
        else:
            logfunc("No Bluetooth Paired Devices available")
    except:
        logfunc("Error on Blueetooth Paired Devices function")

    try:
        tempf, end = os.path.split(filefound[0])
        db = sqlite3.connect(tempf + "/com.apple.MobileBluetooth.ledevices.other.db")
        cursor = db.cursor()

        cursor.execute(
            """SELECT
		Name,
		Address,
		LastSeenTime,
		Uuid
		FROM
		OtherDevices
			"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Bluetooth Other function executing")
            with open(
                reportfolderbase + "Bluetooth/Bluetooth Other.html",
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Bluetooth Other Devices report</h2>")
                f.write(f"Bluetooth Other Devices total: {usageentries}<br>")
                f.write(
                    f"Bluetooth Other Devices location: {tempf}/com.apple.MobileBluetooth.ledevices.paired.db<br>"
                )
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Name</th><th>Address</th><th>Last Seen Time</th><th>UUID</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
            logfunc(f"Bluetooth Other function completed")
        else:
            logfunc("No Bluetooth Other Devices available")
    except:
        logfunc("Error on Blueetooth Other Devices function")
    logfunc(f"Bluetooth function completed")


def whatsapp(filefound):
    try:
        if os.path.isdir(reportfolderbase + "Whatsapp/"):
            pass
        else:
            os.makedirs(reportfolderbase + "Whatsapp/")
    except:
        logfunc("Error creating whatsapp() report directory")

    logfunc(f"Whatsapp function executing")
    try:
        db = sqlite3.connect(filefound[0])
        cursor = db.cursor()
        cursor.execute(
            """ SELECT
		Z_PK, ZPARTNERNAME, ZCONTACTJID, ZLASTMESSAGEDATE
		from ZWACHATSESSION
		"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            f = open(reportfolderbase + "Whatsapp/Chats.html", "w", encoding="utf8")

            for row in all_rows:
                cursor = db.cursor()
                cursor.execute(
                    """SELECT
				ZWAMESSAGE.Z_PK,
				case 
					when ZWAMESSAGE.ZISFROMME = 1 then "Sent to"
					when ZWAMESSAGE.ZISFROMME = 0 then "Received from"
				end as "directionality",
				datetime(ZWAMESSAGE.ZMESSAGEDATE+ 978307200, 'UNIXEPOCH'),
				ZWAMESSAGE.ZFROMJID,
				ZWAMESSAGE.ZPUSHNAME,
				ZWAMESSAGE.ZTOJID,
				ZWAMESSAGE.ZTEXT
				from ZWACHATSESSION, ZWAMESSAGE
				where ZWACHATSESSION.z_pk = %s  and zwamessage.ZCHATSESSION = %s"""
                    % (row[0], row[0])
                )
                all_rows2 = cursor.fetchall()
                usageentries2 = len(all_rows2)
                if usageentries2 > 0:
                    f.write("<html><body>")
                    f.write("<h2> Whatsapp chats report</h2>")
                    f.write(f"Whatsapp chats total conversations: {usageentries2}<br>")
                    f.write(f"Whatsapp chats  location: {filefound[0]}<br>")
                    f.write(
                        "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                    )
                    f.write("<br/>")
                    f.write("")
                    f.write(f'<table class="table sticky">')
                    f.write(
                        f"<tr><th>ID</th><th>Timestamp</th><th>Direction</th><th>Partner</th><th>Message</th><th>From JID</th><th>Name</th><th>To JID</th><th>Media</th></tr>"
                    )
                    for row2 in all_rows2:

                        cursor = db.cursor()
                        cursor.execute(
                            """ select
						ZWAMEDIAITEM.ZVCARDSTRING,
						ZWAMEDIAITEM.ZMEDIALOCALPATH,
						ZWAMEDIAITEM.ZFILESIZE
						 from ZWAMEDIAITEM
						where ZWAMEDIAITEM.ZMESSAGE = %s
						"""
                            % (row2[0])
                        )
                        all_rows3 = cursor.fetchall()
                        usageentries3 = len(all_rows3)
                        if usageentries3 > 0:
                            for row3 in all_rows3:
                                # print all the data from all_rows2 and all_rows3

                                f.write(
                                    f"<tr><td>{row2[0]}</td><td>{row2[2]}</td><td>{row2[1]}</td><td>{row[1]}</td><td>{row2[6]}</td><td>{row2[3]}</td><td>{row2[4]}</td><td>{row2[5]}</td><td>{row3[1]}</td></tr>"
                                )
                        else:
                            # print only the date from all_rows2
                            f.write(
                                f"<tr><td>{row2[0]}</td><td>{row2[2]}</td><td>{row2[1]}</td><td>{row[1]}</td><td>{row2[6]}</td><td>{row2[3]}</td><td>{row2[4]}</td><td>{row2[5]}</td><td> </td></tr>"
                            )
                    f.write(f"</table></body></html>")
            f.close()
    except:
        logfunc("Error on Whatsapp function")
    logfunc(f"Whatsapp function completed")


def ipscl(filefound):
    try:
        logfunc(f"App Crash Logs function executing")
        try:
            os.makedirs(reportfolderbase + "App Crash/")
            db = sqlite3.connect(reportfolderbase + "App Crash/cl.db")
            cursor = db.cursor()
            cursor.execute(
                "CREATE TABLE ips(timestampss TEXT, dnames TEXT, appversions TEXT, bundles TEXT, firstps TEXT, osversions TEXT, bgtypes TEXT, tails TEXT)"
            )
            db.commit()
        except:
            logfunc(f"DB could not be created")

        pathlist = []

        for w in filefound:
            resultant = ""
            times = ""
            appname = ""
            appversion = ""
            bundle = ""
            firstp = ""
            osversion = ""
            dname = ""
            tail = ""
            bugtype = ""

            with open(w, "r", encoding="utf8") as data:
                for line in data:
                    resultant = resultant + line
                    if "}" in line:
                        break
            try:

                resultantdict = json.loads(resultant)

                for x, y in resultantdict.items():
                    # import in a database
                    if x == "timestamp":
                        times = y
                    if x == "name":
                        dname = y
                    if x == "app_version":
                        appversion = y
                    if x == "bundleID":
                        bundle = y
                    if x == "is_first_party":
                        firstp = y
                    if x == "os_version":
                        osversion = y
                    if x == "restore_type":
                        restoretype = y
                    if x == "bug_type":
                        bugtype = y

                p = pathlib.Path(w)
                head, tail = os.path.split(w)

                if head not in pathlist:
                    pathlist.append(head)

                datainsert = (
                    times,
                    dname,
                    appversion,
                    bundle,
                    firstp,
                    osversion,
                    bugtype,
                    tail,
                )
                cursor.execute(
                    "INSERT INTO ips (timestampss, dnames, appversions, bundles, firstps, osversions, bgtypes, tails)  VALUES(?,?,?,?,?,?,?,?)",
                    datainsert,
                )
                db.commit()
            except:
                logfunc(f"No valid dictionary header at {p}")

        try:
            cursor.execute(
                """SELECT
			*
			from ips
			ORDER by dnames desc, timestampss ASC
				"""
            )

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                with open(
                    reportfolderbase + "App Crash/IPS files.html", "w", encoding="utf8"
                ) as f:
                    f.write("<html><body>")
                    f.write("<h2> Application Crash Logs report</h2>")
                    f.write(f"Application Crash Logs: {usageentries}<br>")
                    f.write(f"Applicatipn CraSH Logs location: <br>")
                    for z in pathlist:
                        f.write(f"{z}<br>")
                    f.write(
                        "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                    )
                    f.write("<br/>")
                    f.write("")
                    f.write(f'<table class="table sticky">')
                    f.write(
                        f"<tr><th>Timestamp</th><th>Name</th><th>App Version</th><th>Bundle ID</th><th>1st Party?</th><th>OS Version</th><th>Bug Type</th><th>Filename</th></tr>"
                    )
                    for row in all_rows:
                        f.write(
                            f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td></tr>"
                        )
                    f.write(f"</table></body></html>")
            else:
                logfunc("No App Crash Logs available")
        except:
            logfunc("Error on App Crash Logs function")
        logfunc(f"App Crash Logs function completed")
    except:
        logfunc("Bad data input at App Crash Logs function")


def wapcontact(filefound):
    logfunc(f"Whatsapp Contacts function executing")
    try:
        try:
            if os.path.isdir(reportfolderbase + "Whatsapp/"):
                pass
            else:
                os.makedirs(reportfolderbase + "Whatsapp/")
        except:
            logfunc("Error creating whatsapp() report directory")

        db = sqlite3.connect(filefound[0])
        cursor = db.cursor()
        cursor.execute(
            """ SELECT
		ZFULLNAME, ZPHONENUMBER, ZPHONENUMBERLABEL,
		ZWHATSAPPID, ZABOUTTEXT
		from ZWAADDRESSBOOKCONTACT
		"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            with open(
                reportfolderbase + "Whatsapp/Contacts.html", "w", encoding="utf8"
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Whatsapp chats report</h2>")
                f.write(f"Whatsapp Contacts total: {usageentries}<br>")
                f.write(f"Whatsapp Contacts location: {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Full Name</th><th>Phone Number</th><th>Label</th><th>ID</th><th>About Text</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
        else:
            logfunc("No Whatsapp contacts available")
    except:
        logfunc("Error on Whatsapp contacts function")
    logfunc(f"Whatsapp contacts function completed")


def actrec(filefound):
    try:
        logfunc(f"Activation Record function executing")

        deviceinfo()

        os.makedirs(reportfolderbase + "Activation Record/")
        os.makedirs(reportfolderbase + "Activation Record/Incepted/")
        resultant = ""
        p = open(filefound[0], "rb")
        plist = plistlib.load(p)

        for key, val in plist.items():
            if key == "AccountToken":

                with open(
                    reportfolderbase + "Activation Record/Incepted/AccToken.txt", "wb"
                ) as fileto:  # export dirty from DB
                    fileto.write(val)

                with open(
                    reportfolderbase + "Activation Record/Incepted/AccToken.txt", "r"
                ) as filefrom:  # export dirty from DB
                    lines = filefrom.readlines()
                    alast = lines[-2]
                    for line in lines:
                        if line is alast:
                            line = line.replace("=", ":")
                            line = line.replace(";", " ")
                            resultant = resultant + line
                        else:
                            line = line.replace("=", ":")
                            line = line.replace(";", ",")
                            resultant = resultant + line

                res = json.loads(resultant)

                for x, y in res.items():
                    if x == "InternationalMobileEquipmentIdentity":
                        imei = y
                        ordes = 3
                        kas = "IMEI"
                        vas = y
                        sources = filefound[0]
                        deviceinfoin(ordes, kas, vas, sources)

                    if x == "SerialNumber":
                        serial = y
                        ordes = 4
                        kas = "Serial Number"
                        vas = y
                        sources = filefound[0]
                        deviceinfoin(ordes, kas, vas, sources)

                    if x == "UniqueDeviceID":
                        did = y
                        ordes = 5
                        kas = "Unique Device ID"
                        vas = y
                        sources = filefound[0]
                        deviceinfoin(ordes, kas, vas, sources)

                    if x == "ProductType":
                        pt = y
                        ordes = 6
                        kas = "Prod. Type"
                        vas = y
                        sources = filefound[0]
                        deviceinfoin(ordes, kas, vas, sources)

                with open(
                    reportfolderbase + "Activation Record/Activation Record.html",
                    "w",
                    encoding="utf8",
                ) as f:
                    f.write("<html><body>")
                    f.write("<h2> Activation Record report</h2>")
                    f.write(f"Activation Record location: {filefound[0]}<br>")
                    f.write(
                        "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                    )
                    f.write("<br/>")
                    f.write("")
                    f.write(f'<table class="table sticky">')
                    f.write(f"<tr><th>Key</th><th>Value</th></tr>")
                    f.write(f"<tr><td>IMEI</td><td>{imei}</td></tr>")
                    f.write(f"<tr><td>Serial Number</td><td>{serial}</td></tr>")
                    f.write(f"<tr><td>Unique Device ID</td><td>{did}</td></tr>")
                    f.write(f"<tr><td>Product Type</td><td>{pt}</td></tr>")
                    f.write(f"</table></body></html>")

                logfunc(f"Activation Record function completed")
    except:
        logfunc(f"Error on Activation Record function")


def DHCPL(filefound):
    try:
        logfunc(f"DHCP Received Lease function executing")
        if filefound:
            head, tail = os.path.split(filefound[0])
            try:
                if os.path.isdir(reportfolderbase + "DHCP/"):
                    pass
                else:
                    os.makedirs(reportfolderbase + "DHCP/")
            except:
                logfunc("Error creating DHCP report directory")

            with open(reportfolderbase + "DHCP/Received Lease.html", "w") as f:
                f.write("<html><body>")
                f.write("<h2>DHCP Received Lease Report</h2>")
                f.write(f"DHCP Received Lease located at {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(f"<tr><th>Key</th><th>Values</th></tr>")
                f.write(f"<tr><td>iOS WiFi MAC</td><td>{tail}</td></tr>")

                with open(filefound[0], "rb") as fp:
                    pl = plistlib.load(fp)
                    for key, val in pl.items():
                        if key == "IPAddress":
                            f.write(f"<tr><td>{key}</td><td>{val}</td></tr>")
                        if key == "LeaseLength":
                            f.write(f"<tr><td>{key}</td><td>{val}</td></tr>")
                        if key == "LeaseStartDate":
                            f.write(f"<tr><td>{key}</td><td>{val}</td></tr>")
                        if key == "RouterHardwareAddress":
                            f.write(f"<tr><td>{key}</td><td>{val}</td></tr>")
                        if key == "RouterIPAddress":
                            f.write(f"<tr><td>{key}</td><td>{val}</td></tr>")
                        if key == "SSID":
                            f.write(f"<tr><td>{key}</td><td>{val}</td></tr>")
                f.write(f"</table></body></html>")
        else:
            logfunc(f"No DHCP Received Lease available")
        logfunc(f"DHCP Received Lease function completed")
    except:
        logfunc("Error on DHCP Received Lease function")


def DHCPhp(filefound):
    try:
        logfunc(f"DHCP Hotspot Clients function executing")

        if os.path.isdir(reportfolderbase + "DHCP/"):
            pass
        else:
            os.makedirs(reportfolderbase + "DHCP/")

        with open(reportfolderbase + "DHCP/Hotspot Clients.html", "w") as f:
            f.write("<html><body>")
            f.write("<h2>DHCP Hotspot Clients Report</h2>")
            f.write(f"DHCP Hotspot Clients located at {filefound[0]}<br>")
            f.write(
                "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
            )
            f.write("<br/>")
            f.write("")

            with open(filefound[0], "r") as filefrom:
                for line in filefrom:
                    cline = line.strip()
                    if cline == "{":
                        f.write("<table><tr><td>Key</td><td>Values</td></tr>")
                    elif cline == "}":
                        f.write("</table><br>")
                    # elif cline == '':
                    # 	f.write('<br>')
                    else:
                        ll = cline.split("=")
                        f.write(f"<tr><td>{ll[0]}</td>")
                        f.write(f"<td>{ll[1]}</td></tr>")

        logfunc(f"DHCP Hotspot Clients function completed")
    except:
        logfunc("Error on DHCP Hotspot Clients function")


def redditusers(filefound):

    unix = datetime.datetime(1970, 1, 1)  # UTC
    cocoa = datetime.datetime(2001, 1, 1)  # UTC
    delta = cocoa - unix

    try:
        logfunc(f"Reddit User Accounts function executing")
        try:
            os.makedirs(reportfolderbase + "Reddit/")
            db = sqlite3.connect(reportfolderbase + "Reddit/rusers.db")
            cursor = db.cursor()
            cursor.execute(
                "CREATE TABLE users(username TEXT, userid TEXT, createdtime TEXT)"
            )
            db.commit()
        except:
            logfunc(f"DB could not be created")

        head, tail = os.path.split(filefound[1])
        for filename in glob.glob(head + "/*"):
            with open(filename, "rb") as fp:
                # anadir try except file not a bplist
                plist = ccl_bplist.load(fp)
                ns_keyed_archiver_obj = ccl_bplist.deserialise_NsKeyedArchiver(
                    plist, parse_whole_structure=False
                )
                username = ns_keyed_archiver_obj["Username"]
                if username != "$null":
                    userid = ns_keyed_archiver_obj["PrimaryKey"]
                    date = ns_keyed_archiver_obj["created"]
                    date = date["NS.time"]
                    dia = str(date)
                    dias = dia.rsplit(".", 1)[0]
                    timestamp = datetime.datetime.fromtimestamp(int(dias)) + delta

                    db = sqlite3.connect(reportfolderbase + "Reddit/rusers.db")
                    cursor = db.cursor()
                    datainsert = (
                        username,
                        userid,
                        timestamp,
                    )
                    cursor.execute(
                        "INSERT INTO users(username, userid, createdtime)  VALUES(?,?,?)",
                        datainsert,
                    )
                    db.commit()

        db = sqlite3.connect(reportfolderbase + "Reddit/rusers.db")
        cursor = db.cursor()
        cursor.execute(
            """ SELECT
		*
		from users
		"""
        )
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            with open(
                reportfolderbase + "Reddit/User Accounts.html", "w", encoding="utf8"
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Reddit User Accounts report</h2>")
                f.write(f"Reddit User Accounts total: {usageentries}<br>")
                f.write(f"Reddit User Accounts location: {head}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Username</th><th>User ID</th><th>Creation Date</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
        logfunc(f"Reddit User Accounts function completed")
    except:
        logfunc("Error on Reddit User Accounts function")


def redditchats(filefound):
    logfunc(f"Reddit Chats + Contacts function executing")
    try:
        db = sqlite3.connect(reportfolderbase + "Reddit/rusers.db")
        cursor = db.cursor()
        cursor.execute(
            """ SELECT
		*
		from users
		"""
        )
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            for cpath in filefound:
                cpath = str(cpath)
                for row in all_rows:
                    reddituserid = row[1]
                    redditusername = row[0]
                    if reddituserid + "/chat/" in cpath:
                        db = sqlite3.connect(cpath)
                        cursor = db.cursor()
                        cursor.execute(
                            """ select 
						username,
						userID,
						createdAt,
						profileThumbnailUrl
						from Contact
						"""
                        )
                        all_rows0 = cursor.fetchall()  # selected all channelids
                        usageentries0 = len(all_rows0)
                        if usageentries0 > 0:
                            with open(
                                reportfolderbase
                                + "Reddit/Contacts - "
                                + redditusername
                                + ".html",
                                "w",
                                encoding="utf8",
                            ) as f:
                                f.write("<html><body>")
                                f.write(
                                    f"<h2> Reddit Contacts for {redditusername}</h2>"
                                )
                                f.write(f"Reddit Contacts location: {cpath}<br>")
                                f.write(f"Timestamps in UTC<br>")
                                f.write(
                                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                                )
                                f.write("<br/>")
                                f.write(f'<table class="table sticky">')
                                f.write(
                                    f"<tr><th>Username</th><th>User ID</th><th>Creation Date</th><th>Thumbnail URL</th></tr>"
                                )
                                for row0 in all_rows0:
                                    f.write(
                                        f"<tr><td>{row0[0]}</td><td>{row0[1]}</td><td>{row0[2]}</td><td>{row0[3]}</td></tr>"
                                    )
                                f.write(f"</table></body></html>")

                        db = sqlite3.connect(cpath)
                        cursor = db.cursor()
                        cursor.execute(
                            """ select 
						distinct ChatMessage.channelID
						from 
						ChatMessage
						"""
                        )
                        all_rows1 = cursor.fetchall()  # selected all channelids
                        usageentries1 = len(all_rows1)
                        if usageentries1 > 0:

                            with open(
                                reportfolderbase
                                + "Reddit/Chats - "
                                + redditusername
                                + ".html",
                                "w",
                                encoding="utf8",
                            ) as f:
                                f.write("<html><body>")
                                f.write(
                                    f"<h2> Reddit Chats by Channel for {redditusername}</h2>"
                                )
                                f.write(
                                    f"Reddit Chats by Channel location: {cpath}<br>"
                                )
                                f.write(f"Timestamps in UTC<br>")
                                f.write(
                                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                                )
                                f.write("<br/>")
                                f.write("")

                                for (
                                    row1
                                ) in all_rows1:  # select chats per channelid - table
                                    chan = row1[0]
                                    cursor = db.cursor()
                                    cursor.execute(
                                        """ select 
									Contact.username,
									datetime(ChatMessage.timestamp / 1000, 'UNIXEPOCH') as utctime,
									ChatMessage.messageBody,
									ChatMessage.userID
									from 
									ChatMessage, Contact
									where ChatMessage.channelId = ? and Contact.userID = ChatMessage.userID
									order by ChatMessage.timestamp
									""",
                                        (chan,),
                                    )
                                    all_rows2 = cursor.fetchall()
                                    f.write(f"Channel #{chan}<br>")
                                    f.write(f"<table>")
                                    f.write(
                                        f"<tr><th>Username</th><th>Timestamp</th><th>Message</th><th>User ID</th></tr>"
                                    )
                                    for row2 in all_rows2:
                                        f.write(
                                            f"<tr><td>{row2[0]}</td><td>{row2[1]}</td><td>{row2[2]}</td><td>{row2[3]}</td></tr>"
                                        )
                                    f.write(f"</table><br>")
            logfunc(f"Reddit Chats + Contacts function completed")
        else:
            logfunc("No Reddit User Accounts")
    except:
        logfunc("Error on Reddit Chats + Contacts function")


def interactionc(filefound):
    logfunc(f"InteractionC function executing")
    try:
        iOSversion = versionf

        if version.parse(iOSversion) < version.parse("11"):
            logfunc("Unsupported version" + iOSversion)
            return ()

        db = sqlite3.connect(filefound[0])
        cursor = db.cursor()

        cursor.execute(
            """SELECT
		ZINTERACTIONS.ZBUNDLEID AS "BUNDLE ID",
		ZCONTACTS.ZDISPLAYNAME AS "DISPLAY NAME",
		ZCONTACTS.ZIDENTIFIER AS "IDENTIFIER",
		ZCONTACTS.ZPERSONID AS "PERSONID",
		ZINTERACTIONS.ZDIRECTION AS "DIRECTION",
		ZINTERACTIONS.ZISRESPONSE AS "IS RESPONSE",
		ZINTERACTIONS.ZMECHANISM AS "MECHANISM",
		ZINTERACTIONS.ZRECIPIENTCOUNT AS "RECIPIENT COUNT",
		DATETIME(ZINTERACTIONS.ZCREATIONDATE + 978307200, 'unixepoch') AS "ZINTERACTIONS CREATION DATE",
		DATETIME(ZCONTACTS.ZCREATIONDATE + 978307200, 'unixepoch') AS "ZCONTACTS CREATION DATE",
		DATETIME(ZINTERACTIONS.ZSTARTDATE + 978307200, 'unixepoch') AS "START DATE",
		DATETIME(ZINTERACTIONS.ZENDDATE + 978307200, 'unixepoch') AS "END DATE",
		DATETIME(ZCONTACTS.ZFIRSTINCOMINGRECIPIENTDATE + 978307200, 'unixepoch') AS "FIRST INCOMING RECIPIENT DATE",
		DATETIME(ZCONTACTS.ZFIRSTINCOMINGSENDERDATE + 978307200, 'unixepoch') AS "FIRST INCOMING SENDER DATE",
		DATETIME(ZCONTACTS.ZFIRSTOUTGOINGRECIPIENTDATE + 978307200, 'unixepoch') AS "FIRST OUTGOING RECIPIENT DATE",
		DATETIME(ZCONTACTS.ZLASTINCOMINGSENDERDATE + 978307200, 'unixepoch') AS "LAST INCOMING SENDER DATE",
		CASE
			ZLASTINCOMINGRECIPIENTDATE 
			WHEN
				"0" 
			THEN
				"0" 
			ELSE
				DATETIME(ZCONTACTS.ZLASTINCOMINGRECIPIENTDATE + 978307200, 'unixepoch') 
		END AS "LAST INCOMING RECIPIENT DATE", 
		DATETIME(ZCONTACTS.ZLASTOUTGOINGRECIPIENTDATE + 978307200, 'unixepoch') AS "LAST OUTGOING RECIPIENT DATE", 
		ZINTERACTIONS.ZACCOUNT AS "ACCOUNT", 
		ZINTERACTIONS.ZDOMAINIDENTIFIER AS "DOMAIN IDENTIFIER", 
		ZCONTACTS.ZINCOMINGRECIPIENTCOUNT AS "INCOMING RECIPIENT COUNT", 
		ZCONTACTS.ZINCOMINGSENDERCOUNT AS "INCOMING SENDER COUNT", 
		ZCONTACTS.ZOUTGOINGRECIPIENTCOUNT AS "OUTGOING RECIPIENT COUNT", 
		ZCONTACTS.ZCUSTOMIDENTIFIER AS "CUSTOM IDENTIFIER", 
		ZINTERACTIONS.ZCONTENTURL AS "CONTENT URL", 
		ZINTERACTIONS.ZLOCATIONUUID AS "LOCATION UUID", 
		ZINTERACTIONS.Z_PK AS "ZINTERACTIONS TABLE ID" 
		FROM
		ZINTERACTIONS 
		LEFT JOIN
			ZCONTACTS 
			ON ZINTERACTIONS.ZSENDER = ZCONTACTS.Z_PK
		"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            if os.path.isdir(reportfolderbase + "InteractionC/"):
                pass
            else:
                os.makedirs(reportfolderbase + "InteractionC/")

            with open(
                reportfolderbase + "InteractionC/Interactions.html",
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2>iOS " + iOSversion + " - InteractionC report</h2>")
                f.write(f"InteractionC entries: {usageentries}<br>")
                f.write(f"InteractionC located at: {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Bundle ID</th><th>Display Name</th><th>Identifier</th><th>Person ID</th><th>Direction</th><th>Is Response</th><th>Mechanism</th><th>Recipient Count</th><th>Zinteractions Creation Date</th><th>Zcontacts Creation Date</th><th>Start Date</th><th>End Date</th><th>First Incoming Recipient Date</th><th>First Outgoing Recipient Date</th><th>Last Incoming Sender Date</th><th>Last Incoming Recipient Date</th><th>Last Outgoing Recipient Date</th><th>Account</th><th>Domain Identifier</th><th>Incoming Recipient Count</th><th>Incoming Sender Count</th><th>Outgoing Recipient Count</th><th>Custom Identifier</th><th>Content URL</th><th>Location UUID</th><th>Zinteractions Table ID</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td><td>{row[10]}</td><td>{row[11]}</td><td>{row[12]}</td><td>{row[13]}</td><td>{row[14]}</td><td>{row[15]}</td><td>{row[17]}</td><td>{row[17]}</td><td>{row[18]}</td><td>{row[19]}</td><td>{row[20]}</td><td>{row[21]}</td><td>{row[22]}</td><td>{row[23]}</td><td>{row[24]}</td><td>{row[25]}</td><td>{row[26]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
        else:
            logfunc(f"No InteractionC records in database")
    except:
        logfunv(f"Error in InteractionC function")
    logfunc(f"InteractionC function completed")


def deviceinfo():
    if os.path.isdir(reportfolderbase + "Device Info/"):
        pass
    else:
        os.makedirs(reportfolderbase + "Device Info/")
        db = sqlite3.connect(reportfolderbase + "Device Info/di.db")
        cursor = db.cursor()
        cursor.execute("CREATE TABLE devinf (ord TEXT, ka TEXT, va TEXT, source TEXT)")
        db.commit()


def deviceinfoin(ordes, kas, vas, sources):
    sources = str(sources)
    db = sqlite3.connect(reportfolderbase + "Device Info/di.db")
    cursor = db.cursor()
    datainsert = (
        ordes,
        kas,
        vas,
        sources,
    )
    cursor.execute(
        "INSERT INTO devinf (ord, ka, va, source)  VALUES(?,?,?,?)", datainsert
    )
    db.commit()


def html2csv(reportfolderbase):
    # List of items that take too long to convert or that shouldn't be converted
    itemstoignore = [
        "index.html",
        "Distribution Keys.html",
        "StrucMetadata.html",
        "StrucMetadataCombined.html",
    ]

    if os.path.isdir(reportfolderbase + "_CSV Exports/"):
        pass
    else:
        os.makedirs(reportfolderbase + "_CSV Exports/")
    for root, dirs, files in sorted(os.walk(reportfolderbase)):
        for file in files:
            if file.endswith(".html"):
                fullpath = os.path.join(root, file)
                head, tail = os.path.split(fullpath)
                if file in itemstoignore:
                    pass
                else:
                    data = open(fullpath, "r", encoding="utf8")
                    soup = BeautifulSoup(data, "html.parser")
                    tables = soup.find_all("table")
                    data.close()
                    output_final_rows = []

                    for table in tables:
                        output_rows = []
                        for table_row in table.findAll("tr"):

                            columns = table_row.findAll("td")
                            output_row = []
                            for column in columns:
                                output_row.append(column.text)
                            output_rows.append(output_row)

                        file = os.path.splitext(file)[0]
                        with codecs.open(
                            reportfolderbase + "_CSV Exports/" + file + ".csv",
                            "a",
                            "utf-8-sig",
                        ) as csvfile:
                            writer = csv.writer(
                                csvfile, quotechar='"', quoting=csv.QUOTE_ALL
                            )
                            writer.writerows(output_rows)
