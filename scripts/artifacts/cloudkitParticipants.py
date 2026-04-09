import glob
import os
import nska_deserialize as nd
import sqlite3
import datetime
import io

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly


def get_cloudkitParticipants(files_found, report_folder, seeker, wrap_text, timezone_offset):

    user_dictionary = {}    

    for file_found in files_found:
        file_found = str(file_found)

        # Can add a separate section for each file this information is found in.
        # This is for Apple Notes.
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
                
                filename = os.path.join(report_folder, 'zserversharedata_'+str(row[0])+'.bplist')
                output_file = open(filename, "wb") 
                output_file.write(row[1])
                output_file.close()
                
                deserialized_plist = nd.deserialize_plist(io.BytesIO(row[1]))
                for item in deserialized_plist:
                    if 'Participants' in item:
                        for participant in item['Participants']:
                            try:
                                if not isinstance(participant, dict) or 'UserIdentity' not in participant:
                                    continue
                                
                                # must be dict and have UserIdentity
                                user_identity = participant.get('UserIdentity')
                                if not isinstance(user_identity, dict):
                                    continue
                                
                                user_record_id = user_identity.get('UserRecordID')
                                if not isinstance(user_record_id, dict):
                                    continue

                                record_id = user_record_id.get('RecordName', '')
                                lookup_info = user_identity.get('LookupInfo', {})
                                email_address = lookup_info.get('EmailAddress', '') if isinstance(lookup_info, dict) else ''
                                phone_number = lookup_info.get('PhoneNumber', '') if isinstance(lookup_info, dict) else ''
                                
                                name_components = user_identity.get('NameComponents', {})
                                if isinstance(name_components, dict):
                                    name_private = name_components.get('NS.nameComponentsPrivate', {})
                                    if isinstance(name_private, dict):
                                        first_name = name_private.get('NS.givenName', '')
                                        middle_name = name_private.get('NS.middleName', '')
                                        last_name = name_private.get('NS.familyName', '')
                                        name_prefix = name_private.get('NS.namePrefix', '')
                                        name_suffix = name_private.get('NS.nameSuffix', '')
                                        nickname = name_private.get('NS.nickname', '')
                                    else:
                                        first_name = middle_name = last_name = name_prefix = name_suffix = nickname = ''
                                else:
                                    first_name = middle_name = last_name = name_prefix = name_suffix = nickname = ''
                                
                                # only add valid entries
                                if record_id: 
                                    user_dictionary[record_id] = [record_id, email_address, phone_number, name_prefix, first_name, middle_name, last_name, name_suffix, nickname]
                            except (KeyError, TypeError, AttributeError) as e:
                                logfunc(f'Error processing participant data: {str(e)}')
                                continue
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

    
__artifacts__ = {
    "cloudkitparticipants": (
        "Cloudkit",
        ('*NoteStore.sqlite*'), # TODO confirm this is the correct file ref see issue #322
        get_cloudkitParticipants)
}