__artifacts_v2__ = {
    "get_kleinanzeigenuser": {
        "name": "Kleinanzeigen.de - User Account",
        "description": "Extracts Information about the Kleinanzeigen User Account",
        "author": "@C_Peter",
        "creation_date": "2025-02-19",
        "last_update_date": "2025-02-19",
        "requirements": "none",
        "category": "Kleinanzeigen.de",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Preferences/com.ebaykleinanzeigen.ebc.plist', ),
        "output_types": "standard",
        "artifact_icon": "user"
    },
    "get_kleinanzeigenmessagecache": {
        "name": "Kleinanzeigen.de - Message Cache",
        "description": "Extracts cached Messages",
        "author": "@C_Peter",
        "creation_date": "2025-02-18",
        "last_update_date": "2025-02-19",
        "requirements": "none",
        "category": "Kleinanzeigen.de",
        "notes": "",
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
        "description": "Extracts searched Keywords",
        "author": "@C_Peter",
        "creation_date": "2025-02-19",
        "last_update_date": "2025-02-19",
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
        "output_types": "standard",
        "artifact_icon": "search"
    }
}

import json
import plistlib
import datetime

from ileapp.scripts.ilapfuncs import artifact_processor, get_file_path

@artifact_processor
def get_kleinanzeigenmessagecache(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    source_path = get_file_path(files_found, 'conversation_cache')
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
                m_rec = datetime.datetime.fromtimestamp(elem['clientData']['receivedDate'] + 978307200).strftime('%Y-%m-%d %H:%M:%S')
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
                data_list.append((m_rec, conv_id, conv_name, ad_id, m_from, id_from, m_to, id_to, m_text, m_att, m_id, ad_stat, out))

            except (KeyError, TypeError, ValueError, OverflowError, OSError, NameError):
                pass
        else:
            for message in elem['messages']:
                m_id = message['messageId']
                # Original timestamp is cocoa time - so 978307200 will be added
                m_rec = datetime.datetime.fromtimestamp(message['sentDate'] + 978307200).strftime('%Y-%m-%d %H:%M:%S')
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
                data_list.append((m_rec, conv_id, conv_name, ad_id, m_from, id_from, m_to, id_to, m_text, m_att, m_id, ad_stat, out))

    data_headers = (
        ('Timestamp', 'datetime'), "Conversation-ID", "Advertisement", "Ad-ID",
        "From_Name", "From_ID", "To_Name", "To_ID", "Message", "Attachment", "Message_ID", "AD-Status", "From Me")
    return data_headers, data_list, source_path

@artifact_processor
def get_kleinanzeigenlastquery(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    source_path = get_file_path(files_found, '.last_search_query')
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
def get_kleinanzeigenuser(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    source_path = get_file_path(files_found, 'com.ebaykleinanzeigen.ebc.plist')
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
        data_list.append(("User since", datetime.datetime.fromtimestamp(c_dt + 978307200).strftime('%Y-%m-%d %H:%M:%S')))
        data_list.append(("Last modified", datetime.datetime.fromtimestamp(m_dt + 978307200).strftime('%Y-%m-%d %H:%M:%S')))
    
    data_headers = ("Property", "Property Value")
    return data_headers, data_list, source_path

@artifact_processor
def get_kleinanzeigensearchhistory(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    source_path = get_file_path(files_found, 'com.ebaykleinanzeigen.ebc.plist')
    data_list = []

    with open(source_path, 'rb') as ka_in:
        pref = plistlib.load(ka_in)
        s_hist = json.loads(pref['UserDefaultsKit.UserDefaultItem.advertisementSearchDataHistory'])
        for keyword in s_hist['searchedKeywords']:
            k_word = keyword['value']
            k_time = datetime.datetime.fromtimestamp(keyword['timeStamp'] + 978307200).strftime('%Y-%m-%d %H:%M:%S')
            data_list.append((k_word, k_time))
    
    data_headers = ("Keyword", "Timestamp")
    return data_headers, data_list, source_path