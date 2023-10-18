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
    'ACCOUNT': {
        'AUTH': 'key',
        'default': 'user',
        '_mode': 'search',
    },
    'ADDRESS BOOK': 'book-open',
    'AGGREGATE DICTIONARY': 'book',
    'AIRTAGS': 'map-pin',
    'ALARMS': 'clock',
    'ALLTRAILS': {
        'ALLTRAILS - TRAIL DETAILS': 'map',
        'ALLTRAILS - USER INFO': 'user',
    },
    'APP CONDUIT': 'activity',
    'APP PERMISSIONS': 'key',
    'APP UPDATES': 'codepen',
    'APPLE MAIL': 'mail',
    'APPLE PODCASTS': 'play-circle',
    'APPLE WALLET': {
        'CARDS': 'credit-card',
        'PASSES': 'send',
        'TRANSACTIONS': 'dollar-sign',
        'default': 'credit-card',
    },
    'APPLICATIONS': 'grid',
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
    'BUMBLE': {
        'BUMBLE - ACCOUNT DETAILS': 'user',
        'BUMBLE - MESSAGES': 'message-circle',
    },
    'CACHE DATA': 'box',
    'CALENDAR': 'calendar',
    'CALL HISTORY': {
        'CALL HISTORY': 'phone-call',
        'DELETED VOICEMAIL': 'mic-off',
        'VOICEMAIL': 'mic',
    },
    'CARPLAY': 'package',
    'CASH APP': 'credit-card',
    'CELLULAR WIRELESS': 'bar-chart',
    'CHROMIUM': {
        'AUTOFILL': 'edit-3',
        'BOOKMARKS': 'bookmark',
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
    'CLOUDKIT': {
        'NOTE SHARING': 'share-2',
        'PARTICIPANTS': 'user',
    },
    'CONNECTED TO': 'zap',
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
    'DEVICE INFO': {
        'BUILD INFO': 'terminal',
        'DEFAULT': 'info',
        'IOS SYSTEM VERSION': 'git-commit',
        'PARTNER SETTINGS': 'settings',
        'SETTINGS_SECURE_': 'settings',
        '_mode': 'search',
    },
    'DHCP': 'settings',
    'DISCORD': {
        'DISCORD ACCOUNT': 'user',
        'DISCORD MANIFEST': 'file-text',
        'DISCORD MESSAGES': 'message-square',
    },
    'DRAFT NATIVE MESSAGES': 'message-circle',
    'FACEBOOK MESSENGER': 'facebook',
    'FILES APP': 'file-text',
    'GEOLOCATION': {
        'APPLICATIONS': 'grid',
        'DEFAULT': 'map-pin',
        'MAP TILE CACHE': 'map',
        'MAPSSYNC': 'map',
        'PD PLACE CACHE': 'map-pin',
    },
    'GMAIL': {
        'GMAIL - LABEL DETAILS': 'mail',
        'GMAIL - OFFLINE SEARCH': 'search',
    },
    'GOOGLE CHAT': 'message-square',
    'GOOGLE DUO': {
        'GOOGLE DUO - CALL HISTORY': 'phone-call',
        'GOOGLE DUO - CLIPS': 'video',
        'GOOGLE DUO - CONTACTS': 'user',
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
    'HIKVISION': {
        'CCTV ACTIVITY': 'activity',
        'CCTV CHANNELS': 'film',
        'CCTV INFO': 'settings',
        'USER CREATED MEDIA': 'video',
        '_mode': 'search',
    },
    'ICLOUD QUICK LOOK': 'file',
    'ICLOUD RETURNS': 'cloud',
    'ICLOUD SHARED ALBUMS': 'cloud',
    'IDENTIFIERS': 'file',
    'IMO HD CHAT': {
        'IMO HD CHAT - CONTACTS': 'user',
        'IMO HD CHAT - MESSAGES': 'message-circle',
    },
    'INSTAGRAM': {
        'INSTAGRAM THREADS': 'message-square',
        'INSTAGRAM THREADS CALLS': 'phone',
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
    'KNOWLEDGEC': {
        'DEFAULT': 'activity',
        'KNOWLEDGEC BATTERY LEVEL': 'battery',
        'KNOWLEDGEC DEVICE LOCKED': 'lock',
        'KNOWLEDGEC PLUGGED IN': 'battery-charging',
    },
    'LEAPP_REPORT': {
        'DEFAULT': 'git-commit',
        '_mode': 'search',
    },
    'LOCATION SERVICES CONFIGURATIONS': 'settings',
    'LOCATIONS': {
        'APPLE MAPS SEARCH HISTORY': 'search',
        'DEFAULT': 'map-pin',
    },
    'MEDIA LIBRARY': 'play-circle',
    'MEDIA METADATA': 'file-plus',
    'MEDICAL ID': 'thermometer',
    'METAMASK': {
        'BROWSER': 'globe',
        'CONTACTS': 'users',
        '_mode': 'search',
    },
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
    'NETWORK USAGE': {
        'APP_DATA': 'activity',
        'CONNECTIONS': 'bar-chart',
        'default': 'send',
        '_mode': 'search',
    },
    'NOTES': 'file-text',
    'NOTIFICATIONS': 'bell',
    'OFFLINE PAGES': 'cloud-off',
    'PHOTOS': {
        'DEFAULT': 'image',
        'MIGRATIONS': 'chevrons-up',
    },
    'POWERLOG': 'power',
    'POWERLOG BACKUPS': 'power',
    'PREFERENCES PLIST': 'file',
    'PROTON MAIL': 'mail',
    'RECENT ACTIVITY': 'activity',
    'REMINDERS': 'list',
    'ROUTINED': 'map',
    'SAFARI BROWSER': 'compass',
    'SCREENTIME': 'monitor',
    'SCRIPT LOGS': 'archive',
    'SECRET CALCULATOR PHOTO ALBUM': 'image',
    'SIM INFO': 'info',
    'SLACK': {
        'SLACK ATTACHMENTS': 'paperclip',
        'SLACK CHANNEL DATA': 'slack',
        'SLACK MESSAGES': 'message-square',
        'SLACK TEAM DATA': 'slack',
        'SLACK USER DATA': 'user',
        'SLACK WORKSPACE DATA': 'slack',
    },
    'SMS & IMESSAGE': 'message-square',
    'SQLITE JOURNALING': 'book-open',
    'TELEGRAM': 'message-square',
    'TEXT INPUT MESSAGES': 'message-square',
    'TIKTOK': {
        'TIKTOK CONTACTS': 'user',
        'TIKTOK MESSAGES': 'message-square',
        'TIKTOK SEARCH': 'search',
    },
    'USER DICTIONARY': 'book',
    'VENMO': 'dollar-sign',
    'VIBER': {
        'VIBER - CALL REMNANTS': 'phone-call',
        'VIBER - CHATS': 'message-square',
        'VIBER - CONTACTS': 'users',
        'VIBER - SETTINGS': 'settings',
    },
    'VIPPS': {
        'DEFAULT': 'dollar-sign',
        'VIPPS CONTACTS': 'users',
    },
    'VOICE-RECORDINGS': 'mic',
    'VOICE-TRIGGERS': 'mic',
    'WHATSAPP': {
        'WHATSAPP - CONTACTS': 'users',
        'WHATSAPP - MESSAGES': 'message-square',
    },
    'WIFI CONNECTIONS': 'wifi',
    'WIFI KNOWN NETWORKS': 'wifi',
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


def get_metamask_icon(artifact):
    if 'BROWSER' in artifact:
        return 'globe'
    elif 'CONTACTS' in artifact:
        return 'users'
    else:
        return 'dollar-sign'


def get_network_usage_icon(artifact):
    if 'APP DATA' in artifact:
        return 'activity'
    elif 'CONNECTIONS' in artifact:
        return 'bar-chart'


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
    
