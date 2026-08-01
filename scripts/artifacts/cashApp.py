__artifacts_v2__ = {
    "get_cashApp": {
        "name": "Cash App",
        "description": "Parses Cash App transactions and account data from the CCEntitySync SQLite stores.",
        "author": "@gforce4n6",
        "creation_date": "2021-10-06",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Banking",
        "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/CCEntitySync-api.squareup.com.sqlite*',
                  '*/mobile/Containers/Shared/AppGroup/*/CCEntitySync-internal.cashappapi.com.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "currency-dollar",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | Cash App 5.46.0 | 1 row",
            "abe_ios16": "iOS 16.5 | Cash App 4.0 | 1 row",
        },
    }
}

from scripts.ilapfuncs import open_sqlite_db_readonly, artifact_processor, convert_unix_ts_to_utc

@artifact_processor
def get_cashApp(context):
    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('.sqlite'):
            db = open_sqlite_db_readonly(file_found)
            db.text_factory = lambda b: b.decode(errors = 'ignore')
            cursor = db.cursor()
            cursor.execute('''SELECT

-- Description of the role of the user account signed into the CashApp application of the device.
-- Unrecognized role values are reported as stored in the record.
CASE WHEN ZPAYMENT.ZSYNCPAYMENT LIKE '%"RECIPIENT"%' THEN 'RECIPIENT'
WHEN INSTR(ZPAYMENT.ZSYNCPAYMENT, '"role":"') > 0 THEN SUBSTR(ZPAYMENT.ZSYNCPAYMENT, INSTR(ZPAYMENT.ZSYNCPAYMENT, '"role":"') + 8,
INSTR(SUBSTR(ZPAYMENT.ZSYNCPAYMENT, INSTR(ZPAYMENT.ZSYNCPAYMENT, '"role":"') + 8), '"') - 1) END AS "Account Owner Role",

--Full name from the name fields of the customer record.
LTRIM(SUBSTR(CAST(ZCUSTOMER.ZSYNCCUSTOMER AS BLOB), INSTR(CAST(ZCUSTOMER.ZSYNCCUSTOMER AS BLOB), CAST(',"full_name":' AS BLOB)),
instr(CAST(ZCUSTOMER.ZSYNCCUSTOMER AS BLOB), CAST('","is_cash' AS BLOB)) - 
instr(CAST(ZCUSTOMER.ZSYNCCUSTOMER AS BLOB), CAST(',"full_name":' AS BLOB))), ',"full_name":"') AS 'CUSTOMER FULL DISPLAY NAME', 

--Customer's cashtag username from the customer record.
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
-- Unrecognized state values are reported as stored in the record.
CASE WHEN ZPAYMENT.ZSYNCPAYMENT LIKE '%"COMPLETED"%' THEN 'COMPLETED' WHEN ZPAYMENT.ZSYNCPAYMENT LIKE '%"CANCELED"%' THEN 'CANCELED'
WHEN INSTR(ZPAYMENT.ZSYNCPAYMENT, '"state":"') > 0 THEN SUBSTR(ZPAYMENT.ZSYNCPAYMENT, INSTR(ZPAYMENT.ZSYNCPAYMENT, '"state":"') + 9,
INSTR(SUBSTR(ZPAYMENT.ZSYNCPAYMENT, INSTR(ZPAYMENT.ZSYNCPAYMENT, '"state":"') + 9), '"') - 1) END AS 'Transaction State',

--Unix Epoch timestamp for the transaction display time.
ZPAYMENT.ZDISPLAYDATE as "TRANSACTION DISPLAY DATE"

FROM ZPAYMENT
INNER JOIN ZCUSTOMER ON ZCUSTOMER.ZCUSTOMERTOKEN = ZPAYMENT.ZREMOTECUSTOMERID
ORDER BY ZPAYMENT.ZDISPLAYDATE ASC
                            ''')

            all_rows = cursor.fetchall()
            
            for row in all_rows:
                date = convert_unix_ts_to_utc(row[6])
                data_list.append((date, row[1], row[2], row[0], row[3], row[5], row[4], context.get_relative_path(file_found)))

    data_headers = (('Transaction Date', 'datetime'), 'Display Name', 'Cashtag', 'Account Owner Role',
                    'Currency Amount', 'Transaction State', 'Note', 'Source File')

    db.close()
    
    return data_headers, data_list, 'see Source File for more info'
