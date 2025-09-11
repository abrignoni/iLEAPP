"""
Parses artifact modules to generate comprehensive documentation.

This script scans all Python files in the 'scripts/artifacts' directory to
extract metadata about the artifacts they define. It supports two formats for
artifact definitions: a legacy `__artifacts__` (v1) dictionary and a newer,
more detailed `__artifacts_v2__` dictionary.

The script processes each module to determine its artifact version and extracts
relevant details. For v2 artifacts, it captures the name, description, search
paths, output types, icon, version, and last update date. For v1 artifacts, it
simply lists the artifact names.

Finally, it aggregates all this information and generates a detailed summary in a
Markdown file ('admin/docs/generated/module_info.md'). The summary includes:
- A statistical overview (total modules, v1/v2 artifact counts, etc.).
- A detailed table for v2 artifacts.
- A simpler table for v1 artifacts.
- A table listing any modules that caused parsing errors.

This provides a centralized, auto-generated reference for all artifacts in the
project, which is kept up-to-date by running this script.
"""
import os
import re

# Get the root directory of the repository (2 directories above the script)
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Define key paths and constants
ARTIFACTS_DIR = os.path.join(REPO_ROOT, 'scripts', 'artifacts')
MD_FILE_PATH = os.path.join(REPO_ROOT, 'admin', 'docs', 'generated', 'module_info.md')
GITHUB_MODULE_URL = "/scripts/artifacts/"
START_MARKER = "<!-- MODULE_INFO_START -->"
END_MARKER = "<!-- MODULE_INFO_END -->"


def clean_string(s):
    """
    Sanitize a string by removing line breaks and limiting its length.

    Args:
        s (str): The input string to clean.

    Returns:
        str: The cleaned and truncated string.
    """
    return ' '.join(s.split())[:150]


def extract_v2_info(module_content):
    """
    Extract artifact information from a v2 `__artifacts_v2__` block.

    This function uses regular expressions to find the v2 artifact dictionary
    and then `exec` to safely evaluate it in a restricted scope.

    Args:
        module_content (str): The string content of the Python module.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary contains
                    the details for a single v2 artifact. Returns a list
                    with an error dictionary if parsing fails.
    """
    pattern = re.compile(r"__artifacts_v2__.*\}\n}\n", re.DOTALL)
    match = pattern.search(module_content)
    if not match:
        return []

    artifact_block = match.group(0)  # Get just the dictionary content

    try:
        # Create a local dictionary to store the executed result
        local_dict = {}
        exec(f"__artifacts_v2__ = {artifact_block}", {}, local_dict)
        artifacts_dict = local_dict['__artifacts_v2__']
    except Exception as e:
        return [{
            "artifact": "ERROR",
            "name": "Error parsing v2 artifact",
            "description": clean_string(str(e)),
            "paths": "",
            "output_types": "",
            "version": "",
            "last_update_date": "",
            "artifact_icon": ""
        }]

    results = []
    for artifact_name, details in artifacts_dict.items():
        paths = details.get("paths", "")
        if isinstance(paths, (list, tuple)):
            paths = [f'`{path}`' for path in paths]
        else:
            paths = f'`{paths}`'
        
        output_types = details.get("output_types", "")
        if output_types:
            if isinstance(output_types, (list, tuple)):
                output_types = ', '.join(output_types)
            else:
                output_types = str(output_types)
        else:
            output_types = ""
        
        version = details.get("version", "")
        last_update_date = details.get("last_update_date", "")
        artifact_icon = details.get("artifact_icon", "")
        results.append({
            "artifact": artifact_name,
            "name": clean_string(details.get("name", "")),
            "description": clean_string(details.get("description", "")),
            "paths": paths,
            "output_types": output_types,
            "version": version,
            "last_update_date": last_update_date,
            "artifact_icon": artifact_icon
        })
    return results


def extract_v1_info(module_content):
    """
    Extract artifact names from a legacy v1 `__artifacts__` block.

    Args:
        module_content (str): The string content of the Python module.

    Returns:
        list[str]: A list of artifact names found in the block.
    """
    pattern = re.compile(r"__artifacts__\s*=\s*{(.*?)}", re.DOTALL)
    match = pattern.search(module_content)
    if not match:
        return []

    artifact_block = match.group(1)
    artifact_names = re.findall(r'"(\w+)":', artifact_block)
    return artifact_names


def parse_module_file(module_path):
    """
    Parse a module file to extract artifact details for either v1 or v2.

    Args:
        module_path (str): The path to the artifact module file.

    Returns:
        tuple[str, list]: A tuple containing the artifact version ('v1', 'v2',
                          or 'error') and a list of the extracted artifact
                          details or error messages.
    """
    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "__artifacts_v2__" in content:
            return "v2", extract_v2_info(content)
        elif "__artifacts__" in content:
            return "v1", extract_v1_info(content)
        else:
            return "error", ["No recognized artifacts found"]
    except Exception as e:
        return "error", [f"Error reading file: {clean_string(str(e))}"]


def generate_v2_markdown_table(artifact_data):
    """
    Generate a markdown table for v2 artifacts.

    Args:
        artifact_data (dict): A dictionary mapping module names to their
                              v2 artifact data.

    Returns:
        str: A string containing the formatted markdown table.
    """
    table = "| Module | Artifact | Name | Output Types | Icon | Version | Last Update Date | Description | Paths |\n"
    table += "|--------|----------|------|--------------|------|---------|------------------|-------------|-------|\n"
    for module, artifacts in artifact_data.items():
        module_link = f"[{module}]({GITHUB_MODULE_URL}{module})"
        for artifact in artifacts:
            name = clean_string(artifact.get('name', ''))
            description = clean_string(artifact.get('description', ''))
            paths = artifact.get('paths', '')
            if isinstance(paths, (list, tuple)):
                paths = ', '.join(f'`{path}`' for path in paths)
            else:
                paths = f'`{paths}`'
            output_types = artifact.get('output_types', '-')
            artifact_icon = artifact.get('artifact_icon', '')
            version = artifact.get('version', '')
            last_update_date = artifact.get('last_update_date', '')
            table += f"| {module_link} | {artifact['artifact']} | {name} | {output_types} | {artifact_icon} | {version} | {last_update_date} | {description} | {paths} |\n"

    return table


def generate_v1_markdown_table(artifact_data):
    """
    Generate a markdown table for v1 artifacts.

    Args:
        artifact_data (dict): A dictionary mapping module names to their
                              v1 artifact data.

    Returns:
        str: A string containing the formatted markdown table.
    """
    table = "| Module | Artifacts |\n"
    table += "|--------|----------|\n"
    for module, artifacts in artifact_data.items():
        module_link = f"[{module}]({GITHUB_MODULE_URL}{module})"
        artifacts_str = ', '.join(artifacts)
        table += f"| {module_link} | {artifacts_str} |\n"
    return table


def generate_error_markdown_table(error_data):
    """
    Generate a markdown table for modules with errors.

    Args:
        error_data (dict): A dictionary mapping module names to the
                           errors encountered.

    Returns:
        str: A string containing the formatted markdown table for errors.
    """
    table = "| Module | Error/Issue |\n"
    table += "|--------|-------------|\n"
    for module, errors in error_data.items():
        error_str = ', '.join(map(clean_string, errors))
        table += f"| {module} | {error_str} |\n"
    return table


def update_markdown_file(v1_data, v2_data, error_data):
    """
    Update the markdown file with the parsed artifact data and summary.

    This function calculates summary statistics, generates markdown tables for
    v1, v2, and error data, and then replaces a designated section in the
    markdown file with this new content.

    Args:
        v1_data (dict): Data for v1 artifacts.
        v2_data (dict): Data for v2 artifacts.
        error_data (dict): Data for modules with errors.
    """
    total_modules = len(v1_data) + len(v2_data) + len(error_data)
    v1_count = sum(len(artifacts) for artifacts in v1_data.values())
    v2_count = sum(len(artifacts) for artifacts in v2_data.values())
    error_count = len(error_data)

    # Count modules with 'lava output'
    lava_output_count = sum(
        1 for artifacts in v2_data.values()
        for artifact in artifacts
        if artifact.get('output_types')
    )

    # Count modules using 'artifact_icon'
    artifact_icon_count = sum(
        1 for artifacts in v2_data.values()
        for artifact in artifacts
        if artifact.get('artifact_icon')
    )

    # Count modules using 'version'
    version_count = sum(
        1 for artifacts in v2_data.values()
        for artifact in artifacts
        if artifact.get('version')
    )

    # Count modules using 'artifact_icon'
    last_update_date_count = sum(
        1 for artifacts in v2_data.values()
        for artifact in artifacts
        if artifact.get('last_update_date')
    )

    with open(MD_FILE_PATH, 'r', encoding='utf-8') as md_file:
        content = md_file.read()

    # Split the content into before, between, and after the markers
    before_marker, _ , after_marker = content.partition(START_MARKER)
    _, _ , after_info_marker = after_marker.partition(END_MARKER)

    # Generate new markdown content
    new_module_info = "## Summary\n\n"
    new_module_info += f"Total number of modules: {total_modules}  \n"
    new_module_info += f"Number of v1 artifacts: {v1_count}  \n"
    new_module_info += f"Number of v2 artifacts: {v2_count}  \n"
    new_module_info += f"Number of modules with 'lava output': {lava_output_count}  \n"
    new_module_info += f"Number of modules using 'artifact_icon': {artifact_icon_count}  \n"
    new_module_info += f"Number of modules using 'version': {version_count}  \n"
    new_module_info += f"Number of modules using 'last_update_date': {last_update_date_count}  \n"
    new_module_info += f"Number of modules with errors or no recognized artifacts: {error_count}  \n\n"
    
    if v2_data:
        new_module_info += "## V2 Artifacts Table\n\n"
        new_module_info += generate_v2_markdown_table(v2_data)
        new_module_info += "\n"
    
    if v1_data:
        new_module_info += "## V1 Artifacts Table\n\n"
        new_module_info += generate_v1_markdown_table(v1_data)
        new_module_info += "\n"
    
    if error_data:
        new_module_info += "## Modules with Errors or No Recognized Artifacts\n\n"
        new_module_info += generate_error_markdown_table(error_data)

    # Rebuild the file content with the updated section
    new_content = f"{before_marker}{START_MARKER}\n\n{new_module_info}\n{END_MARKER}{after_info_marker}"

    # Write the updated content back to the markdown file
    with open(MD_FILE_PATH, 'w', encoding='utf-8') as md_file:
        md_file.write(new_content)


def main():
    """
    Main function to drive the artifact parsing and documentation generation.

    It initializes data structures, iterates through all artifact modules,
    parses each file, sorts the collected data, and then calls the function
    to update the final markdown documentation file.
    """
    v1_data = {}
    v2_data = {}
    error_data = {}
    
    print(f"Scanning directory: {ARTIFACTS_DIR}")
    # Scan the artifacts directory for module files
    for module_file in os.listdir(ARTIFACTS_DIR):
        module_path = os.path.join(ARTIFACTS_DIR, module_file)
        if os.path.isfile(module_path):
            module_name = os.path.basename(module_path)
            print(f"Processing module: {module_name}")
            version, artifacts = parse_module_file(module_path)
            if version == "v1":
                v1_data[module_name] = artifacts
            elif version == "v2":
                v2_data[module_name] = artifacts
            else:
                error_data[module_name] = artifacts
    
    # Sort the artifact_data dictionaries by keys (module filenames)
    v1_data = dict(sorted(v1_data.items()))
    v2_data = dict(sorted(v2_data.items()))
    error_data = dict(sorted(error_data.items()))
    
    print("Debug: v1_data =", v1_data)
    print("Debug: v2_data =", v2_data)
    print("Debug: error_data =", error_data)
    
    # Update the markdown file with the sorted artifact data
    update_markdown_file(v1_data, v2_data, error_data)
    print(f"\nMarkdown file updated: {MD_FILE_PATH}")

if __name__ == "__main__":
    main()
