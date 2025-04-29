__artifacts_v2__ = {
    "booking": {
        "name": "Booking.com",
        "description": "account, payment methods, wish lists, viewed, recently searched, recently booked, booked, \
            stored destinations, notifications and flights searched",
        "author": "Django Faiola (djangofaiola.blogspot.com)",
        "version": "0.1.0",
        "date": "28/05/2024",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Preferences/com.booking.BookingApp.plist'),
        "function": "get_booking"
    }
}

import os
import json
import biplist
import plistlib
import nska_deserialize as nd
import sys
import shutil
import sqlite3
import textwrap
import pytz
from datetime import datetime, date
from pathlib import Path
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, open_sqlite_db_readonly, convert_ts_int_to_utc, convert_utc_human_to_timezone, \
    convert_ts_human_to_utc, media_to_html


def location_type_names(value):
    if (value == None) or (value < 0) or (value > 7):
        return ''
    # else:
    #     names = [ 'City', 'District', 'Region', 'Country', 'Hotel', 'Airport', 'Landmark', 'Google Places' ]
    #     return names[value]
    # city
    elif value == 0: return 'City'
    # district
    elif value == 1: return 'District'
    # district
    elif value == 2: return 'Region'
    # country
    elif value == 3: return 'Country'
    # hotel
    elif value == 4: return 'Hotel'
    # airport
    elif value == 5: return 'Airport'
    # landmark
    elif value == 6: return 'Landmark'
    # google place
    else: return 'Google Places'


def hotel_type_names(value):
    if (value == None):
        return ''
    # apartment
    elif value == 201: return 'Apartment'
    # guest accommodation
    elif value == 202: return 'Guest Accommodation'
    # hostel
    elif value == 203: return 'Hostel'
    # hotel
    elif value == 204: return 'Hotel'
    # motel
    elif value == 205: return 'Motel'
    # resort
    elif value == 206: return 'Resort'
    # residence
    elif value == 207: return 'Residence'
    # bed and breakfast
    elif value == 208: return 'Bed and Breakfast'
    # ryokan
    elif value == 209: return 'Ryokan'
    # farmstay
    elif value == 210: return 'Farmstay'
    # bungalow
    elif value == 211: return 'Bungalow'
    # resort village
    elif value == 212: return 'Resort Village'
    # villa
    elif value == 213: return 'Villa'
    # campground
    elif value == 214: return 'Campground'
    # boat
    elif value == 215: return 'Boat'
    # guesthouse
    elif value == 216: return 'Guesthouse'
    # inn
    elif value == 218: return 'Inn'
    # condo hotel
    elif value == 219: return 'Condo Hotel'
    # vacation home
    elif value == 220: return 'Vacation Home'
    # lodge
    elif value == 221: return 'Lodge'
    # homestay
    elif value == 222: return 'Homestay'
    # coutry house
    elif value == 223: return 'Country House'
    # luxury tent
    elif value == 224: return 'Luxury Tent'
    # capsule hotel
    elif value == 225: return 'Capsule Hotel'
    # love hotel
    elif value == 226: return 'Love Hotel'
    # riad
    elif value == 227: return 'Riad'
    # chalet
    elif value == 228: return 'Chalet'
    # condo
    elif value == 229: return 'Condo'
    # cottage
    elif value == 230: return 'Cottage'
    # economy hotel
    elif value == 231: return 'Economy Hotel'
    # gite
    elif value == 232: return 'Gite'
    # health resort
    elif value == 233: return 'Health Resort'
    # cruise
    elif value == 234: return 'Cruise'
    # student accommodation
    elif value == 235: return 'Student Accommodation'
    # unknown
    else: 
        return f'Unknown: {value}'


def convert_ts_utc_to_hotel_tz(ts, tz_str):
    utc_ts = pytz.timezone('UTC').localize(ts)
    return utc_ts.astimezone(pytz.timezone(tz_str))


def format_check_in_out(ts_from, ts_until, tz=''):
    # check-in
    if bool(ts_from):
        # seconds
        if isinstance(ts_from, float):
            check_from = convert_ts_int_to_utc(ts_from).strftime('%H:%M')
        # '00:00'
        elif isinstance(ts_from, str):
            check_from = ts_from
        # timestamp to time zone
        elif len(tz) > 0:
            check_from = convert_ts_utc_to_hotel_tz(ts_from, tz).strftime('%H:%M')
        # timestamp
        else:
            check_from = ts_from.strftime('%H:%M')
    else:
        check_from = '00:00'

    # check-out
    if bool(ts_until):
        # seconds
        if isinstance(ts_until, float):
            check_until = convert_ts_int_to_utc(ts_until).strftime('%H:%M')
        # '00:00'
        elif isinstance(ts_until, str):
            check_until = ts_until
        # timestamp to time zone
        elif len(tz) > 0:
            check_until = convert_ts_utc_to_hotel_tz(ts_until, tz).strftime('%H:%M')
        # timestamp
        else:
            check_until = ts_until.strftime('%H:%M')
    else:
        check_until = '00:00'

    return f'{check_from} - {check_until}'


def append_tag_value(target, tag, value):
    # "key: value"
    if value is None:
        return
    # dict, list, set, tuple
    elif isinstance(value, (dict, list, set, tuple)):
        if len(value) > 0:
            target.append(f'{tag}: {value}')
    else:
        target.append(f'{tag}: {value}')


def load_plist_from_string(data):
    if not bool(data):
        return None
    
    if isinstance(data, (bytes, bytearray)):
        isNska = data.find(b'NSKeyedArchiver') != -1
    else:
        isNska = data.find('NSKeyedArchiver') != -1

    if not isNska:
        if sys.version_info >= (3, 9):
            plist = plistlib.loads(data)
        else:
            plist = biplist.readPlistFromString(data)
    else:
        try:
            plist = nd.deserialize_plist_from_string(data)
        except (nd.DeserializeError, nd.biplist.NotBinaryPlistException, nd.biplist.InvalidPlistException,
                nd.plistlib.InvalidFileException, nd.ccl_bplist.BplistError, ValueError, TypeError, OSError, OverflowError) as ex:
            logfunc(f'Failed to read plist for {data}, error was:' + str(ex))
    return plist


# account
def get_account(file_found, report_folder, timezone_offset):
    data_list = []
    row = [ None ] * 15

    f = open(file_found, "rb")
    try:
        plist = plistlib.load(f)
        if bool(plist):
            # authentication token
            row[14] = plist.get('auth_token')
            # user profile
            user_profile = plist.get('user_profile')
            if bool(user_profile):
                # first name
                row[0] = user_profile.get('first_name')
                # last name
                row[1] = user_profile.get('last_name')
                # nickname
                # avatar
                try: row[2] = user_profile['avatar_details']['urls']['256']
                except: pass
                # gender
                row[3] = user_profile.get('gender')
                # date of birth (yyyy/mm/dd)
                dob = user_profile.get('date_of_birth')
                if bool(dob):
                    row[4] = dob.date()
                # street
                row[5] = user_profile.get('street')
                # city
                row[6] = user_profile.get('city')
                # zip code
                row[7] = user_profile.get('zipcode')
                # country
                row[8] = user_profile.get('country')
                # telephone
                row[9] = user_profile.get('telephone')
                # email address
                email_address = user_profile.get('email_address')
                if bool(email_address):
                    row[10] = ', '.join(email_address)
                # email data
                # genius membership
                row[11] = user_profile.get('is_genius')
                # preferred.facility
                preferred = user_profile.get('preferred')
                if bool(preferred):
                    facility = preferred.get('facility')
                    prefs = []
                    for x in facility:
                        if bool(x.get('is_selected')):
                            prefs.append(x.get('name'))
                    row[12] = ', '.join(prefs)
                # uid
                row[13] = user_profile.get('uid')

    except Exception as ex:
        logfunc('Exception while parsing Booking Account: ' + str(ex))
    finally:
        f.close()

    # row
    if row.count(None) != len(row):
        report = ArtifactHtmlReport('Booking Account')
        report.start_artifact_report(report_folder, 'Booking Account')
        report.add_script()
        data_headers = ('First name', 'Last name', 'Profile picture url', 'Gender', 'Birth date', 'Street', 'City', 'Zip code',
                        'Country', 'Telephone', 'Emails', 'Genius membership', 'Facilities', 'UID', 'Authentication token') 

        data_list.append(row)

        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()
                
        tsvname = f'Booking Account'
        tsv(report_folder, data_headers, data_list, tsvname)
                
        tlactivity = 'Booking Account'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Booking Account data available')


# account settings
def get_account_settings(file_found, report_folder, timezone_offset):
    data_list = []
    row = [ None ] * 11

    f = open(file_found, "rb")
    try:
        plist = plistlib.load(f)
        if bool(plist):
            # user details
            userDetails = None
            try: userDetails = plist['userDetailsResponse']['userDetails']
            except: pass

            if bool(userDetails):
                # personal details
                personalDetails = userDetails.get('personalDetails')
                if bool(personalDetails):
                    # gender
                    row[3] = personalDetails.get('gender')
                    # name
                    name = personalDetails.get('name')
                    if bool(name):
                        # first name
                        row[0] = name.get('first')
                        # last name
                        row[1] = name.get('last')
                    # displayName
                    # date of birth
                    dateOfBirth = personalDetails.get('dateOfBirth')
                    if bool(dateOfBirth):
                        row[4] = date(dateOfBirth.get('year'), dateOfBirth.get('month'), dateOfBirth.get('day'))
                    # avatar
                    try: row[2] = personalDetails['avatar']['urls']['square256']
                    except: pass
                # contact details
                contactDetails = userDetails.get('contactDetails')
                if bool(contactDetails):
                    # address
                    address = contactDetails.get('address')
                    if bool(address):
                        # street
                        row[5] = address.get('street')
                        # city
                        row[6] = address.get('cityName')
                        # zip
                        row[7] = address.get('zip')
                        # country code
                        row[8] = address.get('countryCode')
                    # email address
                    try: row[10] = contactDetails['primaryEmail']['address']
                    except: pass
                    # telephone
                    try: row[9] = contactDetails['primaryPhone']['fullNumber']
                    except: pass

    except Exception as ex:
        logfunc('Exception while parsing Booking Account: ' + str(ex))
    finally:
        f.close()

    # row
    if row.count(None) != len(row):
        report = ArtifactHtmlReport('Booking Account Settings')
        report.start_artifact_report(report_folder, 'Booking Account Settings')
        report.add_script()
        data_headers = ('First name', 'Last name', 'Profile picture url', 'Gender', 'Birth date', 'Street', 'City', 'Zip code',
                        'Country', 'Telephone', 'Email') 

        data_list.append(row)

        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()
                
        tsvname = f'Booking Account Settings'
        tsv(report_folder, data_headers, data_list, tsvname)
                
        tlactivity = 'Booking Account Settings'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Account Settings data available')


# payment methods
def get_payment_methods(file_found, report_folder, timezone_offset):
    data_list = []

    f = open(file_found, "rb")
    try:
        plist = plistlib.load(f)
        if bool(plist):
            # user profile
            user_profile = plist.get('user_profile')
            if bool(user_profile):
                # credit card details
                cc_details = user_profile.get('cc_details')
                if bool(cc_details):
                    # array
                    for i in range(0, len(cc_details)):
                        row = [ None ] * 7
                        cc = cc_details[i]
                        # cc_id
                        row[0] = cc.get('cc_id')
                        # cc_type
                        row[1] = cc.get('cc_type')
                        # cc_status
                        row[2] = cc.get('cc_status')
                        # cc_expire_year
                        ey = cc.get('cc_expire_year')
                        # cc_expire_month
                        em = cc.get('cc_expire_month')
                        # valid thru (mm-yyyy)
                        row[3] = f'{ey}-{em:02}'
                        # cc_name
                        row[4] = cc.get('cc_name')
                        # last_digits
                        row[5] = cc.get('last_digits')
                        # cc_is_business
                        row[6] = cc.get('cc_is_business')
                        # location
                        location = f'[user_profile][cc_details][{i}]'

                        # row
                        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], location))

    except Exception as ex:
        logfunc('Exception while parsing Booking Payment Methods: ' + str(ex))
    finally:
        f.close()

    # row
    if len(data_list) > 0:
        report = ArtifactHtmlReport('Booking Payment Methods')
        report.start_artifact_report(report_folder, 'Booking Payment Methods')
        report.add_script()
        data_headers = ('UID', 'Type', 'Status', 'Valid thru', 'Cardholder name', 'Last four digits', 'Business', 'Location') 

        #data_list.append(row)

        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()
                
        tsvname = f'Booking Payment Methods'
        tsv(report_folder, data_headers, data_list, tsvname)
                
        tlactivity = 'Booking Payment Methods'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Booking Payment Methods data available')


# payment methods settings
def get_payment_methods_settings(file_found, report_folder, timezone_offset):
    data_list = []

    f = open(file_found, "rb")
    try:
        plist = plistlib.load(f)
        if bool(plist):
            # values
            values = None
            try: values = plist['cardsResponse']['values']
            except: pass
 
            if bool(values):
                # credit cards
                for i in range(0, len(values)):
                    row = [ None ] * 5
                    cc = values[i]
                    # id
                    row[0] = cc.get('id')
                    # type/name
                    row[1] = cc.get('name')
                    # status
                    row[2] = cc.get('status')
                    # valid thru (mm-yyyy)
                    row[3] = cc.get('expirationDateFormatted')
                    # last_digits
                    row[4] = cc.get('lastDigits')
                    # location
                    location = f'[cardsResponse][values][{i}]'

                    # row
                    data_list.append((row[0], row[1], row[2], row[3], row[4], location))

    except Exception as ex:
        logfunc('Exception while parsing Booking Payment Methods Settings: ' + str(ex))
    finally:
        f.close()

    # row
    if len(data_list) > 0:
        report = ArtifactHtmlReport('Booking Payment Methods Settings')
        report.start_artifact_report(report_folder, 'Booking Payment Methods Settings')
        report.add_script()
        data_headers = ('UID', 'Type', 'Status', 'Valid thru', 'Last four digits', 'Location') 

        #data_list.append(row)

        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()
                
        tsvname = f'Booking Payment Methods Settings'
        tsv(report_folder, data_headers, data_list, tsvname)
                
        tlactivity = 'Booking Payment Methods Settings'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Booking Payment Methods Settings data available')


# recently searched
def get_recently_searched(file_found, report_folder, timezone_offset):
    data_list = []

    f = open(file_found, "rb")
    try:
        plist = plistlib.load(f)
        if bool(plist):
            # stored searches
            stored_searches = plist.get('stored_searches')
            if bool(stored_searches):
                # array
                for i in range(0, len(stored_searches)):
                    row = [ None ] * 17
                    ss = stored_searches[i]

                    # searched
                    searched = ss.get('created')
                    if bool(searched):
                        searched = convert_ts_human_to_utc(str(searched))
                        row[0] = convert_utc_human_to_timezone(searched, timezone_offset)
                    # destination
                    destination = ss.get('destination')
                    if bool(destination):
                        # location type
                        row[1] = location_type_names(destination.get('locationType_'))
                        # id
                        row[2] = destination.get('id_')
                        # destination name
                        row[3] = destination.get('string_')
                        # description (place name)
                        row[4] = destination.get('substring_')
                        if not bool(row[4]): row[4] = destination.get('address')    # (locationType_=7)
                        # city_
                        city = destination.get('city_')
                        if bool(city):
                            # city name
                            row[5] = city.get('string_')
                            # region name
                            row[6] = city.get('region_name')
                        # no city_
                        else:
                            # city name
                            row[5] = destination.get('cityName_')
                            # region
                            row[6] = destination.get('region_name')
                        # country name
                        row[7] = destination.get('countryName_')
                        if not bool(row[7]): row[7] = destination.get('country')    # (locationType_=7)
                        # location (locationType_=7)
                        location_dict = city = destination.get('location')
                        if bool(location_dict):
                            # latitude
                            row[8] = location_dict.get('latitude')
                            # longitude
                            row[9] = location_dict.get('longitude')
                        # no location
                        else:
                            # latitude
                            row[8] = destination.get('latitude_')
                            # longitude
                            row[9] = destination.get('longitude_')
                        # time zone
                        row[10] = destination.get('timezone')
                    # check-in
                    row[11] = ss.get('checkin')
                    # check-out
                    row[12] = ss.get('checkout')
                    # number of rooms
                    row[13] = ss.get('number_of_rooms')
                    # guests per room
                    row[14] = ss.get('guests_per_room')
                    # number of nights
                    row[15] = ss.get('number_of_nights')
                    # source
                    row[16] = ss.get('source')

                    # location
                    location = f'[stored_searches][{i}]'

                    # row
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], 
                                      row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], 
                                      row[16], location))

    except Exception as ex:
        logfunc('Exception while parsing Booking Recently Searched: ' + str(ex))
    finally:
        f.close()

    # row
    if len(data_list) > 0:
        report = ArtifactHtmlReport('Booking Recently Searched')
        report.start_artifact_report(report_folder, 'Booking Recently Searched')
        report.add_script()
        data_headers = ('Searched', 'Location type', 'Id', 'Destination name', 'Description', 'City', 'Region', 'Country', 
                        'Latitude', 'Longitude', 'Time zone', 'Check-in', 'Check-out', 'Number of rooms', 'Guests', 'Number of nights', 
                        'Source', 'Location')

        #data_list.append(row)

        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()
                
        tsvname = f'Booking Recently Searched'
        tsv(report_folder, data_headers, data_list, tsvname)
                
        tlactivity = 'Booking Recently Searched'
        timeline(report_folder, tlactivity, data_list, data_headers)

        kmlactivity = 'Booking Recently Searched'
        kmlgen(report_folder, kmlactivity, data_list, data_headers)    
    else:
        logfunc('No Booking Recently Searched data available')


# wish lists
def get_wish_lists(file_found, report_folder, timezone_offset):
    data_list = []

    f = open(file_found, "rb")
    try:
        plist = plistlib.load(f)
        if bool(plist):
            # wish lists
            wish_lists = plist.get('wishlists')
            if bool(wish_lists):
                # array
                for i in range(0, len(wish_lists)):
                    row = [ None ] * 3
                    wish = wish_lists[i]

                    # list name
                    row[1] = wish.get('name')
                    # hotels
                    hotels = wish.get('hotels')
                    for j in range(0, len(hotels)):
                        hotel = hotels[j]
                        # added
                        added = hotel.get('created')
                        if bool(added):
                            added = convert_ts_human_to_utc(str(added))
                            row[0] = convert_utc_human_to_timezone(added, timezone_offset)

                        row[2] = hotel['id']
                        
                        # location
                        location = f'[wishlists][{i}], [wishlists][{i}][hotels][{j}]'

                        # row
                        data_list.append((row[0], row[1], row[2], location))

    except Exception as ex:
        logfunc('Exception while parsing Booking Wish Lists: ' + str(ex))
    finally:
        f.close()

    # row
    if len(data_list) > 0:
        report = ArtifactHtmlReport('Booking Wish Lists')
        report.start_artifact_report(report_folder, 'Booking Wish Lists')
        report.add_script()
        data_headers = ('Added', 'Title', 'Hotel Id', 'Location') 

        #data_list.append(row)

        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()
                
        tsvname = f'Booking Wish Lists'
        tsv(report_folder, data_headers, data_list, tsvname)
                
        tlactivity = 'Booking Wish Lists'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Booking Wish Lists data available')


# recently booked
def get_recently_booked(file_found, report_folder, timezone_offset):
    data_list = []

    f = open(file_found, "rb")
    try:
        plist = plistlib.load(f)
        if bool(plist):
            # booked
            booked = plist.get('booked')
            if bool(booked):
                # array
                for key, value in booked.items():
                    # hotel
                    hotel = value.get('hotel')
                    if bool(hotel):
                        row = [ None ] * 13
                        # hotel type
                        row[0] = hotel_type_names(hotel.get('hotel_type'))
                        # hotel id = key
                        row[1] = hotel.get('hotel_id')
                        # name
                        row[2] = hotel.get('name')
                        # address
                        row[3] = hotel.get('address')
                        # city
                        city = hotel.get('city')
                        if bool(city):
                            # city
                            row[4] = city.get('string_')
                            # region
                            row[5] = city.get('region_name')
                        # no city
                        else:
                            # city name
                            row[4] = hotel.get('cityName')
                            # region name
                            row[5] = hotel.get('region_name')
                        # zip code
                        row[6] = hotel.get('zip')
                        # latitude
                        row[7] = hotel.get('latitude')
                        # longitude
                        row[8] = hotel.get('longitude')
                        # check-in
                        row[9] =format_check_in_out(hotel.get('checkInFrom'), hotel.get('checkInUntil'))
                        # check-out
                        row[10] =format_check_in_out(hotel.get('checkOutFrom'), hotel.get('checkOutUntil'))
                        # picture url
                        row[11] = hotel.get('pictureURL')
                        # website
                        row[12] = hotel.get('hotelURL')

                        # location
                        location = f'[booked][{key}]'

                        # row
                        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], 
                                          row[8], row[9], row[10], row[11], row[12], location))

    except Exception as ex:
        logfunc('Exception while parsing Booking Recently Booked: ' + str(ex))
    finally:
        f.close()

    # row
    if len(data_list) > 0:
        report = ArtifactHtmlReport('Booking Recently Booked')
        report.start_artifact_report(report_folder, 'Booking Recently Booked')
        report.add_script()
        data_headers = ('Hotel type', 'Hotel Id', 'Hotel name', 'Address', 'City', 'Region', 'Zip code', 'Latitude', 'Longitude', 
                        'Check-in (Hotel time zone)', 'Check-out (Hotel time zone)', 'Picture url', 'Website', 'Location') 

        #data_list.append(row)

        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()
                
        tsvname = f'Booking Recently Booked'
        tsv(report_folder, data_headers, data_list, tsvname)
                
        tlactivity = 'Booking Recently Booked'
        timeline(report_folder, tlactivity, data_list, data_headers)

        kmlactivity = 'Booking Recently Booked'
        kmlgen(report_folder, kmlactivity, data_list, data_headers)    
    else:
        logfunc('No Booking Recently Booked data available')


# viewed
def get_viewed(file_found, report_folder, timezone_offset):
    data_list = []

    f = open(file_found, "rb")
    try:
        plist = plistlib.load(f)
        if bool(plist):
            # viewed
            viewed = plist.get('viewed')
            if bool(viewed):
                # array
                for key, value in viewed.items():
                    row = [ None ] * 12

                    # hotel
                    hotel = value.get('hotel')
                    if bool(hotel):
                        # last viewed
                        last_viewed = hotel.get('lastViewed')
                        if bool(last_viewed):
                            last_viewed = convert_ts_human_to_utc(str(last_viewed))
                            row[0] = convert_utc_human_to_timezone(last_viewed, timezone_offset)
                        row[1] = hotel_type_names(hotel.get('hotel_type'))
                        # key=id
                        row[2] = hotel.get('hotel_id')
                        # name
                        row[3] = hotel.get('name')
                        # address
                        row[4] = hotel.get('address')
                        # city
                        city = hotel.get('city')
                        if bool(city):
                            # city name
                            row[5] = city.get('string_')
                            # region
                            row[6] = city.get('region_name')
                        # zip code
                        row[7] = hotel.get('zip')
                        # latitude
                        row[8] = hotel.get('latitude')
                        # longitude
                        row[9] = hotel.get('longitude')
                        # picture url
                        row[10] = hotel.get('pictureURL')
                        # website
                        row[11] = hotel.get('hotelURL')

                    # location
                    location = f'[viewed][{key}]'

                    # row
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                      row[8], row[9], row[10], row[11], location))

    except Exception as ex:
        logfunc('Exception while parsing Booking Viewed: ' + str(ex))
    finally:
        f.close()

    # row
    if len(data_list) > 0:
        report = ArtifactHtmlReport('Booking Viewed')
        report.start_artifact_report(report_folder, 'Booking Viewed')
        report.add_script()
        data_headers = ('Last viewed', 'Hotel type', 'Hotel Id', 'Hotel name', 'Address', 'City', 'Region', 'Zip code',
                        'Latitude', 'Longitude', 'Picture url', 'Website', 'Location') 

        #data_list.append(row)

        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()
                
        tsvname = f'Booking Viewed'
        tsv(report_folder, data_headers, data_list, tsvname)
                
        tlactivity = 'Booking Viewed'
        timeline(report_folder, tlactivity, data_list, data_headers)

        kmlactivity = 'Booking Viewed'
        kmlgen(report_folder, kmlactivity, data_list, data_headers)    
    else:
        logfunc('No Booking Viewed data available')


# booked
def get_booked(file_found, documents, report_folder, timezone_offset):
    data_list = []

    f = open(file_found, "rb")
    try:
        plist = plistlib.load(f)
        if bool(plist):
            for key_b, value_b in plist.items():
                if not isinstance(value_b, dict):
                    continue
                  
                # booked
                if (key_b == 'DeviceBookings') or (key_b == 'AccountBookings'):
                    # array
                    for key, value in value_b.items():
                        row = [ None ] * 14

                        # created
                        created = value.get('created_epoch')
                        if bool(created):
                            created = convert_ts_human_to_utc(str(created))
                            row[0] = convert_utc_human_to_timezone(created, timezone_offset)
                        # name
                        row[1] = value.get('hotel_id')
                        # name
                        row[2] = value.get('hotel_name')
                        # full address + couuntry
                        row[3] = value.get('hotel_full_address')
                        # country name
                        country_name = value.get('hotel_country_name')
                        row[3] = ', '.join([row[3], country_name])
                        # time zone
                        hotel_time_zone = value.get('hotel_timezone')
                        row[4] = hotel_time_zone

                        # check-in - check out
                        check_io = []
                        # check-in
                        tmp = value.get('checkin')
                        if bool(tmp):
                            tmp = f"Check-in: {tmp.strftime('%Y-%m-%d')}"
                            tmp = tmp + ' ' + format_check_in_out(value.get('checkin_from_epoch'), value.get('checkin_until_epoch'), tz=hotel_time_zone)
                            check_io.append(tmp)
                        # check-out
                        tmp = value.get('checkout')
                        if bool(tmp):
                            tmp = f"Check-out: {tmp.strftime('%Y-%m-%d')}"
                            tmp = tmp + ' ' + format_check_in_out(value.get('checkout_from_epoch'), value.get('checkout_until_epoch'), tz=hotel_time_zone)
                            check_io.append(tmp)
                        row[5] = '<br />'.join(check_io)

                        # hotel contacts
                        hotel_contacts = []
                        # telephone
                        append_tag_value(hotel_contacts, 'Telephone', value.get('hotel_telephone'))
                        # email
                        append_tag_value(hotel_contacts, 'Email', value.get('hotel_email'))
                        row[6] = '<br />'.join(hotel_contacts)
                        
                        # confirmation number
                        confirm_info = []
                        append_tag_value(confirm_info, 'Confirmation number', value.get('id'))
                        # pin code
                        append_tag_value(confirm_info, 'Pin code', value.get('pincode'))
                        row[7] = '<br />'.join(confirm_info)

                        # currency code + total price
                        row[8] = f"{value.get('user_selected_currency_code')} {value.get('totalprice', '0'):.4f}"

                        # rooms
                        room_meta = []
                        rooms = value.get('room')
                        if bool(rooms):
                            # number of rooms
                            row[9] = len(rooms)

                            for r in range(len(rooms)):
                                room = rooms[r]
                                room_meta.append(f"Room {r} - {room.get('name', '')}")
                                # guest name
                                append_tag_value(room_meta, 'Guest name', room.get('guest_name'))
                                # number of guests
                                append_tag_value(room_meta, 'Number of guests', room.get('nr_guests'))
                                # is cancelled
                                append_tag_value(room_meta, 'Cancelled', room.get('is_cancelled'))
                                # cancel date
                                cancel_date = room.get('cancel_date')
                                if bool(cancel_date):
                                    cancel_date = convert_ts_human_to_utc(str(cancel_date))
                                    cancel_date = convert_utc_human_to_timezone(cancel_date, timezone_offset)
                                    append_tag_value(room_meta, 'Cancel date', cancel_date)
                                # room id
                                append_tag_value(room_meta, 'Identifier', room.get('room_id'))
                                # room photo (string)
                                append_tag_value(room_meta, 'URL photo', room.get('room_photo'))
                                # room photos (array)
                                room_photos = room.get('room_photos')
                                if bool(room_photos):
                                    for j in range(len(room_photos)):
                                        # url_original
                                        append_tag_value(room_meta, f'URL photo #{j}', room_photos[j].get('url_original'))
                                # room separator
                                if r < len(rooms) - 1:
                                    room_meta.append('<hr>')
                        row[10] = '<br />'.join(room_meta).replace('<hr><br />', '<hr>')

                        # booker details
                        booker_details = []
                        # first name
                        append_tag_value(booker_details, 'First name', value.get('booker_firstname'))
                        # last name
                        append_tag_value(booker_details, 'Last name', value.get('booker_lastname'))
                        # country code                        
                        append_tag_value(booker_details, 'Country code', value.get('booker_cc1'))
                        # email
                        append_tag_value(booker_details, 'Email', value.get('booker_email'))
                        # credit card last digits
                        append_tag_value(booker_details, 'Credit card last four digits', value.get('cc_number_last_digits'))
                        row[11] = '<br />'.join(booker_details)
            
                        # source (ios-app, web, etc.)
                        row[12] = value.get('source')

                        # attachment (key=id)Booking
                        if len(documents) > 0:
                            # url encode "#"???
                            attachment_file = f'Booking #{key}.pdf'
                            row[13] = media_to_html(attachment_file, documents, report_folder)
                            if not row[13].startswith('<'):
                                row[13] = ''
                            else:
                                # ".\Booking.com\Documents\Booking #0123456789.pdf" -> ".\Booking.com\Documents\Booking %230123456789.pdf"
                                row[13] = row[13].replace(attachment_file+'"', f'Booking %23{key}.pdf"')

                        # location
                        location = f'[{key_b}][{key}]'

                        # row
                        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], 
                                          row[7], row[8], row[9], row[10], row[11], row[12], row[13], 
                                          location))

    except Exception as ex:
        logfunc('Exception while parsing Booking Booked: ' + str(ex))
    finally:
        f.close()

    # row
    if len(data_list) > 0:
        report = ArtifactHtmlReport('Booking Booked')
        report.start_artifact_report(report_folder, 'Booking Booked')
        report.add_script()
        data_headers = ('Created', 'Hotel Id', 'Hotel name', 'Full address', 'Time zone', 'Check-in/out (Hotel time zone)', 'Hotel contacts', 
                        'Confirmation number/Pin code', 'Total price', 'Number of rooms', 'Rooms', 'Booker details', 'Source', 'Attachment', 
                        'Location') 

        #data_list.append(row)

        report.write_artifact_data_table(data_headers, data_list, file_found, \
                                         html_no_escape=['Check-in/out (Hotel time zone)', 'Hotel contacts', 'Confirmation number/Pin code',
                                                         'Rooms', 'Booker details', 'Attachment'])
        report.end_artifact_report()
                
        tsvname = f'Booking Booked'
        tsv(report_folder, data_headers, data_list, tsvname)
                
        tlactivity = 'Booking Booked'
        timeline(report_folder, tlactivity, data_list, data_headers)

        #kmlactivity = 'Booking Booked'
        #kmlgen(report_folder, kmlactivity, data_list, data_headers)    
    else:
        logfunc('No Booking Booked data available')


# stored destinations
def get_stored_destinations(file_found, report_folder, timezone_offset):
    data_list = []

    f = open(file_found, "rb")
    try:
        plist = plistlib.load(f)
        if bool(plist):
            # stored destinations
            stored_destinations = plist.get('stored_destinations')
            if bool(stored_destinations):
                # array
                for i in range(len(stored_destinations)):
                    row = [ None ] * 12
                    dest = stored_destinations[i]

                    # created/last updated
                    created = dest.get('created')
                    if bool(created):
                        created = convert_ts_human_to_utc(str(created))
                        row[0] = convert_utc_human_to_timezone(created, timezone_offset)
                    # location
                    loc = dest.get('loc')
                    if bool(loc):
                        # location type
                        row[1] = location_type_names(loc.get('locationType_'))
                        # id
                        row[2] = loc.get('id_')
                        # destination name
                        row[3] = loc.get('string_')
                        # description (place name)
                        row[4] = loc.get('substring_')
                        if not bool(row[4]): row[4] = loc.get('address')    # (locationType_=7)
                        # city_
                        city = loc.get('city_')
                        if bool(city):
                            # city name
                            row[5] = city.get('string_')
                            # region name
                            row[6] = city.get('region_name')
                        # no city_
                        else:
                            # city name
                            row[5] = loc.get('cityName_')
                            # region
                            row[6] = loc.get('region_name')
                        # country name
                        row[7] = loc.get('countryName_')
                        if not bool(row[7]): row[7] = loc.get('country')    # (locationType_=7)
                        # location (locationType_=7)
                        location_dict = city = loc.get('location')
                        if bool(location_dict):
                            # latitude
                            row[8] = location_dict.get('latitude')
                            # longitude
                            row[9] = location_dict.get('longitude')
                        # no location
                        else:
                            # latitude
                            row[8] = loc.get('latitude_')
                            # longitude
                            row[9] = loc.get('longitude_')
                        # time zone
                        row[10] = loc.get('timezone')
                        # image url
                        row[11] = loc.get('image_url')

                    # location
                    location = f'[stored_destinations][{i}]'

                    # row
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], 
                                      row[8], row[9], row[10], row[11], location))

    except Exception as ex:
        logfunc('Exception while parsing Booking Stored Destinations: ' + str(ex))
    finally:
        f.close()

    # row
    if len(data_list) > 0:
        report = ArtifactHtmlReport('Booking Stored Destinations')
        report.start_artifact_report(report_folder, 'Booking Stored Destinations')
        report.add_script()
        data_headers = ('Created', 'Location type', 'Id', 'Destination name', 'Address/Description', 'City', 'Region', 'Country',
                        'Latitude', 'Longitude', 'Time zone', 'URL image', 'Location') 

        #data_list.append(row)

        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()
                
        tsvname = f'Booking Stored Destinations'
        tsv(report_folder, data_headers, data_list, tsvname)
                
        tlactivity = 'Booking Stored Destinations'
        timeline(report_folder, tlactivity, data_list, data_headers)

        kmlactivity = 'Booking Stored Destinations'
        kmlgen(report_folder, kmlactivity, data_list, data_headers)    
    else:
        logfunc('No Booking Stored Destinations data available')


# notifications
def get_notifications(file_found, report_folder, timezone_offset):
    database = open_sqlite_db_readonly(file_found)
    try:
        cursor = database.cursor()
        cursor.execute('''
        SELECT
	        ROWID AS "N_ID",
            (ZDATE + 978307200) AS "timestamp",
            ZIDENTIFIER AS "identifier",
            ZTITLE AS "title",
            ZBODY AS "message",
            ZVIEWED AS "viewed",
            ZLOCALLYDELETED AS "deleted",
            ZACTIONIDENTIFIER AS "action_id",
            ZACTIONARGUMENTS AS "arguments"
        FROM ZNOTIFICATION
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Booking Notifications')
            report.start_artifact_report(report_folder, 'Booking Notifications')
            report.add_script()
            data_headers = ('Timestamp', 'Identifier', 'Title', 'Message', 'Viewed', 'Deleted', 'Action Id', 'Action arguments', 'Location') 
            data_list = []
            for row in all_rows:
                # timestamp
                if bool(row[1]):
                    timestamp = convert_ts_int_to_utc(row[1])
                    timestamp = convert_utc_human_to_timezone(timestamp, timezone_offset)
                else:
                    timestamp = ''
                # is_viewed
                is_viewed = bool(row[5])
                # is_deleted
                is_deleted = bool(row[6])
                # arguments
                arguments = ''
                try:
                    # plist = load_plist_from_string(row[8])
                    # arguments = str(plist)
                    arguments = load_plist_from_string(row[8])
                except Exception as ex:
                    logfunc('Exception while parsing Booking Notifications action arguments: ' + str(ex))
                    pass

                # location
                location = f'ZNOTIFICATION (ROWID: {row[0]})'

                # row
                data_list.append((timestamp, row[2], row[3], row[4], is_viewed, is_deleted, row[7], arguments, location))

            report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Action arguments'])
            report.end_artifact_report()
                
            tsvname = f'Booking Notifications'
            tsv(report_folder, data_headers, data_list, tsvname)
                
            tlactivity = f'Booking Notifications'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Booking Notifications data available')

    except Exception as ex:
        logfunc('Exception while parsing Booking Notifications: ' + str(ex))


# flights searched
def get_flights_searched(file_found, report_folder, timezone_offset):
    data_list = []

    # airports details
    def get_airports(airports, section_name='Airport'):
        if not bool(airports) or not isinstance(airports, list):
            return ''
        
        airport_meta = []
        for a in range(len(airports)):
            airport = airports[a]
            airport_meta.append(f"{section_name} {a} - {airport.get('name', '')}")
            # city name
            append_tag_value(airport_meta, 'City', airport.get('cityName'))
            # region name
            append_tag_value(airport_meta, 'Region', airport.get('regionName'))
            # country name
            append_tag_value(airport_meta, 'Country', airport.get('coutryName'))
            # type
            append_tag_value(airport_meta, 'Type', airport.get('type'))
            # code
            append_tag_value(airport_meta, 'Code', airport.get('code'))
            # selected
            append_tag_value(airport_meta, 'Selected', airport.get('selected'))
                                
            # airport separator
            if a < len(airports) - 1:
                airport_meta.append('<hr>')
        return '<br />'.join(airport_meta).replace('<hr><br />', '<hr>')
    
    # routes
    def get_routes(routes):
        if not bool(routes) or not isinstance(routes, list):
            return ""

        routes_meta = []
        for r in range(len(routes)):
            route = routes[r]
            
            # start date
            start_date = None
            try: start_date = date(route.get('startYear'), route.get('startMonth'), route.get('startDay'))
            except: pass
            if not bool(start_date):
                continue
            routes_meta.append(f'Route {r} - {start_date}')
            # sources airports
            routes_meta.append(get_airports(route.get('sourceAirports'), section_name='Source airport'))
            # destinations airports
            routes_meta.append(get_airports(route.get('destinationAirports'), section_name='Destination airport'))

            # routes separator
            if r < len(routes) - 1:
                routes_meta.append('<hr>')
        return '<br />'.join(routes_meta).replace('<hr><br />', '<hr>')


    f = open(file_found, 'r', encoding='utf-8')
    try:
        json_data = json.load(f)
        if bool(json_data):
            # flights (array)
            flights = json_data.get('value')
            if bool(flights):
                # array
                for i in range(0, len(flights)):
                    # flight
                    flight = flights[i]
                    row = [ None ] * 10

                    # last updated
                    last_updated = flight.get('lastUpdated')
                    if bool(last_updated):
                         last_updated = datetime.fromisoformat(last_updated)
                         row[0] = convert_utc_human_to_timezone(last_updated, timezone_offset)
                    # parameters
                    params = flight['parameters']['searchOptionModel']
                    # start date
                    try: row[1] = date(params.get('startYear'), params.get('startMonth'), params.get('startDay'))
                    except: pass
                    # return date (returnType=ONEWAY-> returnYear, returnMonth, returnDay are Null)
                    try: row[2] = date(params.get('returnYear'), params.get('returnMonth'), params.get('returnDay'))
                    except: pass
                    # direct flight
                    row[3] = params.get('direct')
                    # search type
                    row[4] = params.get('searchType')
                    # cabin
                    row[5] = params.get('cabin')
                    # source airports
                    row[6] = get_airports(params.get('sourceAirports'))
                    # destination airports
                    row[7] = get_airports(params.get('destinationAirports'))
                    # routes
                    row[8] = get_routes(params.get('routes'))
                    # travellers' details
                    travellers_details = params.get('travellersDetails')
                    if bool(travellers_details):
                        travellers_meta = []
                        # adults count
                        append_tag_value(travellers_meta, 'Adults count', travellers_details.get('adultsCount'))
                        # children count
                        append_tag_value(travellers_meta, 'Children count', travellers_details.get('childrenCount'))
                        # children ages (array of int)
                        children_ages = travellers_details.get('childrenAges')
                        if bool(children_ages):
                            append_tag_value(travellers_meta, 'Children ages', ', '.join([str(x) for x in children_ages]))
                        row[9] = '<br />'.join(travellers_meta)

                    # location
                    location = f'[value][{i}]'

                    # row
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], 
                                      row[6], row[7], row[8], row[9], location))

    except Exception as ex:
        logfunc('Exception while parsing Booking Flights Searched: ' + str(ex))
    finally:
        f.close()

    # row
    if len(data_list) > 0:
        report = ArtifactHtmlReport('Booking Flights Searched')
        report.start_artifact_report(report_folder, 'Booking Flights Searched')
        report.add_script()
        data_headers = ('Last updated', 'Start date', 'Return date', 'Direct flight', 'Search type', 'Cabin class', 
                        'Source airports', 'Destination airports', 'Routes', "Travellers' details", 'Location') 

        #data_list.append(row)

        report.write_artifact_data_table(data_headers, data_list, file_found, 
                                         html_no_escape=['Source airports', 'Destination airports', 'Routes', "Travellers' details"])
        report.end_artifact_report()
                
        tsvname = f'Booking Flights Searched'
        tsv(report_folder, data_headers, data_list, tsvname)
                
        tlactivity = 'Booking Flights Searched'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Booking Flights Searched data available')


# booking
def get_booking(files_found, report_folder, seeker, wrap_text, timezone_offset):
    identifier = ''

    for file_found in files_found:
        if file_found.endswith('com.booking.BookingApp.plist'):
            # Library/Preferences/com.booking.BookingApp.plist
            identifier = (Path(file_found).parts[-4:])[0]
            break

    if len(identifier) > 0:
        # Documents
        documents = seeker.search(f'*/{identifier}/Documents/*', return_on_first_hit=False)

        # */Library/Application Support/KeyValueStorageAccountDomain[.plist]
        source_files = seeker.search(f'*/{identifier}/Library/Application Support/KeyValueStorageAccountDomain*', return_on_first_hit=True)
        if bool(source_files):
            # account
            get_account(source_files, report_folder, timezone_offset)

            # payment methods
            get_payment_methods(source_files, report_folder, timezone_offset)

        # */Library/Application Support/AccountSettings[.plist]
        source_files = seeker.search(f'*/{identifier}/Library/Application Support/AccountSettings*', return_on_first_hit=True)
        if bool(source_files):
            # account settings
            get_account_settings(source_files, report_folder, timezone_offset)

            # payment methods settings
            get_payment_methods_settings(source_files, report_folder, timezone_offset)

        # */Library/Application Support/BookingClouds[.plist]
        source_files = seeker.search(f'*/{identifier}/Library/Application Support/BookingClouds*', return_on_first_hit=True)
        if bool(source_files):
            # booked
            get_booked(source_files, documents, report_folder, timezone_offset)

        # */Library/Application Support/KeyValueStorageRecentsDomain[.plist]
        source_files = seeker.search(f'*/{identifier}/Library/Application Support/KeyValueStorageRecentsDomain*', return_on_first_hit=True)
        if bool(source_files):
            # recently searched
            get_recently_searched(source_files, report_folder, timezone_offset)

            # recently booked
            get_recently_booked(source_files, report_folder, timezone_offset)

            # viewed
            get_viewed(source_files, report_folder, timezone_offset)

            # wish lists
            get_wish_lists(source_files, report_folder, timezone_offset)

        # */Library/Application Support/KeyValueStorageSharedDomain[.plist]
        source_files = seeker.search(f'*/{identifier}/Library/Application Support/KeyValueStorageSharedDomain*', return_on_first_hit=True)
        if bool(source_files):
            # stored destinations
            get_stored_destinations(source_files, report_folder, timezone_offset)

        # */Library/Application Support/NotificationsModel.sqlite
        source_files = seeker.search(f'*/{identifier}/Library/Application Support/NotificationsModel.sqlite*')
        for file_found in source_files:
            file_found = str(file_found)
            if file_found.endswith('.sqlite'):
                # notifications
                get_notifications(file_found, report_folder, timezone_offset)

        # */Library/Application Support/flight_rs_v2
        source_files = seeker.search(f'*/{identifier}/Library/Application Support/flight_rs_v2', return_on_first_hit=True)
        if bool(source_files):
            # flights searched
            get_flights_searched(source_files, report_folder, timezone_offset)
