__artifacts_v2__ = {
    "skg_archive": {
        "name": "SKG Archive",
        "description": "Parses SKG Archive Records",
        "author": "@JFHyla",
        "version": "0.1",
        "date": "2024-12-02",
        "requirements": "mdplistlib",
        "category": "Spotlight",
        "notes": "",
        "paths": (
            '*/CoreSpotlight/SpotlightKnowledge/index.V2/keyphrases/NSFileProtectionComplete/skg_archive.V2.*',
            '*/CoreSpotlight/SpotlightKnowledge/index.V2/archives/NSFileProtectionComplete/skg_archive.V2.*',
        ),
        "output_types": "standard"
    }
}

from scripts.ilapfuncs import artifact_processor, logfunc
import mdplist
import nska_deserialize as nd
import os
from collections import defaultdict
from pathlib import Path

@artifact_processor
def skg_archive(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_list = []
    dedupe = 0
    grouped_files = defaultdict(list)

    for file_found in files_found:
        path = Path(file_found)
        grouped_files[path.parent].append(path.name)

        sk_archive = nd.deserialize_plist(file_found)
        for item in sk_archive:

            d = mdplist.loads(item['attributes']['container'])
            record  = (
                d[2].get('_kMDItemInterestingDate'),
                d[2].get('kMDItemContentCreationDate'),
                d[2].get('_kMDItemBundleID'),
                d[2].get('_kMDItemOID'),
                d[2].get('_kMDItemExternalID'),
                d[2].get('_kMDItemDomainIdentifier'),
                d[2].get('_kMDItemSnippet'),
                d[2].get('kMDItemAuthorEmailAddresses'),
                d[2].get('kMDItemAuthors'),
                d[2].get('kMDItemContentType'),
                d[2].get('kMDItemRecipientEmailAddresses'),
                str(d)
            )

            if record not in data_list:
                data_list.append(record)
            else:
                dedupe += 1

    #Build list of report files:
    result_parts = []
    for parent, filenames in grouped_files.items():
        formatted_group = f"{parent}/{filenames[0]}" if len(filenames) == 1 else f"{parent}/" + ", ".join(filenames)
        result_parts.append(formatted_group)

    report_files =  ", ".join(result_parts)

    logfunc(f'{dedupe} SKG Archive records deduplicated')

    data_headers = (
         ('_kMDItemInterestingDate', 'datetime'), ('kMDItemContentCreationDate', 'datetime'), '_kMDItemBundleID', '_kMDItemOID', '_kMDItemExternalID', '_kMDItemDomainIdentifier',
         '_kMDItemSnippet', 'kMDItemAuthorEmailAddresses', 'kMDItemAuthors', 'kMDItemContentType', 'kMDItemRecipientEmailAddresses', 'Raw Data')
    return data_headers, data_list, report_files

