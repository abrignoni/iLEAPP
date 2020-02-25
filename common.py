import pathlib

def logfunc(message=""):
    if pathlib.Path(reportfolderbase + "Script Logs/Screen Output.html").is_file():
        with open(
            reportfolderbase + "Script Logs/Screen Output.html", "a", encoding="utf8"
        ) as a:
            print(message)
            a.write(message + "<br>")
    else:
        with open(
            reportfolderbase + "Script Logs/Screen Output.html", "a", encoding="utf8"
        ) as a:
            print(message)
            a.write(message + "<br>")

