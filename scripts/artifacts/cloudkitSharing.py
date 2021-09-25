import glob
import os
import nska_deserialize as nd
import sqlite3
import datetime
import io

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_cloudkitSharing(files_found, report_folder, seeker):
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('NoteStore.sqlite'):
            get_cloudkitServerRecordData(file_found, report_folder, seeker)
            get_cloudkitServerSharedData(file_found, report_folder, seeker)

def get_cloudkitServerSharedData(file_found, report_folder, seeker):
    user_dictionary = {}

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
        
        filename = os.path.join(report_folder, 'zserversharedata_'+str(row[0])+'.bplist')
        output_file = open(filename, "wb") 
        output_file.write(row[1])
        output_file.close()
        
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
        
                    user_dictionary[record_id] = [record_id, email_address, phone_number, name_prefix, first_name, middle_name, last_name, name_suffix, nickname]
    db.close()

    # Build the array after dealing with all the files 
    user_list = list(user_dictionary.values())

    if len(user_list) > 0:
        description = 'CloudKit Participants - Cloudkit accounts participating in CloudKit shares.'
        report = ArtifactHtmlReport('Participants')
        report.start_artifact_report(report_folder, 'Participants', description)
        report.add_script()
        user_headers = ('Record ID','Email Address','Phone Number','Name Prefix','First Name','Middle Name','Last Name','Name Suffix','Nickname')     
        report.write_artifact_data_table(user_headers, user_list, '', write_location=False)
        report.end_artifact_report()
        
        tsvname = 'Cloudkit Participants'
        tsv(report_folder, user_headers, user_list, tsvname)
    else:
        logfunc('No Cloudkit - Cloudkit Participants data available')
    
def get_cloudkitServerRecordData(file_found, report_folder, seeker):
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
    result_number = len(all_rows)
    if result_number > 0:

        for row in all_rows:
            
            filename = os.path.join(report_folder, 'zserverrecorddata_'+str(row[0])+'.bplist')
            output_file = open(filename, "wb") 
            output_file.write(row[1])
            output_file.close()
            
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
            
            note_data.append([record_id,record_type,creation_date,creator_id,last_modified_date,last_modified_id,last_modified_device])

        description = 'CloudKit Note Sharing - Notes information shared via CloudKit. Look up the Record ID in the ZICCLOUDSYYNCINGOBJECT.ZIDENTIFIER column. '
        report = ArtifactHtmlReport('Note Sharing')
        report.start_artifact_report(report_folder, 'Note Sharing', description)
        report.add_script()
        note_headers = ('Record ID','Record Type','Creation Date','Creator ID','Modified Date','Modifier ID','Modifier Device')     
        report.write_artifact_data_table(note_headers, note_data, file_found)
        report.end_artifact_report()
        
        tsvname = 'Cloudkit Note Sharing'
        tsv(report_folder, note_headers, note_data, tsvname)
    else:
        logfunc('No Cloudkit - Cloudkit Note Sharing data available')

    db.close()
