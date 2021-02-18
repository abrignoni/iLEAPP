from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly


def get_appleWalletTransactions(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''SELECT
                    DATETIME(PAYMENT_TRANSACTION.TRANSACTION_DATE + 978307200,'UNIXEPOCH') AS "TRANSACTION DATE",
                    PAYMENT_TRANSACTION.MERCHANT_NAME AS "MERCHANT",
                    PAYMENT_TRANSACTION.CURRENCY_CODE AS "CURRENCY TYPE",
                    CAST (PAYMENT_TRANSACTION.AMOUNT AS REAL)/100  AS  "CURRENCY AMOUNT",
                    PAYMENT_TRANSACTION.PEER_PAYMENT_COUNTERPART_HANDLE AS "PEER PAYMENT HANDLE",
                    PAYMENT_TRANSACTION.PEER_PAYMENT_MEMO AS "PAYMENT MEMO",
                    PAYMENT_TRANSACTION.TRANSACTION_STATUS AS "TRANSACTION STATUS",
                    PAYMENT_TRANSACTION.TRANSACTION_TYPE AS "TRANSACTION TYPE"
                    FROM PAYMENT_TRANSACTION
                    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

        report = ArtifactHtmlReport('Transactions')
        report.start_artifact_report(report_folder, 'Transactions')
        report.add_script()
        data_headers = ('Transaction Date', 'Merchant', 'Currency Type', 'Currency Amount', 'Peer Payment Handle', 'Payment Memo', 'Transaction Status', 'Transaction Type')
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
