import os
import plistlib

from common import logfunc
from contrib.utils import silence_and_log
from settings import *


def mobilact(filefound):
    logfunc(f"Mobile Activation function executing")
    try:
        linecount = 0
        hitcount = 0
        activationcount = 0
        filescounter = 0

        if os.path.exists(os.path.join(reportfolderbase, "SysDiagnose/")):
            pass
        else:
            os.makedirs(os.path.join(reportfolderbase, "SysDiagnose/"))

        f = open(
            os.path.join(reportfolderbase, "SysDiagnose/Mobile Activation Logs.html"),
            "w",
        )
        f.write("<html><body>")
        f.write("<h2>Mobile Activation Report</h2>")
        f.write(
            "Logs in private/var/mobile/Library/Logs/mobileactivationd/mobileactivationd.log.*<br>"
        )

        for filename in filefound:
            file = open(filename, "r", encoding="utf8")
            filescounter = filescounter + 1

            for line in file:
                linecount += 1
                if "perform_data_migration" in line:
                    hitcount += 1
                    # print("\n" + line)
                    txts = line.split()
                    # print(txts, linecount)
                    # print(len(txts))
                    dayofweek = txts[0]
                    month = txts[1]
                    day = txts[2]
                    time = txts[3]
                    year = txts[4]
                    frombuild = txts[12]
                    tobuild = txts[14]
                    f.write(
                        "<br><br>"
                        + day
                        + " "
                        + month
                        + " "
                        + year
                        + " "
                        + time
                        + " Upgraded from "
                        + frombuild
                        + " to "
                        + tobuild
                        + " [line "
                        + str(linecount)
                        + "]"
                    )

                if (
                    "MA: main: ____________________ Mobile Activation Startup _____________________"
                    in line
                ):
                    activationcount += 1
                    # print("\n" + line)
                    txts = line.split()
                    # print(txts, linecount)
                    # print(len(txts))
                    dayofweek = txts[0]
                    month = txts[1]
                    day = txts[2]
                    time = txts[3]
                    year = txts[4]
                    f.write(
                        "<br><br>"
                        + day
                        + " "
                        + month
                        + " "
                        + year
                        + " "
                        + time
                        + " Mobile Activation Startup "
                        + " [line "
                        + str(linecount)
                        + "]"
                    )

                if "MA: main: build_version:" in line:
                    # print("\n" + line)
                    txts = line.split()
                    # print(txts, linecount)
                    # print(len(txts))
                    dayofweek = txts[0]
                    month = txts[1]
                    day = txts[2]
                    time = txts[3]
                    year = txts[4]
                    buildver = txts[11]
                    f.write(
                        "<br>"
                        + day
                        + " "
                        + month
                        + " "
                        + year
                        + " "
                        + time
                        + " Mobile Activation Build Version = "
                        + buildver
                    )

                if "MA: main: hardware_model:" in line:
                    # print("\n" + line)
                    txts = line.split()
                    # print(txts, linecount)
                    # print(len(txts))
                    dayofweek = txts[0]
                    month = txts[1]
                    day = txts[2]
                    time = txts[3]
                    year = txts[4]
                    hwmodel = txts[11]
                    f.write(
                        "<br>"
                        + day
                        + " "
                        + month
                        + " "
                        + year
                        + " "
                        + time
                        + " Mobile Activation Hardware Model = "
                        + hwmodel
                    )

                if "MA: main: product_type:" in line:
                    # print("\n" + line)
                    txts = line.split()
                    # print(txts, linecount)
                    # print(len(txts))
                    dayofweek = txts[0]
                    month = txts[1]
                    day = txts[2]
                    time = txts[3]
                    year = txts[4]
                    prod = txts[11]
                    f.write(
                        "<br>"
                        + day
                        + " "
                        + month
                        + " "
                        + year
                        + " "
                        + time
                        + " Mobile Activation Product Type = "
                        + prod
                    )

                if "MA: main: device_class:" in line:
                    # print("\n" + line)
                    txts = line.split()
                    # print(txts, linecount)
                    # print(len(txts))
                    dayofweek = txts[0]
                    month = txts[1]
                    day = txts[2]
                    time = txts[3]
                    year = txts[4]
                    devclass = txts[11]
                    f.write(
                        "<br>"
                        + day
                        + " "
                        + month
                        + " "
                        + year
                        + " "
                        + time
                        + " Mobile Activation Device Class = "
                        + devclass
                    )
            file.close()
        f.write("<br><br>Found " + str(hitcount) + " Upgrade entries")
        f.write(
            "<br> Found " + str(activationcount) + " Mobile Activation Startup entries"
        )
        f.write("</body></html>")
        f.close()

        logfunc(f"Mobile Activation completed executing")
    except:
        logfunc("Error in MobileActivation Logs section")


def bkupstate(filefound):
    logfunc(f"BackupStateInfo function executing")
    try:
        if os.path.exists(os.path.join(reportfolderbase, "SysDiagnose/")):
            pass
        else:
            os.makedirs(os.path.join(reportfolderbase, "SysDiagnose/"))

        f = open(os.path.join(reportfolderbase, "SysDiagnose/BackupStateInfo.txt"), "w")
        p = open(filefound[0], "rb")
        plist = plistlib.load(p)
        # create html headers
        filedatahtml = open(
            os.path.join(reportfolderbase, "SysDiagnose/BackupStateInfo.html"),
            mode="a+",
        )
        filedatahtml.write("<html><body>")
        filedatahtml.write("<h2>BackupStateInfo Report </h2>")
        filedatahtml.write(
            "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
        )
        filedatahtml.write('<table class="table sticky">')
        filedatahtml.write(f'<tr><td colspan = "2">BackupStateInfo Items</td></tr>')

        pl = plist  # This code taken from https://github.com/cheeky4n6monkey/iOS_sysdiagnose_forensic_scripts/blob/master/sysdiagnose-mobilebackup.py

        if "BackupStateInfo" in pl.keys():
            for key, val in pl["BackupStateInfo"].items():
                # print("key = " + str(key) + ", val = " + str(val))
                if key == "date":
                    filedatahtml.write(
                        f"<tr><td>BackupStateInfo Date</td><td>{str(val)}</td></tr>"
                    )
                if key == "isCloud":
                    filedatahtml.write(
                        f"<tr><td>BackupStateInfo isCloud</td><td>{str(val)}</td></tr>"
                    )

        if "RestoreInfo" in pl.keys():
            for key, val in pl["RestoreInfo"].items():
                if key == "RestoreDate":
                    filedatahtml.write(
                        f"<tr><td>RestoreInfo Date</td><td>{str(val)}</td></tr>"
                    )
                if key == "BackupBuildVersion":
                    filedatahtml.write(
                        f"<tr><td>RestoreInfo BackupBuildVersion</td><td>{str(val)}</td></tr>"
                    )
                if key == "DeviceBuildVersion":
                    filedatahtml.write(
                        f"<tr><td>RestoreInfo DeviceBuildVersion</td><td>{str(val)}</td></tr>"
                    )
                if key == "WasCloudRestore":
                    filedatahtml.write(
                        f"<tr><td>RestoreInfo WasCloudRestore</td><td>{str(val)}</td></tr>"
                    )
        filedatahtml.write("</table></html>")
        filedatahtml.write("<br>")

        filedatahtml.write('<table class="table sticky">')
        filedatahtml.write(f'<tr><td colspan = "2">{filefound[0]}</td></tr>')
        filedatahtml.write("<tr><th>Key</th><th>Value</th></tr>")

        for key, val in plist.items():
            f.write(f"{key}	{val}{nl}")
            filedatahtml.write(f"<tr><td>{key}</td><td>{val}</td></tr>")

        f.close()

        # close html footer
        filedatahtml.write("</table></html>")
        filedatahtml.close()
    except:
        logfunc("Error in BackupStateInfo function section")
    logfunc(f"BackupStateInfo function completed.")
