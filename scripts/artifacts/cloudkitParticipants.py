__artifacts_v2__ = {
    "get_cloudkitParticipants": {  
        "name": "CloudKit Participants",
        "description": "CloudKit Participants - Cloudkit accounts participating in CloudKit shares",
        "author": "@threeplanetssoftware",
        "creation_date": "2022-10-22",
        "last_update_date": "2025-09-26",
        "requirements": "none",
        "category": "CloudKit",
        "notes": "",
        "paths": ('*NoteStore.sqlite*',), # TODO confirm this is the correct file ref see issue #322
        "output_types": "standard", 
    }
}

#import os
import nska_deserialize as nd
import io

from scripts.ilapfuncs import open_sqlite_db_readonly, artifact_processor

@artifact_processor
def get_cloudkitParticipants(context):

    user_dictionary = {}    
    #report_folder = context.get_report_folder()

    for file_found in context.get_files_found():
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
                
                # filename = os.path.join(report_folder, 'zserversharedata_'+str(row[0])+'.bplist')
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
                
                            user_dictionary[record_id] = [record_id, email_address, phone_number, name_prefix, first_name, middle_name, last_name, name_suffix, nickname]
            db.close()
    
    # Build the array after dealing with all the files 
    user_list = list(user_dictionary.values())
    user_headers = ('Record ID','Email Address',('Phone Number', 'phonenumber'),'Name Prefix','First Name','Middle Name','Last Name','Name Suffix','Nickname')     

    return user_headers, user_list, ''