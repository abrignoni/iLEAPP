import pathlib

from settings import report_folder_base

def logfunc(message=""):
    if pathlib.Path(report_folder_base + "Script Logs/Screen Output.html").is_file():
        with open(
            report_folder_base + "Script Logs/Screen Output.html", "a", encoding="utf8"
        ) as a:
            print(message)
            a.write(message + "<br>")
    else:
        with open(
            report_folder_base + "Script Logs/Screen Output.html", "a", encoding="utf8"
        ) as a:
            print(message)
            a.write(message + "<br>")
