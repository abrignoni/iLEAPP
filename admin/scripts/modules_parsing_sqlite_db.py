import os
import re
import ast
from pathlib import Path

def find_function_calls(file_path, function_name):
    """
    Parse a Python file and find all calls to the specified function
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == function_name:
                    if function_name == 'open_sqlite_db_readonly':
                        return True
                    elif function_name == 'get_sqlite_db_records':
                        return True
    except:
        return False
    

def generate_markdown():
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent.parent
    
    artifacts_dir = Path( root_dir, 'scripts/artifacts')
    open_sqlite_db_readonly = []
    get_sqlite_db_records = []
    
    # Scan all Python files in artifacts directory
    for file_path in artifacts_dir.glob('*.py'):
        module_name = file_path.stem
        
        # Find open_sqlite_db_readonly calls
        readonly_calls = find_function_calls(file_path, 'open_sqlite_db_readonly')
        if readonly_calls:
            open_sqlite_db_readonly.append(module_name)
        
        # Find get_sqlite_db_records calls
        get_records_calls = find_function_calls(file_path, 'get_sqlite_db_records')
        if get_records_calls:
            get_sqlite_db_records.append(module_name)
    
    # Generate markdown content
    readonly_md = "| Source Modules |\n|----------------|\n"
    for module in sorted(open_sqlite_db_readonly):
        readonly_md += f"| {module} |\n"
    
    get_records_md = "| Source Modules |\n|----------------|\n"
    for module in sorted(get_sqlite_db_records):
        get_records_md += f"| {module} |\n"
    
    # Read the existing markdown file
    doc_path = Path( root_dir, 'admin/docs/generated/modules_parsing_sqlite_db.md')
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the placeholders
    content = re.sub(
        r'<!-- GET_RECORDS_START -->.*<!-- GET_RECORDS_END -->',
        f'<!-- GET_RECORDS_START -->\n{get_records_md}<!-- GET_RECORDS_END -->',
        content,
        flags=re.DOTALL
    )
    content = re.sub(
        r'<!-- READONLY_START -->.*<!-- READONLY_END -->',
        f'<!-- READONLY_START -->\n{readonly_md}<!-- READONLY_END -->',
        content,
        flags=re.DOTALL
    )
    
    # Write the updated content
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    generate_markdown()
