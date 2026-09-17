from scripts.ilapfuncs import artifact_processor, logfunc

__artifacts_v2__ = {
    "sysdiagnoseProcess": {
        "name": "Sysdiagnose Process",
        "description": "Vue hiérarchique des processus (arbre parent/enfant) extraite de ps.txt / ps_thread.txt",
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

                # 1. Lecture et structuration des données
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

                # 2. Liaison des parents et des enfants
                for pid, pdata in processes.items():
                    ppid = pdata['ppid']
                    if ppid in processes:
                        processes[ppid]['children'].append(pid)
                    else:
                        roots.append(pid)

                # 3. Fonction récursive pour générer les lignes de l'arbre (avec couleurs)
                def colorize_user(user):
                    colors = {
                        'root': '#e74c3c',      # rouge
                        'mobile': '#3498db',    # bleu
                    }
                    color = colors.get(user, '#f39c12')  # orange par défaut pour les autres users système
                    return f"<span style='color:{color}; font-weight:bold;'>[{user}]</span>"

                def colorize_command(command):
                    # Sépare l'exécutable de ses paramètres (premier espace non protégé)
                    parts = command.split(' ', 1)
                    exe = parts[0]
                    params = parts[1] if len(parts) > 1 else ''

                    exe_html = f"<span style='color:#e0e0e0;'>{exe}</span>"
                    if params:
                        params_html = f" <span style='color:#2ecc71;'>{params}</span>"
                    else:
                        params_html = ''
                    return exe_html + params_html

                tree_lines = []
                def build_tree_string(pid, prefix=""):
                    if pid not in processes:
                        return
                    p = processes[pid]
                    pid_html = f"<span style='color:#888;'>(PID: {p['pid']})</span>"
                    user_html = colorize_user(p['user'])
                    cmd_html = colorize_command(p['command'])
                    tree_lines.append(f"{prefix}├── {pid_html} {user_html} {cmd_html}")
                    for child_pid in p['children']:
                        build_tree_string(child_pid, prefix + "│   ")

                # Génération de l'arbre global
                for root_pid in roots:
                    build_tree_string(root_pid)

                full_tree_text = "\n".join(tree_lines)

                # Encapsulation HTML pour conserver l'affichage exact
                html_formatted_tree = (
                    "<pre style=\"font-family:'Consolas','Menlo',monospace; "
                    "font-size:13px; line-height:1.5; margin:0; padding:12px; "
                    "background:#1e1e1e; color:#ddd; border-radius:6px; "
                    "overflow-x:auto;\">"
                    f"{full_tree_text}"
                    "</pre>"
                )
                data_list.append([html_formatted_tree])

            except Exception as e:
                logfunc(f"Erreur lors du parsing de {file_found}: {e}")

    data_headers = ('Process Hierarchy Tree',)
    return data_headers, data_list, source_file
