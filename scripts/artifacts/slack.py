__artifacts_v2__ = {
    "slackModelMessages": {
        "name": "Slack - Messages (ModelDatabase)",
        "description": "Slack chat messages from the newer ModelDatabase (ZCOREDATA*) schema",
        "author": "", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "Slack", "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/*/ModelDatabase/db.sqlite*',),
        "output_types": "standard", "artifact_icon": "message-circle"
    },
    "slackModelUsers": {
        "name": "Slack - User Data (ModelDatabase)",
        "description": "Slack users from the newer ModelDatabase (ZCOREDATAUSER) schema",
        "author": "", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "Slack", "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/*/ModelDatabase/db.sqlite*',),
        "output_types": "standard", "artifact_icon": "users"
    },
    "slackModelChannels": {
        "name": "Slack - Channel Data (ModelDatabase)",
        "description": "Slack channels/DMs from the newer ModelDatabase schema",
        "author": "", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "Slack", "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/*/ModelDatabase/db.sqlite*',),
        "output_types": "standard", "artifact_icon": "hash"
    },
    "slackMessages": {
        "name": "Slack - Messages",
        "description": "Slack chat messages from main_db (ZSLK*/ZSLKDEPRECATED* schema)",
        "author": "", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "Slack", "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/Slack/*/*/main_db*',),
        "output_types": "standard", "artifact_icon": "message-circle"
    },
    "slackUsers": {
        "name": "Slack - User Data",
        "description": "Slack users from main_db (ZSLK*/ZSLKDEPRECATED* schema)",
        "author": "", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "Slack", "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/Slack/*/*/main_db*',),
        "output_types": "standard", "artifact_icon": "users"
    },
    "slackAttachments": {
        "name": "Slack - Attachments",
        "description": "Slack messages with shared file attachments (main_db)",
        "author": "", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "Slack", "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/Slack/*/*/main_db*',),
        "output_types": "standard", "artifact_icon": "paperclip"
    },
    "slackChannels": {
        "name": "Slack - Channel Data",
        "description": "Slack channels from main_db (ZSLK*/ZSLKDEPRECATED* schema)",
        "author": "", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "Slack", "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/Slack/*/*/main_db*',),
        "output_types": "standard", "artifact_icon": "hash"
    },
    "slackTeams": {
        "name": "Slack - Team Data",
        "description": "Slack workspaces/teams from main_db (ZSLK*/ZSLKDEPRECATED* schema)",
        "author": "", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "Slack", "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/Slack/*/*/main_db*',),
        "output_types": "standard", "artifact_icon": "briefcase"
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, does_table_exist_in_db


def _find_model_db(context):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if 'ModelDatabase' in file_found and file_found.endswith('db.sqlite'):
            return file_found
    return ''


def _find_main_db(context):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('main_db'):
            return file_found
    return ''


def _slack_prefix(db_path):
    """main_db tables are ZSLK*; older databases use ZSLKDEPRECATED*. Return the live prefix or None."""
    if does_table_exist_in_db(db_path, 'ZSLKDEPRECATEDMESSAGE'):
        return 'ZSLKDEPRECATED'
    if does_table_exist_in_db(db_path, 'ZSLKMESSAGE'):
        return 'ZSLK'
    return None


# ---------------------------------------------------------------------------
# ModelDatabase (newer ZCOREDATA* schema)
# ---------------------------------------------------------------------------
@artifact_processor
def slackModelMessages(context):
    data_headers = (('Timestamp', 'datetime'), 'Sender ID', 'Sender Name', 'Channel Name',
                    'Message', 'Conversation ID', 'Group ID')
    data_list = []
    db_path = _find_model_db(context)
    if not db_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        datetime(ZCOREDATAMESSAGE.ZTIMESTAMP, 'unixepoch'),
        ZCOREDATAMESSAGE.ZUSERID,
        ZCOREDATAUSER.ZREALNAME,
        ZCOREDATACONVERSATION.ZNAME,
        ZCOREDATAMESSAGE.ZTEXT,
        ZCOREDATAMESSAGE.ZCONVERSATIONID,
        ZCOREDATACONVERSATION.ZCONTEXTTEAMID
    FROM ZCOREDATAMESSAGE
    LEFT OUTER JOIN ZCOREDATAUSER ON ZCOREDATAMESSAGE.ZUSERID = ZCOREDATAUSER.ZTSID
    LEFT OUTER JOIN ZCOREDATACONVERSATION ON ZCOREDATAMESSAGE.ZCONVERSATIONID = ZCOREDATACONVERSATION.ZTSID
    '''
    for row in get_sqlite_db_records(db_path, query):
        data_list.append(tuple(row))
    return data_headers, data_list, context.get_relative_path(db_path)


@artifact_processor
def slackModelUsers(context):
    data_headers = (('User Sync Timestamp', 'datetime'), 'Real Name', 'First Name', 'Last Name',
                    'User Name', 'Email', 'Phone', 'Team ID', 'Workspace ID', 'User ID',
                    'Local User', 'Owner', 'Admin', 'Bot', 'Timezone', 'Timezone Title',
                    'Timezone Offset (Hours)', 'Avatar Hash', 'Color String')
    data_list = []
    db_path = _find_model_db(context)
    if not db_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        datetime(ZSERVERVERSION, 'unixepoch'),
        ZREALNAME, ZFIRSTNAME, ZLASTNAME, ZNAME, ZEMAIL, ZPHONE, ZTEAMID,
        ZWORKSPACEORENTERPRISEID, ZTSID,
        CASE ZISME WHEN 0 THEN '' WHEN 1 THEN 'Yes' END,
        CASE ZISOWNER WHEN 0 THEN '' WHEN 1 THEN 'Yes' END,
        CASE ZISADMIN WHEN 0 THEN '' WHEN 1 THEN 'Yes' END,
        CASE ZISBOT WHEN 0 THEN '' WHEN 1 THEN 'Yes' END,
        ZTIMEZONE, ZTIMEZONETITLE, ZTIMEZONEOFFSET/3600, ZAVATARHASH, ZCOLORSTRING
    FROM ZCOREDATAUSER
    '''
    for row in get_sqlite_db_records(db_path, query):
        data_list.append(tuple(row))
    return data_headers, data_list, context.get_relative_path(db_path)


@artifact_processor
def slackModelChannels(context):
    data_headers = (('Created Timestamp', 'datetime'), ('First Message Timestamp', 'datetime'),
                    'Creator ID', 'Creator Name', 'Channel Name', 'Channel ID', 'DM User ID',
                    'Channel Description', 'Channel Type')
    data_list = []
    db_path = _find_model_db(context)
    if not db_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        datetime(ZCOREDATACONVERSATION.ZCREATED, 'unixepoch'),
        datetime(ZCOREDATACONVERSATION.ZFIRSTMESSAGETIMESTAMP, 'unixepoch'),
        ZCOREDATACONVERSATION.ZCREATORID,
        ZCOREDATAUSER.ZREALNAME,
        ZCOREDATACONVERSATION.ZNAME,
        ZCOREDATACONVERSATION.ZTSID,
        ZCOREDATACONVERSATION.ZIMUSERID,
        ZCOREDATACONVERSATION.ZPURPOSETEXT,
        CASE ZCOREDATACONVERSATION.ZTYPE WHEN 0 THEN 'Channel' WHEN 2 THEN 'Direct Message' END
    FROM ZCOREDATACONVERSATION
    LEFT OUTER JOIN ZCOREDATAUSER ON ZCOREDATACONVERSATION.ZCREATORID = ZCOREDATAUSER.ZTSID
    '''
    for row in get_sqlite_db_records(db_path, query):
        data_list.append(tuple(row))
    return data_headers, data_list, context.get_relative_path(db_path)


# ---------------------------------------------------------------------------
# main_db (ZSLK* / ZSLKDEPRECATED* schema)
# ---------------------------------------------------------------------------
@artifact_processor
def slackMessages(context):
    data_headers = (('Timestamp', 'datetime'), 'Sender ID', 'Sender Name', 'Channel Name',
                    'Message', 'Shared File', 'Channel ID', 'Channel SID', 'Channel SID1', 'User SID')
    data_list = []
    db_path = _find_main_db(context)
    if not db_path:
        return data_headers, data_list, ''
    p = _slack_prefix(db_path)
    if not p:
        return data_headers, data_list, context.get_relative_path(db_path)

    query = f'''
    SELECT DISTINCT
        datetime({p}MESSAGE.ZTIMESTAMP, 'unixepoch'),
        {p}MESSAGE.ZUSERID,
        {p}COREDATAUSER.ZREALNAME,
        {p}BASECHANNEL.ZNAME,
        {p}MESSAGE.ZTEXT,
        json_extract(ZFILEIDS, '$[0]'),
        {p}MESSAGE.ZCHANNELID,
        {p}BASECHANNEL.ZTSID,
        {p}BASECHANNEL.ZTSID1,
        {p}COREDATAUSER.ZTSID
    FROM {p}MESSAGE, {p}BASECHANNEL, {p}COREDATAUSER
    WHERE {p}COREDATAUSER.ZTSID = {p}MESSAGE.ZUSERID
        AND ({p}BASECHANNEL.ZTSID = {p}MESSAGE.ZCHANNELID
             OR {p}BASECHANNEL.ZTSID1 = {p}MESSAGE.ZCHANNELID)
    ORDER BY {p}MESSAGE.ZTIMESTAMP
    '''
    for row in get_sqlite_db_records(db_path, query):
        data_list.append(tuple(row))
    return data_headers, data_list, context.get_relative_path(db_path)


@artifact_processor
def slackUsers(context):
    data_headers = ('Admin', 'Owner', 'Real Name', 'First Name', 'Last Name', 'Display Name',
                    'Name', 'Phone', 'Timezone', 'Timezone Offset', 'Timezone Title', 'Title',
                    'SID', 'Team ID')
    data_list = []
    db_path = _find_main_db(context)
    if not db_path:
        return data_headers, data_list, ''
    p = _slack_prefix(db_path)
    if not p:
        return data_headers, data_list, context.get_relative_path(db_path)

    query = f'''
    SELECT
        {p}COREDATAUSER.ZADMIN, {p}COREDATAUSER.ZOWNER, {p}COREDATAUSER.ZREALNAME,
        {p}COREDATAUSER.ZFIRSTNAME, {p}COREDATAUSER.ZLASTNAME, {p}COREDATAUSER.ZDISPLAYNAME,
        {p}COREDATAUSER.ZNAME, {p}COREDATAUSER.ZPHONE, {p}COREDATAUSER.ZTIMEZONE,
        {p}COREDATAUSER.ZTIMEZONEOFFSET, {p}COREDATAUSER.ZTIMEZONETITLE, {p}COREDATAUSER.ZTITLE,
        {p}COREDATAUSER.ZTSID, {p}COREDATAUSER.ZTEAMID
    FROM {p}COREDATAUSER
    '''
    for row in get_sqlite_db_records(db_path, query):
        data_list.append(tuple(row))
    return data_headers, data_list, context.get_relative_path(db_path)


@artifact_processor
def slackAttachments(context):
    data_headers = (('Timestamp', 'datetime'), 'Sender ID', 'Sender Name', 'Channel Name',
                    'Message', 'Shared File', 'Mode', 'Title', 'Type', ('File Timestamp', 'datetime'),
                    'Preview', 'Size', 'Private Download URL', 'Permalink URL', 'Channel ID',
                    'Channel SID', 'Channel SID1', 'User SID')
    data_list = []
    db_path = _find_main_db(context)
    if not db_path:
        return data_headers, data_list, ''
    p = _slack_prefix(db_path)
    if not p:
        return data_headers, data_list, context.get_relative_path(db_path)
    file_ts = 'ZTIMESTAMPNUMBER' if p == 'ZSLKDEPRECATED' else 'ZTIMESTAMP'

    query = f'''
    SELECT DISTINCT
        datetime({p}MESSAGE.ZTIMESTAMP, 'unixepoch'),
        {p}MESSAGE.ZUSERID,
        {p}COREDATAUSER.ZREALNAME,
        {p}BASECHANNEL.ZNAME,
        {p}MESSAGE.ZTEXT,
        json_extract(ZFILEIDS, '$[0]') as HasSharedFile,
        {p}FILE.ZMODESTRING,
        {p}FILE.ZTITLE,
        {p}FILE.ZTYPESTRING,
        datetime({p}FILE.{file_ts}, 'unixepoch'),
        {p}FILE.ZPREVIEW,
        {p}FILE.ZSIZE,
        {p}FILE.ZPRIVATEDOWNLOADURL,
        {p}FILE.ZPERMALINKURL,
        {p}MESSAGE.ZCHANNELID,
        {p}BASECHANNEL.ZTSID,
        {p}BASECHANNEL.ZTSID1,
        {p}COREDATAUSER.ZTSID
    FROM {p}MESSAGE, {p}BASECHANNEL, {p}COREDATAUSER, {p}FILE
    WHERE {p}COREDATAUSER.ZTSID = {p}MESSAGE.ZUSERID
        AND ({p}BASECHANNEL.ZTSID = {p}MESSAGE.ZCHANNELID
             OR {p}BASECHANNEL.ZTSID1 = {p}MESSAGE.ZCHANNELID)
        AND HasSharedFile = {p}FILE.ZTSID
    ORDER BY {p}MESSAGE.ZTIMESTAMP
    '''
    for row in get_sqlite_db_records(db_path, query):
        data_list.append(tuple(row))
    return data_headers, data_list, context.get_relative_path(db_path)


@artifact_processor
def slackChannels(context):
    data_headers = (('Timestamp Created', 'datetime'), ('Purpose Last Set', 'datetime'),
                    ('Topic Last Set', 'datetime'), ('Latest', 'datetime'), 'Channel Names',
                    'DM Channels', 'Other Channels', 'User ID', 'Creator ID', 'Purpose Creator ID',
                    'Purpose Text', 'Topic Creator ID', 'Topic Text')
    data_list = []
    db_path = _find_main_db(context)
    if not db_path:
        return data_headers, data_list, ''
    p = _slack_prefix(db_path)
    if not p:
        return data_headers, data_list, context.get_relative_path(db_path)

    query = f'''
    SELECT
        datetime({p}BASECHANNEL.ZCREATED, 'unixepoch'),
        datetime({p}BASECHANNEL.ZPURPOSELASTSET, 'unixepoch'),
        datetime({p}BASECHANNEL.ZTOPICLASTSET, 'unixepoch'),
        datetime({p}BASECHANNEL.ZLATEST, 'unixepoch'),
        {p}BASECHANNEL.ZNAME, {p}BASECHANNEL.ZTSID, {p}BASECHANNEL.ZTSID1,
        {p}BASECHANNEL.ZUSERID, {p}BASECHANNEL.ZCREATORID, {p}BASECHANNEL.ZPURPOSECREATORID,
        {p}BASECHANNEL.ZPURPOSETEXT, {p}BASECHANNEL.ZTOPICCREATORID, {p}BASECHANNEL.ZTOPICTEXT
    FROM {p}BASECHANNEL
    '''
    for row in get_sqlite_db_records(db_path, query):
        data_list.append(tuple(row))
    return data_headers, data_list, context.get_relative_path(db_path)


@artifact_processor
def slackTeams(context):
    data_headers = ('Name', 'Domain Name', 'Author User ID', 'SID')
    data_list = []
    db_path = _find_main_db(context)
    if not db_path:
        return data_headers, data_list, ''
    p = _slack_prefix(db_path)
    if not p:
        return data_headers, data_list, context.get_relative_path(db_path)

    query = f'''
    SELECT {p}TEAM.ZNAME, {p}TEAM.ZDOMAIN, {p}TEAM.ZAUTHUSERID, {p}TEAM.ZTSID
    FROM {p}TEAM
    '''
    for row in get_sqlite_db_records(db_path, query):
        data_list.append(tuple(row))
    return data_headers, data_list, context.get_relative_path(db_path)
