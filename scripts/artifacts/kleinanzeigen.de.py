__artifacts_v2__ = {
    "get_kleinanzeigenuser": {
        "name": "Kleinanzeigen.de - User Account",
        "description": "Account values from the currentUserProfile entry of "
                       "com.ebaykleinanzeigen.ebc.plist: e-mail, id, contact name, initials, "
                       "account type, and the userSince and lastModified values read as Cocoa "
                       "seconds and printed in UTC, independently of the time zone of the "
                       "computer running the tool. No tested image is "
                       "recorded for this artifact.",
        "author": "@C_Peter, @AlexisBrignoni, Codex",
        "creation_date": "2025-02-19",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Kleinanzeigen.de",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Preferences/com.ebaykleinanzeigen.ebc.plist', ),
        "output_types": "standard",
        "artifact_icon": "user"
    },
    "get_kleinanzeigenmessagecache": {
        "name": "Kleinanzeigen.de - Message Cache",
        "description": "Rows from the selected conversation_cache JSON file, labelled by the existing preview or "
                 "messages branch. The cache filename alone does not establish app ownership.",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2025-02-18",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "Kleinanzeigen.de",
        "notes": "sender=0 is read as the local account; no source for that mapping is given here and it was "
                 "not measured on a counted sample. The OUTBOUND boundness value is read as the store spells "
                 "it. A conversation with no cached messages is reported as one row built from its preview: "
                 "the text is the shortened textShortTrimmed value, the time is receivedDate and the "
                 "Message_ID is blank, so that row is a preview and not a message record. A conversation "
                 "with no cached messages whose preview keys are missing or whose receivedDate cannot "
                 "be read produces no row, and the run log names its conversation id. Times are read as "
                 "Cocoa seconds and shown in UTC. The file is matched by name within any app container, so "
                 "the owning app should be confirmed from the source path. No tested image is recorded for "
                 "this artifact. Cache Row Origin is Preview only for rows emitted from an empty messages "
                 "list using the existing preview fallback, and Cached Message only for rows emitted by the "
                 "messages loop. Those labels describe parser row origin, not independently verified event "
                 "type, authorship, completeness, or whether a message was sent. The existing conversation "
                 "view includes both origins without filtering. Original contribution credited to @C_Peter.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/conversation_cache', ),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "data_views": {
            'conversation': {
                'conversationDiscriminatorColumn': 'Conversation-ID',
                'conversationLabelColumn': 'Advertisement',
                'textColumn': 'Message',
                'senderColumn': 'From_Name',
                'directionColumn': 'From Me',
                'directionSentValue': 1,
                'timeColumn': 'Timestamp'
            }
        }
    },
    "get_kleinanzeigensearchhistory": {
        "name": "Kleinanzeigen.de - Search History",
        "description": "Entries of searchedKeywords in the advertisementSearchDataHistory value "
                       "of com.ebaykleinanzeigen.ebc.plist, with each entry's timeStamp read as "
                       "Cocoa seconds and printed in UTC, independently of the time zone of the "
                       "computer running the tool. No tested image is "
                       "recorded for this artifact.",
        "author": "@C_Peter, @AlexisBrignoni, Codex",
        "creation_date": "2025-02-19",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Kleinanzeigen.de",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Preferences/com.ebaykleinanzeigen.ebc.plist', ),
        "output_types": "standard",
        "artifact_icon": "search"
    },
    "get_kleinanzeigenlastquery": {
        "name": "Kleinanzeigen.de - Last Search",
        "description": "Extracts the last search query. Locations are search locations, not device locations",
        "author": "@C_Peter",
        "creation_date": "2025-02-19",
        "last_update_date": "2025-02-19",
        "requirements": "none",
        "category": "Kleinanzeigen.de",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Private Documents/.last_search_query', ),
        "output_types": "all",
        "artifact_icon": "search"
    }
}

import json
import plistlib
import datetime

from scripts.ilapfuncs import artifact_processor, get_file_path, logfunc

@artifact_processor
def get_kleinanzeigenmessagecache(context):
    source_path = get_file_path(context.get_files_found(), 'conversation_cache')
    data_list = []

    with open(source_path, 'r', encoding='utf-8') as ka_in:
        m_cache = json.load(ka_in)

    for elem in m_cache['data']:
        conv_id = elem['conversationId']
        ad_name = elem['ad']['displayTitle']
        ad_id = elem['ad']['identifier']
        try:
            ad_stat = elem['clientData']['adStatus']
        except (KeyError, TypeError):
            ad_stat = "UNKNOWN"
        counter_name = elem['counterParty']['name']
        counter_id = elem['counterParty']['identifier']
        if elem['clientData']['role'] == "Seller":
            my_name = elem['clientData']['sellerName']
            my_id = elem['clientData']['userIdSeller']
        else:
            my_name = elem['clientData']['buyerName']
            my_id = elem['clientData']['userIdBuyer']
        if elem['messages'] == []:
            try:
                m_text = elem['clientData']['textShortTrimmed']
                m_rec = datetime.datetime.fromtimestamp(elem['clientData']['receivedDate'] + 978307200, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                # preview row: no message id and no attachments
                m_id = ''
                m_att = "none"
                if elem['clientData']['boundness'] == "OUTBOUND":
                    m_from = my_name
                    id_from = my_id
                    m_to = counter_name
                    id_to = counter_id
                    out = 1
                else:
                    m_from = counter_name
                    id_from = counter_id
                    m_to = my_name
                    id_to = my_id
                    out = 0
                conv_name = f"{ad_name} ({counter_name})"
                data_list.append((m_rec, out, m_from, conv_name, m_text, conv_id, ad_id, id_from, m_to, id_to, m_att, m_id, ad_stat, "Preview"))

            except (KeyError, TypeError, ValueError, OverflowError, OSError) as ex:
                logfunc(f'Kleinanzeigen.de message cache: no preview row for conversation '
                        f'{conv_id}: {type(ex).__name__}: {ex}')
        else:
            for message in elem['messages']:
                m_id = message['messageId']
                # Original timestamp is cocoa time - so 978307200 will be added
                m_rec = datetime.datetime.fromtimestamp(message['sentDate'] + 978307200, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                m_text = message['text']
                m_att = []
                for att in message['attachments']:
                    m_att.append(att['imageURL'])
                if m_att == []:
                    m_att = "none"
                else: 
                    m_att = ", ".join(m_att)
                if message['sender'] == 0:
                    m_from = my_name
                    id_from = my_id
                    m_to = counter_name
                    id_to = counter_id
                    out = 1
                else:
                    m_from = counter_name
                    id_from = counter_id
                    m_to = my_name
                    id_to = my_id
                    out = 0
                conv_name = f"{ad_name} ({counter_name})"
                data_list.append((m_rec, out, m_from, conv_name, m_text, conv_id, ad_id, id_from, m_to, id_to, m_att, m_id, ad_stat, "Cached Message"))

    data_headers = (
        ('Timestamp', 'datetime'),
        "From Me",
        "From_Name",
        "Advertisement",
        "Message",
        "Conversation-ID",
        "Ad-ID",
        "From_ID",
        "To_Name",
        "To_ID",
        "Attachment",
        "Message_ID",
        "AD-Status",
        "Cache Row Origin",
    )
    return data_headers, data_list, source_path

@artifact_processor
def get_kleinanzeigenlastquery(context):
    source_path = get_file_path(context.get_files_found(), '.last_search_query')
    data_list = []

    with open(source_path, 'r', encoding='utf-8') as ka_in:
        searchq = json.load(ka_in)
        s_keywords = searchq['keywords']
        s_category = searchq['categoryLocalizedName']
        for location in searchq['locations']:
            region = location['region']
            d_radius = location['defaultRadius']
            lon = location['longitude']
            lat = location['latitude']
            c_radius = location['currentRadius']
            data_list.append((s_keywords, s_category, region, d_radius, lon, lat, c_radius))
    
    data_headers = (
        "Keywords", "Category", "Region", "Radius (default)",
        "Longitude", "Latitude", "Radius (current)")
    return data_headers, data_list, source_path

@artifact_processor
def get_kleinanzeigenuser(context):
    source_path = get_file_path(context.get_files_found(), 'com.ebaykleinanzeigen.ebc.plist')
    data_list = []

    with open(source_path, 'rb') as ka_in:
        pref = plistlib.load(ka_in)
        user = json.loads(pref['UserDefaultsKit.UserDefaultItem.currentUserProfile'])
        mail = user['email']
        u_id = user['id']
        name = user['preferences']['contactName']
        u_in = user['preferences']['initials']
        atype = user['accountType']
        c_dt = user['userSince']
        m_dt = user['lastModified']
        data_list.append(("Account E-Mail", mail))
        data_list.append(("Account ID", u_id))
        data_list.append(("Contact Name", name))
        data_list.append(("Contact Initials", u_in))
        data_list.append(("Account Type", atype))
        data_list.append(("User since (UTC)", datetime.datetime.fromtimestamp(c_dt + 978307200, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')))
        data_list.append(("Last modified (UTC)", datetime.datetime.fromtimestamp(m_dt + 978307200, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')))
    
    data_headers = ("Property", "Property Value")
    return data_headers, data_list, source_path

@artifact_processor
def get_kleinanzeigensearchhistory(context):
    source_path = get_file_path(context.get_files_found(), 'com.ebaykleinanzeigen.ebc.plist')
    data_list = []

    with open(source_path, 'rb') as ka_in:
        pref = plistlib.load(ka_in)
        s_hist = json.loads(pref['UserDefaultsKit.UserDefaultItem.advertisementSearchDataHistory'])
        for keyword in s_hist['searchedKeywords']:
            k_word = keyword['value']
            k_time = datetime.datetime.fromtimestamp(keyword['timeStamp'] + 978307200, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            data_list.append((k_time, k_word))
    
    data_headers = (("Timestamp", "datetime"), "Keyword")
    return data_headers, data_list, source_path