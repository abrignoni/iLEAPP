__artifacts_v2__ = {
    "storeUser_ca": {  # This should match the function name exactly
        "name": "Installed Apps (storeUser)",
        "description": "Parses storeUser.db for installed app history",
        "author": "@stark4n6",
        "creation_date": "2025-04-11",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "",
        "paths": ('*/mobile/Library/Caches/com.apple.appstored/storeUser.db*',),
        "output_types": "standard",  # or ["html", "tsv", "timeline", "lava"]
        "artifact_icon": "package",
    },
    "storeUser_pha": {  # This should match the function name exactly
        "name": "Purchased Apps History (storeUser)",
        "description": "Parses storeUser.db for App Store purchased app history",
        "author": "@stark4n6",
        "creation_date": "2025-04-11",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "",
        "paths": ('*/mobile/Library/Caches/com.apple.appstored/storeUser.db*',),
        "output_types": "standard",  # or ["html", "tsv", "timeline", "lava"]
        "artifact_icon": "shopping-cart",
    }
}

import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, does_column_exist_in_db

@artifact_processor
def storeUser_ca(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "storeUser.db")
    data_list = []
    
    current_app_query = '''
    select
    datetime(timestamp+978307200, 'unixepoch'),
    bundle_id,
    item_name,
    vendor_name,
    short_version,
    bundle_version,
    item_id,
    case is_system_app
        when 1 then 'Yes'
        else 'No'
    end as "system_app",
    deletion_date
    from current_apps
    '''
    
    current_app_prev_query = '''
    select
    datetime(timestamp+978307200, 'unixepoch'),
    bundle_id,
    item_name,
    vendor_name,
    short_version,
    bundle_version,
    item_id,
    deletion_date
    from current_apps
    '''

    data_headers = (('Install Timestamp', 'datetime'),'Bundle ID','App Name','Developer Name','App Version','App Bundle Version','App Store ID','System App','Deletion Date')

    if does_column_exist_in_db(source_path, "current_apps", "is_system_app"):
        db_records = get_sqlite_db_records(source_path, current_app_query)
        for record in db_records:
            data_list.append((record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7], record[8]))
                            
    else:
        db_records = get_sqlite_db_records(source_path, current_app_prev_query)
        for record in db_records:
            data_list.append((record[0], record[1], record[2], record[3], record[4], record[5], 'No', record[6], record[7]))

    return data_headers, data_list, source_path

@artifact_processor  
def storeUser_pha(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "storeUser.db")
    data_list = []

    purchased_app_query = '''
    select
    datetime(purchase_history_apps.date_purchased+978307200, 'unixepoch') as "purchase_date",
    purchase_history_apps.title,
    purchase_history_apps.long_title,
    purchase_history_apps.bundle_id,
    purchase_history_apps.developer_name,
    purchase_history_apps.product_url,
    purchase_history_apps.store_item_id,
    case purchase_history_apps.hidden_from_springboard
        when 0 then 'No'
        when 1 then 'Yes'
    end as "hidden_from_springboard",
    purchase_history_apps.genre_name,
    purchase_history_apps.required_capabilities,
    account_events.apple_id,
    purchase_history_apps.purchaser_dsid,
    purchase_history_apps.purchase_token
    from purchase_history_apps
    left join account_events on account_events.account_id = purchase_history_apps.purchaser_dsid
    '''

    data_headers = (('Purchased Timestamp', 'datetime'),'App Name','App Name (Long)','Bundle ID','Developer Name','App Store URL','App ID','Hidden from Springboard','App Category','Required Capabilities','Purchaser Apple ID','Purchaser ID','Purchase Token')

    db_records = get_sqlite_db_records(source_path, purchased_app_query)
    for record in db_records:
        capabilities = caps = ''
        concat_cap = []
        if record[9] != None:
            capabilities = record[9].decode('utf-8').strip("[]").split(",")
            for item in capabilities:
                cleaned_item = item.strip().strip('"')
                concat_cap.append(cleaned_item)
            caps = ";\n".join(concat_cap)[:-1]
        
        data_list.append((record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7], record[8], caps, record[10], record[11], record[12]))

    return data_headers, data_list, source_path