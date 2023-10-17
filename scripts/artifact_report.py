import html
import os
from scripts.html_parts import *
from scripts.ilapfuncs import is_platform_windows
from scripts.version_info import aleapp_version

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
        self.report_file = open(os.path.join(report_folder, f'{artifact_file_name}.temphtml'), 'w', encoding='utf8')
        self.report_file.write(page_header.format(f'iLEAPP - {self.artifact_name} report'))
        self.report_file.write(body_start.format(f'iLEAPP {aleapp_version}'))
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
        html_no_escape=[]
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
        '''
        if (not self.report_file):
            raise ValueError('Output report file is closed/unavailable!')

        num_entries = len(data_list)
        if write_total:
            self.write_minor_header(f'Total number of entries: {num_entries}', 'h6')
        if write_location:
            if is_platform_windows():
                source_path = source_path.replace('/', '\\')
            if source_path.startswith('\\\\?\\'):
                source_path = source_path[4:]
            self.write_lead_text(f'{self.artifact_name} located at: {source_path}')

        self.report_file.write('<br />')

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

        
