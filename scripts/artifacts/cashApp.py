__artifacts_v2__ = {
    "get_cashApp": {
        "name": "Cash App",
        "description": "Parses Cash App customer and payment records from the CCEntitySync SQLite stores, "
                       "decoding the ZSYNCCUSTOMER and ZSYNCPAYMENT protobuf blobs and the JSON payloads "
                       "they carry.",
        "author": "@gforce4n6, Alexis Brignoni",
        "creation_date": "2021-10-06",
        "last_update_date": "2026-08-25",
        "requirements": "none",
        "category": "Banking",
        "notes": "Merged from the original Cash App and Cash App (B) artifacts. Amounts are stored in the "
                 "smallest denomination unit of the currency (e.g. 100 = $1.00 USD); both the raw stored "
                 "value and a formatted value are reported. Protobuf field positions for name/url/cashtag "
                 "were established through testing. Records whose blobs do not match the expected protobuf "
                 "layout fall back to a raw scan for the role and state values. Reference: Square Developer "
                 "Documentation, 'Working with Monetary Amounts', "
                 "https://developer.squareup.com/docs/build-basics/working-with-monetary-amounts",
        # The first pattern is deliberately not anchored to the app group container: it also
        # matches extractions where that prefix is absent or rooted differently, and it fully
        # covers the narrower AppGroup/*/Environments/... form.
        "paths": ('*/Environments/Production/Accounts/*/CCEntitySync.sqlite*',
                  '*/mobile/Containers/Shared/AppGroup/*/CCEntitySync-internal.cashappapi.com.sqlite*',
                  '*/mobile/Containers/Shared/AppGroup/*/CCEntitySync-api.squareup.com.sqlite*'),
        "output_types": "all",
        "artifact_icon": "currency-dollar",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | Cash App 5.46.0 | 1 row",
            "abe_ios16": "iOS 16.5 | Cash App 4.0 | 1 row",
        },
    }
}

import json
import re

from scripts import blackboxprotobuf
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, convert_unix_ts_to_utc

# Protobuf message structures for the binary ZSYNCCUSTOMER and ZSYNCPAYMENT columns.
# Declaring the types explicitly keeps fields from being misinterpreted (ie: str as sub-message).
TYPEDEF_CUSTOMER = {
    "1": {"type": "message", "message_typedef": {
        "3": {"name": "name", "type": "str"},
        "5": {"name": "url", "type": "str"},
        "8": {"name": "cashtag", "type": "str"},
        "15": {"name": "extrainfo", "type": "str"},
    }},
}

TYPEDEF_PAYMENT = {
    "1": {"type": "message", "message_typedef": {
        "16": {"name": "extrainfo", "type": "str"},
    }},
}

QUERY = '''
SELECT
    ZPAYMENT.ZDISPLAYDATE,
    ZCUSTOMER.ZCUSTOMERTOKEN,
    ZCUSTOMER.ZSYNCCUSTOMER,
    ZPAYMENT.ZSYNCPAYMENT
FROM ZPAYMENT
INNER JOIN ZCUSTOMER
    ON ZCUSTOMER.ZCUSTOMERTOKEN = ZPAYMENT.ZREMOTECUSTOMERID
ORDER BY ZPAYMENT.ZDISPLAYDATE ASC
'''

# ISO 4217 currencies whose minor unit is not two decimal places.
ZERO_DECIMAL_CURRENCIES = {'BIF', 'CLP', 'DJF', 'GNF', 'ISK', 'JPY', 'KMF', 'KRW', 'PYG',
                           'RWF', 'UGX', 'UYI', 'VND', 'VUV', 'XAF', 'XOF', 'XPF'}
THREE_DECIMAL_CURRENCIES = {'BHD', 'IQD', 'JOD', 'KWD', 'LYD', 'OMR', 'TND'}


def _to_text(value):
    '''Normalize protobuf output, which may come back as bytes, to text.'''
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='ignore')
    return value


def _decode_blob(raw, typedef):
    '''Decode a sync blob and return its field 1 sub-message as a dict, or {} on failure.'''
    if not raw:
        return {}
    try:
        decoded, _ = blackboxprotobuf.decode_message(raw, typedef)
    except Exception:
        return {}
    inner = decoded.get('1')
    if isinstance(inner, list):
        inner = inner[0] if inner else None
    return inner if isinstance(inner, dict) else {}


def _load_json(value):
    '''Parse an embedded JSON payload, returning {} if it is absent or malformed.'''
    value = _to_text(value)
    if not value:
        return {}
    try:
        parsed = json.loads(value)
    except (ValueError, TypeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _scan_raw(raw, key):
    '''Recover a "key":"value" pair straight from a blob whose protobuf layout did not match.'''
    if not raw:
        return None
    if isinstance(raw, str):
        raw = raw.encode('utf-8', errors='ignore')
    match = re.search(b'"' + re.escape(key.encode()) + b'":"([^"]*)"', raw)
    return match.group(1).decode('utf-8', errors='ignore') if match else None


def _format_amount(minor_units, currency):
    '''Render a minor-unit amount using the currency's own exponent.'''
    if minor_units is None:
        return None
    try:
        minor_units = int(minor_units)
    except (ValueError, TypeError):
        return None
    if currency in ZERO_DECIMAL_CURRENCIES:
        exponent = 0
    elif currency in THREE_DECIMAL_CURRENCIES:
        exponent = 3
    else:
        exponent = 2
    value = minor_units / (10 ** exponent)
    return f'{value:,.{exponent}f} {currency}'.strip() if currency else f'{value:,.{exponent}f}'


def _timestamp(value):
    return convert_unix_ts_to_utc(value) if value is not None else None


@artifact_processor
def get_cashApp(context):
    data_list = []
    seen_files = set()
    seen_rows = set()

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('.sqlite'):
            continue
        # The artifact's path patterns overlap, so the same database can be handed
        # over more than once. Parse each one only a single time.
        if file_found in seen_files:
            continue
        seen_files.add(file_found)

        for row in get_sqlite_db_records(file_found, QUERY):
            display_date, customer_token, raw_customer, raw_payment = row[0], row[1], row[2], row[3]

            customer = _decode_blob(raw_customer, TYPEDEF_CUSTOMER)
            payment = _decode_blob(raw_payment, TYPEDEF_PAYMENT)

            payment_info = _load_json(payment.get('extrainfo'))
            customer_info = _load_json(customer.get('extrainfo'))

            amount = payment_info.get('amount') or {}
            # Amounts are expressed in the smallest denomination unit of that currency
            # (e.g. 100 = $1.00 USD); currency codes are ISO 4217 Alpha-3.
            minor_units = amount.get('amount')
            currency = amount.get('currency_code')

            instrument = payment_info.get('instrument') or {}

            # Fall back to a raw scan for older records whose blobs miss the JSON payload.
            role = payment_info.get('role') or _scan_raw(raw_payment, 'role')
            state = payment_info.get('state') or _scan_raw(raw_payment, 'state')

            record = (
                _timestamp(display_date if display_date is not None else payment_info.get('display_date')),
                customer_token,
                _to_text(customer.get('name')),
                _to_text(customer.get('cashtag')),
                customer_info.get('id'),
                customer_info.get('full_name'),
                role,
                _format_amount(minor_units, currency),
                minor_units,
                currency,
                payment_info.get('note'),
                customer_info.get('region'),
                customer_info.get('display_units'),
                _to_text(customer.get('url')),
                instrument.get('card_brand'),
                instrument.get('suffix'),
                instrument.get('display_name'),
                payment_info.get('display_instrument'),
                payment_info.get('instrument_type'),
                payment_info.get('transaction_id'),
                payment_info.get('token'),
                payment_info.get('receipt_token'),
                state,
                _timestamp(payment_info.get('created_at')),
                _timestamp(payment_info.get('captured_at')),
                _timestamp(payment_info.get('reached_customer_at')),
                _timestamp(payment_info.get('paid_out_at')),
                _timestamp(payment_info.get('deposited_at')),
                context.get_relative_path(file_found),
            )

            # Guard against duplicate rows from repeated joins or re-parsed copies.
            if record in seen_rows:
                continue
            seen_rows.add(record)
            data_list.append(record)

    data_headers = (('Transaction Date', 'datetime'), 'Customer Token', 'Name', 'Cashtag', 'ID', 'Full Name',
                    'Account Owner Role', 'Amount', 'Amount (Minor Units)', 'Currency', 'Note', 'Region',
                    'Units', 'URL', 'Card Brand', 'Suffix', 'Instrument Display Name', 'Display Instrument',
                    'Instrument Type', 'Transaction ID', 'Token', 'Receipt', 'Transaction State',
                    ('Created At', 'datetime'), ('Captured At', 'datetime'), ('Reached Customer At', 'datetime'),
                    ('Paid Out At', 'datetime'), ('Deposited At', 'datetime'), 'Source File')

    return data_headers, data_list, 'see Source File for more info'