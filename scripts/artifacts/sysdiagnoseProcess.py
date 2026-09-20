__artifacts_v2__ = {
    "sysdiagnoseProcess": {
        "name": "Sysdiagnose Process",
        "description": "Parses ps.txt from Sysdiagnose logs to list running processes with PID, parent PID, user, command and other ps(1) fields.",
        "author": "@mathisdesaulty",
        "creation_date": "2026-09-17",
        "last_update_date": "2026-09-20",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "Parses ps.txt only. ps_thread.txt is not read: its columns sit in a different order "
                 "from ps.txt (its 4th column is %CPU, where the 4th of ps.txt holds the process "
                 "identifier), and on the three sysdiagnose captures tested it carried a header line "
                 "and no data rows. The %CPU, %MEM and TIME fields are read from each line but not "
                 "reported: each held a single value on all 1,668 rows of the four captures tested "
                 "(0.0, 0.0 and 0:00.00 on iOS 16 20A362, iOS 17.3 21D50, iOS 26 23G71 and "
                 "iOS 26.5.2 23F84). STARTED is reported as recorded (e.g. '1:25PM'); it carries no "
                 "date and no timezone, so no instant is asserted. See 'Sysdiagnose Process - Tree' "
                 "for a rendered image of the process hierarchy.",
        "paths": (
            '*/ps.txt',
            '*/sysdiagnose_*.tar.gz'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "list-tree",
        "sample_data": {
            "rodeo_ios17_sysdiag": "iOS 17.3 | 407 rows",
            "hc_ios26_sysdiag": "iOS 26 | 546 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 382 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows; the image carries no sysdiagnose",
        }
    },
    "sysdiagnoseProcessTree": {
        "name": "Sysdiagnose Process - Tree",
        "description": "Rendered image of the process hierarchy (parent/child tree) from ps.txt",
        "author": "@mathisdesaulty",
        "creation_date": "2026-09-18",
        "last_update_date": "2026-09-20",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "A PNG is rendered per ps.txt capture as a visual reference of the process tree, one "
                 "image per sysdiagnose. Tree branches use plain ASCII characters (not Unicode "
                 "box-drawing) so the image renders correctly regardless of which font is available "
                 "on the host running the report. The image is drawn on a fixed dark background and "
                 "does not follow the report's light or dark setting. 'Sysdiagnose Process' holds "
                 "the same data in queryable form.",
        "paths": (
            '*/ps.txt',
            '*/sysdiagnose_*.tar.gz'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "list-tree",
        "sample_data": {
            "rodeo_ios17_sysdiag": "iOS 17.3 | 1 row",
            "hc_ios26_sysdiag": "iOS 26 | 1 row",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 1 row",
            "jess_ios15": "iOS 15.0.2 | 0 rows; the image carries no sysdiagnose",
        }
    }
}

import io

from PIL import Image, ImageDraw, ImageFont

from scripts.ilapfuncs import artifact_processor, get_sysdiagnose_files, check_in_embedded_media, logfunc

_LINE_H = 16
_PAD = 10
_FONT_SIZE = 12
_USER_PALETTE = ['#5b7ea6', '#6a9e6a', '#a68c5b', '#8c5ba6', '#5ba6a1', '#a65b7e', '#8c8c5b']
_DEFAULT_USER_COLOR = '#9a9a9a'


def _mono_font(size):
    for path in ('DejaVuSansMono.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
                 '/System/Library/Fonts/Supplemental/Menlo.ttc', '/Library/Fonts/Menlo.ttc'):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size)
    except TypeError:
        return ImageFont.load_default()


def _parse_ps_line(line):
    """Parse one ps.txt line into a dict, or None if the line should be skipped."""
    if line.startswith("USER") or not line.strip():
        return None

    # Columns ps.txt: user,uid,prsna,pid,ppid,flags,%cpu,%mem,pri,ni,vsz,rss,wchan,tt,stat,start,time,command
    parts = line.split(maxsplit=17)
    if len(parts) < 18:
        return None

    try:
        pid = int(parts[3])
        ppid = int(parts[4])
    except ValueError:
        return None

    return {
        'pid': pid,
        'ppid': ppid,
        'user': parts[0],
        'uid': parts[1],
        'cpu': parts[6],
        'mem': parts[7],
        'stat': parts[14],
        'started': parts[15],
        'time': parts[16],
        'command': parts[17].strip(),
    }


def _build_tree(file_obj):
    """Parse a ps.txt stream into {pid: {..., children}} plus root pids."""
    processes = {}
    for line in file_obj:
        entry = _parse_ps_line(line)
        if entry is None:
            continue
        entry['children'] = []
        processes[entry['pid']] = entry

    roots = []
    for pid, pdata in processes.items():
        if pdata['ppid'] in processes and pdata['ppid'] != pid:
            processes[pdata['ppid']]['children'].append(pid)
        else:
            roots.append(pid)
    return processes, roots


def _flatten_tree(processes, roots):
    """Depth-first walk into a flat list of (depth, pid, user, command)."""
    flat = []

    def walk(pid, depth):
        p = processes.get(pid)
        if not p:
            return
        flat.append((depth, p['pid'], p['user'], p['command']))
        for child_pid in p['children']:
            walk(child_pid, depth + 1)

    for root_pid in roots:
        walk(root_pid, 0)
    return flat


def _user_colors(flat):
    colors = {}
    for _, _, user, _ in flat:
        if user not in colors:
            colors[user] = _USER_PALETTE[len(colors) % len(_USER_PALETTE)]
    return colors


def _render_tree(title, flat, user_colors):
    font = _mono_font(_FONT_SIZE)
    header_font = _mono_font(_FONT_SIZE + 4)

    probe_img = Image.new('RGB', (1, 1))
    probe_draw = ImageDraw.Draw(probe_img)
    lines = [f"{'|   ' * depth}|-- (PID: {pid}) [{user}] {command}" for depth, pid, user, command in flat]
    max_width = max((probe_draw.textlength(line, font=font) for line in lines), default=200)

    width = int(max_width) + _PAD * 2
    height = _PAD * 2 + 26 + len(flat) * _LINE_H

    img = Image.new('RGB', (width, height), '#1e1e1e')
    draw = ImageDraw.Draw(img)
    draw.text((_PAD, _PAD), title, fill='#ffffff', font=header_font)

    y = _PAD + 26
    for depth, pid, user, command in flat:
        x = _PAD
        prefix = '|   ' * depth + '|-- '
        draw.text((x, y), prefix, fill='#666666', font=font)
        x += draw.textlength(prefix, font=font)

        pid_text = f"(PID: {pid}) "
        draw.text((x, y), pid_text, fill='#888888', font=font)
        x += draw.textlength(pid_text, font=font)

        user_text = f"[{user}] "
        draw.text((x, y), user_text, fill=user_colors.get(user, _DEFAULT_USER_COLOR), font=font)
        x += draw.textlength(user_text, font=font)

        draw.text((x, y), command, fill='#dddddd', font=font)
        y += _LINE_H

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()


@artifact_processor
def sysdiagnoseProcess(context):
    """ See artifact description """
    data_headers = (
        "PID", "Parent PID", "User", "Command",
        "UID", "STAT", "STARTED",
        "Source File"
    )
    data_list = []
    sources = []

    for file_obj, source_path in get_sysdiagnose_files(context.get_files_found(), "ps.txt"):
        source_name = context.get_relative_path(source_path)
        sources.append(source_path)

        for line in file_obj:
            entry = _parse_ps_line(line)
            if entry is None:
                continue
            data_list.append((
                entry['pid'], entry['ppid'], entry['user'], entry['command'],
                entry['uid'], entry['stat'], entry['started'], source_name
            ))

    return data_headers, data_list, '\n'.join(sorted(set(sources)))


@artifact_processor
def sysdiagnoseProcessTree(context):
    """ See artifact description """
    data_headers = ('Capture', ('Tree', 'media'))
    data_list = []
    sources = []

    for file_obj, source_path in get_sysdiagnose_files(context.get_files_found(), "ps.txt"):
        source_name = context.get_relative_path(source_path)
        sources.append(source_path)

        processes, roots = _build_tree(file_obj)
        flat = _flatten_tree(processes, roots)
        if not flat:
            data_list.append((source_name, None))
            continue

        user_colors = _user_colors(flat)
        try:
            png = _render_tree(source_name, flat, user_colors)
            media_ref = check_in_embedded_media(source_path, png, 'sysdiagnose_process_tree.png',
                                                force_type='image/png', force_extension='png')
        except (OSError, ValueError) as ex:
            logfunc(f'Failed to render process tree for {source_path}: {ex}')
            media_ref = None
        data_list.append((source_name, media_ref))

    return data_headers, data_list, '\n'.join(sorted(set(sources)))