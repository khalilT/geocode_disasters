import os

def create_folder_structure(base_dir):
    """Creates the folder structure for the project."""
    folders = [
        os.path.join(base_dir, "src"),
        os.path.join(base_dir, "src", "utils"),
        os.path.join(base_dir, "scripts"),
        os.path.join(base_dir, "data"),
        os.path.join(base_dir, "notebooks"),
        os.path.join(base_dir, "figures"),
    ]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    
    # Add __init__.py to src
    init_file = os.path.join(base_dir, "src", "__init__.py")
    with open(init_file, "w") as f:
        f.write("# src package initialization\n")
    print("Folder structure created, including __init__.py for src.")

   # Add .gitignore file
    gitignore_content = '''# Ignore Python cache files
__pycache__/
*.pyc
*.pyo

# Ignore virtual environments
venv/
.env/

# Ignore data files
/data/*
!/data/.gitkeep

# Ignore Jupyter Notebook checkpoints
**/.ipynb_checkpoints/

# Ignore metadata generation
create_project_structure.py
generate_readme_info.py
README_template.md

# Ignore system files
.DS_Store
Thumbs.db'''
    gitignore_file = os.path.join(base_dir, ".gitignore")
    with open(gitignore_file, "w") as f:
        f.write(gitignore_content)
    print("Folder structure created, including __init__.py for src and .gitignore.")

def create_paths_py(src_utils_dir):
    """Creates the paths.py file in src/utils."""
    paths_content = '''import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DATA_PATHS = {
    "remote_data": "/path/to/cluster/data1",
}

def get_path(name):
    """
    Retrieve the path for a given dataset name.
    Raises KeyError if the name is not found.
    """
    if name in DATA_PATHS:
        return DATA_PATHS[name]
    raise KeyError(f"No path found for dataset '{name}'")
'''
    paths_file = os.path.join(src_utils_dir, "paths.py")
    with open(paths_file, "w") as f:
        f.write(paths_content)
    print("paths.py created.")
    
def create_functions_py(src_utils_dir):
    """Creates the functions.py file in src/utils."""
    paths_content = '''#module containing functions
    '''
    paths_file = os.path.join(src_utils_dir, "functions.py")
    with open(paths_file, "w") as f:
        f.write(paths_content)
    print("functions.py created.")
    
def create_constants_py(src_utils_dir):
    """Creates the constants.py file in src/utils."""
    paths_content = '''#module containing constants
    '''
    paths_file = os.path.join(src_utils_dir, "constants.py")
    with open(paths_file, "w") as f:
        f.write(paths_content)
    print("constants.py created.")

def create_generate_readme_info(base_dir):
    """Creates the generate_readme_info.py script in the base directory."""
    readme_generator_content = '''
import os
import platform
import sys
from datetime import datetime
import pkg_resources

def generate_session_info():
    """Generate session info including Python version, platform, and more."""
    info = {
        "Python Version": sys.version,
        "Platform": platform.platform(),
        "OS": platform.system(),
        "Architecture": platform.architecture()[0],
        "Processor": platform.processor(),
        "Generated On": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return info

def generate_requirements(output_path="requirements.txt"):
    """Generate a requirements.txt file for the current environment."""
    installed_packages = sorted(
        [(d.project_name, d.version) for d in pkg_resources.working_set],
        key=lambda x: x[0].lower()
    )
    with open(output_path, "w") as f:
        for package, version in installed_packages:
            f.write(f"{package}=={version}\\n")
    print(f"Requirements file generated at {output_path}")

def generate_readme_content(readme_template_path, output_path):
    """Generate README.md with session info included."""
    # Load the base README template
    with open(readme_template_path, "r") as f:
        readme_content = f.read()
    
    # Generate session info
    session_info = generate_session_info()
    session_info_text = "\\n".join(f"- **{key}**: {value}" for key, value in session_info.items())
    
    # Append session info to the README
    readme_content += "\\n\\n## **Session Info**\\n\\n"
    readme_content += session_info_text
    
    # Write the updated README content to a file
    with open(output_path, "w") as f:
        f.write(readme_content)
    print(f"README file generated at {output_path}")

if __name__ == "__main__":
    # Paths for the README template and output
    TEMPLATE_PATH = "README_template.md"
    README_PATH = "README.md"
    REQUIREMENTS_PATH = "requirements.txt"
    
    # Generate requirements.txt
    generate_requirements(REQUIREMENTS_PATH)
    
    # Generate README.md
    generate_readme_content(TEMPLATE_PATH, README_PATH)
'''
    readme_generator_file = os.path.join(base_dir, "generate_readme_info.py")
    with open(readme_generator_file, "w") as f:
        f.write(readme_generator_content)
    print("generate_readme_info.py created.")

def create_readme_template(base_dir):
    """Creates the README_template.md file in the base directory."""
    readme_template_content = '''# Project Name

A Python project for centralized and FAIR data path management.

## **Overview**

This project simplifies data handling with centralized path management.

## **Installation**

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/yourproject.git
   cd yourproject
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
'''
    readme_template_file = os.path.join(base_dir, "README_template.md")
    with open(readme_template_file, "w") as f:
        f.write(readme_template_content)
    print("README_template.md created.")

def main():
    base_dir = os.getcwd()

    create_folder_structure(base_dir)
    create_paths_py(os.path.join(base_dir, "src", "utils"))
    create_functions_py(os.path.join(base_dir, "src", "utils"))
    create_constants_py(os.path.join(base_dir, "src", "utils"))
    create_generate_readme_info(base_dir)
    create_readme_template(base_dir)
    print("Project setup complete.")

if __name__ == "__main__":
    main()

