__artifacts_v2__ = {
    "get_cashAppB": {
        "name": "Cash App",
        "description": "",
        "author": "Alexis Brignoni",
        "version": "0.0.1",
        "date": "2025-08-24",
        "requirements": "none",
        "category": "Banking",
        "notes": "",
        "paths": ('*/Environments/Production/Accounts/*/*-internal.cashappapi.com.sqlite*'),
        "output_types": "none",
        "function": "get_cashAppB",
        "output_types": "all",
        "artifact_icon": "dollar-sign",
    }
}

import blackboxprotobuf
import sqlite3
import json
from datetime import datetime, timezone
from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records

@artifact_processor
def get_cashAppB(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            source = file_found
            
            query = """
            SELECT
            ZDISPLAYDATE,
            ZCUSTOMERTOKEN,
            ZSYNCCUSTOMER,
            ZSYNCPAYMENT
            FROM ZCUSTOMER
            JOIN ZPAYMENT
                ON ZCUSTOMER.ZCUSTOMERTOKEN = ZPAYMENT.ZREMOTECUSTOMERID;
            """
            results = get_sqlite_db_records(file_found, query)
        
            for row in results:
                timestamp = datetime.fromtimestamp(row[0]/1000, tz=timezone.utc)
                customertoken = row[1]
                protocustomer, types = blackboxprotobuf.decode_message(row[2])
                protopayment, types = blackboxprotobuf.decode_message(row[3])
        
                payment = (protopayment['1'].get('16'))
                if payment is not None:
                    payment = payment.decode()
                    payment = json.loads(payment)
                    amount = payment.get('amount')
                    howmuch = amount['amount']
                    currency = amount['currency_code']
                    note = payment.get('note')
                    
        
                name = (protocustomer['1'].get('3'))
                if name is not None:
                    name = name.decode()
                    
                username = (protocustomer['1'].get('8'))
                if username is not None:
                    username = username.decode()
                    
                extrainfo = (protocustomer['1'].get('15'))
                if extrainfo is not None:
                    extrainfo = extrainfo.decode()
                    extrainfo = json.loads(extrainfo)
                    
                    id = (extrainfo['id'])
                    fullname = (extrainfo['full_name'])
                    region = (extrainfo.get('region'))
                    dunits = (extrainfo.get('display_units'))
                    
                data_list.append((timestamp,customertoken,name,username,id,fullname,howmuch,currency,note,region,dunits,str(protocustomer),str(protopayment)))
        
    data_headers = (('Timestamp', 'datetime'), 'Customer Token', 'Name', 'Username','ID','Full Name', 'Amount', 'Currency','Note', 'Region', 'Units','Customer Data', 'Payment Data',)
    return data_headers,data_list,source
    
    