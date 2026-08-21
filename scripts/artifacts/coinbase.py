__artifacts_v2__ = {
    "coinbase_wallets": {
        "name": "Coinbase - Wallets and Balances",
        "description": "Parses the Coinbase iOS wallet accounts and their balances from the "
                       "app's offline GraphQL cache.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Coinbase",
        "notes": "One row per wallet the account holds. Coinbase is a React Native app and "
                 "keeps its state in an MMKV store, read here with the reader in "
                 "scripts/mmkv_parser.py. Inside that store the @GraphqlOfflineCache.store "
                 "value is a normalised Apollo cache: an account record links to its "
                 "balances by reference, and each reference resolves to an amount record "
                 "carrying a value and a currency. This artifact reports only the accounts "
                 "whose balance reference resolves to such an amount, because the same cache "
                 "holds hundreds of account records for currencies the user does not hold, "
                 "which are the app's currency catalogue rather than the account's wallets; "
                 "on the tested device 5 of 429 account records resolved to a balance. Total "
                 "Balance and Available Balance are in the wallet's own currency and Native "
                 "Balance is the same total in the account's display currency. Every balance "
                 "was zero on the tested device, which records that the wallets existed and "
                 "were empty rather than that the values could not be read. On the tested "
                 "device every wallet was a primary account of type WALLET and none was marked "
                 "sanctioned, so those three columns did not distinguish one wallet from another "
                 "there. The account "
                 "identifier is stored base64 encoded and is decoded here. Field mapping was "
                 "done against a private sample provided by Mattia; no sample data is "
                 "recorded for it.",
        "paths": ('*/Documents/mmkv/CB_RRN_MMKV_STORAGE',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "credit-card"
    },
    "coinbase_account": {
        "name": "Coinbase - Account and Device",
        "description": "Parses the Coinbase iOS account identifiers, login state and app "
                       "settings from the app's MMKV store.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Coinbase",
        "notes": "One row per app data directory. The values are top level keys of the "
                 "app's MMKV store. Wallet Link User ID is the identifier the app records "
                 "for the account. Logged In is the flag the app keeps for whether it "
                 "expects to be signed in, reported as stored. Push Token is the notification "
                 "token registered for the device. App Version is the version the store "
                 "recorded. The number of wallets is counted from the same GraphQL cache the "
                 "wallets artifact reads, so the two agree by construction. Field mapping was "
                 "done against a private sample provided by Mattia; no sample data is "
                 "recorded for it.",
        "paths": ('*/Documents/mmkv/CB_RRN_MMKV_STORAGE',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user"
    },
}

import base64
import json
import os

from scripts.mmkv_parser import read_dict
from scripts.ilapfuncs import artifact_processor, logfunc

_STORE = 'CB_RRN_MMKV_STORAGE'
_CACHE_KEY = '@GraphqlOfflineCache.store'


def _stores(files_found):
    '''Every copy of the app's MMKV store among the matched files.'''
    seen = []
    for found in files_found:
        path = str(found)
        if os.path.basename(path) == _STORE and path not in seen:
            seen.append(path)
    return seen


def _read(path):
    '''(top level dict, Apollo record map) for one MMKV store, or (None, None).'''
    try:
        top = read_dict(path)
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'Coinbase: could not read the MMKV store: {error}')
        return None, None
    records = {}
    cache = top.get(_CACHE_KEY)
    if cache:
        try:
            records = json.loads(cache).get('recordMap', {})
        except (TypeError, ValueError) as error:
            logfunc(f'Coinbase: could not parse the offline GraphQL cache: {error}')
    return top, records


def _deref(records, value):
    '''The record a single Apollo reference points at, or the value unchanged.'''
    if isinstance(value, dict) and '__ref' in value:
        return records.get(value['__ref'])
    return value


def _amount(records, value):
    '''(value, currency) for a referenced amount record, or ('', '').'''
    record = _deref(records, value)
    if isinstance(record, dict) and 'value' in record:
        return _text(record.get('value')), _text(record.get('currency'))
    return '', ''


def _text(value):
    '''A stored value as text, with a stored null read as absent.'''
    return '' if value is None else str(value)


def _string(top, key):
    '''A top level MMKV value with any surrounding JSON quotes removed.'''
    value = top.get(key)
    if isinstance(value, str) and len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1]
    return _text(value)


def _decode_id(identifier):
    '''A base64 account identifier decoded to text, or the value unchanged.'''
    try:
        return base64.b64decode(identifier + '==').decode('utf-8')
    except (ValueError, UnicodeDecodeError):
        return identifier


def _wallets(records):
    '''The account records whose balance resolves to an amount.

    The cache holds an account record for every currency the app can display, so a record
    is a wallet the account actually holds only when its balance reference resolves to an
    amount. That is what separates the account's wallets from the currency catalogue.
    '''
    wallets = []
    for record in records.values():
        if not (isinstance(record, dict) and record.get('__typename') == 'Account'):
            continue
        total = _deref(records, record.get('totalBalance'))
        if isinstance(total, dict) and total.get('value') is not None:
            wallets.append(record)
    return wallets


@artifact_processor
def coinbase_wallets(context):
    data_list = []
    source_files = []

    for path in _stores(context.get_files_found()):
        _, records = _read(path)
        if not records:
            continue
        relative = context.get_relative_path(path)
        for account in _wallets(records):
            total_value, total_currency = _amount(records, account.get('totalBalance'))
            available_value, available_currency = _amount(records, account.get('availableBalance'))
            native_value, native_currency = _amount(
                records, account.get('totalBalanceInNativeCurrency'))
            source_files.append(relative)
            data_list.append((
                _decode_id(_text(account.get('id'))),
                _text(account.get('uuid')),
                _text(account.get('type')),
                _text(account.get('primary')),
                total_value,
                total_currency,
                available_value,
                available_currency,
                native_value,
                native_currency,
                _text(account.get('isSanctioned')),
                _text(account.get('platform')),
                relative,
            ))

    data_headers = (
        'Account',
        'Currency',
        'Type (as stored)',
        'Primary',
        'Total Balance',
        'Total Balance Currency',
        'Available Balance',
        'Available Balance Currency',
        'Native Balance',
        'Native Balance Currency',
        'Sanctioned (as stored)',
        'Platform (as stored)',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def coinbase_account(context):
    data_list = []
    source_files = []

    for path in _stores(context.get_files_found()):
        top, records = _read(path)
        if top is None:
            continue
        relative = context.get_relative_path(path)

        push_token = ''
        token_cache = top.get('@NotificationRegistrar.PushTokenCache')
        if token_cache:
            try:
                push_token = json.loads(token_cache).get('token', '')
            except (TypeError, ValueError):
                push_token = ''

        source_files.append(relative)
        data_list.append((
            _string(top, '@walletlink.user_id'),
            _text(top.get('@OAUTH.IS_EXPECTED_TO_BE_LOGGED_IN')),
            _string(top, '@UserVersion.version'),
            _string(top, '@notifications.push_permissions_set_status'),
            push_token,
            len(_wallets(records)),
            _string(top, '@cds_preferences.appearance'),
            relative,
        ))

    data_headers = (
        'Wallet Link User ID',
        'Logged In (as stored)',
        'App Version',
        'Push Permission (as stored)',
        'Push Token',
        'Wallets Held',
        'Appearance (as stored)',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))
