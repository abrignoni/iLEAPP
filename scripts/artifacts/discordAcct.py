__artifacts_v2__ = {
    "get_discordAcct": {
        "name": "Discord - Account",
        "description": "The Discord accounts signed in on the device, with the user name, "
                       "discriminator, email address, verification and two-factor state the "
                       "app cached for each, and the profile text the account published.",
        "author": "@abrignoni, Claude",
        "creation_date": "2020-09-15",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Discord",
        "notes": "Read from the app's MMKV store (Documents/mmkv/mmkv.default) with the vendored "
                 "mmkv_parser, replacing a printable-strings scrape that reported two keys. The "
                 "path pattern matches every app's mmkv.default because an iOS data container is "
                 "named by a GUID, so a store is read only when it carries Discord's own keys "
                 "(user_id_cache, MultiAccountStore or UserStore-snapshot) and is skipped "
                 "otherwise. One row per account in MultiAccountStore, which lists every "
                 "account signed in on the device, joined to the fuller record in "
                 "UserStore-snapshot and UserProfileStore-snapshot where the same id appears; an "
                 "account present only in the older user_id_cache and email_cache keys is still "
                 "reported from those. Token Status is reported as stored. The account's "
                 "authentication tokens and push tokens are in the same store and are not "
                 "reported. Email is what the app cached, not a verified identifier. Profile Fetched At and Legacy Username come from "
                 "UserProfileStore-snapshot and are present only where that key is; it was on one of "
                 "the fifteen tested extractions.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/mmkv/mmkv.default',),
        "output_types": "standard",
        "artifact_icon": "brand-discord",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | com.zhiliaoapp.musically | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | Discord - Talk, Play, Hang Out 298.0, NFL 60.0.12, TikTok - Videos, Shop & LIVE 41.8.0 | 1 row",
            "felix_ios17": "iOS 17.6.1 | Discord – Talk, Play, Hang Out 244.0 | 1 row",
            "fsfull002_ios17": "iOS 17.1 | TikTok 28.4.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Discord - Talk, Play, Hang Out 324.0 | 1 row",
            "iphone11_ios17": "iOS 17.3 | Discord - Talk, Play, Hang Out 238.0, TikTok 35.1.0 | 1 row",
            "iphone12_ios18": "iOS 18.7 | Evernote - Notes Organizer 10.167.1, Discord - Talk, Play, Hang Out 306.1, TikTok - Videos, Shop & LIVE 42.7.0 | 1 row",
            "iphone14plus_ios18": "iOS 18.0 | Untappd: Find Drinks You Love 4.7.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | TikTok 35.6.0 | 0 rows",
            "abe_ios16": "iOS 16.5 | TikTok 30.0.0 | 0 rows",
            "felix23_ios16": "iOS 16.5 | Discord - Chat, Talk & Hangout 183.0 | 1 row",
            "hickman_ios13": "iOS 13.3.1 | Discord 15.0, TikTok - Make Your Day 15.4.0 | 1 row",
            "hickman_ios14": "iOS 14.3 | Discord - Talk, Chat, Hang Out 58.1, TikTok 18.4.5 | 1 row",
            "jess_ios15": "iOS 15.0.2 | Discord - Talk, Chat & Hangout 109.0 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | Discord - Chat, Talk & Hangout 156.0, TikTok 27.0.1 | 1 row",
        },
    },
    "discordDevice": {
        "name": "Discord - Device and Sessions",
        "description": "The device and app identity Discord recorded, when the app was first run "
                       "and last synced, the most recent session, and the voice region the app "
                       "measured as nearest.",
        "author": "@abrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Discord",
        "notes": "Read from the app's MMKV store. One row per store. First Run is the "
                 "first_run_date_key value and First Use the firstUse value of RequestReviewStore, "
                 "both Unix milliseconds. Last Sync, Session Started and Last Heartbeat are the "
                 "lastSyncTime, LATEST_SESSION_INITIALIZED_TIMESTAMP and the newest of the "
                 "LATEST_SESSION_TIMESTAMP and LATEST_HEARTBEAST_TIMESTAMP values; the store is "
                 "append-only so the heartbeat key can carry dozens of superseded writes, and the "
                 "count of those writes is reported as Heartbeat Writes; Session UUID, Session Started "
                 "and Last Heartbeat are present only where the app wrote those keys (two of fifteen "
                 "tested extractions). Device fields come from "
                 "the deviceProperties JSON as stored: OS, client, device model, system locale, "
                 "client version, release channel and the device vendor identifier. Preferred "
                 "Voice Region and Region Test At come from RTCRegionStore; the region is the one "
                 "the app measured as nearest at that time and is a coarse indication, not a "
                 "location. Camera and Microphone Permission are the app's recorded permission "
                 "states as stored. Values are what the app cached and are reported without "
                 "interpretation.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/mmkv/mmkv.default',),
        "output_types": "standard",
        "artifact_icon": "device-mobile",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | com.zhiliaoapp.musically | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | Discord - Talk, Play, Hang Out 298.0, NFL 60.0.12, TikTok - Videos, Shop & LIVE 41.8.0 | 1 row",
            "felix_ios17": "iOS 17.6.1 | Discord – Talk, Play, Hang Out 244.0 | 1 row",
            "fsfull002_ios17": "iOS 17.1 | TikTok 28.4.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Discord - Talk, Play, Hang Out 324.0 | 1 row",
            "iphone11_ios17": "iOS 17.3 | Discord - Talk, Play, Hang Out 238.0, TikTok 35.1.0 | 1 row",
            "iphone12_ios18": "iOS 18.7 | Evernote - Notes Organizer 10.167.1, Discord - Talk, Play, Hang Out 306.1, TikTok - Videos, Shop & LIVE 42.7.0 | 1 row",
            "iphone14plus_ios18": "iOS 18.0 | Untappd: Find Drinks You Love 4.7.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | TikTok 35.6.0 | 0 rows",
            "abe_ios16": "iOS 16.5 | TikTok 30.0.0 | 0 rows",
            "felix23_ios16": "iOS 16.5 | Discord - Chat, Talk & Hangout 183.0 | 1 row",
            "hickman_ios13": "iOS 13.3.1 | Discord 15.0, TikTok - Make Your Day 15.4.0 | 1 row",
            "hickman_ios14": "iOS 14.3 | Discord - Talk, Chat, Hang Out 58.1, TikTok 18.4.5 | 1 row",
            "jess_ios15": "iOS 15.0.2 | Discord - Talk, Chat & Hangout 109.0 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | Discord - Chat, Talk & Hangout 156.0, TikTok 27.0.1 | 1 row",
        },
    },
    "discordSessions": {
        "name": "Discord - App Sessions",
        "description": "Times the Discord app recorded a session start, by day.",
        "author": "@abrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Discord",
        "notes": "Read from the UsageStatisticsStore JSON in the app's MMKV store, whose _state "
                 "holds a sessions map from a calendar day to a list of startTimestamp values in "
                 "Unix milliseconds. One row per start. The day string is the app's own bucket "
                 "and is reported as stored beside the rendered UTC time. This key was present on "
                 "two of the fifteen tested extractions; where it is absent the artifact reports "
                 "nothing for that store.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/mmkv/mmkv.default',),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | com.zhiliaoapp.musically | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | Discord - Talk, Play, Hang Out 298.0, NFL 60.0.12, TikTok - Videos, Shop & LIVE 41.8.0 | 3 rows",
            "felix_ios17": "iOS 17.6.1 | Discord – Talk, Play, Hang Out 244.0 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | TikTok 28.4.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Discord - Talk, Play, Hang Out 324.0 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Discord - Talk, Play, Hang Out 238.0, TikTok 35.1.0 | 1 row",
            "iphone12_ios18": "iOS 18.7 | Evernote - Notes Organizer 10.167.1, Discord - Talk, Play, Hang Out 306.1, TikTok - Videos, Shop & LIVE 42.7.0 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | Untappd: Find Drinks You Love 4.7.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | TikTok 35.6.0 | 0 rows",
            "abe_ios16": "iOS 16.5 | TikTok 30.0.0 | 0 rows",
            "felix23_ios16": "iOS 16.5 | Discord - Chat, Talk & Hangout 183.0 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | Discord 15.0, TikTok - Make Your Day 15.4.0 | 0 rows",
            "hickman_ios14": "iOS 14.3 | Discord - Talk, Chat, Hang Out 58.1, TikTok 18.4.5 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | Discord - Talk, Chat & Hangout 109.0 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | Discord - Chat, Talk & Hangout 156.0, TikTok 27.0.1 | 0 rows",
        },
    },
    "discordDrafts": {
        "name": "Discord - Message Drafts",
        "description": "Text the account typed into a channel's message box and had not sent when "
                       "the app saved it, with the time of each save, including superseded "
                       "versions that show the text as it was being typed.",
        "author": "@abrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Discord",
        "notes": "Read from every write of the DraftStore key in the app's MMKV store, not only "
                 "the current one: the store is append-only, so each save of the draft box is a "
                 "separate entry, and one tested extraction held 120 rows tracing a message being "
                 "typed a few characters at a time. Each write's _state maps an account id to a "
                 "channel id to a draft type to a timestamp and the draft text; one row per "
                 "(write, account, channel, type). Superseded Write is True for every entry "
                 "except the newest, and Write Index is that entry's position in the store. Draft "
                 "Type is reported as stored. Channel IDs are Discord snowflakes and are not "
                 "resolved to names here.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/mmkv/mmkv.default',),
        "output_types": "standard",
        "artifact_icon": "edit",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | com.zhiliaoapp.musically | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | Discord - Talk, Play, Hang Out 298.0, NFL 60.0.12, TikTok - Videos, Shop & LIVE 41.8.0 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Discord – Talk, Play, Hang Out 244.0 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | TikTok 28.4.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Discord - Talk, Play, Hang Out 324.0 | 8 rows",
            "iphone11_ios17": "iOS 17.3 | Discord - Talk, Play, Hang Out 238.0, TikTok 35.1.0 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | Evernote - Notes Organizer 10.167.1, Discord - Talk, Play, Hang Out 306.1, TikTok - Videos, Shop & LIVE 42.7.0 | 3 rows",
            "iphone14plus_ios18": "iOS 18.0 | Untappd: Find Drinks You Love 4.7.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | TikTok 35.6.0 | 0 rows",
            "abe_ios16": "iOS 16.5 | TikTok 30.0.0 | 0 rows",
            "felix23_ios16": "iOS 16.5 | Discord - Chat, Talk & Hangout 183.0 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | Discord 15.0, TikTok - Make Your Day 15.4.0 | 0 rows",
            "hickman_ios14": "iOS 14.3 | Discord - Talk, Chat, Hang Out 58.1, TikTok 18.4.5 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | Discord - Talk, Chat & Hangout 109.0 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | Discord - Chat, Talk & Hangout 156.0, TikTok 27.0.1 | 120 rows",
        },
    },
    "discordSelected": {
        "name": "Discord - Selected Guilds and Channels",
        "description": "The guilds and channels the app recorded as selected, with the time each "
                       "guild was last selected and the last voice connection time, including "
                       "superseded values.",
        "author": "@abrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Discord",
        "notes": "Read from every write of SelectedGuildStore and SelectedChannelStore in the "
                 "app's MMKV store. From SelectedGuildStore, one row per guild in "
                 "selectedGuildTimestampMillis, with lastSelectedGuildId flagged. From "
                 "SelectedChannelStore, one row per guild-to-channel pair in selectedChannelIds "
                 "and mostRecentSelectedTextChannelIds, plus the top-level selectedChannelId, "
                 "selectedVoiceChannelId and lastConnectedTime. Superseded Write is True for "
                 "entries older than the newest write of that key. A guild id of null in the "
                 "store denotes direct messages and is reported as stored. Guild and channel ids "
                 "are Discord snowflakes and are not resolved to names here.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/mmkv/mmkv.default',),
        "output_types": "standard",
        "artifact_icon": "hash",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | com.zhiliaoapp.musically | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | Discord - Talk, Play, Hang Out 298.0, NFL 60.0.12, TikTok - Videos, Shop & LIVE 41.8.0 | 8 rows",
            "felix_ios17": "iOS 17.6.1 | Discord – Talk, Play, Hang Out 244.0 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | TikTok 28.4.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Discord - Talk, Play, Hang Out 324.0 | 5 rows",
            "iphone11_ios17": "iOS 17.3 | Discord - Talk, Play, Hang Out 238.0, TikTok 35.1.0 | 15 rows",
            "iphone12_ios18": "iOS 18.7 | Evernote - Notes Organizer 10.167.1, Discord - Talk, Play, Hang Out 306.1, TikTok - Videos, Shop & LIVE 42.7.0 | 2 rows",
            "iphone14plus_ios18": "iOS 18.0 | Untappd: Find Drinks You Love 4.7.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | TikTok 35.6.0 | 0 rows",
            "abe_ios16": "iOS 16.5 | TikTok 30.0.0 | 0 rows",
            "felix23_ios16": "iOS 16.5 | Discord - Chat, Talk & Hangout 183.0 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | Discord 15.0, TikTok - Make Your Day 15.4.0 | 27 rows",
            "hickman_ios14": "iOS 14.3 | Discord - Talk, Chat, Hang Out 58.1, TikTok 18.4.5 | 4 rows",
            "jess_ios15": "iOS 15.0.2 | Discord - Talk, Chat & Hangout 109.0 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | Discord - Chat, Talk & Hangout 156.0, TikTok 27.0.1 | 4 rows",
        },
    },
}

import json
import os
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.mmkv_parser import MMKVError, decode_value, read_entries

# Keys only Discord writes. The glob is cross-app, so these decide attribution.
_MARKERS = ('user_id_cache', 'MultiAccountStore', 'UserStore-snapshot')


def _ms(value):
    """Unix milliseconds (int or digit string) as an aware UTC datetime, or ''."""
    try:
        text = str(value).strip().strip('"')
        if not text or text in ('null', 'None'):
            return ''
        return datetime.fromtimestamp(int(text) / 1000, tz=timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _json(value):
    """A decoded MMKV string parsed as JSON, or None when it is not JSON."""
    if isinstance(value, (bytes, bytearray)):
        try:
            value = value.decode('utf-8')
        except UnicodeDecodeError:
            return None
    if not isinstance(value, str) or value[:1] not in '{[':
        return None
    try:
        return json.loads(value)
    except ValueError:
        return None


def _text(value):
    if value is None:
        return ''
    if isinstance(value, bool):
        return value
    if isinstance(value, (list, tuple)):
        return ', '.join(str(v) for v in value)
    if isinstance(value, str):
        return value.strip('"')
    return value


def _stores(files_found):
    """Each Discord MMKV store as (path, entries in file order, live dict)."""
    found = []
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.isdir(file_found) or not file_found.endswith('mmkv.default'):
            continue
        try:
            entries = read_entries(file_found)
        except MMKVError as error:
            logfunc(f'Discord: {os.path.basename(os.path.dirname(os.path.dirname(file_found)))}/mmkv.default not read: {error}')
            continue
        except OSError as error:
            logfunc(f'Discord: could not read {file_found}: {error}')
            continue
        live = {}
        for key, raw in entries:
            live[key] = decode_value(raw)
        if not any(marker in live for marker in _MARKERS):
            continue
        found.append((file_found, entries, live))
    return found


def _writes(entries, key):
    """Every write of ``key``: (write index, decoded value), oldest first."""
    return [(i, decode_value(raw)) for i, (k, raw) in enumerate(entries) if k == key]


@artifact_processor
def get_discordAcct(context):
    data_headers = (
        ('Profile Fetched At', 'datetime'),
        'Username',
        'Discriminator',
        'Email',
        'Account ID',
        'Verified',
        'MFA Enabled',
        'Mobile',
        'Desktop',
        'Token Status (as stored)',
        'Legacy Username',
        'Source File',
    )
    data_list = []
    sources = []
    for store, _entries, live in _stores(context.get_files_found()):
        users = {}
        multi = _json(live.get('MultiAccountStore')) or {}
        for u in (multi.get('_state') or {}).get('users') or []:
            if isinstance(u, dict) and u.get('id'):
                users.setdefault(str(u['id']), {}).update(
                    {'username': u.get('username'), 'discriminator': u.get('discriminator'),
                     'tokenStatus': u.get('tokenStatus')})
        snap = _json(live.get('UserStore-snapshot')) or {}
        for u in (snap.get('data') or {}).get('users') or []:
            if isinstance(u, dict) and u.get('id'):
                users.setdefault(str(u['id']), {}).update(u)
        prof = _json(live.get('UserProfileStore-snapshot')) or {}
        for entry in prof.get('data') or []:
            if isinstance(entry, dict) and entry.get('userId'):
                p = entry.get('profile') or {}
                users.setdefault(str(entry['userId']), {}).update(
                    {'legacyUsername': p.get('legacyUsername'), 'lastFetched': p.get('lastFetched')})
        # the two keys the previous version of this artifact read
        cached_id = _text(live.get('user_id_cache'))
        if cached_id and cached_id != 'null':
            users.setdefault(cached_id, {})
            email = _text(live.get('email_cache'))
            if email and email != 'null':
                users[cached_id].setdefault('email', email)
        for account_id, u in users.items():
            data_list.append((
                _ms(u.get('lastFetched')),
                _text(u.get('username')),
                _text(u.get('discriminator')),
                _text(u.get('email')),
                account_id,
                _text(u.get('verified')),
                _text(u.get('mfaEnabled')),
                _text(u.get('mobile')),
                _text(u.get('desktop')),
                _text(u.get('tokenStatus')),
                _text(u.get('legacyUsername')),
                context.get_relative_path(store),
            ))
        if users:
            sources.append(store)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def discordDevice(context):
    data_headers = (
        ('First Run', 'datetime'),
        ('First Use', 'datetime'),
        ('Last Sync', 'datetime'),
        ('Session Started', 'datetime'),
        ('Last Heartbeat', 'datetime'),
        ('Region Test At', 'datetime'),
        'Heartbeat Writes',
        'Session UUID',
        'OS',
        'Client',
        'Device',
        'System Locale',
        'Client Version',
        'Release Channel',
        'Device Vendor ID',
        'Preferred Voice Region',
        'Camera Permission',
        'Microphone Permission',
        'Theme',
        'Source File',
    )
    data_list = []
    sources = []
    for store, entries, live in _stores(context.get_files_found()):
        dev = _json(live.get('deviceProperties')) or {}
        review = _json(live.get('RequestReviewStore')) or {}
        rtc = (_json(live.get('RTCRegionStore')) or {}).get('_state') or {}
        perms = ((_json(live.get('NativePermissionsStore')) or {}).get('_state') or {}).get('permissionStates') or {}
        theme = ((_json(live.get('ThemeStore')) or {}).get('_state') or {}).get('theme')
        beats = [v for _i, v in _writes(entries, 'LATEST_HEARTBEAST_TIMESTAMP')] + \
                [v for _i, v in _writes(entries, 'LATEST_SESSION_TIMESTAMP')]
        newest_beat = max((int(str(b).strip('"')) for b in beats if str(b).strip('"').isdigit()), default=None)
        data_list.append((
            _ms(live.get('first_run_date_key')),
            _ms(review.get('firstUse')),
            _ms(live.get('lastSyncTime')),
            _ms(live.get('LATEST_SESSION_INITIALIZED_TIMESTAMP') or live.get('LATEST_HEARTBEAST_INITIALIZED_TIMESTAMP')),
            _ms(newest_beat),
            _ms(rtc.get('lastTestTimestamp')),
            len(beats),
            _text(live.get('LATEST_SESSION_UUID') or live.get('LATEST_HEARTBEAST_UUID')),
            _text(dev.get('os')),
            _text(dev.get('browser')),
            _text(dev.get('device')),
            _text(dev.get('system_locale')),
            _text(dev.get('client_version')),
            _text(dev.get('release_channel')),
            _text(dev.get('device_vendor_id')),
            _text(rtc.get('preferredRegion')),
            _text(perms.get('camera')),
            _text(perms.get('audio')),
            _text(theme),
            context.get_relative_path(store),
        ))
        sources.append(store)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def discordSessions(context):
    data_headers = (
        ('Session Started', 'datetime'),
        'Day (as stored)',
        'Source File',
    )
    data_list = []
    sources = []
    for store, _entries, live in _stores(context.get_files_found()):
        usage = (_json(live.get('UsageStatisticsStore')) or {}).get('_state') or {}
        rows = 0
        for day, starts in (usage.get('sessions') or {}).items():
            for s in starts or []:
                if isinstance(s, dict) and s.get('startTimestamp'):
                    data_list.append((_ms(s['startTimestamp']), _text(day), context.get_relative_path(store)))
                    rows += 1
        if rows:
            sources.append(store)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def discordDrafts(context):
    data_headers = (
        ('Saved At', 'datetime'),
        'Draft Text',
        'Account ID',
        'Channel ID',
        'Draft Type (as stored)',
        'Superseded Write',
        'Write Index',
        'Source File',
    )
    data_list = []
    sources = []
    for store, entries, _live in _stores(context.get_files_found()):
        writes = _writes(entries, 'DraftStore')
        if not writes:
            continue
        newest = writes[-1][0]
        rows = 0
        for index, value in writes:
            state = (_json(value) or {}).get('_state') or {}
            for account_id, channels in state.items():
                if not isinstance(channels, dict):
                    continue
                for channel_id, kinds in channels.items():
                    if not isinstance(kinds, dict):
                        continue
                    for draft_type, d in kinds.items():
                        if not isinstance(d, dict):
                            continue
                        data_list.append((
                            _ms(d.get('timestamp')),
                            _text(d.get('draft')),
                            _text(account_id),
                            _text(channel_id),
                            _text(draft_type),
                            index != newest,
                            index,
                            context.get_relative_path(store),
                        ))
                        rows += 1
        if rows:
            sources.append(store)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def discordSelected(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Record',
        'Guild ID',
        'Channel ID',
        'Last Selected Guild',
        'Superseded Write',
        'Write Index',
        'Source File',
    )
    data_list = []
    sources = []
    for store, entries, _live in _stores(context.get_files_found()):
        rows = 0
        gw = _writes(entries, 'SelectedGuildStore')
        newest = gw[-1][0] if gw else None
        for index, value in gw:
            state = (_json(value) or {}).get('_state') or {}
            last = str(state.get('lastSelectedGuildId') or '')
            for guild_id, ts in (state.get('selectedGuildTimestampMillis') or {}).items():
                data_list.append((_ms(ts), 'guild selected', _text(guild_id), '', str(guild_id) == last,
                                  index != newest, index, context.get_relative_path(store)))
                rows += 1
        cw = _writes(entries, 'SelectedChannelStore')
        newest = cw[-1][0] if cw else None
        for index, value in cw:
            j = _json(value) or {}
            for label, mapping in (('selected channel', j.get('selectedChannelIds')),
                                   ('most recent text channel', j.get('mostRecentSelectedTextChannelIds'))):
                for guild_id, channel_id in (mapping or {}).items():
                    data_list.append(('', label, _text(guild_id), _text(channel_id), '',
                                      index != newest, index, context.get_relative_path(store)))
                    rows += 1
            if j.get('selectedChannelId') or j.get('selectedVoiceChannelId') or j.get('lastConnectedTime'):
                data_list.append((_ms(j.get('lastConnectedTime')), 'current selection',
                                  '', _text(j.get('selectedChannelId')), '',
                                  index != newest, index, context.get_relative_path(store)))
                if j.get('selectedVoiceChannelId'):
                    data_list.append(('', 'selected voice channel', '', _text(j.get('selectedVoiceChannelId')), '',
                                      index != newest, index, context.get_relative_path(store)))
                    rows += 1
                rows += 1
        if rows:
            sources.append(store)
    return data_headers, data_list, '\n'.join(sources)
