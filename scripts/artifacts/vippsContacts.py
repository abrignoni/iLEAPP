__artifacts_v2__ = {
    'get_vippsContacts': {
        'name': 'Vipps - Contacts',
        'description': 'Extracts contacts and profile images from Vipps.',
        'author': '@AlexisBrignoni',
        'creation_date': '2022-06-22',
        'last_update_date': '2025-11-21',
        'requirements': 'none',
        'category': 'Vipps',
        'notes': '',
        'paths': ('*/Vipps.sqlite*',),
        'output_types': 'standard',
        'artifact_icon': 'users'
    }
}

from scripts.ilapfuncs import (
    artifact_processor,
    logfunc,
    get_file_path,
    get_sqlite_db_records,
    does_column_exist_in_db,
    check_in_embedded_media
    )


@artifact_processor
def get_vippsContacts(context):
    files_found = context.get_files_found()
    data_list = []

    source_path = get_file_path(files_found, 'Vipps.sqlite')
    if not source_path:
        logfunc('Vipps.sqlite not found.')
        return (), [], ''

    if does_column_exist_in_db(source_path, 'ZCONTACTMODEL', 'ZRAWPHONENUMBERS'):
        phone_column = 'ZRAWPHONENUMBERS'
    elif does_column_exist_in_db(source_path, 'ZCONTACTMODEL', 'ZPHONENUMBERS'):
        phone_column = 'ZPHONENUMBERS'
    else:
        logfunc('Neither ZRAWPHONENUMBERS nor ZPHONENUMBERS exist in ZCONTACTMODEL table.')
        return (), [], source_path

    query = f'''
    SELECT
    ZNAME,
    {phone_column},
    ZPROFILEIMAGEDATA,
    ZCONTACTSTOREIDENTIFIER
    FROM ZCONTACTMODEL
    '''
    all_rows = get_sqlite_db_records(source_path, query)

    if all_rows:
        for row in all_rows:
            name = row[0]
            phonenumbers = row[1]
            image_blob = row[2]
            contact_id = row[3]

            thumb_id = None
            if image_blob:
                thumb_id = check_in_embedded_media(
                    source_file=source_path,
                    data=image_blob,
                    name=f"{contact_id}_profile"
                )

            data_list.append((thumb_id, name, phonenumbers, source_path))

    data_headers = (
        ('Profile Image', 'media'),
        'Name',
        'Telephone',
        'Source File'
    )

    return data_headers, data_list, source_path
