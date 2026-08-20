__artifacts_v2__ = {
    "tinderMessages": {
        "name": "Tinder - Messages",
        "description": "Messages from the ZMESSAGE table of the Tinder Core Data store "
                       "Tinder2.sqlite, with the sender, the match and the media fields",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Tinder",
        "notes": "Timestamps are Core Data (Cocoa) seconds and are converted to UTC. ZCREATED "
                 "is reported as the message time and ZCLIENTCREATED alongside it; the two "
                 "differ, and nothing in the extraction documents what each records.\n"
                 "Sender is ZFROMUSERID, resolved to a first name through the ZUSER table where "
                 "a matching row exists. Messages the app itself sends into the user's inbox "
                 "carry the literal sender id com.tinder.inbox.user, which is the app's own "
                 "identifier rather than a person; in the tested image every message row was of "
                 "that kind, so the person-to-person path of this artifact is implemented and "
                 "not exercised by a corpus. A sample with real conversations would be welcome.\n"
                 "ZTYPE and ZSUBTYPE are reported as stored and were empty on every tested row. "
                 "Media columns are reported where present: ZMEDIAURL, ZPHOTOURL and "
                 "ZLOCALIMAGEURL hold locations rather than content, and no media message "
                 "existed in the tested image, so this artifact renders no media. See the "
                 "Tinder - Cached Photos artifact for the images present on disk.\n"
                 "The ZFORMATTINGDATA, ZVERSIONINGDATA and ZANALYTICSINFO columns hold "
                 "NSKeyedArchiver plists and are not decoded here.\n"
                 "The WAL sidecar is load-bearing for this database and must travel with it: "
                 "in the tested image the committed file held 10 message rows and the "
                 "WAL-applied read held 12.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/Tinder/Tinder2.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "abe_ios16": "iOS 16.4.1 | Tinder 14.9.0 | 12 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Match ID",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Created",
                "senderColumn": "Sender Name",
            }
        },
    },
    "tinderMatches": {
        "name": "Tinder - Matches",
        "description": "Matches from the ZMATCH table of the Tinder Core Data store "
                       "Tinder2.sqlite, joined to the matched person's ZUSER row",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Tinder",
        "notes": "One row per ZMATCH entry. Timestamps are Core Data (Cocoa) seconds. The "
                 "boolean-shaped columns (ZISSUPERLIKEMATCH, ZISFASTMATCH, ZISBOOSTMATCH, "
                 "ZISEXPIRED, ZMATCHSEEN and the rest) are reported as stored; Core Data leaves "
                 "them NULL rather than 0 when unset, so a blank means the app stored nothing.\n"
                 "The match whose ZMATCHID is the literal com.tinder.inbox.match is the app's "
                 "own inbox rather than a person, and it was the only match in the tested "
                 "image, so the person-match path here is implemented and not exercised by a "
                 "corpus. A sample with real matches would be welcome.\n"
                 "The WAL sidecar must travel with the database; see the Tinder - Messages "
                 "notes for the counts that show it is load-bearing.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/Tinder/Tinder2.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "heart",
        "sample_data": {
            "abe_ios16": "iOS 16.4.1 | Tinder 14.9.0 | 1 row",
        },
    },
    "tinderRecommendations": {
        "name": "Tinder - Recommendations",
        "description": "Recommended profiles from the ZRECOMMENDATION table of the Tinder Core "
                       "Data store Tinder2.sqlite, joined to each profile's ZUSER row",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Tinder",
        "notes": "Each row is a profile the app had stored as a recommendation, with that "
                 "person's name, user id, bio, city, distance and school where stored. "
                 "Presence of a row records that the app held the profile locally. It does not "
                 "establish that the profile was displayed to the user, that the user viewed "
                 "it, or that the user acted on it.\n"
                 "ZRECTYPE, ZRECSOURCE and ZSUBSOURCE are reported as stored; nothing in the "
                 "extraction maps their values. ZLIKED and ZSUPERLIKED come from the joined "
                 "ZUSER row and were NULL on every row in the tested image, so no swipe "
                 "decision is recoverable from it; a blank is an unset column, not a negative "
                 "answer. Birth dates are stored as Core Data seconds; in the tested image "
                 "most carried an identical time of day, which suggests the app stores a date "
                 "rather than an instant, so read the date and not the clock time.\n"
                 "ZDISTANCEMILES is the stored value, in miles, as the app recorded it at the "
                 "time; it is a distance from the account holder, not a location.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/Tinder/Tinder2.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "abe_ios16": "iOS 16.4.1 | Tinder 14.9.0 | 18 rows",
        },
    },
    "tinderAccount": {
        "name": "Tinder - Account",
        "description": "The signed-in account from the Tinder preferences plist "
                       "com.cardify.tinder.plist and the current-user row of the Core Data "
                       "store Tinder2.sqlite",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Tinder",
        "notes": "The email address, account creation time and login times come from the "
                 "preferences plist keys Profile.email, Profile.accountCreated, "
                 "Session.firstConsecutiveLoginDate and Session.lastConsecutiveLoginDate. The "
                 "Profile.account key holds a JSON document whose linked-account booleans "
                 "(Apple, Facebook, Google, phone and so on) are reported as stored.\n"
                 "The name, user id, birth date, gender, city and bio come from the ZUSER row "
                 "flagged ZISCURRENTUSER. Gender is reported as stored; nothing in the "
                 "extraction maps its values, and -1 appears on rows where the app stored no "
                 "value.\n"
                 "A key absent from the plist is reported blank. Tinder writes several of these "
                 "keys only once the corresponding action has happened, so a blank is absence "
                 "from the file rather than a zero or a negative finding.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Preferences/com.cardify.tinder.plist',
                  '*/mobile/Containers/Data/Application/*/Library/Application Support/Tinder/Tinder2.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "abe_ios16": "iOS 16.4.1 | Tinder 14.9.0 | 1 row",
        },
    },
    "tinderCachedPhotos": {
        "name": "Tinder - Cached Photos",
        "description": "Images in the Tinder PINRemoteImage disk cache, checked in as media "
                       "and matched to the profile photo URLs stored in Tinder2.sqlite",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Tinder",
        "notes": "The cache file name is the source URL with the ':', '/' and '.' characters "
                 "percent-encoded, so a cached file is tied to its URL by name rather than by "
                 "guesswork; the URL is decoded back from the file name and reported. Where "
                 "that URL also appears in the ZPHOTO or ZPROCESSEDPHOTO tables of "
                 "Tinder2.sqlite, the owning profile's name and user id are reported with it, "
                 "and the Source column says whether the row was matched to the database.\n"
                 "In the tested image the Tinder container held 79 cache files. 53 carry a "
                 "percent encoded name that decodes to a URL and 26 carry an opaque cache "
                 "key that does not, so the Source URL column holds the stored name as is on "
                 "those 26 rows. 4 of the 79 matched a stored profile photo URL, all of them "
                 "the account holder's own photos; the rest are app assets and marketing "
                 "images served from static-assets, marketing-images and inboxcrm hosts, and "
                 "they are reported too rather than dropped. A profile photo URL with no "
                 "cached file means no copy was found in the extraction; it does not "
                 "establish that the image was never on the device.\n"
                 "Content is sniffed from the file header rather than trusted from the URL "
                 "extension, since the cache stores webp, jpeg and png alike with no extension "
                 "of its own.\n"
                 "PINRemoteImage is Pinterest's own open source image library and other "
                 "applications embed it, so this cache directory carries the "
                 "com.pinterest.PINDiskCache prefix inside those applications' containers too "
                 "and its name does not say which application wrote a file. Twelve distinct "
                 "applications were observed carrying this directory across the tested images. "
                 "Rows are therefore restricted to files sitting under a container that also "
                 "holds Tinder2.sqlite or com.cardify.tinder.plist, which only Tinder writes. "
                 "Cache files under any other container are skipped and counted in the run log "
                 "rather than reported here, and where no Tinder container is identified no "
                 "rows are produced and that is logged. An empty result is not evidence that "
                 "the cache was empty.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/com.pinterest.PINDiskCache.PINRemoteImageManagerCache/*',
                  '*/mobile/Containers/Data/Application/*/Library/Application Support/Tinder/Tinder2.sqlite*',
                  '*/mobile/Containers/Data/Application/*/Library/Preferences/com.cardify.tinder.plist'),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
            "abe_ios16": "iOS 16.4.1 | Tinder 14.9.0 | 79 rows",
            "jess_ios15": "iOS 15.0.2 | Tinder not installed | 0 rows",
            "iphone12_ios18": "iOS 18.7 | Tinder not installed | 0 rows",
        },
    },
}

import json
import os
import plistlib

from scripts.ilapfuncs import artifact_processor, check_in_media, \
    convert_cocoa_core_data_ts_to_utc, convert_plist_date_to_utc, get_file_path, \
    get_sqlite_db_records, logfunc

# The app's own inbox uses these literal identifiers in place of a person.
_INBOX_USER = 'com.tinder.inbox.user'

_STORE = 'Tinder2.sqlite'

# The image cache directory is named for PINRemoteImage, Pinterest's open source
# image library, which other applications embed as well, so the directory carries
# the com.pinterest.PINDiskCache prefix inside their containers too and the name
# alone does not say which application wrote a file.
_IMAGE_CACHE_DIR = 'com.pinterest.PINDiskCache.PINRemoteImageManagerCache'

# Files only the Tinder application writes, used to tell its container from any
# other container in the same extraction. Both are matched by this artifact's own
# path patterns, so the set is built from the files handed to it rather than from
# the filesystem, which holds only what has been copied out so far.
_CONTAINER_MARKERS = (
    'Library/Application Support/Tinder/Tinder2.sqlite',
    'Library/Preferences/com.cardify.tinder.plist',
)


def _store_path(files_found):
    return get_file_path(files_found, _STORE)


def _containers(files_found):
    """Container directories holding a file only the Tinder app writes."""
    roots = set()
    for path in sorted(str(f) for f in files_found):
        normalized = path.replace('\\', '/')
        for marker in _CONTAINER_MARKERS:
            index = normalized.rfind('/' + marker)
            if index > 0:
                roots.add(normalized[:index])
                break
    return roots


def _container_of(path, roots):
    """The Tinder container a path sits under, or '' when it is outside them.

    The longest match wins, so a container nested inside another cannot be
    attributed to the outer one.
    """
    normalized = path.replace('\\', '/')
    matches = [root for root in roots if normalized.startswith(root + '/')]
    return max(matches, key=len) if matches else ''


def _cached_photo_files(files_found):
    """The image cache files that sit inside a Tinder container.

    A file matched in another application's container is skipped and counted, and
    when no Tinder container is identified nothing is reported, so a run that
    reports fewer rows says why rather than reporting a bare zero.
    """
    roots = _containers(files_found)
    candidates = [path for path in sorted(str(f) for f in files_found)
                  if '/' + _IMAGE_CACHE_DIR + '/' in path.replace('\\', '/')
                  and os.path.isfile(path)]
    if not candidates:
        return []
    if not roots:
        logfunc(f'Tinder: {len(candidates)} {_IMAGE_CACHE_DIR} file(s) were found but no '
                f'Tinder container was identified, so none are reported. This cache '
                f'directory is named for a shared library and is not evidence of Tinder.')
        return []
    kept = [path for path in candidates if _container_of(path, roots)]
    skipped = len(candidates) - len(kept)
    if skipped:
        logfunc(f'Tinder: skipped {skipped} {_IMAGE_CACHE_DIR} file(s) found outside a '
                f'Tinder container; this cache directory is named for a shared library.')
    return kept


def _records(files_found, query):
    source_path = _store_path(files_found)
    if not source_path:
        return '', []
    return source_path, list(get_sqlite_db_records(source_path, query))


def _decode_cache_name(name):
    '''The PINRemoteImage cache stores a file under its source URL with ':', '/' and
    '.' percent-encoded. Decode those three back, leaving any other percent escape
    from the URL itself untouched.'''
    return (name.replace('%3A', ':').replace('%2F', '/').replace('%2E', '.')
                .replace('%3a', ':').replace('%2f', '/').replace('%2e', '.'))


def _sniffed_extension(path):
    try:
        with open(path, 'rb') as f:
            magic = f.read(16)
    except OSError:
        return None
    if magic.startswith(b'\xff\xd8\xff'):
        return '.jpg'
    if magic.startswith(b'\x89PNG'):
        return '.png'
    if magic.startswith(b'RIFF') and b'WEBP' in magic:
        return '.webp'
    if magic.startswith(b'GIF8'):
        return '.gif'
    if b'ftyp' in magic:
        return '.mp4'
    return None


@artifact_processor
def tinderMessages(context):
    files_found = context.get_files_found()
    data_list = []
    source_path, records = _records(files_found, '''
        SELECT MESSAGE.ZCREATED, MESSAGE.ZCLIENTCREATED, MESSAGE.ZFROMUSERID,
               SENDER.ZFIRSTNAME AS SENDER_NAME, MESSAGE.ZTEXT, MESSAGE.ZTYPE,
               MESSAGE.ZSUBTYPE, MESSAGE.ZLIKED, MESSAGE.ZVIEWED, MESSAGE.ZISHIDDEN,
               MESSAGE.ZMEDIAURL, MESSAGE.ZPHOTOURL, MESSAGE.ZLOCALIMAGEURL,
               MESSAGE.ZLINKURL, MESSAGE.ZMESSAGEID, MATCH.ZMATCHID,
               OTHER.ZFIRSTNAME AS MATCH_NAME
        FROM ZMESSAGE MESSAGE
        LEFT JOIN ZUSER SENDER ON MESSAGE.ZFROMUSERID = SENDER.ZUSERID
        LEFT JOIN ZMATCH MATCH ON MESSAGE.ZMATCH = MATCH.Z_PK
        LEFT JOIN ZUSER OTHER ON MATCH.ZUSER = OTHER.Z_PK
        ORDER BY MESSAGE.ZCREATED
    ''')

    own_id = ''
    if source_path:
        for record in get_sqlite_db_records(
                source_path, 'SELECT ZUSERID FROM ZUSER WHERE ZISCURRENTUSER = 1'):
            own_id = record['ZUSERID'] or ''

    for record in records:
        sender_id = record['ZFROMUSERID'] or ''
        if own_id and sender_id == own_id:
            direction = 'Outgoing'
        elif sender_id:
            direction = 'Incoming'
        else:
            direction = ''
        data_list.append((
            convert_cocoa_core_data_ts_to_utc(record['ZCREATED']),
            convert_cocoa_core_data_ts_to_utc(record['ZCLIENTCREATED']),
            direction,
            record['SENDER_NAME'] or '',
            record['ZTEXT'] or '',
            record['MATCH_NAME'] or '',
            record['ZTYPE'] or '',
            record['ZSUBTYPE'] or '',
            record['ZLIKED'],
            record['ZVIEWED'],
            record['ZISHIDDEN'],
            record['ZMEDIAURL'] or '',
            record['ZPHOTOURL'] or '',
            record['ZLOCALIMAGEURL'] or '',
            record['ZLINKURL'] or '',
            sender_id,
            record['ZMESSAGEID'] or '',
            record['ZMATCHID'] or '',
        ))

    data_headers = (
        ('Created', 'datetime'),
        ('Client Created', 'datetime'),
        'Direction',
        'Sender Name',
        'Message',
        'Match Name',
        'Type (as stored)',
        'Subtype (as stored)',
        'Liked (as stored)',
        'Viewed (as stored)',
        'Is Hidden (as stored)',
        'Media URL',
        'Photo URL',
        'Local Image URL',
        'Link URL',
        'Sender ID',
        'Message ID',
        'Match ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def tinderMatches(context):
    files_found = context.get_files_found()
    data_list = []
    source_path, records = _records(files_found, '''
        SELECT MATCH.ZCREATED, MATCH.ZLASTACTIVITY, MATCH.ZEXPIRATIONDATE,
               MATCH.ZTOUCHED, USER.ZFIRSTNAME, USER.ZUSERID, USER.ZBIO,
               USER.ZCITYNAME, USER.ZBIRTHDATE, USER.ZGENDER, USER.ZDISTANCEMILES,
               MATCH.ZSERVERMESSAGECOUNT, MATCH.ZISSUPERLIKEMATCH, MATCH.ZISFASTMATCH,
               MATCH.ZISBOOSTMATCH, MATCH.ZISTOPPICKSMATCH, MATCH.ZISEXPIRED,
               MATCH.ZMATCHSEEN, MATCH.ZVIEWED, MATCH.ZFOLLOWING,
               MATCH.ZSUBSCRIPTIONTIER, MATCH.ZMESSAGEDRAFT, MATCH.ZMATCHID
        FROM ZMATCH MATCH
        LEFT JOIN ZUSER USER ON MATCH.ZUSER = USER.Z_PK
        ORDER BY MATCH.ZCREATED
    ''')

    for record in records:
        data_list.append((
            convert_cocoa_core_data_ts_to_utc(record['ZCREATED']),
            convert_cocoa_core_data_ts_to_utc(record['ZLASTACTIVITY']),
            convert_cocoa_core_data_ts_to_utc(record['ZTOUCHED']),
            convert_cocoa_core_data_ts_to_utc(record['ZEXPIRATIONDATE']),
            record['ZFIRSTNAME'] or '',
            convert_cocoa_core_data_ts_to_utc(record['ZBIRTHDATE']),
            record['ZBIO'] or '',
            record['ZCITYNAME'] or '',
            record['ZGENDER'],
            record['ZDISTANCEMILES'],
            record['ZSERVERMESSAGECOUNT'],
            record['ZISSUPERLIKEMATCH'],
            record['ZISFASTMATCH'],
            record['ZISBOOSTMATCH'],
            record['ZISTOPPICKSMATCH'],
            record['ZISEXPIRED'],
            record['ZMATCHSEEN'],
            record['ZVIEWED'],
            record['ZFOLLOWING'],
            record['ZSUBSCRIPTIONTIER'] or '',
            record['ZMESSAGEDRAFT'] or '',
            record['ZUSERID'] or '',
            record['ZMATCHID'] or '',
        ))

    data_headers = (
        ('Match Created', 'datetime'),
        ('Last Activity', 'datetime'),
        ('Touched', 'datetime'),
        ('Expiration Date', 'datetime'),
        'Matched Person',
        ('Birth Date', 'datetime'),
        'Bio',
        'City',
        'Gender (as stored)',
        'Distance (miles, as stored)',
        'Server Message Count',
        'Is Super Like Match (as stored)',
        'Is Fast Match (as stored)',
        'Is Boost Match (as stored)',
        'Is Top Picks Match (as stored)',
        'Is Expired (as stored)',
        'Match Seen (as stored)',
        'Viewed (as stored)',
        'Following (as stored)',
        'Subscription Tier (as stored)',
        'Message Draft',
        'Matched Person ID',
        'Match ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def tinderRecommendations(context):
    files_found = context.get_files_found()
    data_list = []
    source_path, records = _records(files_found, '''
        SELECT USER.ZBIRTHDATE, USER.ZFIRSTNAME, USER.ZUSERID, USER.ZBIO,
               USER.ZCITYNAME, USER.ZUSERLOCATIONNAME, USER.ZDISTANCEMILES,
               USER.ZGENDER, USER.ZCUSTOMGENDER, USER.ZVERIFIED, USER.ZLIKED,
               USER.ZSUPERLIKED, USER.ZINSTAGRAMNAME, USER.ZPUBLICUSERNAME,
               SCHOOL.ZNAME AS SCHOOL_NAME, REC.ZRECTYPE, REC.ZRECSOURCE,
               REC.ZSUBSOURCE, REC.ZISNEW, REC.ZDIDREWIND, REC.ZSWIPENOTE,
               REC.ZEXPIRATIONDATE, REC.ZRECOMMENDATIONID
        FROM ZRECOMMENDATION REC
        LEFT JOIN ZUSER USER ON REC.ZUSER = USER.Z_PK
        LEFT JOIN ZSCHOOL SCHOOL ON USER.ZSCHOOL = SCHOOL.Z_PK
        ORDER BY REC.Z_PK
    ''')

    for record in records:
        data_list.append((
            convert_cocoa_core_data_ts_to_utc(record['ZBIRTHDATE']),
            convert_cocoa_core_data_ts_to_utc(record['ZEXPIRATIONDATE']),
            record['ZFIRSTNAME'] or '',
            record['ZBIO'] or '',
            record['ZCITYNAME'] or '',
            record['ZUSERLOCATIONNAME'] or '',
            record['ZDISTANCEMILES'],
            record['ZGENDER'],
            record['ZCUSTOMGENDER'] or '',
            record['SCHOOL_NAME'] or '',
            record['ZINSTAGRAMNAME'] or '',
            record['ZPUBLICUSERNAME'] or '',
            record['ZVERIFIED'],
            record['ZLIKED'],
            record['ZSUPERLIKED'],
            record['ZRECTYPE'],
            record['ZRECSOURCE'] or '',
            record['ZSUBSOURCE'] or '',
            record['ZISNEW'],
            record['ZDIDREWIND'],
            record['ZSWIPENOTE'] or '',
            record['ZUSERID'] or '',
            record['ZRECOMMENDATIONID'] or '',
        ))

    data_headers = (
        ('Birth Date', 'datetime'),
        ('Expiration Date', 'datetime'),
        'Name',
        'Bio',
        'City',
        'User Location Name',
        'Distance (miles, as stored)',
        'Gender (as stored)',
        'Custom Gender',
        'School',
        'Instagram Name',
        'Public Username',
        'Verified (as stored)',
        'Liked (as stored)',
        'Super Liked (as stored)',
        'Rec Type (as stored)',
        'Rec Source (as stored)',
        'Sub Source (as stored)',
        'Is New (as stored)',
        'Did Rewind (as stored)',
        'Swipe Note',
        'User ID',
        'Recommendation ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def tinderAccount(context):
    files_found = context.get_files_found()
    data_list = []
    plist_path = get_file_path(files_found, 'com.cardify.tinder.plist')
    store_path = _store_path(files_found)

    prefs = {}
    if plist_path:
        try:
            with open(plist_path, 'rb') as f:
                prefs = plistlib.load(f)
        except (plistlib.InvalidFileException, ValueError, OSError) as ex:
            logfunc(f'Tinder: could not read {plist_path}: {ex}')

    account = {}
    raw_account = prefs.get('Profile.account')
    if isinstance(raw_account, bytes):
        try:
            account = json.loads(raw_account)
        except ValueError:
            account = {}
    elif isinstance(raw_account, dict):
        account = raw_account

    user = {}
    if store_path:
        for record in get_sqlite_db_records(store_path, '''
                SELECT ZUSERID, ZFIRSTNAME, ZBIRTHDATE, ZGENDER, ZBIO, ZCITYNAME,
                       ZPUBLICUSERNAME, ZINSTAGRAMNAME, ZSNUMBER
                FROM ZUSER WHERE ZISCURRENTUSER = 1'''):
            user = record

    if prefs or user:
        data_list.append((
            convert_plist_date_to_utc(prefs.get('Profile.accountCreated')),
            convert_plist_date_to_utc(prefs.get('Session.firstConsecutiveLoginDate')),
            convert_plist_date_to_utc(prefs.get('Session.lastConsecutiveLoginDate')),
            user['ZFIRSTNAME'] if user else '',
            user['ZUSERID'] if user else '',
            prefs.get('Profile.email', '') or account.get('account_email', ''),
            account.get('account_phone_number', ''),
            convert_cocoa_core_data_ts_to_utc(user['ZBIRTHDATE']) if user else '',
            user['ZGENDER'] if user else '',
            (user['ZBIO'] or '') if user else '',
            (user['ZCITYNAME'] or '') if user else '',
            (user['ZINSTAGRAMNAME'] or '') if user else '',
            account.get('apple_id_linked', ''),
            account.get('facebook_id_linked', ''),
            account.get('google_id_linked', ''),
            account.get('line_id_linked', ''),
            prefs.get('Session.hasAnyUserPreviouslyLoggedIn', ''),
        ))

    data_headers = (
        ('Account Created', 'datetime'),
        ('First Consecutive Login', 'datetime'),
        ('Last Consecutive Login', 'datetime'),
        'Name',
        'User ID',
        'Email',
        'Phone Number',
        ('Birth Date', 'datetime'),
        'Gender (as stored)',
        'Bio',
        'City',
        'Instagram Name',
        'Apple ID Linked (as stored)',
        'Facebook ID Linked (as stored)',
        'Google ID Linked (as stored)',
        'Line ID Linked (as stored)',
        'Has Any User Previously Logged In (as stored)',
    )
    return data_headers, data_list, plist_path or store_path


@artifact_processor
def tinderCachedPhotos(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''

    owners = {}
    store_path = _store_path(files_found)
    if store_path:
        # The owning profile is on ZPHOTO.ZMEDIAUSER; ZPHOTO.ZUSER was NULL on every
        # row of the tested image, so both are tried.
        for record in get_sqlite_db_records(store_path, '''
                SELECT PHOTO.ZIMAGEURL AS URL, USER.ZFIRSTNAME AS NAME,
                       USER.ZUSERID AS USER_ID
                FROM ZPHOTO PHOTO
                LEFT JOIN ZUSER USER
                    ON USER.Z_PK = COALESCE(PHOTO.ZMEDIAUSER, PHOTO.ZUSER)
                WHERE PHOTO.ZIMAGEURL IS NOT NULL
                UNION ALL
                SELECT PROCESSED.ZIMAGEURL, USER.ZFIRSTNAME, USER.ZUSERID
                FROM ZPROCESSEDPHOTO PROCESSED
                LEFT JOIN ZPHOTO PHOTO ON PROCESSED.ZPHOTO = PHOTO.Z_PK
                LEFT JOIN ZUSER USER
                    ON USER.Z_PK = COALESCE(PHOTO.ZMEDIAUSER, PHOTO.ZUSER)
                WHERE PROCESSED.ZIMAGEURL IS NOT NULL'''):
            owners.setdefault(record['URL'],
                              (record['NAME'] or '', record['USER_ID'] or ''))

    for file_found in _cached_photo_files(files_found):
        source_path = os.path.dirname(file_found)
        name = os.path.basename(file_found)
        url = _decode_cache_name(name)
        owner_name, owner_id = owners.get(url, ('', ''))
        media_ref = check_in_media(file_found, name,
                                   force_extension=_sniffed_extension(file_found))
        data_list.append((
            media_ref or '',
            owner_name,
            'Profile photo in Tinder2.sqlite' if url in owners else 'Cache only',
            url,
            os.path.getsize(file_found),
            owner_id,
            name,
        ))

    data_headers = (
        ('Photo', 'media'),
        'Owner Name',
        'Source',
        'Source URL',
        'File Size (bytes)',
        'Owner User ID',
        'Cache File Name',
    )
    return data_headers, data_list, source_path
