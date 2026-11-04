__artifacts_v2__ = {
    "google_chat": {  # This should match the function name exactly
        "name": "Google Chat",
        "description": "Messages from the first Google Chat dynamite.db matched, including messages "
                       "and earlier message text another state in its write-ahead log holds and the "
                       "current state does not",
        "author": "@AlexisBrignoni",
        "creation_date": "2023-09-03",
        "last_update_date": "2026-10-31",
        "requirements": "none",
        "category": "Google Chats",
        "notes": "Only the first dynamite.db matched is read, so a second account's database is "
                 "not reported. A message with no users row or no Groups row is not reported. "
                 "Timestamp reads create_time as Unix microseconds; the basis for that unit is not "
                 "given here. Is Sent is 1 when the message's creator_id equals the name of the "
                 "account directory holding the database; it is not a stored flag. Group Type "
                 "shows Group Message where the stored group_type value is 1 and 1-to-1 Message "
                 "where it is 2; no source for that mapping was found, so the two labels are not "
                 "established, and any other value is reported as stored. Reaction and Reaction "
                 "User are read from the reactions protobuf by field position; the positions were "
                 "not sourced. One reaction and one user are read. Where the stored value holds "
                 "more than one of either, neither is reported and the cells are blank, so a blank "
                 "cell does not establish that a message had no reaction. Filename is the value "
                 "read from field 10.3 of each entry of the message's annotation protobuf, by "
                 "field position, and treated as an attachment name; neither the position nor "
                 "that meaning was sourced, and annotation entries without that field are not "
                 "reported. Where a message holds several, the names are joined with a comma and "
                 "Media holds one item per file found. Media shows the file of that name "
                 "in the app container's tmp folder when the extraction holds it, so a Filename "
                 "with a blank Media means no file of that name was found there. The container is "
                 "the GUID-named folder in the database's path inside the extraction; where the "
                 "path holds none, as in an iTunes backup, which stages app files under the "
                 "bundle id, no attachment is looked for and Media is blank. "
                 "Record Origin. Live rows come from a normal read of the query. A message is the unique index of topic_messages on (group_id, topic_id, id), not row_id: on iphone11_ios17 and hc_ios17_2 some messages held a different row_id in different states. A Recovered row is a message another state in the database's write-ahead log holds and the current topic_messages table does not. An Earlier version row is a non-empty text_body another state held for a message whose current text_body differs, one row per distinct text. A row whose message and text the current state still holds is not reported again. The whole query is run in each state, so a Recovered or Earlier version row's sender and conversation come from the same state as its text. Recovery Method and Recovery Location are filled in only on those rows. Why a message is absent or its text changed is not established here. States are read by scripts/sqlite_wal.py: each readable earlier committed state of the log's current generation (state n is the database after the first n committed transactions, and state 0 the database file without its log; states the reader cannot rebuild exactly are skipped and counted in the run log), the previous generation's left-over frames where its checks pass, and frames after the last commit where SQLite's quick_check passes. Each row is reported as the newest committed state holding it stored it, else the previous generation's newest left-over commit, else the frames after the last commit. Recovery Location names the committed states the row was read in, with their first and last numbers, and the previous log generation with the first and last numbers of its left-over commits; for a row read only after the last commit it names the log's frames after the last commit. Recovery Method is WAL committed states, or WAL uncommitted frames for a row read only after the last commit. The previous-generation and uncommitted-frame paths were not exercised on the tested images or by the unit test. "
                 "On iphone11_ios17 the run returned 8 Recovered and 2 Earlier version rows, and on "
                 "hc_ios17_2 2 Earlier version rows, every one from committed states of the current "
                 "generation and with Message text. On magnet_ios16 Record Origin held Live on every "
                 "row and Recovery Method and Recovery Location were empty on every row. On those 4 "
                 "Earlier "
                 "version messages the current row has an empty text_body, is_tombstone 1 and a "
                 "delete_time; what the app means by those fields is not established here. Those "
                 "current rows are not reported as Live: their creator_id matches no users row, so "
                 "the query's join leaves them out. Filename and Media were empty on every "
                 "Recovered and Earlier version row.",
        "paths": ('*/Documents/user_accounts/*/dynamite.db*',
                  '*/Documents/user_accounts/*/tmp/*'),
        "output_types": "standard",  # or ["html", "tsv", "timeline", "lava"]
        "data_views": {
            "conversation": {
                "directionSentValue": 1,
                "conversationDiscriminatorColumn": "Conversation Name",
                "textColumn": "Message",
                "directionColumn": "Is Sent",
                "timeColumn": "Timestamp",
                "senderColumn": "Message Author",
                "mediaColumn": "Media"
            }
        },
        "artifact_icon": "message-circle",
        "sample_data": {
            "hc_ios17_2": "iOS 17.2.1 | 47 rows (2 Earlier version)",
            "iphone11_ios17": "iOS 17.3 | Google Chat 0.390 | 106 rows (8 Recovered, 2 Earlier version)",
            "magnet_ios16": "iOS 16.1.1 | Gmail - Email by Google 6.0.221127 | 5 rows",
        }
    }
}

import os
from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
import re
import sqlite3
from io import BytesIO

from scripts.ilapfuncs import (
    artifact_processor,
    open_sqlite_db_readonly,
    utf8_in_extended_ascii,
    check_in_media,
    convert_ts_human_to_utc,
    logfunc,
)
from scripts.sqlite_wal import (KIND_COMMITTED, KIND_EARLIER, KIND_UNCOMMITTED,
                                rows_not_in_current)

_DECODE_ERRORS = (DecodeError, KeyError, ValueError, TypeError, IndexError, AttributeError)


GUID_RE = re.compile(
    r"[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}",
    re.IGNORECASE)


def _container_guid(evidence_path):
    """The app container GUID in a path inside the extraction, or '' when there is none.

    The container as iOS lays it out, .../Application/<GUID>/. Taking the first match
    anywhere in the path meant an output directory or case folder whose name looks like a
    GUID could be picked instead, and the media lookup would then search a directory that
    does not exist and quietly find nothing. The caller passes the path inside the
    extraction, without the examiner's folders, so the fallback cannot take a GUID from
    the output or case folder either: an iTunes backup stages app files under
    .../Application/<bundle id>/, with no GUID in the path at all.
    """
    parts = os.path.normpath(evidence_path).split(os.sep)
    for index in range(len(parts) - 1, 0, -1):
        if GUID_RE.fullmatch(parts[index]) and parts[index - 1] == 'Application':
            return parts[index]
    for part in reversed(parts):
        if GUID_RE.fullmatch(part):
            return part
    return ''


def _attachment_names(annotations):
    """The attachment file names in a decoded annotation field, in stored order.

    The name is read from field 10.3 of each annotation, by position; the position was not
    sourced. Annotations without it are skipped.
    """
    if not isinstance(annotations, list):
        annotations = [annotations]
    names = []
    for annotation in annotations:
        attachment = annotation.get('10') if isinstance(annotation, dict) else None
        name = attachment.get('3') if isinstance(attachment, dict) else None
        if isinstance(name, bytes):
            names.append(name.decode('utf-8', 'replace'))
    return names


# topic_messages is unique on (group_id, topic_id, id) (its IDXU_ index); row_id is not the
# message, because a rewritten row takes a new row_id. The message query ends with those three.
_KEY = slice(-3, None)
_WAL_KINDS = (KIND_COMMITTED, KIND_EARLIER, KIND_UNCOMMITTED)
_ORIGIN_LIVE = 'Live'
_ORIGIN_RECOVERED = 'Recovered'
_ORIGIN_EARLIER = 'Earlier version'
_METHOD_WAL_STATES = 'WAL committed states'
_METHOD_WAL_UNCOMMITTED = 'WAL uncommitted frames'


def _recovery_location(name, spans):
    """(method, location) for a row read in the states spans names."""
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


def _current_texts(db_file):
    """{(group_id, topic_id, id): text_body} for every row topic_messages holds now."""
    db = open_sqlite_db_readonly(db_file)
    try:
        return {tuple(row[:3]): row[3] for row in db.execute(
            'SELECT group_id, topic_id, id, text_body FROM topic_messages')}
    except sqlite3.Error:
        return {}
    finally:
        db.close()


def _rows_in_log(db_file, query, text_index, live_texts):
    """Rows of query that another state in the write-ahead log holds, read through
    scripts/sqlite_wal.py with each state's own joins: a message whose key the current state
    does not hold (Recovered), and a non-empty text of a message whose current text differs
    (Earlier version).

    live_texts maps each key topic_messages holds now to its current text, read from the table
    itself rather than the joined query, whose joins can drop a current row. Returns
    [(row, origin, method, location)], one per Recovered key and one per distinct earlier text,
    each as the newest state holding it stored it (a committed state before the previous log
    generation before the frames after the last commit).
    """
    try:
        _columns, found, wal = rows_not_in_current(str(db_file), query, include=_WAL_KINDS)
    except (sqlite3.Error, OSError) as ex:
        logfunc(f'Google Chat: write-ahead log not read: {ex}')
        return []
    if wal.log:
        logfunc(f'Google Chat: {wal.summary()}')
    entries = {}
    for item in found:
        key = tuple(item.values[_KEY])
        text = item.values[text_index]
        if key in live_texts:
            if not text or text == live_texts[key]:
                continue
            slot, origin = (key, text), _ORIGIN_EARLIER
        else:
            slot, origin = (key,), _ORIGIN_RECOVERED
        rank = ((2, item.last_state) if item.first_state is not None else
                (1, item.earlier_generation[1]) if item.earlier_generation else (0, 0))
        entry = entries.setdefault(slot, {'row': item.values, 'origin': origin, 'rank': rank,
                                          'committed': None, 'earlier': None})
        if rank > entry['rank']:
            entry['row'], entry['rank'] = item.values, rank
        for part, span in (('committed', (item.first_state, item.last_state)
                            if item.first_state is not None else None),
                           ('earlier', item.earlier_generation)):
            if span:
                old = entry[part]
                entry[part] = span if old is None else (min(old[0], span[0]), max(old[1], span[1]))
    name = os.path.basename(str(db_file))
    return [(entry['row'], entry['origin'], *_recovery_location(name, entry))
            for entry in entries.values()]


@artifact_processor
def google_chat(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Is Sent',
        'Message Author',
        'Message',
        ('Media', 'media'),
        'Group Type',
        'Conversation Name',
        'Filename',
        'Reaction',
        'Reaction User',
        'Account ID',
        'Record Origin',
        'Recovery Method',
        'Recovery Location',
    )
    data_list = []
    source_path = ''

    for file_found in context.get_files_found():
        file_found = str(file_found)

        if not file_found.endswith('dynamite.db'):
            continue

        source_path = file_found
        evidence_path = context.get_relative_path(file_found)
        guid = _container_guid(evidence_path)
        if not guid:
            logfunc(f'Google Chat: no app container GUID in {evidence_path}; '
                    'attachments cannot be matched for this database')
        account_id = os.path.basename(os.path.dirname(file_found))

        query = f'''
        SELECT
            datetime(topic_messages.create_time/1000000,'unixepoch') AS "Message Time",
            CASE
            WHEN group_type=1 THEN "Group Message"
            WHEN group_type=2 THEN "1-to-1 Message"
            ELSE group_type
            END AS "Group Type",
            Groups.name AS "Conversation Name",
            users.name AS "Message Author",
            topic_messages.text_body AS "Message",
            topic_messages.reactions AS "Message Reactions",
            topic_messages.annotation AS "Message Annotation (Possible Attachment Information)",
            CASE
                WHEN topic_messages.creator_id = '{account_id}' THEN 1
                ELSE 0
            END is_sent,
            topic_messages.group_id,
            topic_messages.topic_id,
            topic_messages.id
        FROM
        topic_messages
        JOIN users ON users.user_id=topic_messages.creator_id
        JOIN Groups ON Groups.group_id=topic_messages.group_id
        ORDER BY "Message Time" ASC
        '''
        db = open_sqlite_db_readonly(file_found)
        live = db.execute(query).fetchall()
        db.close()
        records = [(row, _ORIGIN_LIVE, '', '') for row in live]
        records.extend(_rows_in_log(file_found, query, 4, _current_texts(file_found)))

        for row, origin, method, location in records:
            media_ref_id = ''
            protobufreactions = row[5]
            checkforempty = BytesIO(protobufreactions)
            check = checkforempty.read(3)

            if check == b'\xfe\xff\x00':
                reaction = ''
                reactionuser = ''
            else:
                try:
                    protostuff, _types = blackboxprotobuf.decode_message(protobufreactions)
                    reaction = (protostuff['1']['1']['1']['1']).decode()
                    reaction = (utf8_in_extended_ascii(reaction))[1]

                    reactionuser = protostuff['1'].get('2')
                    if reactionuser is not None:
                        reactionuser = protostuff['1']['2']['1']
                        reactionuser = (reactionuser.decode())
                    else:
                        reactionuser = ''
                except _DECODE_ERRORS as ex:
                    logfunc(f'Google Chat: could not decode reactions for message '
                            f'{row[7]}: {ex}')
                    reaction = ''
                    reactionuser = ''

            protobufmedia = row[6]
            checkforempty = BytesIO(protobufmedia)
            check = checkforempty.read(3)

            if check == b'\xfe\xff\x00':
                mediafilename = ''
            else:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(protobufmedia)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Google Chat: could not decode media reference for message '
                            f'{row[7]}: {ex}')
                    protostuff = {'1': {}}
                # Field 1 holds one annotation, or a list of them when there are several.
                # Each list entry is read the same way as a single annotation. A list used to
                # be labelled 'Group List', with every string in it put in the Media column,
                # where nothing could show it, and an attachment in it was never looked for.
                names = _attachment_names(protostuff.get('1'))
                mediafilename = ', '.join(names)
                media_refs = []
                for name in names:
                    pattern_name = re.sub(r'([*?[])', r'[\1]', name)
                    attachment = guid and context.get_seeker().search(
                        f'*/{guid}/tmp/{pattern_name}', return_on_first_hit=True)
                    media_ref = check_in_media(attachment, name=name) if attachment else None
                    if media_ref:
                        media_refs.append(media_ref)
                if len(media_refs) == 1:
                    media_ref_id = media_refs[0]
                elif media_refs:
                    media_ref_id = media_refs

            timestamp = convert_ts_human_to_utc(row[0]) if row[0] else row[0]

            data_list.append((
                timestamp,
                row[7],
                row[3],
                row[4],
                media_ref_id,
                row[1],
                row[2],
                mediafilename,
                reaction,
                reactionuser,
                account_id,
                origin,
                method,
                location,
            ))

        break

    return data_headers, data_list, source_path
