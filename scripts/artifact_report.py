import html
import os
import sys
from scripts.html_parts import *
#from scripts.ilapfuncs import is_platform_windows
from scripts.version_info import leapp_version

# Rows above which write_artifact_data_table leaves the table off the page and writes a
# notice pointing at the LAVA database and the TSV export instead. Measured 2026-09-19 on
# a 16-column messages page in Chromium: 25,000 rows were usable 5.9 s after opening,
# 50,000 in 11.3 s and 100,000 in 25.8 s with the browser holding 1.7 GB for the page; at
# 150,000 the table script failed with "Maximum call stack size exceeded" inside jQuery,
# the loading spinner never cleared and the browser held 9 GB. The main script sets this
# from --html_row_limit; 0 turns the limit off.
HTML_TABLE_ROW_LIMIT = 50000

LAVA_DATABASE_LOCATION = ('the LAVA database (<code>_lava_artifacts.db</code> in the report '
                          'folder, opened with LAVA)')


def set_html_row_limit(limit):
    """Set the row limit for HTML tables; 0 turns it off."""
    global HTML_TABLE_ROW_LIMIT  # pylint: disable=global-statement
    HTML_TABLE_ROW_LIMIT = max(0, int(limit))


def tsv_export_location(tsv_name):
    """Describe an artifact's TSV export for the held-back table notice."""
    return f'the TSV export <code>_TSV Exports/{html.escape(tsv_name)}.tsv</code>'


def table_held_back_notice(num_entries, row_limit, full_data_locations=None):
    """The notice written in place of a table that exceeds the row limit."""
    if full_data_locations:
        where = ' and in '.join(full_data_locations)
    else:
        where = "the report's other outputs, such as the LAVA database and the TSV export"
    return (f'<p class="note note-warning">This table has {num_entries:,} rows, above the '
            f'{row_limit:,}-row limit for HTML report pages, so it is not shown here. The '
            f'complete rows are in {where}. Run with <code>--html_row_limit 0</code> to write '
            f'it anyway.</p>')


class ArtifactHtmlReport:

    def __init__(self, artifact_name, artifact_category=''):
        self.report_file = None
        self.report_file_path = ''
        self.script_code = ''
        self.artifact_name = artifact_name
        self.artifact_category = artifact_category # unused

    def __del__(self):
        if self.report_file:
            self.end_artifact_report()

    def start_artifact_report(self, report_folder, artifact_file_name, artifact_description=''):
        '''Creates the report HTML file and writes the artifact name as a heading'''
        # artifact_file_name =  artifact_file_name.replace(" ", "_") # Replace " " with "_" in HTML filenames
        self.report_file = open(os.path.join(report_folder, f'{artifact_file_name}.temphtml'), 'w', encoding='utf8')
        self.report_file.write(page_header.format(f'iLEAPP - {self.artifact_name} report'))
        self.report_file.write(body_start.format(f'iLEAPP {leapp_version}'))
        self.report_file.write(body_sidebar_setup)
        self.report_file.write(body_sidebar_dynamic_data_placeholder) # placeholder for sidebar data
        self.report_file.write(body_sidebar_trailer)
        self.report_file.write(body_main_header)
        self.report_file.write(body_main_data_title.format(f'{self.artifact_name} report', artifact_description))
        self.report_file.write(body_spinner) # Spinner till data finishes loading
        #self.report_file.write(body_infinite_loading_bar) # Not working!

    def add_script(self, script=''):
        '''Adds a default script or the script supplied'''
        if script:
            self.script_code += script + nav_bar_script_footer
        else:
            self.script_code += default_responsive_table_script + nav_bar_script_footer

    def write_artifact_data_table(
        self,
        data_headers,
        data_list,
        source_path,
        write_total=True,
        write_location=True,
        html_escape=True,
        cols_repeated_at_bottom=True,
        table_responsive=True,
        table_style='',
        table_id='dtBasicExample',
        html_no_escape=[],
        row_limit=None,
        full_data_locations=None
    ):
        ''' Writes info about data, then writes the table to html file
            Parameters
            ----------
            data_headers   : List/Tuple of table column names

            data_list      : List/Tuple of lists/tuples which contain rows of data

            source_path    : Source path of data

            write_total    : Toggles whether to write out a line of total rows written

            write_location : Toggles whether to write the location of data source

            html_escape    : If True (default), then html special characters are encoded

            cols_repeated_at_bottom : If True (default), then col names are also at the bottom of the table

            table_responsive : If True (default), div class is table_responsive

            table_style    : Specify table style like "width: 100%;"

            table_id       : Specify an identifier string, which will be referenced in javascript

            html_no_escape  : if html_escape=True, list of columns not to escape

            row_limit      : Rows above which the table is left off the page and a notice
                             written instead; None uses HTML_TABLE_ROW_LIMIT, 0 means no limit

            full_data_locations : HTML fragments naming where the complete rows are, for
                             the notice (see LAVA_DATABASE_LOCATION and tsv_export_location)

            Returns True when the table was held back, False when it was written.
        '''
        if (not self.report_file):
            raise ValueError('Output report file is closed/unavailable!')

        num_entries = len(data_list)
        if write_total:
            self.write_minor_header(f'Total number of entries: {num_entries}', 'h6')
        if write_location:
            if sys.platform == 'win32':
                source_path = source_path.replace('/', '\\')
            if source_path.startswith('\\\\?\\'):
                source_path = source_path[4:]
            self.write_lead_text(f'{self.artifact_name} located at: {source_path}')

        self.report_file.write('<br />')

        if row_limit is None:
            row_limit = HTML_TABLE_ROW_LIMIT
        if row_limit and num_entries > row_limit:
            self.report_file.write(table_held_back_notice(num_entries, row_limit, full_data_locations))
            return True

        if table_responsive:
            self.report_file.write("<div class='table-responsive'>")

        table_head = '<table id="{}" class="table table-striped table-bordered table-xsm" cellspacing="0" {}>' \
                     '<thead>'.format(table_id, (f'style="{table_style}"') if table_style else '')
        self.report_file.write(table_head)
        self.report_file.write(
            '<tr>' + ''.join(('<th class="th-sm">{}</th>'.format(html.escape(str(x))) for x in data_headers)) + '</tr>')
        self.report_file.write('</thead><tbody>')

        if html_escape:
            for row in data_list:
                if html_no_escape:
                    self.report_file.write('<tr>' + ''.join(('<td>{}</td>'.format(html.escape(
                        str(x) if x not in [None, 'N/A'] else '')) if h not in html_no_escape else '<td>{}</td>'.format(
                        str(x) if x not in [None, 'N/A'] else '') for x, h in zip(row, data_headers))) + '</tr>')
                else:
                    self.report_file.write('<tr>' + ''.join(
                        ('<td>{}</td>'.format(html.escape(str(x) if x not in [None, 'N/A'] else '')) for x in
                         row)) + '</tr>')
        else:
            for row in data_list:
                self.report_file.write('<tr>' + ''.join( ('<td>{}</td>'.format(str(x) if x not in [None, 'N/A'] else '') for x in row) ) + '</tr>')
        
        self.report_file.write('</tbody>')
        if cols_repeated_at_bottom:
            self.report_file.write('<tfoot><tr>' + ''.join(
                ('<th>{}</th>'.format(html.escape(str(x))) for x in data_headers)) + '</tr></tfoot>')
        self.report_file.write('</table>')
        if table_responsive:
            self.report_file.write("</div>")
        return False

    def add_section_heading(self, heading, size='h2'):
        heading = html.escape(heading)
        data = '<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">' \
               '    <{0} class="{0}">{1}</{0}>' \
               '</div>'
        self.report_file.write(data.format(size, heading))

    def write_minor_header(self, heading, heading_tag=''):
        heading = html.escape(heading)
        if heading_tag:
            self.report_file.write(f'<{heading_tag}>{heading}</{heading_tag}>')
        else:
            self.report_file.write(f'<h3 class="h3">{heading}</h3>')

    def write_lead_text(self, text):
        self.report_file.write(f'<p class="lead">{text}</p>')

    def write_raw_html(self, code):
        self.report_file.write(code)

    def end_artifact_report(self):
        if self.report_file:
            self.report_file.write(body_main_trailer + body_end + self.script_code + page_footer)
            self.report_file.close()
            self.report_file = None

        
