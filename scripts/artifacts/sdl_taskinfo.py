__artifacts_v2__ = {
    "taskinfo_processes": {
        "name": "Sysdiagnose - Process Task Info",
        "description": "One row per process block of taskinfo.txt in a sysdiagnose: name, process id, executable UUID, "
                       "run time, memory footprint, CPU time and I/O volume, as printed",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": (
            "taskinfo.txt is the output of the taskinfo tool run when the sysdiagnose was taken, so it "
            "describes the processes that existed at that moment and no others; its first line gives "
            "the number of tasks. One row per block that starts with process: \"<name>\" [<pid>]. "
            "Executable UUID, Architecture and Platform are as printed. Run Time (s) is the printed "
            "run time in seconds, which is the time the process had existed when the tool ran; the "
            "tool's own clock is not in the file, so a start time is not computed here. Physical "
            "Footprint and Lifetime Maximum Footprint are the phys_footprint values as printed "
            "(with their units). CPU Time (s) is the first number of the CPU time line. Bytes Read and "
            "Bytes Written are as printed with their units. RunningBoard Managed and PID Suspended are "
            "the printed YES/NO values. The process name is the executable name printed by the tool, "
            "not an app bundle identifier or a display name. A process that was not running when the "
            "sysdiagnose was taken is not listed, so an app absent here may still be installed or have "
            "been used earlier; a listed process does not show that the user opened it. Observed on "
            "three sysdiagnoses (two iOS 26.6 of one device: 413 and 463 process blocks; one iOS 26.6.2 sysdiagnose of another device: 557). Not reported: the per-thread "
            "and per-QoS lines, the audit token and the coalition lines."
        ),
        "paths": (
            '*/taskinfo.txt',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cpu",
        "sample_data": {
            "local_sysdiag_ios26_6_a1": "iOS 26.6 sysdiagnose | 413 rows",
            "local_sysdiag_ios26_6_a2": "iOS 26.6 sysdiagnose | 463 rows",
            "local_sysdiag_ios26_6_2_b": "iOS 26.6.2 sysdiagnose | 557 rows",
        },
    },
}

import re
import tarfile
import zlib

from scripts.ilapfuncs import artifact_processor, get_sysdiagnose_files, logfunc

_READ_ERRORS = (OSError, EOFError, tarfile.TarError, zlib.error)

_PROCESS = re.compile(r'^process: "(.*)" \[(\d+)\]$')


def _first(pattern, text, group=1):
    match = re.search(pattern, text, re.M)
    return match.group(group) if match else ''


def _blocks(lines):
    block = None
    for line in lines:
        match = _PROCESS.match(line)
        if match:
            if block:
                yield block
            block = {'name': match.group(1), 'pid': int(match.group(2)), 'text': []}
        elif block is not None:
            block['text'].append(line)
    if block:
        yield block


@artifact_processor
def taskinfo_processes(context):
    data_headers = (
        'Process', 'PID', 'Executable UUID', 'Architecture', 'Platform', 'Run Time (s)',
        'Physical Footprint', 'Lifetime Maximum Footprint', 'CPU Time (s)', 'Bytes Read',
        'Bytes Written', 'RunningBoard Managed', 'PID Suspended', 'Source File')
    data_list = []
    sources = []
    for file_obj, source_path in get_sysdiagnose_files(
            context.get_files_found(), 'taskinfo.txt', text_mode=False):
        rel = context.get_relative_path(source_path)
        try:
            lines = file_obj.read().decode('utf-8', errors='replace').splitlines()
        except _READ_ERRORS as ex:
            logfunc(f'Failed to read {rel}: {ex}')
            continue
        sources.append(source_path)
        for block in _blocks(lines):
            text = '\n'.join(block['text'])
            run_time = _first(r'^run time: (\d+) s', text)
            cpu = _first(r'^CPU time: ([\d.]+) s', text)
            data_list.append((
                block['name'], block['pid'], _first(r'^executable uuid: (\S+)', text),
                _first(r'^architecture: (.*)$', text), _first(r'^platform: (.*)$', text),
                int(run_time) if run_time else '',
                _first(r'phys_footprint bytes: (.*?)(?:;|$)', text),
                _first(r'phys_footprint lifetime maximum bytes: (.*)$', text),
                float(cpu) if cpu else '',
                _first(r'^bytes read: (.*?) written:', text),
                _first(r'^bytes read: .*? written: (.*?) logical writes', text),
                _first(r'^runningboard managed: (\S+)', text),
                _first(r'^pid suspended: (\S+)', text), rel))
    return data_headers, data_list, '\n'.join(sources)
