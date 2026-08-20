__artifacts_v2__ = {
    "googleDocsDocuments": {
        "name": "Google Docs - Documents",
        "description": "Documents the Google Docs iOS app kept a local store for, with the "
                       "document title, identifier, type, ownership flag and the timestamps the "
                       "app recorded for creation, server modification, sync and app start",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Docs",
        "notes": "The localStore and fileStore layouts are shared by the Google editor apps, so a Google Sheets or Google Slides container carries the same paths; a store is only reported when the same container also holds the Google Docs preferences file, and one that does not is skipped and logged. That guard fails closed, so a collection that captured the stores but not the preferences file would report nothing here; the skip lines in the run log are what distinguishes that from an app that was never used. One row per <document id>.db under Documents/<account id>/localStore/documents/"
                 "<document id>/. Values come from that store's document_properties table, which "
                 "holds a property name, a type code and a value blob. The type code is read from "
                 "the file: code 0 values decoded as UTF-8 on all 762 rows tested, code 2 values "
                 "parsed as JSON on all 188, and code 1 values were 8 bytes on all 694 and decode "
                 "as little endian IEEE 754 doubles. Little endian is the reading the data "
                 "supports: it classified all 694 code 1 values as either an exact integer below "
                 "one million or a Unix millisecond time between 2005 and 2030, where big endian "
                 "classified none as a time and left 587 unclassified. Timestamps in this table "
                 "are Unix milliseconds. The account name, email address, account identifier and "
                 "profile image URL are read from the docosKeyData property, a positional JSON "
                 "array; the four fields were confirmed by shape on all 38 values that carried "
                 "the block, and the identifier equalled the account directory in the path on all "
                 "38. It records the signed in account rather than the document creator: three "
                 "documents whose isOwner property was not true carried the same account. Owner "
                 "state is reported from isOwner as stored. Revision, access level and the "
                 "remaining code 1 values are reported as stored because no value list ships in "
                 "the file. A store with no title property had never synced. Reference: Park, "
                 "Park, Kim, Kang and Kim, 'A comprehensive artifact analysis of Google "
                 "applications on Android and iOS platforms', Forensic Science International: "
                 "Digital Investigation.",
        "paths": ('*/Documents/*/localStore/documents/*/*.db*',
                  '*/Library/Preferences/com.google.Docs.plist'),
        "output_types": "standard",
        "artifact_icon": "file-text",
        "sample_data": {
            "magnet_ios16": "iOS 16.1.1 | 4 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "hc_ios26": "iOS 26.5.2 | 0 rows, no document stores in the container",
        },
    },
    "googleDocsDocumentText": {
        "name": "Google Docs - Document Text",
        "description": "Text stored in the Google Docs iOS app's per document command log, one "
                       "row per document",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Docs",
        "notes": "The localStore and fileStore layouts are shared by the Google editor apps, so a "
                 "Google Sheets or Google Slides container carries the same paths; a store is "
                 "only reported when the same container also holds the Google Docs preferences "
                 "file, and one that does not is skipped and logged. That guard fails closed, so a "
                 "collection that captured the stores but not the preferences file would report "
                 "nothing here; the skip lines in the run log are what distinguishes that from an "
                 "app that was never used. "
                 "A container holds a directory per signed in account and the same document can be "
                 "open under more than one of them, so each account's copy is reported as its own "
                 "row. "
                 "One row per document, built "
                 "from the document_commands table of the <document id>.db store under "
                 "Documents/<account id>/localStore/documents/. Each command row holds a JSON "
                 "array; the text is taken from the commands whose stored ty value is is, using "
                 "their s value, and the rows are read in stored order, revision then chunk "
                 "index, so joining them reproduces the order the log holds. The Stored Text "
                 "Segments column gives how many such commands the document was built from. "
                 "Command types are reported as stored: the tested stores held as, is, ae, nm, "
                 "te, ord, umv, mkch, ac and utlp, and no mapping for those names was sourced. "
                 "The text is what the command log holds, not a rendering of the document: "
                 "across the tested stores the recovered characters covered 99.49 percent of the "
                 "index span the insert commands describe, and 18 of 38 documents were gap free, "
                 "so positions held by other command types are absent. The timestamp column of "
                 "document_commands was zero on all 361 tested rows and is not reported, and the "
                 "part identifier was 0 on all of them. Reference: Park, Park, Kim, Kang and "
                 "Kim, 'A comprehensive artifact analysis of Google applications on Android and "
                 "iOS platforms', Forensic Science International: Digital Investigation.",
        "paths": ('*/Documents/*/localStore/documents/*/*.db*',
                  '*/Library/Preferences/com.google.Docs.plist'),
        "output_types": "standard",
        "artifact_icon": "file-description",
        "sample_data": {
            "magnet_ios16": "iOS 16.1.1 | 3 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "hc_ios26": "iOS 26.5.2 | 0 rows, no document stores in the container",
        },
    },
    "googleDocsDocumentMedia": {
        "name": "Google Docs - Document Media",
        "description": "Images and drawings the Google Docs iOS app stored for a document, "
                       "rendered and shown with the document they belong to",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Docs",
        "notes": "The localStore and fileStore layouts are shared by the Google editor apps, so a Google Sheets or Google Slides container carries the same paths; a store is only reported when the same container also holds the Google Docs preferences file, and one that does not is skipped and logged. That guard fails closed, so a collection that captured the stores but not the preferences file would report nothing here; the skip lines in the run log are what distinguishes that from an app that was never used. One row per file under Documents/<account id>/fileStore/documents/<document id>/"
                 "documents/<document id>/image/ and the sibling drawing/ directory. The document "
                 "is taken from the path, which repeats the document identifier. The two "
                 "identifiers were equal on all 61 tested files, image and drawing alike, and "
                 "each resolved to a per document store holding a title, so only the outer one "
                 "is reported; a path whose "
                 "two identifiers disagree is logged. The blob_metadata table that could carry a "
                 "database side link was empty in all 46 tested stores, so the link reported here "
                 "is the one the path records. Files are stored without an extension and the "
                 "image type is read from the file content; PNG and JPEG were observed. "
                 "Reference: Park, Park, Kim, Kang and Kim, 'A comprehensive artifact analysis of "
                 "Google applications on Android and iOS platforms', Forensic Science "
                 "International: Digital Investigation.",
        "paths": ('*/Documents/*/localStore/documents/*/*.db*',
                  '*/Documents/*/fileStore/documents/*/documents/*/image/*',
                  '*/Documents/*/fileStore/documents/*/documents/*/drawing/*',
                  '*/Library/Preferences/com.google.Docs.plist'),
        "output_types": "standard",
        "artifact_icon": "photo",
        "sample_data": {
            "magnet_ios16": "iOS 16.1.1 | 0 rows, no stored document media in the container",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows, no stored document media in the container",
            "hc_ios26": "iOS 26.5.2 | 0 rows, no document stores in the container",
        },
    },
    "googleDocsDocumentSync": {
        "name": "Google Docs - Document Sync State",
        "description": "Per document sync state the Google Docs iOS app records across documents, "
                       "with the server update time, the last sync finish time and the failure "
                       "count",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Docs",
        "notes": "The localStore and fileStore layouts are shared by the Google editor apps, so a Google Sheets or Google Slides container carries the same paths; a store is only reported when the same container also holds the Google Docs preferences file, and one that does not is skipped and logged. That guard fails closed, so a collection that captured the stores but not the preferences file would report nothing here; the skip lines in the run log are what distinguishes that from an app that was never used. One row per cross_document_metadata row in documentMetadata.db under "
                 "Documents/<account id>/localStore/shared/. This table stores the same server "
                 "update time in two units in two columns, so each is converted by its own unit "
                 "rather than by magnitude: last_server_updated_timestamp_milliseconds is Unix "
                 "milliseconds and drive_last_server_udated_timestamp, whose name carries the "
                 "spelling used in the schema, is Unix seconds. On all 30 tested rows that "
                 "carried both, the millisecond value equalled the second value times one "
                 "thousand. last_sync_finish_timestamp is Unix seconds. A row whose timestamps "
                 "are zero had not synced; 8 of the 46 tested rows were in that state. Pending "
                 "change, snapshot and failure counts are reported as stored. The resource key "
                 "column was empty on every tested row and is kept so its absence is visible, and "
                 "the seconds column was empty on one tested sample while the millisecond column "
                 "was populated, so the two are reported separately rather than merged. "
                 "The main database "
                 "file can be nearly empty with the rows held in the write ahead log, so the "
                 "sidecars are matched by the path pattern and must travel with the database. "
                 "Reference: Park, Park, Kim, Kang and Kim, 'A comprehensive artifact analysis of "
                 "Google applications on Android and iOS platforms', Forensic Science "
                 "International: Digital Investigation.",
        "paths": ('*/Documents/*/localStore/shared/documentMetadata.db*',
                  '*/Library/Preferences/com.google.Docs.plist'),
        "output_types": "standard",
        "artifact_icon": "refresh",
        "sample_data": {
            "magnet_ios16": "iOS 16.1.1 | 4 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "hc_ios26": "iOS 26.5.2 | 0 rows, no document stores in the container",
        },
    },
    "googleDocsCommentSync": {
        "name": "Google Docs - Comment Sync State",
        "description": "Documents the Google Docs iOS app tracked comments for, with the last "
                       "modified time and the next scheduled sync time",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Docs",
        "notes": "The localStore and fileStore layouts are shared by the Google editor apps, so a Google Sheets or Google Slides container carries the same paths; a store is only reported when the same container also holds the Google Docs preferences file, and one that does not is skipped and logged. That guard fails closed, so a collection that captured the stores but not the preferences file would report nothing here; the skip lines in the run log are what distinguishes that from an app that was never used. One row per comment_items row in comments_snapshot_<account id>.db under "
                 "Documents/<account id>/. The stored item_identifier reads <kind>:<document id>; "
                 "the kind part was document on each tested row and is not reported as its own "
                 "column, and the identifier part is used "
                 "to fill the Document Title column when a per document store in the same "
                 "container holds a title. last_modified_date is Unix seconds. next_sync_date is "
                 "an ISO 8601 string carrying its own zone designator and is reported as stored "
                 "rather than converted. The comments table in the same database, which holds "
                 "comment text, was empty on both tested samples while comment_items held rows, "
                 "so a row here records that the app tracked comments for that document and does "
                 "not carry the comment content. The resource key column was empty on every "
                 "tested row and is kept so its absence is visible; the stored comment item "
                 "version held the same value on every tested row and is not reported. Comment text from this database is covered by "
                 "the Google Drive comments artifact, whose path pattern also matches this file. "
                 "The whole table sat in the write ahead log on both tested samples, with a 4096 "
                 "byte main database file, so the sidecars must travel with the database.",
        "paths": ('*/Documents/*/comments_snapshot_*.db*',
                  '*/Documents/*/localStore/documents/*/*.db*',
                  '*/Library/Preferences/com.google.Docs.plist'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "magnet_ios16": "iOS 16.1.1 | 4 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "hc_ios26": "iOS 26.5.2 | 0 rows, no document stores in the container",
        },
    },
    "googleDocsAccounts": {
        "name": "Google Docs - Accounts",
        "description": "Google accounts the Google Docs iOS app recorded, showing the signed in "
                       "account and the account identifiers named by keys in the app's "
                       "preferences",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Docs",
        "notes": "One row per account identifier named by a key in the app's preferences property "
                 "list, together with the value of signed_in_user_id. Identifiers are taken from "
                 "the key names the app writes per account, so an account can appear here after "
                 "its documents have gone: on one tested sample five identifiers appeared in the "
                 "notification keys while only one had a document directory. The name, email "
                 "address and profile image URL are filled from the docosKeyData property of a "
                 "document store belonging to that account when the container holds one. Presence "
                 "of an identifier records that the app held state for that account and does not "
                 "establish that the account was signed in at the time of the extraction.",
        "paths": ('*/Library/Preferences/com.google.Docs.plist',
                  '*/Documents/*/localStore/documents/*/*.db*'),
        "output_types": "standard",
        "artifact_icon": "user-circle",
        "sample_data": {
            "magnet_ios16": "iOS 16.1.1 | 2 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "hc_ios26": "iOS 26.5.2 | 1 row",
        },
    },
    "googleDocsAppState": {
        "name": "Google Docs - Application State",
        "description": "Application level state recorded by the Google Docs iOS app, including "
                       "first launch dates, the recorded app version and device boot time",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Docs",
        "notes": "One row per key read from Library/Preferences/com.google.Docs.plist. Date typed "
                 "values are property list dates and are reported in UTC. The three orphan file "
                 "cleanup keys and the crash state tracker boot time are floating point Unix "
                 "seconds and are converted as seconds; no other key is converted. The two first "
                 "launch keys are written by different libraries and disagreed on one tested "
                 "sample, so both are reported under their stored key names rather than merged. "
                 "Remaining values are reported as stored. Absence of a key means the app wrote "
                 "no value for it and is not evidence that a feature was unused.",
        "paths": ('*/Library/Preferences/com.google.Docs.plist',),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {
            "magnet_ios16": "iOS 16.1.1 | 38 rows",
            "hc_ios18_7": "iOS 18.7.8 | 32 rows",
            "hc_ios26": "iOS 26.5.2 | 32 rows",
        },
    },
    "googleDocsContacts": {
        "name": "Google Docs - Contacts Cache",
        "description": "People cached by the Google Docs iOS app for looking up collaborators, "
                       "with the display name, addresses and the affinity value as stored",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Docs",
        "notes": "One row per contacts row in Contacts_<number>_<account id>.db under "
                 "Library/Caches/. The file name is a shared Google people cache name and is not "
                 "specific to this app, so a cache is only reported when the same container also "
                 "holds the Google Docs preferences file; a container holding the cache without "
                 "that marker is skipped and logged. The container set is built from the files "
                 "this artifact's own patterns matched, so it does not depend on the order "
                 "artifacts run in. Identity fields are read from the undocumented protobuf in "
                 "the proto_data column and are selected by field position. Most cached people "
                 "carry no name: on the one tested cache 2 of 42 rows held a display name while "
                 "all 42 held an address, so a blank name is the stored state rather than a "
                 "decoding failure. Where that field is empty the name recorded inside the "
                 "contact method is used. The affinity value is reported as stored and no meaning "
                 "is asserted for it. Presence of a person here "
                 "records that the app held them in a lookup cache and does not establish that "
                 "the user shared a document with them or contacted them. Photo values are the "
                 "remote URLs the app recorded; no image bytes were present in the tested "
                 "samples, so nothing is checked in as media. Reference: Park, Park, Kim, Kang "
                 "and Kim, 'A comprehensive artifact analysis of Google applications on Android "
                 "and iOS platforms', Forensic Science International: Digital Investigation.",
        "paths": ('*/Library/Caches/Contacts_*.db*',
                  '*/Library/Preferences/com.google.Docs.plist'),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "magnet_ios16": "iOS 16.1.1 | 4 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows, contacts cache present in the container but empty",
            "hc_ios26": "iOS 26.5.2 | 0 rows, no contacts cache in the container",
        },
    },
}

import json
import os
import re
import sqlite3
import struct
from datetime import datetime, timezone

from google.protobuf.message import DecodeError

from scripts import blackboxprotobuf
from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    get_plist_file_content,
    get_sqlite_db_records,
    null_absent_columns,
    logfunc,
)

# The exception types the vendored protobuf reader raises on input it cannot read. Listed
# rather than catching Exception, so a bug in this module's own field handling still
# surfaces instead of being reported as an undecodable value.
_PROTOBUF_ERRORS = (DecodeError, KeyError, IndexError, ValueError, struct.error)

# document_properties, blob_metadata_properties and their siblings store a value blob next
# to an integer type code. The codes below are the ones the tested stores used; see the
# artifact notes for how each was established from the data.
_TYPE_TEXT = 0
_TYPE_DOUBLE = 1
_TYPE_JSON = 2

_DOC_STORE_RE = re.compile(
    r'[/\\]Documents[/\\]([^/\\]+)[/\\]localStore[/\\]documents[/\\]([^/\\]+)[/\\][^/\\]+\.db$')
_DOC_MEDIA_RE = re.compile(
    r'[/\\]Documents[/\\]([^/\\]+)[/\\]fileStore[/\\]documents[/\\]([^/\\]+)'
    r'[/\\]documents[/\\]([^/\\]+)[/\\](image|drawing)[/\\]([^/\\]+)$')
_ACCOUNT_DIR_RE = re.compile(r'[/\\]Documents[/\\](\d{6,})[/\\]')
# Keys the app writes one per account. The identifier is whatever follows the key name.
_ACCOUNT_KEY_PREFIXES = (
    'GNPRepresentativeTargetIDKey-',
    'GNPRenderContextStorage-google_docs-',
    'shared_container_id_to_folder_',
    'userid:',
)
_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
_ACCOUNT_ID_RE = re.compile(r'^\d{15,25}$')


# --------------------------------------------------------------------------------------
# Unit specific timestamp helpers.
#
# This app stores seconds and milliseconds in adjacent columns of the same table, so each
# converter is named for the unit it takes and every call site chooses one. Nothing here
# infers a unit from the size of the value.
# --------------------------------------------------------------------------------------

def _from_ms(value):
    """Render a Unix millisecond value, keeping a missing or zero value empty."""
    if value in (None, '', 0):
        return ''
    try:
        seconds = float(value) / 1000
        return datetime.fromtimestamp(seconds, timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    except (TypeError, ValueError, OSError, OverflowError):
        return ''


def _from_seconds(value):
    """Render a Unix second value, keeping a missing or zero value empty."""
    if value in (None, '', 0):
        return ''
    try:
        return datetime.fromtimestamp(float(value), timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    except (TypeError, ValueError, OSError, OverflowError):
        return ''


def _from_plist_date(value):
    """Render a property list date in UTC, keeping anything else empty."""
    if not isinstance(value, datetime):
        return ''
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


# --------------------------------------------------------------------------------------
# Property store helpers.
# --------------------------------------------------------------------------------------

def _decode_property(type_code, value):
    """Decode one property value using the type code stored beside it.

    Returns the decoded value, or the raw text when the code is one this module has not
    seen. A value is never dropped for having an unexpected code: an unreadable value is
    more useful visible than absent.
    """
    if value is None:
        return None
    if type_code == _TYPE_DOUBLE:
        if len(value) != 8:
            return None
        return struct.unpack('<d', value)[0]
    try:
        text = value.decode('utf-8')
    except (UnicodeDecodeError, AttributeError):
        return None
    if type_code == _TYPE_JSON:
        try:
            return json.loads(text)
        except ValueError:
            return text
    return text


def _read_properties(db_path, table='document_properties'):
    """Read one property table into a name to decoded value mapping."""
    try:
        records = list(get_sqlite_db_records(
            db_path, f'SELECT name, type, value FROM {table}'))
    except sqlite3.Error as error:
        logfunc(f'Google Docs: could not read {table} from {db_path}: {error}')
        return {}
    properties = {}
    for name, type_code, value in records:
        if name is None:
            continue
        properties[name] = _decode_property(type_code, value)
    return properties


def _text(value):
    """Render a decoded value as report text."""
    if value is None:
        return ''
    if isinstance(value, str):
        return value
    if isinstance(value, float):
        # Every code 1 value in the tested stores was a whole number; keep it that way in
        # the report rather than printing a trailing .0, but do not hide a fraction.
        return str(int(value)) if value.is_integer() else str(value)
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _identity(properties):
    """The account name, photo URL, identifier and email recorded on a document.

    docosKeyData is a positional JSON array. The block at index 8 held the four values
    below in every tested store, and its identifier equalled the account directory in the
    path on all of them. It records the account the app was signed in as, which is not
    necessarily the account that created the document.
    """
    block = properties.get('docosKeyData')
    if not isinstance(block, list) or len(block) <= 8:
        return '', '', '', ''
    entry = block[8]
    if not isinstance(entry, list) or len(entry) < 8:
        return '', '', '', ''

    def at(index, check=None):
        value = entry[index] if index < len(entry) else None
        if not isinstance(value, str):
            return ''
        if check and not check.match(value):
            return ''
        return value

    return (at(0), at(2), at(3, _ACCOUNT_ID_RE), at(7, _EMAIL_RE))


def _docs_containers(files):
    """Container roots holding this app's preferences file.

    The localStore and fileStore layouts are shared by the Google editor apps, so a Google
    Sheets or Google Slides container carries the same paths and would otherwise be
    reported here as Google Docs. The set is built from this artifact's own matched files,
    so it does not depend on the order artifacts run in.
    """
    roots = {_container_root(f) for f in files
             if os.path.basename(str(f)) == 'com.google.Docs.plist'}
    roots.discard(None)
    return roots


def _in_docs_container(path, containers, context):
    """True when a matched file sits in a container that holds the Docs preferences file."""
    if _container_root(path, '/Documents/') in containers:
        return True
    logfunc('Google Docs: skipping a store with no Google Docs preferences file in the '
            f'same container: {context.get_relative_path(path)}')
    return False


def _document_stores(files, containers=None):
    """Map a store to its path, keyed by container, account directory and document id.

    One container holds a directory per signed in account, and the same document can be
    open under more than one of them. Keying on the document id alone silently drops all
    but one copy, so the account directory is part of the key.
    """
    stores = {}
    skipped = set()
    for file_found in files:
        match = _DOC_STORE_RE.search(str(file_found).replace('\\', '/'))
        if not match:
            continue
        if containers is not None and _container_root(file_found, '/Documents/') not in containers:
            skipped.add(_container_root(file_found, '/Documents/'))
            continue
        # The directory and the file are named for the same document in every tested
        # store; the file name is what is read here.
        document_id = os.path.splitext(os.path.basename(str(file_found)))[0]
        key = (_container_root(file_found, '/Documents/'), match.group(1), document_id)
        stores[key] = str(file_found)
    for container in sorted(x for x in skipped if x):
        logfunc('Google Docs: skipping the document stores of a container with no Google Docs '
                f'preferences file: {container}')
    return stores


def _container_root(path, marker='/Library/'):
    """The app container directory a path sits under, or None.

    The stores this module reads all sit under either the container's Library or its
    Documents directory, so cutting at the last occurrence of that segment gives a key
    that files in the same container share.
    """
    normalised = str(path).replace('\\', '/')
    index = normalised.rfind(marker)
    return normalised[:index] if index != -1 else None


def _titles_by_document(files, containers=None):
    """Title per (container, account, document id), read from the per document stores."""
    titles = {}
    for key, path in _document_stores(files, containers).items():
        title = _text(_read_properties(path).get('title'))
        if title:
            titles[key] = title
    return titles


@artifact_processor
def googleDocsDocuments(context):
    data_list = []
    files = [str(f) for f in context.get_files_found()]
    containers = _docs_containers(files)

    for (_container, _account, document_id), file_found in sorted(
            _document_stores(files, containers).items()):
        properties = _read_properties(file_found)
        if not properties:
            continue
        name, photo, account_id, email = _identity(properties)
        account_from_path = _ACCOUNT_DIR_RE.search(file_found.replace('\\', '/'))

        data_list.append((
            _from_ms(properties.get('lastModifiedServerTimestamp')),
            _from_ms(properties.get('docCreationTimestamp')),
            _from_ms(properties.get('lastSyncedTimestamp')),
            _from_ms(properties.get('lastColdStartedTimestamp')),
            _from_ms(properties.get('lastWarmStartedTimestamp')),
            _from_ms(properties.get('lastServerSnapshotTimestamp')),
            _text(properties.get('title')),
            _text(properties.get('id')) or document_id,
            _text(properties.get('documentType')),
            _text(properties.get('mimeType')),
            _text(properties.get('isOwner')),
            _text(properties.get('rev')),
            _text(properties.get('acl')),
            name,
            email,
            account_id or (account_from_path.group(1) if account_from_path else ''),
            photo,
            _text(properties.get('jobset')),
            context.get_relative_path(file_found),
        ))

    data_headers = (
        ('Last Modified On Server', 'datetime'),
        ('Document Created', 'datetime'),
        ('Last Synced', 'datetime'),
        ('Last Cold Started', 'datetime'),
        ('Last Warm Started', 'datetime'),
        ('Last Server Snapshot', 'datetime'),
        'Title',
        'Document ID',
        'Document Type',
        'MIME Type',
        'Is Owner (as stored)',
        'Revision (as stored)',
        'Access Level (as stored)',
        'Account Name',
        'Account Email',
        'Account ID',
        'Account Photo URL',
        'Jobset',
        'Source File',
    )
    return data_headers, data_list, 'see Source File for more info'


@artifact_processor
def googleDocsDocumentText(context):
    data_list = []
    files = [str(f) for f in context.get_files_found()]
    containers = _docs_containers(files)

    for (_container, _account, document_id), file_found in sorted(
            _document_stores(files, containers).items()):
        title = _text(_read_properties(file_found).get('title'))
        try:
            records = list(get_sqlite_db_records(
                file_found,
                'SELECT revision, chunk_index, serialized_commands '
                'FROM document_commands ORDER BY revision, chunk_index'))
        except sqlite3.Error as error:
            logfunc('Google Docs: could not read document_commands from '
                    f'{context.get_relative_path(file_found)}: {error}')
            continue

        segments = []
        types = []
        for _revision, _chunk_index, serialized in records:
            if not serialized:
                continue
            try:
                commands = json.loads(serialized)
            except (ValueError, TypeError) as error:
                logfunc('Google Docs: could not read a command row of '
                        f'{context.get_relative_path(file_found)}: {error}')
                continue
            if not isinstance(commands, list):
                continue
            for command in commands:
                if not isinstance(command, dict):
                    continue
                stored_type = command.get('ty')
                if stored_type not in types:
                    types.append(str(stored_type))
                if stored_type == 'is':
                    text = command.get('s')
                    if isinstance(text, str) and text:
                        segments.append(text)

        if not segments:
            continue

        # The rows are read in stored order, so joining them reproduces the order the
        # command log holds. One row per document: the storage chunks are not something an
        # examiner acts on individually.
        body = ''.join(segments)
        data_list.append((
            title,
            document_id,
            len(body),
            len(segments),
            ' | '.join(types),
            body,
            context.get_relative_path(file_found),
        ))

    data_headers = (
        'Title',
        'Document ID',
        'Characters',
        'Stored Text Segments',
        'Command Types In Document (as stored)',
        'Text',
        'Source File',
    )
    return data_headers, data_list, 'see Source File for more info'


@artifact_processor
def googleDocsDocumentMedia(context):
    data_list = []
    files = [str(f) for f in context.get_files_found()]
    containers = _docs_containers(files)
    titles = _titles_by_document(files, containers)

    for file_found in sorted(files):
        match = _DOC_MEDIA_RE.search(str(file_found).replace('\\', '/'))
        if not match:
            continue
        if not _in_docs_container(file_found, containers, context):
            continue
        account_id, outer_id, inner_id, kind, blob_name = match.groups()
        container = _container_root(file_found, '/Documents/')

        # The path names the document twice. They were equal on every tested file; log it
        # rather than reporting a column that is empty whenever the path is well formed.
        if inner_id != outer_id:
            logfunc('Google Docs: a stored media path names two different documents, '
                    f'reporting the outer one: {context.get_relative_path(file_found)}')

        media = check_in_media(file_found, blob_name)
        data_list.append((
            titles.get((container, account_id, outer_id), ''),
            outer_id,
            kind,
            blob_name,
            account_id,
            media,
            context.get_relative_path(file_found),
        ))

    data_headers = (
        'Document Title',
        'Document ID',
        'Stored Under',
        'Blob Name',
        'Account ID',
        ('Media', 'media'),
        'Source File',
    )
    return data_headers, data_list, 'see Source File for more info'


@artifact_processor
def googleDocsDocumentSync(context):
    data_list = []
    files = [str(f) for f in context.get_files_found()]
    containers = _docs_containers(files)

    for file_found in sorted(files):
        if os.path.basename(str(file_found)) != 'documentMetadata.db':
            continue
        if not _in_docs_container(file_found, containers, context):
            continue
        account = _ACCOUNT_DIR_RE.search(str(file_found).replace('\\', '/'))
        # Older stores do not carry every column: last_sync_finish_timestamp is absent on
        # the oldest tested image. Resolve the query against the file's own schema so a
        # missing column reports empty instead of failing the whole read.
        query = '''
            SELECT document_id, document_type,
                   last_server_updated_timestamp_milliseconds,
                   drive_last_server_udated_timestamp,
                   last_sync_finish_timestamp,
                   has_pending_changes, is_fast_track, needs_snapshot,
                   sync_failures, all_pending_commands_persisted,
                   jobset, resource_key
            FROM cross_document_metadata
        '''
        try:
            records = list(get_sqlite_db_records(
                file_found, null_absent_columns(file_found, query)))
        except sqlite3.Error as error:
            logfunc('Google Docs: could not read '
                    f'{context.get_relative_path(file_found)}: {error}')
            continue

        for record in records:
            (document_id, document_type, updated_ms, updated_seconds, sync_finish,
             pending, fast_track, needs_snapshot, failures, persisted,
             jobset, resource_key) = record
            data_list.append((
                _from_ms(updated_ms),
                _from_seconds(updated_seconds),
                _from_seconds(sync_finish),
                document_id,
                document_type,
                pending,
                fast_track,
                needs_snapshot,
                failures,
                persisted,
                jobset,
                resource_key,
                account.group(1) if account else '',
                context.get_relative_path(file_found),
            ))

    data_headers = (
        ('Last Server Update (ms column)', 'datetime'),
        ('Last Server Update (seconds column)', 'datetime'),
        ('Last Sync Finished', 'datetime'),
        'Document ID',
        'Document Type',
        'Has Pending Changes (as stored)',
        'Is Fast Track (as stored)',
        'Needs Snapshot (as stored)',
        'Sync Failures',
        'All Pending Commands Persisted (as stored)',
        'Jobset',
        'Resource Key',
        'Account ID',
        'Source File',
    )
    return data_headers, data_list, 'see Source File for more info'


@artifact_processor
def googleDocsCommentSync(context):
    data_list = []
    files = [str(f) for f in context.get_files_found()]
    containers = _docs_containers(files)
    titles = _titles_by_document(files, containers)

    for file_found in sorted(files):
        base = os.path.basename(str(file_found))
        if not base.startswith('comments_snapshot_') or not base.endswith('.db'):
            continue
        if not _in_docs_container(file_found, containers, context):
            continue
        container = _container_root(file_found, '/Documents/')
        account = _ACCOUNT_DIR_RE.search(str(file_found).replace('\\', '/'))
        try:
            records = list(get_sqlite_db_records(file_found, '''
                SELECT item_identifier, last_modified_date, next_sync_date,
                       resource_key
                FROM comment_items
            '''))
        except sqlite3.Error as error:
            logfunc('Google Docs: could not read '
                    f'{context.get_relative_path(file_found)}: {error}')
            continue

        for identifier, last_modified, next_sync, resource_key in records:
            stored = identifier or ''
            _kind, _, document_id = stored.partition(':')
            if not document_id:
                document_id = stored
            data_list.append((
                _from_seconds(last_modified),
                titles.get((container, account.group(1) if account else '', document_id), ''),
                document_id,
                next_sync,
                resource_key,
                account.group(1) if account else '',
                context.get_relative_path(file_found),
            ))

    data_headers = (
        ('Last Modified', 'datetime'),
        'Document Title',
        'Document ID',
        'Next Sync (as stored)',
        'Resource Key',
        'Account ID',
        'Source File',
    )
    return data_headers, data_list, 'see Source File for more info'


def _account_identities(files, containers=None):
    """Account identifier to the name, email and photo a document store recorded for it."""
    identities = {}
    for _key, path in _document_stores(files, containers).items():
        name, photo, account_id, email = _identity(_read_properties(path))
        if account_id and account_id not in identities:
            identities[account_id] = (name, email, photo)
    return identities


@artifact_processor
def googleDocsAccounts(context):
    data_list = []
    files = [str(f) for f in context.get_files_found()]
    identities = _account_identities(files, _docs_containers(files))

    for file_found in sorted(files):
        if os.path.basename(str(file_found)) != 'com.google.Docs.plist':
            continue
        plist = get_plist_file_content(file_found)
        if not isinstance(plist, dict):
            continue
        signed_in = plist.get('signed_in_user_id') or ''

        found = {}
        for key in plist:
            for prefix in _ACCOUNT_KEY_PREFIXES:
                if not key.startswith(prefix):
                    continue
                identifier = key[len(prefix):]
                # One key spelling carries a suffix after the identifier.
                identifier = identifier.split('-')[0]
                if _ACCOUNT_ID_RE.match(identifier):
                    found.setdefault(identifier, set()).add(prefix.rstrip('-:'))

        for identifier in sorted(found):
            name, email, photo = identities.get(identifier, ('', '', ''))
            data_list.append((
                identifier,
                'Yes' if identifier == signed_in else '',
                name,
                email,
                photo,
                ' | '.join(sorted(found[identifier])),
                context.get_relative_path(file_found),
            ))

    data_headers = (
        'Account ID',
        'Signed In',
        'Account Name',
        'Account Email',
        'Account Photo URL',
        'Recorded By Preference Keys',
        'Source File',
    )
    return data_headers, data_list, 'see Source File for more info'


# Keys whose value is floating point Unix seconds. Listed rather than detected, so a value
# is only converted where the call site knows the unit.
_SECOND_KEYS = (
    'PDLDatabaseOrphanFileMatcherCleanupTimestamp',
    'PDLAppGroupContainerOrphanFileMatcherCleanupTimestamp',
    'PDLLegacyOrphanFileMatcherCleanupTimestamp',
    'kSignalCrashStateTrackerBootTime',
)


@artifact_processor
def googleDocsAppState(context):
    data_list = []
    files = [str(f) for f in context.get_files_found()]

    for file_found in sorted(files):
        if os.path.basename(str(file_found)) != 'com.google.Docs.plist':
            continue
        plist = get_plist_file_content(file_found)
        if not isinstance(plist, dict):
            continue

        for key in sorted(plist):
            value = plist[key]
            converted = ''
            if isinstance(value, datetime):
                converted = _from_plist_date(value)
                stored = value.isoformat()
            elif key in _SECOND_KEYS and isinstance(value, (int, float)):
                converted = _from_seconds(value)
                stored = str(value)
            elif isinstance(value, bytes):
                stored = f'{len(value)} bytes'
            elif isinstance(value, (dict, list)):
                try:
                    stored = json.dumps(value, ensure_ascii=False, default=str)
                except (TypeError, ValueError):
                    stored = str(value)
            else:
                stored = str(value)

            data_list.append((
                converted,
                key,
                stored,
                type(value).__name__,
                context.get_relative_path(file_found),
            ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Key',
        'Value (as stored)',
        'Stored Type',
        'Source File',
    )
    return data_headers, data_list, 'see Source File for more info'


def _get(message, *path):
    """Walk a decoded protobuf by field number, returning None when a step is missing."""
    current = message
    for step in path:
        if not isinstance(current, dict):
            return None
        current = current.get(step)
        if isinstance(current, list):
            current = current[0] if current else None
    return current


def _repeated(message, field):
    """The values of a protobuf field as a list, whether or not it repeated."""
    if not isinstance(message, dict):
        return []
    value = message.get(field)
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _proto_text(value):
    """Render a protobuf string value."""
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return ''
    return value if isinstance(value, str) else ''


@artifact_processor
def googleDocsContacts(context):
    data_list = []
    files = [str(f) for f in context.get_files_found()]

    # Contacts_<number>_<account>.db under Library/Caches is a shared Google people cache
    # name and is not specific to this app. Anchor on the container: only report a cache
    # that sits beside the Google Docs preferences file, so another Google app's copy of
    # the same cache is not reported as this app's. The container set is built from this
    # artifact's own matched files, so it does not depend on artifact run order.
    docs_containers = {
        _container_root(f) for f in files
        if os.path.basename(f) == 'com.google.Docs.plist'
    }
    docs_containers.discard(None)

    for file_found in sorted(files):
        base = os.path.basename(str(file_found))
        # The pattern also matches the WAL and SHM sidecars so they travel with the
        # database. Only the database itself is opened.
        if not base.startswith('Contacts_') or not base.endswith('.db'):
            continue
        if _container_root(file_found) not in docs_containers:
            logfunc('Google Docs: skipping a contacts cache with no Google Docs preferences '
                    f'file in the same container: {context.get_relative_path(file_found)}')
            continue

        # The file name carries the account identifier after the source number.
        account_id = base[len('Contacts_'):-len('.db')]
        if '_' in account_id:
            account_id = account_id.split('_', 1)[1]

        try:
            records = list(get_sqlite_db_records(file_found, '''
                SELECT c.identifier, c.affinity, c.source, c.type, c.proto_data,
                       (SELECT group_concat(k.value, ' | ') FROM contact_lookup_keys k
                         WHERE k.contact_identifier = c.identifier AND k.value <> '')
                FROM contacts c
            '''))
        except sqlite3.Error as error:
            logfunc('Google Docs: could not read '
                    f'{context.get_relative_path(file_found)}: {error}')
            continue

        for identifier, affinity, source, ctype, blob, lookup_values in records:
            message = None
            if blob:
                try:
                    message, _ = blackboxprotobuf.decode_message(blob)
                except _PROTOBUF_ERRORS as error:
                    logfunc('Google Docs: could not decode a contact value in '
                            f'{context.get_relative_path(file_found)}: {error}')
            person = _get(message, '4') if message else None
            person = person if isinstance(person, dict) else {}

            display_name = _proto_text(_get(person, '3', '2'))
            photo_url = _proto_text(_get(person, '4', '2'))

            addresses = []
            nested_names = []
            for contact_method in _repeated(person, '10'):
                if not isinstance(contact_method, dict):
                    continue
                value = _proto_text(_get(contact_method, '2'))
                if value and value not in addresses:
                    addresses.append(value)
                nested = _proto_text(_get(contact_method, '9', '2'))
                if nested and nested not in nested_names:
                    nested_names.append(nested)

            data_list.append((
                display_name or (nested_names[0] if nested_names else ''),
                ' | '.join(addresses),
                lookup_values or '',
                photo_url,
                identifier,
                affinity,
                source,
                ctype,
                account_id,
                context.get_relative_path(file_found),
            ))

    data_headers = (
        'Display Name',
        'Addresses',
        'Lookup Keys',
        'Photo URL',
        'Contact Identifier',
        'Affinity (as stored)',
        'Source (as stored)',
        'Type (as stored)',
        'Account ID',
        'Source File',
    )
    return data_headers, data_list, 'see Source File for more info'
