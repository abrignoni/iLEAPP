__artifacts_v2__ = {
    "splitwise": {
        "name": "Splitwise",
        "description": "Parses users, accounts, and transaction information from Splitwise app",
        "author": "@KevinPagano3",
        "version": "0.0.1",
        "date": "2024-04-09",
        "requirements": "none",
        "category": "Splitwise",
        "notes": "",
        "paths": ('*/Library/Application Support/database.sqlite*',),
        "function": "get_Splitwise"
    }
}

import re
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone, does_table_exist

def get_Splitwise(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    data_list_users = []
    data_list_expenses = []
    data_list_expense_balance = []
    data_list_groups = []
    data_list_groups_tsv = []
    data_list_notification = []
    data_list_notification_tsv = []
    data_list_total_balance = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('database.sqlite'):
            db = open_sqlite_db_readonly(file_found)
            
            if does_table_exist(db, 'SWPerson'):
                cursor = db.cursor()
                
                # Users
                cursor.execute('''
                select
                datetime(createdAt,'unixepoch'),
                datetime(updatedAt,'unixepoch'),
                firstName,
                lastName,
                email,
                phone,
                personId,
                largeImagePath,
                currencyCode,
                countryCode,
                registrationStatus
                from SWPerson
                ''')

                all_rows = cursor.fetchall()
                
                for row in all_rows:
                    created_ts = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),timezone_offset)
                    updated_ts = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[1]),timezone_offset)
                    
                    data_list_users.append((created_ts,updated_ts,row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],file_found))
                 
                # Expenses
                cursor.execute('''
                select
                datetime(SWExpense.createdAtDate,'unixepoch'),
                datetime(SWExpense.updatedAt,'unixepoch'),
                coalesce(SWPerson.firstName,'') || coalesce(SWPerson.lastName,'') || ' ('|| coalesce(SWPerson.email,'') || ')',
                SWExpense.description,
                SWExpense.cost,
                SWExpense.currencyCode,
                SWExpense.category,            
                SWGroup.groupName,
                SWExpense.expenseId,
                SWExpense.guid
                from SWExpense
                left join SWPerson on SWExpense.createdById = SWPerson.personId
                left join SWGroup on SWExpense.groupId = SWGroup.groupId
                ''')
                
                all_rows = cursor.fetchall()
                
                for row in all_rows:
                    created_ts = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),timezone_offset)
                    updated_ts = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[1]),timezone_offset)
                    
                    data_list_expenses.append((created_ts,updated_ts,row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],file_found))
                    
                # Expense Balances
                cursor.execute('''
                select
                datetime(SWExpenseMember.createdAt,'unixepoch'),
                coalesce(SWPerson.firstName,'') || coalesce(SWPerson.lastName,''),
                SWPerson.email,
                SWExpense.description,
                SWExpenseMember.owedShare,
                SWExpenseMember.paidShare
                from SWExpenseMember
                left join SWExpense on SWExpense.id = SWExpenseMember.sWExpenseId
                left join SWPerson on SWPerson.id = SWExpenseMember.sWPersonId
                ''')
                
                all_rows = cursor.fetchall()
                
                for row in all_rows:
                    created_ts = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),timezone_offset)
                    
                    data_list_expense_balance.append((created_ts,row[1],row[2],row[3],row[4],row[5],file_found))
                
                # Groups
                cursor.execute('''
                select
                datetime(SWGroup.createdAtDate,'unixepoch'),
                datetime(SWGroup.updatedAtDate,'unixepoch'),
                SWGroup.groupName,
                group_concat(
                (select coalesce(SWPerson.firstName,'') || ' ' || coalesce(SWPerson.lastName,'') || '(' || coalesce(SWPerson.email,'') || ')'
                 from SWPerson
                 where SWPerson.personId = SWGroupMember.personId
                ), '; '
                ) as "Members",
                SWGroup.groupId,
                SWGroup.groupType,
                SWGroup.inviteLink,
                SWGroup.whiteboard,
                SWGroup.imagePath,
                SWGroup.coverPhotoURLString
                from SWGroup
                left join SWGroupMember on SWGroup.id = SWGroupMember.sWGroupId
                group by SWGroup.groupId
                ''')
                
                all_rows = cursor.fetchall()
                
                for row in all_rows:
                    created_ts = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),timezone_offset)
                    updated_ts = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[1]),timezone_offset)
                    
                    member_split = row[3].split('; ')
                    members = ''
                    for section in member_split:
                        members += section + ';<br>'
                    members = members[:-5]
                    
                    if row[5] is None:
                        data_list_groups_tsv.append((created_ts,row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],file_found))
                        data_list_groups.append((created_ts,updated_ts,row[2],members,row[4],row[5],row[6],row[7],row[8],row[9],file_found))
                    else:
                        data_list_groups_tsv.append((created_ts,row[2],row[3],row[4],row[5].title(),row[6],row[7],row[8],row[9],file_found))
                        data_list_groups.append((created_ts,updated_ts,row[2],members,row[4],row[5].title(),row[6],row[7],row[8],row[9],file_found))
                    
                # Activity / Notifications
                cursor.execute('''
                select
                datetime(createdAtDate,'unixepoch'),
                content,
                sourceType,
                notificationId
                from SWNotification
                ''')
                
                all_rows = cursor.fetchall()
                usageentries = len(all_rows)
                
                for row in all_rows:
                    created_ts = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),timezone_offset)
                    
                    data_list_notification.append((created_ts,row[1],row[2],row[3],file_found))
                    
                    if '<strong>' and '</strong>' in row[1]:
                        remove_html = row[1].replace('<strong>','').replace('</strong>','')
                        
                    data_list_notification_tsv.append((created_ts,remove_html,row[2],row[3],file_found))
                    
                # Total Balances
                cursor.execute('''
                select
                datetime(SWBalance.createdAt,'unixepoch'),
                datetime(SWBalance.updatedAt,'unixepoch'),
                coalesce(SWPerson.firstName,'') || coalesce(SWPerson.lastName,''),
                SWPerson.email,
                SWBalance.amount,
                SWBalance.currencyCode
                from SWBalance
                left join SWFriendship on SWFriendship.id = SWBalance.sWFriendshipId
                left join SWPerson on SWPerson.personId = SWFriendship.personId
                ''')
                
                all_rows = cursor.fetchall()
                
                for row in all_rows:
                    created_ts = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),timezone_offset)
                    updated_ts = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[1]),timezone_offset)
                    
                    data_list_total_balance.append((created_ts,updated_ts,row[2],row[3],row[4],row[5],file_found))

                db.close()
            else:
                continue
        else:
            continue
    
    # Users
    if data_list_users:
        report = ArtifactHtmlReport('Splitwise - Users')
        report.start_artifact_report(report_folder, 'Splitwise - Users')
        report.add_script()
        data_headers = ('Created Timestamp','Updated Timestamp','First Name','Last Name','Email','Phone','Person ID','Avatar Path','Currency','Country','Registration Status','Source File') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
          
        report.write_artifact_data_table(data_headers, data_list_users, file_found)
        report.end_artifact_report()
        
        tsvname = 'Splitwise - Users'
        tsv(report_folder, data_headers, data_list_users, tsvname)
        
        tlactivity = 'Splitwise - Users'
        timeline(report_folder, tlactivity, data_list_users, data_headers)
    else:
        logfunc('No Splitwise - Users available')
        
    # Expenses
    if data_list_expenses:
        report = ArtifactHtmlReport('Splitwise - Expenses')
        report.start_artifact_report(report_folder, 'Splitwise - Expenses')
        report.add_script()
        data_headers = ('Created Timestamp','Updated Timestamp','Payer','Expense Description','Cost','Currency','Category','Group Name','Expense ID','Expense GUID','Source File') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
          
        report.write_artifact_data_table(data_headers, data_list_expenses, file_found)
        report.end_artifact_report()
        
        tsvname = 'Splitwise - Expenses'
        tsv(report_folder, data_headers, data_list_expenses, tsvname)
        
        tlactivity = 'Splitwise - Expenses'
        timeline(report_folder, tlactivity, data_list_expenses, data_headers)
    else:
        logfunc('No Splitwise - Expenses available')
        
    # Expense Balances
    if data_list_expense_balance:
        report = ArtifactHtmlReport('Splitwise - Expense Balances')
        report.start_artifact_report(report_folder, 'Splitwise - Expense Balances')
        report.add_script()
        data_headers = ('Created Timestamp','Member Name','Email','Expense','Owed Share','Paid Share','Source File') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
          
        report.write_artifact_data_table(data_headers, data_list_expense_balance, file_found)
        report.end_artifact_report()
        
        tsvname = 'Splitwise - Expense Balances'
        tsv(report_folder, data_headers, data_list_expense_balance, tsvname)
        
        tlactivity = 'Splitwise - Expense Balances'
        timeline(report_folder, tlactivity, data_list_expense_balance, data_headers)
    else:
        logfunc('No Splitwise - Expense Balances available')
        
    # Groups    
    if data_list_groups:
        report = ArtifactHtmlReport('Splitwise - Groups')
        report.start_artifact_report(report_folder, 'Splitwise - Groups')
        report.add_script()
        data_headers = ('Created Timestamp','Updated Timestamp','Group Name','Members','Group ID','Group Type','Invite Link','Whiteboard','Avatar URL','Cover Photo URL','Source File') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
          
        report.write_artifact_data_table(data_headers, data_list_groups, file_found, html_no_escape=['Members'])
        report.end_artifact_report()
        
        tsvname = 'Splitwise - Groups'
        tsv(report_folder, data_headers, data_list_groups_tsv, tsvname)
        
        tlactivity = 'Splitwise - Groups'
        timeline(report_folder, tlactivity, data_list_groups, data_headers)
    else:
        logfunc('No Splitwise - Groups available')
        
    # Notifications    
    if data_list_notification:
        report = ArtifactHtmlReport('Splitwise - Notifications')
        report.start_artifact_report(report_folder, 'Splitwise - Notifications')
        report.add_script()
        data_headers = ('Created Timestamp','Notification','Source Type','Notification ID','Source File') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
          
        report.write_artifact_data_table(data_headers, data_list_notification, file_found, html_no_escape=['Notification'])
        report.end_artifact_report()
        
        tsvname = 'Splitwise - Notifications'
        tsv(report_folder, data_headers, data_list_notification_tsv, tsvname)
        
        tlactivity = 'Splitwise - Notifications'
        timeline(report_folder, tlactivity, data_list_notification, data_headers)
    else:
        logfunc('No Splitwise - Notifications available')
        
    # Total Balances    
    if data_list_total_balance:
        report = ArtifactHtmlReport('Splitwise - Total Balances')
        report.start_artifact_report(report_folder, 'Splitwise - Total Balances')
        report.add_script()
        data_headers = ('Created Timestamp','Updated Timestamp','Friend Name','Email','Balance','Currency','Source File') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
          
        report.write_artifact_data_table(data_headers, data_list_total_balance, file_found)
        report.end_artifact_report()
        
        tsvname = 'Splitwise - Total Balances'
        tsv(report_folder, data_headers, data_list_total_balance, tsvname)
        
        tlactivity = 'Splitwise - Total Balances'
        timeline(report_folder, tlactivity, data_list_total_balance, data_headers)
    else:
        logfunc('No Splitwise - Total Balances available')
    