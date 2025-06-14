# Singleton Storage System

A simple Python module for setting up organized project storage with YAML, JSON, and file management.

## Quick Start

```python
from persistent_storage_system.singleton_storage_fns import main

# Create storage at specific path
storage_path = main("/path/to/my/storage")

# Or create storage in container with auto-naming
storage_path = main("/path/to/container", 
                   path_is_only_to_container=True, 
                   semantic_id_of_proc="my_project")
```

## What Gets Created

### Structure
```
storage_folder/
├── main.yaml              # Main config
├── shared_storage.yaml    # Shared config
├── file_tree.yaml         # File structure info
├── tiny_db.json          # JSON database
├── old_yamls/            # YAML backups
└── files/                # General files
```

## Usage Patterns

### 1. Specific Storage Location
```python
# Creates storage at exact path (if doesn't exist)
# Returns existing path if already exists
storage_path = main("/my/project/storage")
```

### 2. Auto-Generated Storage
```python
# Creates uniquely named folder in container
storage_path = main("/my/projects", 
                   path_is_only_to_container=True,
                   semantic_id_of_proc="experiment_1")
# Creates: /my/projects/001_experiment_1/ (or next available number)
```

## Command Line Usage

```bash
# Create specific storage
python -m persistent_storage_system.singleton_storage_fns /path/to/storage

# Create auto-named storage
python -m persistent_storage_system.singleton_storage_fns /path/to/container \
  --path_is_only_to_container \
  --semantic_id_of_proc "my_experiment"
```

## File Access Helper

Use `SetupNames` class to avoid hardcoded strings:

```python
from persistent_storage_system.singleton_storage_fns import SetupNames

sn = SetupNames()
main_config = storage_path / sn.MAIN_YAML
database = storage_path / sn.TINY_DB_JSON
files_dir = storage_path / sn.FILES_FOLDER
...
```

## Project Structure Requirements

- Place `persistent_storage_system/` in your project root
- Run from project root directory for relative imports
- Or use absolute paths

```
your_project/
├── persistent_storage_system/  ← This module
│   ├── persistent_storage_fns.py
│   ├── singleton_storage_fns
│   ├── setup.py
│   ├── yaml_handler.py
│   └── json_handler.py
└── your_code.py
```

## Key Features

- **Safe**: Won't overwrite existing storage
- **Organized**: Consistent folder structure
- **Flexible**: Works with specific or auto-generated paths
- **Type-safe**: `SetupNames` class prevents typos