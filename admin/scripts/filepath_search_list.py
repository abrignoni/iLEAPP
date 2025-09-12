"""
Processes artifact files to find file path search patterns.

This script searches through specified artifact modules to extract file search
patterns. It then runs these patterns against lists of file paths from various
data sources (provided in zip files) to count matches. The results are
aggregated and written to a CSV file.

The script also generates a summary table in a Markdown file, showing the
number of hits for each artifact from each data source.

Can be run in two modes:
1. Full processing: Extracts patterns, searches, and generates CSV and MD summary.
2. Summary only: Skips the search and just regenerates the MD summary from an
   existing CSV file using the --csv-to-md flag.
"""
import os
import csv
import glob
import ast
import time
import traceback
import argparse
import zipfile
from io import StringIO
from fnmatch import fnmatch
from collections import defaultdict

# Define paths
MD_FILE_PATH = 'admin/docs/filepath_search_summary.md'
CSV_OUTPUT_FILE = 'admin/data/generated/filepath_results.csv'
ARTIFACTS_DIR = 'scripts/artifacts'
FILEPATH_LISTS_DIR = 'admin/data/filepath-lists'


def get_artifacts(file_path):
    """
    Extract artifact definitions from a Python module file.

    Parses the given file to find __artifacts_v2__ or __artifacts__
    dictionaries and returns their content.

    Args:
        file_path (str): The path to the artifact module file.

    Returns:
        tuple: A tuple containing the artifacts dictionary and a boolean
               indicating if it's the v2 format. Returns (None, False)
               on failure.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if target.id == '__artifacts_v2__':
                            return ast.literal_eval(node.value), True
                        elif target.id == '__artifacts__':
                            artifacts = {}
                            if isinstance(node.value, ast.Dict):
                                for key, value in zip(node.value.keys, node.value.values):
                                    if isinstance(key, ast.Constant) and isinstance(value, ast.Tuple):
                                        artifact_name = ast.literal_eval(key)
                                        artifact_values = []
                                        for v in value.elts:
                                            if isinstance(v, ast.Constant):
                                                artifact_values.append(ast.literal_eval(v))
                                            elif isinstance(v, ast.Name):
                                                artifact_values.append(v.id)
                                            elif isinstance(v, ast.Tuple):
                                                artifact_values.append(tuple(ast.literal_eval(e) if isinstance(e, ast.Constant) else e.id for e in v.elts))
                                            else:
                                                artifact_values.append(v)
                                        artifacts[artifact_name] = {
                                            'name': artifact_values[0],
                                            'paths': artifact_values[1],
                                            'function': artifact_values[2] if len(artifact_values) > 2 else None
                                        }
                                return artifacts, False
                            else:
                                print(f"Unexpected __artifacts__ format in {file_path}")
                                return None, False
        print(f"No __artifacts__ or __artifacts_v2__ found in {file_path}")
        return None, False
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
        traceback.print_exc()
        return None, False


def count_matches(pattern, filepath_list):
    """
    Count occurrences of a pattern in a list of file paths.

    Args:
        pattern (str): The glob-style pattern to match.
        filepath_list (list): A list of file path strings.

    Returns:
        int: The number of file paths that match the pattern.
    """
    count = 0
    for filepath in filepath_list:
        if fnmatch(filepath, pattern):
            count += 1
    return count


def generate_summary_table(results):
    """
    Create a summary table from the detailed search results.

    Args:
        results (list): A list of lists, where each inner list is a
                        result row.

    Returns:
        list: A list of lists representing the summary table, including
              a header row.
    """
    summary = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    csv_files = set()

    for row in results:
        module_name, artifact_name, _, csv_file, count, _ = row
        csv_file = csv_file.split('/')[0]  # Get only the zip file name
        csv_file = csv_file.replace('.zip', '').replace('.csv', '')  # Remove .zip and .csv
        summary[module_name][artifact_name][csv_file] += int(count)
        csv_files.add(csv_file)

    csv_files = sorted(csv_files)
    table_rows = []

    for module_name in sorted(summary.keys()):
        for artifact_name in sorted(summary[module_name].keys()):
            row = [module_name, artifact_name]
            for csv_file in csv_files:
                row.append(str(summary[module_name][artifact_name][csv_file]))
            table_rows.append(row)

    header = ["Module", "Artifact"] + csv_files
    return [header] + table_rows


def update_markdown_file(table):
    """
    Update the summary table in the project's Markdown documentation.

    Args:
        table (list): A list of lists representing the summary table data.
    """
    start_marker = "<!-- FILEPATH_SEARCH_SUMMARY_START -->"
    end_marker = "<!-- FILEPATH_SEARCH_SUMMARY_END -->"

    with open(MD_FILE_PATH, 'r', encoding='utf-8') as file:
        content = file.read()

    start_index = content.index(start_marker) + len(start_marker)
    end_index = content.index(end_marker)

    table_md = "\n\n| " + " | ".join(table[0]) + " |\n"
    table_md += "|" + "|".join(["---" for _ in table[0]]) + "|\n"
    for row in table[1:]:
        table_md += "| " + " | ".join(row) + " |\n"

    updated_content = (
        content[:start_index] +
        "\n\n" + table_md + "\n" +
        content[end_index:]
    )

    with open(MD_FILE_PATH, 'w', encoding='utf-8') as file:
        file.write(updated_content)


def csv_to_md():
    """
    Generate the Markdown summary table from the results CSV file.

    This function is intended to be run when you only want to update the
    markdown documentation without re-running the entire search process.
    """
    if not os.path.exists(CSV_OUTPUT_FILE):
        print(f"Error: {CSV_OUTPUT_FILE} does not exist. Please run the full script first.")
        return

    with open(CSV_OUTPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        results = list(reader)

    summary_table = generate_summary_table(results)
    update_markdown_file(summary_table)
    print(f"Summary table updated in {MD_FILE_PATH}")


def read_csv_with_encoding(content):
    """
    Read CSV data from a byte string, trying multiple common encodings.

    Args:
        content (bytes): The byte string content of the CSV file.

    Raises:
        ValueError: If the content cannot be decoded with any of the
                    tried encodings.

    Returns:
        list: A list of lists representing the CSV data.
    """
    encodings = ['utf-8', 'latin-1', 'ascii', 'utf-16']
    for encoding in encodings:
        try:
            decoded_content = content.decode(encoding)
            return list(csv.reader(StringIO(decoded_content)))
        except UnicodeDecodeError:
            continue
    raise ValueError("Unable to determine the correct encoding")


def main():
    """
    Main function to run the artifact processing and summary generation.

    Parses command-line arguments, processes artifact files, counts file path
    matches, and writes the results to CSV and Markdown files.
    """
    parser = argparse.ArgumentParser(description='Process artifact files and generate summary.')
    parser.add_argument('--csv-to-md', action='store_true', help='Only convert CSV to Markdown summary')
    args = parser.parse_args()

    if args.csv_to_md:
        csv_to_md()
        return

    # Debug output: Show recognized filepath zip files
    filepath_zip_files = glob.glob(os.path.join(FILEPATH_LISTS_DIR, '*.zip'))
    print("Recognized filepath zip files:")
    for zip_file in filepath_zip_files:
        print(f"- {os.path.basename(zip_file)}")
    print(f"Total filepath zip files: {len(filepath_zip_files)}\n")

    results = []

    for artifact_file in list(glob.glob(os.path.join(ARTIFACTS_DIR, '*.py'))):
        module_name = os.path.splitext(os.path.basename(artifact_file))[0]
        artifacts, is_v2 = get_artifacts(artifact_file)

        if artifacts:
            print(f"Processing {module_name}")
            module_hits = 0
            for artifact_name, artifact_data in artifacts.items():
                search_patterns = artifact_data['paths']
                
                # Ensure search_patterns is always a list
                if isinstance(search_patterns, str):
                    search_patterns = [search_patterns]
                elif isinstance(search_patterns, tuple):
                    search_patterns = list(search_patterns)
                elif not isinstance(search_patterns, list):
                    print(f"Unexpected type for search_patterns in {module_name}: {type(search_patterns)}")
                    continue

                # Process filepath list files
                for zip_file in filepath_zip_files:
                    zip_file_name = os.path.basename(zip_file)
                    zip_file_name = zip_file_name.replace('.zip', '').replace('.csv', '')  # Remove .zip and .csv
                    
                    with zipfile.ZipFile(zip_file, 'r') as zf:
                        csv_files = [f for f in zf.namelist() if f.endswith('.csv') and not os.path.basename(f).startswith('.')]
                        for csv_file in csv_files:
                            try:
                                with zf.open(csv_file) as file:
                                    content = file.read()
                                rows = read_csv_with_encoding(content)
                                filepaths = [row[0] for row in rows[1:] if row]  # Skip header
                            except ValueError as e:
                                print(f"Error reading {csv_file} in {zip_file_name}: {str(e)}")
                                continue
                            except Exception as e:
                                print(f"Unexpected error reading {csv_file} in {zip_file_name}: {str(e)}")
                                continue

                            for pattern in search_patterns:
                                start_time = time.time()
                                count = count_matches(pattern, filepaths)
                                end_time = time.time()
                                search_time = end_time - start_time
                                
                                results.append([
                                    module_name,
                                    artifact_name,
                                    pattern,
                                    zip_file_name,  # Use only the modified zip file name
                                    count,
                                    f"{search_time:.4f}"
                                ])
                                module_hits += count

            print(f"  Total hits for {module_name}: {module_hits}")
        else:
            print(f"Skipping {module_name} due to parsing errors")

    with open(CSV_OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Module Name', 'Artifact Name', 'Search Pattern', 'List File Name', 'Count', 'Search Time (s)'])
        writer.writerows(results)

    print(f"\nResults written to {CSV_OUTPUT_FILE}")

    # Generate and update summary table
    summary_table = generate_summary_table(results)
    update_markdown_file(summary_table)
    print(f"Summary table updated in {MD_FILE_PATH}")

if __name__ == "__main__":
    main()