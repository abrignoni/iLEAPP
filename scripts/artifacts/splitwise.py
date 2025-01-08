__artifacts_v2__ = {
    "splitwiseUsers": {
        "name": "Splitwise - Users",
        "description": "Parses users information from Splitwise app",
        "author": "@KevinPagano3",
        "creation_date": "2024-04-09",
        "last_update_date": "2025-01-07",
        "requirements": "none",
        "category": "Finance",
        "notes": "",
        "paths": ('*/Library/Application Support/database.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "user"
    },
    "splitwiseExpenses": {
        "name": "Splitwise - Expenses",
        "description": "Parses expenses information from Splitwise app",
        "author": "@KevinPagano3",
        "creation_date": "2024-04-09",
        "last_update_date": "2025-01-07",
        "requirements": "none",
        "category": "Finance",
        "notes": "",
        "paths": ('*/Library/Application Support/database.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "dollar-sign"
    },
    "splitwiseExpenseBalances": {
        "name": "Splitwise - Expense Balances",
        "description": "Parses expense balances information from Splitwise app",
        "author": "@KevinPagano3",
        "creation_date": "2024-04-09",
        "last_update_date": "2025-01-07",
        "requirements": "none",
        "category": "Finance",
        "notes": "",
        "paths": ('*/Library/Application Support/database.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "dollar-sign"
    },
    "splitwiseTotalBalances": {
        "name": "Splitwise - Total Balances",
        "description": "Parses total balances information from Splitwise app",
        "author": "@KevinPagano3",
        "creation_date": "2024-04-09",
        "last_update_date": "2025-01-07",
        "requirements": "none",
        "category": "Finance",
        "notes": "",
        "paths": ('*/Library/Application Support/database.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "dollar-sign"
    },
    "splitwiseGroups": {
        "name": "Splitwise - Groups",
        "description": "Parses groups information in Splitwise app",
        "author": "@KevinPagano3",
        "creation_date": "2024-04-09",
        "last_update_date": "2025-01-07",
        "requirements": "none",
        "category": "Finance",
        "notes": "",
        "paths": ('*/Library/Application Support/database.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "html_columns": ['Members']
    },
    "splitwiseNotifications": {
        "name": "Splitwise - Notifications",
        "description": "Parses notifications from Splitwise app",
        "author": "@KevinPagano3",
        "creation_date": "2024-04-09",
        "last_update_date": "2025-01-07",
        "requirements": "none",
        "category": "Finance",
        "notes": "",
        "paths": ('*/Library/Application Support/database.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "bell",
        "html_columns": ['Notification']
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, convert_unix_ts_to_utc

@artifact_processor
def splitwiseUsers(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "database.sqlite")
    data_list = []

    query = '''
    SELECT
        createdAt,
        updatedAt,
        firstName,
        lastName,
        email,
        phone,
        personId,
        largeImagePath,
        currencyCode,
        countryCode,
        registrationStatus
    FROM SWPerson
    '''

    data_headers = (
        ('Created Timestamp', 'datetime'), 
        ('Updated Timestamp', 'datetime'), 
        'First Name', 
        'Last Name', 
        'Email', 
        ('Phone', 'phonenumber'), 
        'Person ID', 
        'Avatar Path', 
        'Currency', 
        'Country', 
        'Registration Status')

    db_records = get_sqlite_db_records(source_path, query)
    
    for record in db_records:
        created_ts = convert_unix_ts_to_utc(record[0])
        updated_ts = convert_unix_ts_to_utc(record[1])
        
        data_list.append(
            (created_ts, updated_ts, record[2], record[3], record[4], record[5], record[6], 
             record[7], record[8], record[9], record[10]))

    return data_headers, data_list, source_path


@artifact_processor
def splitwiseExpenses(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "database.sqlite")
    data_list = []

    query = '''
    SELECT
        SWExpense.createdAtDate,
        SWExpense.updatedAt,
        coalesce(SWPerson.firstName,'') || coalesce(SWPerson.lastName,'') || ' ('|| coalesce(SWPerson.email,'') || ')',
        SWExpense.description,
        SWExpense.cost,
        SWExpense.currencyCode,
        SWExpense.category,            
        SWGroup.groupName,
        SWExpense.expenseId,
        SWExpense.guid
    FROM SWExpense
    LEFT JOIN SWPerson ON SWExpense.createdById = SWPerson.personId
    LEFT JOIN SWGroup ON SWExpense.groupId = SWGroup.groupId
    '''
    
    data_headers = (
        ('Created Timestamp', 'datetime'), 
        ('Updated Timestamp', 'datetime'), 
        'Payer', 
        'Expense Description', 
        'Cost', 
        'Currency', 
        'Category', 
        'Group Name', 
        'Expense ID', 
        'Expense GUID')

    db_records = get_sqlite_db_records(source_path, query)
    
    for record in db_records:
        created_ts = convert_unix_ts_to_utc(record[0])
        updated_ts = convert_unix_ts_to_utc(record[1])
        
        data_list.append(
            (created_ts, updated_ts, record[2], record[3], record[4], record[5], record[6], 
             record[7], record[8], record[9]))
        
    return data_headers, data_list, source_path


@artifact_processor
def splitwiseExpenseBalances(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "database.sqlite")
    data_list = []

    query = '''
    SELECT
        SWExpenseMember.createdAt,
        coalesce(SWPerson.firstName,'') || coalesce(SWPerson.lastName,''),
        SWPerson.email,
        SWExpense.description,
        SWExpenseMember.owedShare,
        SWExpenseMember.paidShare
    FROM SWExpenseMember
    LEFT JOIN SWExpense ON SWExpense.id = SWExpenseMember.sWExpenseId
    LEFT JOIN SWPerson ON SWPerson.id = SWExpenseMember.sWPersonId
    '''
    
    data_headers = (
        ('Created Timestamp', 'datetime'), 
        'Member Name', 
        'Email', 
        'Expense', 
        'Owed Share', 
        'Paid Share')
    
    db_records = get_sqlite_db_records(source_path, query)
    
    for record in db_records:
        created_ts = convert_unix_ts_to_utc(record[0])
        data_list.append((created_ts, record[1], record[2], record[3], record[4], record[5]))
        
    return data_headers, data_list, source_path


@artifact_processor
def splitwiseTotalBalances(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "database.sqlite")
    data_list = []

    query = '''
    SELECT
        SWBalance.createdAt,
        SWBalance.updatedAt,
        coalesce(SWPerson.firstName,'') || coalesce(SWPerson.lastName,''),
        SWPerson.email,
        SWBalance.amount,
        SWBalance.currencyCode
    FROM SWBalance
    LEFT JOIN SWFriendship ON SWFriendship.id = SWBalance.sWFriendshipId
    LEFT JOIN SWPerson ON SWPerson.personId = SWFriendship.personId
    '''
    
    data_headers = (
        ('Created Timestamp', 'datetime'), 
        ('Updated Timestamp', 'datetime'), 
        'Friend Name', 
        'Email', 
        'Balance', 
        'Currency')
    
    db_records = get_sqlite_db_records(source_path, query)
    
    for record in db_records:
        created_ts = convert_unix_ts_to_utc(record[0])
        updated_ts = convert_unix_ts_to_utc(record[1])
        data_list.append((created_ts, updated_ts, record[2], record[3], record[4], record[5]))

    return data_headers, data_list, source_path



@artifact_processor
def splitwiseGroups(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "database.sqlite")
    data_list = []
    data_list_html = []

    query = '''
    SELECT
        SWGroup.createdAtDate,
        SWGroup.updatedAtDate,
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
    FROM SWGroup
    LEFT JOIN SWGroupMember ON SWGroup.id = SWGroupMember.sWGroupId
    GROUP BY SWGroup.groupId
    '''
    
    data_headers = (
        ('Created Timestamp', 'datetime'), 
        ('Updated Timestamp', 'datetime'), 
        'Group Name', 
        'Members', 
        'Group ID', 
        'Group Type', 
        'Invite Link', 
        'Whiteboard', 
        'Avatar URL', 
        'Cover Photo URL')
    
    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        created_ts = convert_unix_ts_to_utc(record[0])
        updated_ts = convert_unix_ts_to_utc(record[1])
        
        member_split = record[3].split('; ')
        members = ''
        for section in member_split:
            members += section + ';' + chr(13)
        
        group_title = record[5].title() if record[5] else record[5]
        data_list.append(
            (created_ts, updated_ts, record[2], members, record[4], group_title, record[6], 
             record[7], record[8], record[9]))
        data_list_html.append(
            (created_ts, updated_ts, record[2], members.replace(chr(13), '<br>')[:-2], record[4], 
             group_title, record[6], record[7], record[8], record[9]))

    return data_headers, (data_list, data_list_html), source_path


@artifact_processor
def splitwiseNotifications(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "database.sqlite")
    data_list = []
    data_list_html = []

    query = '''
    SELECT
        createdAtDate,
        content,
        sourceType,
        notificationId
    FROM SWNotification
    '''
    
    data_headers = (
        ('Created Timestamp', 'datetime'), 
        'Notification', 
        'Source Type', 
        'Notification ID')
    
    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        created_ts = convert_unix_ts_to_utc(record[0])
        data_list_html.append((created_ts, record[1], record[2], record[3]))
        if '<strong>' and '</strong>' in record[1]:
            remove_html = record[1].replace('<strong>', '').replace('</strong>', '')
        data_list.append((created_ts, remove_html, record[2], record[3]))

    return data_headers, (data_list, data_list_html), source_path
