#!/usr/bin/env python3
"""
Baseline: replicate the current LEAPP search behavior over a TAR or ZIP.

- Reads glob-like patterns from file_path.txt (one per line).
- Dedupe patterns in input order (like the framework’s “don’t search the same twice” goal).
- Uses FileSeekerTar or FileSeekerZip from scripts/search_files.py, which:
  * compiles patterns with fnmatch._compile_pattern(normcase(...))
  * matches against "root/" + normcase(member.name)
  * iterates members and extracts matching files to an output folder
  * memoizes results per pattern in self.searched

Usage:
    python exp/baseline_search.py /path/to/image.tar or .zip

Outputs:
    - Extraction under exp/_out_baseline/<run_stamp>/
    - A CSV summary of matches: exp/_out_baseline/<run_stamp>/baseline_match_summary.csv
    - A CSV detail of matches: exp/_out_baseline/<run_stamp>/baseline_match_detail.csv
    - A stats file: exp/_out_baseline/<run_stamp>/baseline_stats.txt
    - Stats printed to stdout
"""

import sys
import time
from pathlib import Path
from collections import OrderedDict
import csv

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from scripts.search_files import FileSeekerTar, FileSeekerZip  # uses the same search implementation as the framework

def read_patterns(pattern_file: Path) -> list[str]:
    """
    Read patterns from path_list.txt (one per line).
    - Strips whitespace
    - Skips empty/comment lines
    - Dedupe in original order
    """
    raw = []
    with pattern_file.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            raw.append(s)

    # Ordered dedupe (preserve author/testing ordering)
    unique = list(OrderedDict((p, None) for p in raw).keys())
    return unique

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python exp/baseline_search.py /path/to/image.tar or .zip")
        sys.exit(2)

    archive_path = Path(sys.argv[1])
    if not archive_path.exists():
        print(f"Archive not found: {archive_path}")
        sys.exit(1)

    # Locate file_path.txt sitting next to this script or in root of repo
    patterns_path = Path(__file__).with_name("path_list.txt")
    if not patterns_path.exists():
        patterns_path = Path(repo_root) / "path_list.txt"
    if not patterns_path.exists():
        print(f"Missing {patterns_path}. Run 'python ileapp.py -p' to generate it.")
        sys.exit(1)

    patterns = read_patterns(patterns_path)
    print(f"Loaded {len(patterns)} unique patterns from {patterns_path.name}")

    # Output folder: exp/_out_baseline/<timestamp>/
    run_stamp = time.strftime("%Y%m%d-%H%M%S")
    out_root = Path(__file__).with_name("_out_baseline") / run_stamp
    out_root.mkdir(parents=True, exist_ok=True)
    print(f"Extraction dir: {out_root}")

    # Create the seeker using the same class LEAPP uses today
    seeker = None
    if str(archive_path).lower().endswith('.zip'):
        seeker = FileSeekerZip(str(archive_path), str(out_root))
        print("Processing ZIP file...")
    elif str(archive_path).lower().endswith(('.tar', '.gz')):
        seeker = FileSeekerTar(str(archive_path), str(out_root))
        print("Processing TAR file...")
    else:
        print(f"Unsupported archive type: {archive_path.suffix}")
        sys.exit(1)

    # Get total file count for stats
    total_files = 0
    if isinstance(seeker, FileSeekerTar):
        total_files = len(seeker.tar_file.getmembers())
    elif isinstance(seeker, FileSeekerZip):
        total_files = len(seeker.name_list)

    total_matches = 0
    per_pattern_counts: list[tuple[str,int,float]] = []

    t0 = time.perf_counter()

    for pat in patterns:
        p_start = time.perf_counter()
        # Set extract=False so we only get back path strings
        hits = seeker.search(pat, return_on_first_hit=False, force=False, extract=False)
        p_elapsed = time.perf_counter() - p_start

        count = len(hits) if isinstance(hits, list) else (1 if hits else 0)
        total_matches += count
        per_pattern_counts.append((pat, count, p_elapsed))

        # lightweight progress line (keeps stdout readable)
        print(f"[{len(per_pattern_counts):>4}/{len(patterns)}] {pat} -> {count} hits in {p_elapsed:.3f}s")

    elapsed = time.perf_counter() - t0
    seeker.cleanup()

    # Assign sequential IDs to patterns for linking
    pattern_to_id = {pat: idx for idx, pat in enumerate(patterns, 1)}

    # Collect detailed matches from seeker's memo (seeker.searched has pattern -> list of extracted paths)
    detail_rows = []
    for pat in patterns:
        hits = seeker.searched.get(pat, [])
        pat_id = pattern_to_id[pat]
        for hit in hits:
            # The 'hit' is now just the relative path string, so no conversion is needed.
            detail_rows.append((pat_id, hit))

    # Write baseline_match_summary.csv (with ID)
    summary_csv_path = out_root / "baseline_match_summary.csv"
    with summary_csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pattern_id", "pattern", "match_count", "seconds"])
        for pat, cnt, secs in per_pattern_counts:
            pat_id = pattern_to_id[pat]
            w.writerow([pat_id, pat, cnt, f"{secs:.6f}"])

    # Write baseline_match_detail.csv
    detail_csv_path = out_root / "baseline_match_detail.csv"
    with detail_csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pattern_id", "file_path"])
        for pat_id, path in sorted(detail_rows):
            w.writerow([pat_id, path])

    # Generate stats, write to file, and print to console
    stats_content = generate_stats_text(archive_path, patterns, total_matches, elapsed, total_files)
    stats_path = out_root / "baseline_stats.txt"
    with stats_path.open("w", encoding="utf-8") as f:
        f.write(stats_content)

    print(stats_content)
    
    # Final summary of files written
    print("\n--- Output Files ---")
    print(f"Wrote summary CSV : {summary_csv_path}")
    print(f"Wrote detail CSV  : {detail_csv_path}")
    print(f"Wrote stats file  : {stats_path}")


def generate_stats_text(archive_path, patterns, total_matches, elapsed, total_files):
    """Generates a formatted string of summary stats."""
    import io
    
    s = io.StringIO()

    s.write("\n=== Baseline Summary ===\n")
    s.write(f"Input file        : {archive_path}\n")
    s.write(f"Patterns searched : {len(patterns)}\n")
    s.write(f"Total files       : {total_files}\n")
    s.write(f"Total matches     : {total_matches}\n")
    s.write(f"Total time        : {elapsed:.3f}s\n")
    
    return s.getvalue()


if __name__ == "__main__":
    main()
