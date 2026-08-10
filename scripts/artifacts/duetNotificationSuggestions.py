__artifacts_v2__ = {
    "duetNotifications": {
        "name": "DuetExpertCenter - Notifications",
        "description": "Parses the notification history in DuetExpertCenter's "
                       "notificationAndSuggestionDB.db, including the delivering app, urgency, "
                       "delivery method and the latest recorded outcome",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-28",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "DuetExpertCenter",
        "notes": "No notification body text was present in tested databases; only metadata such as "
                 "body length. In tested images this database retained notification records older "
                 "than some apps' own message databases. The numeric urgency, "
                 "delivery-method, delivery-reason and outcome codes are Apple-internal and are "
                 "reported verbatim rather than guessed at.",
        "paths": ('*/mobile/Library/DuetExpertCenter/notificationAndSuggestionDB.db*',),
        "output_types": "standard",
        "artifact_icon": "bell",
        "sample_data": {
            "otto_ios17": "iOS 17.5.1 | 12396 rows",
            "iphone11_ios17": "iOS 17.3 | 3273 rows (no notificationBodyLength column)",
            "dexter_ios18": "iOS 18.3.2 | 3109 rows",
            "hc_ios18_7": "iOS 18.7.8 | 171 rows",
            "felix23_ios16": "iOS 16.5 | 543 rows",
            "fsfull002_ios17": "iOS 17.1 | 27 rows (no notificationBodyLength column)",
        },
    },
    "duetNotificationSuggestions": {
        "name": "DuetExpertCenter - Notification Suggestions",
        "description": "Parses the notification-handling suggestions generated "
                       "by DuetExpertCenter, with the triggering notification and the outcome",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-28",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "DuetExpertCenter",
        "notes": "Suggestion, scope and outcome codes are Apple-internal and are reported verbatim. "
                 "The Trigger Notification UUID joins back to the DuetExpertCenter - Notifications "
                 "artifact.",
        "paths": ('*/mobile/Library/DuetExpertCenter/notificationAndSuggestionDB.db*',),
        "output_types": "standard",
        "artifact_icon": "bulb",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 117 rows",
            "otto_ios17": "iOS 17.5.1 | 100 rows",
            "dexter_ios18": "iOS 18.3.2 | 14 rows",
            "iphone11_ios17": "iOS 17.3 | 11 rows",
            "felix23_ios16": "iOS 16.5 | 5 rows",
        },
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, \
    convert_cocoa_core_data_ts_to_utc, does_column_exist_in_db


@artifact_processor
def duetNotifications(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'notificationAndSuggestionDB.db')
    data_list = []

    # Apple added columns to this table over time (notificationBodyLength is absent on some
    # iOS 17 builds), so each late column is selected only when the database actually has it.
    # Naming them in the query regardless would raise "no such column" and silently drop every row.
    optional_columns = ('numExpansions', 'notificationBodyLength', 'receivedMode', 'rawIdentifier')
    present = {column: does_column_exist_in_db(source_path, 'notifications', column)
               for column in optional_columns}
    selected = [column if present[column] else f"'' AS {column}" for column in optional_columns]

    query = f'''
    SELECT
        receiveTimestamp,
        bundleId,
        isMessage,
        isGroupMessage,
        urgency,
        deliveryMethod,
        deliveryReason,
        latestOutcome,
        latestOutcomeTimestamp,
        isProminent,
        isActive,
        {selected[0]},
        {selected[1]},
        threadId,
        contactId,
        {selected[2]},
        {selected[3]},
        uuid
    FROM notifications
    ORDER BY receiveTimestamp DESC
    '''

    for record in get_sqlite_db_records(source_path, query):
        received = convert_cocoa_core_data_ts_to_utc(record[0])
        outcome_ts = convert_cocoa_core_data_ts_to_utc(record[8]) if record[8] else ''

        data_list.append((received, record[1], record[2], record[3], record[4], record[5],
                          record[6], record[7], outcome_ts, record[9], record[10], record[11],
                          record[12], record[13], record[14], record[15], record[16], record[17]))

    data_headers = (
        ('Received Timestamp', 'datetime'), 'Bundle ID', 'Is Message', 'Is Group Message',
        'Urgency', 'Delivery Method', 'Delivery Reason', 'Latest Outcome',
        ('Latest Outcome Timestamp', 'datetime'), 'Is Prominent', 'Is Active', 'Expansions',
        'Notification Body Length', 'Thread ID', 'Contact ID', 'Received Mode', 'Raw Identifier',
        'UUID')

    return data_headers, data_list, source_path


@artifact_processor
def duetNotificationSuggestions(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'notificationAndSuggestionDB.db')
    data_list = []

    query = '''
    SELECT
        createdTimestamp,
        shownTimestamp,
        suggestionType,
        scope,
        entityIdentifier,
        latestOutcome,
        latestOutcomeTimestamp,
        isActive,
        feedbackKey,
        triggerNotificationUUID,
        uuid
    FROM suggestions
    ORDER BY createdTimestamp DESC
    '''

    for record in get_sqlite_db_records(source_path, query):
        created = convert_cocoa_core_data_ts_to_utc(record[0])
        shown = convert_cocoa_core_data_ts_to_utc(record[1]) if record[1] else ''
        outcome_ts = convert_cocoa_core_data_ts_to_utc(record[6]) if record[6] else ''

        data_list.append((created, shown, record[2], record[3], record[4], record[5], outcome_ts,
                          record[7], record[8], record[9], record[10]))

    data_headers = (
        ('Created Timestamp', 'datetime'), ('Shown Timestamp', 'datetime'), 'Suggestion Type',
        'Scope', 'Entity Identifier', 'Latest Outcome', ('Latest Outcome Timestamp', 'datetime'),
        'Is Active', 'Feedback Key', 'Trigger Notification UUID', 'UUID')

    return data_headers, data_list, source_path
