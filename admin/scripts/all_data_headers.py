import os
import csv
import ast
import sys
import json
import tempfile
import subprocess
import argparse
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Set
import re

# Add the root directory to Python path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)

class HeadersFinder(ast.NodeVisitor):
    def __init__(self):
        self.headers_by_function = {}
        
    def visit_FunctionDef(self, node):
        # Check if function has artifact_processor decorator
        if any(isinstance(d, ast.Name) and d.id == 'artifact_processor' for d in node.decorator_list):
            # Look for data_headers assignment
            for n in ast.walk(node):
                if isinstance(n, ast.Assign):
                    for target in n.targets:
                        if isinstance(target, ast.Name) and target.id == 'data_headers':
                            try:
                                self.headers_by_function[node.name] = ast.literal_eval(n.value)
                            except Exception as e:
                                print(f"    Error evaluating headers in {node.name}: {str(e)}")
        self.generic_visit(node)

def collect_data_headers():
    """Collect all headers from artifact processors"""
    headers_by_module = {}
    artifacts_dir = os.path.join(root_dir, "scripts/artifacts")
    
    print(f"Searching for artifacts in: {artifacts_dir}")
    
    # Walk through all python files in the artifacts directory
    for root, _, files in os.walk(artifacts_dir):
        for file in files:
            if file.endswith('.py'):
                module_path = os.path.join(root, file)
                module_name = os.path.splitext(file)[0]
                
                print(f"\nProcessing {module_name}...")
                
                try:
                    # Read and parse the file
                    with open(module_path, 'r') as f:
                        tree = ast.parse(f.read())
                    
                    # Find headers in decorated functions
                    finder = HeadersFinder()
                    finder.visit(tree)
                    
                    if finder.headers_by_function:
                        for func_name, headers in finder.headers_by_function.items():
                            headers_by_module[f"{module_name}.{func_name}"] = headers
                            print(f"  Found headers in {func_name}: {headers}")
                
                except Exception as e:
                    print(f"Error processing {module_path}: {str(e)}")
    
    print(f"\nFound headers from {len(headers_by_module)} modules")
    return headers_by_module

def export_to_csv(headers_by_module, output_file='all_data_headers.csv'):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Module', 'Artifact', 'Header Name', 'Type'])
        
        for full_name, headers in headers_by_module.items():
            # Split module and artifact names
            module_name, artifact_name = full_name.split('.')
            
            # Convert headers to list if it's a tuple
            headers_list = list(headers) if isinstance(headers, tuple) else headers
            
            # Process each header
            for header in headers_list:
                if isinstance(header, tuple):
                    # Header is a tuple with name and type
                    writer.writerow([module_name, artifact_name, f'"{header[0]}"', header[1]])
                else:
                    # Header is just a string
                    writer.writerow([module_name, artifact_name, f'"{header}"', ''])

def check_translations(headers: Set[str], repo_url: str, repo_path: str, is_github_action: bool, local_repo: str = None) -> tuple[Dict[str, List[str]], Dict[str, Dict[str, str]]]:
    """Check which headers are missing translations"""
    missing_translations = {header: [] for header in headers}
    translations = {}
    
    # If using local repo, construct the full path
    if local_repo:
        lang_dir = Path(local_repo) / repo_path
        print(f"Using local repo: {lang_dir}")
    else:
        # Git clone logic for remote repo
        if is_github_action:
            temp_dir = os.path.join(os.environ.get('GITHUB_WORKSPACE', ''), 'temp_i18n')
        else:
            temp_dir = tempfile.mkdtemp()
            
        os.makedirs(temp_dir, exist_ok=True)
        print(f"Using temp directory: {temp_dir}")
        
        try:
            # Git operations...
            subprocess.run(['git', 'init'], cwd=temp_dir, capture_output=True)
            subprocess.run(['git', 'remote', 'add', 'origin', repo_url], cwd=temp_dir)
            subprocess.run(['git', 'config', 'core.sparseCheckout', 'true'], cwd=temp_dir)
            
            sparse_checkout_path = Path(temp_dir) / '.git' / 'info' / 'sparse-checkout'
            sparse_checkout_content = f"{repo_path}/*/translation.json\n"
            sparse_checkout_path.write_text(sparse_checkout_content)
            
            subprocess.run(['git', 'pull', 'origin', 'main', '--depth=1'], cwd=temp_dir)
            lang_dir = Path(temp_dir) / repo_path
        
        finally:
            if not is_github_action and not local_repo:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    # Process translations
    print(f"\nLooking for translations in: {lang_dir}")
    if lang_dir.exists():
        print("Found directories:")
        for d in lang_dir.iterdir():
            if d.is_dir():
                print(f"  {d.name}")
                trans_file = d / 'translation.json'
                if trans_file.exists():
                    print(f"    Found translation file")
                    try:
                        all_translations = json.loads(trans_file.read_text())
                        artifact_translations = all_translations.get('artifacts', {})
                        print(f"    Found {len(artifact_translations)} translations")
                        
                        lang_code = d.name
                        # Check each header against this language file
                        for header in headers:
                            i18n_key = title_to_i18n_key(header)
                            translation = artifact_translations.get(i18n_key)
                            
                            if translation:  # Translation exists
                                if header not in translations:
                                    translations[header] = {}
                                translations[header][lang_code] = translation
                            else:  # Translation is missing
                                missing_translations[header].append(lang_code)
                                
                    except Exception as e:
                        print(f"    Error processing {trans_file}: {str(e)}")
    else:
        print(f"Translation directory not found: {lang_dir}")
    
    # Remove headers that aren't missing any translations
    missing_translations = {k: v for k, v in missing_translations.items() if v}
    
    print(f"\nFound translations for {len(translations)} headers")
    print(f"Found missing translations for {len(missing_translations)} headers")
    
    return missing_translations, translations

def title_to_i18n_key(header: str) -> str:
    """Convert a Title Case header to i18n key format"""
    # If header is a tuple, get just the name part
    if isinstance(header, tuple):
        header = header[0]
        
    # Convert to lowercase
    key = header.lower()
    
    # Replace spaces and special chars with hyphens
    key = re.sub(r'[^a-z0-9]+', '-', key)
    
    # Remove leading/trailing hyphens
    key = key.strip('-')
    
    # Remove duplicate hyphens
    key = re.sub(r'-+', '-', key)
    
    return key

def update_markdown(headers_by_module: dict, missing: dict, translations: dict, output_file: str):
    """Update the markdown file with headers data and translations"""
    # Get header usage counts and locations
    header_counts = Counter()
    header_locations = defaultdict(list)
    for module_name, module_headers in headers_by_module.items():
        for header in module_headers:
            header_name = header[0] if isinstance(header, tuple) else header
            header_counts[header_name] += 1
            header_locations[header_name].append(module_name)
    
    # Get unique headers and sort alphabetically
    unique_headers = sorted(header_counts.keys(), key=str.lower)
    
    # Build translations section
    translations_content = "## Headers and Translations\n\n"
    
    for header in unique_headers:
        i18n_key = f"artifacts.{title_to_i18n_key(header)}"
        missing_count = len(missing.get(header, []))
        
        # Header and key
        translations_content += f"### {header}\n"
        translations_content += f"i18n key: `{i18n_key}`\n\n"
        
        # Usage collapsible
        translations_content += "<details>\n"
        translations_content += f"<summary>Used in {header_counts[header]} artifact{'s' if header_counts[header] != 1 else ''}</summary>\n\n"
        for module in sorted(header_locations[header]):
            translations_content += f"- {module}\n"
        translations_content += "\n</details>\n\n"
        
        # Translations collapsible (only if we have any translations or missing ones)
        if header in translations or missing_count > 0:
            translations_content += "<details>\n"
            if missing_count > 0:
                translations_content += f"<summary>❌ Missing {missing_count} translation{'s' if missing_count > 1 else ''}</summary>\n\n"
            else:
                translations_content += "<summary>✅ All translations available</summary>\n\n"
            
            # List existing translations
            if header in translations:
                for lang, trans in sorted(translations[header].items()):
                    translations_content += f"- {lang}: {trans}\n"
            translations_content += "\n</details>\n\n"
        
        translations_content += "\n"
    
    # Add statistics
    stats = f"""## Statistics
- Total unique headers: {len(unique_headers)}
- Headers with complete translations: {len(unique_headers) - len(missing)}
- Headers missing translations: {len(missing)}
"""
    
    # Read template and update content
    with open(output_file, 'r') as f:
        content = f.read()
    
    # Update sections
    content = replace_section(content, "STATS_START", "STATS_END", stats)
    content = replace_section(content, "HEADERS_START", "HEADERS_END", translations_content)
    
    # Write updated content
    with open(output_file, 'w') as f:
        f.write(content)

def update_missing_translations(headers: dict, missing: dict, output_file: str):
    """Update the missing translations table in the documentation"""
    # Get list of all languages from translation files
    languages = set()
    for langs in missing.values():
        languages.update(langs)
    languages = sorted(languages)
    
    print(f"Found languages: {languages}")
    print(f"Missing translations for {len(missing)} headers")
    
    if not languages or not missing:
        print("No missing translations to document")
        return
    
    # Create table content
    table_content = "| Header | i18n Key | " + " | ".join(languages) + " |\n"
    table_content += "|--------|----------|" + "|".join(["-" * len(lang) for lang in languages]) + "|\n"
    
    # Add each header with missing translations
    for header in sorted(missing.keys(), key=str.lower):
        i18n_key = f"{title_to_i18n_key(header)}"
        row = [header, i18n_key]
        for lang in languages:
            row.append("❌" if lang in missing[header] else "✅")
        table_content += "| " + " | ".join(row) + " |\n"
    
    # Read existing content
    try:
        with open(output_file, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Warning: {output_file} not found. Creating new file.")
        content = """# Missing Header Translations

This document shows which headers are missing translations in one or more languages. The data below is generated by the [@all_data_headers.py](https://github.com/abrignoni/iLEAPP/blob/main/admin/scripts/all_data_headers.py) script.

## Overview
Headers should have translations in all supported languages. This document helps identify gaps in translation coverage. Headers are listed only if they are missing one or more translations.

<!-- MISSING_TRANSLATIONS_START -->
<!-- MISSING_TRANSLATIONS_END -->

## Notes
- ✅ indicates a translation exists
- ❌ indicates a missing translation
- Headers are converted to i18n keys by:
  - Converting to lowercase
  - Replacing spaces and special characters with hyphens
  - Removing duplicate hyphens
- New translations should be added to the appropriate language file under the `artifacts` object"""
    
    # Replace only the table section
    content = replace_section(content, "MISSING_TRANSLATIONS_START", "MISSING_TRANSLATIONS_END", table_content)
    
    # Write updated content
    with open(output_file, 'w') as f:
        f.write(content)

def replace_section(content: str, start_marker: str, end_marker: str, new_content: str) -> str:
    """Replace content between markers in markdown"""
    start = content.find(f"<!-- {start_marker} -->")
    end = content.find(f"<!-- {end_marker} -->")
    if start == -1 or end == -1:
        return content
    
    before = content[:start + len(f"<!-- {start_marker} -->")]
    after = content[end:]
    return f"{before}\n{new_content}\n{after}"

def main():
    parser = argparse.ArgumentParser(description='Update headers documentation')
    parser.add_argument('--github-action', action='store_true', 
                       help='Running as GitHub Action')
    parser.add_argument('--local-repo', 
                       help='Path to local LAVA repo (relative to iLEAPP root)',
                       default=None)
    args = parser.parse_args()

    # Configuration
    repo_url = "https://github.com/abrignoni/LAVA.git"
    repo_path = "src/renderer/locales"
    output_file = "admin/docs/module_language_list.md"
    missing_file = "admin/docs/module_language_missing.md"
    csv_file = "admin/docs/all_data_headers.csv"

    # If using local repo, construct full path
    local_repo = None
    if args.local_repo:
        local_repo = os.path.join(root_dir, args.local_repo)
        if not os.path.exists(local_repo):
            print(f"Error: Local repo not found at {local_repo}")
            sys.exit(1)
        print(f"Using local repo at: {local_repo}")

    # Collect and analyze headers
    headers_by_module = collect_data_headers()
    
    # Get unique headers
    unique_headers = set()
    for module_headers in headers_by_module.values():
        for header in module_headers:
            if isinstance(header, tuple):
                unique_headers.add(header[0])
            else:
                unique_headers.add(header)
    
    # Check translations
    missing, translations = check_translations(
        headers=unique_headers,
        repo_url=repo_url,
        repo_path=repo_path,
        is_github_action=args.github_action,
        local_repo=local_repo
    )

    export_to_csv(headers_by_module, csv_file)
    
    # Update documentation
    update_markdown(headers_by_module, missing, translations, output_file)
    update_missing_translations(unique_headers, missing, missing_file)

    print(f"\nDocumentation updated:")
    print(f"- Main documentation: {output_file}")
    print(f"- Missing translations: {missing_file}")

if __name__ == '__main__':
    main()