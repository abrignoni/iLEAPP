__artifacts_v2__ = {
    "keyboardInputContexts": {
        "name": "Keyboard Input Contexts",
        "description": "Keyboard records from UITextInputContextIdentifiers.plist, both the copy in each app "
        "container and the one under mobile/Library/Preferences: the input context "
        "identifier, the keyboard language recorded against it and the recorded time. The "
        "identifier is written by the app, so its form varies: Messenger uses <account "
        "id>_<thread id>_0 and WhatsApp uses the chat's JID. Where the form is known the "
        "chat type (direct or group) and the other party are decoded from it.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-17",
        "last_update_date": "2026-09-19",
        "requirements": "none",
        "category": "User Activity",
        "notes": "An identifier key holds a keyboard language; a <key>_SETTIME key holds a time for it "
        "where one was written, and an identifier without that key is reported with an empty "
        "Recorded value rather than dropped. Identifiers are reported as stored in Input "
        "Context. What the recorded time marks is not established: whether the app writes it "
        "when a conversation is opened or only when the keyboard is used was not tested. "
        "Measured against the Messenger message store on the 4 registered corpora carrying "
        "both a Messenger-shaped identifier and a Messenger mailbox: of 9 such identifiers, 1 "
        "carries no time, and all 8 that do are followed by a message that account sent in "
        "the named thread, 3 to 136 seconds later. That is a measured correlation on those "
        "images, not a general rule. An empty identifier is an app-level context that names "
        "no conversation and is reported as stored. The copy under mobile/Library/Preferences "
        "sits outside any app container, so its rows carry no bundle id or container id; its "
        "identifiers are the CK_ and IM_ forms, which are hashes this artifact does not "
        "resolve to a conversation. Chat Type and Chat Party are decoded from the identifier "
        "form. A WhatsApp identifier is the chat's JID, and its server part sets the type: "
        "s.whatsapp.net is a direct chat and the local part is the phone number, lid is a "
        "direct chat under a linked id that is not a phone number, g.us is a group, "
        "status@broadcast is the status composer, another @broadcast is a broadcast list and "
        "newsletter is a channel. Under a com.facebook.* bundle, an identifier of the form "
        "<account id>_<thread key>_0 is split into Account ID and the thread key, which Chat "
        "Party carries. Messenger keys a one-to-one thread by the other user's id and a group "
        "by an id of its own, so the thread key is looked up in the contacts table of every "
        "msys mailbox on the image: a match is reported as Direct with the contact's name, and "
        "a key that is not a contact but is a thread with 3 or more participants in "
        "thread_participant_detail is reported as Group. A key matching neither is left "
        "undecoded: the thread and the contact may both be gone from the mailbox, and the "
        "identifier itself does not carry the type. The mailbox lookup is pooled across "
        "accounts because a user id is not account-scoped. Messenger also writes a second "
        "form, <account id>_<1 digit>_<4 digits>, seen 3 times across the 2 public Josh "
        "Hickman images (hickman_ios15, iphone11_ios17): its first group is the local account "
        "on every one, and neither of its other parts is a contact id or a thread key, so it "
        "is reported with Account ID only and no Chat Type or Chat Party. The record outlives "
        "the thread: it sits in the app's Preferences, not the message store, so an identifier "
        "with no matching thread is consistent with a thread that has since been deleted. "
        "Measured on hickman_ios15 and iphone11_ios17: every _0 identifier (1 and 2) resolved "
        "to Direct through a contact whose id is also the key of a two-participant thread, and "
        "every WhatsApp identifier (1 and 2) is an s.whatsapp.net JID present as a chat "
        "session in ChatStorage.sqlite. Neither image holds a group thread, so the Group "
        "branch has not been exercised on real data. The threads table also carries a "
        "thread_type column, 1 on the one-to-one threads keyed by a contact and 15 on the "
        "two-participant threads that are not, whose meaning is not established and is not "
        "used.",
        "paths": (
            "*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist",
            "*/Containers/Data/Application/*/Library/Preferences/UITextInputContextIdentifiers.plist",
            "*/mobile/Library/Preferences/UITextInputContextIdentifiers.plist",
            "*/lightspeed-userDatabases/*.db*",
            "*/FBMessagingMailboxCaskStore/*/fb-msys-*.db*",
        ),
        "output_types": "standard",
        "artifact_icon": "keyboard",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 34 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 4 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 3 rows",
            "ctf2020_ios12": "iOS 12.4 | 12 rows",
            "dexter_ios18": "iOS 18.3.2 | 24 rows",
            "falken_ios26": "iOS 26.2.1 | 10 rows",
            "felix23_ios16": "iOS 16.5 | 10 rows",
            "felix_ios17": "iOS 17.6.1 | 12 rows",
            "fsfull002_ios17": "iOS 17.1 | 10 rows",
            "hc_ios18_7": "iOS 18.7.8 | 7 rows",
            "hc_ios26": "iOS 26.5.2 | 10 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 4 rows",
            "hickman_ios13": "iOS 13.3.1 | 11 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 10 rows | 1 Messenger Direct, 1 WhatsApp Direct",
            "iphone11_ios17": "iOS 17.3 | 17 rows | 2 Messenger Direct, 2 WhatsApp Direct",
            "iphone12_ios18": "iOS 18.7 | 4 rows",
            "iphone14plus_ios18": "iOS 18.0 | 3 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 2 rows",
            "jess_ios15": "iOS 15.0.2 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 37 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 0 rows",
        },
    },
}

import os
import re

from scripts.ilapfuncs import (
    artifact_processor,
    convert_plist_date_to_utc,
    does_table_exist_in_db,
    does_view_exist_in_db,
    get_plist_file_content,
    get_sqlite_db_records,
)

CONTAINER_METADATA = ".com.apple.mobile_container_manager.metadata.plist"
CONTEXT_PLIST = "UITextInputContextIdentifiers.plist"
KEY_PREFIX = "ID_"
TIME_SUFFIX = "_SETTIME"

# Messenger writes <account id>_<thread key>_0 for a conversation composer. A second form,
# <account id>_<1 digit>_<4 digits>, names no contact or thread on the images checked, so
# only its account id is read.
MESSENGER_THREAD_CONTEXT = re.compile(r"^(\d+)_(\d+)_0$")
MESSENGER_ACCOUNT_CONTEXT = re.compile(r"^(\d+)_\d+_\d+$")
MESSENGER_BUNDLE_PREFIX = "com.facebook."
MESSENGER_CONTACTS_TABLE = "contacts"
MESSENGER_PARTICIPANTS_VIEW = "thread_participant_detail"
# A one-to-one thread holds the local user and the other party. Anything above that is
# a group; a group left with two members is not distinguishable here and stays undecoded.
GROUP_MIN_PARTICIPANTS = 3

# WhatsApp writes the chat's JID: <local part>@<server>.
WHATSAPP_JID = re.compile(r"^([^@]*)@([a-z.]+)$")
WHATSAPP_SERVER_TYPES = {
    "s.whatsapp.net": "Direct",
    "lid": "Direct (linked id)",
    "g.us": "Group",
    "broadcast": "Broadcast list",
    "newsletter": "Channel",
}


def _container_id(file_found):
    """The Application container UUID: the path segment below Containers/Data/Application.

    Matched as a whole segment. A substring test against the staged absolute path would
    also read the examiner's own folder names.
    """
    parts = os.path.normpath(file_found).split(os.sep)
    for index, part in enumerate(parts):
        if part == "Application" and index >= 2 and parts[index - 1] == "Data" \
                and parts[index - 2] == "Containers" and index + 1 < len(parts):
            return parts[index + 1]
    return ""


def _bundle_ids_by_container(files_found):
    bundle_ids = {}
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.basename(file_found) != CONTAINER_METADATA:
            continue
        plist = get_plist_file_content(file_found)
        if not isinstance(plist, dict):
            continue
        bundle_id = plist.get("MCMMetadataIdentifier")
        container_id = _container_id(file_found)
        if bundle_id and container_id:
            bundle_ids[container_id] = bundle_id
    return bundle_ids


def _messenger_lookups(files_found):
    """Contact names by user id and participant counts by thread key, pooled across every
    msys mailbox on the image. Both are keyed by the id as text, since the plist holds text."""
    contacts = {}
    participant_counts = {}
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith(".db"):
            continue
        if does_table_exist_in_db(file_found, MESSENGER_CONTACTS_TABLE):
            for record in get_sqlite_db_records(
                    file_found, f"SELECT id, name FROM {MESSENGER_CONTACTS_TABLE}"):
                if record[0] is None:
                    continue
                contacts.setdefault(str(record[0]), record[1] or "")
        if does_view_exist_in_db(file_found, MESSENGER_PARTICIPANTS_VIEW):
            for record in get_sqlite_db_records(
                    file_found,
                    f"SELECT thread_key, COUNT(*) FROM {MESSENGER_PARTICIPANTS_VIEW} "
                    "GROUP BY thread_key"):
                if record[0] is None:
                    continue
                key = str(record[0])
                participant_counts[key] = max(participant_counts.get(key, 0), record[1])
    return contacts, participant_counts


def _decode_whatsapp(identifier):
    match = WHATSAPP_JID.match(identifier)
    if not match:
        return "", ""
    local_part, server = match.groups()
    if server == "broadcast" and local_part == "status":
        return "Status", ""
    chat_type = WHATSAPP_SERVER_TYPES.get(server, "")
    if not chat_type:
        return "", ""
    return chat_type, local_part


def _decode_messenger(identifier, contacts, participant_counts):
    match = MESSENGER_THREAD_CONTEXT.match(identifier)
    if not match:
        account = MESSENGER_ACCOUNT_CONTEXT.match(identifier)
        return "", "", account.group(1) if account else ""
    account_id, thread_key = match.groups()
    if thread_key in contacts:
        name = contacts[thread_key]
        party = f"{name} ({thread_key})" if name else thread_key
        return "Direct", party, account_id
    if participant_counts.get(thread_key, 0) >= GROUP_MIN_PARTICIPANTS:
        return "Group", thread_key, account_id
    return "", thread_key, account_id


def _decode(identifier, bundle_id, contacts, participant_counts):
    """(chat type, chat party, account id) for an identifier whose form is known."""
    if bundle_id.startswith(MESSENGER_BUNDLE_PREFIX):
        return _decode_messenger(identifier, contacts, participant_counts)
    chat_type, party = _decode_whatsapp(identifier)
    return chat_type, party, ""


@artifact_processor
def keyboardInputContexts(context):
    files_found = context.get_files_found()
    bundle_ids = _bundle_ids_by_container(files_found)
    contacts, participant_counts = _messenger_lookups(files_found)

    data_list = []
    sources = []

    for file_found in files_found:
        file_found = str(file_found)
        if os.path.basename(file_found) != CONTEXT_PLIST:
            continue
        plist = get_plist_file_content(file_found)
        if not isinstance(plist, dict):
            continue

        container_id = _container_id(file_found)
        bundle_id = bundle_ids.get(container_id, "")
        source_file = context.get_relative_path(file_found)

        # One row per context identifier. The language and the time arrive as two
        # separate keys, so collect both before emitting, and emit an identifier that
        # carries only one of them rather than dropping it.
        languages = {}
        times = {}
        for key, value in plist.items():
            if not key.startswith(KEY_PREFIX):
                continue
            if key.endswith(TIME_SUFFIX):
                times[key[len(KEY_PREFIX):-len(TIME_SUFFIX)]] = value
            else:
                languages[key[len(KEY_PREFIX):]] = value

        for identifier in sorted(set(languages) | set(times)):
            recorded = times.get(identifier)
            if recorded is not None:
                recorded = convert_plist_date_to_utc(recorded)
            language = languages.get(identifier)
            chat_type, chat_party, account_id = _decode(
                identifier, bundle_id, contacts, participant_counts)
            data_list.append((
                recorded if recorded is not None else "",
                bundle_id,
                identifier,
                chat_type,
                chat_party,
                account_id,
                language if language is not None else "",
                container_id,
                source_file,
            ))

        if source_file not in sources:
            sources.append(source_file)

    data_headers = (
        ("Recorded", "datetime"),
        "App Bundle ID",
        "Input Context",
        "Chat Type",
        "Chat Party",
        "Account ID",
        "Keyboard Language",
        "App Container ID",
        "Source File",
    )

    return data_headers, data_list, "\n".join(sources)
