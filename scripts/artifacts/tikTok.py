from os.path import dirname, join, basename
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, attach_sqlite_db_readonly


def get_tikTok(files_found, report_folder, seeker, wrap_text, timezone_offset):

    aweme_im_db_path = None
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('AwemeIM.db'):
            aweme_im_db_path = file_found
            logfunc("FOUND AwemeIM.db")
            break

    if not aweme_im_db_path:
        logfunc("AwemeIM.db not found in files_found. TikTok artifact cannot proceed.")
        return

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('db.sqlite'):
            dir_path = dirname(file_found)
            account_id = basename(dir_path)
            data_list = []
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            try:
                attach_query = attach_sqlite_db_readonly(aweme_im_db_path, 'AwemeIM')
                cursor.execute(attach_query)

                cursor.execute("SELECT name FROM AwemeIM.sqlite_master WHERE type='table' and name like 'AwemeContacts%';")
                table_results = cursor.fetchall()
                contacts_tables = [row[0] for row in table_results]

                if not contacts_tables:
                    logfunc(f"No contacts tables found in AwemeIM.db for account {account_id}, skipping TikTok messages for this db.")
                else:
                    contacts_union_parts = []
                    for table in contacts_tables:
                        contacts_union_parts.append(f'SELECT uid, customid, nickname, url1 FROM {table}')
                    contacts_union_query = ' UNION ALL '.join(contacts_union_parts)

                    query = f'''
                    WITH UniqueContacts AS (
                        {contacts_union_query}
                    )
                    SELECT
                        datetime(localcreatedat, 'unixepoch') as Local_Create_Time,
                        sender,
                        customid,
                        nickname,
                        CASE
                            WHEN json_valid(content) THEN json_extract(content, '$.text')
                        END message,
                        CASE
                            WHEN json_valid(content) THEN json_extract(content, '$.tips')
                        END localresponse,
                        CASE
                            WHEN json_valid(content) THEN json_extract(content,'$.display_name')
                        END links_display_name,
                        CASE
                            WHEN json_valid(content) THEN json_extract(content, '$.url.url_list[0]')
                        END links_gifs_urls,
                        case
                            when servercreatedat > 1 then datetime(servercreatedat, 'unixepoch')
                            else servercreatedat
                        end servercreatedat,
                        url1 as profilepicURL
                    FROM TIMMessageORM
                    LEFT JOIN UniqueContacts ON UniqueContacts.uid = sender
                    ORDER BY Local_Create_Time
                    '''

                    try:
                        cursor.execute(query)
                        all_rows = cursor.fetchall()
                        logfunc(f'TikTok Messages - all rows length {len(all_rows)}')
                    except sqlite3.OperationalError as e:
                        logfunc(f"[!] Error executing TikTok Messages query for {account_id}: {e}")
                        all_rows = []

                    if len(all_rows) > 0:
                        for row in all_rows:
                            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))

                report = ArtifactHtmlReport(f'TikTok Messages - {account_id}')
                description = 'Note that messages may appear multiple times due to the way contacts are duplicated ' \
                            'in multiple tables'
                report.start_artifact_report(report_folder, f'TikTok Messages - {account_id}', description)
                report.add_script()
                data_headers = ('Timestamp','Sender','Custom ID','Nickname','Message', 'Local Response','Link GIF Name','Link GIF URL','Server Create Timestamps','Profile Pic URL')
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()

                tsvname = 'TikTok Messages'
                tsv(report_folder, data_headers, data_list, tsvname)

                tlactivity = 'TikTok Messages'
                timeline(report_folder, tlactivity, data_list, data_headers)

            except Exception as e:
                logfunc(f"[!] Unexpected error processing db.sqlite {file_found}: {e}")
            finally:
                db.close()

    contact_db = open_sqlite_db_readonly(aweme_im_db_path)
    contact_cursor = contact_db.cursor()
    data_list1 = []

    try:
        contact_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' and name like 'AwemeContacts%';")
        contact_table_results = contact_cursor.fetchall()
        contact_tables = [row[0] for row in contact_table_results]

        if not contact_tables:
            logfunc('No TikTok Contacts tables available in AwemeIM.db')
        else:
            contacts_queries = []
            for table in contact_tables:
                contacts_queries.append(f'''
                select
                    case
                        when latestchattimestamp > 1 then datetime(latestchattimestamp, 'unixepoch')
                        else latestchattimestamp
                    end latestchattimestamp,
                    nickname,
                    uid,
                    customID,
                    url1,
                    '{table}'
                from {table}
                ''')

            contacts_query = ' UNION ALL '.join(contacts_queries)

            try:
                contact_cursor.execute(contacts_query)
                all_rows1 = contact_cursor.fetchall()
            except sqlite3.OperationalError as e:
                logfunc(f"[!] Error executing TikTok Contacts query: {e}")
                all_rows1 = []

            if len(all_rows1) > 0:
                description = 'Timestamp corresponds to latest chat if available'
                for row in all_rows1:
                    data_list1.append((row[0], row[1], row[2], row[3], row[4], row[5]))

                report = ArtifactHtmlReport('TikTok Contacts')
                report.start_artifact_report(report_folder, 'TikTok Contacts', description)
                report.add_script()
                data_headers1 = ('Timestamp','Nickname','Unique ID','Custom ID','URL', 'Table')
                report.write_artifact_data_table(data_headers1, data_list1, aweme_im_db_path)
                report.end_artifact_report()

                tsvname = 'TikTok Contacts'
                tsv(report_folder, data_headers1, data_list1, tsvname)

                tlactivity = 'TikTok Last Contact'
                timeline(report_folder, tlactivity, data_list1, data_headers1)
            else:
                logfunc('No TikTok Contacts data found in tables.')

    except Exception as e:
        logfunc(f"[!] Unexpected error processing AwemeIM.db for contacts: {e}")
    finally:
        contact_db.close()

__artifacts__ = {
    "tikTok": (
        "TikTok",
        ('*/Application/*/Library/Application Support/ChatFiles/*/db.sqlite*','*AwemeIM.db*'),
        get_tikTok)
}