import os
import csv
import glob
import ast
import time
import traceback
import argparse
from fnmatch import fnmatch
from unittest.mock import MagicMock
from collections import defaultdict

def get_artifacts(file_path):
    try:
        with open(file_path, 'r') as file:
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
    count = 0
    for filepath in filepath_list:
        if fnmatch(filepath, pattern):
            count += 1
    return count

def generate_summary_table(results):
    summary = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    csv_files = set()

    for row in results:
        module_name, artifact_name, _, csv_file, count, _ = row
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
    md_file_path = 'admin/docs/filepath_search_summary.md'
    start_marker = "<!-- FILEPATH_SEARCH_SUMMARY_START -->"
    end_marker = "<!-- FILEPATH_SEARCH_SUMMARY_END -->"

    with open(md_file_path, 'r') as file:
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

    with open(md_file_path, 'w') as file:
        file.write(updated_content)

def csv_to_md():
    output_file = 'admin/docs/filepath_results.csv'
    
    if not os.path.exists(output_file):
        print(f"Error: {output_file} does not exist. Please run the full script first.")
        return

    with open(output_file, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        results = list(reader)

    summary_table = generate_summary_table(results)
    update_markdown_file(summary_table)
    print(f"Summary table updated in admin/docs/filepath_search_summary.md")

def main():
    parser = argparse.ArgumentParser(description='Process artifact files and generate summary.')
    parser.add_argument('--csv-to-md', action='store_true', help='Only convert CSV to Markdown summary')
    args = parser.parse_args()

    if args.csv_to_md:
        csv_to_md()
        return

    artifacts_dir = 'scripts/artifacts'
    filepath_lists_dir = 'admin/data/filepath-lists'
    output_file = 'admin/docs/filepath_results.csv'

    # Debug output: Show recognized filepath CSV files
    filepath_csv_files = glob.glob(os.path.join(filepath_lists_dir, '*.csv'))
    print("Recognized filepath CSV files:")
    for csv_file in filepath_csv_files:
        print(f"- {os.path.basename(csv_file)}")
    print(f"Total filepath CSV files: {len(filepath_csv_files)}\n")

    results = []

    for artifact_file in list(glob.glob(os.path.join(artifacts_dir, '*.py'))):
        module_name = os.path.splitext(os.path.basename(artifact_file))[0]
        artifacts, is_v2 = get_artifacts(artifact_file)

        if artifacts:
            print(f"Processing {module_name}")
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
                for list_file in filepath_csv_files:
                    list_file_name = os.path.basename(list_file)
                    
                    with open(list_file, 'r') as f:
                        reader = csv.reader(f)
                        next(reader)
                        filepaths = [row[0] for row in reader]

                    for pattern in search_patterns:
                        start_time = time.time()
                        count = count_matches(pattern, filepaths)
                        end_time = time.time()
                        search_time = end_time - start_time
                        
                        results.append([
                            module_name,
                            artifact_name,
                            pattern,
                            list_file_name,
                            count,
                            f"{search_time:.4f}"
                        ])
        else:
            print(f"Skipping {module_name} due to parsing errors")

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Module Name', 'Artifact Name', 'Search Pattern', 'List File Name', 'Count', 'Search Time (s)'])
        writer.writerows(results)

    print(f"\nResults written to {output_file}")

    # Generate and update summary table
    summary_table = generate_summary_table(results)
    update_markdown_file(summary_table)
    print(f"Summary table updated in admin/docs/filepath_search_summary.md")

if __name__ == "__main__":
    main()
