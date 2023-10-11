import plistlib
# use to get iOS version -> iOSversion = scripts.artifacts.artGlobals.versionf
# import scripts.artifacts.artGlobals
# from packaging import version  # use to search per version number


from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, is_platform_windows


def get_iconsScreen(files_found, report_folder, seeker, wrap_text, timezone_offset):
    # iOSversion = scripts.artifacts.artGlobals.versionf
    # if version.parse(iOSversion) >= version.parse("14"):
    #     logfunc(f'iOS Screen artifact not compatible with iOS {iOSversion}')
    #     return

    data_list = []
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        plist = plistlib.load(fp)
        for key, val in plist.items():
            if key == "buttonBar":
                bbar = val
            elif key == "iconLists":
                icon = val

        for x in range(0, len(icon)):
            page = icon[x]
            htmlstring = (f"<table><tr>")
            htmlstring = htmlstring + \
                (f'<td> Icons screen #{x}</td></tr><tr><td>') + \
                (f'<div style="display: grid;grid-template-columns: repeat(4, 1fr);grid-gap: 2px;">')
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
        htmlstring = (
            f'<table><tr> <td colspan="4"> Icons bottom bar</td></tr><tr>')
        for x in range(0, len(bbar)):
            htmlstring = htmlstring + (f"<td width = 25%>{bbar[x]}</td>")
        htmlstring = htmlstring + ("</tr></table>")
        data_list.append((htmlstring,))

        logfunc("Screens: " + str(len(icon)))

        report = ArtifactHtmlReport(f'Apps per screen')
        report.start_artifact_report(report_folder, f'Apps per screen')
        report.add_script()
        data_headers = ((f'Apps per Screens',))
        report.write_artifact_data_table(
            data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()


__artifacts__ = {
    "iconsScreen": (
        "iOS Screens",
        ('**/SpringBoard/IconState.plist'),
        get_iconsScreen)
}
