__artifacts_v2__ = {
    'appleWalletTransactions': {
        'name': 'Apple Wallet Transactions',
        'description': 'Apple Wallet Transactions',
        'author': '@any333',
        'creation_date': '2021-02-05',
        'last_update_date': '2025-04-05',
        'requirements': 'none',
        'category': 'Apple Wallet',
        'notes': '',
        'paths': ('*/mobile/Library/Passes/passes23.sqlite*'),
        'output_types': 'all',
        'artifact_icon': 'credit_card',
    }
}

from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_sqlite_db_records, convert_cocoa_core_data_ts_to_utc
from scripts.context import Context

@artifact_processor
def appleWalletTransactions(context:Context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'passes23.sqlite')
    data_list = []

    query = '''
    SELECT
        transaction_date,
        merchant_name,
        locality,
        administrative_area,
        CAST(amount AS REAL)/10000,
        currency_code,
        location_date,
        location_latitude,
        location_longitude,
        location_altitude,
        peer_payment_counterpart_handle,
        peer_payment_memo,
        transaction_status,
        transaction_type
    FROM payment_transaction
    '''

    data_headers = (
        ('Transaction Date', 'datetime'),
        ('Location Date', 'datetime'),
        'Merchant',
        'Locality',
        'Administrative Area',
        'Currency Amount',
        'Currency Type',
        'Latitude',
        'Longitude',
        'Altitude',
        'Peer Payment Handle',
        'Payment Memo',
        'Transaction Status',
        'Transaction Type')

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:

        transaction_date = convert_cocoa_core_data_ts_to_utc(
            record['transaction_date'])
        location_date = convert_cocoa_core_data_ts_to_utc(
            record['location_date'])

        data_list.append((
            transaction_date, location_date, record[1], record[2], record[3], record[4], record[5],
            record[7], record[8], record[9], record[10], record[11], record[12], record[13]))

    return data_headers, data_list, source_path
