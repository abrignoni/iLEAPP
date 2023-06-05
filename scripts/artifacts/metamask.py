from os.path import dirname, join
import json
import datetime
import time
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_metamask(files_found, report_folder, seeker, wrap_text):
    wallets = []
    contacts = []
    transactions = []
    artifacts_from_in_app_browser = []

    for file_found in files_found:
        file_found = str(file_found)
    
    root = open(file_found)
    data = json.load(root)
    if 'engine' in data:
        json_object = json.loads(data['engine'])
        json_browser = json.loads(data['browser'])
        for i in json_object:
            for accs in json_object['backgroundState']['AccountTrackerController']['accounts']:
                s = json_object['backgroundState']['PreferencesController']['identities'][accs]['importTime'] / 1000.0
                import_time = datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S.%f')
                balance = int(str(json_object['backgroundState']['AccountTrackerController']['accounts'][accs]['balance']), 16)
                wallets.append((str(json_object['backgroundState']['PreferencesController']['identities'][accs]['name']) , accs, balance/(10**18) , import_time))
            for contactId in json_object['backgroundState']['AddressBookController']['addressBook']:
                for contact in json_object['backgroundState']['AddressBookController']['addressBook'][contactId]:
                    contacts.append((str(json_object['backgroundState']['AddressBookController']['addressBook'][contactId][contact]['name']), str(json_object['backgroundState']['AddressBookController']['addressBook'][contactId][contact]['address'])))
            for transaction in json_object['backgroundState']['TransactionController']['transactions']:
                s = transaction['time'] / 1000.0
                transaction_time = datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S.%f')
                transaction_value = int(str(transaction['transaction']['value']), 16) / (10**18)
                transactions.append((str(transaction['transaction']['from']),str(transaction['transaction']['to']),transaction_value ,transaction_time, transaction['transactionHash']))
            for history in json_browser["history"]:
                artifacts_from_in_app_browser.append((str(history["url"]),str(history['name'])))

    description = ''

    report = ArtifactHtmlReport('Meta Mask Wallets')
    report.start_artifact_report(report_folder, 'Wallets', description)
    wallet_headers = ("Wallet Name", 'Wallet Address','Balance (In Network Currency)', 'Import Time')     
    report.write_artifact_data_table(wallet_headers, wallets, file_found)
    report.end_artifact_report()
    report.start_artifact_report(report_folder, 'Contacts', description)
    contacts_headers = ('Contact Name','Wallet Address')     
    report.write_artifact_data_table(contacts_headers, contacts, file_found)
    report.end_artifact_report()
    report.start_artifact_report(report_folder, 'Transactions', description)
    transaction_headers = ('From','To', 'Value' ,'Time', 'Transaction Hash')     
    report.write_artifact_data_table(transaction_headers, transactions, file_found)
    report.end_artifact_report()
    report.start_artifact_report(report_folder, 'Browser', description)
    browser_headers = ('name','url')     
    report.write_artifact_data_table(browser_headers, artifacts_from_in_app_browser, file_found)
    report.end_artifact_report()
__artifacts__ = {
    "metamask": (
        "Metamask",
        ('*/private/var/mobile/Containers/Data/Application/*/Documents/persistStore/persist-root',''),
        get_metamask)
}