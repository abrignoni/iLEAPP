from os.path import dirname, join
import json
import datetime
import time
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_metamask(files_found, report_folder, seeker, wrap_text, timezone_offset):
    wallets = []
    contacts = []
    transactions = []
    artifacts_from_in_app_browser = []

    for file_found in files_found:
        file_found = str(file_found)
    
        root = open(file_found, "r")
        data = json.load(root)
        if 'engine' in data:
            json_object = json.loads(data['engine'])
            json_browser = json.loads(data['browser'])
            for i in json_object:
                for accs in json_object['backgroundState']['AccountTrackerController']['accounts']:
                    s = json_object['backgroundState']['PreferencesController']['identities'][accs]['importTime'] / 1000.0
                    import_time = datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S.%f')
                    balance = int(str(json_object['backgroundState']['AccountTrackerController']['accounts'][accs]['balance']), 16)
                    wallets.append((import_time, str(json_object['backgroundState']['PreferencesController']['identities'][accs]['name']) , accs, balance/(10**18)))
                for contactId in json_object['backgroundState']['AddressBookController']['addressBook']:
                    for contact in json_object['backgroundState']['AddressBookController']['addressBook'][contactId]:
                        contacts.append((str(json_object['backgroundState']['AddressBookController']['addressBook'][contactId][contact]['name']), str(json_object['backgroundState']['AddressBookController']['addressBook'][contactId][contact]['address'])))
                for transaction in json_object['backgroundState']['TransactionController']['transactions']:
                    s = transaction['time'] / 1000.0
                    transaction_time = datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S.%f')
                    transaction_value = int(str(transaction['transaction']['value']), 16) / (10**18)
                    transactions.append((transaction_time, str(transaction['transaction']['from']),str(transaction['transaction']['to']),transaction_value , transaction['transactionHash']))
                for history in json_browser["history"]:
                    artifacts_from_in_app_browser.append((str(history["url"]),str(history['name'])))

        description = ''

        report = ArtifactHtmlReport('Meta Mask - Wallerts')
        report.start_artifact_report(report_folder, 'Meta Mask - Wallets', description)
        report.add_script()
        wallet_headers = ('Import Timestamp', 'Wallet Name', 'Wallet Address','Balance (In Network Currency)')
        report.write_artifact_data_table(wallet_headers, wallets, file_found)
        report.end_artifact_report()
        
        tsvname = 'Meta Mask - Wallets'
        tsv(report_folder, wallet_headers, wallets, tsvname)

        tlactivity = 'Meta Mask - Wallets'
        timeline(report_folder, tlactivity, wallets, wallet_headers)
        
        report = ArtifactHtmlReport('Meta Mask - Contacts')
        report.start_artifact_report(report_folder, 'Meta Mask - Contacts', description)
        report.add_script()
        contacts_headers = ('Contact Name','Wallet Address')     
        report.write_artifact_data_table(contacts_headers, contacts, file_found)
        report.end_artifact_report()
        
        tsvname = 'Meta Mask - Contacts'
        tsv(report_folder, contacts_headers, contacts, tsvname)
        
        report = ArtifactHtmlReport('Meta Mask - Transactions')
        report.start_artifact_report(report_folder, 'Meta Mask - Transactions', description)
        report.add_script()
        transaction_headers = ('Timestamp', 'From','To', 'Value' ,'Transaction Hash')     
        report.write_artifact_data_table(transaction_headers, transactions, file_found)
        report.end_artifact_report()
        
        tsvname = 'Meta Mask - Transactions'
        tsv(report_folder, transaction_headers, transactions, tsvname)
        
        report = ArtifactHtmlReport('Meta Mask - Browser')
        report.start_artifact_report(report_folder, 'Meta Mask - Browser', description)
        report.add_script()
        browser_headers = ('Name','URL')     
        report.write_artifact_data_table(browser_headers, artifacts_from_in_app_browser, file_found)
        report.end_artifact_report()
        
        tsvname = 'Meta Mask - Browser'
        tsv(report_folder, browser_headers, artifacts_from_in_app_browser, tsvname)

        tlactivity = 'Meta Mask - Browser'
        timeline(report_folder, tlactivity, artifacts_from_in_app_browser, browser_headers)
    
    
__artifacts__ = {
    "metamask": (
        "Metamask",
        ('*/mobile/Containers/Data/Application/*/Documents/persistStore/persist-root'),
        get_metamask)
}