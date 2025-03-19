__artifacts_v2__ = {
    "userPayByPhone": {  
        "name": "PayByPhone - Users and Vehicules Info",
        "description": "Extract users and vehicules infos",
        "author": "@flashesc, @thibgav, @borelmo",
        "version": "1.2",
        "date": "2024-11-20",
        "requirements": "none",
        "category": "Parking",  
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/PayByPhone.sqlite*',),
        "output_types": ["tsv", "timeline", "kml", "lava"],
        "artifact_icon": "users"
    },
    "sessionPayByPhone": { 
        "name": "PayByPhone - Parking Sessions",  
        "description": "List of parking sessions",
        "author": "@flashesc, @thibgav, @borelmo",
        "version": "1.2",
        "date": "2024-11-20",
        "requirements": "none",
        "category": "Parking",  
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/PayByPhone.sqlite*',),
        "output_types": "all",
        "artifact_icon": "map"
    }
}

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, media_to_html, webkit_timestampsconv
import re

def price_format(value): # limit to two digits after the decimal point
    if value:
        try:
            return f"{float(value):.2f}"
        except (ValueError, TypeError):
            return value
    else:
        return value
    

def clean_text(html): # remove html tags
    if not html:
        return "" 

    try:
        text_without_tags = re.sub(r'<[^>]+>', '', html)
        
        text_without_tags = text_without_tags.replace('&quot;', '"')
        text_without_tags = text_without_tags.replace('&nbsp;', ' ')
        text_without_tags = text_without_tags.replace('&amp;', '&')
        
        lignes = [ligne.strip() for ligne in text_without_tags.split('\n') if ligne.strip()]
        cleaned_text = "\n".join(lignes)
        
        return cleaned_text
    except Exception as e:
        print(f"Error while processing HTML contents : {e}")
        return ""

@artifact_processor
def userPayByPhone(files_found, report_folder, seeker, wrap_text, time_offset):
    source_path = get_file_path(files_found, "PayByPhone.sqlite")
    data_list = []
    html_data_list = []
    pictures_path = source_path[source_path.find("/mobile"):]
    pictures_found = seeker.search(f"*{pictures_path}")

    query = '''
    SELECT 
        ZUSERACCOUNT.ZEMAIL AS "EMAIL",
        ZUSERACCOUNT.ZMEMBERID AS "ID Membre",
        ZUSERACCOUNT.ZUSERNAME AS "Telephone",
        ZVEHICLE.ZCOUNTRY AS "Pays",
        ZVEHICLE.ZLICENSEPLATE AS "Numero plaque",
        ZVEHICLE.ZVEHICLEDESCRIPTION AS "Description véhicule",
        ZVEHICLE.ZVEHICLETYPESTRING AS "Catégorie",
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
                    'Vehicule Picture'
                    )

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        media_path = f'{record[-1]}.png'
        media_tag = media_to_html(media_path, pictures_found, report_folder)
        data_list.append(
            (record[0], record[1], record[2], record[3], record[4], record[5], record[6], media_path)
            )
        html_data_list.append(
            (record[0], record[1], record[2], record[3], record[4], record[5], record[6], media_tag)
            )

    report = ArtifactHtmlReport('PayByPhone - Users and Vehicules Info')
    report.start_artifact_report(report_folder, 'PayByPhone - Users and Vehicules Info', artifact_description= "Extract users and vehicules infos")
    report.add_script()
    report.write_artifact_data_table(data_headers, html_data_list, source_path, html_no_escape=['Vehicule Picture'])
    report.end_artifact_report()

    return data_headers, data_list, source_path


@artifact_processor
def sessionPayByPhone(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "PayByPhone.sqlite")
    data_list = []

    query = '''
    SELECT 
        ps.ZSTARTTIME AS "Heure_arrivee",
        ps.ZEXPIRETIME AS "Heure_depart",
        u.ZEMAIL,
        v.ZVEHICLEDESCRIPTION as Voiture,
        ps.ZAMOUNT as Prix,
        l.ZCURRENCY as Devise,
        ps.ZCOORDINATELATITUDE as Latitude,
        ps.ZCOORDINATELONGITUDE as Longitude,
        ps.ZLOCATIONNUMBER AS "tarif/zone",             
        l.ZNAME as Nom_parking,
        l.ZVENDORNAME as Ville,
        l.ZCOUNTRY as Pays,
        l.ZLOTMESSAGE as Info
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
    
    db_records = get_sqlite_db_records(source_path, query)
    
    for record in db_records:
        start_timestamp = webkit_timestampsconv(record[0])
        expire_timestamp = webkit_timestampsconv(record[1])
        price = price_format(record[4])
        info_lisible = clean_text(record[12])
        data_list.append(
            (start_timestamp, expire_timestamp, record[2],record[3], price, record[5], record[6], record[7], 
                record[8], record[9], record[10], record[11], info_lisible,)
            )


    return data_headers, data_list, source_path
