__artifacts_v2__ = {
    "get_cashApp": {
        "name": "Cash App",
        "description": "Parses Cash App customer and payment records from the CCEntitySync SQLite stores, "
                       "decoding the ZSYNCCUSTOMER and ZSYNCPAYMENT protobuf blobs and the JSON payloads "
                       "they carry.",
        "author": "@gforce4n6, @AlexisBrignoni, @charpy4n6, Claude",
        "creation_date": "2021-10-06",
        "last_update_date": "2026-08-25",
        "requirements": "none",
        "category": "Banking",
        "notes": "Merged from the original Cash App and Cash App (B) artifacts, which cashAppB.py provided "
                 "until this change removed it. Rows come from ZPAYMENT joined to ZCUSTOMER on the "
                 "customer token, so a customer record carrying no payment is not reported: the two tested "
                 "stores held 65 and 21 customer records behind one payment each. Amounts are stored in "
                 "the smallest denomination unit of the currency (e.g. 100 = $1.00 USD); both the stored "
                 "value and a formatted value are reported. In the customer blob, protobuf field 3 held "
                 "the display name, field 5 the avatar URL and field 8 the cashtag; field 8 was checked "
                 "against one customer record whose own JSON payload carries the same cashtag string. "
                 "Account Owner Role and Transaction State are read from the payment JSON payload, and the "
                 "raw scan is used only where that payload is absent, which neither tested image "
                 "exercised. On both tested images the single payment is a referral bonus still pending, "
                 "and its payload carries no state key, no instrument object and no capture, payout or "
                 "deposit timestamp, so Transaction State, Card Brand, Suffix, Instrument Display Name, "
                 "Display Instrument, Instrument Type, Transaction ID, Receipt, Captured At, Reached "
                 "Customer At, Paid Out At and Deposited At were empty on both reported rows; Cashtag was "
                 "empty because the joined customer record on both images carries no cashtag field. Those "
                 "columns are code-present and unexercised here, and a sample holding a settled card "
                 "payment would close that gap. Customer Token and ID, and Name and Full Name, are read "
                 "from separate sources (a table column and a protobuf field against the JSON payload) and "
                 "agreed on each tested row. Customer Bitcoin Display Units is the customer's own bitcoin "
                 "unit preference and not the unit of the payment amount. Reference: Square Developer "
                 "Documentation, 'Working with Monetary Amounts', "
                 "https://developer.squareup.com/docs/build-basics/working-with-monetary-amounts",
        # fnmatch's * crosses path separators, so the two AppGroup patterns cover both observed
        # layouts: the store sits directly under the container on one tested image and under
        # Environments/Production/Accounts/<token>/ on the other. The third pattern is not
        # anchored to the app group container, so an extraction rooted below it still matches.
        # The patterns overlap by design and the module parses each database once.
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/CCEntitySync-internal.cashappapi.com.sqlite*',
                  '*/mobile/Containers/Shared/AppGroup/*/CCEntitySync-api.squareup.com.sqlite*',
                  '*/Environments/Production/Accounts/*/CCEntitySync-*.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "currency-dollar",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | Cash App 5.46.0 | 1 row",
            "abe_ios16": "iOS 16.5 | Cash App 4.0 | 1 row",
        },
    }
}

import json
import re

from google.protobuf.message import DecodeError

from scripts import blackboxprotobuf
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, convert_unix_ts_to_utc

# What blackboxprotobuf.decode_message raises on a blob that does not match the
# expected layout: a malformed protobuf, or a length/field mismatch it surfaces as
# one of the plain built-ins below.
_DECODE_ERRORS = (DecodeError, ValueError, TypeError, KeyError, IndexError)

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
    except _DECODE_ERRORS:
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
    '''Recover a "key":"value" pair straight from a blob that carries no JSON payload.

    The search is not anchored to any object, so it must not be used on a blob whose
    payload parsed: ZSYNCPAYMENT nests a "state" inside pending_referral_render_data
    that belongs to a referral bonus rather than to the payment, and a whole-blob scan
    cannot tell the two apart.
    '''
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
        # The artifact's path patterns overlap by design, so the same database can be
        # handed over more than once. Parse each one only a single time.
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

            # Read role and state from the payment's JSON payload. The raw scan is a
            # fallback for a blob that carries no payload at all; running it against a
            # blob that parsed would report a nested object's value under a payment
            # column. See _scan_raw.
            if payment_info:
                role = payment_info.get('role')
                state = payment_info.get('state')
            else:
                role = _scan_raw(raw_payment, 'role')
                state = _scan_raw(raw_payment, 'state')

            record = (
                _timestamp(display_date if display_date is not None else payment_info.get('display_date')),
                _timestamp(payment_info.get('created_at')),
                _timestamp(payment_info.get('captured_at')),
                _timestamp(payment_info.get('reached_customer_at')),
                _timestamp(payment_info.get('paid_out_at')),
                _timestamp(payment_info.get('deposited_at')),
                customer_token,
                customer_info.get('id'),
                _to_text(customer.get('name')),
                customer_info.get('full_name'),
                _to_text(customer.get('cashtag')),
                role,
                state,
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
                context.get_relative_path(file_found),
            )

            # Guard against duplicate rows from re-parsed copies of the same database.
            if record in seen_rows:
                continue
            seen_rows.add(record)
            data_list.append(record)

    data_headers = (('Transaction Date', 'datetime'), ('Created At', 'datetime'),
                    ('Captured At', 'datetime'), ('Reached Customer At', 'datetime'),
                    ('Paid Out At', 'datetime'), ('Deposited At', 'datetime'),
                    'Customer Token', 'ID', 'Name', 'Full Name', 'Cashtag',
                    'Account Owner Role', 'Transaction State', 'Amount', 'Amount (Minor Units)',
                    'Currency', 'Note', 'Region', 'Customer Bitcoin Display Units', 'URL',
                    'Card Brand', 'Suffix', 'Instrument Display Name', 'Display Instrument',
                    'Instrument Type', 'Transaction ID', 'Token', 'Receipt', 'Source File')

    return data_headers, data_list, '\n'.join(sorted(seen_files))
