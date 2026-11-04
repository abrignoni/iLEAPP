__artifacts_v2__ = {
    "chatgptConversationsMetadata": {
        "name": "ChatGPT - Conversations Metadata",
        "description": "Metadata from ChatGPT conversation files. Returned rows on ChatGPT "
                       "1.2023.159, 1.2023.347, 1.2024.219, 1.2024.233 and 1.2026.013 on the "
                       "tested images. 1.2025.261 (dexter_ios18) was run and held no "
                       "conversation files; other versions were not tested.",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-14",
        "last_update_date": "2026-10-29",
        "requirements": "none",
        "category": "ChatGPT",
        "notes": "Conversation files are read from three folders under Library/Application "
                 "Support in the app container: conversations-<id> (ChatGPT 1.2023.347 to "
                 "1.2024.233 on the tested images), conversations-v3-<id> (1.2026.013) and "
                 "conversations (1.2023.159). Any app could use a folder named conversations, so "
                 "that folder is read only from a container that also holds "
                 "Library/Preferences/com.openai.chat.plist or com.openai.chat.StatsigService.plist. "
                 "Model, Default Model and Last Model are the configuration keys model, "
                 "default_model and last_model as stored. Which of them a file carries varied by "
                 "app version and between files of one image, each is blank where the file does "
                 "not store it, and what "
                 "distinguishes them is not documented here. Custom Instructions (Model) and "
                 "Custom Instructions (User) are blank on every row of every tested image: the "
                 "file stores an empty string on 12 files (adams_iphone12mini 10, "
                 "hexordia_ios1651 1, otto_ios17 1) and does not carry the key on the other 44. "
                 "Custom Instructions (Enabled) and Is Temporary are blank where the file "
                 "does not store the key, and Is Temporary held False on every row that stored it. "
                 "Other configuration keys, such as gizmo_id and customizations on 1.2024.219, "
                 "are not reported. dexter_ios18 and falken_ios26 hold the ChatGPT app container "
                 "but no conversation files.",
        "paths": ('**/Containers/Data/Application/*/Library/Application Support/conversations-*/*.json',
                  '**/Containers/Data/Application/*/Library/Application Support/conversations/*.json',
                  '**/Containers/Data/Application/*/Library/Preferences/com.openai.chat.plist',
                  '**/Containers/Data/Application/*/Library/Preferences/com.openai.chat.StatsigService.plist'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | ChatGPT 1.2023.159 | 5 rows",
            "adams_iphone12mini": "iOS 17.1.1 | ChatGPT 1.2026.013 | 10 rows",
            "dexter_ios18": "iOS 18.3.2 | ChatGPT 1.2025.261 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | ChatGPT 1.2026.013 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | ChatGPT 1.2024.233 | 16 rows",
            "hexordia_ios1651": "iOS 16.5.1 | ChatGPT 1.2023.347 | 3 rows",
            "otto_ios17": "iOS 17.5.1 | ChatGPT 1.2024.219 | 22 rows",
        }
    },
    "chatgptConversations": {
        "name": "ChatGPT - Conversations",
        "description": "Messages stored in ChatGPT conversation files, one row per "
                       "entry of the file's message tree, with the author role as "
                       "stored. Returned rows on ChatGPT "
                       "1.2023.159, 1.2023.347, 1.2024.219, 1.2024.233 and 1.2026.013 on the "
                       "tested images. 1.2025.261 (dexter_ios18) was run and held no "
                       "conversation files; other versions were not tested.",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-14",
        "last_update_date": "2026-10-29",
        "requirements": "none",
        "category": "ChatGPT",
        "notes": "One row per node of the conversation's message tree, read from the same "
                 "folders and with the same container check as ChatGPT - Conversations Metadata. "
                 "Older files store the tree as a dictionary and Message ID is the dictionary key. "
                 "On felix_ios17 (9 of 150 rows) and otto_ios17 (27 of 172) that key differs from "
                 "the node's own id field, which is not reported. conversations-v3 files store a "
                 "list alternating the message id and its node; both layouts are read. Creation "
                 "Time is the node's create_time, read as Unix seconds and shown to the whole "
                 "second; the stored fraction is dropped. Rows with no create_time are kept with a "
                 "blank time: 46 of 179 on adams_iphone12mini (25 tool, 19 system, 2 assistant), "
                 "20 of 172 on otto_ios17, 8 of 150 on felix_ios17 and 2 of 17 on "
                 "hexordia_ios1651, those three all system entries. Content Type is the message "
                 "content's content_type, and held text on all 21 rows of abe_ios16. Voice Mode "
                 "Message is the metadata key voice_mode_message as stored. It was stored only on "
                 "otto_ios17, True on 12 of 172 rows, and is blank where the key is absent. Media: "
                 "rows whose Content Type is multimodal_text (30 on adams_iphone12mini, 7 on "
                 "felix_ios17) carry an asset pointer, reported in Parts as the text form of the "
                 "stored part. No file in the ChatGPT app container on either image is named by "
                 "those asset ids, and no other recorded link from a part to a local file was "
                 "found, so no image is shown.",
        "paths": ('**/Containers/Data/Application/*/Library/Application Support/conversations-*/*.json',
                  '**/Containers/Data/Application/*/Library/Application Support/conversations/*.json',
                  '**/Containers/Data/Application/*/Library/Preferences/com.openai.chat.plist',
                  '**/Containers/Data/Application/*/Library/Preferences/com.openai.chat.StatsigService.plist'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | ChatGPT 1.2023.159 | 21 rows",
            "adams_iphone12mini": "iOS 17.1.1 | ChatGPT 1.2026.013 | 179 rows",
            "dexter_ios18": "iOS 18.3.2 | ChatGPT 1.2025.261 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | ChatGPT 1.2026.013 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | ChatGPT 1.2024.233 | 150 rows",
            "hexordia_ios1651": "iOS 16.5.1 | ChatGPT 1.2023.347 | 17 rows",
            "otto_ios17": "iOS 17.5.1 | ChatGPT 1.2024.219 | 172 rows",
        }
    },
    "chatgptDraftConversations": {
        "name": "ChatGPT - Draft Conversations",
        "description": "Text held in the ChatGPT drafts-* JSON files, with the conversation id "
                       "stored beside it. No tested image is recorded as returning rows.",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-14",
        "last_update_date": "2026-08-21",
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
        "last_update_date": "2026-08-21",
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
        "description": ".png files matched under the tmp directory of the ChatGPT app container, "
                       "when com.openai.chat.plist or com.openai.chat.StatsigService.plist "
                       "identifies that container",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-14",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "ChatGPT",
        "notes": "The tmp patterns match every app container. A container is taken as ChatGPT's "
                 "only when Library/Preferences/com.openai.chat.plist or "
                 "com.openai.chat.StatsigService.plist sits in it, and rows come only from that "
                 "container. With neither file, nothing is reported. In sample_data the four "
                 "images that hold ChatGPT have no .png in its tmp folder and returned 0 rows, so "
                 "no row has been produced from a real image; the row path is exercised by a "
                 "unit test on constructed paths and by a run over a hand-built folder, not by "
                 "any corpus image. Only .png files are reported. A row is not "
                 "evidence that a file was uploaded to ChatGPT.",
        "paths": ('**/Containers/Data/Application/*/tmp/photo-*.png',
                  '**/Containers/Data/Application/*/tmp/*/*.png',
                  '**/Containers/Data/Application/*/Library/Preferences/com.openai.chat.plist',
                  '**/Containers/Data/Application/*/Library/Preferences/com.openai.chat.StatsigService.plist'),
        "output_types": ["html","lava","tsv"],
        "artifact_icon": "photo",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | ChatGPT 1.2025.261 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | ChatGPT 1.2024.233 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | no ChatGPT preference file | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | no ChatGPT preference file | 0 rows",
            "iphone11_ios17": "iOS 17.3 | no ChatGPT preference file | 0 rows",
            "otto_ios17": "iOS 17.5.1 | ChatGPT 1.2024.219 | 0 rows",
            "abe_ios16": "iOS 16.5 | ChatGPT 1.2023.159 | 0 rows",
            "felix23_ios16": "iOS 16.5 | no ChatGPT preference file | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | no ChatGPT preference file | 0 rows",
        }
    },
    "chatgptVoicePrompts": {
        "name": "ChatGPT - Voice Prompts",
        "description": ".m4a files matched under the tmp directory of the ChatGPT app container, "
                       "when com.openai.chat.plist or com.openai.chat.StatsigService.plist "
                       "identifies that container",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-14",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "ChatGPT",
        "notes": "The tmp patterns match every app container. A container is taken as ChatGPT's "
                 "only when Library/Preferences/com.openai.chat.plist or "
                 "com.openai.chat.StatsigService.plist sits in it, and rows come only from that "
                 "container. With neither file, nothing is reported. In sample_data the four "
                 "images that hold ChatGPT have no .m4a in its tmp folder and returned 0 rows, so "
                 "no row has been produced from a real image; the row path is exercised by a "
                 "unit test on constructed paths and by a run over a hand-built folder, not by "
                 "any corpus image. A row is an .m4a file under the ChatGPT tmp "
                 "folder and is not shown to be a voice prompt.",
        "paths": ('**/Containers/Data/Application/*/tmp/recordings/*.m4a',
                  '**/Containers/Data/Application/*/tmp/*/*.m4a',
                  '**/Containers/Data/Application/*/Library/Preferences/com.openai.chat.plist',
                  '**/Containers/Data/Application/*/Library/Preferences/com.openai.chat.StatsigService.plist'),
        "output_types": "standard",
        "artifact_icon": "microphone",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | ChatGPT 1.2023.159 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | ChatGPT 1.2025.261 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | ChatGPT 1.2024.233 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | no ChatGPT preference file | 0 rows",
            "otto_ios17": "iOS 17.5.1 | ChatGPT 1.2024.219 | 0 rows",
        }
    }
}

import json
import os
import re

import plistlib
from xml.parsers.expat import ExpatError

from scripts.ilapfuncs import (artifact_processor, check_in_media, convert_ts_int_to_utc,
                               logfunc, webkit_timestampsconv)

_JSON_ERRORS = (json.JSONDecodeError, KeyError, ValueError, TypeError, AttributeError, OSError)
# plistlib.InvalidFileException is a ValueError; a malformed XML plist raises ExpatError.
_PLIST_ERRORS = (plistlib.InvalidFileException, ExpatError, OSError, ValueError, OverflowError)

_CONTAINER = re.compile(r'(?:^|[\\/])Containers[\\/]Data[\\/]Application[\\/]([^\\/]+)[\\/](.+)$')
# Preference files named for ChatGPT's bundle id. Only its own container holds them.
_MARKERS = ('Library/Preferences/com.openai.chat.plist',
            'Library/Preferences/com.openai.chat.StatsigService.plist')
# conversations-<id>/ and conversations-v3-<id>/ name the folder after ChatGPT's own ids. The
# 2023 app kept a plain conversations/ folder, a name any app could use, so that one is read
# only from a container a marker identifies.
_CONVERSATION_FILE = re.compile(r'^Library/Application Support/conversations-[^/]+/[^/]+\.json$')
_LEGACY_CONVERSATION_FILE = re.compile(r'^Library/Application Support/conversations/[^/]+\.json$')


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


def _container_path(context, file_found):
    """Split a found file into (app container directory name, path inside that container).

    Works on the evidence-relative path, so the folder the report was written to is never
    read as part of the evidence.
    """
    match = _CONTAINER.search(context.get_relative_path(str(file_found)) or '')
    if not match:
        return '', ''
    return match.group(1), match.group(2).replace('\\', '/')


def _chatgpt_containers(context):
    """Return the app containers that hold a com.openai.chat preference file."""
    containers = set()
    for file_found in context.get_files_found():
        container, inner = _container_path(context, file_found)
        if inner in _MARKERS:
            containers.add(container)
    return containers


def _conversation_files(context):
    """Return the conversation JSON files, each once, the legacy folder only from ChatGPT's container."""
    containers = None
    files = []
    for file_found in dict.fromkeys(str(found) for found in context.get_files_found()):
        container, inner = _container_path(context, file_found)
        if _CONVERSATION_FILE.match(inner):
            files.append(file_found)
        elif _LEGACY_CONVERSATION_FILE.match(inner):
            if containers is None:
                containers = _chatgpt_containers(context)
            if container in containers:
                files.append(file_found)
    return files


def _tree_nodes(storage):
    """Yield (message id, node) from a conversation tree.

    Older files keep the nodes in a dict keyed by message id. conversations-v3 files keep a
    list alternating the message id and its node.
    """
    if isinstance(storage, dict):
        yield from storage.items()
    elif isinstance(storage, list):
        for index, node in enumerate(storage):
            if isinstance(node, dict):
                previous = storage[index - 1] if index else None
                yield (previous if isinstance(previous, str) else node.get('id', '')), node


@artifact_processor
def chatgptConversationsMetadata(context):
    data_headers = (
        ('Creation Time', 'datetime'), ('Modification Date', 'datetime'), 'Title', 'Conversation ID',
        'Model', 'Default Model', 'Last Model', 'Custom Instructions (Model)',
        'Custom Instructions (User)', 'Custom Instructions (Enabled)', 'Is Temporary', 'File Path')
    data_list = []
    sources = []

    for file_found in _conversation_files(context):
        try:
            with open(file_found, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            config = data.get('configuration', {})
            ci = config.get('custom_instructions', {})
            data_list.append((
                _webkit(data.get('creation_date', 0)), _webkit(data.get('modification_date', 0)),
                data.get('title', ''), data.get('id', ''), config.get('model', ''),
                config.get('default_model', ''), config.get('last_model', ''),
                ci.get('about_model_message', ''), ci.get('about_user_message', ''),
                ci.get('active', ''), config.get('is_temporary_chat', ''),
                context.get_relative_path(file_found)))
            sources.append(context.get_relative_path(file_found))
        except _JSON_ERRORS:
            logfunc(f'Error parsing ChatGPT conversation metadata from -> {file_found}')

    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def chatgptConversations(context):
    data_headers = (
        ('Creation Time', 'datetime'), 'Message ID', 'Conversation Title', 'Conversation ID',
        'Author', 'Parts', 'Content Type', 'Finish Details', 'Voice Mode Message', 'Metadata',
        'File Path')
    data_list = []
    sources = []

    for file_found in _conversation_files(context):
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
        if not isinstance(storage, (dict, list)):
            logfunc(f'ChatGPT conversation tree not read, unrecognised layout -> {file_found}')
            continue
        rel = context.get_relative_path(file_found)
        for message_id, message_details in _tree_nodes(storage):
            content = message_details.get('content', {})
            author = content.get('author', {}).get('role', '')
            body = content.get('content', {})
            parts = body.get('parts', [''])
            parts = '\n'.join(str(p) for p in parts) if isinstance(parts, list) else str(parts)
            metadata = content.get('metadata', {})
            data_list.append((
                _unix(content.get('create_time')), message_id, title, conv_id, author, parts,
                body.get('content_type', ''), metadata.get('finish_details', {}).get('type', ''),
                metadata.get('voice_mode_message', ''), str(metadata), rel))
        sources.append(rel)

    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


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

    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


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
                    plist_data = plistlib.load(fh)
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
                    plist_data = plistlib.load(fh)
            except _PLIST_ERRORS as ex:
                logfunc(f'Error parsing ChatGPT account from -> {file_found}: {ex}')
                continue
            traits = {}
            traits_raw = plist_data.get('segment.traits')
            if traits_raw:
                try:
                    traits = plistlib.loads(traits_raw)
                except (*_PLIST_ERRORS, TypeError) as ex:
                    logfunc(f'Error parsing ChatGPT nested plist from {file_found}: {ex}')
            data_list.append(('', plist_data.get('segment.userId', ''), '',
                              traits.get('plan_type', ''), traits.get('has_paid_plan', ''),
                              traits.get('workspace_id', ''), traits.get('device_id', ''),
                              plist_data.get('segment.events', '')))
            sources.append(context.get_relative_path(file_found))

    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


def _checkin_tmp_media(context, extension):
    """Check in tmp media of a given extension belonging to the ChatGPT app container.

    The tmp patterns match every app container. Without a preference file naming the
    ChatGPT container, the matched files are some other app's (#1732 reported
    Voice Memos recordings here), so nothing is reported.
    """
    containers = _chatgpt_containers(context)
    data_list = []
    source_dirs = set()
    if not containers:
        return data_list, ''
    # A file matched by two of the patterns is listed twice.
    for file_found in dict.fromkeys(str(found) for found in context.get_files_found()):
        container, inner = _container_path(context, file_found)
        if container not in containers:
            continue
        if not (inner.startswith('tmp/') and inner.endswith(extension)):
            continue
        media_ref = check_in_media(file_found, os.path.basename(file_found))
        source_dirs.add(os.path.dirname(file_found))
        data_list.append((media_ref, os.path.basename(file_found),
                          context.get_relative_path(file_found)))
    return data_list, '\n'.join(sorted(source_dirs))


@artifact_processor
def chatgptMediaUploads(context):
    data_headers = (('Media', 'media'), 'File Name', 'File Path')
    data_list, source_path = _checkin_tmp_media(context, '.png')
    return data_headers, data_list, source_path


@artifact_processor
def chatgptVoicePrompts(context):
    data_headers = (('Audio', 'media'), 'File Name', 'File Path')
    data_list, source_path = _checkin_tmp_media(context, '.m4a')
    return data_headers, data_list, source_path
