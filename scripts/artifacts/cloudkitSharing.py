__artifacts_v2__ = {
    "get_cloudkitServerSharedData": {
        "name": "Cloudkit Participants",
        "description": "CloudKit Participants - Cloudkit accounts participating in CloudKit shares.",
        "author": "@DFIRScience",
        "creation_date": "2022-08-09",
        "last_update_date": "2025-09-26",
        "requirements": "none",
        "category": "CloudKit",
        "notes": "",
        "paths": ('*NoteStore.sqlite*',),
    },
    "get_cloudkitServerSharedData": {
        "name": "Cloudkit Note Sharing",
        "description": "CloudKit Note Sharing - Notes information shared via CloudKit. Look up the Record ID in the ZICCLOUDSYYNCINGOBJECT.ZIDENTIFIER column. ",
        "author": "@DFIRScience",
        "creation_date": "2022-08-09",
        "last_update_date": "2025-09-26",
        "requirements": "none",
        "category": "CloudKit",
        "notes": "",
        "paths": ('*NoteStore.sqlite*',),
    }
}

import nska_deserialize as nd
import io

from scripts.ilapfuncs import open_sqlite_db_readonly, artifact_processor

@artifact_processor
def get_cloudkitServerSharedData(context):
    user_dictionary = {}
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('NoteStore.sqlite'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT Z_PK, ZSERVERSHAREDATA 
            FROM
            ZICCLOUDSYNCINGOBJECT
            WHERE
            ZSERVERSHAREDATA NOT NULL
            ''')

            all_rows = cursor.fetchall()
            for row in all_rows:

                # filename = os.path.join(report_folder, 'zserversharedata_' + str(row[0]) + '.bplist')
                # output_file = open(filename, "wb")
                # output_file.write(row[1])
                # output_file.close()

                deserialized_plist = nd.deserialize_plist(io.BytesIO(row[1]))
                for item in deserialized_plist:
                    if 'Participants' in item:
                        for participant in item['Participants']:
                            record_id = participant['UserIdentity']['UserRecordID']['RecordName']
                            email_address = participant['UserIdentity']['LookupInfo']['EmailAddress']
                            phone_number = participant['UserIdentity']['LookupInfo']['PhoneNumber']
                            first_name = participant['UserIdentity']['NameComponents']['NS.nameComponentsPrivate']['NS.givenName']
                            middle_name = participant['UserIdentity']['NameComponents']['NS.nameComponentsPrivate']['NS.middleName']
                            last_name = participant['UserIdentity']['NameComponents']['NS.nameComponentsPrivate']['NS.familyName']
                            name_prefix = participant['UserIdentity']['NameComponents']['NS.nameComponentsPrivate']['NS.namePrefix']
                            name_suffix = participant['UserIdentity']['NameComponents']['NS.nameComponentsPrivate']['NS.nameSuffix']
                            nickname = participant['UserIdentity']['NameComponents']['NS.nameComponentsPrivate']['NS.nickname']

                            user_dictionary[record_id] = [record_id, email_address, phone_number, name_prefix, first_name,
                                                        middle_name, last_name, name_suffix, nickname, file_found]
            db.close()

    # Build the array after dealing with all the files 
    user_list = list(user_dictionary.values())
    user_headers = (
        'Record ID', 'Email Address', ('Phone Number', 'phonenumber'), 'Name Prefix', 'First Name', 'Middle Name', 'Last Name',
        'Name Suffix', 'Nickname', 'Source File')
    
    return user_headers, user_list, ''

@artifact_processor
def get_cloudkitServerRecordData(context):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('NoteStore.sqlite'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            select z_pk, zserverrecorddata 
            from
            ziccloudsyncingobject
            where
            zserverrecorddata not null
            ''')

            note_data = []
            all_rows = cursor.fetchall()
            for row in all_rows:
                # filename = os.path.join(report_folder, 'zserverrecorddata_' + str(row[0]) + '.bplist')
                # output_file = open(filename, "wb")
                # output_file.write(row[1])
                # output_file.close()

                deserialized_plist = nd.deserialize_plist(io.BytesIO(row[1]))
                creator_id = ''
                last_modified_id = ''
                creation_date = ''
                last_modified_date = ''
                last_modified_device = ''
                record_type = ''
                record_id = ''
                for item in deserialized_plist:
                    if 'RecordCtime' in item:
                        creation_date = item['RecordCtime']
                    elif 'RecordMtime' in item:
                        last_modified_date = item['RecordMtime']
                    elif 'LastModifiedUserRecordID' in item:
                        last_modified_id = item['LastModifiedUserRecordID']['RecordName']
                    elif 'CreatorUserRecordID' in item:
                        creator_id = item['CreatorUserRecordID']['RecordName']
                    elif 'ModifiedByDevice' in item:
                        last_modified_device = item['ModifiedByDevice']
                    elif 'RecordType' in item:
                        record_type = item['RecordType']
                    elif 'RecordID' in item:
                        record_id = item['RecordID']['RecordName']

                note_data.append([record_id, record_type, creation_date, creator_id, last_modified_date, last_modified_id,
                                last_modified_device, file_found])
                note_headers = (
                'Record ID', 'Record Type', 'Creation Date', 'Creator ID', 'Modified Date', 'Modifier ID', 'Modifier Device', 'Source File')
                
                db.close()
                
    return note_headers, note_data, ''

