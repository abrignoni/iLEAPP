import glob
import os
import pathlib
import plistlib
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows 

def get_conDev(files_found, report_folder, seeker, wrap_text, timezone_offset):
    file_found = str(files_found[0])
    with open(file_found, "rb") as f:
        data = f.read()
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

    report = ArtifactHtmlReport('Connected Devices')
    report.start_artifact_report(report_folder, 'Connected Devices')
    report.add_script()
    data_list = []
    data_list.append((userComps,))
    data_headers = ('User & Computer Names', )     
    report.write_artifact_data_table(data_headers, data_list, file_found)
    report.end_artifact_report()
    
    tsvname = 'Connected Devices'
    tsv(report_folder, data_headers, data_list, tsvname)
    
    return      
    
__artifacts__ = {
    "condev": (
        "Connected to",
        ('**/iTunes_Control/iTunes/iTunesPrefs'),
        get_conDev)
}
    
