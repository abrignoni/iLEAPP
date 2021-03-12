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


def get_icon_name(category, artifact):
    ''' Returns the icon name from the feathericons collection. To add an icon type for 
        an artifact, select one of the types from ones listed @ feathericons.com
        If no icon is available, the alert triangle is returned as default icon.
    '''
    category = category.upper()
    artifact = artifact.upper()
    icon = 'alert-triangle'  # default (if not defined!)

    ## Please keep list below SORTED by category

    if category.find('ACCOUNT') >= 0:
        if artifact.find('AUTH') >= 0:
            icon = 'key'
        else:
            icon = 'user'
    elif category == 'ADDRESS BOOK':
        icon = 'book-open'
    elif category == 'ALARMS':
        icon = 'clock'
    elif category == 'APPLE WALLET':
        if artifact == 'TRANSACTIONS':
            icon = 'dollar-sign'
        if artifact == 'CARDS':
            icon = 'credit-card'
        if artifact == 'PASSES':
            icon = 'send'
    elif category == 'APP CONDUIT':
        icon = 'activity'
    elif category == 'APP PERMISSIONS':
        icon = 'key'
    elif category == 'APP UPDATES':
        icon = 'codepen'
    elif category == 'APPLICATIONS':
        icon = 'grid'
    elif category == 'AGGREGATE DICTIONARY':
        icon = 'book'
    elif category == 'BLUETOOTH':
        icon = 'bluetooth'
    elif category == 'CALENDAR':
        icon = 'calendar'
    elif category == 'CALL LOGS':
        icon = 'phone'
    elif category == 'CELLULAR WIRELESS':
        icon = 'bar-chart'
    elif category == 'CLOUDKIT':
        if artifact == 'PARTICIPANTS':
            icon = 'user'
        elif artifact == 'NOTE SHARING':
            icon = 'share-2'
    elif category == 'CONNECTED TO':
        icon = 'zap'
    elif category == 'COREDUET':
        if artifact == 'AIRPLANE MODE':
            icon = 'pause'
        if artifact == 'LOCK STATE':
            icon = 'lock'
        if artifact == 'PLUGGED IN':
            icon = 'battery-charging'
    elif category == 'DATA USAGE':
        icon = 'wifi'
    elif category == 'DEVICE INFO':
        if artifact == 'BUILD INFO':
            icon = 'terminal'
        elif artifact == 'IOS SYSTEM VERSION':
            icon = 'git-commit'
        elif artifact == 'PARTNER SETTINGS':
            icon = 'settings'
        elif artifact.find('SETTINGS_SECURE_') >= 0:
            icon = 'settings'
        else:
            icon = 'info'
    elif category == 'DHCP':
        icon = 'settings'
    elif category == 'DISCORD':
        if artifact == 'DISCORD MESSAGES':
            icon = 'message-square'
        if artifact == 'DISCORD ACCOUNT':
            icon = 'user'
        if artifact == 'DISCORD MANIFEST':
            icon = 'file-text'
    elif category == 'FACEBOOK MESSENGER':
        icon = 'facebook'
    elif category == 'FILES APP':
        icon = 'file-text'
    elif category == 'GEOLOCATION':
        if artifact == 'APPLICATIONS':
            icon = 'grid'
        elif artifact == 'MAP TILE CACHE':
            icon = 'map'
        elif artifact == 'PD PLACE CACHE':
            icon = 'map-pin'
    elif category == 'HEALTH DATA':
        icon = 'heart'
    elif category == 'ICLOUD SHARED ALBUMS':
        icon = 'cloud'
    elif category == 'IMO HD CHAT':
        if artifact == 'IMO HD CHAT - MESSAGES':
            icon = 'message-circle'
        if artifact == 'IMO HD CHAT - CONTACTS':
            icon = 'user'
    elif category == 'INSTALLED APPS':
        icon = 'package'
    elif category == 'INTERACTIONC':
        if artifact == 'CONTACTS':
            icon = 'user'
        elif artifact == 'ATTACHMENTS':
            icon = 'paperclip'
    elif category == 'IOS BUILD':
        icon = 'git-commit'
    elif category == 'IOS MAIL':
        icon = 'mail'
    elif category == 'IOS SCREENS':
        icon = 'maximize'
    elif category == 'KEYBOARD':
        if artifact == 'KEYBOARD DYNAMIC LEXICON':
            icon = 'type'
        elif artifact == 'KEYBOARD APPLICATION USAGE':
            icon = 'type'
    elif category == 'KIK':
        if artifact == 'KIK MESSAGES':
            icon = 'message-square'
    elif category == 'KNOWLEDGEC':
        if artifact == 'KNOWLEDGEC DEVICE LOCKED':
            icon = 'lock'
        elif artifact == 'KNOWLEDGEC PLUGGED IN':
            icon = 'battery-charging'
        elif artifact == 'KNOWLEDGEC BATTERY LEVEL':
            icon = 'battery'
        else:
            icon = 'activity'
    elif category == 'LOCATIONS':
        if artifact == 'APPLE MAPS SEARCH HISTORY':
            icon = 'search'
        else:
            icon = 'map-pin'
    elif category == 'MEDIA METADATA':
        icon = 'file-plus'
    elif category == 'MEDICAL ID':
        icon = 'thermometer'
    elif category == 'MOBILE ACTIVATION LOGS':
        icon = 'clipboard'
    elif category == 'MOBILE BACKUP':
        icon = 'save'
    elif category == 'MOBILE CONTAINER MANAGER':
        icon = 'save'
    elif category == 'MOBILE INSTALLATION LOGS':
        icon = 'clipboard'
    elif category == 'MEDIA LIBRARY':
        icon = 'play-circle'
    elif category == 'NOTES':
        icon = 'file-text'
    elif category == 'ICLOUD RETURNS':
        icon = 'cloud'
    elif category == 'ICLOUD SHARED ALBUMS':
        icon = 'cloud'
    elif category == 'DISCORD':
        if artifact == 'DISCORD MESSAGES':
            icon = 'message-square'
        if artifact == 'DISCORD ACCOUNT':
            icon = 'user'
        if artifact == 'DISCORD MANIFEST':
            icon = 'file-text'
    elif category == 'KIK':
        if artifact == 'KIK MESSAGES':
            icon = 'message-square'
    elif category == 'WIFI CONNECTIONS':
        icon = 'wifi'
    elif category == 'GEOLOCATION':
        if artifact == 'APPLICATIONS':
            icon = 'grid'
        elif artifact == 'MAP TILE CACHE':
            icon = 'map'
        elif artifact == 'PD PLACE CACHE':
            icon = 'map-pin'
    elif category == 'CLOUDKIT':
        if artifact == 'PARTICIPANTS':
            icon = 'user'
        elif artifact == 'NOTE SHARING':
            icon = 'share-2'
    elif category == 'APP PERMISSIONS':
        icon = 'key'
    elif category == 'NOTIFICATIONS':
        icon = 'bell'
    elif category == 'PHOTOS':
        icon = 'image'
    elif category == 'POWERLOG':
        icon = 'power'
    elif category == 'POWERLOG BACKUPS':
        icon = 'power'
    elif category == 'RECENT ACTIVITY':
        icon = 'activity'
    elif category == 'REMINDERS':
        icon = 'list'
    elif category == 'ROUTINED':
        icon = 'map'
    elif category == 'SAFARI BROWSER':
        icon = 'compass'
    elif category == 'SCREENTIME':
        icon = 'monitor'
    elif category == 'SCRIPT LOGS':
        icon = 'archive'
    elif category == 'SMS & IMESSAGE':
        icon = 'message-square'
    elif category == 'SQLITE JOURNALING':
        icon = 'book-open'
    elif category == 'USER DICTIONARY':
        icon = 'book'
    elif category == 'VOICE-RECORDINGS':
        icon = 'mic'
    elif category == 'VOICE-TRIGGERS':
        icon = 'mic'
    elif category == 'WIFI CONNECTIONS':
        icon = 'wifi'
    elif category == 'ICLOUD QUICK LOOK':
        icon = 'file'
    elif category == 'TIKTOK':
        if artifact == 'TIKTOK MESSAGES':
            icon = 'message-square'
        if artifact == 'TIKTOK CONTACTS':
            icon = 'user'
    elif category == 'SLACK':
        if artifact == 'SLACK MESSAGES':
            icon = 'message-square'
        if artifact == 'SLACK USER DATA':
            icon = 'user'
        if artifact == 'SLACK ATTACHMENTS':
            icon = 'paperclip'
        if artifact == 'SLACK WORKSPACE DATA':
            icon = 'slack'
        if artifact == 'SLACK TEAM DATA':
            icon = 'slack'
        if artifact == 'SLACK CHANNEL DATA':
            icon = 'slack'
    elif category == 'MICROSOFT TEAMS - LOGS':
        if artifact == 'TEAMS LOCATIONS':
            icon = 'map-pin'
        if artifact == 'TEAMS MOTION':
            icon = 'move'
        if artifact == 'TEAMS STATE CHANGE':
            icon = 'truck'
        if artifact == 'TEAMS POWER LOG':
            icon = 'battery-charging'
        if artifact == 'TEAMS TIMEZONE':
            icon = 'clock'
    elif category == 'MICROSOFT TEAMS':
        if artifact == 'TEAMS MESSAGES':
            icon = 'message-square'
        if artifact == 'TEAMS CONTACT':
            icon = 'users'
        if artifact == 'TEAMS USER':
            icon = 'user'
        if artifact == 'TEAMS CALL LOGS':
            icon = 'phone'
        if artifact == 'TEAMS SHARED LOCATIONS':
            icon = 'map-pin'
    elif category == 'INSTAGRAM':
        if artifact == 'INSTAGRAM THREADS':
            icon = 'message-square'
        if artifact == 'INSTAGRAM THREADS CALLS':
            icon = 'phone'
            
    return icon


def generate_report(reportfolderbase, time_in_secs, time_HMS, extraction_type, image_input_path):
    control = None
    side_heading = \
        """<h6 class="sidebar-heading justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
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
    side_list = OrderedDict()  # { Category1 : [path1, path2, ..], Cat2:[..] } Dictionary containing paths as values, key=category

    for root, dirs, files in sorted(os.walk(reportfolderbase)):
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
                pass  # Perhaps it was not empty!

    # Create index.html's page content
    create_index_html(reportfolderbase, time_in_secs, time_HMS, extraction_type, image_input_path, nav_list_data)
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


def create_index_html(reportfolderbase, time_in_secs, time_HMS, extraction_type, image_input_path, nav_list_data):
    '''Write out the index.html page to the report folder'''
    content = '<br />'
    content += """
    <div class="card bg-white" style="padding: 20px;">
        <h2 class="card-title">Case Information</h2>
    """  # CARD start

    case_list = [['Extraction location', image_input_path],
                 ['Extraction type', extraction_type],
                 ['Report directory', reportfolderbase],
                 ['Processing time', f'{time_HMS} (Total {time_in_secs} seconds)']]

    tab1_content = generate_key_val_table_without_headings('', case_list) + \
                   """         <p class="note note-primary mb-4">
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
            code += '<tr>' + ''.join(('<td>{}</td>'.format(html.escape(str(x))) for x in row)) + '</tr>'
    else:
        for row in data_list:
            code += '<tr>' + ''.join(('<td>{}</td>'.format(str(x)) for x in row)) + '</tr>'

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
    
    
