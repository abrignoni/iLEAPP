__artifacts_v2__ = {
    "safariHistory": {
        "name": "Safari Browser - History",
        "description": "Safari web history visits",
        "author": "@KevinPagano3",
        "creation_date": "2023-02-14",
        "last_update_date": "2026-10-01",
        "requirements": "none",
        "category": "Safari Browser",
        "notes": (
            "Where Safari profiles are present, each has its own "
            "History.db under Safari/Profiles/. The Profile column carries the profile "
            "directory name for those records and Default for the main history database. "
            "Tags and Tag Identifiers list the title and identifier of each history_tags row "
            "that a history_items_to_tags row links to the visit's history item, ordered by "
            "the link's timestamp and separated by a semicolon and a space. The link is to "
            "the history item, so each visit of that item shows the same tags. Tags and Tag "
            "Identifiers are blank when the item has no link and on a database that lacks "
            "either table. ctf2020_ios12 (iOS 12.4) has neither. The tags, their timestamps and the tags no item is linked to are "
            "reported by Safari Browser - History Tags."
        ),
        "paths": (
            '**/Safari/History.db*',
            '**/Safari/Profiles/*/History.db*',
        ),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | com.apple.mobilesafari | 208 rows",
            "dexter_ios18": "iOS 18.3.2 | 10 rows",
            "felix_ios17": "iOS 17.6.1 | 32 rows",
            "fsfull002_ios17": "iOS 17.1 | 13 rows",
            "hc_ios18_7": "iOS 18.7.8 | 7 rows",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 151 rows",
            "iphone14plus_ios18": "iOS 18.0 | 95 rows",
            "otto_ios17": "iOS 17.5.1 | 57 rows",
            "abe_ios16": "iOS 16.5 | 87 rows",
            "felix23_ios16": "iOS 16.5 | 20 rows",
            "hickman_ios13": "iOS 13.3.1 | 16 rows",
            "hickman_ios14": "iOS 14.3 | 36 rows",
            "jess_ios15": "iOS 15.0.2 | 44 rows",
            "magnet_ios16": "iOS 16.1.1 | 3 rows",
        }
    },
    "safariHistoryTags": {
        "name": "Safari Browser - History Tags",
        "description": "Tags stored in Safari's History.db and the history items each tag is linked to",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-01",
        "last_update_date": "2026-10-01",
        "requirements": "none",
        "category": "Safari Browser",
        "notes": (
            "One row per history_items_to_tags row, which links a history_tags row to a "
            "history_items row, and one row for each history_tags row that no link names. "
            "Tag Modified is history_tags.modification_timestamp and Item Tagged is "
            "history_items_to_tags.timestamp. Tag is the title column, Identifier the "
            "identifier column and URL the linked item's url. Item Count is "
            "history_tags.item_count as stored, Linked Items is the number of links that "
            "name the tag in the same database, counted by this artifact, and Type and "
            "Level are the stored integers. On the row of a tag with no link, Item Tagged "
            "and URL are blank and Linked Items is 0. A link that names a tag id "
            "history_tags lacks would not be reported, and a link that names a missing "
            "history item would show a blank URL. No tested database held either. "
            "The CREATE statements stored in the database allow one link per item and tag "
            "(UNIQUE(history_item, tag_id) ON CONFLICT REPLACE) and define two triggers "
            "that add 1 to item_count after a link is inserted and subtract 1 before a "
            "link is deleted. "
            "Measured on the 20 registered images that hold tags (iOS 13.3.1 to 26.5.2, "
            "178 tags and 104 links): Item Count was higher than Linked Items on 83 tags "
            "and lower on none, and 47 of the 103 tags with no link stored an Item Count "
            "above 0, so Linked Items, not Item Count, shows whether a history item is "
            "linked to the tag. Tag Modified equalled the tag's latest Item Tagged value on "
            "all 75 tags that had a link, and Item Tagged was within 60 seconds of a visit "
            "to the linked item on 99 of the 104 links. What event either time records is "
            "not established. Type held one value, 1, and Level held one value, 200, on "
            "all 178 tags, and what they mean is not established. No item was linked to more than 2 tags. "
            "The 103 tags with no link were on 8 of the 20 images; what removed their "
            "links is not established. In a known-data session on a Mac (macOS 27.0.1, "
            "Safari 27.0.1; DLEAPP's safari_tags_known_data_macos27, not an iOS image), deleting in "
            "Safari's History window the only history item linked to a tag removed the link "
            "and left the tag, with Item Count going from 1 to 0, and Clear History for the "
            "last hour, which covered every visit, removed every tag, the one with no link "
            "included. That session did not produce a tag with no link and an Item Count "
            "above 0, and none of it was tested on iOS. "
            "Every Identifier was the letter Q followed by digits, the form of a Wikidata "
            "item identifier. For the five public images abe_ios16, felix23_ios16, "
            "jess_ios15, magnet_ios16 and otto_ios17, wikidata.org returned an item for "
            "each of their 99 distinct identifiers on 2026-10-01, and Tag equalled that "
            "item's English label, ignoring case, on 86 and one of its English aliases on "
            "7. How Safari chooses a tag for a page is not established. "
            "All 282 stored values of the two times were below 978307200 and are read as "
            "seconds since 2001-01-01, shown in UTC. A value above 978307200 would be read as Unix seconds, the rule "
            "Safari Browser - History applies to visit_time; no tested image holds one, so "
            "that branch is unexercised. "
            "ctf2020_ios12 (iOS 12.4) has neither table, and dexter_ios18 and felix_ios17 "
            "hold both tables with no rows. Each History.db is read on its own, because "
            "item and tag ids are numbered within each database, and "
            "Profile carries the profile directory name or Default. Profile held one "
            "value, Default, on every row, because no tested image held a tag in a "
            "profile's database; that case was exercised with a constructed database "
            "only. "
            "The two tables and the Wikidata form of the identifier are described in the "
            "reference. Reference: Yogesh Khatri, 'Tags in Safari History db', "
            "https://www.swiftforensics.com/2026/10/tags-in-safari-history-db.html"
        ),
        "paths": (
            '**/Safari/History.db*',
            '**/Safari/Profiles/*/History.db*',
        ),
        "output_types": "standard",
        "artifact_icon": "tag",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 37 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 12 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 22 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows (History.db has neither tag table)",
            "dexter_ios18": "iOS 18.3.2 | 0 rows (both tag tables are empty)",
            "falken_ios26": "iOS 26.2.1 | 23 rows",
            "felix23_ios16": "iOS 16.5 | 3 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows (both tag tables are empty)",
            "fsfull002_ios17": "iOS 17.1 | 2 rows",
            "hc_ios17_2": "iOS 17.2.1 | 7 rows",
            "hc_ios18_7": "iOS 18.7.8 | 2 rows",
            "hc_ios26": "iOS 26.5.2 | 7 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 5 rows",
            "hickman_ios13": "iOS 13.3.1 | 1 row",
            "hickman_ios14": "iOS 14.3 | 4 rows",
            "hickman_ios15": "iOS 15.3.1 | 4 rows",
            "iphone11_ios17": "iOS 17.3 | 3 rows",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "iphone14plus_ios18": "iOS 18.0 | 3 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 6 rows",
            "jess_ios15": "iOS 15.0.2 | 12 rows",
            "magnet_ios16": "iOS 16.1.1 | 1 row",
            "otto_ios17": "iOS 17.5.1 | 52 rows",
        }
    }
}

from pathlib import PurePath

from scripts.ilapfuncs import artifact_processor, does_table_exist_in_db, get_sqlite_db_records


def _profile_name(source_path):
    parts = PurePath(source_path).parts
    if len(parts) >= 3 and parts[-3] == 'Profiles':
        return parts[-2]
    return 'Default'


def _history_databases(context):
    return [str(file_found) for file_found in context.get_files_found()
            if str(file_found).endswith('History.db')]


def _has_tag_tables(source_path):
    return (does_table_exist_in_db(source_path, 'history_tags')
            and does_table_exist_in_db(source_path, 'history_items_to_tags'))


def _item_tags(source_path):
    '''history_items.id -> (tag titles, tag identifiers), ordered by link timestamp.'''
    if not _has_tag_tables(source_path):
        return {}
    tags = {}
    for row in get_sqlite_db_records(source_path, '''
        SELECT history_items_to_tags.history_item, history_tags.title, history_tags.identifier
        FROM history_items_to_tags
        JOIN history_tags ON history_tags.id = history_items_to_tags.tag_id
        ORDER BY history_items_to_tags.history_item, history_items_to_tags.timestamp,
            history_tags.id'''):
        titles, identifiers = tags.setdefault(row[0], ([], []))
        titles.append(row[1])
        identifiers.append(row[2])
    return {item: ('; '.join(titles), '; '.join(identifiers))
            for item, (titles, identifiers) in tags.items()}


@artifact_processor
def safariHistory(context):
    data_headers = (('Visit Timestamp', 'datetime'), 'Title', 'URL', 'Visit Count',
                    'Redirect Source', 'Redirect Destination', 'Visit ID', 'Origin',
                    'Tags', 'Tag Identifiers', 'Profile')
    data_list = []

    source_paths = _history_databases(context)
    if not source_paths:
        return data_headers, data_list, ''

    # visit_time is Apple absolute (Cocoa) time on iOS <= 18, but iOS 26+ may
    # store a Unix timestamp instead. Cocoa values for realistic dates stay well
    # below the 978307200 offset (year 2032 in Cocoa time), while Unix values are
    # always above it, so the magnitude disambiguates the two encodings.
    query = '''
    SELECT
        CASE
            WHEN history_visits.visit_time > 978307200
                THEN datetime(history_visits.visit_time, 'unixepoch')
            ELSE datetime(history_visits.visit_time + 978307200, 'unixepoch')
        END,
        history_visits.title,
        history_items.url,
        history_items.visit_count,
        history_visits.redirect_source,
        history_visits.redirect_destination,
        history_visits.id,
        CASE history_visits.origin WHEN 0 THEN 'Local Device' WHEN 1 THEN 'iCloud Synced Device' END,
        history_visits.history_item
    FROM history_visits
    LEFT JOIN history_items ON history_visits.history_item = history_items.id
    ORDER BY
        CASE
            WHEN history_visits.visit_time > 978307200 THEN history_visits.visit_time
            ELSE history_visits.visit_time + 978307200
        END,
        history_visits.id
    '''
    for source_path in source_paths:
        profile = _profile_name(source_path)

        # Map visit id -> url so redirect source/destination ids can be resolved to
        # URLs. Visit ids are only unique within one database, so the map is per file.
        id_url = {}
        for row in get_sqlite_db_records(source_path, '''
            SELECT history_visits.id, history_items.url
            FROM history_visits
            LEFT JOIN history_items ON history_items.id = history_visits.history_item'''):
            id_url[str(row[0])] = row[1]

        # Item ids are only unique within one database as well.
        item_tags = _item_tags(source_path)

        for row in get_sqlite_db_records(source_path, query):
            redirect_source = id_url.get(str(row[4]), '') if row[4] is not None else ''
            redirect_destination = id_url.get(str(row[5]), '') if row[5] is not None else ''
            tags, tag_identifiers = item_tags.get(row[8], ('', ''))
            data_list.append((row[0], row[1], row[2], row[3], redirect_source,
                              redirect_destination, row[6], row[7], tags, tag_identifiers,
                              profile))

    sources = '\n'.join(context.get_relative_path(path) for path in source_paths)
    return data_headers, data_list, sources


@artifact_processor
def safariHistoryTags(context):
    data_headers = (('Tag Modified', 'datetime'), ('Item Tagged', 'datetime'), 'Tag',
                    'Identifier', 'URL', 'Item Count', 'Linked Items', 'Type', 'Level',
                    'Profile')
    data_list = []

    source_paths = _history_databases(context)
    if not source_paths:
        return data_headers, data_list, ''

    # One row per link between a tag and a history item, and one row for a tag no
    # link names. Both timestamps are read with the rule the visit time uses above.
    query = '''
    SELECT
        CASE
            WHEN history_tags.modification_timestamp > 978307200
                THEN datetime(history_tags.modification_timestamp, 'unixepoch')
            ELSE datetime(history_tags.modification_timestamp + 978307200, 'unixepoch')
        END,
        CASE
            WHEN history_items_to_tags.timestamp > 978307200
                THEN datetime(history_items_to_tags.timestamp, 'unixepoch')
            ELSE datetime(history_items_to_tags.timestamp + 978307200, 'unixepoch')
        END,
        history_tags.title,
        history_tags.identifier,
        history_items.url,
        history_tags.item_count,
        (SELECT COUNT(*) FROM history_items_to_tags AS links
            WHERE links.tag_id = history_tags.id),
        history_tags.type,
        history_tags.level
    FROM history_tags
    LEFT JOIN history_items_to_tags ON history_items_to_tags.tag_id = history_tags.id
    LEFT JOIN history_items ON history_items.id = history_items_to_tags.history_item
    ORDER BY
        CASE
            WHEN history_tags.modification_timestamp > 978307200
                THEN history_tags.modification_timestamp
            ELSE history_tags.modification_timestamp + 978307200
        END,
        history_tags.id,
        history_items_to_tags.timestamp
    '''
    for source_path in source_paths:
        if not _has_tag_tables(source_path):
            continue
        profile = _profile_name(source_path)
        for row in get_sqlite_db_records(source_path, query):
            data_list.append((row[0], row[1], row[2], row[3], row[4] or '', row[5],
                              row[6], row[7], row[8], profile))

    sources = '\n'.join(context.get_relative_path(path) for path in source_paths)
    return data_headers, data_list, sources
