# Experimental Archive Search Scripts

This directory contains experimental Python scripts designed to test and compare different strategies for searching file patterns within large TAR and ZIP archives, like those from mobile device extractions.

The goal is to evaluate a faster, indexed search method against the current baseline implementation.

## Scripts

### `baseline_search.py`
- **What it does:** Replicates the current `iLEAPP` framework's file search behavior (`FileSeekerTar`). It performs a linear scan through the archive for each pattern.
- **Purpose:** Serves as the control for performance and accuracy comparison.

### `improved_search.py`
- **What it does:** Implements a multi-level, optimized search strategy.
    1.  It first builds a set of in-memory indexes (by basename, extension, directory, and heuristic-based buckets) in a single pass over the archive.
    2.  For each pattern, it attempts the fastest match strategy first: direct hash lookup for exact paths, or a "DB Family" fast-path for specific database files (including their `-wal` and `-shm` sidecars).
    3.  For general wildcard patterns, it uses the indexes to dramatically prune the list of candidate files before running a final regex match.
- **Purpose:** To demonstrate a significant speedup in search time with no loss of accuracy.

## Running the Experiment

Both scripts are run from the root of the `iLEAPP` repository.

### 1. Generate the Pattern List

The scripts rely on a `path_list.txt` file, which contains all file search patterns used by the `iLEAPP` modules. The script looks for this file first in the `exp/` directory, then in the repo root. If it doesn't exist, generate into the root folder it by running:
```bash
python ileapp.py -p
```

### 2. Run a Script

Execute either script by passing the path to a TAR or ZIP archive as an argument.

**For the baseline test:**
```bash
python exp/baseline_search.py /path/to/your/archive.zip
```

**For the improved test:**
```bash
python exp/improved_search.py /path/to/your/archive.zip
```

## Output

Each script creates a timestamped output directory inside `exp/` (e.g., `_out_baseline/` or `_out_improved/`). These directories contain:
-   `*_match_summary.csv`: A summary of match counts and timings for each pattern.
-   `*_match_detail.csv`: A detailed list of every file path that was found, linked by a pattern ID.
-   `*_stats.txt`: A list of info and stats about the search performed (same as console output).

The console output provides a real-time progress log and a final summary of total matches, timings, and (for the improved script) statistics on index and bucket performance.
