__artifacts_v2__ = {
    "get_venmo_transactions": {
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
        "artifact_icon": "dollar-sign"
    },
    "get_venmo_users": {
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
        "artifact_icon": "users"
    }
}

from scripts.ilapfuncs import (
    artifact_processor,
    logfunc,
    convert_ts_human_to_utc,
    get_plist_file_content
)


@artifact_processor
def get_venmo_transactions(context):
    files_found = context.get_files_found()
    data_list = []

    data_headers = (
        ('Date Created', 'datetime'),
        ('Date Completed', 'datetime'),
        'Action', 'Payer', 'Payer ID',
        'Receiver', 'Receiver ID',
        'Note', 'Amount', 'Status', 'Audience', 'Type', 'Context',
        'Source File'
    )

    for file_found in files_found:
        file_found = str(file_found)

        plist_data = get_plist_file_content(file_found)

        if not plist_data:
            continue

        for row in plist_data.get('stories', []):
            if row.get('type') == 'disbursement':
                continue

            t_created_str = row.get('date_created')
            t_created = convert_ts_human_to_utc(t_created_str.replace('T', ' ').replace('Z', '')) if t_created_str else ''

            payment = row.get('payment', {})
            t_completed_str = payment.get('date_completed')
            t_completed = convert_ts_human_to_utc(t_completed_str.replace('T', ' ').replace('Z', '')) if t_completed_str else ''

            ptype = row.get('type', '')
            action = payment.get('action', '')
            note = payment.get('note', '')
            amount = payment.get('amount', '')
            status = payment.get('status', '')
            audience = row.get('audience', '')

            actor = payment.get('actor', {})
            target = payment.get('target', {})
            target_user = target.get('user', {})

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

            elif action == 'pay':
                payer = actor.get('display_name', '')
                payer_id = actor.get('username', '')
                receiver = target_user.get('display_name', '')
                receiver_id = target_user.get('username', '')
                context_str = f'{payer} paid {receiver}'
                if amount:
                    context_str += f' {amount}'

            data_list.append((
                t_created, t_completed, action, payer, payer_id,
                receiver, receiver_id, note, amount, status,
                audience, ptype, context_str, file_found
            ))

    if not data_list:
        logfunc('No Venmo transactions found.')
        return data_headers, [], ''

    return data_headers, data_list, ''


@artifact_processor
def get_venmo_users(context):
    files_found = context.get_files_found()
    data_list = []

    data_headers = (
        'User ID',
        ('Date Joined', 'datetime'),
        'Display Name', 'First Name', 'Last Name',
        'Friend Status', 'Is Blocked', 'Is Active', 'Is Payable',
        'Identity Type', ('Profile Pic URL', 'image'),
        'Source File'
    )

    users = {}

    for file_found in files_found:
        file_found = str(file_found)

        plist_data = get_plist_file_content(file_found)

        if not plist_data:
            continue

        for row in plist_data.get('stories', []):
            payment = row.get('payment', {})

            def process_user(user_data):
                if not user_data:
                    return

                uid = user_data.get('id')
                if not uid or uid in users:
                    return

                joined_str = user_data.get('date_joined')
                joined = convert_ts_human_to_utc(joined_str.replace('T', ' ').replace('Z', '')) if joined_str else ''

                users[uid] = (
                    uid,
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
                    file_found
                )

            process_user(payment.get('actor'))
            process_user(payment.get('target', {}).get('user'))

    data_list = list(users.values())

    if not data_list:
        logfunc('No Venmo users found.')
        return data_headers, [], ''

    return data_headers, data_list, ''
