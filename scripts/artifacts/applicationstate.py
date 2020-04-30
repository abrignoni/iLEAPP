import glob
import os
import pathlib
import plistlib
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows 
from scripts.ccl import ccl_bplist

def get_applicationstate(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select
    application_identifier_tab.[application_identifier],
    kvs.[value]
    from kvs, key_tab,application_identifier_tab
    where 
    key_tab.[key]='compatibilityInfo' and kvs.[key] = key_tab.[id]
    and application_identifier_tab.[id] = kvs.[application_identifier]
    order by application_identifier_tab.[id]  
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        os.mkdir(report_folder + "exported-dirty/")
        os.mkdir(report_folder + "exported-clean/")
        data_list = []
        for row in all_rows:
            bundleid = str(row[0])
            bundleidplist = bundleid + ".bplist"
            f = row[1]
            
            output_file = open(
                report_folder + "/exported-dirty/" + bundleidplist, "wb"
            )  # export dirty from DB
            output_file.write(f)
            output_file.close()
            
            g = open(report_folder + "/exported-dirty/" + bundleidplist, "rb")
            # plist = plistlib.load(g)

            plist = ccl_bplist.load(g)
            
            if type(plist) is dict:
                var1 = (plist['bundleIdentifier'])
                var2 = (plist['bundlePath'])
                var3 = (plist['sandboxPath'])
                data_list.append((var1, var2, var3))
            else:
                output_file = open(report_folder + "exported-clean/" + bundleidplist, "wb")
                output_file.write(plist)
                output_file.close()
            
        for filename in glob.glob(report_folder + "exported-clean/*.bplist"):
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
            data_list.append((bid,bpath,bsandbox))

        report = ArtifactHtmlReport('Application State')
        report.start_artifact_report(report_folder, 'Application State DB')
        report.add_script()
        data_headers = ('Bundle ID','Bundle Path','Sandbox Path' )     
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
    else:
        logfunc('No Application State data available')

    db.close()
    return      