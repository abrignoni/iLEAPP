import re
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


__artifacts_v2__ = {
    "userPayByPhone": {  
        "name": "PayByPhone - Users and Vehicules Info",
        "description": "Collect data from PayByPhone",
        "author": "@flashesc, @thibgav, @borelmo",
        "version": "1.2",
        "date": "2024-11-20",
        "requirements": "none",
        "category": "Parking",  
        "notes": "",
        "paths": ('*/var/mobile/Containers/Data/Application/*/Documents/PayByPhone.sqlite*',  '*/var/mobile/Containers/Data/Application/*/Documents/*.png'),  
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
        "paths": ('*/var/mobile/Containers/Data/Application/*/Documents/PayByPhone.sqlite*',),
        "output_types": "all",
        "artifact_icon": "map"
    }

}


from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, media_to_html, webkit_timestampsconv


def format_price(value): #limite les float à 2 chiffres après la virgule   
    try:
        return f"{float(value):.2f}"
    except (ValueError, TypeError):
        return value 
    

def lisible_text(html): #rend lisible les balises html
    if not html:
        return "" 

    try:
        texte_sans_balises = re.sub(r'<[^>]+>', '', html)
        
        texte_sans_balises = texte_sans_balises.replace('&quot;', '"')
        texte_sans_balises = texte_sans_balises.replace('&nbsp;', ' ')
        texte_sans_balises = texte_sans_balises.replace('&amp;', '&')
        
        lignes = [ligne.strip() for ligne in texte_sans_balises.split('\n') if ligne.strip()]
        texte_lisible = "\n".join(lignes)
        
        return texte_lisible
    except Exception as e:
        print(f"Erreur lors du traitement du texte HTML : {e}")
        return ""



@artifact_processor
def userPayByPhone(files_found, report_folder, seeker, wrap_text, time_offset):
    data_list = []
    html_data_list = []
    db_file = ''

    for file_found in files_found:
        if file_found.endswith('PayByPhone.sqlite'):
            db_file = file_found
            break


    with open_sqlite_db_readonly(db_file) as db:
        cursor = db.cursor()
        cursor.execute('''
        SELECT 
                ZUSERACCOUNT.ZEMAIL AS "EMAIL",
                ZUSERACCOUNT.ZMEMBERID AS "ID Membre",
                ZUSERACCOUNT.ZUSERNAME AS "Telephone",
                ZVEHICLE.ZCOUNTRY AS "Pays",
                ZVEHICLE.ZLICENSEPLATE AS "Numero plaque",
                ZVEHICLE.ZVEHICLEDESCRIPTION AS "Description véhicule",
                ZVEHICLE.ZVEHICLETYPESTRING AS "Catégorie",
                ZVEHICLE.ZVEHICLEID
            FROM 
                ZUSERACCOUNT
            LEFT JOIN 
                ZVEHICLE 
            ON 
                ZUSERACCOUNT.Z_PK = ZVEHICLE.ZUSERACCOUNT;
        ''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            media_path = f'{row[-1]}.png'
            media_tag = media_to_html(media_path, files_found, report_folder)
            data_list.append(
                (row[0], row[1], row[2], row[3], row[4], row[5], row[6], media_path)
                )
            html_data_list.append(
                (row[0], row[1], row[2], row[3], row[4], row[5], row[6], media_tag)
                )

    data_headers = ('Email',
                    'Membre ID',
                    'Phone Number',
                    'Country',
                    'License Plate',
                    'Vehicule Description',
                    'Vehicule Type',
                    'Vehicule Picture'
                    )

    report = ArtifactHtmlReport('PayByPhone - Users and Vehicules Info')
    report.start_artifact_report(report_folder, 'PayByPhone - Users and Vehicules Info', artifact_description= "Collect data from PayByPhone")
    report.add_script()
    report.write_artifact_data_table(data_headers, html_data_list, db_file, html_no_escape=['Vehicule Picture'])
    report.end_artifact_report()

    return data_headers, data_list, db_file


@artifact_processor
def sessionPayByPhone(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    db_file = ''

    for file_found in files_found:
        if file_found.endswith('PayByPhone.sqlite'):
            db_file = file_found
            break

    with open_sqlite_db_readonly(db_file) as db:
        cursor = db.cursor()
        cursor.execute('''
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
            JOIN ZPARKINGSESSION AS ps
                ON v.Z_PK = ps.ZVEHICLE
            JOIN ZLOCATION AS l
                ON ps.ZLOCATIONNUMBER = l.ZLOCATIONNUMBER
            JOIN ZUSERACCOUNT as u
                ON ps.ZUSERACCOUNT = u.ZPARKINGACCOUNT;
        ''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            timestamp_1 = webkit_timestampsconv(row[0])
            timestamp_2 = webkit_timestampsconv(row[1])
            price_adapted = format_price(row[4])
            info_lisible = lisible_text(row[12])
            data_list.append(
                (timestamp_1, timestamp_2, row[2],row[3], price_adapted,row[5], row[6], row[7], 
                    row[8], row[9], row[10], row[11], info_lisible,)
                )

    data_headers = (
            'Start Time',
            'Expire Time',
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

    return data_headers, data_list, db_file
