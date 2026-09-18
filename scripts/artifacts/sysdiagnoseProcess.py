from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.html_safe import esc

__artifacts_v2__ = {
    "sysdiagnoseProcess": {
        "name": "Sysdiagnose Process",
        "description": "Hierarchical view of processes (parent/child tree) extracted from ps.txt / ps_thread.txt",
        "author": "@mathisdesaulty",
        "creation_date": "2026-09-17",
        "last_update_date": "2026-09-17",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "",
        "paths": ('*/ps.txt', '*/ps_thread.txt'),
        "output_types": "html",
        "html_columns": ["Process Hierarchy Tree"],
        "artifact_icon": "list-tree"
    }
}

@artifact_processor
def sysdiagnoseProcess(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    source_file = ''

    for file_found in files_found:
        if 'ps.txt' in file_found or 'ps_thread.txt' in file_found:
            source_file = file_found
            try:
                processes = {}
                roots = []

                with open(file_found, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        if line.startswith("USER") or not line.strip():
                            continue

                        parts = line.split(maxsplit=17)
                        if len(parts) >= 18:
                            try:
                                pid = int(parts[3])
                                ppid = int(parts[4])
                                user = parts[0]
                                command = parts[17].strip()

                                processes[pid] = {
                                    'pid': pid,
                                    'ppid': ppid,
                                    'user': user,
                                    'command': command,
                                    'children': []
                                }
                            except ValueError:
                                continue

                for pid, pdata in processes.items():
                    ppid = pdata['ppid']
                    if ppid in processes:
                        processes[ppid]['children'].append(pid)
                    else:
                        roots.append(pid)

                def colorize_user(user):
                    badge_classes = {
                        'root': 'badge-danger',
                        'mobile': 'badge-primary',
                    }
                    badge_class = badge_classes.get(user, 'badge-warning')  
                    return f"<span class='badge {badge_class}'>{esc(user)}</span>"

                tree_lines = []
                def build_tree_string(pid, prefix=""):
                    if pid not in processes:
                        return
                    p = processes[pid]
                    pid_html = f"<span class='text-muted'>(PID: {esc(str(p['pid']))})</span>"  
                    user_html = colorize_user(p['user'])
                    tree_lines.append(f"{prefix}├── {pid_html} {user_html} {esc(p['command'])}")
                    for child_pid in p['children']:
                        build_tree_string(child_pid, prefix + "│   ")

                for root_pid in roots:
                    build_tree_string(root_pid)

                full_tree_text = "\n".join(tree_lines)

                html_formatted_tree = f"<pre class='mb-0'>{full_tree_text}</pre>"
                data_list.append([html_formatted_tree])

            except Exception as e:
                logfunc(f"Erreur lors du parsing de {file_found}: {e}")

    data_headers = ('Process Hierarchy Tree',)
    return data_headers, data_list, source_file