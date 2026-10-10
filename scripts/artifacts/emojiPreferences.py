""" Emoji keyboard preferences: com.apple.EmojiPreferences.plist """
__artifacts_v2__ = {
    "emojiRecents": {
        "name": "Emoji Recents and Usage",
        "description": "One row per emoji named in the recents list or the usage history of "
                       "com.apple.EmojiPreferences.plist, with its position in the recents list "
                       "and the count, lowest and highest of the use sequence numbers recorded "
                       "for it, as stored.",
        "author": "@ayobamiseun, Claude",
        "creation_date": "2026-10-10",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "User Activity",
        "notes": "None of the 23 sample_data files holds a timestamp value. EMFRecentsKey is a "
                 "list of emoji strings and "
                 "Recents Rank is the 1-based position in it, as stored. The list is not ordered "
                 "by Last Use Sequence: on 9 of the 17 sample_data images that hold a recents "
                 "list the list order differs from the order of Last Use Sequence, highest "
                 "first, and on 6 of those 9 rank 1 is not the emoji with the "
                 "highest sequence number, so rank 1 is not established as the most recently "
                 "used emoji. EMFUsageHistoryKey maps an emoji to a list of integers and "
                 "EMFRecentSequenceNumberKey holds one integer; on those 17 images (iOS 12.4 to "
                 "26.2.1) the integers across all lists were distinct, ran from 0 to one below "
                 "the sequence number, and each list was ascending, so Uses Recorded is the "
                 "length of the list and First and Last Use Sequence are its lowest and highest "
                 "values, reported as stored. What a sequence number counts, and whether the "
                 "history is capped, is not established. The recents list held 30 entries on the "
                 "two images whose usage history names more emoji than the list does (abe_ios16, "
                 "otto_ios17) and fewer than 30 on the other 15; an emoji in the history and not "
                 "in the list has an empty Recents Rank. On the 6 images recorded with 0 rows "
                 "the file is present and holds neither key. Suggested in issue #1876.",
        "paths": ('*/mobile/Library/Preferences/com.apple.EmojiPreferences.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "smile",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 3 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 4 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 48 rows",
            "felix23_ios16": "iOS 16.5 | 2 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 14 rows",
            "fsfull002_ios17": "iOS 17.1 | 9 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 3 rows",
            "hc_ios17_2": "iOS 17.2.1 | 12 rows",
            "iphone11_ios17": "iOS 17.3 | 7 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 1 rows",
            "otto_ios17": "iOS 17.5.1 | 59 rows",
            "felix_ios17": "iOS 17.6.1 | 2 rows",
            "iphone14plus_ios18": "iOS 18.0 | 3 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 4 rows",
            "dexter_ios18": "iOS 18.3.2 | 4 rows",
            "iphone12_ios18": "iOS 18.7 | 10 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 11 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
    "emojiPreferenceKeys": {
        "name": "Emoji Preferences",
        "description": "The keys of com.apple.EmojiPreferences.plist other than the recents list "
                       "and usage history, flattened to one row per stored value with its key "
                       "path, rendered as text.",
        "author": "@ayobamiseun, Claude",
        "creation_date": "2026-10-10",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "User Activity",
        "notes": "The recents list and usage history are reported by Emoji Recents and Usage and "
                 "left out here. Nested dictionaries are flattened as parent.key and lists as "
                 "parent[index], so each emoji under EMFSkinToneBaseKeyPreferences is one row. "
                 "A top-level key whose own name contains dots "
                 "(com.apple.stickerkit.onboarding.shown) is shown whole and is not a nested "
                 "path. Values are rendered as text: booleans as True or False, binary data as "
                 "hex. On the 23 sample_data images the key paths reported were "
                 "DidMigrateToEMF (23 images) and com.apple.stickerkit.onboarding.shown (1) at "
                 "the top level, and under EMFDefaultsKey (present on all 23, empty on 2): "
                 "EMFRecentSequenceNumberKey (21), "
                 "EMFPreviouslyUsedCategoryKey (13), EMFViewedInCategoryKey (13), "
                 "EMFSkinToneBaseKeyPreferences (11), EMFDidDisplaySkinToneHelpKey (8) and "
                 "EMFTypingNamesKey (2). Any other key in the file is reported the same way. "
                 "What each key records is not established. Suggested in issue #1876.",
        "paths": ('*/mobile/Library/Preferences/com.apple.EmojiPreferences.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "smile",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 4 rows",
            "hickman_ios13": "iOS 13.3.1 | 2 rows",
            "hickman_ios14": "iOS 14.3 | 2 rows",
            "jess_ios15": "iOS 15.0.2 | 2 rows",
            "hickman_ios15": "iOS 15.3.1 | 5 rows",
            "magnet_ios16": "iOS 16.1.1 | 2 rows",
            "abe_ios16": "iOS 16.5 | 28 rows",
            "felix23_ios16": "iOS 16.5 | 2 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 10 rows",
            "fsfull002_ios17": "iOS 17.1 | 6 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 4 rows",
            "hc_ios17_2": "iOS 17.2.1 | 9 rows",
            "iphone11_ios17": "iOS 17.3 | 8 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | 15 rows",
            "felix_ios17": "iOS 17.6.1 | 2 rows",
            "iphone14plus_ios18": "iOS 18.0 | 11 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 9 rows",
            "dexter_ios18": "iOS 18.3.2 | 8 rows",
            "iphone12_ios18": "iOS 18.7 | 7 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1 rows",
            "falken_ios26": "iOS 26.2.1 | 8 rows",
            "hc_ios26": "iOS 26.5.2 | 1 rows",
        },
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
                    'Last Use Sequence')
    data_list = []
    if not source_path:
        return data_headers, data_list, ''

    defaults = _defaults(get_plist_file_content(source_path))
    recents = _recents(defaults)
    history = _usage_history(defaults)
    if not recents and not history:
        logfunc(f'{source_path} holds no {_RECENTS_KEY} list or {_USAGE_HISTORY_KEY} dictionary')

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
        ))
    return data_headers, data_list, source_path


@artifact_processor
def emojiPreferenceKeys(context):
    """ See artifact description """
    source_path = get_file_path(context.get_files_found(), 'com.apple.EmojiPreferences.plist')
    data_headers = ('Key', 'Value')
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

    _flatten(remaining, '', data_list)
    return data_headers, data_list, source_path
