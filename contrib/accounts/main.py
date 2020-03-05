import os
import plistlib
import sqlite3

from common import logfunc
from settings import *


def accs(filefound):
    try:
        db = sqlite3.connect(filefound[0])
        cursor = db.cursor()
        cursor.execute(
            """
		SELECT
		ZACCOUNTTYPEDESCRIPTION,
		ZUSERNAME,
		DATETIME(ZDATE+978307200,'UNIXEPOCH','UTC' ) AS 'ZDATE TIMESTAMP',
		ZACCOUNTDESCRIPTION,
		ZACCOUNT.ZIDENTIFIER,
		ZACCOUNT.ZOWNINGBUNDLEID
		FROM ZACCOUNT
		JOIN ZACCOUNTTYPE ON ZACCOUNTTYPE.Z_PK=ZACCOUNT.ZACCOUNTTYPE
		ORDER BY ZACCOUNTTYPEDESCRIPTION
		"""
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            logfunc(f"Account Data function executing")

            if os.path.isdir(os.path.join(reportfolderbase, "Accounts/")):
                pass
            else:
                os.makedirs(os.path.join(reportfolderbase, "Accounts"))

            with open(
                os.path.join(reportfolderbase, "Accounts/Accounts.html"),
                "w",
                encoding="utf8",
            ) as f:
                f.write("<html><body>")
                f.write("<h2> Account Data report</h2>")
                f.write(f"Account Data entries: {usageentries}<br>")
                f.write(f"Account Data located at: {filefound[0]}<br>")
                f.write(
                    "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
                )
                f.write("<br/>")
                f.write("")
                f.write(f'<table class="table sticky">')
                f.write(
                    f"<tr><th>Account Desc</th><th>Usermane</th><th>Timestamp</th><th>Description</th><th>Identifier</th><th>Bundle ID</th></tr>"
                )
                for row in all_rows:
                    f.write(
                        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td></tr>"
                    )
                f.write(f"</table></body></html>")
                logfunc(f"Account Data function completed")
        else:
            logfunc("No Account Data available")
    except:
        logfunc("Error in Account Data Section.")


def confaccts(filefound):
    logfunc(f"Config Accounts function executing")

    try:
        if os.path.isdir(reportfolderbase + "Accounts/"):
            pass
        else:
            os.makedirs(reportfolderbase + "Accounts")
    except:
        logfunc("Error creating confaccts() report directory")

    try:
        with open(reportfolderbase + "Accounts/Config Accounts.html", "w") as f:
            f.write("<html><body>")
            f.write("<h2>Config Accounts Report</h2>")
            f.write(f"Config Accounts located at {filefound[0]}<br>")
            f.write(
                "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
            )
            f.write("<br/>")
            f.write("")
            f.write(f"<table>")
            f.write(f"<tr><td>Key</td><td>Values</td></tr>")
            with open(filefound[0], "rb") as fp:
                pl = plistlib.load(fp)
                for key, val in pl.items():
                    f.write(f"<tr><td>{key}</td><td>{val}</td></tr>")
            f.write(f"</table></body></html>")
    except:
        logfunc("Error in Config Accounts function.")
    logfunc("Config Accounts function completed.")
