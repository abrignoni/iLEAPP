""" cloudkitSharing """
__artifacts_v2__ = {
    "cloudkit_sharing": {
        "name": "CloudKit Shares",
        "description": "Processes CloudKit sharing data from NoteStore.sqlite",
        "author": "@DFIRScience",
        "creation_date": "2022-08-09",
        "last_update_date": "2026-05-28",
        "requirements": "none",
        "category": "Cloudkit",
        "notes": "",
        "paths": ('*NoteStore.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "share-2",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | group.com.apple.notes | 3 rows",
            "dexter_ios18": "iOS 18.3.2 | group.com.apple.notes | 9 rows",
            "felix_ios17": "iOS 17.6.1 | group.com.apple.notes | 12 rows",
            "fsfull002_ios17": "iOS 17.1 | group.com.apple.notes | 4 rows",
            "hc_ios18_7": "iOS 18.7.8 | group.com.apple.notes | 10 rows",
            "iphone11_ios17": "iOS 17.3 | group.com.apple.notes | 35 rows",
            "iphone12_ios18": "iOS 18.7 | group.com.apple.notes | 40 rows",
            "iphone14plus_ios18": "iOS 18.0 | group.com.apple.notes | 0 rows",
            "otto_ios17": "iOS 17.5.1 | group.com.apple.notes | 11 rows",
        }
    },
    "cloudkit_participants": {
        "name": "CloudKit Share Participants",
        "description": "Processes CloudKit participant data from NoteStore.sqlite",
        "author": "@DFIRScience",
        "creation_date": "2022-08-09",
        "last_update_date": "2026-05-28",
        "requirements": "none",
        "category": "Cloudkit",
        "notes": "",
        "paths": ('*NoteStore.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | group.com.apple.notes | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | group.com.apple.notes | 0 rows",
            "felix_ios17": "iOS 17.6.1 | group.com.apple.notes | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | group.com.apple.notes | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | group.com.apple.notes | 0 rows",
            "iphone11_ios17": "iOS 17.3 | group.com.apple.notes | 6 rows",
            "iphone12_ios18": "iOS 18.7 | group.com.apple.notes | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | group.com.apple.notes | 0 rows",
            "otto_ios17": "iOS 17.5.1 | group.com.apple.notes | 0 rows",
        }
    }
}

import os
import io
import nska_deserialize as nd
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def deep_get(data, path, default=''):
    """Safe nested dictionary access."""
    for key in path:
        if not isinstance(data, dict):
            return default
        data = data.get(key)
        if data is None:
            return default
    return data


def as_dict(data):
    """Return a dictionary only when the plist value has that shape."""
    return data if isinstance(data, dict) else {}


def as_list(data):
    """Normalize plist values that may be a single dict, list, or scalar."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    return []


def write_debug_bplist(report_folder, prefix, z_pk, data):
    """Writes extracted blobs to the report folder for validation."""
    filename = os.path.join(report_folder, f'{prefix}_{z_pk}.bplist')
    with open(filename, "wb") as f:
        f.write(data)


@artifact_processor
def cloudkit_sharing(context):
    """ See artifact description """
    data_list = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('NoteStore.sqlite'):
            continue

        # Dictionary to merge share and record data by Z_PK
        shares = {}

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        # 1. Process Server Record Data
        cursor.execute('SELECT Z_PK, ZIDENTIFIER, ZSERVERRECORDDATA '
                       'FROM ZICCLOUDSYNCINGOBJECT WHERE ZSERVERRECORDDATA IS NOT NULL')
        for row in cursor:
            z_pk, z_id, blob = row
            write_debug_bplist(context.get_report_folder(), 'zserverrecorddata', z_pk, blob)

            deserialized = nd.deserialize_plist(io.BytesIO(blob))

            record_items = [x for x in as_list(deserialized) if isinstance(x, dict) and 'RecordID' in x]

            for item in record_items:
                shares[z_pk] = {
                    'z_id': z_id,
                    'record_id': deep_get(item, ['RecordID', 'RecordName']),
                    'record_type': item.get('RecordType', ''),
                    'ctime': item.get('RecordCtime', ''),
                    'creator': deep_get(item, ['CreatorUserRecordID', 'RecordName']),
                    'mtime': item.get('RecordMtime', ''),
                    'modifier': deep_get(item, ['LastModifiedUserRecordID', 'RecordName']),
                    'device': item.get('ModifiedByDevice', ''),
                    'root_id': '',  # Filled by share data if available
                    'container': '',
                    'hostname': '',
                    'permission': '',
                    'visibility': '',
                    'anon': '',
                    'known': ''
                }
                break # Only take the first matching record item per Z_PK

        # 2. Process Server Share Data
        cursor.execute('SELECT Z_PK, ZIDENTIFIER, ZSERVERSHAREDATA '
                       'FROM ZICCLOUDSYNCINGOBJECT WHERE ZSERVERSHAREDATA IS NOT NULL')
        for row in cursor:
            z_pk, z_id, blob = row
            write_debug_bplist(context.get_report_folder(), 'zserversharedata', z_pk, blob)

            deserialized = nd.deserialize_plist(io.BytesIO(blob))

            share_items = [x for x in as_list(deserialized) if isinstance(x, dict) and 'RecordID' in x]

            for item in share_items:
                if z_pk not in shares:
                    shares[z_pk] = {
                        'z_id': z_id,
                        'record_id': deep_get(item, ['RecordID', 'RecordName']),
                        'record_type': '',
                        'ctime': '',
                        'creator': '',
                        'mtime': '',
                        'modifier': '',
                        'device': ''
                    }

                shares[z_pk].update({
                    'root_id': deep_get(item, ['RootRecordID', 'RecordName']),
                    'container': deep_get(item, ['ContainerID', 'ContainerIdentifier']),
                    'hostname': item.get('DisplayedHostname', ''),
                    'permission': item.get('PublicPermission', ''),
                    'visibility': item.get('ParticipantVisibility', ''),
                    'anon': item.get('AllowsAnonymousAccess', ''),
                    'known': item.get('KnownToServer', '')
                })
                break # Only take the first matching share item per Z_PK

        db.close()

        for z_pk, s in shares.items():
            data_list.append((
                context.get_relative_path(file_found), z_pk, s['z_id'], s['record_id'],
                s['root_id'], s['record_type'],
                s['ctime'], s['creator'], s['mtime'], s['modifier'], s['device'],
                s['container'], s['hostname'], s['permission'], s['visibility'],
                s['anon'], s['known']
            ))

    data_headers = (
        'Source File', 'Source Z_PK', 'ZIDENTIFIER', 'Record ID', 'Root Record ID', 'Record Type',
        ('Creation Date', 'datetime'), 'Creator User Record ID', ('Modified Date', 'datetime'),
        'Last Modified User Record ID', 'Modified By Device', 'Container Identifier',
        'Displayed Hostname', 'Public Permission', 'Participant Visibility',
        'Allows Anonymous Access', 'Known To Server'
    )
    return data_headers, data_list, 'NoteStore.sqlite'


@artifact_processor
def cloudkit_participants(context):
    """ See artifact description """
    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('NoteStore.sqlite'):
            continue

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('SELECT Z_PK, ZIDENTIFIER, ZSERVERSHAREDATA '
                       'FROM ZICCLOUDSYNCINGOBJECT WHERE ZSERVERSHAREDATA IS NOT NULL')

        for row in cursor:
            z_pk, z_id, blob = row
            deserialized = nd.deserialize_plist(io.BytesIO(blob))

            share_items = [x for x in as_list(deserialized) if isinstance(x, dict) and 'Participants' in x]

            for item in share_items:
                share_record_id = deep_get(item, ['RecordID', 'RecordName'])
                root_record_id = deep_get(item, ['RootRecordID', 'RecordName'])

                participants = as_list(item.get('Participants'))
                for p in participants:
                    p = as_dict(p)
                    if not p:
                        continue
                    ui = as_dict(p.get('UserIdentity'))
                    name_priv = deep_get(ui, ['NameComponents', 'NS.nameComponentsPrivate'], {})
                    name_priv = as_dict(name_priv)

                    data_list.append((
                        context.get_relative_path(file_found),
                        z_pk,
                        z_id,
                        share_record_id,
                        root_record_id,
                        p.get('ParticipantID', ''),
                        deep_get(ui, ['UserRecordID', 'RecordName']),
                        deep_get(ui, ['LookupInfo', 'EmailAddress']),
                        deep_get(ui, ['LookupInfo', 'PhoneNumber']),
                        p.get('Type', ''),
                        p.get('AcceptanceStatus', ''),
                        p.get('Permission', ''),
                        p.get('OriginalType', ''),
                        p.get('OriginalAcceptanceStatus', ''),
                        p.get('OriginalPermission', ''),
                        p.get('IsCurrentUser', ''),
                        p.get('InviterID', ''),
                        p.get('HasICloudAccount', ''),
                        p.get('InvitationTokenStatus', ''),
                        p.get('WantsNewInvitationToken', ''),
                        p.get('IsAnonymousInvitedParticipant', ''),
                        p.get('CreatedInProcess', ''),
                        p.get('AcceptedInProcess', ''),
                        name_priv.get('NS.namePrefix', ''),
                        name_priv.get('NS.givenName', ''),
                        name_priv.get('NS.middleName', ''),
                        name_priv.get('NS.familyName', ''),
                        name_priv.get('NS.nameSuffix', ''),
                        name_priv.get('NS.nickname', '')
                    ))
        db.close()

    data_headers = (
        'Source File', 'Source Z_PK', 'ZIDENTIFIER', 'Share Record ID', 'Root Record ID',
        'Participant ID', 'Participant User Record ID', 'Email Address',
        ('Phone Number', 'phonenumber'),
        'Participant Type', 'Acceptance Status', 'Permission', 'Original Participant Type',
        'Original Acceptance Status', 'Original Permission', 'Is Current User', 'Inviter ID',
        'Has iCloud Account', 'Invitation Token Status', 'Wants New Invitation Token',
        'Is Anonymous Invited Participant', 'Created In Process', 'Accepted In Process',
        'Name Prefix', 'First Name', 'Middle Name', 'Last Name', 'Name Suffix', 'Nickname'
    )
    return data_headers, data_list, 'NoteStore.sqlite'
