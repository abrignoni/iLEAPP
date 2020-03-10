"""
This module intends to be the source of truth for all configuration settings.
"""
import datetime
import os


nl = "\n"
now = datetime.datetime.now()
currenttime = str(now.strftime("%Y-%m-%d_%A_%H%M%S"))

reportfolderbase = "./ILEAPP_Reports_" + currenttime + "/"
# alias for new code to use
report_folder_base = reportfolderbase

base = "/ILEAPP_Reports_" + currenttime + "/"
temp = os.path.join(report_folder_base, "temp", "")
