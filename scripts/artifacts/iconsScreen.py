import plistlib

from scripts.ilapfuncs import artifact_processor, logfunc


@artifact_processor
def get_iconsScreen(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        plist = plistlib.load(fp)
        bbar = []
        icon = []
        for key, val in plist.items():
            if key == "buttonBar":
                bbar = val
            elif key == "iconLists":
                icon = val

        for x in range(0, len(icon)):
            page = icon[x]
            htmlstring = "<table><tr>"
            htmlstring = htmlstring + \
                (f'<td> Icons screen #{x}</td></tr><tr><td>') + \
                '<div style="display: grid;grid-template-columns: repeat(4, 1fr);grid-gap: 2px;">'
            for y in range(0, len(page)):
                rows = page[y]
                style = 'border: 1px solid grey;padding: 10px;max-height: 235px; overflow-y: scroll;'
                grid_column = ''
                grid_row = ''
                if isinstance(rows, dict):
                    var = rows
                    if 'listType' in var.keys():
                        foldername = var['displayName']
                        rows = ''
                        bundlesinfolder = var['iconLists']
                        total_app = 0
                        for items in bundlesinfolder:
                            for bundle in items:
                                rows = rows + '<br>' + bundle
                                total_app += 1
                        rows = (f'Folder: {foldername} ({total_app} Apps)') + rows
                    elif 'gridSize' in var.keys():
                        grid_size = var['gridSize']
                        grid_column = 'grid-column: span 2;' if grid_size == 'small' else 'grid-column: span 4;'
                        grid_row = 'grid-row: span 4;' if grid_size == 'large' else 'grid-row: span 2;'
                        if 'elementType' in var.keys():
                            widget_identifier = var['widgetIdentifier'] if var[
                                'elementType'] == 'widget' else var['elementType']
                            rows = (f'Widget<br>{widget_identifier}')
                        elif 'elements' in var.keys():
                            rows = 'Stack:'
                            widgets_in_stack = var['elements']
                            for widget in widgets_in_stack:
                                widget_identifier = widget['widgetIdentifier'] if widget[
                                    'elementType'] == 'widget' else widget['elementType']
                                rows = rows + '<br>' + widget_identifier
                        else:
                            rows = ''

                htmlstring = htmlstring + \
                    (f'<div style="{style}{grid_column}{grid_row}">{rows}</div>')
            htmlstring = htmlstring + ("</div></td></tr></table>")
            data_list.append((htmlstring,))

        htmlstring = ''
        htmlstring = '<table><tr> <td colspan="4"> Icons bottom bar</td></tr><tr>'
        for x in range(0, len(bbar)):
            htmlstring = htmlstring + (f"<td width = 25%>{bbar[x]}</td>")
        htmlstring = htmlstring + ("</tr></table>")
        data_list.append((htmlstring,))

        logfunc("Screens: " + str(len(icon)))

    data_headers = ('Apps per Screens',)
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_iconsScreen": {
        "name": "Apps per Screen",
        "description": "Home screen app layout and widget placement.",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "iOS Screens",
        "notes": "",
        "paths": ('**/SpringBoard/IconState.plist',),
        "output_types": ["html"],
        "artifact_icon": "grid",
        "html_columns": ["Apps per Screens"]
    }
}
