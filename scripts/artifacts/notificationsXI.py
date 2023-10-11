import os
import textwrap
import datetime
import sys
import re
import string
import glob
from scripts.ccl import ccl_bplist
from html import escape

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows


def get_notificationsXI(files_found, report_folder, seeker, wrap_text, timezone_offset):
    pathfound = 0
    count = 0
    notdircount = 0
    exportedbplistcount = 0
    unix = datetime.datetime(1970, 1, 1)  # UTC
    cocoa = datetime.datetime(2001, 1, 1)  # UTC
    delta = cocoa - unix

    __location__ = os.path.dirname(os.path.abspath(__file__))

    f = open(os.path.join(__location__,"NotificationParams.txt"), "r")
    notiparams = [line.strip() for line in f]
    f.close()
    
    pathfound = str(files_found[0])
    #logfunc(pathfound)
    if pathfound == 0:
        logfunc("No PushStore directory located")
    else:
        #logfunc('Pathfound was found')
        folder = report_folder 
        # logfunc("Processing:")
        for filename in glob.iglob(pathfound + "/**", recursive=True):
            if os.path.isfile(filename):  # filter dirs
                file_name = os.path.splitext(os.path.basename(filename))[0]
                # get extension and iterate on those files
                # file_extension = os.path.splitext(filename)
                # logfunc(file_extension)
                # create directory
                if filename.endswith("pushstore"):
                    # create directory where script is running from
                    #logfunc(filename)  # full path
                    notdircount = notdircount + 1
                    # logfunc (os.path.basename(file_name)) #filename with  no extension
                    openplist = os.path.basename(
                        os.path.normpath(filename)
                    )  # filename with extension
                    # logfunc (openplist)
                    # bundlepath = (os.path.basename(os.path.dirname(filename)))#previous directory
                    bundlepath = file_name
                    appdirect = folder + bundlepath
                    # logfunc(appdirect)
                    os.makedirs(appdirect)

                    # open the plist
                    p = open(filename, "rb")
                    plist = ccl_bplist.load(p)
                    plist2 = plist["$objects"]

                    long = len(plist2)
                    # logfunc (long)
                    h = open(
                        appdirect + "/DeliveredNotificationsReport.html", "w"
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

                    f = open(os.path.join(__location__,"script.txt"), "r")
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
                                        #logfunc("Bplist processed and exported.")
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

    path = report_folder
    level2, level1 = (os.path.split(path))
    
    #final = level2+'/'+level1
    dict = {}
    files = os.listdir(path)
    for name in files:
        try:
            size = os.path.getsize(f"{path}{name}/DeliveredNotificationsReport.html")
            key = (f'<a href = "{level2}/{name}/DeliveredNotificationsReport.html" style = "color:blue" target="content">{name}</a>')
            dict[key] = size
        except NotADirectoryError as nade:
            logfunc(nade)
            pass

        
    data_list = []
    for k, v in dict.items():
        v = v / 1000
        # logfunc(f'{k} -> {v}')
        data_list.append((k, v))
    
    location = pathfound
    description = 'iOS <= 11 Notifications'
    report = ArtifactHtmlReport('iOS Notificatons')
    report.start_artifact_report(report_folder, 'iOS Notifications', description)
    report.add_script()
    data_headers = ('Bundle GUID', 'Reports Size')
    report.write_artifact_data_table(data_headers, data_list, location, html_escape=False)
    report.end_artifact_report()
    

    logfunc("Total notification directories processed:" + str(notdircount))
    logfunc("Total exported bplists from notifications:" + str(exportedbplistcount))
    if notdircount == 0:
        logfunc("No notifications located.")
    
__artifacts__ = {
    "notificationsXI": (
        "Notifications",
        ('*PushStore*'),
        get_notificationsXI)
}  
       



  