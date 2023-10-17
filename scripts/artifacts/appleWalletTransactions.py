from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone 


def get_appleWalletTransactions(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('passes23.sqlite'):
            
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''SELECT
                            DATETIME(TRANSACTION_DATE + 978307200,'UNIXEPOCH'),
                            MERCHANT_NAME,
                            LOCALITY,
                            ADMINISTRATIVE_AREA,
                            CAST(AMOUNT AS REAL)/10000,
                            CURRENCY_CODE,
                            DATETIME(LOCATION_DATE + 978307200,'UNIXEPOCH'),
                            LOCATION_LATITUDE,
                            LOCATION_LONGITUDE,
                            LOCATION_ALTITUDE,
                            PEER_PAYMENT_COUNTERPART_HANDLE,
                            PEER_PAYMENT_MEMO,
                            TRANSACTION_STATUS,
                            TRANSACTION_TYPE
                            FROM PAYMENT_TRANSACTION
                            ''')
        
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
    
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            
            timestamptrdate = row[0]
            timestamplocdate = row[6]
            
            if (timestamptrdate == '') or (timestamptrdate == None):
                timestamptrdate = ''
            else:
                timestamptrdate = convert_ts_human_to_utc(row[0])
                timestamptrdate = convert_utc_human_to_timezone(timestamptrdate,timezone_offset)
            
            if (timestamplocdate == '') or (timestamplocdate == None):
                timestamplocdate = ''
            else:
                timestamplocdate = convert_ts_human_to_utc(row[6])
                timestamplocdate = convert_utc_human_to_timezone(timestamplocdate,timezone_offset)
            
            data_list.append((timestamptrdate, row[1], row[2], row[3], row[4], row[5], timestamplocdate, row[7], row[8], row[9], row[10], row[11], row[12], row[13]))

        report = ArtifactHtmlReport('Transactions')
        report.start_artifact_report(report_folder, 'Transactions')
        report.add_script()
        data_headers = ('Transaction Date', 'Merchant', 'Locality', 'Administrative Area', 'Currency Amount', 'Currency Type', 'Location Date', 'Latitude', 'Longitude', 'Altitude', 'Peer Payment Handle', 'Payment Memo', 'Transaction Status', 'Transaction Type')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = 'Apple Wallet Transactions'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Apple Wallet Transactions'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Apple Wallet Transactions available')

    db.close()
    return

__artifacts__ = {
    "applewallettransactions": (
        "Apple Wallet",
        ('*/passes23.sqlite*'),
        get_appleWalletTransactions)
}