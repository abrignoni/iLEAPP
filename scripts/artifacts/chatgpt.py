__artifacts_v2__ = {
    "chatgptConversationsMetadata": {
        "name": "ChatGPT - Conversations Metadata",
        "description": "Metadata from ChatGPT conversations. Based on a research project; "
                       "validated up to the app's 1.2024.178 version.",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-14",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "ChatGPT",
        "notes": "",
        "paths": ('**/Containers/Data/Application/*/Library/Application Support/conversations-*/*.json',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "felix_ios17": "iOS 17.6.1 | ChatGPT 1.2024.233 | 16 rows",
            "otto_ios17": "iOS 17.5.1 | ChatGPT 1.2024.219 | 22 rows",
        }
    },
    "chatgptConversations": {
        "name": "ChatGPT - Conversations",
        "description": "User conversations with ChatGPT. Based on a research project; "
                       "validated up to the app's 1.2024.178 version.",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-14",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "ChatGPT",
        "notes": "",
        "paths": ('**/Containers/Data/Application/*/Library/Application Support/conversations-*/*.json',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "felix_ios17": "iOS 17.6.1 | ChatGPT 1.2024.233 | 150 rows",
            "otto_ios17": "iOS 17.5.1 | ChatGPT 1.2024.219 | 172 rows",
        }
    },
    "chatgptDraftConversations": {
        "name": "ChatGPT - Draft Conversations",
        "description": "User draft conversations with ChatGPT.",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-14",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "ChatGPT",
        "notes": "",
        "paths": ('**/Containers/Data/Application/*/Library/Application Support/drafts-*/*.json',),
        "output_types": "standard",
        "artifact_icon": "pencil-minus"
    },
    "chatgptPreferences": {
        "name": "ChatGPT - Preferences",
        "description": "ChatGPT preferences (account information).",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-14",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "ChatGPT",
        "notes": "",
        "paths": ('**/Containers/Data/Application/*/Library/Preferences/com.openai.chat.StatsigService.plist',
                  '**/Containers/Data/Application/*/Library/Preferences/com.segment.storage.oai.plist'),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | ChatGPT 1.2025.261 | 2 rows",
            "felix_ios17": "iOS 17.6.1 | ChatGPT 1.2024.233 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | ChatGPT 1.2024.219 | 2 rows",
        }
    },
    "chatgptMediaUploads": {
        "name": "ChatGPT - Media Uploads",
        "description": "Images uploaded to ChatGPT.",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-14",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "ChatGPT",
        "notes": "",
        "paths": ('**/Containers/Data/Application/*/tmp/photo-*.png',
                  '**/Containers/Data/Application/*/tmp/*/*.png',
                  '**/Containers/Data/Application/*/Library/Application Support/conversations-*/*.json',
                  '**/Containers/Data/Application/*/Library/Preferences/com.openai.chat.StatsigService.plist'),
        "output_types": "standard",
        "artifact_icon": "photo",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | ChatGPT 1.2025.261 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | ChatGPT 1.2024.233 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Text Me - Phone Call + Texting 3.35.9 | 2 rows",
            "hc_ios18_7": "iOS 18.7.8 | Kik Messaging & Chat App 17.11.3 | 1 row",
            "iphone11_ios17": "iOS 17.3 | Kik Messaging & Chat App 16.16.1, Imgur: Funny Memes & GIF Maker 2023.23.1, WhatsApp Messenger 24.15.1 | 6 rows",
            "otto_ios17": "iOS 17.5.1 | ChatGPT 1.2024.219 | 0 rows",
        }
    },
    "chatgptVoicePrompts": {
        "name": "ChatGPT - Voice Prompts",
        "description": "Voice prompts that were transcribed and uploaded to ChatGPT.",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-14",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "ChatGPT",
        "notes": "",
        "paths": ('**/Containers/Data/Application/*/tmp/recordings/*.m4a',
                  '**/Containers/Data/Application/*/tmp/*/*.m4a',
                  '**/Containers/Data/Application/*/Library/Application Support/conversations-*/*.json',
                  '**/Containers/Data/Application/*/Library/Preferences/com.openai.chat.StatsigService.plist'),
        "output_types": "standard",
        "artifact_icon": "microphone",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | ChatGPT 1.2025.261 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | ChatGPT 1.2024.233 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | Wire • Secure Messenger 4.10.0 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | ChatGPT 1.2024.219 | 0 rows",
        }
    }
}

import json
import os

import biplist

from scripts.ilapfuncs import (artifact_processor, check_in_media, convert_ts_int_to_utc,
                               logfunc, webkit_timestampsconv)

_JSON_ERRORS = (json.JSONDecodeError, KeyError, ValueError, TypeError, AttributeError, OSError)
_PLIST_ERRORS = (biplist.InvalidPlistException, biplist.NotBinaryPlistException, OSError, ValueError)


def _webkit(value):
    if not value:
        return ''
    try:
        return webkit_timestampsconv(int(value))
    except (ValueError, TypeError):
        return ''


def _unix(value):
    if not value:
        return ''
    try:
        return convert_ts_int_to_utc(int(value))
    except (ValueError, TypeError):
        return ''


def _app_id(context):
    """Identify the ChatGPT app container GUID from a conversations/openai marker file."""
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if 'conversations-' in file_found or 'com.openai.chat' in file_found:
            parts = file_found.split(os.sep)
            for i in range(len(parts) - 1):
                if parts[i] == 'Application':
                    return parts[i + 1]
    return ''


@artifact_processor
def chatgptConversationsMetadata(context):
    data_headers = (
        ('Creation Time', 'datetime'), ('Modification Date', 'datetime'), 'Title', 'Conversation ID',
        'Model', 'Custom Instructions (Model)', 'Custom Instructions (User)',
        'Custom Instructions (Enabled)', 'Is Temporary', 'File Path')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not (file_found.endswith('.json') and 'conversations-' in file_found):
            continue
        try:
            with open(file_found, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            config = data.get('configuration', {})
            ci = config.get('custom_instructions', {})
            data_list.append((
                _webkit(data.get('creation_date', 0)), _webkit(data.get('modification_date', 0)),
                data.get('title', ''), data.get('id', ''), config.get('model', ''),
                ci.get('about_model_message', ''), ci.get('about_user_message', ''),
                ci.get('active', False), config.get('is_temporary_chat', False),
                context.get_relative_path(file_found)))
            sources.append(context.get_relative_path(file_found))
        except _JSON_ERRORS:
            logfunc(f'Error parsing ChatGPT conversation metadata from -> {file_found}')

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))


@artifact_processor
def chatgptConversations(context):
    data_headers = (
        ('Creation Time', 'datetime'), 'Message ID', 'Conversation Title', 'Conversation ID',
        'Author', 'Parts', 'Content Type', 'Finish Details', 'Voice Mode Message', 'Metadata',
        'File Path')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not (file_found.endswith('.json') and 'conversations-' in file_found):
            continue
        try:
            with open(file_found, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
        except _JSON_ERRORS:
            logfunc(f'Error parsing ChatGPT conversation from -> {file_found}')
            continue

        title = data.get('title', '')
        conv_id = data.get('id', '')
        tree = data.get('tree', {})
        storage = tree.get('storage', {}) if isinstance(tree, dict) else {}
        if not isinstance(storage, dict):
            continue
        rel = context.get_relative_path(file_found)
        for message_id, message_details in storage.items():
            content = message_details.get('content', {})
            author = content.get('author', {}).get('role', '')
            parts = content.get('content', {}).get('parts', [''])
            parts = '\n'.join(str(p) for p in parts) if isinstance(parts, list) else str(parts)
            metadata = content.get('metadata', {})
            data_list.append((
                _unix(content.get('create_time')), message_id, title, conv_id, author, parts,
                content.get('content_type', ''), metadata.get('finish_details', {}).get('type', ''),
                metadata.get('voice_mode_message', False), str(metadata), rel))
        sources.append(rel)

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))


@artifact_processor
def chatgptDraftConversations(context):
    data_headers = ('Conversation ID', 'Content', 'File Path')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not (file_found.endswith('.json') and 'drafts-' in file_found):
            continue
        try:
            with open(file_found, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            data_list.append((data.get('conversation_id', ''),
                              data.get('content', {}).get('text', ''),
                              context.get_relative_path(file_found)))
            sources.append(context.get_relative_path(file_found))
        except _JSON_ERRORS:
            logfunc(f'Error parsing ChatGPT draft messages from -> {file_found}')

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))


@artifact_processor
def chatgptPreferences(context):
    data_headers = ('Account ID', 'User ID', 'Email', 'Plan Type', 'Paid Plan', 'Workspace ID',
                    'Device ID', 'Segments Events')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        name = os.path.basename(file_found)

        if name.endswith('com.openai.chat.StatsigService.plist'):
            try:
                with open(file_found, 'rb') as fh:
                    plist_data = biplist.readPlist(fh)
            except _PLIST_ERRORS as ex:
                logfunc(f'Error parsing ChatGPT preferences from -> {file_found}: {ex}')
                continue
            data_list.append((plist_data.get('accountID', ''), plist_data.get('userID', ''),
                              plist_data.get('userEmail', ''), plist_data.get('planType', ''),
                              '', '', '', ''))
            sources.append(context.get_relative_path(file_found))

        elif name.endswith('com.segment.storage.oai.plist'):
            try:
                with open(file_found, 'rb') as fh:
                    plist_data = biplist.readPlist(fh)
            except _PLIST_ERRORS as ex:
                logfunc(f'Error parsing ChatGPT account from -> {file_found}: {ex}')
                continue
            traits = {}
            traits_raw = plist_data.get('segment.traits')
            if traits_raw:
                try:
                    traits = biplist.readPlistFromString(traits_raw)
                except biplist.InvalidPlistException as ex:
                    logfunc(f'Error parsing ChatGPT nested plist from {file_found}: {ex}')
            data_list.append(('', plist_data.get('segment.userId', ''), '',
                              traits.get('plan_type', ''), traits.get('has_paid_plan', ''),
                              traits.get('workspace_id', ''), traits.get('device_id', ''),
                              plist_data.get('segment.events', '')))
            sources.append(context.get_relative_path(file_found))

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))


def _checkin_tmp_media(context, extension):
    """Check in tmp media of a given extension belonging to the ChatGPT app container."""
    app_id = _app_id(context)
    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not (file_found.endswith(extension) and 'tmp' in file_found):
            continue
        if app_id and app_id not in file_found:
            continue
        media_ref = check_in_media(file_found, os.path.basename(file_found))
        data_list.append((media_ref, os.path.basename(file_found),
                          context.get_relative_path(file_found)))
    return data_list


@artifact_processor
def chatgptMediaUploads(context):
    data_headers = (('Media', 'media'), 'File Name', 'File Path')
    return data_headers, _checkin_tmp_media(context, '.png'), ''


@artifact_processor
def chatgptVoicePrompts(context):
    data_headers = (('Voice Prompt', 'media'), 'File Name', 'File Path')
    return data_headers, _checkin_tmp_media(context, '.m4a'), ''
