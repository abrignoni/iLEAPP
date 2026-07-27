"""
Run synthetic ArtifactResult benchmark profiles and capture basic metrics.

This script launches iLEAPP as a child process for each selected profile, samples
the child process working set while it runs, and writes JSON/CSV summaries. It
does not require psutil; on Windows it uses the process handle directly.
"""

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = ROOT_DIR / "admin" / "test" / "perf_data" / "artifact_result_fixture"
DEFAULT_OUTPUT = ROOT_DIR / "admin" / "test" / "perf_output"
DEFAULT_PROFILE_DIR = ROOT_DIR / "admin" / "test" / "perf_profiles"
DEFAULT_CUSTOM_ARTIFACTS = ROOT_DIR / "scripts" / "alternate_artifacts"
FOUND_RECORDS_RE = re.compile(r"Found\s+([\d,]+)\s+records\s+for\s+(.+)")

DEFAULT_PROFILES = (
    "perf_narrow_legacy_list",
    "perf_narrow_artifact_result",
    "perf_medium_legacy_transform",
    "perf_medium_artifact_result_transform",
    "perf_wide_legacy_list",
    "perf_wide_artifact_result_cursor",
)


def get_working_set_bytes(process):
    """Return current process-tree working-set/RSS bytes, or None if unavailable."""
    if os.name == "nt":
        return get_windows_process_tree_working_set_bytes(process.pid)
    return get_proc_status_rss(process.pid)


def get_windows_process_tree_working_set_bytes(root_pid):
    pids = get_windows_process_tree_pids(root_pid)
    total = 0
    for pid in pids:
        working_set = get_windows_working_set_bytes(pid)
        if working_set:
            total += working_set
    return total or None


def get_windows_process_tree_pids(root_pid):
    import ctypes
    from ctypes import wintypes

    class ProcessEntry32(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("th32DefaultHeapID", ctypes.POINTER(wintypes.ULONG)),
            ("th32ModuleID", wintypes.DWORD),
            ("cntThreads", wintypes.DWORD),
            ("th32ParentProcessID", wintypes.DWORD),
            ("pcPriClassBase", wintypes.LONG),
            ("dwFlags", wintypes.DWORD),
            ("szExeFile", wintypes.WCHAR * 260),
        ]

    create_snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot
    process_first = ctypes.windll.kernel32.Process32FirstW
    process_next = ctypes.windll.kernel32.Process32NextW
    close_handle = ctypes.windll.kernel32.CloseHandle

    create_snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    create_snapshot.restype = wintypes.HANDLE
    process_first.argtypes = [wintypes.HANDLE, ctypes.POINTER(ProcessEntry32)]
    process_first.restype = wintypes.BOOL
    process_next.argtypes = [wintypes.HANDLE, ctypes.POINTER(ProcessEntry32)]
    process_next.restype = wintypes.BOOL
    close_handle.argtypes = [wintypes.HANDLE]

    snapshot = create_snapshot(0x00000002, 0)
    if snapshot == wintypes.HANDLE(-1).value:
        return [root_pid]

    parent_map = {}
    try:
        entry = ProcessEntry32()
        entry.dwSize = ctypes.sizeof(entry)
        if process_first(snapshot, ctypes.byref(entry)):
            while True:
                parent_map[int(entry.th32ProcessID)] = int(entry.th32ParentProcessID)
                if not process_next(snapshot, ctypes.byref(entry)):
                    break
    finally:
        close_handle(snapshot)

    tree = {root_pid}
    changed = True
    while changed:
        changed = False
        for pid, parent_pid in parent_map.items():
            if parent_pid in tree and pid not in tree:
                tree.add(pid)
                changed = True
    return list(tree)


def get_windows_working_set_bytes(pid):
    import ctypes
    from ctypes import wintypes

    class ProcessMemoryCounters(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD),
            ("PageFaultCount", wintypes.DWORD),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
        ]

    open_process = ctypes.windll.kernel32.OpenProcess
    close_handle = ctypes.windll.kernel32.CloseHandle
    open_process.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    open_process.restype = wintypes.HANDLE
    close_handle.argtypes = [wintypes.HANDLE]

    process_query_information = 0x0400
    process_vm_read = 0x0010
    handle = open_process(process_query_information | process_vm_read, False, pid)
    if not handle:
        return None

    counters = ProcessMemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    get_process_memory_info = ctypes.windll.psapi.GetProcessMemoryInfo
    get_process_memory_info.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(ProcessMemoryCounters),
        wintypes.DWORD,
    ]
    get_process_memory_info.restype = wintypes.BOOL
    try:
        ok = get_process_memory_info(handle, ctypes.byref(counters), counters.cb)
        if not ok:
            return None
        return int(counters.WorkingSetSize)
    finally:
        close_handle(handle)


def get_proc_status_rss(pid):
    status_path = Path("/proc") / str(pid) / "status"
    try:
        for line in status_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) * 1024
    except OSError:
        return None
    return None


def parse_found_records(stdout):
    matches = FOUND_RECORDS_RE.findall(stdout)
    if not matches:
        return None, None
    count, artifact_name = matches[-1]
    return int(count.replace(",", "")), artifact_name.strip()


def run_profile(args, profile_name, run_index):
    profile_path = args.profile_dir / f"{profile_name}.ilprofile"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    output_folder = f"bench_{profile_name}_{run_index}_{timestamp}"
    command = [
        sys.executable,
        "ileapp.py",
        "-t",
        "fs",
        "-i",
        str(args.input),
        "-o",
        str(args.output),
        "-m",
        str(profile_path),
        "--custom_artifacts_path",
        str(args.custom_artifacts_path),
        "--custom_output_folder",
        output_folder,
    ]

    started_at = time.perf_counter()
    process = subprocess.Popen(
        command,
        cwd=ROOT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    peak_working_set = 0
    while process.poll() is None:
        current_working_set = get_working_set_bytes(process)
        if current_working_set:
            peak_working_set = max(peak_working_set, current_working_set)
        time.sleep(args.sample_interval)

    stdout, _ = process.communicate()
    current_working_set = get_working_set_bytes(process)
    if current_working_set:
        peak_working_set = max(peak_working_set, current_working_set)

    ended_at = time.perf_counter()
    row_count, artifact_name = parse_found_records(stdout)
    log_path = args.output / f"{output_folder}.log"
    log_path.write_text(stdout, encoding="utf-8")

    return {
        "profile": profile_name,
        "artifact_name": artifact_name,
        "run_index": run_index,
        "return_code": process.returncode,
        "wall_time_seconds": round(ended_at - started_at, 4),
        "peak_working_set_bytes": peak_working_set or None,
        "peak_working_set_mib": round(peak_working_set / 1024 / 1024, 2)
        if peak_working_set
        else None,
        "row_count": row_count,
        "output_folder": str(args.output / output_folder),
        "log_path": str(log_path),
    }


def write_results(args, results):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    json_path = args.output / f"artifact_result_benchmark_{timestamp}.json"
    csv_path = args.output / f"artifact_result_benchmark_{timestamp}.csv"

    json_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    return json_path, csv_path


def main():
    parser = argparse.ArgumentParser(description="Run ArtifactResult benchmark profiles.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--profile-dir", type=Path, default=DEFAULT_PROFILE_DIR)
    parser.add_argument("--custom-artifacts-path", type=Path, default=DEFAULT_CUSTOM_ARTIFACTS)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--sample-interval", type=float, default=0.1)
    parser.add_argument("--profiles", nargs="+", default=list(DEFAULT_PROFILES))
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    results = []
    for run_index in range(1, args.repeat + 1):
        for profile_name in args.profiles:
            print(f"Running {profile_name}, pass {run_index}")
            result = run_profile(args, profile_name, run_index)
            results.append(result)
            print(
                f"  rc={result['return_code']} rows={result['row_count']} "
                f"time={result['wall_time_seconds']}s "
                f"peak={result['peak_working_set_mib']} MiB"
            )

    json_path, csv_path = write_results(args, results)
    print(f"Wrote {json_path}")
    print(f"Wrote {csv_path}")


if __name__ == "__main__":
    main()
