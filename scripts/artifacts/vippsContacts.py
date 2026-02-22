import os

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly, does_column_exist_in_db, is_platform_windows


def relative_paths(source, splitter):
    splitted_a = source.split(splitter)
    rpt_folder = ''
    for x in splitted_a:
        if 'LEAPP_Reports_' in x:
            rpt_folder = x

    splitted_b = source.split(rpt_folder)
    return '.'+ splitted_b[1]


@artifact_processor
def get_vippsContacts(files_found, report_folder, seeker, wrap_text, timezone_offset):
    file_found = str(files_found[0])
    for ff in files_found:
        ff = str(ff)
        if ff.endswith('.sqlite'):
            file_found = ff
            break

    data_list = []

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()

    # Check if ZRAWPHONENUMBERS exists, if not, check ZPHONENUMBERS
    if does_column_exist_in_db(file_found, 'ZCONTACTMODEL', 'ZRAWPHONENUMBERS'):
        phone_column = 'ZRAWPHONENUMBERS'
    elif does_column_exist_in_db(file_found, 'ZCONTACTMODEL', 'ZPHONENUMBERS'):
        phone_column = 'ZPHONENUMBERS'
    else:
        logfunc('Neither ZRAWPHONENUMBERS nor ZPHONENUMBERS exist in ZCONTACTMODEL table.')
        db.close()
        return (), [], ''

    # phone_column is always one of two hardcoded values above, safe for interpolation
    cursor.execute(f'''
    SELECT
    ZNAME,
    "{phone_column}",
    ZPROFILEIMAGEDATA,
    ZCONTACTSTOREIDENTIFIER
    FROM ZCONTACTMODEL
    ''')

    all_rows = cursor.fetchall()

    for row in all_rows:
        name = row[0]
        phonenumbers = row[1]
        image = row[2]
        pathing = os.path.join(report_folder, f'{row[3]}')
        if image is not None:
            with open(pathing, 'wb') as f:
                f.write(image)

            platform = is_platform_windows()
            if platform:
                pathing = pathing.replace('/', '\\')
                splitter = '\\'
            else:
                splitter = '/'

            source = relative_paths(pathing, splitter)

            thumb = f'<img src="{source}"width="300"></img>'

        else:
            thumb = ''

        data_list.append((thumb, name, phonenumbers))

    db.close()
    data_headers = ('Profile Image', 'Name', 'Telephone')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_vippsContacts": {
        "name": "Vipps Contacts",
        "description": "Vipps contact profiles with images.",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Vipps",
        "notes": "",
        "paths": ('*/Vipps.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "html_columns": ["Profile Image"]
    }
}
