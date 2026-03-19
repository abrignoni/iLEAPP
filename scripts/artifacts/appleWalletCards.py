__artifacts_v2__ = {
    "applewalletcards": {
        "name": "Apple Wallet Cards",
        "description": "Apple Wallet Cards",
        "author": "@any333",
        "creation_date": "2021-02-05",
        "last_update_date": "2025-10-09",
        "requirements": "none",
        "category": "Apple Wallet",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/com.apple.Passbook/Cache.db*'),
        "output_types": "standard",
        "artifact_icon": "credit_card",
    }
}


import re
from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_sqlite_db_records, \
    convert_human_ts_to_utc


def get_bank_card_number(card_information):
    num_of_digits = [19, 18, 17, 16, 15, 14, 13]

    for digit_num in num_of_digits:
        found_entry = re.findall(r'\d{{{digits}}}'.format(digits=digit_num), card_information)
        if found_entry:
            return found_entry[0]


def get_card_type(card_num, num_length):
    first_digit = str(card_num)[:1]
    first_two_digits = str(card_num)[:2]

    if first_digit == '4' and (num_length == 13 or num_length == 16):
        return 'Visa'
    elif first_digit == '5' and num_length == 16:
        return 'Mastercard'
    elif first_digit == '6' and num_length == 16:
        return 'Discover'
    elif (first_two_digits == '34' or first_two_digits == '37') and num_length == 15:
        return 'American Express'
    elif (first_two_digits == '30' or first_two_digits == '36' or first_two_digits == '38') and num_length == 14:
        return 'Diners Club Carte Blanche'
    else:
        return 'Unknown'



@artifact_processor
def applewalletcards(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "Cache.db")
    data_list = []

    query = '''
    SELECT 
        time_stamp, 
        proto_props
    FROM cfurl_cache_response
    INNER JOIN cfurl_cache_blob_data ON cfurl_cache_blob_data.entry_ID = cfurl_cache_response.entry_ID
    WHERE request_key LIKE '%CARDS'
    '''

    data_headers = (
        ('Timestamp (Card Added)', 'datetime'), 
        'Card Number', 
        'Expiration Date', 
        'Type')
    
    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        card_added_timestamp = convert_human_ts_to_utc(record[0])
        card_info = str(record[1], 'utf-8', 'ignore')
        card_number = get_bank_card_number(card_info)
        if card_number is None:
            pass
        else:
            expiration_date = re.findall(r'\d{2}/\d{2}', card_info)
            card_type = get_card_type(card_number, len(card_number))

            data_list.append((card_added_timestamp, card_number, expiration_date[0], card_type))
                
    return data_headers, data_list, source_path
