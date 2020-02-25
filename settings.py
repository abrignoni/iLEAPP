"""
This module intends to be the source of truth for all configuration settings.
"""
import datetime

nl = "\n"
now = datetime.datetime.now()
currenttime = str(now.strftime("%Y-%m-%d_%A_%H%M%S"))
reportfolderbase = "./ILEAPP_Reports_" + currenttime + "/"
base = "/ILEAPP_Reports_" + currenttime + "/"
temp = reportfolderbase + "temp/"

# aliases for new code to use
report_folder_base = reportfolderbase
