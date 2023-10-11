import datetime
import os
import re
import sqlite3

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly

def get_browser_name(file_name):

    if 'brave' in file_name.lower():
        return 'Brave'
    elif 'microsoft' in file_name.lower():
        return 'Edge'
    elif 'opera' in file_name.lower():
        return 'Opera'
    elif 'chrome' in file_name.lower():
        return 'Chrome'
    else:
        return 'Unknown'

def decrypt(ciphertxt, key=b"peanuts"):
    if re.match(rb"^v1[01]",ciphertxt): 
        ciphertxt = ciphertxt[3:]
    salt = b"saltysalt"
    derived_key = PBKDF2(key, salt, 0x10, 1)
    iv = b" "*0x10
    cipher = AES.new(derived_key, AES.MODE_CBC, IV=iv)
    try:
        plaintxt_pad = cipher.decrypt(ciphertxt)
        plaintxt = plaintxt_pad[:-ord(plaintxt_pad[len(plaintxt_pad)-1:])]
    except ValueError as ex:
        logfunc('Exception while decrypting data: ' + str(ex))
        plaintxt = b''
    return plaintxt

def get_valid_date(d1, d2):
    '''Returns a valid date based on closest year to now'''
    # Since the dates in question will be hundreds of years apart, this should be easy
    if d1 == '': return d2
    if d2 == '': return d1

    year1 = int(d1[0:4])
    year2 = int(d2[0:4])

    today = datetime.datetime.today()
    diff1 = abs(today.year - year1)
    diff2 = abs(today.year - year2)

    if diff1 < diff2:
        return d1
    else:
        return d2

def get_chromeLoginData(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'Login Data': # skip -journal and other files
            continue
        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        username_value,
        password_value,
        CASE date_created 
            WHEN "0" THEN "" 
            ELSE datetime(date_created / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
            END AS "date_created_win_epoch", 
        CASE date_created WHEN "0" THEN "" 
            ELSE datetime(date_created / 1000000 + (strftime('%s', '1970-01-01')), "unixepoch")
            END AS "date_created_unix_epoch",
        origin_url,
        blacklisted_by_user
        FROM logins
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'{browser_name} - Login Data')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{browser_name} - Login Data.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('Created Time','Username','Password','Origin URL','Blacklisted by User', 'Browser Name') 
            data_list = []
            for row in all_rows:
                password = ''
                password_enc = row[1]
                if password_enc:
                    password = decrypt(password_enc).decode("utf-8", 'replace')
                valid_date = get_valid_date(row[2], row[3])
                data_list.append( (valid_date, row[0], password, row[4], row[5], browser_name) )

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'{browser_name} - Login Data'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'{browser_name} - Login Data'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc(f'No {browser_name} - Login Data available')
        
        db.close()
    
__artifacts__ = {
        "ChromeLoginData": (
                "Chromium",
                ('*/Chrome/Default/Login Data*', '*/app_sbrowser/Default/Login Data*', '*/app_opera/Login Data*'),
                get_chromeLoginData)
}