import re

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_appleWalletCards(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.db'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''SELECT 
                            TIME_STAMP, 
                            PROTO_PROPS
                            FROM CFURL_CACHE_RESPONSE
                            INNER JOIN CFURL_CACHE_BLOB_DATA ON CFURL_CACHE_BLOB_DATA.ENTRY_ID = CFURL_CACHE_RESPONSE.ENTRY_ID
                            WHERE REQUEST_KEY LIKE '%CARDS'
                            ''')

            all_rows = cursor.fetchall()
            db_file = file_found

    if len(all_rows) > 0:
        for row in all_rows:
            card_info = str(row[1], 'utf-8', 'ignore')
            card_number = get_bank_card_number(card_info)
            if card_number is None:
                pass
            else:
                expiration_date = re.findall(r'\d{2}/\d{2}', card_info)
                card_type = get_card_type(card_number, len(card_number))

                data_list.append((row[0], card_number, expiration_date[0], card_type))
                
    if len(data_list) > 0:
        report = ArtifactHtmlReport('Cards')
        report.start_artifact_report(report_folder, 'Cards')
        report.add_script()
        data_headers = ('Timestamp (Card Added)', 'Card Number', 'Expiration Date', 'Type')
        report.write_artifact_data_table(data_headers, data_list, db_file)
        report.end_artifact_report()

        tsvname = 'Apple Wallet Cards'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Apple Wallet Cards'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Apple Wallet Cards available')

    db.close()
    return


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

__artifacts__ = {
    "applewalletcards": (
        "Apple Wallet",
        ('*/mobile/Containers/Data/Application/*/Library/Caches/com.apple.Passbook/Cache.db*'),
        get_appleWalletCards)
}
