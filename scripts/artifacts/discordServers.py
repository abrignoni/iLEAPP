__artifacts_v2__ = {
    "discordServers": {
        "name": "Discord - Servers",
        "description": "Discord servers (guilds) cached in the app's kv-storage database for each "
                       "@account.<id> folder, with the joinedAt time, owner id and the number of "
                       "that server's channels cached beside it.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-23",
        "last_update_date": "2026-10-23",
        "requirements": "none",
        "category": "Discord",
        "notes": "Read from the kv_cache0 table of Library/Caches/kv-storage/@account.<id>/a, "
                 "one row per server id among the records of kind guilds. For records of kind "
                 "guilds and guild_channels, data is one byte followed by JSON, as messages0 "
                 "rows are; what that byte encodes is not established, and some other kinds in "
                 "the table did not decode as JSON after it. Joined At is the "
                 "record's joinedAt value (ISO 8601). The Discord Developer Documentation "
                 "describes joined_at on the Guild Create gateway event as when the guild was "
                 "joined (https://docs.discord.com/developers/events/gateway-events#guild-create; "
                 "source https://github.com/discord/discord-api-docs/blob/aaef8ae4c3398fcdabeec0d1dd5a3e69be587ad8/developers/events/gateway-events.mdx#L762); "
                 "that the cached joinedAt holds the same value for the account in the folder "
                 "name was not tested. A joinedAt value that does not parse is left blank and "
                 "counted in the log. Owner Is Account is True when ownerId equals the account id in the "
                 "@account.<id> path. Cached Channels counts the guild_channels records in the "
                 "same table whose guild_id is the server's id; it is the channel list the app "
                 "cached; this artifact does not report which of those channels were viewed. In tested "
                 "samples each image "
                 "with a server held exactly one server record, Description held text on "
                 "dexter_ios18 only, Owner Is Account was False on every row, and Cached "
                 "Channels was 80 on dexter_ios18 and 4 on iphone11_ios17; on dexter_ios18 the chat "
                 "artifacts held messages in 3 of those 80 channels. The same table also caches "
                 "other record kinds, among them emoji, sticker, read-state and settings records, "
                 "which this artifact does not report. Channel and server names from this table are also added to the "
                 "Discord - Chats and Discord Chats (KV Storage) artifacts.",
        "paths": ('*/Library/Caches/kv-storage/@account*/a*',),
        "output_types": "standard",
        "artifact_icon": "server",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | Discord - Talk, Play, Hang Out 298.0 | 1 row",
            "iphone11_ios17": "iOS 17.3 | Discord - Talk, Play, Hang Out 238.0 | 1 row",
            "iphone12_ios18": "iOS 18.7 | Discord - Talk, Play, Hang Out 306.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Discord - Talk, Play, Hang Out 324.0 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | Discord 15.0 | 0 rows (no kv-storage database found)",
        },
    }
}

import json
import re
import sqlite3
from datetime import datetime
from os.path import basename

from scripts.ilapfuncs import artifact_processor, does_table_exist_in_db, get_sqlite_db_records, logfunc
from scripts.sqlite_wal import (KIND_COMMITTED, KIND_EARLIER, KIND_UNCOMMITTED,
                                rows_not_in_current)

_ACCOUNT_ID_RE = re.compile(r'[/\\]@account\.(\d+)[/\\]')


def _kv_cache_records(db_file, kinds):
    """Yield (kind, record) for kv_cache0 rows whose kind is in kinds.

    Column a holds the record kind and data the record, each behind one prefix
    byte; data after that byte is JSON. Rows that do not decode are skipped.
    """
    if not does_table_exist_in_db(db_file, 'kv_cache0'):
        return
    for kind_blob, data in get_sqlite_db_records(db_file, 'SELECT a, data FROM kv_cache0'):
        if not isinstance(kind_blob, (bytes, bytearray)) or not isinstance(data, (bytes, bytearray)):
            continue
        kind = bytes(kind_blob[1:]).decode('utf-8', 'replace')
        if kind not in kinds:
            continue
        try:
            record = json.loads(bytes(data[1:]))
        except (ValueError, UnicodeDecodeError):
            continue
        if isinstance(record, dict) and record.get('id'):
            yield kind, record


def discord_kv_lookup(db_files):
    """Map server and channel ids to their cached records across kv-storage databases.

    Returns (guilds, channels), each keyed by id as a string. Channel ids are
    global snowflakes, so records from several accounts can share one map.
    """
    guilds = {}
    channels = {}
    for db_file in db_files:
        for kind, record in _kv_cache_records(db_file, ('guilds', 'guild_channels')):
            target = guilds if kind == 'guilds' else channels
            target.setdefault(str(record['id']), record)
    return guilds, channels


# messages0 declares no primary key; the unique index messages0_by_key on (a, b, c, d, e, f)
# is what makes a row one message, so that is the key compared across states.
_MESSAGE_KEY_SQL = 'SELECT a, b, c, d, e, f, data FROM messages0'
_MESSAGE_KEY = (0, 1, 2, 3, 4, 5)
_WAL_KINDS = (KIND_COMMITTED, KIND_EARLIER, KIND_UNCOMMITTED)
ORIGIN_LIVE = 'Live'
ORIGIN_RECOVERED = 'Recovered'
_METHOD_WAL_STATES = 'WAL committed states'
_METHOD_WAL_UNCOMMITTED = 'WAL uncommitted frames'


def _recovery_location(name, spans):
    """(method, location) for a key read in the states spans names."""
    parts = []
    committed, earlier = spans['committed'], spans['earlier']
    if committed:
        first, last = committed
        if last == 0:
            parts.append(f'{name} without its log, state 0')
        elif first == 0:
            parts.append(f'{name} and {name}-wal, committed states 0 to {last}')
        else:
            states = f'state {first}' if first == last else f'states {first} to {last}'
            parts.append(f'{name}-wal, committed {states}')
    if earlier:
        first, last = earlier
        commits = f'commit {first}' if first == last else f'commits {first} to {last}'
        parts.append(f'{name}-wal, previous log generation, left-over {commits}')
    if not parts:
        return _METHOD_WAL_UNCOMMITTED, f'{name}-wal, frames after the last commit'
    return _METHOD_WAL_STATES, '; '.join(parts)


def discord_removed_messages(db_file):
    """messages0 rows whose key another state in the write-ahead log holds and the
    current state does not, read through scripts/sqlite_wal.py.

    Returns [(data, method, location)], one per key: data as the newest state holding the
    key stored it (a committed state before the previous log generation before the frames
    after the last commit).
    """
    db_file = str(db_file)
    live = {tuple(row[i] for i in _MESSAGE_KEY)
            for row in get_sqlite_db_records(db_file, _MESSAGE_KEY_SQL)}
    try:
        _columns, found, wal = rows_not_in_current(db_file, _MESSAGE_KEY_SQL,
                                                   key_columns=_MESSAGE_KEY, include=_WAL_KINDS)
    except (sqlite3.Error, OSError) as ex:
        logfunc(f'Discord write-ahead log not read for {basename(db_file)}: {ex}')
        return []
    logfunc(f'Discord {wal.summary()}')
    by_key = {}
    for item in found:
        key = tuple(item.values[i] for i in _MESSAGE_KEY)
        if key in live:
            continue
        rank = ((2, item.last_state) if item.first_state is not None else
                (1, item.earlier_generation[1]) if item.earlier_generation else (0, 0))
        entry = by_key.setdefault(key, {'data': item.values[6], 'rank': rank, 'committed': None,
                                        'earlier': None})
        if rank > entry['rank']:
            entry['data'], entry['rank'] = item.values[6], rank
        for slot, span in (('committed', (item.first_state, item.last_state)
                            if item.first_state is not None else None),
                           ('earlier', item.earlier_generation)):
            if span:
                old = entry[slot]
                entry[slot] = span if old is None else (min(old[0], span[0]), max(old[1], span[1]))
    name = basename(db_file)
    return [(entry['data'], *_recovery_location(name, entry)) for entry in by_key.values()]


def _recipients(channel):
    names = []
    for user in channel.get('rawRecipients') or []:
        if isinstance(user, dict) and user.get('id'):
            username = user.get('username') or ''
            names.append(f"{username} ({user['id']})" if username else str(user['id']))
    if not names:
        names = [str(user_id) for user_id in channel.get('recipients') or []]
    return ', '.join(names)


def discord_channel_context(channel_id, guilds, channels):
    """Return (conversation, server name, server id, channel name, dm recipients).

    Blank values when the channel is not cached; the conversation label then
    falls back to the channel id.
    """
    channel = channels.get(str(channel_id or ''))
    if not channel:
        return str(channel_id or ''), '', '', '', ''
    name = channel.get('name') or ''
    guild_id = str(channel.get('guild_id') or '')
    if guild_id:
        server = (guilds.get(guild_id) or {}).get('name') or ''
        label = f"{server or guild_id} #{name}" if name else (server or guild_id)
        return label, server, guild_id, name, ''
    recipients = _recipients(channel)
    label = name or (f"DM: {recipients}" if recipients else str(channel_id))
    return label, '', '', name, recipients


def _joined_at(value):
    """Parsed joinedAt, or None when it is missing or does not parse."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except ValueError:
        return None


@artifact_processor
def discordServers(context):
    data_headers = (
        ('Joined At', 'datetime'),
        'Server Name',
        'Server ID',
        'Owner ID',
        'Owner Is Account',
        'Description',
        'Cached Channels',
        'Account ID',
    )
    data_list = []
    sources = []
    seen = set()
    unparsed = 0

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if basename(file_found) != 'a':
            continue
        match = _ACCOUNT_ID_RE.search(file_found)
        account_id = match.group(1) if match else ''
        guilds, channels = discord_kv_lookup([file_found])
        if not guilds:
            continue
        per_guild = {}
        for channel in channels.values():
            guild_id = str(channel.get('guild_id') or '')
            if guild_id:
                per_guild[guild_id] = per_guild.get(guild_id, 0) + 1
        for guild_id, guild in guilds.items():
            if (account_id, guild_id) in seen:
                continue
            seen.add((account_id, guild_id))
            owner_id = str(guild.get('ownerId') or '')
            joined_at = _joined_at(guild.get('joinedAt'))
            if joined_at is None and guild.get('joinedAt'):
                unparsed += 1
            data_list.append((
                joined_at or '',
                guild.get('name') or '',
                guild_id,
                owner_id,
                bool(account_id and owner_id == account_id),
                guild.get('description') or '',
                per_guild.get(guild_id, 0),
                account_id,
            ))
        sources.append(context.get_relative_path(file_found))

    if unparsed:
        logfunc(f'Discord: {unparsed} joinedAt value(s) did not parse and were left blank')
    if data_list:
        logfunc(f'Discord: {len(data_list)} cached server record(s)')
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))
