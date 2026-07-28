__artifacts_v2__ = {
    "metamaskWallets": {
        "name": "MetaMask - Wallets",
        "description": "MetaMask wallet accounts (import time, name, address, balance)",
        "author": "", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "Metamask", "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/persistStore/persist-root',),
        "output_types": "standard", "artifact_icon": "credit-card"
    },
    "metamaskContacts": {
        "name": "MetaMask - Contacts",
        "description": "MetaMask address book contacts",
        "author": "", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "Metamask", "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/persistStore/persist-root',),
        "output_types": "standard", "artifact_icon": "users"
    },
    "metamaskTransactions": {
        "name": "MetaMask - Transactions",
        "description": "MetaMask transactions (time, from/to address, value, hash)",
        "author": "", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "Metamask", "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/persistStore/persist-root',),
        "output_types": "standard", "artifact_icon": "repeat"
    },
    "metamaskBrowser": {
        "name": "MetaMask - Browser",
        "description": "MetaMask in-app browser history",
        "author": "", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "Metamask", "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/persistStore/persist-root',),
        "output_types": "standard", "artifact_icon": "globe"
    }
}

import json

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc

_WEI = 10 ** 18


def _load_metamask(context):
    """Return (backgroundState, browserState, source_path) from the MetaMask persist-root, or ({}, {}, '')."""
    for file_found in context.get_files_found():
        file_found = str(file_found)
        try:
            with open(file_found, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            continue
        if 'engine' in data:
            background = json.loads(data['engine']).get('backgroundState', {})
            browser = json.loads(data['browser']) if 'browser' in data else {}
            return background, browser, context.get_relative_path(file_found)
    return {}, {}, ''


def _hex_to_eth(hex_value):
    try:
        return int(str(hex_value), 16) / _WEI
    except (ValueError, TypeError):
        return hex_value


@artifact_processor
def metamaskWallets(context):
    data_headers = (('Import Timestamp', 'datetime'), 'Wallet Name', 'Wallet Address',
                    'Balance (In Network Currency)')
    data_list = []
    background, _, source = _load_metamask(context)
    accounts = background.get('AccountTrackerController', {}).get('accounts', {})
    identities = background.get('PreferencesController', {}).get('identities', {})
    for address in accounts:
        ident = identities.get(address, {})
        data_list.append((convert_unix_ts_to_utc(ident.get('importTime')),
                          str(ident.get('name', '')), address,
                          _hex_to_eth(accounts[address].get('balance', '0x0'))))
    return data_headers, data_list, source


@artifact_processor
def metamaskContacts(context):
    data_headers = ('Contact Name', 'Wallet Address')
    data_list = []
    background, _, source = _load_metamask(context)
    address_book = background.get('AddressBookController', {}).get('addressBook', {})
    for chain_id in address_book:
        for contact in address_book[chain_id].values():
            data_list.append((str(contact.get('name', '')), str(contact.get('address', ''))))
    return data_headers, data_list, source


@artifact_processor
def metamaskTransactions(context):
    data_headers = (('Timestamp', 'datetime'), 'From Address', 'To Address', 'Value',
                    'Transaction Hash')
    data_list = []
    background, _, source = _load_metamask(context)
    for entry in background.get('TransactionController', {}).get('transactions', []):
        tx = entry.get('transaction', {})
        data_list.append((convert_unix_ts_to_utc(entry.get('time')), str(tx.get('from', '')),
                          str(tx.get('to', '')), _hex_to_eth(tx.get('value', '0x0')),
                          entry.get('transactionHash')))
    return data_headers, data_list, source


@artifact_processor
def metamaskBrowser(context):
    data_headers = ('Name', 'URL')
    data_list = []
    _, browser, source = _load_metamask(context)
    for history in browser.get('history', []):
        data_list.append((str(history.get('name', '')), str(history.get('url', ''))))
    return data_headers, data_list, source
