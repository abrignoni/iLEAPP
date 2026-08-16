__artifacts_v2__ = {
    "iosInstallHistory": {
        "name": "iOS Install History",
        "description": "Successful operating-system install and rollback completion history",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-07-29",
        "last_update_date": "2026-08-15",
        "requirements": "none",
        "category": "Software Updates",
        "notes": (
            "The database stores date as text without a UTC offset; it is reported as device-"
            "local time. SoftwareUpdateServices limits the table to the 25 newest records. "
            "Observed operationType semantics in a reverse-engineered iOS 26.1 "
            "SoftwareUpdateServices implementation are 303 = successful rollback completed and "
            "304 = successful install completed. Unknown values are preserved and not inferred. "
            "Implementation references: recordInstallCompleted records operationType 304 and "
            "recordRollbackCompleted records 303, each on the no-error path, in "
            "https://github.com/EthanArbuckle/iPhone18-3_26.1_23B85_Restore/blob/"
            "90aa0cfe59d9682b4265e1354c8b19ec3c7823ab/"
            "System/Library/PrivateFrameworks/SoftwareUpdateServices.framework/"
            "SoftwareUpdateServices/SUSHistoryTracker.mm ; the 25-record trim is in "
            "https://github.com/EthanArbuckle/iPhone18-3_26.1_23B85_Restore/blob/"
            "90aa0cfe59d9682b4265e1354c8b19ec3c7823ab/"
            "System/Library/PrivateFrameworks/SoftwareUpdateServices.framework/"
            "SoftwareUpdateServices/SUSHistoryInstalls.mm"
        ),
        "paths": (
            "*/private/var/containers/Data/System/*/history/installHistory.db*",
            "*/private/var/containers/Data/System/*/history/installHistory.db-*",
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "device-mobile-up",
        "sample_data": {},
    }
}

from scripts.ilapfuncs import (
    artifact_processor,
    does_table_exist_in_db,
    get_sqlite_db_records,
)


_OPERATION_TYPES = {
    303: "Successful rollback completed",
    304: "Successful install completed",
}


@artifact_processor
def iosInstallHistory(context):
    data_headers = (
        ("Timestamp (Device Local, No Offset)", "datetime"),
        "Record ID",
        "Operation",
        "Operation Type",
        "Update Name",
        "Build",
        "Source File",
    )
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith("installHistory.db"):
            continue
        if not does_table_exist_in_db(file_found, "logs"):
            continue

        relative_path = context.get_relative_path(file_found)
        query = """
            SELECT date, id, operationType, name, build
            FROM logs
            ORDER BY date, id
        """
        for row in get_sqlite_db_records(file_found, query):
            operation_type = row[2]
            operation = _OPERATION_TYPES.get(
                operation_type, f"Unknown operation ({operation_type})"
            )
            data_list.append(
                (row[0], row[1], operation, operation_type, row[3], row[4], relative_path)
            )
        sources.append(relative_path)

    return data_headers, data_list, "\n".join(dict.fromkeys(sources))
