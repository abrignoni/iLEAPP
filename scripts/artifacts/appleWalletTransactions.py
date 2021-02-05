import os
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_applewalletTransactions(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select
	datetime(payment_transaction.transaction_date + 978307200,'unixepoch') AS "Transaction Date",
    payment_transaction.merchant_name AS "Merchant",
	payment_transaction.currency_code AS "Currency Type",
	CAST (payment_transaction.amount as REAL)/100  AS  "Currency Amount",
	payment_transaction.peer_payment_counterpart_handle AS "Peer Payment Handle",
	payment_transaction.peer_payment_memo AS "Payment Memo",
	payment_transaction.transaction_status AS "Transaction Status",
	payment_transaction.transaction_type AS "Transaction Type"
	from payment_transaction
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))

        
        report = ArtifactHtmlReport('Apple Wallet - Transactions')
        report.start_artifact_report(report_folder, 'Apple Wallet - Transactions')
        report.add_script()
        data_headers = ('Transaction Date','Merchant','Currency Type','Currency Amount','Peer Payment Handle','Payment Memo','Transaction Status','Transaction Type')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Apple Wallet - Transactions'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Apple Wallet - Transactions'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Apple Wallet transactions available')

    db.close()
    return      
    
    
