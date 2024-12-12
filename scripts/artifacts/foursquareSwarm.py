__artifacts_v2__ = {
    "foursquare_swarm_account": {
        "name": "Foursquare Swarm Account",
        "description": "Parses and extract Foursquare Swarm Account",
        "author": "Django Faiola",
        "version": "0.1",
        "date": "2024-11-10",
        "requirements": "none",
        "category": "Foursquare Swarm",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/foursquare.sqlite*'),
        "output_types": [ "lava", "tsv", "timeline" ],
        "artifact_icon": "user"
    },
    "foursquare_swarm_contacts": {
        "name": "Foursquare Swarm Contacts",
        "description": "Parses and extract Foursquare Swarm Contacts",
        "author": "Django Faiola",
        "version": "0.1",
        "date": "2024-11-10",
        "requirements": "none",
        "category": "Foursquare Swarm",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/foursquare.sqlite*'),
        "output_types": [ "lava", "tsv" ],
        "artifact_icon": "users"
    },
    "foursquare_swarm_checkins": {
        "name": "Foursquare Swarm Check-ins",
        "description": "Parses and extract Foursquare Swarm Check-ins",
        "author": "Django Faiola",
        "version": "0.1",
        "date": "2024-11-10",
        "requirements": "none",
        "category": "Foursquare Swarm",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/foursquare.sqlite*'),
        "output_types": [ "lava", "tsv", "timeline" ],
        "artifact_icon": "user-check"
    },
    "foursquare_swarm_tips": {
        "name": "Foursquare Swarm Tips",
        "description": "Parses and extract Foursquare Swarm Tips",
        "author": "Django Faiola",
        "version": "0.1",
        "date": "2024-11-10",
        "requirements": "none",
        "category": "Foursquare Swarm",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/foursquare.sqlite*'),
        "output_types": [ "lava", "tsv", "timeline" ],
        "artifact_icon": "info"
    },
    "foursquare_swarm_stickers": {
        "name": "Foursquare Swarm Stickers",
        "description": "Parses and extract Foursquare Swarm Stickers",
        "author": "Django Faiola",
        "version": "0.1",
        "date": "2024-11-10",
        "requirements": "none",
        "category": "Foursquare Swarm",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/foursquare.sqlite*'),
        "output_types": [ "lava", "tsv" ],
        "artifact_icon": "award"
    },
    "foursquare_swarm_venues_history": {
        "name": "Foursquare Swarm Venues History",
        "description": "Parses and extract Foursquare Swarm Venues History",
        "author": "Django Faiola",
        "version": "0.1",
        "date": "2024-11-10",
        "requirements": "none",
        "category": "Foursquare Swarm",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/foursquare.sqlite*'),
        "output_types": [ "lava", "tsv", "timeline", "kml" ],
        "artifact_icon": "map-pin"
    },
    "foursquare_swarm_venues_photos": {
        "name": "Foursquare Swarm Venues Photos",
        "description": "Parses and extract Foursquare Swarm Venues Photos",
        "author": "Django Faiola",
        "version": "0.1",
        "date": "2024-11-10",
        "requirements": "none",
        "category": "Foursquare Swarm",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/foursquare.sqlite*'),
        "output_types": [ "lava", "tsv", "timeline" ],
        "artifact_icon": "camera"
    },
    "foursquare_swarm_checkins_comments": {
        "name": "Foursquare Swarm Check-ins Comments",
        "description": "Parses and extract Foursquare Swarm Check-ins Comments",
        "author": "Django Faiola",
        "version": "0.1",
        "date": "2024-11-10",
        "requirements": "none",
        "category": "Foursquare Swarm",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/foursquare.sqlite*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "artifact_icon": "message-square"
    }
}


from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import open_sqlite_db_readonly, convert_ts_human_to_timezone_offset, artifact_processor, kmlgen


def facebook_url(value, html_format=True):
    if value != None and len(value) > 0:
        url = f"http://www.facebook.com/profile.php?id={value}"
        return url if not html_format else f'<a href="{url}" target="_blank">{value}</>'
    else:
        return ''

def twitter_url(value, html_format=True):
    if value != None and len(value) > 0:
        url = f"http://twitter.com/{value}"
        return url if not html_format else f'<a href="{url}" target="_blank">{value}</>'
    else:
        return ''

def instagram_url(value, html_format=True):
    if value != None and len(value) > 0:
        url = f"https://www.instagram.com/{value}"
        return url if not html_format else f'<a href="{url}" target="_blank">{value}</>'
    else:
        return ''


def foursquare_uid_url(uid, url, html_format=True):
    # http://foursquare.com/u/1234567
    # https://foursquare.com/user/1234567890
    if uid != None and len(uid) > 0:
        return uid if not html_format else f'<a href="{url}" target="_blank">{uid}</>'
    else:
        return ''


def generic_url(value, html_format=True):
    if value != None and len(value) > 0:
        return value if not html_format else f'<a href="{value}" target="_blank">{value}</>'
    else:
        return ''


# account
@artifact_processor
def foursquare_swarm_account(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = [ 'Created', 'Joined at', 'First name', 'Last name', 'Gender', 'Birthday', 'Home city', 
                     'Phone number',  'Email', 'Facebook', 'Twitter', 'Profile picture URL', 'Neighborhood sharing state', 
                     'Total Check-ins', 'Unique ID', 'Location' ]
    data_list = []
    data_list_html = []
    report_file = 'Unknown'

    for file_found in files_found:
        file_found = str(file_found)

        # foursquare.sqlite
        if file_found.endswith('foursquare.sqlite'):
            report_file = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute('''
            SELECT
                U.Z_PK AS "U_PK",
                FU.Z_PK AS "FU_PK",
	            datetime(U.ZSWARMCREATEDAT + 978307200, 'unixepoch') AS "created",
	            datetime(U.ZJOINEDAT + 978307200, 'unixepoch') AS "joined_at",
                U.ZFIRSTNAME,
                U.ZLASTNAME,
                U.ZGENDER,
                date(U.ZBIRTHDAY + 978307200, 'unixepoch') AS "birthday",
                U.ZHOMECITY,
                U.ZPHONE,
                U.ZEMAIL,
                FU.ZMONGOID AS "facebook",
                U.ZTWITTER,
                U.ZCANONICALURL,
                IIF(U.ZPHOTOPREFIX NOT NULL AND U.ZPHOTOSUFFIX NOT NULL, U.ZPHOTOPREFIX || 'original' || U.ZPHOTOSUFFIX, '') AS "originalPhoto",
                U.ZCHECKINPINGS AS "neighborhood_sharing_state",
                U.ZCHECKINSCOUNT AS "total_checkins",
                U.ZMONGOID AS "uid"
            FROM ZFSUSER AS "U"
            LEFT JOIN ZFSFACEBOOKUSER AS "FU" ON (U.ZFACEBOOKUSER = FU.Z_PK)
            WHERE U.ZRELATIONSHIP = 'self'
            ''')

            all_rows = cursor.fetchall()
            if len(all_rows) > 0:
                artifact_name = __artifacts_v2__['foursquare_swarm_account']['name']

                # html
                report = ArtifactHtmlReport(artifact_name)
                report.start_artifact_report(report_folder, artifact_name)
                report.add_script()

                for row in all_rows:
                    # created
                    created = convert_ts_human_to_timezone_offset(row[2], timezone_offset)
                    # joined at
                    joined_at = convert_ts_human_to_timezone_offset(row[3], timezone_offset)
                    # facebook profile
                    facebook = facebook_url(row[11])
                    # twitter
                    twitter = twitter_url(row[12])
                    # foursquare
                    foursquare = foursquare_uid_url(row[17], row[13])
                    # profile picture url
                    profile_picture = generic_url(row[14])

                    # location
                    location = [ f'ZFSUSER (Z_PK: {row[0]})' ]
                    if row[1] != None: location.append(f'ZFSFACEBOOKUSER (Z_PK: {row[1]})')
                    location = ', '.join(location)

                    # html row
                    data_list_html.append((created, joined_at, row[4], row[5], row[6], row[7], row[8], row[9], row[10],
                                           facebook, twitter, profile_picture, row[15], row[16], foursquare, location))
                    
                    # facebook profile
                    facebook = facebook_url(row[11], html_format=False)
                    # twitter
                    twitter = twitter_url(row[12], html_format=False)
                    # foursquare
                    foursquare = foursquare_uid_url(row[17], row[13], html_format=False)
                    # profile picture url
                    profile_picture = generic_url(row[14], html_format=False)
                    # lava row
                    data_list.append((created, joined_at, row[4], row[5], row[6], row[7], row[8], row[9], row[10],
                                      facebook, twitter, profile_picture, row[15], row[16], foursquare, location))

                report.write_artifact_data_table(data_headers, data_list_html, file_found, html_no_escape=['Facebook', 'Twitter', 'Profile picture URL', 'Unique ID'])
                report.end_artifact_report()

            db.close()

    # lava types
    data_headers[0] = (data_headers[0], 'datetime')
    data_headers[1] = (data_headers[1], 'datetime')
    data_headers[5] = (data_headers[5], 'date')

    return data_headers, data_list, report_file


# contacts
@artifact_processor
def foursquare_swarm_contacts(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = [ 'Contact type', 'Relationship', 'First name', 'Last name', 'Gender', 'Birthday', 'Home city',
                     'Phone number', 'Email', 'Facebook', 'Twitter', 'Profile picture URL', 'Unique ID', 
                     'Location' ]
    data_list = []
    data_list_html = []
    report_file = 'Unknown'

    for file_found in files_found:
        file_found = str(file_found)

        # foursquare.sqlite
        if file_found.endswith('foursquare.sqlite'):
            report_file = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute('''
            SELECT
	            U.Z_PK AS "U_PK",
	            FU.Z_PK AS "FU_PK",
                CASE U.ZUSERTYPE
                    WHEN 'user' Then 'User'
                    WHEN 'brand' Then 'Brand'
                    WHEN 'celebrity' Then 'Celebrity'
                    WHEN 'venuePage' Then 'Venue Page'
                    WHEN 'page' Then 'Page'
                    WHEN 'chain' Then 'Chain'
                    ELSE U.ZUSERTYPE
                END AS "user_type",
                CASE U.ZRELATIONSHIP
                    WHEN 'self' THEN 'Owner'
                    WHEN 'friend' THEN 'Friend'
                    WHEN 'pendingMe' THEN 'Follower'
                    WHEN 'pendingThem' THEN 'Follower'
                    WHEN 'followingThem' THEN 'Following'
                    ELSE 'Other'
                END AS "relationship",
	            U.ZFIRSTNAME,
	            U.ZLASTNAME,
	            U.ZGENDER,
	            date(U.ZBIRTHDAY + 978307200, 'unixepoch') AS "birthday",
	            U.ZHOMECITY,
	            U.ZPHONE,
	            U.ZEMAIL,
	            FU.ZMONGOID AS "facebook",
	            U.ZTWITTER,
	            U.ZCANONICALURL,
                IIF(U.ZPHOTOPREFIX NOT NULL AND U.ZPHOTOSUFFIX NOT NULL, U.ZPHOTOPREFIX || 'original' || U.ZPHOTOSUFFIX, '') AS "originalPhoto",
	            U.ZMONGOID AS "uid"
            FROM ZFSUSER AS "U"
            LEFT JOIN ZFSFACEBOOKUSER AS "FU" ON (U.ZFACEBOOKUSER = FU.Z_PK)
            WHERE (U.ZRELATIONSHIP != 'self') OR (U.ZRELATIONSHIP IS NULL)
            ''')

            all_rows = cursor.fetchall()
            if len(all_rows) > 0:
                artifact_name = __artifacts_v2__['foursquare_swarm_contacts']['name']

                # html
                report = ArtifactHtmlReport(artifact_name)
                report.start_artifact_report(report_folder, artifact_name)
                report.add_script()

                for row in all_rows:
                    # facebook profile
                    facebook = facebook_url(row[11])
                    # twitter
                    twitter = twitter_url(row[12])
                    # foursquare
                    foursquare = foursquare_uid_url(row[15], row[13])
                    # profile picture url
                    profile_picture = generic_url(row[14])

                    # location
                    location = [ f'ZFSUSER (Z_PK: {row[0]})' ]
                    if row[1] != None: location.append(f'ZFSFACEBOOKUSER (Z_PK: {row[1]})')
                    location = ', '.join(location)

                    # html row
                    data_list_html.append((row[2], row[3], row[4], row[5], row[6], row[7], row[8], 
                                           row[9], row[10], facebook, twitter, profile_picture, foursquare, 
                                           location))

                    # facebook profile
                    facebook = facebook_url(row[11], html_format=False)
                    # twitter
                    twitter = twitter_url(row[12], html_format=False)
                    # foursquare
                    foursquare = foursquare_uid_url(row[15], row[13], html_format=False)
                    # profile picture url
                    profile_picture = generic_url(row[14], html_format=False)
                    # lava row
                    data_list.append((row[2], row[3], row[4], row[5], row[6], row[7], row[8], 
                                      row[9], row[10], facebook, twitter, profile_picture, foursquare,
                                      location))

                report.write_artifact_data_table(data_headers, data_list_html, file_found, html_no_escape=['Facebook', 'Twitter', 'Profile picture URL', 'Unique ID'])
                report.end_artifact_report()
                
            db.close()

    # lava types
    data_headers[4] = (data_headers[4], 'date')

    return data_headers, data_list, report_file


# checkins
@artifact_processor
def foursquare_swarm_checkins(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = [ 'Created', 'TZ offset (minutes)', 'Relationship', 'Full name', 'Privacy', 'Venue name', 'Distance (meters)', 
                     'Latitude', 'Longitude', 'Address', 'Neighborhood', 'Country', 'State', 'City', 'Cross street', 'Postal code', 'Phone number', 
                     'Facebook', 'Twitter', 'Instagram', 'Check-in URL', 'Website', 'Major', 'Unique ID', 'Location' ]
    data_list = []
    data_list_html = []
    report_file = 'Unknown'

    for file_found in files_found:
        file_found = str(file_found)

        # foursquare.sqlite
        if file_found.endswith('foursquare.sqlite'):
            report_file = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute('''
            SELECT 
	            CI.Z_PK AS "CI_PK",
	            V.Z_PK AS "V_PK",
	            U.Z_PK AS "U_PK",
                datetime(CI.ZCREATEDAT + 978307200, 'unixepoch') AS "created",
	            CI.ZTIMEZONEOFFSET AS "tzoffset_min",
	            CASE U.ZRELATIONSHIP
		            WHEN 'self' THEN 'Owner'
		            WHEN 'friend' THEN 'Friend'
		            WHEN 'pendingMe' THEN 'Follower'
		            WHEN 'pendingThem' THEN 'Follower'
		            WHEN 'followingThem' THEN 'Following'
		            ELSE 'Other'
	            END AS "relationship",
                IIF(U.ZLASTNAME IS NULL OR length(U.ZLASTNAME) = 0, coalesce(U.ZFIRSTNAME, ''), IIF(U.ZFIRSTNAME IS NULL OR length(U.ZFIRSTNAME) = 0, coalesce(U.ZLASTNAME, ''), U.ZFIRSTNAME || ' ' || coalesce(U.ZLASTNAME, ''))) AS "full_name",
                IIF(CI.ZPRIVATE = 1, 'Private', 'Public') AS "privacy",
                V.ZNAME AS "venue_name",
	            V.ZDISTANCE,
	            V.ZGEOLAT,
	            V.ZGEOLONG,
	            V.ZADDRESS,
	            V.ZNEIGHBORHOOD,
	            V.ZCOUNTRY,
	            V.ZSTATE,
	            V.ZCITY,
	            V.ZCROSSSTREET,
	            V.ZPOSTALCODE,
	            V.ZPHONE,
	            V.ZFACEBOOKID,
	            V.ZTWITTER,
	            V.ZINSTAGRAM,
	            V.ZCANONICALURL AS "checkin_url",
	            V.ZURL AS "website",
                IIF(CI.ZISMAYOR = 0, '', 'Yes') AS "is_major",
                CI.ZMONGOID AS "uid"
            FROM ZFSCHECKIN AS "CI"
            LEFT JOIN ZFSVENUE AS "V" ON (CI.ZVENUE = V.Z_PK)
            LEFT JOIN ZFSUSER AS "U" ON (CI.ZUSER = U.Z_PK)
            WHERE (CI.ZCHECKINTYPE = 'checkin')
            ''')

            all_rows = cursor.fetchall()
            if len(all_rows) > 0:
                artifact_name = __artifacts_v2__['foursquare_swarm_checkins']['name']

                # html
                report = ArtifactHtmlReport(artifact_name)
                report.start_artifact_report(report_folder, artifact_name)
                report.add_script()

                for row in all_rows:
                    # created
                    created = convert_ts_human_to_timezone_offset(row[3], timezone_offset)
                    # facebook profile
                    facebook = facebook_url(row[20])
                    # twitter
                    twitter = twitter_url(row[21])
                    # instagram
                    instagram = instagram_url(row[22])
                    # check-in url
                    checkin_url = generic_url(row[23])
                    # foursquare
                    website = generic_url(row[24])

                    # location
                    location = [ f'ZFSCHECKIN (Z_PK: {row[0]})' ]
                    if row[1] != None: location.append(f'ZFSVENUE (Z_PK: {row[1]})')
                    if row[2] != None: location.append(f'ZFSUSER (Z_PK: {row[2]})')
                    location = ', '.join(location)

                    # html row
                    data_list_html.append((created, row[4], row[5], row[6], row[7], row[8], row[9],
                                           row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19],
                                           facebook, twitter, instagram, checkin_url, website, row[25], row[26], location))
                    
                    # facebook profile
                    facebook = facebook_url(row[20], html_format=False)
                    # twitter
                    twitter = twitter_url(row[21], html_format=False)
                    # instagram
                    instagram = instagram_url(row[22], html_format=False)
                    # check-in url
                    checkin_url = generic_url(row[23], html_format=False)
                    # foursquare
                    website = generic_url(row[24], html_format=False)
                    # lava row
                    data_list.append((created, row[4], row[5], row[6], row[7], row[8], row[9],
                                      row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19],
                                      facebook, twitter, instagram, checkin_url, website, row[25], row[26], location))

                report.write_artifact_data_table(data_headers, data_list_html, file_found, html_no_escape=['Facebook', 'Twitter', 'Instagram', 'Check-in URL', 'Website'])
                report.end_artifact_report()

                # kml
                headers_0 = data_headers[0]
                data_headers[0] = 'Timestamp'
                kmlgen(report_folder, artifact_name, data_list, data_headers)
                data_headers[0] = headers_0

            db.close()

    # lava types
    data_headers[0] = (data_headers[0], 'datetime')

    return data_headers, data_list, report_file


# tips
@artifact_processor
def foursquare_swarm_tips(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers =  [ 'Created', 'Relationship', 'Full name', 'Tip', 'Venue name', 'Distance (meters)', 'Latitude', 'Longitude', 'URL', 'Unique ID', 'Location' ]
    data_list = []
    data_list_html = []
    report_file = 'Unknown'

    for file_found in files_found:
        file_found = str(file_found)

        # foursquare.sqlite
        if file_found.endswith('foursquare.sqlite'):
            report_file = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute('''
            SELECT 
                T.Z_PK AS "T_PK",
                V.Z_PK AS "V_PK",
                U.Z_PK AS "U_PK",
                datetime(T.ZCREATEDAT + 978307200, 'unixepoch') AS "created",
                CASE U.ZRELATIONSHIP
                    WHEN 'self' THEN 'Owner'
                    WHEN 'friend' THEN 'Friend'
                    WHEN 'pendingMe' THEN 'Follower'
                    WHEN 'pendingThem' THEN 'Follower'
                    WHEN 'followingThem' THEN 'Following'
		            ELSE 'Other'
                END AS "relationship",
	            IIF(U.ZLASTNAME IS NULL OR length(U.ZLASTNAME) = 0, coalesce(U.ZFIRSTNAME, ''), IIF(U.ZFIRSTNAME IS NULL OR length(U.ZFIRSTNAME) = 0, coalesce(U.ZLASTNAME, ''), U.ZFIRSTNAME || ' ' || coalesce(U.ZLASTNAME, ''))) AS "full_name",
	            T.ZTEXT AS "tip",
	            V.ZNAME AS "venue_name",
                V.ZDISTANCE,
	            V.ZGEOLAT,
	            V.ZGEOLONG,
	            T.ZURL AS "url_tip",
                T.ZMONGOID AS "uid"	
            FROM ZFSTIP AS "T"
            LEFT JOIN ZFSUSER AS "U" ON (T.ZUSER = U.Z_PK)
            LEFT JOIN ZFSVENUE AS "V" ON (T.ZVENUE = V.Z_PK)
            ORDER BY T.ZCREATEDAT DESC
            ''')

            all_rows = cursor.fetchall()
            if len(all_rows) > 0:
                artifact_name = __artifacts_v2__['foursquare_swarm_tips']['name']

                # html
                report = ArtifactHtmlReport(artifact_name)
                report.start_artifact_report(report_folder, artifact_name)
                report.add_script()

                for row in all_rows:
                    # created
                    created = convert_ts_human_to_timezone_offset(row[3], timezone_offset)
                    # venue url
                    url = generic_url(row[11])

                    # location
                    location = [ f'ZFSCHECKIN (Z_PK: {row[0]})' ]
                    if row[2] != None: location.append(f'ZFSVENUE (Z_PK: {row[1]})')
                    if row[1] != None: location.append(f'ZFSUSER (Z_PK: {row[2]})')
                    location = ', '.join(location)

                    # html row
                    data_list_html.append((created, row[4], row[5], row[6], row[7], row[8], row[9], row[10], url, row[12], location))

                    # venue url
                    url = generic_url(row[11], html_format=False)

                    # lava row
                    data_list.append((created, row[4], row[5], row[6], row[7], row[8], row[9], row[10], url, row[12], location))

                report.write_artifact_data_table(data_headers, data_list_html, file_found, html_no_escape=['URL'])
                report.end_artifact_report()

                # kml
                headers_0 = data_headers[0]
                data_headers[0] = 'Timestamp'
                kmlgen(report_folder, artifact_name, data_list, data_headers)
                data_headers[0] = headers_0

            db.close()

    # lava types
    data_headers[0] = (data_headers[0], 'datetime')

    return data_headers, data_list, report_file


# stickers
@artifact_processor
def foursquare_swarm_stickers(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = [ 'Title', 'Category', 'Preview text', 'Unlocked', 'Unlocked text', 'Bonus status', 'Bonus text', 'Image URL', 'Unique ID', 'Location' ]
    data_list = []
    data_list_html = []
    report_file = 'Unknown'

    for file_found in files_found:
        file_found = str(file_found)

        # foursquare.sqlite
        if file_found.endswith('foursquare.sqlite'):
            report_file = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute('''
            SELECT
	            S.Z_PK AS "S_PK",
	            S.ZNAME,
	            S.ZCATEGORYNAME,
	            S.ZTEASETEXT,
	            IIF(S.ZUNLOCKED = 0, '', 'Yes') AS "unlocked",
	            S.ZUNLOCKTEXT,
	            S.ZBONUSSTATUS,
	            S.ZBONUSTEXT,
                IIF(S.ZIMAGEPREFIX NOT NULL AND S.ZIMAGENAME NOT NULL, S.ZIMAGEPREFIX || 'original' || S.ZIMAGENAME, '') AS "original_image",
                S.ZMONGOID AS "uid"
            FROM ZFSSTICKER AS "S"
            ''')

            all_rows = cursor.fetchall()
            if len(all_rows) > 0:
                artifact_name = __artifacts_v2__['foursquare_swarm_stickers']['name']

                # html
                report = ArtifactHtmlReport(artifact_name)
                report.start_artifact_report(report_folder, artifact_name)
                report.add_script()

                for row in all_rows:
                    # image url
                    image_url = generic_url(row[8])

                    # location
                    location = [ f'ZFSSTICKER (Z_PK: {row[0]})' ]
                    location = ', '.join(location)

                    # html row
                    data_list_html.append((row[1], row[2], row[3], row[4], row[5], row[6], row[7], image_url, row[9], location))

                    # photo url
                    image_url = generic_url(row[8], html_format=False)
                    # lava row
                    data_list.append((row[1], row[2], row[3], row[4], row[5], row[6], row[7], image_url, row[9], location))

                report.write_artifact_data_table(data_headers, data_list_html, file_found, html_no_escape=['Image URL'])
                report.end_artifact_report()

            db.close()

    return data_headers, data_list, report_file


# venues history
@artifact_processor
def foursquare_swarm_venues_history(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = [ 'Category', 'Venue name', 'Distance (meters)', 'Latitude', 'Longitude', 'Address', 'Neighborhood', 'Country', 'State', 'City', 'Cross street', 
                     'Postal code', 'Phone number', 'Facebook', 'Twitter', 'Instagram', 'Foursquare URL', 'Website', 'Description', 'Major', 'Mayor info',
                     'Friends visits info', 'Event info', 'Reason info','Likes count', 'Visiters count', 'Check-ins count', 'Photo count', 'Tips count', 'Events count', 
                     'Location' ]
    data_list = []
    data_list_html = []
    report_file = 'Unknown'

    for file_found in files_found:
        file_found = str(file_found)

        # foursquare.sqlite
        if file_found.endswith('foursquare.sqlite'):
            report_file = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute('''
            SELECT
	            V.Z_PK AS "V_PK",
	            C.Z_PK AS "C_PK",
	            U.Z_PK AS "U_PK",
	            C.ZNAME AS "category_name",
	            V.ZNAME AS "venue_name",
	            V.ZDISTANCE,
	            V.ZGEOLAT,
	            V.ZGEOLONG,
	            V.ZADDRESS,
	            V.ZNEIGHBORHOOD,
	            V.ZCOUNTRY,
	            V.ZSTATE,
	            V.ZCITY,
	            V.ZCROSSSTREET,
	            V.ZPOSTALCODE,
	            V.ZPHONE,
	            V.ZFACEBOOKID,
	            V.ZTWITTER,
	            V.ZINSTAGRAM,
	            V.ZCANONICALURL AS "foursquare_url",
	            V.ZURL AS "website",	
	            V.ZDESCRIPTIONTEXT,
	            U.ZMONGOID AS "mayor_uid",
	            IIF(U.ZLASTNAME IS NULL OR length(U.ZLASTNAME) = 0, coalesce(U.ZFIRSTNAME, ''), IIF(U.ZFIRSTNAME IS NULL OR length(U.ZFIRSTNAME) = 0, coalesce(U.ZLASTNAME, ''), U.ZFIRSTNAME || ' ' || coalesce(U.ZLASTNAME, ''))) AS "full_name",
	            V.ZMAYORSUMMARY,
	            V.ZFRIENDVISITSSUMMARY,
                V.ZEVENTSSUMMARY,
	            V.ZREASONSUMMARY,
	            V.ZLIKESCOUNT,
	            V.ZUSERSCOUNT AS "visiters_count",
	            V.ZCHECKINSCOUNT,
	            V.ZPHOTOSCOUNT,
	            V.ZTIPSCOUNT,
	            V.ZEVENTSCOUNT
            FROM ZFSVENUE AS "V"
            LEFT JOIN ZFSCATEGORY AS "C" ON (V.ZPRIMARYCATEGORY = C.Z_PK)
            LEFT JOIN ZFSUSER AS "U" ON (V.ZMAYOR = U.Z_PK)
            ORDER BY V.ZNAME ASC
            ''')

            all_rows = cursor.fetchall()
            if len(all_rows) > 0:
                artifact_name = __artifacts_v2__['foursquare_swarm_venues_history']['name']

                # html
                report = ArtifactHtmlReport(artifact_name)
                report.start_artifact_report(report_folder, artifact_name)
                report.add_script()

                for row in all_rows:
                    # facebook profile
                    facebook = facebook_url(row[16])
                    # twitter
                    twitter = twitter_url(row[17])
                    # instagram
                    instagram = instagram_url(row[18])
                    # foursquare url
                    foursquare_url = generic_url(row[19])
                    # website
                    website = generic_url(row[20])
                    # mayor
                    mayor = f'{row[22]} ({row[23]})' if bool(row[23]) else row[22]

                    # location
                    location = [ f'ZFSVENUE (Z_PK: {row[0]})' ]
                    if row[1] != None: location.append(f'ZFSCATEGORY (Z_PK: {row[1]})')
                    if row[2] != None: location.append(f'ZFSUSER (Z_PK: {row[2]})')
                    location = ', '.join(location)

                    # html row
                    data_list_html.append((row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], 
                                        row[14], row[15], facebook, twitter, instagram, foursquare_url, website, row[21], mayor, row[24], 
                                        row[25], row[26], row[27], row[28], row[29], row[30], row[31], row[32], row[33], 
                                        location))

                    # facebook profile
                    facebook = facebook_url(row[16], html_format=False)
                    # twitter
                    twitter = twitter_url(row[17], html_format=False)
                    # instagram
                    instagram = instagram_url(row[18], html_format=False)
                    # foursquare url
                    foursquare_url = generic_url(row[19], html_format=False)
                    # website
                    website = generic_url(row[20], html_format=False)
                    # lava row
                    data_list.append((row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], 
                                      row[14], row[15], facebook, twitter, instagram, foursquare_url, website, row[21], mayor, row[24], 
                                      row[25], row[26], row[27], row[28], row[29], row[30], row[31], row[32], row[33], 
                                      location))

                report.write_artifact_data_table(data_headers, data_list_html, file_found, html_no_escape=['Facebook', 'Twitter', 'Instagram', 'Foursquare URL', 'Website'])
                report.end_artifact_report()
                
            db.close()

    return data_headers, data_list, report_file


# venues photos
@artifact_processor
def foursquare_swarm_venues_photos(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = [ 'Created', 'Full name', 'User ID', 'Venue name', 'Distance (meters)', 'Latitude', 'Longitude', 'Address', 'Neighborhood', 'Country', 
                     'State', 'City', 'Cross street', 'Postal code', 'Phone number', 'Facebook', 'Twitter', 'Instagram', 'Foursquare URL', 'Website',
                     'Description', 'Photo URL', 'Photo size', 'Privacy', 'Source name', 'Location' ]
    data_list = []
    data_list_html = []
    report_file = 'Unknown'

    for file_found in files_found:
        file_found = str(file_found)

        # foursquare.sqlite
        if file_found.endswith('foursquare.sqlite'):
            report_file = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute('''
            SELECT
	            P.Z_PK AS "P_PK",
	            V.Z_PK AS "V_PK",
	            U.Z_PK AS "U_PK",
	            datetime(P.ZCREATEDAT + 978307200, 'unixepoch') AS "created",
	            IIF(U.ZLASTNAME IS NULL OR length(U.ZLASTNAME) = 0, coalesce(U.ZFIRSTNAME, ''), IIF(U.ZFIRSTNAME IS NULL OR length(U.ZFIRSTNAME) = 0, coalesce(U.ZLASTNAME, ''), U.ZFIRSTNAME || ' ' || coalesce(U.ZLASTNAME, ''))) AS "full_name",
	            U.ZMONGOID AS "user_uid",
    	        V.ZNAME AS "venue_name",
	            V.ZDISTANCE,
	            V.ZGEOLAT,
	            V.ZGEOLONG,
	            V.ZADDRESS,
	            V.ZNEIGHBORHOOD,
	            V.ZCOUNTRY,
	            V.ZSTATE,
	            V.ZCITY,
	            V.ZCROSSSTREET,
	            V.ZPOSTALCODE,
	            V.ZPHONE,
	            V.ZFACEBOOKID,
        	    V.ZTWITTER,
	            V.ZINSTAGRAM,
        	    V.ZCANONICALURL AS "foursquare_url",
	            V.ZURL AS "website",
                V.ZDESCRIPTIONTEXT,
                IIF(P.ZPREFIX NOT NULL AND P.ZSUFFIX NOT NULL, P.ZPREFIX || 'original' || P.ZSUFFIX, '') AS "original_photo",
                (P.ZWIDTH || 'x' || P.ZHEIGHT) AS "photo_size",
                P.ZSWARMPRIVACYSETTING,
                P.ZSOURCENAME
            FROM ZFSPHOTO AS "P"	
            LEFT JOIN ZFSVENUE AS "V" ON (P.ZPREVIEWVENUE = V.Z_PK)
            LEFT JOIN ZFSUSER AS "U" ON (P.ZUSER = U.Z_PK)
            WHERE P.ZPHOTOTYPE = 'venue'
            ''')

            all_rows = cursor.fetchall()
            if len(all_rows) > 0:
                artifact_name = __artifacts_v2__['foursquare_swarm_venues_photos']['name']

                # html
                report = ArtifactHtmlReport(artifact_name)
                report.start_artifact_report(report_folder, artifact_name)
                report.add_script()

                for row in all_rows:
                    # created
                    created = convert_ts_human_to_timezone_offset(row[3], timezone_offset)
                    # facebook profile
                    facebook = facebook_url(row[18])
                    # twitter
                    twitter = twitter_url(row[19])
                    # instagram
                    instagram = instagram_url(row[20])
                    # foursquare url
                    foursquare_url = generic_url(row[21])
                    # website
                    website = generic_url(row[22])
                    # photo url
                    photo_url = generic_url(row[24])

                    # location
                    location = [ f'ZFSPHOTO (Z_PK: {row[0]})' ]
                    if row[1] != None: location.append(f'ZFSVENUE (Z_PK: {row[1]})')
                    if row[2] != None: location.append(f'ZFSUSER (Z_PK: {row[2]})')
                    location = ', '.join(location)

                    # html row
                    data_list_html.append((created, row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], 
                                           row[13], row[14], row[15], row[16], row[17], facebook, twitter, instagram, foursquare_url, website,
                                           row[23], photo_url, row[25], row[26], row[27], location))

                    # facebook profile
                    facebook = facebook_url(row[18], html_format=False)
                    # twitter
                    twitter = twitter_url(row[19], html_format=False)
                    # instagram
                    instagram = instagram_url(row[20], html_format=False)
                    # foursquare url
                    foursquare_url = generic_url(row[21], html_format=False)
                    # website
                    website = generic_url(row[22], html_format=False)
                    # photo url
                    photo_url = generic_url(row[24], html_format=False)
                    # lava row
                    data_list.append((created, row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12],
                                      row[13], row[14], row[15], row[16], row[17], facebook, twitter, instagram, foursquare_url, website,
                                      row[23], photo_url, row[25], row[26], row[27], location))

                report.write_artifact_data_table(data_headers, data_list_html, file_found, html_no_escape=['Facebook', 'Twitter', 'Instagram', 'Foursquare URL', 'Website', 'Photo URL'])
                report.end_artifact_report()
                

                # kml
                headers_0 = data_headers[0]
                data_headers[0] = 'Timestamp'
                kmlgen(report_folder, artifact_name, data_list, data_headers)
                data_headers[0] = headers_0

            db.close()

    # lava types
    data_headers[0] = (data_headers[0], 'datetime')

    return data_headers, data_list, report_file


# check-ins comments
@artifact_processor
def foursquare_swarm_checkins_comments(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = [ 'Created', 'Relationship', 'Full name', 'Text', 'Latitude', 'Longitude', 'Venue name', 'Venue latitude', 'Venue longitude',
                     'Unique ID', 'Location' ]
    data_list = []
    report_file = 'Unknown'

    for file_found in files_found:
        file_found = str(file_found)

        # foursquare.sqlite
        if file_found.endswith('foursquare.sqlite'):
            report_file = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute('''
            SELECT
                C.Z_PK AS "C_PK",
                U.Z_PK AS "U_PK",
                CI.Z_PK AS "CI_PK",
                V.Z_PK AS "V_PK",
                datetime(C.ZCREATEDAT + 978307200, 'unixepoch') AS "created",
                CASE U.ZRELATIONSHIP
                    WHEN 'self' THEN 'Owner'
                    WHEN 'friend' THEN 'Friend'
                    WHEN 'pendingMe' THEN 'Follower'
                    WHEN 'pendingThem' THEN 'Follower'
                    WHEN 'followingThem' THEN 'Following'
                    ELSE 'Other'
                END AS "relationship",
                IIF(U.ZLASTNAME IS NULL OR length(U.ZLASTNAME) = 0, coalesce(U.ZFIRSTNAME, ''), IIF(U.ZFIRSTNAME IS NULL OR length(U.ZFIRSTNAME) = 0, coalesce(U.ZLASTNAME, ''), U.ZFIRSTNAME || ' ' || coalesce(U.ZLASTNAME, ''))) AS "full_name",
                C.ZTEXT AS "text",
                C.ZLAT AS "latitude",
                C.ZLNG AS "longitude",
                V.ZNAME AS "venue_name",
                V.ZGEOLAT AS "venue_latitude",
                V.ZGEOLONG AS "venue_longitude",
                C.ZMONGOID AS "uid"
            FROM ZFSCOMMENT AS "C"
            LEFT JOIN ZFSUSER AS "U" ON (C.ZUSER = U.Z_PK)
            LEFT JOIN ZFSCHECKIN AS "CI" ON (C.ZCHECKIN = CI.Z_PK)
            LEFT JOIN ZFSVENUE AS "V" ON (CI.ZVENUE = V.Z_PK)
            ''')

            all_rows = cursor.fetchall()
            if len(all_rows) > 0:
                artifact_name = __artifacts_v2__['foursquare_swarm_checkins_comments']['name']

                for row in all_rows:
                    # created
                    created = convert_ts_human_to_timezone_offset(row[4], timezone_offset)

                    # location
                    location = [ f'ZFSCOMMENT (Z_PK: {row[0]})' ]
                    if row[1] != None: location.append(f'ZFSUSER (Z_PK: {row[1]})')
                    if row[2] != None: location.append(f'ZFSCHECKIN (Z_PK: {row[2]})')
                    if row[3] != None: location.append(f'ZFSVENUE (Z_PK: {row[3]})')
                    location = ', '.join(location)

                    # row
                    data_list.append((created, row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], 
                                      row[13], location))

                # kml
                headers_0 = data_headers[0]
                data_headers[0] = 'Timestamp'
                kmlgen(report_folder, artifact_name, data_list, data_headers)
                data_headers[0] = headers_0

            db.close()

    # lava types
    data_headers[0] = (data_headers[0], 'datetime')

    return data_headers, data_list, report_file
