__artifacts_v2__ = {
    "google_chat": {  # This should match the function name exactly
        "name": "Google Chat",
        "description": "Messages from the first Google Chat dynamite.db matched",
        "author": "@AlexisBrignoni",
        "creation_date": "2023-09-03",
        "last_update_date": "2026-10-14",
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
                 "bundle id, no attachment is looked for and Media is blank.",
        "paths": ('*/Documents/user_accounts/*/dynamite.db*',
                  '*/Documents/user_accounts/*/tmp/*'),
        "output_types": "all",  # or ["html", "tsv", "timeline", "lava"]
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
            "iphone11_ios17": "iOS 17.3 | Google Chat 0.390 | 96 rows",
            "magnet_ios16": "iOS 16.1.1 | Gmail - Email by Google 6.0.221127 | 5 rows",
        }
    }
}

import os
from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
import re
from io import BytesIO

from scripts.ilapfuncs import (
    artifact_processor,
    open_sqlite_db_readonly,
    utf8_in_extended_ascii,
    check_in_media,
    convert_ts_human_to_utc,
    logfunc,
)

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

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute(f'''
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
            END is_sent
        FROM
        topic_messages
        JOIN users ON users.user_id=topic_messages.creator_id
        JOIN Groups ON Groups.group_id=topic_messages.group_id
        ORDER BY "Message Time" ASC
        ''')

        for row in cursor.fetchall():
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
                    attachment = guid and context.get_seeker().search(
                        f'*/{guid}/tmp/{re.sub(r"([*?[])", r"[\1]", name)}',
                        return_on_first_hit=True)
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
            ))

        break

    return data_headers, data_list, source_path
