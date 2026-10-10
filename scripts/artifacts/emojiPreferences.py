""" Emoji keyboard preferences: com.apple.EmojiPreferences.plist """
__artifacts_v2__ = {
    "emojiRecents": {
        "name": "Emoji Recents and Usage",
        "description": "One row per emoji named in the recents list or the usage history of "
                       "com.apple.EmojiPreferences.plist, with its position in the recents list "
                       "and the use sequence numbers recorded for it, as stored.",
        "author": "@ayobamiseun, Claude",
        "creation_date": "2026-10-10",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "User Activity",
        "notes": "The file holds no timestamps. EMFRecentsKey is a list of emoji strings and "
                 "Recents Rank is the 1-based position in it. EMFUsageHistoryKey maps an emoji to "
                 "a list of integers and EMFRecentSequenceNumberKey holds one integer; on the one "
                 "instance examined, written by macOS 26, the integers across all lists were "
                 "distinct, ran from 0 to one below the sequence number, and each list was "
                 "ascending, so Uses Recorded is the length of the list and First and Last Use "
                 "Sequence are its ends, reported as stored. What a sequence number counts, and "
                 "whether the history is capped, is not established. The key names are those "
                 "the EmojiFoundation framework carries; the iOS file was not examined here, and "
                 "the artifact was exercised on the macOS instance and on constructed data only. "
                 "An iOS instance exists on every recorded path listing "
                 "(admin/data/filepath-lists) at private/var/mobile/Library/Preferences/. "
                 "Suggested in issue #1876.",
        "paths": ('*/mobile/Library/Preferences/com.apple.EmojiPreferences.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "smile",
    },
    "emojiPreferenceKeys": {
        "name": "Emoji Preferences",
        "description": "The keys of com.apple.EmojiPreferences.plist other than the recents list "
                       "and usage history, flattened to one row per stored value with its key "
                       "path, as stored.",
        "author": "@ayobamiseun, Claude",
        "creation_date": "2026-10-10",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "User Activity",
        "notes": "The recents list and usage history are reported by Emoji Recents and Usage and "
                 "left out here. Nested dictionaries are flattened as parent.key and lists as "
                 "parent[index], so a skin tone choice under EMFSkinToneBaseKey or a sticker id "
                 "under com.apple.stickers.recency.order is one row each. Other key names the "
                 "EmojiFoundation framework carries (EMFSkinToneBaseKey, "
                 "EMFDidDisplaySkinToneHelpKey, EMFPreviouslyUsedCategoryKey, "
                 "EMFViewedInCategoryKey, EMFTypingNamesKey, EMFEmojiUsageKey) are reported when "
                 "present; what each records is not established. The iOS file was not examined "
                 "here; the artifact was exercised on a macOS 26 instance written by the same "
                 "framework and on constructed data only. Suggested in issue #1876.",
        "paths": ('*/mobile/Library/Preferences/com.apple.EmojiPreferences.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "smile",
    },
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_plist_file_content, logfunc

_DEFAULTS_KEY = 'EMFDefaultsKey'
_RECENTS_KEY = 'EMFRecentsKey'
_USAGE_HISTORY_KEY = 'EMFUsageHistoryKey'


def _defaults(plist):
    defaults = plist.get(_DEFAULTS_KEY) if isinstance(plist, dict) else None
    return defaults if isinstance(defaults, dict) else {}


def _recents(defaults):
    recents = defaults.get(_RECENTS_KEY)
    return [str(emoji) for emoji in recents] if isinstance(recents, list) else []


def _usage_history(defaults):
    history = defaults.get(_USAGE_HISTORY_KEY)
    if not isinstance(history, dict):
        return {}
    return {str(emoji): [n for n in uses if isinstance(n, int)] if isinstance(uses, list) else []
            for emoji, uses in history.items()}


def _flatten(value, key_path, rows):
    if isinstance(value, dict):
        for key in sorted(value, key=str):
            _flatten(value[key], f'{key_path}.{key}' if key_path else str(key), rows)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _flatten(item, f'{key_path}[{index}]', rows)
    elif isinstance(value, bytes):
        rows.append((key_path, value.hex()))
    else:
        rows.append((key_path, str(value)))


@artifact_processor
def emojiRecents(context):
    """ See artifact description """
    source_path = get_file_path(context.get_files_found(), 'com.apple.EmojiPreferences.plist')
    data_headers = ('Recents Rank', 'Emoji', 'Uses Recorded', 'First Use Sequence',
                    'Last Use Sequence', 'Source File')
    data_list = []
    if not source_path:
        return data_headers, data_list, ''

    defaults = _defaults(get_plist_file_content(source_path))
    recents = _recents(defaults)
    history = _usage_history(defaults)
    if not recents and not history:
        logfunc(f'{source_path} holds no {_RECENTS_KEY} list or {_USAGE_HISTORY_KEY} dictionary')
    source_file = context.get_relative_path(source_path)

    ranks = {}
    for position, emoji in enumerate(recents, start=1):
        ranks.setdefault(emoji, position)
    ordered = list(dict.fromkeys(recents)) + sorted(set(history) - set(recents))
    for emoji in ordered:
        uses = history.get(emoji, [])
        data_list.append((
            ranks.get(emoji, ''),
            emoji,
            len(uses) if emoji in history else '',
            min(uses) if uses else '',
            max(uses) if uses else '',
            source_file,
        ))
    return data_headers, data_list, source_path


@artifact_processor
def emojiPreferenceKeys(context):
    """ See artifact description """
    source_path = get_file_path(context.get_files_found(), 'com.apple.EmojiPreferences.plist')
    data_headers = ('Key', 'Value (as stored)', 'Source File')
    data_list = []
    if not source_path:
        return data_headers, data_list, ''

    plist = get_plist_file_content(source_path)
    if not isinstance(plist, dict):
        logfunc(f'{source_path} did not read as a plist dictionary')
        return data_headers, data_list, source_path
    remaining = {}
    for key, value in plist.items():
        if key == _DEFAULTS_KEY and isinstance(value, dict):
            value = {k: v for k, v in value.items() if k not in (_RECENTS_KEY, _USAGE_HISTORY_KEY)}
        remaining[key] = value

    rows = []
    _flatten(remaining, '', rows)
    source_file = context.get_relative_path(source_path)
    data_list = [(key, value, source_file) for key, value in rows]
    return data_headers, data_list, source_path
