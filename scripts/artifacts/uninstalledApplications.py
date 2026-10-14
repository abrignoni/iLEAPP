__artifacts_v2__ = {
    "uninstalled_applications_plist": {
        "name": "Apps - Uninstalled Applications Plist",
        "description": (
            "Bundle identifiers and dates recorded in "
            "/private/var/installd/Library/MobileInstallation/UninstalledApplications.plist, "
            "a property list whose keys are bundle identifiers and whose values are dates."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-25",
        "last_update_date": "2026-08-25",
        "requirements": "none",
        "category": "Mobile Installation Logs",
        "notes": (
            "The file holds one date per bundle identifier, so a bundle that was installed and "
            "removed more than once carries only the date recorded against it here. The dates are "
            "read from the property list's own date type, which is stored in UTC. The file is not "
            "present on every device: it was found on two of the twenty-four tested images. Absence "
            "of the file, or of a bundle identifier within it, is absence of this source and is not "
            "evidence that no application was removed."
        ),
        "paths": ('*/installd/Library/MobileInstallation/UninstalledApplications.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "trash-2",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | 5 rows",
            "otto_ios17": "iOS 17.5.1 | 5 rows",
        }
    }
}

import datetime
import plistlib

from scripts.ilapfuncs import artifact_processor, logfunc


@artifact_processor
def uninstalled_applications_plist(context):
    data_headers = (('Date', 'datetime'), 'Bundle ID')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        try:
            with open(file_found, 'rb') as fp:
                parsed = plistlib.load(fp)
        except (OSError, plistlib.InvalidFileException, ValueError) as ex:
            logfunc(f'Could not read {context.get_relative_path(file_found)}: {ex}')
            continue

        if not isinstance(parsed, dict):
            logfunc(f'Unexpected top-level type in {context.get_relative_path(file_found)}: '
                    f'{type(parsed).__name__}')
            continue

        rel = context.get_relative_path(file_found)
        if rel not in sources:
            sources.append(rel)

        for bundle_id, value in parsed.items():
            if isinstance(value, datetime.datetime):
                # plistlib returns the property list date type as a naive UTC datetime.
                value = value.replace(tzinfo=datetime.timezone.utc)
            data_list.append((value, bundle_id))

    return data_headers, data_list, '\n'.join(sources)
