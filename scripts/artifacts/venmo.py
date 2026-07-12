__artifacts_v2__ = {
    "venmo_transactions": {
        "name": "Venmo - Transactions",
        "description": "Extracts transaction history from Venmo feed files.",
        "author": "@jfarley248",
        "creation_date": "2021-09-25",
        "last_update_date": "2025-11-28",
        "requirements": "none",
        "category": "Venmo",
        "notes": "",
        "paths": ('*PrivateFeed','*PublicFeed','*FriendsFeed'),
        "output_types": "standard",
        "artifact_icon": "currency-dollar",
        "sample_data": {
            "hickman_ios13": "iOS 13.3.1 | Venmo 7.47.1 | 30 rows",
            "hickman_ios14": "iOS 14.3 | Venmo 8.14.1 | 39 rows",
        }
    },
    "venmo_users": {
        "name": "Venmo - Users",
        "description": "Extracts user information found in Venmo transaction history.",
        "author": "@jfarley248",
        "creation_date": "2021-09-25",
        "last_update_date": "2025-11-28",
        "requirements": "none",
        "category": "Venmo",
        "notes": "",
        "paths": ('*PrivateFeed', '*PublicFeed', '*FriendsFeed'),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "hickman_ios13": "iOS 13.3.1 | Venmo 7.47.1 | 42 rows",
            "hickman_ios14": "iOS 14.3 | Venmo 8.14.1 | 3 rows",
        }
    }
}

from scripts.ilapfuncs import (
    artifact_processor,
    logfunc,
    convert_ts_human_to_utc,
    get_plist_file_content
)


def process_user(users, user_data, source_file):
    """Add a Venmo user to the deduplicated user collection."""
    if not isinstance(user_data, dict):
        return

    user_id = user_data.get('id')
    if not user_id or user_id in users:
        return

    joined_str = user_data.get('date_joined')
    joined = convert_ts_human_to_utc(
        joined_str.replace('T', ' ').replace('Z', '')
    ) if joined_str else ''

    users[user_id] = (
        user_id,
        joined,
        user_data.get('display_name', ''),
        user_data.get('first_name', ''),
        user_data.get('last_name', ''),
        user_data.get('friend_status', ''),
        str(user_data.get('is_blocked', '')),
        str(user_data.get('is_active', '')),
        str(user_data.get('is_payable', '')),
        user_data.get('identity_type', ''),
        user_data.get('profile_picture_url', ''),
        source_file,
    )


@artifact_processor
def venmo_transactions(context):
    files_found = context.get_files_found()
    data_list = []

    data_headers = (
        ('Date Created', 'datetime'),
        ('Date Completed', 'datetime'),
        'Action', 'Payer', 'Payer Username',
        'Receiver', 'Receiver Username',
        'Note', 'Amount', 'Status', 'Audience', 'Transaction Type', 'Context',
        'Source File'
    )

    for file_found in files_found:
        file_found = str(file_found)

        plist_data = get_plist_file_content(file_found)

        if not isinstance(plist_data, dict):
            continue

        for row in plist_data.get('stories', []):
            if not isinstance(row, dict):
                continue

            transaction_type = row.get('type')
            payment = row.get('payment')
            if transaction_type != 'payment' or not isinstance(payment, dict):
                if transaction_type != 'disbursement':
                    logfunc(f'Unsupported Venmo transaction type: {transaction_type}')
                continue

            if payment.get('type') != 'payment':
                logfunc(f"Unsupported Venmo payment type: {payment.get('type')}")
                continue

            action = payment.get('action', '')
            if action not in ('charge', 'pay'):
                logfunc(f'Unsupported Venmo payment action: {action}')
                continue

            t_created_str = row.get('date_created')
            t_created = convert_ts_human_to_utc(t_created_str.replace('T', ' ').replace('Z', '')) if t_created_str else ''

            t_completed_str = payment.get('date_completed')
            t_completed = convert_ts_human_to_utc(t_completed_str.replace('T', ' ').replace('Z', '')) if t_completed_str else ''

            note = payment.get('note', '')
            amount = payment.get('amount', '')
            status = payment.get('status', '')
            audience = row.get('audience', '')

            actor = payment.get('actor', {})
            target = payment.get('target', {})
            target_user = target.get('user', {}) if isinstance(target, dict) else {}
            if not isinstance(actor, dict):
                actor = {}
            if not isinstance(target_user, dict):
                target_user = {}

            payer = ''
            payer_id = ''
            receiver = ''
            receiver_id = ''
            context_str = ''

            if action == 'charge':
                receiver = actor.get('display_name', '')
                receiver_id = actor.get('username', '')
                payer = target_user.get('display_name', '')
                payer_id = target_user.get('username', '')
                context_str = f'{receiver} charged {payer}'
                if amount:
                    context_str += f' {amount}'

            else:
                payer = actor.get('display_name', '')
                payer_id = actor.get('username', '')
                receiver = target_user.get('display_name', '')
                receiver_id = target_user.get('username', '')
                context_str = f'{payer} paid {receiver}'
                if amount:
                    context_str += f' {amount}'

            source_file = context.get_relative_path(file_found)
            data_list.append((
                t_created, t_completed, action, payer, payer_id,
                receiver, receiver_id, note, amount, status,
                audience, transaction_type, context_str, source_file
            ))

    if not data_list:
        logfunc('No Venmo transactions found.')
        return data_headers, [], 'Source files listed in report'

    return data_headers, data_list, 'Source files listed in report'


@artifact_processor
def venmo_users(context):
    files_found = context.get_files_found()
    data_list = []

    data_headers = (
        'User ID',
        ('Date Joined', 'datetime'),
        'Display Name', 'First Name', 'Last Name',
        'Friend Status', 'Is Blocked', 'Is Active', 'Is Payable',
        'Identity Type', 'Profile Pic URL',
        'Source File'
    )

    users = {}

    for file_found in files_found:
        file_found = str(file_found)

        plist_data = get_plist_file_content(file_found)

        if not isinstance(plist_data, dict):
            continue

        for row in plist_data.get('stories', []):
            if not isinstance(row, dict):
                continue

            payment = row.get('payment')
            if not isinstance(payment, dict):
                continue

            target = payment.get('target')
            target_user = target.get('user') if isinstance(target, dict) else None
            source_file = context.get_relative_path(file_found)

            process_user(users, payment.get('actor'), source_file)
            process_user(users, target_user, source_file)

    data_list = list(users.values())

    if not data_list:
        logfunc('No Venmo users found.')
        return data_headers, [], 'Source files listed in report'

    return data_headers, data_list, 'Source files listed in report'
