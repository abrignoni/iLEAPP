__artifacts_v2__ = {
    "coinbase_wallet_account": {
        "name": "Coinbase Wallet - Account",
        "description": "The self-custody account the Coinbase Wallet app holds, with the time it "
                       "was created and its primary address.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Coinbase Wallet",
        "notes": "One row per row of the account table in Documents/default/wallet-rn-v2.sqlite, "
                 "joined to the wallet_group row that names the same account. This is the "
                 "Coinbase Wallet app, bundle id org.toshi.distribution, which is a separate app "
                 "from the Coinbase exchange app that coinbase.py reads; the two keep different "
                 "stores and neither artifact reads the other's. Created is the timestamp the "
                 "account row stores. Account Type is reported as stored and held the value "
                 "mnemonic on both tested images, which is the app's own word and is not read "
                 "here as a statement about how any key was generated. The stored timestamps "
                 "carry no zone marker and are read as UTC on the evidence of the app's own "
                 "writing: the MMKV store beside this database holds a migration timestamp "
                 "written with an explicit Z marker, and on the two tested images it sits 11 and "
                 "108 seconds before the account row, on the same date and hour, which a "
                 "local-zone reading would place hours apart. Device ID and Active Wallet Group "
                 "are read from that same MMKV store, Documents/mmkv/CBStore.plaintext. That "
                 "store also holds a session access token and an authentication state blob; "
                 "neither is reported here, and an examiner who needs them can read the file "
                 "this artifact names. Account Nickname, Wallet Group Nickname and Hardware "
                 "Derivation Path held no value on either tested image; the conditions under "
                 "which the app fills them are not established here. MPC Conversion State, "
                 "Deleted and Completed Backup Flow are columns "
                 "the older of the two stores does not declare at all, so they are read as "
                 "NULL there and carry values only on the newer one.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/default/wallet-rn-v2.sqlite*',
                  '*/mobile/Containers/Data/Application/*/Documents/mmkv/CBStore.plaintext'),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "user",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Coinbase Wallet | 1 row",
            "otto_ios17": "iOS 17.5.1 | Coinbase Wallet | 1 row",
        },
    },
    "coinbase_wallet_addresses": {
        "name": "Coinbase Wallet - Addresses",
        "description": "The blockchain addresses Coinbase Wallet derived for the account, with "
                       "the derivation path and use flag of each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Coinbase Wallet",
        "notes": "One row per row of the address table. The derivation index ran from 0 to 19 on "
                 "both tested images and the paths follow the BIP-44 shape. The presence of an "
                 "address is not evidence that it was ever used or funded. Balance is a string "
                 "in the asset's own base unit and is mostly zero: a value other than zero "
                 "appeared on one row of one tested image and on none of the other. Is Used is "
                 "the app's own flag, reported as stored, and was true on 203 of 491 rows on one "
                 "image and 200 of 406 on the other. Contract Address held no value on any row "
                 "of either image, since every derived address there belongs to a chain's native "
                 "asset rather than to a token. The rows name addresses the app derived for this "
                 "device's account, which "
                 "an examiner can search against a public blockchain. Is Change Address, Address "
                 "Type, Blockchain, Currency Code and Network are reported as stored; the type "
                 "values name address formats such as BitcoinSegWit and BitcoinLegacy and are the "
                 "app's own labels. The same address can appear more than once where the app "
                 "derived it under more than one asset, so the row count is higher than the count "
                 "of distinct addresses: 491 rows against 270 distinct on one image and 406 "
                 "against 226 on the other. "
                 "Account ID held one value on every row of both tested images, which is what "
                 "a device holding a single account looks like; it is kept because the column "
                 "is what ties a row to the account the Account artifact reports.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/default/wallet-rn-v2.sqlite*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "hash",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Coinbase Wallet | 491 rows",
            "otto_ios17": "iOS 17.5.1 | Coinbase Wallet | 406 rows",
        },
    },
    "coinbase_wallet_assets": {
        "name": "Coinbase Wallet - Assets",
        "description": "The per asset wallet rows Coinbase Wallet holds, with the balance recorded "
                       "against each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Coinbase Wallet",
        "notes": "One row per row of the wallet table, which the app keeps per asset rather than "
                 "per holding: 207 and 203 rows on the two tested images against 26 and 23 "
                 "distinct primary addresses. Balance held a value other than zero on exactly one "
                 "row of each image, and a row is not evidence that the asset was ever held. "
                 "Balance, Decimals and Minimum Balance are reported as stored, because the "
                 "store carries the amounts as strings in each asset's own base unit and no unit "
                 "conversion is applied here. Contract Address is set for tokens and blank for a "
                 "chain's native asset. A separate table, curated_asset_setting, held 9,979 rows "
                 "on one image and none on the other; it is not reported and what its rows "
                 "represent is not established here. "
                 "Minimum Balance, Asset UUID, Is Spam and Is Whitelist held no value on "
                 "either tested image, and the last two are columns the older store does not "
                 "declare. Last Balance Update Transaction Hash was set on one row of the "
                 "newer image and on none of the older one. Image URL is the address of the "
                 "asset icon the app shows and is set on every row; it is reported as stored "
                 "and is not fetched. "
                 "Account ID held one value on every row of both tested images, for the same "
                 "reason.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/default/wallet-rn-v2.sqlite*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "credit-card",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Coinbase Wallet | 207 rows",
            "otto_ios17": "iOS 17.5.1 | Coinbase Wallet | 203 rows",
        },
    },
    "coinbase_wallet_transactions": {
        "name": "Coinbase Wallet - Transactions",
        "description": "Transactions Coinbase Wallet recorded, with the addresses, amount and "
                       "transaction hash of each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Coinbase Wallet",
        "notes": "One row per row of tx_history_v2 and of the older tx_history table, told apart "
                 "by the Source Table column; tx_history is present only on the older of the two "
                 "tested stores and held no rows there. Transaction Hash is a value an examiner "
                 "can look up on a public blockchain. From Address and To Address are the "
                 "parties the row records, and the From Domain and To Domain columns carry the "
                 "app's resolved name for either where it has one. Direction is read from the "
                 "isSent flag the row stores. Amount, Fee and the gas columns are reported as "
                 "stored, in each asset's own base unit, with no conversion applied. State and "
                 "Type are reported as stored; both tested rows held state 3 and type RECEIVE. "
                 "Transfers holds the row's own JSON list as stored. One transaction was "
                 "recorded on each tested image, so this artifact is proven on a single row per "
                 "store rather than on a busy account. Contract Address, Gas Limit, Max Fee Per "
                 "Gas, Max Priority Fee Per Gas, Base Fee Per Gas, Submission Type, From Domain "
                 "and To Domain each held no value on the single row of either image. That is "
                 "one observation per store rather than a property of the table: the one "
                 "transaction on each is a receive, and no sent transaction was present on "
                 "either image.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/default/wallet-rn-v2.sqlite*',),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "repeat",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Coinbase Wallet | 1 row",
            "otto_ios17": "iOS 17.5.1 | Coinbase Wallet | 1 row",
        },
    },
    "coinbase_wallet_xpubs": {
        "name": "Coinbase Wallet - Extended Public Keys",
        "description": "The extended public keys Coinbase Wallet stored for the account, one per "
                       "chain and address type.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Coinbase Wallet",
        "notes": "One row per BIP44XpubKey entry in the app's MMKV store at "
                 "Documents/mmkv/CBStore.plaintext, read with the reader vendored at "
                 "scripts/mmkv_parser.py. Under BIP-32 an extended public key allows derivation "
                 "of its non-hardened descendant public keys and removes the ability to sign "
                 "transactions (Reference: bitcoin/bips, bip-0032.mediawiki at commit "
                 "c0644a054fd1568ecbfc9c2b656ad5200b16ff74), so these rows reach further than "
                 "the Addresses artifact, which lists only the run of addresses the app had "
                 "already derived. Nothing here recovers or reports key material that would "
                 "permit spending. The store held 11 of these on one tested image and 8 on the "
                 "other. "
                 "The MMKV key itself carries the currency, the address type and the account's "
                 "primary address, and those are split into their own columns; the primary "
                 "address in the key is upper cased by the app and is reported as stored rather "
                 "than normalised, so it may differ in case from the same address elsewhere in "
                 "this module. "
                 "Account Primary Address held one value on each tested image, which is what a "
                 "device with a single account looks like.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/mmkv/CBStore.plaintext',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "key",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Coinbase Wallet | 11 rows",
            "otto_ios17": "iOS 17.5.1 | Coinbase Wallet | 8 rows",
        },
    },
    "coinbase_wallet_signed_transactions": {
        "name": "Coinbase Wallet - Signed Transactions",
        "description": "Rows from the Coinbase Wallet per chain signed transaction tables, empty "
                       "on both tested images.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Coinbase Wallet",
        "notes": "One row per row of ethereum_signed_tx, solana_signed_tx, utxo_signed_tx, "
                 "xlm_signed_tx and xrp_signed_tx, told apart by the Source Table column. What a "
                 "row in these tables records beyond what the table names say is not "
                 "established, and the Transactions artifact reads different tables. "
                 "All five were empty on both tested images, so this reader is code present and "
                 "was not exercised, and the columns it reports are the ones the tables declare "
                 "rather than ones observed carrying values. The columns each table does not "
                 "declare are read as NULL, because the five schemas differ: only the Ethereum "
                 "table carries a nonce and a wei value, only Solana carries a recent block hash, "
                 "and the UTXO table names neither party.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/default/wallet-rn-v2.sqlite*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "edit-3",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Coinbase Wallet | 0 rows",
            "otto_ios17": "iOS 17.5.1 | Coinbase Wallet | 0 rows",
        },
    },
}

import json
import os
from datetime import datetime, timezone

from scripts.ilapfuncs import (artifact_processor, does_table_exist_in_db, get_sqlite_db_records,
                               logfunc, null_absent_columns)
from scripts.mmkv_parser import MMKVError, read_dict

_STORE_NAME = 'wallet-rn-v2.sqlite'
_MMKV_NAME = 'CBStore.plaintext'
_XPUB_MARKER = 'BIP44XpubKey_'


def _stores(files_found, name):
    '''Every file with the given base name among the matches, directories skipped.'''
    seen = []
    for found in files_found:
        path = str(found)
        if os.path.isdir(path):
            continue
        if os.path.basename(path) == name and path not in seen:
            seen.append(path)
    return seen


def _rows(path, table, columns):
    '''Rows of a table, or nothing when the store does not have it.

    Columns the store lacks are read as NULL, because the app adds columns between
    releases and the five signed-transaction tables do not share a schema.
    '''
    if not does_table_exist_in_db(path, table):
        return []
    statement = null_absent_columns(path, f'SELECT {columns} FROM {table}')
    try:
        return list(get_sqlite_db_records(path, statement))
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'Coinbase Wallet: could not read {table}: {error}')
        return []


def _text(value):
    '''A stored value as text, with a stored null read as absent.'''
    return '' if value is None else str(value)


def _stored_datetime(value):
    '''A stored 'YYYY-MM-DD HH:MM:SS[.fff]' string as an aware UTC datetime, or the text.'''
    if value in (None, ''):
        return ''
    text = str(value).strip()
    for shape in ('%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.strptime(text, shape).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return text


def _mmkv(path):
    '''The live entries of the app's MMKV store, or {} when it cannot be read.'''
    try:
        return read_dict(path)
    except (MMKVError, OSError, ValueError) as error:
        logfunc(f'Coinbase Wallet: could not read {os.path.basename(path)}: {error}')
        return {}


def _mmkv_value(entries, wanted):
    '''The value of the first key whose tail matches, unquoted, or ''.'''
    for key, value in entries.items():
        if key.split(':', 1)[-1] == wanted:
            return _unquote(value)
    return ''


def _unquote(value):
    '''An MMKV value that holds a JSON string, as plain text.'''
    text = _text(value)
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        try:
            decoded = json.loads(text)
        except ValueError:
            return text[1:-1]
        if isinstance(decoded, str):
            return decoded
    return text


@artifact_processor
def coinbase_wallet_account(context):
    data_list = []
    files_found = context.get_files_found()
    sources = _stores(files_found, _STORE_NAME)
    mmkv_files = _stores(files_found, _MMKV_NAME)
    entries = {}
    for mmkv_path in mmkv_files:
        entries.update(_mmkv(mmkv_path))
    device_id = _mmkv_value(entries, 'deviceId')
    active_group = _mmkv_value(entries, 'activeWalletGroupId')

    for source_path in sources:
        groups = {}
        for (group_id, account_id, created, nickname, index, hidden,
             derivation) in _rows(
                source_path, 'wallet_group',
                'id, accountId, createdAt, nickname, walletIndex, isHidden, '
                'hardwareDerivationPath'):
            groups[account_id] = (group_id, created, nickname, index, hidden, derivation)
        for (account_id, created, kind, chain, address, nickname, conversion,
             deleted, backed_up) in _rows(
                source_path, 'account',
                'id, createdAt, type, primaryAddressChain, primaryAddress, nickname, '
                'mpcConversionState, isDeleted, hasCompletedBackupFlow'):
            group = groups.get(account_id, ('', '', '', '', '', ''))
            data_list.append((
                _stored_datetime(created), _text(address), _text(chain), _text(kind),
                _text(nickname), _text(conversion), _text(deleted), _text(backed_up),
                _stored_datetime(group[1]), _text(group[2]), _text(group[3]),
                _text(group[4]), _text(group[5]), device_id, active_group,
                _text(group[0]), _text(account_id),
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)

    data_headers = (
        ('Created', 'datetime'), 'Primary Address', 'Primary Address Chain (as stored)',
        'Account Type (as stored)', 'Account Nickname', 'MPC Conversion State (as stored)',
        'Deleted (as stored)', 'Completed Backup Flow (as stored)',
        ('Wallet Group Created', 'datetime'), 'Wallet Group Nickname',
        'Wallet Index (as stored)', 'Wallet Group Hidden (as stored)',
        'Hardware Derivation Path', 'Device ID', 'Active Wallet Group', 'Wallet Group ID',
        'Account ID',
    )
    return data_headers, data_list, '\n'.join(sources + mmkv_files)


@artifact_processor
def coinbase_wallet_addresses(context):
    data_list = []
    sources = _stores(context.get_files_found(), _STORE_NAME)

    for source_path in sources:
        for (row_id, address, index, currency, network, kind, blockchain, derivation,
             is_used, is_change, balance, contract, account_id) in _rows(
                source_path, 'address',
                'id, address, indexStr, currencyCodeStr, networkStr, typeStr, blockchainStr, '
                'derivationPath, isUsedStr, isChangeAddressStr, balanceStr, contractAddress, '
                'accountId'):
            data_list.append((
                _text(address), _text(blockchain), _text(currency), _text(kind),
                _text(derivation), _text(index), _text(is_used), _text(is_change),
                _text(balance), _text(network), _text(contract), _text(account_id),
                _text(row_id),
            ))

    data_list.sort(key=lambda row: (str(row[1]), str(row[4])))

    data_headers = (
        'Address', 'Blockchain (as stored)', 'Currency Code (as stored)',
        'Address Type (as stored)', 'Derivation Path', 'Derivation Index (as stored)',
        'Is Used (as stored)', 'Is Change Address (as stored)', 'Balance (as stored)',
        'Network (as stored)', 'Contract Address', 'Account ID', 'Row ID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def coinbase_wallet_assets(context):
    data_list = []
    sources = _stores(context.get_files_found(), _STORE_NAME)

    for source_path in sources:
        for (row_id, name, currency, blockchain, network, balance, decimals, minimum,
             primary, contract, image, account_id, asset_uuid, last_hash, spam,
             whitelist) in _rows(
                source_path, 'wallet',
                'id, displayName, currencyCodeStr, blockchainStr, networkStr, balanceStr, '
                'decimalsStr, minimumBalanceStr, primaryAddress, contractAddress, imageURLStr, '
                'accountId, assetUUID, lastBalanceUpdateTxHash, isSpam, isWhitelist'):
            data_list.append((
                _text(name), _text(currency), _text(blockchain), _text(network),
                _text(balance), _text(decimals), _text(minimum), _text(primary),
                _text(contract), _text(last_hash), _text(spam), _text(whitelist),
                _text(image), _text(asset_uuid), _text(account_id), _text(row_id),
            ))

    data_list.sort(key=lambda row: (str(row[2]), str(row[1])))

    data_headers = (
        'Display Name', 'Currency Code (as stored)', 'Blockchain (as stored)',
        'Network (as stored)', 'Balance (as stored)', 'Decimals (as stored)',
        'Minimum Balance (as stored)', 'Primary Address', 'Contract Address',
        'Last Balance Update Transaction Hash', 'Is Spam (as stored)',
        'Is Whitelist (as stored)', 'Image URL', 'Asset UUID', 'Account ID', 'Row ID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def coinbase_wallet_transactions(context):
    data_list = []
    sources = _stores(context.get_files_found(), _STORE_NAME)

    for source_path in sources:
        for table in ('tx_history_v2', 'tx_history'):
            for (row_id, created, confirmed, kind, state, is_sent, from_address, from_domain,
                 to_address, to_domain, amount, fee, token, decimals, currency, fee_currency,
                 blockchain, network, tx_hash, contract, nonce, gas_limit, max_fee,
                 max_priority, base_fee, submission, transfers, metadata,
                 wallet_id) in _rows(
                    source_path, table,
                    'id, createdAt, confirmedAt, type, state, isSent, fromAddress, fromDomain, '
                    'toAddress, toDomain, amount, fee, tokenName, tokenDecimal, '
                    'currencyCodeStr, feeCurrencyCodeStr, blockchainStr, networkStr, txHash, '
                    'contractAddress, nonce, gasLimit, maxFeePerGas, maxPriorityFeePerGas, '
                    'baseFeePerGas, txSubmissionType, transfersStr, metadataStrArray, walletId'):
                direction = ''
                if is_sent is not None:
                    direction = 'Sent' if str(is_sent) in ('1', 'True', 'true') else 'Received'
                data_list.append((
                    _stored_datetime(created), _stored_datetime(confirmed), _text(kind),
                    direction, _text(from_address), _text(from_domain), _text(to_address),
                    _text(to_domain), _text(amount), _text(token), _text(currency),
                    _text(decimals), _text(fee), _text(fee_currency), _text(tx_hash),
                    _text(blockchain), _text(network), _text(state), _text(contract),
                    _text(nonce), _text(gas_limit), _text(max_fee), _text(max_priority),
                    _text(base_fee), _text(submission), _text(transfers), _text(metadata),
                    _text(wallet_id), table, _text(row_id),
                ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)

    data_headers = (
        ('Created', 'datetime'), ('Confirmed', 'datetime'), 'Type (as stored)', 'Direction',
        'From Address', 'From Domain', 'To Address', 'To Domain', 'Amount (as stored)',
        'Token Name', 'Currency Code (as stored)', 'Token Decimals (as stored)',
        'Fee (as stored)', 'Fee Currency (as stored)', 'Transaction Hash',
        'Blockchain (as stored)', 'Network (as stored)', 'State (as stored)',
        'Contract Address', 'Nonce (as stored)', 'Gas Limit (as stored)',
        'Max Fee Per Gas (as stored)', 'Max Priority Fee Per Gas (as stored)',
        'Base Fee Per Gas (as stored)', 'Submission Type (as stored)', 'Transfers (as stored)',
        'Metadata (as stored)', 'Wallet ID', 'Source Table', 'Row ID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def coinbase_wallet_xpubs(context):
    data_list = []
    sources = _stores(context.get_files_found(), _MMKV_NAME)

    for source_path in sources:
        for key, value in _mmkv(source_path).items():
            if _XPUB_MARKER not in key:
                continue
            tail = key.split(_XPUB_MARKER, 1)[1]
            parts = tail.split(',')
            currency = parts[0] if parts else ''
            address_type = parts[2] if len(parts) > 2 else ''
            remainder = parts[3] if len(parts) > 3 else ''
            primary = remainder.rsplit('/', 1)[-1] if remainder else ''
            data_list.append((
                _unquote(value), currency, address_type, primary, key,
            ))

    data_list.sort(key=lambda row: (str(row[1]), str(row[2])))

    data_headers = (
        'Extended Public Key', 'Currency Code (as stored)', 'Address Type (as stored)',
        'Account Primary Address (as stored)', 'Store Key',
    )
    return data_headers, data_list, '\n'.join(sources)


_SIGNED_TABLES = (
    ('ethereum_signed_tx', 'ETH'),
    ('solana_signed_tx', 'SOL'),
    ('utxo_signed_tx', 'UTXO'),
    ('xlm_signed_tx', 'XLM'),
    ('xrp_signed_tx', 'XRP'),
)


@artifact_processor
def coinbase_wallet_signed_transactions(context):
    data_list = []
    sources = _stores(context.get_files_found(), _STORE_NAME)

    for source_path in sources:
        for table, _family in _SIGNED_TABLES:
            for (row_id, from_address, to_address, tx_hash, state, blockchain, currency,
                 network, nonce, chain_id, wei_value, erc20_value, transfer_value,
                 recent_block, valid_before, max_ledger, not_found, signed_data,
                 signed_data_alt) in _rows(
                    source_path, table,
                    'id, fromAddress, toAddress, txHash, state, blockchainStr, currencyCodeStr, '
                    'networkStr, nonce, chainId, weiValue, erc20Value, transferValue, '
                    'recentBlockHash, validBefore, maxLedgerVersion, notFoundCount, '
                    'signedTxData, signedTransactionData'):
                data_list.append((
                    _text(from_address), _text(to_address), _text(tx_hash), _text(state),
                    _text(blockchain), _text(currency), _text(network), _text(nonce),
                    _text(chain_id), _text(wei_value), _text(erc20_value),
                    _text(transfer_value), _text(recent_block), _text(valid_before),
                    _text(max_ledger), _text(not_found),
                    _text(signed_data) or _text(signed_data_alt), table, _text(row_id),
                ))

    data_headers = (
        'From Address', 'To Address', 'Transaction Hash', 'State (as stored)',
        'Blockchain (as stored)', 'Currency Code (as stored)', 'Network (as stored)',
        'Nonce (as stored)', 'Chain ID (as stored)', 'Wei Value (as stored)',
        'ERC20 Value (as stored)', 'Transfer Value (as stored)', 'Recent Block Hash',
        'Valid Before (as stored)', 'Max Ledger Version (as stored)',
        'Not Found Count (as stored)', 'Signed Transaction Data (as stored)', 'Source Table',
        'Row ID',
    )
    return data_headers, data_list, '\n'.join(sources)
