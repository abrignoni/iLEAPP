__artifacts_v2__ = {
    "get_cashApp": {  
        "name": "Cash App",
        "description": "",
        "author": "@gforce4n6",
        "creation_date": "2021-10-06",
        "last_update_date": "2025-09-26",
        "requirements": "none",
        "category": "Banking",
        "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/CCEntitySync-api.squareup.com.sqlite*', '*/mobile/Containers/Shared/AppGroup/*/CCEntitySync-internal.cashappapi.com.sqlite*',),
        "output_types": "standard",
    }
}

from scripts.ilapfuncs import open_sqlite_db_readonly, artifact_processor
from scripts.context import Context

@artifact_processor
def get_cashApp(context:Context):
    for file_found in context.get_files_found():
        file_found = str(file_found)

        if file_found.endswith('.sqlite'):
            db = open_sqlite_db_readonly(file_found)
            db.text_factory = lambda b: b.decode(errors = 'ignore')
            cursor = db.cursor()
            cursor.execute('''SELECT

-- Description of the role of the user account signed into the CashApp application of the device.
CASE WHEN ZPAYMENT.ZSYNCPAYMENT LIKE '%"RECIPIENT"%' THEN 'RECIPIENT' ELSE 'SENDER' END AS "Account Owner Role",

--Full name of the customer as entered into the "First Name" and "Last Name" fields upon application setup.
LTRIM(SUBSTR(CAST(ZCUSTOMER.ZSYNCCUSTOMER AS BLOB), INSTR(CAST(ZCUSTOMER.ZSYNCCUSTOMER AS BLOB), CAST(',"full_name":' AS BLOB)),
instr(CAST(ZCUSTOMER.ZSYNCCUSTOMER AS BLOB), CAST('","is_cash' AS BLOB)) - 
instr(CAST(ZCUSTOMER.ZSYNCCUSTOMER AS BLOB), CAST(',"full_name":' AS BLOB))), ',"full_name":"') AS 'CUSTOMER FULL DISPLAY NAME', 

--Customer's username created upon application setup.
CASE WHEN INSTR(ZSYNCCUSTOMER, '"cashtag":null') THEN '***NO CASH TAG***' WHEN ZSYNCCUSTOMER LIKE '%C_INCOMING_TRANSFER%' THEN '***NO CASH TAG***' ELSE
LTRIM(SUBSTR(CAST(ZCUSTOMER.ZSYNCCUSTOMER AS BLOB), INSTR(CAST(ZCUSTOMER.ZSYNCCUSTOMER AS BLOB), CAST(',"cashtag":' AS BLOB)),
instr(CAST(ZCUSTOMER.ZSYNCCUSTOMER AS BLOB), CAST('","is_verification' AS BLOB)) - 
instr(CAST(ZCUSTOMER.ZSYNCCUSTOMER AS BLOB), CAST(',"cashtag":' AS BLOB))), ',"cashtag":"') END CASHTAG,

--Transaction amount sent/received between the account user and customer
printf("$%.2f", LTRIM( SUBSTR(CAST(ZPAYMENT.ZSYNCPAYMENT AS BLOB), INSTR(CAST(ZPAYMENT.ZSYNCPAYMENT AS BLOB), CAST('{"amount":' AS BLOB)),
instr(CAST(ZPAYMENT.ZSYNCPAYMENT AS BLOB), CAST(',"currency' AS BLOB)) - 
instr(CAST(ZPAYMENT.ZSYNCPAYMENT AS BLOB), CAST('ount":' AS BLOB)) - 6), '{"amount":') / 100.0) AS 'Transaction Amount',

--Note provided by the sender. Like a memo line on a bank check.
CASE WHEN ZPAYMENT.ZSYNCPAYMENT LIKE '%"note"%' THEN LTRIM( SUBSTR(CAST(ZPAYMENT.ZSYNCPAYMENT AS BLOB), INSTR(CAST(ZPAYMENT.ZSYNCPAYMENT AS BLOB), CAST(',"note":' AS BLOB)),
instr(CAST(ZPAYMENT.ZSYNCPAYMENT AS BLOB), CAST(',"sent' AS BLOB)) - 
instr(CAST(ZPAYMENT.ZSYNCPAYMENT AS BLOB), CAST('"note":' AS BLOB))), ',"note":') ELSE '***NO NOTE PRESENT***' END NOTE, 

--State of the transaction. Certain times the user may have to accept or decline a payment or payment request from the sender.
CASE WHEN ZPAYMENT.ZSYNCPAYMENT LIKE '%"COMPLETED"%' THEN 'COMPLETED' WHEN ZPAYMENT.ZSYNCPAYMENT LIKE '%"CANCELED"%' THEN 'CANCELED' ELSE 'WAITING ON RECIPIENT' END AS 'Transaction State',

--Unix Epoch timestamp for the transaction display time.
datetime(ZPAYMENT.ZDISPLAYDATE/1000.0,'unixepoch') as "TRANSACTION DISPLAY DATE"

FROM ZPAYMENT
INNER JOIN ZCUSTOMER ON ZCUSTOMER.ZCUSTOMERTOKEN = ZPAYMENT.ZREMOTECUSTOMERID
ORDER BY ZPAYMENT.ZDISPLAYDATE ASC
                            ''')

            all_rows = cursor.fetchall()
            db_file = file_found
        
        data_list = []
        for row in all_rows:
            data_list.append((row[6], row[1], row[2], row[0], row[3], row[5], row[4], db_file))

        db.close()

    data_headers = ('Transaction Date', 'Display Name', 'Cashtag', 'Account Owner Role', 'Currency Amount', 'Transaction State', 'Transaction State', 'Source DB')
    return data_headers, data_list, ''