





## Implementation Notes

### Overflow Mechanism
When counters reach 100, functions add "#" to prefix and reset counter to 999:
- Normal: `999`, `998`, `997`...`101`, `100`
- Overflow: `#999`, `#998`...`##999`, `##998`...

### Base-62 Encoding
Alphanumeric functions use base-62 encoding with character set `[0-9A-Za-z]` for compact, readable identifiers.

### Error Handling
- Functions create necessary parent directories automatically
- Missing source files in backup operations are logged and skipped
- Collision detection prevents overwrites in all naming functions
# File System Utility Functions

A collection of Python functions for creating unique folders and filenames, managing backups, and handling file system operations.

## Key Design Principles

- **Reverse numbering**: Numeric functions count down from 999 to ensure newer items appear first in file explorers
- **Overflow handling**: When counters reach 100, adds "#" prefix and resets to 999 (e.g., "#999", "##999")
- **Path safety**: Functions ensure parent directories exist before operations


## Key Warnings Summary

1. **Shallow duplicate checking**: `make_non_duplicate_backups` only checks filenames, not file contents



## Implementation Notes

### Overflow Mechanism
When counters reach 100, functions add "#" to prefix and reset counter to 999:
- Normal: `999`, `998`, `997`...`101`, `100`
- Overflow: `#999`, `#998`...`##999`, `##998`...

### Base-62 Encoding
Alphanumeric functions use base-62 encoding with character set `[0-9A-Za-z]` for compact, readable identifiers.

### Error Handling
- Functions create necessary parent directories automatically
- Missing source files in backup operations are logged and skipped
- Collision detection prevents overwrites in all naming functions



## Functions Overview



### `novel_start_of_folder(path_to_parent_folder, semantic_id="")`
Creates a folder with format `{counter}_{semantic_id}` where counter starts at 999 and counts down.

**⚠️ Note**: Uses descending counter so newer folders appear first in file explorers (999, 998, 997...).

**Example**: `999_experiment`, `998_baseline`, `997_test`




---

### `novel_folder(path_to_parent_folder, folder_basic_name="")`
Creates a folder with format `{folder_basic_name}_{counter}` using descending counter.

**⚠️ Note**: Counter decreases, so newer folders have lower numbers.

**Example**: `model_999`, `model_998`, `model_997`




---

### `novel_filename(path_to_parent_folder, filename="", suffix="")`
Returns unique filepath with format `{filename}_{counter}{suffix}` using descending counter.

**⚠️ Note**: Creates parent directories automatically but does not create the actual file.

**Example**: `results_999.txt`, `data_998.csv`




---

### `make_symlink(path_to_target, path_to_simlink)`
Creates a symlink, automatically replacing any existing symlink at the target location.

**Usage**: Useful for maintaining "current" or "latest" links that always point to the newest version.






---

### `make_non_duplicate_backups(paths_of_files_to_back_up, path_to_backup_folder)`
Copies files to backup folder only if they don't already exist there. Returns status list: `True` (backed up), `False` (already exists), `None` (source missing).

**⚠️ Warning**: Only checks filenames, not content - files with identical names but different content won't be backed up.

**Use case**: Efficient backup of model weights without duplicating identical files across multiple training runs.




---

### `get_no_overwrite_path(file_path_no_suffix, suffix="", make_folders_on_path=True, warn_if_already_exists=False)`
Returns non-conflicting filepath by appending incremental numbers (`_1`, `_2`, etc.) if original exists.

**Parameters**:
- `make_folders_on_path`: Creates parent directories when `True`
- `warn_if_already_exists`: Prints warning message when `True`

**Returns**: `(new_path, original_path)` tuple




---

### `novel_folder_anum(path_to_parent_folder, digit_num=10)`
Creates folder with random base-62 alphanumeric name of specified length. Uses incremental search if collision occurs.

**Character set**: `0-9`, `A-Z`, `a-z` (62 total characters)

**Example**: With `digit_num=4`: `A7x9`, `Zm3K`, `p9Q2`




---

### `novel_filename_anum(path_to_parent_folder, suffix='', digit_num=10)`
Returns unique filepath using random base-62 name plus suffix.

**⚠️ Note**: Creates parent directory but not the file itself - just ensures path uniqueness.

**Example**: `A7x9p2K1m3.txt`, `Zm3Kp9Q2A7.json`
