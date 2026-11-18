__artifacts_v2__ = {
    "appGrouplisting": {
        "name": "Bundle ID by AppGroup & PluginKit IDs",
        "description": "Identifier (MCMMetadataIdentifier) recorded in each container's metadata "
                       "plist under Shared/AppGroup and Data/PluginKitPlugin, with the container "
                       "directory name and the folder that holds it. Each file is named "
                       ".com.apple.mobile_container_manager.metadata.plist. When an AppGroup "
                       "container has no readable metadata plist but holds "
                       "Library/Preferences/group.<id>.plist, the identifier is that file name "
                       "without the .plist extension.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2020-09-22",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "For rows whose Identifier Source is Container metadata plist, the Bundle ID column "
                 "holds the MCMMetadataIdentifier value as stored, which can be empty. The Bundle ID "
                 "header is historical: for AppGroup rows the column holds a group identifier. "
                 "Identifier Source says where each identifier came from: the container metadata "
                 "plist, or, for an AppGroup container with no readable metadata plist, the name of "
                 "its Library/Preferences/group.<id>.plist file without the .plist extension (the "
                 "group. prefix is kept). In two iOS 26 extractions, the preferences file name "
                 "without .plist equalled the plist identifier in every AppGroup container that had "
                 "both files (49 of 49 containers and 32 of 32 containers). This is an observation "
                 "from those two extractions; no source for the naming was read. Only AppGroup "
                 "containers holding such a preferences file can be listed without the metadata "
                 "plist: on a copy of one of those extractions with all 166 AppGroup metadata plists "
                 "removed, 49 of the 166 were listed. An AppGroup container with neither file is not "
                 "listed, and neither is a PluginKitPlugin container without its metadata plist "
                 "(source-read, not seen missing in either extraction). This artifact does not "
                 "report which app owns a container.",
        "paths": (
            '*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist', 
            '*/Containers/Data/PluginKitPlugin/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/Containers/Shared/AppGroup/*/Library/Preferences/group.*.plist'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "package",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 439 rows",
            "dexter_ios18": "iOS 18.3.2 | 1111 rows",
            "felix_ios17": "iOS 17.6.1 | 829 rows",
            "fsfull002_ios17": "iOS 17.1 | 780 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1085 rows",
            "iphone11_ios17": "iOS 17.3 | 950 rows",
            "iphone12_ios18": "iOS 18.7 | 1066 rows",
            "iphone14plus_ios18": "iOS 18.0 | 901 rows",
            "otto_ios17": "iOS 17.5.1 | 892 rows",
            "abe_ios16": "iOS 16.5 | 827 rows",
            "hc_ios26": "iOS 26.5.2 | 1225 rows",
            "felix23_ios16": "iOS 16.5 | 674 rows",
            "hickman_ios13": "iOS 13.3.1 | 458 rows",
            "hickman_ios14": "iOS 14.3 | 521 rows",
            "jess_ios15": "iOS 15.0.2 | 490 rows",
            "magnet_ios16": "iOS 16.1.1 | 685 rows",
        }
    }
}

import pathlib
from scripts.ilapfuncs import artifact_processor, get_plist_file_content

METADATA_PLIST = '.com.apple.mobile_container_manager.metadata.plist'
FROM_METADATA = 'Container metadata plist'
FROM_PREFERENCES = 'Group preferences file name'


def _group_preferences_container(file_found):
    """The AppGroup container folder if file_found is Library/Preferences/group.*.plist
    directly inside one, else None. The seeker's * crosses /, so the shape is re-checked."""
    p = pathlib.Path(file_found)
    if (p.parent.name == 'Preferences' and p.parents[1].name == 'Library'
            and p.parents[3].name == 'AppGroup' and p.parents[4].name == 'Shared'
            and p.name.startswith('group.') and p.suffix == '.plist'):
        return p.parents[2]
    return None


@artifact_processor
def appGrouplisting(context):
    source_paths = set()
    data_headers = ('Bundle ID', 'Type', 'Directory GUID', 'Path', 'Identifier Source')

    results = context.create_artifact_result(
        headers=data_headers,
        estimated_row_count=len(context.get_files_found()),
    )

    files = [str(f) for f in context.get_files_found()]
    listed = set()  # containers already listed from their metadata plist
    for file_found in files:
        if pathlib.Path(file_found).name != METADATA_PLIST:
            continue
        plist = get_plist_file_content(file_found)
        # Check if plist is a valid parseable object
        if not plist or not isinstance(plist, dict):
            continue
        source_paths.add(file_found)
        bundleid = plist['MCMMetadataIdentifier']

        p = pathlib.Path(file_found)
        listed.add(p.parent)
        appgroupid = p.parent.name
        fileloc = context.get_relative_path(str(p.parents[1]))
        typedir = str(p.parents[1].name)

        results.add_row((bundleid, typedir, appgroupid, fileloc, FROM_METADATA))

    # AppGroup containers whose metadata plist is not in the extraction: the identifier
    # is the group preferences file's name. Only one such file per container is used.
    for file_found in sorted(files):
        container = _group_preferences_container(file_found)
        if container is None or container in listed:
            continue
        listed.add(container)
        source_paths.add(file_found)
        fileloc = context.get_relative_path(str(container.parent))
        results.add_row((pathlib.Path(file_found).stem, container.parent.name,
                         container.name, fileloc, FROM_PREFERENCES))

    results.set_source_path('\n'.join(sorted(source_paths)))
    return results
