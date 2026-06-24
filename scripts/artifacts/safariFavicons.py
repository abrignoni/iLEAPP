__artifacts_v2__ = {
    "safariFavicons": {
        "name": "Safari Browser - Favicons",
        "description": "Safari favicon cache entries (page URL, icon URL, dimensions)",
        "author": "",
        "version": "2.0",
        "date": "2026-06-23",
        "requirements": "none",
        "category": "Safari Browser",
        "notes": "",
        "paths": ('*/Containers/Data/Application/*/Library/Image Cache/Favicons/Favicons.db*',),
        "output_types": "standard",
        "artifact_icon": "image"
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records


@artifact_processor
def safariFavicons(context):
    data_headers = (('Timestamp', 'datetime'), 'Page URL', 'Icon URL', 'Width', 'Height',
                    'Generated Representations?')
    data_list = []

    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('Favicons.db'):
            source_path = file_found
            break
    if not source_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        datetime('2001-01-01', "timestamp" || ' seconds'),
        page_url.url,
        icon_info.url,
        icon_info.width,
        icon_info.height,
        icon_info.has_generated_representations
    FROM icon_info
    LEFT JOIN page_url ON icon_info.uuid = page_url.uuid
    '''
    for row in get_sqlite_db_records(source_path, query):
        data_list.append(tuple(row))

    return data_headers, data_list, context.get_relative_path(source_path)
