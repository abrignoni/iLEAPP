import os
import re

# Get the root directory of the repository (2 directories above the script location)
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Adjust paths relative to the repository root
ARTIFACTS_DIR = os.path.join(REPO_ROOT, 'scripts', 'artifacts')
MD_FILE_PATH = os.path.join(REPO_ROOT, 'admin', 'docs', 'module_info.md')

START_MARKER = "<!-- MODULE_INFO_START -->"
END_MARKER = "<!-- MODULE_INFO_END -->"

def clean_string(s):
    """Remove line breaks and limit string length."""
    return ' '.join(s.split())[:150]

def extract_v2_info(module_content):
    """Extract artifact information from a v2 block."""
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
    """Extract artifact names from a v1 block."""
    pattern = re.compile(r"__artifacts__\s*=\s*{(.*?)}", re.DOTALL)
    match = pattern.search(module_content)
    if not match:
        return []

    artifact_block = match.group(1)
    artifact_names = re.findall(r'"(\w+)":', artifact_block)
    return artifact_names

def parse_module_file(module_path):
    """Parse a module file and return the artifact details."""
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
    """Generate a markdown table for v2 artifacts."""
    table = "| Module | Artifact | Name | Output Types | Icon | Version | Last Update Date | Description | Paths |\n"
    table += "|--------|----------|------|--------------|------|---------|------------------|-------------|-------|\n"
    for module, artifacts in artifact_data.items():
        module_link = f"[{module}](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/{module})"
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
    """Generate a markdown table for v1 artifacts."""
    table = "| Module | Artifacts |\n"
    table += "|--------|----------|\n"
    for module, artifacts in artifact_data.items():
        module_link = f"[{module}](https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/{module})"
        artifacts_str = ', '.join(artifacts)
        table += f"| {module_link} | {artifacts_str} |\n"
    return table

def generate_error_markdown_table(error_data):
    """Generate a markdown table for modules with errors or no recognized artifacts."""
    table = "| Module | Error/Issue |\n"
    table += "|--------|-------------|\n"
    for module, errors in error_data.items():
        error_str = ', '.join(map(clean_string, errors))
        table += f"| {module} | {error_str} |\n"
    return table

def update_markdown_file(v1_data, v2_data, error_data):
    """Update the markdown file with the parsed artifact data."""
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

    with open(MD_FILE_PATH, 'r') as md_file:
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
    with open(MD_FILE_PATH, 'w') as md_file:
        md_file.write(new_content)

def main():
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
