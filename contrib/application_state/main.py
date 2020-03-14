import glob
import os
import pathlib
import plistlib
import sqlite3

from common import logfunc
from contrib.utils import silence_and_log
from settings import *
from vendor import ccl_bplist


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
    filedatahtml.write(f'<tr><td colspan = "4">Total bundle IDs: {str(len(all_rows))}</td></tr>')
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

        '''# csv report - Currently convertig the html to csv after all artifacts are done. No need to do it here for now.
        filedata = open(outpath + "ApplicationState_InstalledAppInfo.csv", mode="a+")
        filewrite = csv.writer(
            filedata, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        filewrite.writerow([bid, bpath, bcontainer, bsandbox])
        count = count + 1
        filedata.close()
        '''
        
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
