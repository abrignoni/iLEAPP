__artifacts_v2__ = {
    'appleWalletTransactions': {
        'name': 'Apple Wallet Transactions',
        'description': 'Apple Wallet Transactions',
        'author': '@any333',
        'creation_date': '2021-02-05',
        'last_update_date': '2025-10-09',
        'requirements': 'none',
        'category': 'Apple Wallet',
        'notes': '',
        'paths': ('*/mobile/Library/Passes/passes23.sqlite*'),
        'output_types': 'all',
        'artifact_icon': 'credit-card',
        'sample_data': {
            'ctf2020_ios12': 'iOS 12.4 | 0 rows',
            'dexter_ios18': 'iOS 18.3.2 | 10 rows',
            'felix_ios17': 'iOS 17.6.1 | 0 rows',
            'fsfull002_ios17': 'iOS 17.1 | 0 rows',
            'hc_ios18_7': 'iOS 18.7.8 | 0 rows',
            'iphone11_ios17': 'iOS 17.3 | 0 rows',
            'iphone12_ios18': 'iOS 18.7 | 0 rows',
            'iphone14plus_ios18': 'iOS 18.0 | 0 rows',
            'otto_ios17': 'iOS 17.5.1 | 0 rows',
            'abe_ios16': 'iOS 16.5 | 1 row',
            'felix23_ios16': 'iOS 16.5 | 0 rows',
            'hickman_ios13': 'iOS 13.3.1 | 0 rows',
            'hickman_ios14': 'iOS 14.3 | 0 rows',
            'jess_ios15': 'iOS 15.0.2 | 0 rows',
            'magnet_ios16': 'iOS 16.1.1 | 0 rows',
        },
    }
}


from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_sqlite_db_records, convert_cocoa_core_data_ts_to_utc


@artifact_processor
def appleWalletTransactions(context):
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
        'Merchant',
        'Locality',
        'Administrative Area',
        'Currency Amount',
        'Currency Type',
        ('Location Date', 'datetime'),
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
            transaction_date, record[1], record[2], record[3], record[4], record[5], location_date,
            record[7], record[8], record[9], record[10], record[11], record[12], record[13]))

    return data_headers, data_list, source_path
