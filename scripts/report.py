import html
import os
import pathlib
import shutil
import sqlite3
import sys

from collections import OrderedDict
from scripts.html_parts import *
from scripts.ilapfuncs import logfunc
from scripts.version_info import aleapp_version, aleapp_contributors

# Icon Mappings Dictionary
# The icon_mappings dictionary is organized by category and is used to map categories and artifacts to icons.
# Please maintain the list in alphabetical order by category for ease of navigation and updating.
#
# To specify an icon for a particular artifact within a category, use the structure:
# 'CATEGORY': {'ARTIFACT': 'icon-name', ...}
# Example:
# 'CHROMIUM': {'BOOKMARKS': 'bookmark', 'DOWNLOADS': 'download', ...}
#
# To specify a default icon for all artifacts within a category or a single icon for the entire category, use:
# 'CATEGORY': 'icon-name' or 'CATEGORY': {'default': 'icon-name', ...}
# Example:
# 'ADDRESS BOOK': 'book-open'
#
# If a category or artifact does not have a specified icon, the 'alert-triangle' icon will be used as a fallback.
#
# Icons are sourced from Feather Icons (feathericons.com). When adding a new icon, ensure that the icon name
# matches the name listed on the Feather Icons website.
#
# The optional '_mode' key can be used to specify a search mode for finding matching artifacts within a category:
# 'CATEGORY': {'_mode': 'search', ...}
# In search mode, the function will attempt to find a partial match for the artifact name within the specified category.

icon_mappings = \
{
    'ACCESSORY DATA HYUNDAI': 'settings',
    'ACCOUNT': {
        'AUTH': 'key',
        'default': 'user',
        '_mode': 'search',
    },
    'ADB HOSTS': 'terminal',
    'ADDRESS BOOK': 'book-open',
    'ADIDAS-RUNNING': {
        'ACTIVITIES': 'activity',
        'GOALS': 'target',
        'USER': 'user',
        'default': 'user'
    },
    'AGGREGATE DICTIONARY': 'book',
    'AIRDROP DISCOVERABLE': 'search',
    'AIRDROP EMAILS': 'send',
    'AIRDROP NUMBERS': 'smartphone',
    'AIRDROP REAL NAMES': 'user',
    'AIRTAG DETECTION': 'alert-circle',
    'AIRTAGS': 'map-pin',
    'ALARMS': 'clock',
    'ALFA ROMEO CONTACTS': 'users',  # TODO: adjust artifact to share a category
    'ALFA ROMEO BLUETOOTH': 'bluetooth',
    'ALFA ROMEO SIRIUS DATA': 'settings',
    'ALLTRAILS': {
        'ALLTRAILS - TRAIL DETAILS': 'map',
        'ALLTRAILS - USER INFO': 'user',
    },
    'ANDROID SYSTEM INTELLIGENCE': {
        'SIMPLESTORAGE': 'loader',
        'default': 'user'
    },
    'APP CONDUIT': 'activity',
    'APP INTERACTION': 'bar-chart-2',
    'APP PERMISSIONS': 'key',
    'APP ROLES': 'tool',
    'APP UPDATES': 'codepen',
    'APPLE MAIL': 'mail',
    'APPLE NOTES': 'book-open',
    'APPLE PODCASTS': 'play-circle',
    'APPLE WALLET': {
        'CARDS': 'credit-card',
        'PASSES': 'send',
        'TRANSACTIONS': 'dollar-sign',
        'default': 'credit-card',
    },
    'APPLICATIONS': 'grid',
    'AUDIO UUIDS': 'smartphone',
    'BADOO': {
        'CHAT': 'message-circle',
        'CONNECTIONS': 'heart',
        'default': 'user'
    },
    'BASH HISTORY': 'terminal',
    'BIOME': 'eye',
    'BIOME APP INSTALL': 'eye',
    'BIOME BACKLIGHT': 'eye',
    'BIOME BATTERY PERC': 'eye',
    'BIOME BLUETOOTH': 'eye',
    'BIOME CARPLAY CONN': 'eye',
    'BIOME DEVICE PLUG': 'eye',
    'BIOME HARDWARE': 'eye',
    'BIOME IN FOCUS': 'eye',
    'BIOME INTENTS': 'eye',
    'BIOME LOCATION ACT': 'eye',
    'BIOME NOTES': 'eye',
    'BIOME NOTIFICATIONS PUB': 'eye',
    'BIOME NOW PLAYING': 'eye',
    'BIOME SAFARI': 'eye',
    'BIOME SYNC': 'smartphone',
    'BIOME TEXT INPUT': 'eye',
    'BIOME USER ACT META': 'eye',
    'BIOME WIFI': 'eye',
    'BITTORRENT': 'share',
    'BLUETOOTH': 'bluetooth',
    'BLUETOOTH CONNECTIONS': 'bluetooth',
    'BLUETOOTH_DEVICES': 'bluetooth',  # TODO: can this be combined?
    'BROWSER CACHE': {
        'CHROME BROWSER CACHE': 'chrome',
        'default': 'globe'
    },
    'BT REPORT': {
        'GPS DETAIL': 'map-pin',
        'BT CALL REPORT': 'bluetooth',
        'default': 'bluetooth',
    },
    'BUMBLE': {
        'BUMBLE - ACCOUNT DETAILS': 'user',
        'BUMBLE - MESSAGES': 'message-circle',
        'USER SETTINGS': 'user',
        'CHAT MESSAGES': 'message-circle',
        'MATCHES': 'smile',
    },
    'BURNER': {
        'NUMBER INFORMATION': 'user',
        'COMMUNICATION INFORMATION': 'message-circle',
        'default': 'user'
    },
    'CACHE DATA': 'box',
    'CALCULATOR LOCKER': 'lock',
    'CALENDAR': {
        'CALENDAR BIRTHDAYS': 'gift',
        'default': 'calendar',
    },
    'CALL HISTORY': {
        'CALL HISTORY': 'phone-call',
        'DELETED VOICEMAIL': 'mic-off',
        'VOICEMAIL': 'mic',
        'default': 'phone',
    },
    'CALL LOGS': 'phone',
    'CAST': 'cast',
    'CARPLAY': 'package',
    'CASH APP': 'credit-card',
    'CELLULAR WIRELESS': 'bar-chart',
    'CHASE RETURNS': 'paperclip',
    'CHATS': 'message-circle',
    'CHROMIUM': {
        'AUTOFILL': 'edit-3',
        'BOOKMARKS': 'bookmark',
        'DETECT INCIDENTAL PARTY STATE': 'skip-forward',
        'DOWNLOADS': 'download',
        'LOGIN': 'log-in',
        'MEDIA HISTORY': 'video',
        'NETWORK ACTION PREDICTOR': 'type',
        'OFFLINE PAGES': 'cloud-off',
        'SEARCH TERMS': 'search',
        'TOP SITES': 'list',
        'WEB VISITS': 'globe',
        'default': 'chrome',
        '_mode': 'search',
    },
    'CLIPBOARD': 'clipboard',
    'CLOUDKIT': {
        'NOTE SHARING': 'share-2',
        'PARTICIPANTS': 'user',
    },
    'COINBASE ARCHIVE': {
        '3RD': 'log-in',
        'CARD': 'credit-card',
        'PERSONAL': 'user',
        'SITE': 'activity',
        'TRANS': 'archive',
        'default': 'monitor',
    },
    'CONNECTED DEVICES': 'smartphone',
    'CONNECTED TO': 'zap',
    'CONTACTS': 'user',
    'CONTACT_LIST': 'users',  # TODO: can this use another category?
    'CONTROL CENTER': {
        'CONTROL CENTER - ACTIVE CONTROLS': 'sliders',
        'CONTROL CENTER - DISABLED CONTROLS': 'x-square',
        'CONTROL CENTER - USER TOGGLED CONTROLS': 'check-square',
    },
    'CORE ACCESSORIES': {
        'ACCESSORYD': 'zap',
        'USER EVENT AGENT': 'activity',
    },
    'COREDUET': {
        'AIRPLANE MODE': 'pause',
        'LOCK STATE': 'lock',
        'PLUGGED IN': 'battery-charging',
    },
    'DAHUA TECHNOLOGY (DMSS)': {
        'CHANNELS': 'film',
        'DEVICES': 'tablet',
        'INFO': 'settings',
        'NOTIFICATIONS': 'bell',
        'PIN': 'unlock',
        'SENSORS': 'smartphone',
        'USER CREATED MEDIA': 'video',
        '_mode': 'search',
    },
    'DATA USAGE': 'wifi',
    'DEVICE DATA': 'file',
    'DEVICE HEALTH SERVICES': {
        'BLUETOOTH': 'bluetooth',
        'BATTERY': 'battery-charging',
        'default': 'bar-chart-2',
        '_mode': 'search'
    },
    'DEVICE INFO': {
        'BUILD INFO': 'terminal',
        'IOS SYSTEM VERSION': 'git-commit',
        'PARTNER SETTINGS': 'settings',
        'SETTINGS_SECURE_': 'settings',
        'default': 'info',
        '_mode': 'search',
    },
    'DHCP': 'settings',
    'DIAGNOSTIC_DATA': 'thermometer',
    'DIGITAL WELLBEING': {
        'ACCOUNT DATA': 'user',
        'default': 'layers',
        '_mode': 'search',
    },
    'DIGITAL WELLBEING ACCOUNT': {
        'ACCOUNT DATA': 'user',
        'default': 'layers',
        '_mode': 'search',
    },
    'DISCORD': {
        'DISCORD ACCOUNT': 'user',
        'DISCORD MANIFEST': 'file-text',
        'DISCORD MESSAGES': 'message-square',
    },
    'DISCORD CHATS': 'message-square',
    'DISCORD RETURNS': 'message-square',
    'DOWNLOADS': 'download',
    'DRAFT NATIVE MESSAGES': 'message-circle',
    'DUCKDUCKGO': {
        'DUCKDUCKGO TAB THUMBNAILS': 'image',
        'default': 'layers'
    },
    'EMULATED STORAGE METADATA': 'database',
    'ENCRYPTING MEDIA APPS': 'lock',
    'ETC HOSTS': 'globe',
    'FACEBOOK MESSENGER': {
        'CALLS': 'phone-call',
        'CHAT': 'message-circle',
        'CONTACTS': 'users',
        'default': 'facebook',
        '_mode': 'search',
    },
    'FACEBOOK - INSTAGRAM RETURNS': 'facebook',
    'FILES APP': 'file-text',
    'FILES BY GOOGLE': 'file',
    'FIREBASE CLOUD MESSAGING': 'database',
    'FIREFOX': {
        'BOOKMARKS': 'bookmark',
        'COOKIES': 'info',
        'DOWNLOADS': 'download',
        'FORM HISTORY': 'edit-3',
        'PERMISSIONS': 'sliders',
        'RECENTLY CLOSED TABS': 'x-square',
        'SEARCH TERMS': 'search',
        'TOP SITES': 'list',
        'VISITS': 'globe',
        'WEB HISTORY': 'globe',
        'default': 'firefox',
        '_mode': 'search',
    },
    'FITBIT': 'watch',
    'GALLERY TRASH': 'image',
    'GARMIN': {
        'DEVICES': 'watch',
        'NOTIFICATIONS': 'bell',
        'SLEEP': 'moon',
        'WEATHER': 'sun',
        'default': 'activity',
        '_mode': 'search',
    },
    'GARMIN-API': {
        'ACTIVITY API': 'watch',
        'DAILIES API': 'calendar',
        'HEART RATE API': 'heart',
        'STEPS API': 'arrow-up-circle',
        'SLEEP API': 'moon',
        'STRESS API': 'frown',
        'POLYLINE API': 'map-pin',
        'default': 'activity',
        '_mode': 'search',
    },
    'GARMIN-CACHE': {
        'ACTIVITIES': 'watch',
        'CHARTS': 'activity',
        'DAILIES': 'calendar',
        'POLYLINE': 'map-pin',
        'RESPONSE': 'terminal',
        'SPO2': 'heart',
        'SLEEP': 'moon',
        'WEIGHT': 'bar-chart-2',
        'default': 'activity',
        '_mode': 'search',
    },
    'GARMIN-FILES': {
        'LOG': 'file-text',
        'PERSISTENT': 'code',
        '_mode': 'search',
    },
    'GARMIN-GCM': {
        'ACTIVITIES': 'watch',
        'JSON': 'code',
        '_mode': 'search',
    },
    'GARMIN-NOTIFICATIONS': 'message-square',
    'GARMIN-SHAREDPREFS': {
        'FACEBOOK': 'facebook',
        'USER': 'user',
        '_mode': 'search',
    },
    'GARMIN-SYNC': 'loader',
    'GEO LOCATION': 'map-pin',
    'GEOLOCATION': {
        'APPLICATIONS': 'grid',
        'MAP TILE CACHE': 'map',
        'MAPSSYNC': 'map',
        'PD PLACE CACHE': 'map-pin',
        'default': 'map-pin',
    },
    'GMAIL': {
        'GMAIL - LABEL DETAILS': 'mail',
        'GMAIL - OFFLINE SEARCH': 'search',
        'ACTIVE': 'at-sign',
        'APP EMAILS': 'at-sign',
        'DOWNLOAD REQUESTS': 'download-cloud',
        'LABEL DETAILS': 'mail',
        '_mode': 'search',
    },
    'GOOGLE CALL SCREEN': 'phone-incoming',
    'GOOGLE CHAT': {
        'GROUP INFORMATION': 'users',
        'MESSAGES': 'message-circle',
        'DRAFTS': 'edit-3',
        'USERS': 'users',
        'default': 'message-circle',
        '_mode': 'search',
    },
    'GOOGLE DRIVE': 'file',
    'GOOGLE DUO': {
        'GOOGLE DUO - CALL HISTORY': 'phone-call',
        'GOOGLE DUO - CLIPS': 'video',
        'GOOGLE DUO - CONTACTS': 'user',
        'CALL HISTORY': 'phone-call',
        'CONTACTS': 'users',
        'NOTES': 'edit-3',
        '_mode': 'search',
    },
    'GOOGLE FIT (GMS)': 'activity',
    'GOOGLE KEEP': 'list',
    'GBOARD KEYBOARD': {
        'CLIPBOARD': 'clipboard',
        '_mode': 'search',
    },
    'GOOGLE MAPS VOICE GUIDANCE': 'map',
    'GOOGLE MAPS TEMP VOICE GUIDANCE': 'map',
    'GOOGLE MESSAGES': 'message-circle',
    'GOOGLE NOW & QUICKSEARCH': 'search',
    'GOOGLE PHOTOS': {
        'LOCAL TRASH': 'trash-2',
        'BACKED UP FOLDER': 'refresh-cw',
        '_mode': 'search',
    },
    'GOOGLE PLAY': {
        'GOOGLE PLAY SEARCHES': 'search',
        'default': 'play',
        '_mode': 'search',
    },
    'GOOGLE RETURNS': {
        'GOOGLE RETURNS - ACTIVITIES': 'activity',
        'default': 'chrome'
    },
    'GOOGLE RETURNS MBOXES': 'mail',
    'GOOGLE RETURNS SUBSCRIBER INFO': 'user',
    'GOOGLE RETURNS PLAY USER ACT': 'smartphone',
    'GOOGLE RETURNS ANDROID DEVICE CONFIG': 'smartphone',
    'GOOGLE RETURNS MY ACTIVITY IMAGE SEARCH': 'search',
    'GOOGLE RETURNS MY ACTIVITY SEARCH': 'search',
    'GOOGLE RETURNS YOUTUBE SUBS INFO': 'search',
    'GOOGLE RETURNS ACCOUNT TARGET ASSOC. PHONE': 'target',
    'GOOGLE RETURNS ACCOUNT TARGET ASSOC. COOKIES': 'target',
    'GOOGLE RETURNS GOOGLE PLAY STORE DEVICES': 'tablet',
    'GOOGLE RETURNS GOOGLE PLAY INSTALLS': 'shield',
    'GOOGLE RETURNS GOOGLE PLAY LIBRARY': 'book-open',
    'GOOGLE RETURNS GOOGLE PLAY USER REVIEWS': 'book-open',
    'GOOGLE TAKEOUT ARCHIVE': {
        'CHROME WEB HISTORY': 'chrome',
        'CHROME ARC PACKAGES': 'package',
        'CHROME AUTOFILL': 'edit-3',
        'CHROME BOOKMARKS': 'star',
        'CHROME DEVICE INFO': 'chrome',
        'CHROME EXTENSIONS': 'tool',
        'CHROME OS SETTINGS': 'settings',
        'CHROME READING LIST': 'book',
        'CHROME SEARCH ENGINES': 'search',
        'CHROME OMNIBOX': 'search',
        'FITBIT ACCOUNT PROFILE': 'user',
        'FITBIT ACTIVITY GOALS': 'check-circle',
        'FITBIT COMPUTED TEMPERATURE': 'thermometer',
        'FITBIT OXYGEN SATURATION': 'droplet',
        'FITBIT SLEEP': 'moon',
        'FITBIT STRESS': 'activity',
        'FITBIT TRACKERS': 'watch',
        'GOOGLE ACCESS LOG ACTIVITIES': 'activity',
        'GOOGLE ACCESS LOG DEVICES': 'smartphone',
        'GOOGLE CHAT - MESSAGES': 'message-square',
        'GOOGLE FI - USER INFO RECORDS': 'phone',
        'GOOGLE FIT - DAILY ACTIVITY METRICS': 'trending-up',
        'GOOGLE LOCATION HISTORY - LOCATION HISTORY': 'map-pin',
        'GOOGLE PAY TRANSACTIONS': 'credit-card',
        'GOOGLE PLAY STORE DEVICES': 'smartphone',
        'GOOGLE PLAY STORE INSTALLS': 'box',
        'GOOGLE PLAY STORE LIBRARY': 'grid',
        'GOOGLE PLAY STORE PURCHASE HISTORY': 'shopping-cart',
        'GOOGLE PLAY STORE REVIEWS': 'edit-3',
        'GOOGLE PLAY STORE SUBSCRIPTIONS': 'refresh-cw',
        'GOOGLE PROFILE': 'user',
        'GOOGLE SEMANTIC LOCATION HISTORY - PLACE VISITS': 'map-pin',
        'GOOGLE SEMANTIC LOCATION HISTORY - ACTIVITY SEGMENTS': 'activity',
        'GOOGLE TASKS': 'check-circle',
        'MBOX': 'mail',
        'SAVED LINKS - DEFAULT LIST': 'list',
        'SAVED LINKS - FAVORITE IMAGES': 'image',
        'SAVED LINKS - FAVORITE PAGES': 'link-2',
        'SAVED LINKS - WANT TO GO': 'navigation-2',
        'YOUTUBE SUBSCRIPTIONS': 'youtube',
        'default': 'user'
    },
    'GOOGLE TAKEOUT SEMANTIC LOCATIONS BY MONTH': 'map-pin',
    'GOOGLE TASKS': 'list',
    'GPS_DATA': 'map-pin',
    'GROUPME': {
        'GROUP INFORMATION': 'users',
        'CHAT INFORMATION': 'message-circle',
        '_mode': 'search',
    },
    'HEALTH': {
        'DEFAULT': 'heart',
        'HEALTH - ACHIEVEMENTS': 'star',
        'HEALTH - HEADPHONE AUDIO LEVELS': 'headphones',
        'HEALTH - HEART RATE': 'activity',
        'HEALTH - RESTING HEART RATE': 'activity',
        'HEALTH - STEPS': 'activity',
        'HEALTH - WORKOUTS': 'activity',
    },
    'HIDEX': 'eye-off',
    'HIKVISION': {
        'CCTV ACTIVITY': 'activity',
        'CCTV CHANNELS': 'film',
        'CCTV INFO': 'settings',
        'USER CREATED MEDIA': 'video',
        '_mode': 'search',
    },
    'ICLOUD DOCUMENTS FOLDERS': 'book-open',
    'ICLOUD QUICK LOOK': 'file',
    'ICLOUD RETURNS': {
        'ICLOUD - ACCOUNT FEATURES': 'user',
        'default': 'cloud'
    },
    'ICLOUD SHARED ALBUMS': 'cloud',
    'IDENTIFIERS': 'file',
    'IMAGE MANAGER CACHE': 'image',
    'IMO': {
        'IMO - ACCOUNT ID': 'user',
        'IMO - MESSAGES': 'message-square',
    },
    'IMO HD CHAT': {
        'IMO HD CHAT - CONTACTS': 'user',
        'IMO HD CHAT - MESSAGES': 'message-circle',
    },
    'INSTAGRAM': {
        'INSTAGRAM THREADS': 'message-square',
        'INSTAGRAM THREADS CALLS': 'phone',
    },
    'INSTAGRAM ARCHIVE': {
        'INSTAGRAM ARCHIVE - ACCOUNT INFO': 'user',
        'INSTAGRAM ARCHIVE - PERSONAL INFO': 'user',
        'default': 'instagram'
    },
    'INSTALLED APPS': 'package',
    'INTENTS': 'command',
    'INTERACTIONC': {
        'ATTACHMENTS': 'paperclip',
        'CONTACTS': 'user',
    },
    'IOS ATXDATASTORE': 'database',
    'IOS BUILD': 'git-commit',
    'IOS BUILD (ITUNES BACKUP)': 'git-commit',
    'IOS SCREENS': 'maximize',
    'KEYBOARD': {
        'KEYBOARD APPLICATION USAGE': 'type',
        'KEYBOARD DYNAMIC LEXICON': 'type',
    },
    'KIK': {
        'KIK GROUP ADMINISTRATORS': 'user-plus',
        'KIK LOCAL ACCOUNT': 'user-check',
        'KIK MEDIA METADATA': 'file-plus',
        'KIK MESSAGES': 'message-square',
        'KIK PENDING UPLOADS': 'upload',
        'KIK USERS': 'user',
        'KIK USERS IN GROUPS': 'user',
    },
    'KIK RETURNS': {
        'KIK - PROFILE PIC': 'image',
        'default': 'file-text'
    },
    'KNOWLEDGEC': {
        'KNOWLEDGEC - BATTERY PERCENTAGE': 'battery',
        'KNOWLEDGEC DEVICE LOCKED': 'lock',
        'KNOWLEDGEC - MEDIA PLAYING': 'play-circle',
        'KNOWLEDGEC - DEVICE PLUGIN STATUS': 'battery-charging',
        'default': 'activity',
    },
    'LEAPP_REPORT': {
        'default': 'git-commit',
        '_mode': 'search',
    },
    'LIBRE TORRENT': 'download',
    'LINE': {
        'LINE - CONTACTS': 'user',
        'LINE - MESSAGES': 'message-square',
        'LINE - CALL LOGS': 'phone',
    },
    'LOCATION SERVICES CONFIGURATIONS': 'settings',
    'LOCATIONS': {
        'APPLE MAPS SEARCH HISTORY': 'search',
        'default': 'map-pin',
    },
    'MAP-MY-WALK': {
        'ACTIVITIES': 'map',
        'USER': 'user',
        '_mode': 'search',
    },
    'MASTODON': {
        'ACCOUNT DETAILS': 'user',
        'ACCOUNT SEARCHES': 'users',
        'HASHTAG SEARCHES': 'hash',
        'INSTANCE DETAILS': 'info',
        'NOTIFICATIONS': 'bell',
        'TIMELINE': 'activity',
        '_mode': 'search',
    },
    'MEDIA LIBRARY': 'play-circle',
    'MEDIA METADATA': 'file-plus',
    'MEDICAL ID': 'thermometer',
    'MEGA': 'message-circle',
    'METAMASK': {
        'BROWSER': 'globe',
        'CONTACTS': 'users',
        '_mode': 'search',
    },
    'MEWE': 'message-circle',
    'MICROSOFT RETURNS': 'target',
    'MICROSOFT TEAMS': {
        'TEAMS CALL LOGS': 'phone',
        'TEAMS CONTACT': 'users',
        'TEAMS MESSAGES': 'message-square',
        'TEAMS SHARED LOCATIONS': 'map-pin',
        'TEAMS USER': 'user',
    },
    'MICROSOFT TEAMS - LOGS': {
        'TEAMS LOCATIONS': 'map-pin',
        'TEAMS MOTION': 'move',
        'TEAMS POWER LOG': 'battery-charging',
        'TEAMS STATE CHANGE': 'truck',
        'TEAMS TIMEZONE': 'clock',
    },
    'MOBILE ACTIVATION LOGS': 'clipboard',
    'MOBILE BACKUP': 'save',
    'MOBILE CONTAINER MANAGER': 'save',
    'MOBILE INSTALLATION LOGS': 'clipboard',
    'MOBILE SOFTWARE UPDATE': 'refresh-cw',
    'MY FILES': {
        'MY FILES DB - CACHE MEDIA': 'image',
        '_mode': 'search',
    },
    'NETFLIX ARCHIVE': {
        'NETFLIX - BILLING HISTORY': 'credit-card',
        'NETFLIX - PROFILES': 'users',
        'NETFLIX - IP ADDRESS LOGIN': 'log-in',
        'NETFLIX - ACCOUNT DETAILS': 'users',
        'NETFLIX - MESSAGES SENT BY NETFLIX': 'mail',
        'NETFLIX - SEARCH HISTORY': 'search',
        'default': 'tv'
    },
    'NETWORK USAGE': {
        'APP_DATA': 'activity',
        'CONNECTIONS': 'bar-chart',
        'default': 'send',
        '_mode': 'search',
    },
    'NIKE-RUN': {
        'ACTIVITIES': 'watch',
        'ACTIVITY ROUTE': 'map-pin',
        'ACTIVITY MOMENTS': 'list',
        'NOTIFICATIONS': 'bell',
        '_mode': 'search',
    },
    'NOTES': 'file-text',
    'NOTIFICATIONS': 'bell',
    'NOW PLAYING': 'music',
    'OFFLINE PAGES': 'cloud-off',
    'PACKAGE PREDICTIONS': 'package',
    'PAS_DEBUG': {
        'SEND GPS CAN DATA': 'map-pin',
        'DEV LOC RESULTS': 'map-pin',
        'ROAD SPEED LIMITS': 'target',
        'ACCESS POINT LIST': 'wifi',
        'VEHICLE SPEED': 'trending-up',
        'TRANSMISSION STATUS': 'corner-up-right',
        'OUTSIDE TEMPERATURE': 'thermometer',
        'ODOMETER': 'plus-circle',
        'default': 'archive',
    },
    'PERMISSIONS': 'check',
    'PHONE BOOK DB': 'smartphone',
    'PHONE CONFIG': 'smartphone',
    'PHOTOS': {
        'MIGRATIONS': 'chevrons-up',
        'default': 'image',
    },
    'PIKPAK': 'cloud',
    'PINGER': {
        'PINGER - CDR': 'phone',
        'PINGER - DML': 'phone',
        'PINGER - IP': 'monitor',
        'PINGER - MESSAGES': 'message-square',
        'PINGER - ACCOUNT': 'user',
        'default': 'phone'
    },
    'PLAYGROUND VAULT': 'lock',
    'PODCAST ADDICT': 'music',
    'POWER EVENTS': {
        'POWER OFF RESET': 'power',
        'LAST BOOT TIME': 'power',
        'SHUTDOWN CHECKPOINTS': 'power',
        '_mode': 'search',
    },
    'POWERLOG': 'power',
    'POWERLOG BACKUPS': 'power',
    'PREFERENCES PLIST': 'file',
    'PRIVACY DASHBOARD': 'eye',
    'PROTON MAIL': 'mail',
    'PROTONMAIL': {
        'CONTACTS': 'users',
        'MESSAGES': 'inbox',
        '_mode': 'search',
    },
    'PROTONVPN': 'shield',
    'PUMA-TRAC': {
        'ACTIVITIES': 'watch',
        'USER': 'user',
        '_mode': 'search',
    },
    'RAR LAB PREFS': 'settings',
    'RCS CHATS': 'message-circle',
    'RECENT ACTIVITY': 'activity',
    'REDDIT RETURNS': 'chevrons-up',
    'REMINDERS': 'list',
    'ROUTINED': 'map',
    'RUNKEEPER': {
        'ACTIVITIES': 'watch',
        'USER': 'user',
        '_mode': 'search',
    },
    'SAFARI BROWSER': 'compass',
    'SAMSUNG SMARTTHINGS': 'bluetooth',
    'SAMSUNG WEATHER CLOCK': {
        'DAILY': 'sunrise',
        'HOURLY': 'thermometer',
        '_mode': 'search',
    },
    'SAMSUNG_CMH': 'disc',
    'SCREENTIME': 'monitor',
    'SCRIPT LOGS': 'archive',
    'SECRET CALCULATOR PHOTO ALBUM': 'image',
    'SETTINGS SERVICES': 'battery-charging',
    'SIM INFO': 'info',
    'SKOUT': {
        'SKOUT MESSAGES': 'message-circle',
        'SKOUT USERS': 'users',
    },
    'SKYPE': {
        'SKYPE - CALL LOGS': 'phone',
        'SKYPE - MESSAGES': 'message-square',
        'SKYPE - CONTACTS': 'user',
    },
    'SLACK': {
        'SLACK ATTACHMENTS': 'paperclip',
        'SLACK CHANNEL DATA': 'slack',
        'SLACK MESSAGES': 'message-square',
        'SLACK TEAM DATA': 'slack',
        'SLACK USER DATA': 'user',
        'SLACK WORKSPACE DATA': 'slack',
    },
    'SLOPES': {
        'SLOPES - ACTIONS': 'trending-down',
        'SLOPES - LIFT DETAILS': 'shuffle',
        'SLOPES - RESORT DETAILS': 'home',
    },
    'SMS & IMESSAGE': 'message-square',
    'SMS & MMS': 'message-square',
    'SNAPCHAT': 'bell',
    'SNAPCHAT ARCHIVE': 'camera',
    'SNAPCHAT RETURNS': 'camera',
    'SQLITE JOURNALING': 'book-open',
    'STRAVA': 'map',
    'TEAMS': {  # TODO: align I & A artifacts since theres a 'microsoft teams' also
        'TEAMS MESSAGES': 'message-circle',
        'TEAMS USERS': 'users',
        'TEAMS CALL LOG': 'phone',
        'TEAMS ACTIVITY FEED': 'at-sign',
        'TEAMS FILE INFO': 'file',
        'default': 'file-text',
    },
    'TANGO': 'message-square',
    'TELEGRAM': 'message-square',
    'TELEMATICS': {
        'GPS DETAIL': 'map-pin',
        'WDWSTATUS REPORT': 'map-pin',
        '_mode': 'search',
    },
    'TEXT INPUT MESSAGES': 'message-square',
    'TEXT NOW': {
        'TEXT NOW - CALL LOGS': 'phone',
        'TEXT NOW - MESSAGES': 'message-square',
        'TEXT NOW - CONTACTS': 'user',
    },
    'TIKTOK': {  # TODO: align I & A artifacts with each other
        'TIKTOK CONTACTS': 'user',
        'TIKTOK MESSAGES': 'message-square',
        'TIKTOK SEARCH': 'search',
        'TIKTOK - MESSAGES': 'message-square',
        'TIKTOK - CONTACTS': 'user',
    },
    'TIKTOK RETURNS': 'film',
    'TODOIST': {
        'ITEMS': 'list',
        'NOTES': 'file-text',
        'PROJECTS': 'folder',
        '_mode': 'search',
    },
    'TOR': 'globe',
    'TORRENT DATA': 'download',
    'TUSKY': {
        'TIMELINE': 'activity',
        'ACCOUNT': 'user',
        '_mode': 'search',
    },
    'TWITTER': 'twitter',
    'TWITTER RETURNS': 'twitter',
    'USAGE STATS': 'bar-chart-2',
    'USER DICTIONARY': 'book',
    'VEHICLE INFO': 'truck',
    'VENMO': 'dollar-sign',
    'VERIZON RDD ANALYTICS': {
        'VERIZON RDD - BATTERY HISTORY': 'power',
        'VERIZON RDD - WIFI DATA': 'wifi',
    },
    'VIBER': {
        'VIBER - CALL REMNANTS': 'phone-call',
        'VIBER - CHATS': 'message-square',
        'VIBER - CONTACTS': 'users',
        'VIBER - SETTINGS': 'settings',
        'VIBER - MESSAGES': 'message-square',
        'VIBER - CALL LOGS': 'phone',
    },
    'VIPPS': {
        'VIPPS CONTACTS': 'users',
        'default': 'dollar-sign',
    },
    'VLC': {
        'VLC MEDIA LIST': 'film',
        'VLC THUMBNAILS': 'image',
    },
    'VLC THUMBS': {
        'VLC MEDIA LIB': 'film',
        'VLC THUMBNAILS': 'image',
        'VLC THUMBNAIL DATA': 'image',
        'default': 'image',
    },
    'VOICE-RECORDINGS': 'mic',
    'VOICE-TRIGGERS': 'mic',
    'WAZE': 'navigation-2',
    'WHATSAPP': {  # TODO: I don't think search mode is required
        'WHATSAPP - CONTACTS': 'users',
        'WHATSAPP - MESSAGES': 'message-square',
        'WHATSAPP - ONE TO ONE MESSAGES': 'message-circle',
        'WHATSAPP - GROUP MESSAGES': 'message-circle',
        'WHATSAPP - CALL LOGS': 'phone',
        'WHATSAPP - GROUP DETAILS': 'users',
        'default': 'user',
        '_mode': 'search',
    },
    'WHATSAPP EXPORTED CHAT': 'message-circle',
    'WIFI CONNECTIONS': 'wifi',
    'WIFI KNOWN NETWORKS': 'wifi',
    'WIFI PROFILES': 'wifi',
    'WIPE & SETUP': {
        'FACTORY RESET': 'loader',
        'SUGGESTIONS.XML': 'loader',
        'SETUP_WIZARD_INFO.XML': 'loader',
        'APPOPS.XML': 'loader',
        'SAMSUNG WIPE HISTORY': 'trash-2',
        'SAMSUNG WIPE RECOVERY HISTORY LOG': 'trash-2',
        'default': 'loader',
    },
}

# function that can be run against the list to sort and output to console
def sort_and_print_mappings():
    sorted_keys = sorted(icon_mappings.keys(), key=lambda x: x.lower())
    sorted_dict = {key: icon_mappings[key] for key in sorted_keys}

    print("{")
    for category, mappings in sorted_dict.items():
        if isinstance(mappings, dict):
            print(f"    '{category}': {{")
            # Sort the artifacts, with 'default' and '_mode' at the end
            sorted_artifacts = sorted(
                [(k, v) for k, v in mappings.items() if k not in ['default', '_mode']],
                key=lambda x: x[0]
            )
            # Append 'default' and '_mode' at the end if they exist
            if 'default' in mappings:
                sorted_artifacts.append(('default', mappings['default']))
            if '_mode' in mappings:
                sorted_artifacts.append(('_mode', mappings['_mode']))
            for artifact, icon in sorted_artifacts:
                print(f"        '{artifact}': '{icon}',")
            print("    },")
        else:
            print(f"    '{category}': '{mappings}',")
    print("}")


if __name__ == '__main__':
    # Call the function to print the sorted mappings to the console
    sort_and_print_mappings()

def get_icon_name(category, artifact):
    """
    Returns the icon name from the feathericons collection. To add an icon type for
    an artifact, select one of the types from ones listed @ feathericons.com
    If no icon is available, the alert triangle is returned as default icon.
    """
    category = category.upper()
    artifact = artifact.upper()

    category_match = icon_mappings.get(category)

    if category_match:
        if isinstance(category_match, str):
            return category_match
        elif isinstance(category_match, dict):
            artifact_match = category_match.get(artifact)
            if artifact_match:
                return artifact_match
            else:
                if category_match.get('_mode') == 'search':
                    for key, value in category_match.items():
                        if artifact.find(key) >= 0:
                            return value
                    art_default = category_match.get('default')
                    if art_default:
                        return art_default
                art_default = category_match.get('default')
                if art_default:
                    return art_default
    else:
        # search_set = get_search_mode_categories()
        for r in search_set:
            for record in search_set:
                category_key, category_mapping = list(record.items())[0]
                if category.find(category_key) >= 0:
                    for key, value in category_mapping.items():
                        if artifact.find(key) >= 0:
                            return value
                    art_default = category_mapping.get('default')
                    if art_default:
                        return art_default

    return 'alert-triangle'


def get_search_mode_categories():
    search_mode_categories = []
    for category, mappings in icon_mappings.items():
        if isinstance(mappings, dict) and mappings.get('_mode') == 'search':
            search_mode_categories.append({category: mappings})
    return search_mode_categories
# get them populated
search_set = get_search_mode_categories()


def generate_report(reportfolderbase, time_in_secs, time_HMS, extraction_type, image_input_path, casedata):
    control = None
    side_heading = \
        """
        <h6 class="sidebar-heading justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
            {0}
        </h6>
        """
    list_item = \
        """
        <li class="nav-item">
            <a class="nav-link {0}" href="{1}">
                <span data-feather="{2}"></span> {3}
            </a>
        </li>
        """
    # Populate the sidebar dynamic data (depends on data/files generated by parsers)
    # Start with the 'saved reports' (home) page link and then append elements
    nav_list_data = side_heading.format('Saved Reports') + list_item.format('', 'index.html', 'home', 'Report Home')
    # Get all files
    side_list = OrderedDict() # { Category1 : [path1, path2, ..], Cat2:[..] } Dictionary containing paths as values, key=category

    for root, dirs, files in sorted(os.walk(reportfolderbase)):
        files = sorted(files)
        for file in files:
            if file.endswith(".temphtml"):
                fullpath = (os.path.join(root, file))
                head, tail = os.path.split(fullpath)
                p = pathlib.Path(fullpath)
                SectionHeader = (p.parts[-2])
                if SectionHeader == '_elements':
                    pass
                else:
                    if control == SectionHeader:
                        side_list[SectionHeader].append(fullpath)
                        icon = get_icon_name(SectionHeader, tail.replace(".temphtml", ""))
                        nav_list_data += list_item.format('', tail.replace(".temphtml", ".html"), icon,
                                                          tail.replace(".temphtml", ""))
                    else:
                        control = SectionHeader
                        side_list[SectionHeader] = []
                        side_list[SectionHeader].append(fullpath)
                        nav_list_data += side_heading.format(SectionHeader)
                        icon = get_icon_name(SectionHeader, tail.replace(".temphtml", ""))
                        nav_list_data += list_item.format('', tail.replace(".temphtml", ".html"), icon,
                                                          tail.replace(".temphtml", ""))

    # Now that we have all the file paths, start writing the files

    for category, path_list in side_list.items():
        for path in path_list:
            old_filename = os.path.basename(path)
            filename = old_filename.replace(".temphtml", ".html")
            # search for it in nav_list_data, then mark that one as 'active' tab
            active_nav_list_data = mark_item_active(nav_list_data, filename) + nav_bar_script
            artifact_data = get_file_content(path)

            # Now write out entire html page for artifact
            f = open(os.path.join(reportfolderbase, filename), 'w', encoding='utf8')
            artifact_data = insert_sidebar_code(artifact_data, active_nav_list_data, path)
            f.write(artifact_data)
            f.close()

            # Now delete .temphtml
            os.remove(path)
            # If dir is empty, delete it
            try:
                os.rmdir(os.path.dirname(path))
            except OSError:
                pass # Perhaps it was not empty!

    # Create index.html's page content
    create_index_html(reportfolderbase, time_in_secs, time_HMS, extraction_type, image_input_path, nav_list_data, casedata)
    elements_folder = os.path.join(reportfolderbase, '_elements')
    os.mkdir(elements_folder)
    __location__ = os.path.dirname(os.path.abspath(__file__))

    def copy_no_perm(src, dst, *, follow_symlinks=True):
        if not os.path.isdir(dst):
            shutil.copyfile(src, dst)
        return dst

    try:
        shutil.copyfile(os.path.join(__location__, "logo.jpg"), os.path.join(elements_folder, "logo.jpg"))
        shutil.copyfile(os.path.join(__location__, "dashboard.css"), os.path.join(elements_folder, "dashboard.css"))
        shutil.copyfile(os.path.join(__location__, "feather.min.js"), os.path.join(elements_folder, "feather.min.js"))
        shutil.copyfile(os.path.join(__location__, "dark-mode.css"), os.path.join(elements_folder, "dark-mode.css"))
        shutil.copyfile(os.path.join(__location__, "dark-mode-switch.js"),
                        os.path.join(elements_folder, "dark-mode-switch.js"))
        shutil.copyfile(os.path.join(__location__, "chats.css"), os.path.join(elements_folder, "chats.css"))
        shutil.copytree(os.path.join(__location__, "MDB-Free_4.13.0"), os.path.join(elements_folder, 'MDB-Free_4.13.0'),
                        copy_function=copy_no_perm)
        
        
    except shutil.Error:
        print("shutil reported an error. Maybe due to recursive directory copying.")
        if os.path.exists(os.path.join(elements_folder, 'MDB-Free_4.13.0')):
            print("_elements folder seems fine. Probably nothing to worry about")


def get_file_content(path):
    f = open(path, 'r', encoding='utf8')
    data = f.read()
    f.close()
    return data

def create_index_html(reportfolderbase, time_in_secs, time_HMS, extraction_type, image_input_path, nav_list_data, casedata):
    '''Write out the index.html page to the report folder'''
    content = '<br />'
    content += """
                   <div class="card bg-white" style="padding: 20px;">
                   <h2 class="card-title">Case Information</h2>
               """  # CARD start

    case_list = [
        ['Extraction location', image_input_path],
        ['Extraction type', extraction_type],
        ['Report directory', reportfolderbase],
        ['Processing time', f'{time_HMS} (Total {time_in_secs} seconds)']
    ]
    
    if len(casedata) > 0:
        for key, value in casedata.items():
            case_list.append([key, value])
    
    tab1_content = generate_key_val_table_without_headings('', case_list) + \
        """
            <p class="note note-primary mb-4">
            All dates and times are in UTC unless noted otherwise!
            </p>
        """

    # Get script run log (this will be tab2)
    devinfo_files_path = os.path.join(reportfolderbase, 'Script Logs', 'DeviceInfo.html')
    tab2_content = get_file_content(devinfo_files_path)

    # Get script run log (this will be tab3)
    script_log_path = os.path.join(reportfolderbase, 'Script Logs', 'Screen Output.html')
    tab3_content = get_file_content(script_log_path)

    # Get processed files list (this will be tab3)
    processed_files_path = os.path.join(reportfolderbase, 'Script Logs', 'ProcessedFilesLog.html')
    tab4_content = get_file_content(processed_files_path)

    content += tabs_code.format(tab1_content, tab2_content, tab3_content, tab4_content)

    content += '</div>'  # CARD end

    authors_data = generate_authors_table_code(aleapp_contributors)
    credits_code = credits_block.format(authors_data)

    # WRITE INDEX.HTML LAST
    filename = 'index.html'
    page_title = 'iLEAPP Report'
    body_heading = 'iOS Logs Events And Protobuf Parser'
    body_description = 'iLEAPP is an open source project that aims to parse every known iOS artifact for the purpose of forensic analysis.'
    active_nav_list_data = mark_item_active(nav_list_data, filename) + nav_bar_script

    f = open(os.path.join(reportfolderbase, filename), 'w', encoding='utf8')
    f.write(page_header.format(page_title))
    f.write(body_start.format(f"iLEAPP {aleapp_version}"))
    f.write(body_sidebar_setup + active_nav_list_data + body_sidebar_trailer)
    f.write(body_main_header + body_main_data_title.format(body_heading, body_description))
    f.write(content)
    f.write(thank_you_note)
    f.write(credits_code)
    f.write(body_main_trailer + body_end + nav_bar_script_footer + page_footer)
    f.close()

def generate_authors_table_code(aleapp_contributors):
    authors_data = ''
    for author_name, blog, tweet_handle, git in aleapp_contributors:
        author_data = ''
        if blog:
            author_data += f'<a href="{blog}" target="_blank">{blog_icon}</a> &nbsp;\n'
        else:
            author_data += f'{blank_icon} &nbsp;\n'
        if tweet_handle:
            author_data += f'<a href="https://twitter.com/{tweet_handle}" target="_blank">{twitter_icon}</a> &nbsp;\n'
        else:
            author_data += f'{blank_icon} &nbsp;\n'
        if git:
            author_data += f'<a href="{git}" target="_blank">{github_icon}</a>\n'
        else:
            author_data += f'{blank_icon}'

        authors_data += individual_contributor.format(author_name, author_data)
    return authors_data

def generate_key_val_table_without_headings(title, data_list, html_escape=True, width="70%"):
    '''Returns the html code for a key-value table (2 cols) without col names'''
    code = ''
    if title:
        code += f'<h2>{title}</h2>'
    table_header_code = \
        """
        <div class="table-responsive">
            <table class="table table-bordered table-hover table-sm" width={}>
                <tbody>
        """
    table_footer_code = \
        """
                </tbody>
            </table>
        </div>
        """
    code += table_header_code.format(width)

    # Add the rows
    if html_escape:
        for row in data_list:
            code += '<tr>' + ''.join( ('<td>{}</td>'.format(html.escape(str(x))) for x in row) ) + '</tr>'
    else:
        for row in data_list:
            code += '<tr>' + ''.join( ('<td>{}</td>'.format(str(x)) for x in row) ) + '</tr>'

    # Add footer
    code += table_footer_code

    return code

def insert_sidebar_code(data, sidebar_code, filename):
    pos = data.find(body_sidebar_dynamic_data_placeholder)
    if pos < 0:
        logfunc(f'Error, could not find {body_sidebar_dynamic_data_placeholder} in file {filename}')
        return data
    else:
        ret = data[0: pos] + sidebar_code + data[pos + len(body_sidebar_dynamic_data_placeholder):]
        return ret

def mark_item_active(data, itemname):
    '''Finds itemname in data, then marks that node as active. Return value is changed data'''
    pos = data.find(f'" href="{itemname}"')
    if pos < 0:
        logfunc(f'Error, could not find {itemname} in {data}')
        return data
    else:
        ret = data[0: pos] + " active" + data[pos:]
        return ret
    
