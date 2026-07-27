"""
Collects artifact processor headers and manages their translations.

This script performs several key functions to maintain artifact data headers
and their internationalization (i18n) status:

1.  **Collects Headers**: It traverses all Python files in the
    `scripts/artifacts` directory, parsing the AST to find all functions
    decorated with `@artifact_processor`. Within these functions, it
    extracts the `data_headers` list.

2.  **Exports to CSV**: All collected headers are exported to a CSV file
    at `admin/docs/all_data_headers.csv`, mapping each header to its
    source module and artifact function.

3.  **Checks Translations**: It fetches translation files from the LAVA
    i18n repository (either by cloning it or using a local copy). It
    compares the collected headers against available translations to
    identify which headers are missing translations for which languages.

4.  **Updates Documentation**:
    - It updates `admin/docs/module_language_list.md` with a comprehensive
      list of all unique headers, where they are used, and their current
      translation status (including existing translations and a summary
      of missing ones).
    - It updates `admin/docs/module_language_missing.md` with a summary
      table showing exactly which headers are missing translations for
      each language.

The script can be run as part of a GitHub Action or locally. When run
locally, it can be pointed to a local clone of the LAVA repository to avoid
network operations.

Usage:
    python admin/scripts/all_data_headers.py [--github-action] [--local-repo PATH]
"""

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
import shutil

# Add the root directory to Python path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)

from scripts.lavafuncs import sanitize_sql_name  # pylint: disable=wrong-import-position

class V2ArtifactInfoFinder(ast.NodeVisitor):
    """
    An AST node visitor that finds and extracts the `__artifacts_v2__`
    dictionary from a module.
    """
    def __init__(self):
        self.artifacts_v2 = {}

    def visit_Assign(self, node):  # pylint: disable=invalid-name
        """Visits an `Assign` node to find `__artifacts_v2__`."""
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == '__artifacts_v2__':
            try:
                self.artifacts_v2 = ast.literal_eval(node.value)
            except (ValueError, SyntaxError):
                # This can happen if the dictionary contains function calls (e.g., for paths).
                # Silently ignore these, as this script can only handle literal dictionaries.
                pass
        self.generic_visit(node)

class HeadersFinder(ast.NodeVisitor):
    """
    An AST node visitor that finds `data_headers` assignments within
    functions decorated with `@artifact_processor`.
    """
    def __init__(self):
        self.headers_by_function = {}
        self.errors = []

    def visit_FunctionDef(self, node):  # pylint: disable=invalid-name
        """
        Visits a `FunctionDef` node to find decorated artifact processors
        and extracts their `data_headers`.
        """
        # Check if function has artifact_processor decorator
        if any(isinstance(d, ast.Name) and d.id == 'artifact_processor' for d in node.decorator_list):
            # Look for data_headers assignment
            for n in ast.walk(node):
                if isinstance(n, ast.Assign):
                    for target in n.targets:
                        if isinstance(target, ast.Name) and target.id == 'data_headers':
                            try:
                                self.headers_by_function[node.name] = ast.literal_eval(n.value)
                            except (ValueError, SyntaxError, TypeError) as e:
                                self.errors.append({'function': node.name, 'error': str(e)})
        self.generic_visit(node)

def load_exclusions(file_path: str) -> tuple[Set[str], Set[str], Set[str]]:
    """Loads translation exclusion rules from a JSON file."""
    if not os.path.exists(file_path):
        return set(), set(), set()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        exclude_modules = set(data.get('exclude_modules', []))
        exclude_artifacts = set(data.get('exclude_artifacts', []))
        exclude_headers = set(data.get('exclude_headers', []))

        print(f"\nLoaded {len(exclude_modules)} modules, "
              f"{len(exclude_artifacts)} artifacts, and "
              f"{len(exclude_headers)} headers to exclude from translation checks.")

        return exclude_modules, exclude_artifacts, exclude_headers
    except (OSError, json.JSONDecodeError) as e:
        print(f"Warning: Could not read or parse exclusion file {file_path}: {e}")
        return set(), set(), set()

def collect_data_headers():
    """Collect all headers from artifact processors and identify unprocessed modules."""
    headers_by_module = {}
    expected_no_headers = []
    issues_to_resolve = []
    all_module_names = []
    processed_module_names = set()
    artifacts_dir = os.path.join(root_dir, "scripts/artifacts")

    print(f"Searching for artifacts in: {artifacts_dir}")

    # Walk through all python files in the artifacts directory
    for root, _, files in os.walk(artifacts_dir):
        for file in files:
            if file.endswith('.py'):
                module_path = os.path.join(root, file)
                module_name = os.path.splitext(file)[0]
                all_module_names.append(module_name)

                print(f"\nProcessing {module_name}...")

                try:
                    # Read and parse the file
                    with open(module_path, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())

                    # Find headers in decorated functions
                    finder = HeadersFinder()
                    finder.visit(tree)

                    # Find v2 artifact info
                    v2_finder = V2ArtifactInfoFinder()
                    v2_finder.visit(tree)
                    v2_info = v2_finder.artifacts_v2

                    # Keep track of functions that have been dealt with in this module
                    handled_functions = set()

                    if finder.headers_by_function:
                        processed_module_names.add(module_name)
                        for func_name, headers in finder.headers_by_function.items():
                            headers_by_module[f"{module_name}.{func_name}"] = headers
                            handled_functions.add(func_name)
                            print(f"  Found headers in {func_name}: {len(headers)}")

                    if finder.errors:
                        processed_module_names.add(module_name)
                        for error in finder.errors:
                            reason = (
                                f"Error in function '{error['function']}': "
                                f"Could not evaluate `data_headers`. "
                                f"Error: {error['error']}"
                            )
                            issues_to_resolve.append({'module_name': f"{module_name} ({error['function']})", 'reason': reason})
                            handled_functions.add(error['function'])

                    # For v2 artifacts, check functions that were defined but had no headers found
                    for func_name, info in v2_info.items():
                        if func_name not in handled_functions:
                            if info.get('output_types') == 'none':
                                reason = "V2 artifact with `output_types` set to `none`. No data table output is expected."
                                expected_no_headers.append({'module_name': f"{module_name} ({func_name})", 'reason': reason})
                                processed_module_names.add(module_name)

                except (OSError, SyntaxError, ValueError) as e:
                    print(f"Error processing {module_path}: {str(e)}")
                    issues_to_resolve.append({'module_name': module_name, 'reason': f'Error parsing file: {e}'})
                    processed_module_names.add(module_name) # Mark as processed to avoid double reporting

    # Now find modules that were not processed at all
    for module_name in sorted(all_module_names):
        if module_name not in processed_module_names:
            issues_to_resolve.append({
                'module_name': module_name,
                'reason': 'No `data_headers` found. This may be a v1 artifact or is missing the `@artifact_processor` decorator.'
            })

    print(f"\nFound headers from {len(headers_by_module)} functions across {len(processed_module_names)} modules")
    print(f"Found {len(expected_no_headers)} modules with no expected headers.")
    print(f"Found {len(issues_to_resolve)} modules/functions with issues.")
    return headers_by_module, expected_no_headers, issues_to_resolve

def export_to_csv(headers_by_module, output_file='all_data_headers.csv'):
    """Export headers to CSV file"""
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Module', 'Artifact', 'Header Name', 'SQL Safe Header Name', 'Type'])

        for full_name, headers in headers_by_module.items():
            # Split module and artifact names
            module_name, artifact_name = full_name.rsplit('.', 1)

            # Convert headers to list if it's a tuple
            headers_list = list(headers) if isinstance(headers, tuple) else headers

            # Process each header
            for header in headers_list:
                header_name = header[0] if isinstance(header, tuple) else header
                header_type = header[1] if isinstance(header, tuple) else ''
                sql_safe_name = sanitize_sql_name(header_name)
                writer.writerow([module_name, artifact_name, f'"{header_name}"', sql_safe_name, header_type])

def check_translations(
        headers: Set[str],
        repo_url: str,
        repo_path: str,
        is_github_action: bool,
        local_repo: str = None) -> tuple[Dict[str, List[str]], Dict[str, Dict[str, str]]]:
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
            subprocess.run(['git', 'init'], cwd=temp_dir, capture_output=True, check=True)
            subprocess.run(['git', 'remote', 'add', 'origin', repo_url], cwd=temp_dir, check=True)
            subprocess.run(['git', 'config', 'core.sparseCheckout', 'true'], cwd=temp_dir, check=True)

            sparse_checkout_path = Path(temp_dir) / '.git' / 'info' / 'sparse-checkout'
            sparse_checkout_content = f"{repo_path}/*/artifacts.json\n"
            sparse_checkout_path.write_text(sparse_checkout_content)

            subprocess.run(['git', 'pull', 'origin', 'main', '--depth=1'], cwd=temp_dir, check=True)
            lang_dir = Path(temp_dir) / repo_path

        finally:
            if not is_github_action and not local_repo:
                shutil.rmtree(temp_dir, ignore_errors=True)

    # Process translations
    print(f"\nLooking for translations in: {lang_dir}")
    if lang_dir.exists():
        print("Found directories:")
        for d in lang_dir.iterdir():
            if d.is_dir():
                print(f"  {d.name}")
                trans_file = d / 'artifacts.json'
                if trans_file.exists():
                    print("    Found artifacts translation file")
                    try:
                        artifact_translations = json.loads(trans_file.read_text(encoding='utf-8'))
                        print(f"    Found {len(artifact_translations)} translations")

                        lang_code = d.name
                        # Check each header against this language file
                        for header in headers:
                            i18n_key = title_to_i18n_key(header)
                            translation = artifact_translations.get(i18n_key)

                            if translation:  # Translation exists (and is not empty)
                                if header not in translations:
                                    translations[header] = {}
                                translations[header][lang_code] = translation
                            else:  # Translation is missing
                                missing_translations[header].append(lang_code)

                    except (OSError, json.JSONDecodeError) as e:
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
        # i18n_key = f"artifacts.{title_to_i18n_key(header)}"
        missing_count = len(missing.get(header, []))

        # Header and key
        sql_safe_name = sanitize_sql_name(header)
        translations_content += f"### {header}\n"
        translations_content += f"SQL-safe name: `{sql_safe_name}`\n\n"

        # Usage collapsible
        translations_content += "<details>\n"
        translations_content += (
            f"<summary>Used in {header_counts[header]} "
            f"artifact{'s' if header_counts[header] != 1 else ''}</summary>\n\n"
        )
        for module in sorted(header_locations[header]):
            translations_content += f"- {module}\n"
        translations_content += "\n</details>\n\n"

        # Translations collapsible (only if we have any translations or missing ones)
        if header in translations or missing_count > 0:
            translations_content += "<details>\n"
            if missing_count > 0:
                translations_content += (
                    f"<summary>❌ Missing {missing_count} "
                    f"translation{'s' if missing_count > 1 else ''}</summary>\n\n"
                )
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
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update sections
    content = replace_section(content, "STATS_START", "STATS_END", stats)
    content = replace_section(content, "HEADERS_START", "HEADERS_END", translations_content)

    # Write updated content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

def update_missing_translations(missing: dict, output_file: str):
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
    table_content = (
        "| Header | SQL Safe Header Name | "
        + " | ".join(languages)
        + " |\n"
    )
    table_content += (
        "|--------|----------------------|"
        + "|".join(["-" * len(lang) for lang in languages])
        + "|\n"
    )

    # Add each header with missing translations
    for header in sorted(missing.keys(), key=str.lower):
        sql_safe_name = sanitize_sql_name(header)
        row = [header, sql_safe_name]
        for lang in languages:
            row.append("❌" if lang in missing[header] else "✅")
        table_content += "| " + " | ".join(row) + " |\n"

    # Read existing content
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace only the table section
    content = replace_section(content, "MISSING_TRANSLATIONS_START", "MISSING_TRANSLATIONS_END", table_content)

    # Write updated content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

def update_no_headers_markdown(expected_no_headers: list, issues_to_resolve: list, output_file: str):
    """Update the markdown file with modules that could not be processed."""

    # Create table for expected no headers
    expected_table_content = "| Module | Reason |\n"
    expected_table_content += "|--------|--------|\n"
    for module in sorted(expected_no_headers, key=lambda x: x['module_name']):
        expected_table_content += f"| {module['module_name']} | {module['reason']} |\n"

    # Create table for issues to resolve
    issues_table_content = "| Module | Reason for a Lack of Headers |\n"
    issues_table_content += "|--------|------------------------------|\n"
    for module in sorted(issues_to_resolve, key=lambda x: x['module_name']):
        issues_table_content += f"| {module['module_name']} | {module['reason']} |\n"

    # Read existing content
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace sections
    content = replace_section(content, "EXPECTED_NO_HEADERS_START", "EXPECTED_NO_HEADERS_END", expected_table_content)
    content = replace_section(content, "ISSUES_TO_RESOLVE_START", "ISSUES_TO_RESOLVE_END", issues_table_content)

    # Write updated content
    with open(output_file, 'w', encoding='utf-8') as f:
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
    """
    Main entry point for the script.

    Parses command-line arguments, collects artifact headers, checks for
    translations, and generates CSV and markdown documentation files.
    """
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
    output_file = "admin/docs/generated/module_language_list.md"
    missing_file = "admin/docs/generated/module_language_missing.md"
    no_headers_file = "admin/docs/generated/module_language_no_headers.md"
    csv_file = "admin/data/generated/all_data_headers.csv"
    exclusion_file = "admin/scripts/translation_exclusions.json"

    # Determine local repo path
    local_repo = None
    if args.local_repo:
        # Use provided path if it exists
        candidate_path = os.path.join(root_dir, args.local_repo)
        if os.path.exists(candidate_path):
            local_repo = candidate_path
        else:
            print(f"Error: Provided local repo not found at {candidate_path}")
            sys.exit(1)
    else:
        # If no path provided, check for default sibling 'lava' directory
        default_lava_path = os.path.abspath(os.path.join(root_dir, '..', 'lava'))
        if os.path.exists(default_lava_path):
            local_repo = default_lava_path

    if local_repo:
        print(f"Using local LAVA repo at: {local_repo}")
    elif not args.github_action:
        # This branch is for when cloning is necessary
        # The check_translations function handles the case where local_repo is None
        print("Local LAVA repo not specified or found, will clone from GitHub.")

    # Load exclusions
    excluded_modules, excluded_artifacts, excluded_headers = load_exclusions(exclusion_file)

    # Collect and analyze headers
    headers_by_module, expected_no_headers, issues_to_resolve = collect_data_headers()

    # Get unique headers, applying exclusions
    unique_headers = set()
    for full_name, module_headers in headers_by_module.items():
        module_name, artifact_name = full_name.rsplit('.', 1)

        if module_name in excluded_modules:
            continue
        if artifact_name in excluded_artifacts:
            continue

        for header in module_headers:
            header_name = header[0] if isinstance(header, tuple) else header
            if header_name in excluded_headers:
                continue
            unique_headers.add(header_name)

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
    update_missing_translations(missing, missing_file)
    update_no_headers_markdown(expected_no_headers, issues_to_resolve, no_headers_file)

    print("\nDocumentation updated:")
    print(f"- Main documentation: {output_file}")
    print(f"- Missing translations: {missing_file}")
    print(f"- Modules without headers: {no_headers_file}")

if __name__ == '__main__':
    main()
