"""
Extracts Voice Memo recordings and metadata from iOS devices.
"""

__artifacts_v2__ = {
    "voice_memos": {
        "name": "Voice Memos",
        "description": "Extracts Voice Memo recordings and metadata.",
        "author": "@Anna-Mariya Mateyna - @Johann-PLW",
        "creation_date": "2020-12-21",
        "last_update_date": "2026-07-15",
        "requirements": "none",
        "category": "Audio",
        "notes": "2026-07-14 Update: Rewriting the artifact to use the recording database and fix issue #1717.",
        "paths": (
            "*/Recordings/*Recordings.db*",
            "*/Recordings/*.m4a",
            "*/Recordings/*.qta",
            ),
        "output_types": "standard",
        "artifact_icon": "microphone",
        "sample_data": {
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | com.apple.VoiceMemos | 3 rows",
            "otto_ios17": "iOS 17.5.1 | com.apple.VoiceMemos | 3 rows",
            "abe_ios16": "iOS 16.5 | 30 rows",
        }
    }
}

from scripts.ilapfuncs import (
    artifact_processor, get_file_path, get_sqlite_db_records,
    convert_cocoa_core_data_ts_to_utc, check_in_media
)


@artifact_processor
def voice_memos(context):
    """See artifact description"""
    files_found = context.get_files_found()
    cloud_recordings_source_path = get_file_path(files_found, "CloudRecordings.db")
    recordings_source_path = get_file_path(files_found, "Recordings.db")

    source_path = ""
    query = ""
    data_list = []

    if cloud_recordings_source_path:
        source_path = cloud_recordings_source_path
        query = """
        SELECT
            ZDATE,
            time(ZDURATION, 'unixepoch') as ZDURATION,
            ZCUSTOMLABELFORSORTING,
            ZPATH
        FROM ZCLOUDRECORDING
        """
    elif recordings_source_path:
        source_path = recordings_source_path
        query = """
        SELECT
            ZDATE,
            time(ZDURATION, 'unixepoch') as ZDURATION,
            ZCUSTOMLABEL,
            ZPATH
        FROM ZRECORDING
        """

    if source_path:
        db_records = get_sqlite_db_records(source_path, query)
        for record in db_records:
            timestamp = convert_cocoa_core_data_ts_to_utc(record["ZDATE"])
            if record["ZPATH"]:
                storage = "On the device"
                audio_file = check_in_media(record["ZPATH"])
            else:
                storage = "In iCloud"
                audio_file = ""
            data_list.append((timestamp, record["ZDURATION"], record["ZCUSTOMLABELFORSORTING"],
                              storage, audio_file))

    data_headers = (
        ("Date and time", "datetime"), "Duration", "Title", "Storage", ("Audio File", "media"))

    return data_headers, data_list, source_path
