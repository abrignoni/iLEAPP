import os
import csv
import glob
import ast
import time
from fnmatch import fnmatch

def get_artifacts_v2(file_path):
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read())
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == '__artifacts_v2__':
                    return ast.literal_eval(node.value)
    return None

def count_matches(pattern, filepath_list):
    count = 0
    for filepath in filepath_list:
        if fnmatch(filepath, pattern):
            count += 1
    return count

def main():
    artifacts_dir = 'scripts/artifacts'
    filepath_lists_dir = 'admin/data/filepath-lists'
    output_file = 'admin/docs/filepath_results.csv'

    results = []

    for artifact_file in list(glob.glob(os.path.join(artifacts_dir, '*.py'))):
        module_name = os.path.splitext(os.path.basename(artifact_file))[0]
        artifacts_v2 = get_artifacts_v2(artifact_file)

        if artifacts_v2:
            print(f"Processing {module_name}")
            for artifact_name, artifact_data in artifacts_v2.items():
                search_patterns = artifact_data['paths']
                
                # Ensure search_patterns is always a list
                if isinstance(search_patterns, str):
                    search_patterns = [search_patterns]

                # Process filepath list files
                for list_file in glob.glob(os.path.join(filepath_lists_dir, '*.csv')):
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

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Module Name', 'Artifact Name', 'Search Pattern', 'List File Name', 'Count', 'Search Time (s)'])
        writer.writerows(results)

    print(f"Results written to {output_file}")

if __name__ == "__main__":
    main()
