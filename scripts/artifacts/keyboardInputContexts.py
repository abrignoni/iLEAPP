__artifacts_v2__ = {
    "keyboardInputContexts": {
        "name": "Keyboard Input Contexts",
        "description": "Keyboard records from UITextInputContextIdentifiers.plist, both the copy in each app "
        "container and the one under mobile/Library/Preferences: the input context "
        "identifier, the keyboard language recorded against it and the recorded time. The "
        "identifier is written by the app, so its form varies: Messenger uses <account "
        "id>_<thread id>_0 and WhatsApp uses the chat's JID.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-17",
        "last_update_date": "2026-09-17",
        "requirements": "none",
        "category": "User Activity",
        "notes": "An identifier key holds a keyboard language; a <key>_SETTIME key holds a time for it "
        "where one was written, and an identifier without that key is reported with an empty "
        "Recorded value rather than dropped. Identifiers are reported as stored and are not "
        "decoded into participants. What the recorded time marks is not established: whether "
        "the app writes it when a conversation is opened or only when the keyboard is used "
        "was not tested. Measured against the Messenger message store on the 4 registered "
        "corpora carrying both a Messenger-shaped identifier and a Messenger mailbox: of 9 "
        "such identifiers, 1 carries no time, and all 8 that do are followed by a message "
        "that account sent in the named thread, 3 to 136 seconds later. That is a measured "
        "correlation on those images, not a general rule. An empty identifier is an app-level "
        "context that names no conversation and is reported as stored. The copy under "
        "mobile/Library/Preferences sits outside any app container, so its rows carry no "
        "bundle id or container id; its identifiers are the CK_ and IM_ forms, which are "
        "hashes this artifact does not resolve to a conversation.",
        "paths": (
            "*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist",
            "*/Containers/Data/Application/*/Library/Preferences/UITextInputContextIdentifiers.plist",
            "*/mobile/Library/Preferences/UITextInputContextIdentifiers.plist",
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
            "hickman_ios15": "iOS 15.3.1 | 10 rows",
            "iphone11_ios17": "iOS 17.3 | 17 rows",
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

from scripts.ilapfuncs import (
    artifact_processor,
    convert_plist_date_to_utc,
    get_plist_file_content,
)

CONTAINER_METADATA = ".com.apple.mobile_container_manager.metadata.plist"
CONTEXT_PLIST = "UITextInputContextIdentifiers.plist"
KEY_PREFIX = "ID_"
TIME_SUFFIX = "_SETTIME"


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


@artifact_processor
def keyboardInputContexts(context):
    files_found = context.get_files_found()
    bundle_ids = _bundle_ids_by_container(files_found)

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
            data_list.append((
                recorded if recorded is not None else "",
                bundle_id,
                identifier,
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
        "Keyboard Language",
        "App Container ID",
        "Source File",
    )

    return data_headers, data_list, "\n".join(sources)
