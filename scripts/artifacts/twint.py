# Created by @KefreR (Frank Ressat)

from scripts.ilapfuncs import logfunc, logdevinfo, timeline, kmlgen, tsv, is_platform_windows, open_sqlite_db_readonly
from scripts.artifact_report import ArtifactHtmlReport

def get_twint(files_found, report_folder, seeker, wrap_text):
    for file_found in files_found:
        file_found = str(file_found)

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
        SELECT
        ZTRANSACTION.Z_PK,
        datetime(ZTRANSACTION.ZCREATIONDATE+978307200,'UNIXEPOCH', 'LOCALTIME'), 
        datetime(ZTRANSACTION.ZMODIFIEDTIMESTAMP+978307200,'UNIXEPOCH', 'LOCALTIME'), 
        datetime(ZTRANSACTION.ZSECONDPHASETIMESTAMP+978307200,'UNIXEPOCH', 'LOCALTIME'), 
        datetime(ZTRANSACTION.ZSTATUSPENDINGUNTILDATE+978307200,'UNIXEPOCH', 'LOCALTIME'),
        ZTRANSACTION.ZMERCHANTBRANCHNAME,
        ZTRANSACTION.ZMERCHANTNAME,
        ZTRANSACTION.ZP2PSENDERMOBILENR,
        ZTRANSACTION.ZP2PINITIATEMESSAGE,
        ZTRANSACTION.ZP2PRECIPIENTMOBILENR, 
        ZTRANSACTION.ZP2PRECIPIENTNAME ,
        ZTRANSACTION.ZP2PREPLYMESSAGE,
        ZTRANSACTION.ZAUTHORIZEDAMOUNT, 
        ZTRANSACTION.ZPAIDAMOUNT, 
        ZTRANSACTION.ZREQUESTEDAMOUNT, 
        ZTRANSACTION.ZDISCOUNT, 
        ZTRANSACTION.ZCURRENCY,
        ZTRANSACTION.ZCONTENTREFERENCE, 
        ZTRANSACTION.ZORDERLINK, 
        ZTRANSACTION.ZCONTENTREFERENCESOURCEVALUE, 
        ZTRANSACTION.ZORDERSTATEVALUE,
        ZTRANSACTION.ZORDERTYPEVALUE,
        ZTRANSACTION.ZP2PHASPICTURE,
        ZTRANSACTION.ZTRANSACTIONSIDEVALUE,
        ZTRANSACTION.ZMERCHANTCONFIRMATION FROM ZTRANSACTION''')

    data_list = cursor.fetchall()
    usagentries = len(data_list)

    if usagentries > 0:
        descritpion ="Twint - Transaction"
        report = ArtifactHtmlReport(f'{descritpion}')
        report.start_artifact_report(report_folder, f'{descritpion}')
        report.add_script()
        data_headers = (
            'Index', 'Creation date', 'Sender confirmation date', 'Receiver validation date', 'Transaction expiry date',
            'Merchant branch name','Merchant name', 'Sender mobile number', 'Sender message', 'Receiver mobiler number', 
            'Receiver contact name', 'Response message', 'Amount authorized for the transaction', 'Paid amount', 
            'Requested amount', 'Discount', 'Currency', 'Content reference', 'Order link','Presence of multimedia content',
            'Transaction status', 'Type of transaction', 'Direction of the transaction', 'Merchant confirmation' )
        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()

        tsvname = f'{descritpion}'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('Twint - No data available')

__artifacts__ = {
    "twint": (
        "Twint",
        ('*/var/mobile/Containers/Data/Application/*/Library/Application Support/Twint.sqlite'),
        get_twint)
}