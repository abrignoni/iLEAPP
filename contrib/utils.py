import sqlite3


def get_sql_output(query, db_path):
    """
    Returns back results of SQL query on being passed a query.

    Args:
        query (str): a valid sql query as a string
        db_path (str): path to connect to SQLite database
    """
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows


def write_html_to_file(file_path, rows, db_path, category, additional_cols=None):
    """
    """
    with open(file_path, "w", encoding="utf8") as f:
        f.write("<html><body>")
        f.write(f"<h2> {category} report</h2>")
        f.write(f"{category} entries: {len(rows)}<br>")
        f.write(f"{category} located at: {db_path}<br>")
        f.write(
            "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
        )
        f.write("<br/>")
        f.write("")
        f.write(f'<table class="table sticky">')

        base_table_header_template = f"<tr><th>Timestamp</th><th>Key</th><th>Value</th>"
        template = base_table_header_template

        if additional_cols:
            for col in additional_cols:
                template = f"{template}<th>{col}</th>"

        template = f"{template}</tr>"
        f.write(f"{template}")

        for row in rows:
            base_table_row_template = (
                f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td>"
            )
            if not additional_cols:
                f.write(f"{base_table_row_template}</tr>")
            else:
                template = base_table_row_template
                for ind in range(len(additional_cols)):
                    template = f"{template}<td>{row[(3 + ind)]}</td>"
                f.write(f"{template}</tr>")

        f.write(f"</table></body></html>")
    return
