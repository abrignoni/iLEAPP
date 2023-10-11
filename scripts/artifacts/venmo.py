import nska_deserialize as nd
import plistlib
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def output_users(report_folder, transactions, filename):
    """
    Outputs users info found through all transaction history
    """
    if len(transactions) > 0:
        report = ArtifactHtmlReport('Venmo - Users')
        report.start_artifact_report(report_folder, 'Venmo - Users')
        report.add_script()
        data_headers = (
            'User ID', 'Date Joined', 'Display Name', 'First Name', 'Last Name', 'Friend Status', 'Is Blocked', 'Is Active', 'Is Payable',
            'Identity Type', 'Profile Pic URL')  # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        users = {}
        for row in transactions:
            # Check actor
            actor_date_joined = row.get('payment', {}).get('actor', {}).get('date_joined', 'UNKNOWN').replace('T', ' ').replace('Z', '')
            actor_id =  row.get('payment', {}).get('actor', {}).get('id', 'UNKNOWN')
            actor_display_name =row.get('payment', {}).get('actor', {}).get('display_name', 'UNKNOWN')
            actor_fname = row.get('payment', {}).get('actor', {}).get('first_name', 'UNKNOWN')
            actor_lname = row.get('payment', {}).get('actor', {}).get('last_name', 'UNKNOWN')
            actor_friend_status = row.get('payment', {}).get('actor', {}).get('friend_status', 'UNKNOWN')
            actor_is_blocked = row.get('payment', {}).get('actor', {}).get('is_blocked', 'UNKNOWN')
            actor_is_active = row.get('payment', {}).get('actor', {}).get('is_active', 'UNKNOWN')
            actor_is_payable = row.get('payment', {}).get('actor', {}).get('is_payable', 'UNKNOWN')
            actor_identity_type = row.get('payment', {}).get('actor', {}).get('identity_type', 'UNKNOWN')
            actor_profile_pic_url = row.get('payment', {}).get('actor', {}).get('profile_picture_url', 'UNKNOWN')

            if users.get(actor_id, None) is None:
                dict_to_add = [actor_date_joined, actor_display_name, actor_fname, actor_lname, actor_friend_status,
                                        actor_is_blocked, actor_is_active, actor_is_payable, actor_identity_type, actor_profile_pic_url]
                users[actor_id] = dict_to_add
            x = 0

            # Check target
            target_date_joined = row.get('payment', {}).get('target', {}).get('user', {}).get('date_joined','UNKNOWN').replace('T',' ').replace('Z', '')
            target_id = row.get('payment', {}).get('target', {}).get('user', {}).get('id', 'UNKNOWN')
            target_display_name = row.get('payment', {}).get('target', {}).get('user', {}).get('display_name','UNKNOWN')
            target_fname = row.get('payment', {}).get('target', {}).get('user', {}).get('first_name', 'UNKNOWN')
            target_lname = row.get('payment', {}).get('target', {}).get('user', {}).get('last_name', 'UNKNOWN')
            target_friend_status = row.get('payment', {}).get('target', {}).get('user', {}).get('friend_status', 'UNKNOWN')
            target_is_blocked = row.get('payment', {}).get('target', {}).get('user', {}).get('is_blocked', 'UNKNOWN')
            target_is_active = row.get('payment', {}).get('target', {}).get('user', {}).get('is_active', 'UNKNOWN')
            target_is_payable = row.get('payment', {}).get('target', {}).get('user', {}).get('is_payable', 'UNKNOWN')
            target_identity_type = row.get('payment', {}).get('target', {}).get('user', {}).get('identity_type', 'UNKNOWN')
            target_profile_pic_url = row.get('payment', {}).get('target', {}).get('user', {}).get('profile_picture_url',
                                                                                              'UNKNOWN')

            if users.get(target_id, None) is None:
                dict_to_add = [target_date_joined, target_display_name, target_fname, target_lname, target_friend_status,
                                        target_is_blocked, target_is_active, target_is_payable, target_identity_type, target_profile_pic_url]
                users[target_id] = dict_to_add

        for user in users:
            data_list.append((user, users[user][0], users[user][1], users[user][2], users[user][3], users[user][4],
                              users[user][5], users[user][6], users[user][7], users[user][8], users[user][9]))

        report.write_artifact_data_table(data_headers, data_list, filename)
        report.end_artifact_report()

        tsvname = f'Venmo - Users'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Venmo - Users'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Venmo - Users data available')

def output_transactions(report_folder, transactions, filename):
    """
    Outputs transaction history
    """

    if len(transactions) > 0:
        report = ArtifactHtmlReport('Venmo - Transactions')
        report.start_artifact_report(report_folder, 'Venmo - Transactions')
        report.add_script()
        data_headers = (
        'Date Created', 'Date Completed', 'Action', 'Payer', 'Payer ID', 'Receiver', 'Receiver ID', 'Note', 'Amount', 'Status', 'Audience', 'Type', 'Context')  # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in transactions:

            if row['type'] == 'disbursement':
                pass
            if row['type'] == 'payment':

                if row['payment']['type'] == 'payment':
                    t_created = row.get('date_created', 'UNKNOWN').replace('T', ' ').replace('Z', '')
                    t_completed = row.get('payment', {}).get('date_completed', 'N/A').replace('T', ' ').replace('Z', '')
                    ptype = row.get('type', 'UNKNOWN')
                    action = row.get('payment', {}).get('action', 'UNKNOWN')

                    note = row.get('payment', {}).get('note', 'UNKNOWN')
                    amount = row.get('payment', {}).get('amount', 'UNKNOWN')
                    status =row.get('payment', {}).get('status', 'UNKNOWN')
                    audience = row.get('audience', 'UNKNOWN')

                    #Make the context sentence for easier understanding + logic for payer vs receiver
                    if action == 'charge':
                        receiver = row.get('payment', {}).get('actor', {}).get('display_name', 'UNKNOWN')
                        receiver_id = row.get('payment', {}).get('actor', {}).get('username', 'UNKNOWN')
                        payer = row.get('payment', {}).get('target', {}).get('user', {}).get('display_name', 'UNKNOWN')
                        payer_id = row.get('payment', {}).get('target', {}).get('user', {}).get('username', 'UNKNOWN')
                        if amount == "UNKNOWN":
                            context = f'{receiver} charged {payer}'
                        else:
                            context = f'{receiver} charged {payer} {amount}'

                    if action == 'pay':
                        payer = row.get('payment', {}).get('actor', {}).get('display_name', 'UNKNOWN')
                        payer_id = row.get('payment', {}).get('actor', {}).get('username', 'UNKNOWN')
                        receiver = row.get('payment', {}).get('target', {}).get('user', {}).get('display_name', 'UNKNOWN')
                        receiver_id = row.get('payment', {}).get('target', {}).get('user', {}).get('username', 'UNKNOWN')
                        if amount == "UNKNOWN":
                            context = f'{payer} paid {receiver}'
                        else:
                            context = f'{payer} paid {receiver} {amount}'

            elif row['type'] != 'payment' and row['type'] != 'disbursement':
                logfunc(f'Unknown transaction type of \"{row["type"]}\" found!!')
            data_list.append((t_created, t_completed, action, payer, payer_id, receiver, receiver_id, note, amount, status, audience, ptype, context))


        report.write_artifact_data_table(data_headers, data_list, filename)
        report.end_artifact_report()

        tsvname = f'Venmo - Transactions'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Venmo - Transactions'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Venmo - Transactions data available')

def deserialize_plist(plist_path):
    """
    Use nska_deserialize to deserialize our plists
    Goes right off of: https://pypi.org/project/nska-deserialize/
    """
    with open(plist_path, 'rb') as f:
        try:
            deserialized_plist = nd.deserialize_plist(f)
        except (nd.DeserializeError,
                nd.biplist.NotBinaryPlistException,
                nd.biplist.InvalidPlistException,
                plistlib.InvalidFileException,
                nd.ccl_bplist.BplistError,
                ValueError,
                TypeError, OSError, OverflowError) as ex:
            # These are all possible errors from libraries imported

            deserialized_plist = None

    return deserialized_plist

def get_venmo(files_found, report_folder, seeker, wrap_text, timezone_offset):
    """
    Parse venmo transactions. It's pretty simply stored in a serialized plist, but an awesome resource for learning more is:
    https://thebinaryhick.blog/2019/11/07/venmo-the-app-for-virtual-ballers/
    """

    transaction_data = []

    # Loop through files and deserialize
    for filename in files_found:
        deserialized_feed = deserialize_plist(filename)
        if deserialized_feed is not None:
            for row in deserialized_feed.get('stories', []): transaction_data.append(row)

    filenames = '\n'.join(files_found)
    output_transactions(report_folder, transaction_data, filenames)
    output_users(report_folder, transaction_data, filenames)

__artifacts__ = {
    "venmo": (
        "Venmo",
        ('*PrivateFeed','*PublicFeed','*FriendsFeed'),
        get_venmo)
}