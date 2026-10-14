__artifacts_v2__ = {
    "twint_transactions": {
        "name": "Twint - Transactions",
        "description": "Rows of the ZTRANSACTION table of Twint.sqlite. ZP2PHASPICTURE, "
                       "ZORDERSTATEVALUE, ZORDERTYPEVALUE and ZTRANSACTIONSIDEVALUE are "
                       "reported as stored; their value meanings are not established. "
                       "No registered corpus coverage is recorded for this artifact.",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2023-11-21",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "Finance",
        "notes": "The four As Stored columns use their SQLite column names and retain the "
                 "selected values without interpretation. Their names do not establish "
                 "attachment presence, transaction status, transaction type or transaction "
                 "direction. Every matched Twint.sqlite is read, and the report's located at "
                 "line lists each one read. "
                 "Original parser credit: @KefreR (Frank Ressat).",
        "paths": ('*/var/mobile/Containers/Data/Application/*/Library/Application Support/Twint.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "currency-dollar"
    }
}
from scripts.ilapfuncs import (
    artifact_processor,
    get_sqlite_db_records,
    convert_cocoa_core_data_ts_to_utc
    )


@artifact_processor
def twint_transactions(context):
    files_found = context.get_files_found()
    data_list = []
    source_paths = []

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

    db_records = []
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('Twint.sqlite'):
            continue
        relative_path = context.get_relative_path(file_found)
        if relative_path in source_paths:
            continue
        source_paths.append(relative_path)
        db_records.extend(get_sqlite_db_records(file_found, query) or [])

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
        ('Creation date', 'datetime'),
        ('Modified Timestamp', 'datetime'),
        ('Second Phase Timestamp', 'datetime'),
        ('Status Pending Until', 'datetime'),
        'Merchant branch name', 'Merchant name',
        ('Sender mobile number', 'phonenumber'),
        'Sender message',
        ('Receiver mobile number', 'phonenumber'),
        'Receiver contact name', 'Response message',
        'Amount authorized for the transaction', 'Paid amount',
        'Requested amount', 'Discount', 'Currency',
        'Content reference', 'Order link', 'ZP2PHASPICTURE (As Stored)',
        'ZORDERSTATEVALUE (As Stored)', 'ZORDERTYPEVALUE (As Stored)',
        'ZTRANSACTIONSIDEVALUE (As Stored)', 'Merchant confirmation')

    return data_headers, data_list, '\n'.join(source_paths)
