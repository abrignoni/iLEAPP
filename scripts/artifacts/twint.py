__artifacts_v2__ = {
    "twintTransactions": {
        "name": "Twint - Transactions",
        "description": "Extract data related to transactions made with the instant payment app Twint prepaid",
        "author": "@KefreR (Frank Ressat)",
        "version": "0.1",
        "date": "2023-11-21",
        "requirements": "none",
        "category": "Finance",
        "notes": "",
        "paths": ('*/var/mobile/Containers/Data/Application/*/Library/Application Support/Twint.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "dollar-sign"
    }
}


from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, convert_cocoa_core_data_ts_to_utc

@artifact_processor
def twintTransactions(files_found, report_folder, seeker, wrap_text, time_offset):
    data_list = []
    db_file = ''
    db_records = []

    query = '''
        SELECT
            ZTRANSACTION.ZCREATIONDATE, 
            ZTRANSACTION.ZMODIFIEDTIMESTAMP, 
            ZTRANSACTION.ZSECONDPHASETIMESTAMP, 
            ZTRANSACTION.ZSTATUSPENDINGUNTILDATE, 
            ZTRANSACTION.ZMERCHANTBRANCHNAME, 
            ZTRANSACTION.ZMERCHANTNAME, 
            ZTRANSACTION.ZP2PSENDERMOBILENR, 
            ZTRANSACTION.ZP2PINITIATEMESSAGE, 
            ZTRANSACTION.ZP2PRECIPIENTMOBILENR, 
            ZTRANSACTION.ZP2PRECIPIENTNAME, 
            ZTRANSACTION.ZP2PREPLYMESSAGE, 
            ZTRANSACTION.ZAUTHORIZEDAMOUNT, 
            ZTRANSACTION.ZPAIDAMOUNT, 
            ZTRANSACTION.ZREQUESTEDAMOUNT, 
            ZTRANSACTION.ZDISCOUNT, 
            ZTRANSACTION.ZCURRENCY, 
            ZTRANSACTION.ZCONTENTREFERENCE, 
            ZTRANSACTION.ZORDERLINK, 
            ZTRANSACTION.ZP2PHASPICTURE, 
            ZTRANSACTION.ZORDERSTATEVALUE, 
            ZTRANSACTION.ZORDERTYPEVALUE, 
            ZTRANSACTION.ZTRANSACTIONSIDEVALUE, 
            ZTRANSACTION.ZMERCHANTCONFIRMATION
        FROM ZTRANSACTION'''

    for file_found in files_found:
        if file_found.endswith('Twint.sqlite'):
            db_file = file_found
            db_records = get_sqlite_db_records(db_file, query)
            break

    for record in db_records:
        creation_date = convert_cocoa_core_data_ts_to_utc(record[0])
        modified_ts = convert_cocoa_core_data_ts_to_utc(record[1])
        second_phase_ts = convert_cocoa_core_data_ts_to_utc(record[2])
        status_pending_until_date = convert_cocoa_core_data_ts_to_utc(record[3])
        data_list.append(
            (creation_date, modified_ts, second_phase_ts, status_pending_until_date, record[4], record[5], 
             record[6], record[7], record[8], record[9], record[10], record[11], record[12], 
             record[13], record[14], record[15], record[16], record[17], record[18], record[19], 
             record[20], record[21], record[22]))

    data_headers = (
        ('Creation date', 'datetime'), ('Sender confirmation date', 'datetime'), ('Receiver validation date', 'datetime'), 
        ('Transaction expiry date', 'datetime'), 'Merchant branch name', 'Merchant name', 'Sender mobile number', 
        'Sender message', 'Receiver mobile number', 'Receiver contact name', 'Response message', 
        'Amount authorized for the transaction', 'Paid amount', 'Requested amount', 'Discount', 'Currency', 
        'Content reference', 'Order link', 'Presence of multimedia content', 'Transaction status', 'Type of transaction', 
        'Direction of the transaction', 'Merchant confirmation')

    return data_headers, data_list, db_file
