__artifacts_v2__ = {
    "userPayByPhone": {
        "name": "PayByPhone - Users and Vehicules Info",
        "description": "Extract users and vehicules infos",
        "author": "@flashesc, @thibgav, @borelmo",
        "creation_date": "2024-11-20",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Parking",
        "notes": "Vehicule Picture is the on-device picture filename for the vehicle.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/PayByPhone.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "users"
    },
    "sessionPayByPhone": {
        "name": "PayByPhone - Parking Sessions",
        "description": "List of parking sessions",
        "author": "@flashesc, @thibgav, @borelmo",
        "creation_date": "2024-11-20",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Parking",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/PayByPhone.sqlite*',),
        "output_types": "all",
        "artifact_icon": "map"
    }
}

import re

from scripts.ilapfuncs import (artifact_processor, get_file_path, get_sqlite_db_records,
                               webkit_timestampsconv)


def price_format(value):
    """Limit a price to two digits after the decimal point."""
    if value:
        try:
            return f"{float(value):.2f}"
        except (ValueError, TypeError):
            return value
    return value


def clean_text(html):
    """Strip HTML tags and unescape a handful of entities from a lot message."""
    if not html:
        return ""
    text_without_tags = re.sub(r'<[^>]+>', '', html)
    text_without_tags = text_without_tags.replace('&quot;', '"')
    text_without_tags = text_without_tags.replace('&nbsp;', ' ')
    text_without_tags = text_without_tags.replace('&amp;', '&')
    lignes = [ligne.strip() for ligne in text_without_tags.split('\n') if ligne.strip()]
    return "\n".join(lignes)


@artifact_processor
def userPayByPhone(context):
    source_path = get_file_path(context.get_files_found(), "PayByPhone.sqlite")
    data_list = []

    query = '''
    SELECT
        ZUSERACCOUNT.ZEMAIL,
        ZUSERACCOUNT.ZMEMBERID,
        ZUSERACCOUNT.ZUSERNAME,
        ZVEHICLE.ZCOUNTRY,
        ZVEHICLE.ZLICENSEPLATE,
        ZVEHICLE.ZVEHICLEDESCRIPTION,
        ZVEHICLE.ZVEHICLETYPESTRING,
        ZVEHICLE.ZVEHICLEID
    FROM ZUSERACCOUNT
    LEFT JOIN ZVEHICLE ON ZUSERACCOUNT.Z_PK = ZVEHICLE.ZUSERACCOUNT
    '''

    data_headers = ('Email',
                    'Membre ID',
                    ('Phone Number', 'phonenumber'),
                    'Country',
                    'License Plate',
                    'Vehicule Description',
                    'Vehicule Type',
                    'Vehicule Picture')

    for record in get_sqlite_db_records(source_path, query):
        data_list.append(
            (record[0], record[1], record[2], record[3], record[4], record[5], record[6],
             f'{record[-1]}.png'))

    return data_headers, data_list, source_path


@artifact_processor
def sessionPayByPhone(context):
    source_path = get_file_path(context.get_files_found(), "PayByPhone.sqlite")
    data_list = []

    query = '''
    SELECT
        ps.ZSTARTTIME,
        ps.ZEXPIRETIME,
        u.ZEMAIL,
        v.ZVEHICLEDESCRIPTION,
        ps.ZAMOUNT,
        l.ZCURRENCY,
        ps.ZCOORDINATELATITUDE,
        ps.ZCOORDINATELONGITUDE,
        ps.ZLOCATIONNUMBER,
        l.ZNAME,
        l.ZVENDORNAME,
        l.ZCOUNTRY,
        l.ZLOTMESSAGE
    FROM ZVEHICLE AS v
    JOIN ZPARKINGSESSION AS ps ON v.Z_PK = ps.ZVEHICLE
    JOIN ZLOCATION AS l ON ps.ZLOCATIONNUMBER = l.ZLOCATIONNUMBER
    JOIN ZUSERACCOUNT as u ON ps.ZUSERACCOUNT = u.ZPARKINGACCOUNT
    '''

    data_headers = (
        ('Start Time', 'datetime'),
        ('Expire Time', 'datetime'),
        'Email',
        'Vehicule',
        'Price',
        'Currency',
        'Latitude',
        'Longitude',
        'Location Number',
        'Parking Name',
        'City',
        'Country',
        'Info')

    for record in get_sqlite_db_records(source_path, query):
        data_list.append(
            (webkit_timestampsconv(record[0]), webkit_timestampsconv(record[1]), record[2],
             record[3], price_format(record[4]), record[5], record[6], record[7], record[8],
             record[9], record[10], record[11], clean_text(record[12])))

    return data_headers, data_list, source_path
