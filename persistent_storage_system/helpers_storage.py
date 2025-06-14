




import os
import os.path as osp
from pathlib import Path
import shutil as sh
import random
import string




def novel_start_of_folder(path_to_parent_folder, semantic_id=""):
    """
    Creates a new folder inside `path_to_parent_folder` with a unique start of name:
    start of name is e.g. "##999". The start is always unique.
    This ensures ordering, while also allowing you to 
    give a semantic id after the numerical start_of_name.
    """

    prefix = "" # will be k*"#" if overflow
    counter=999
    
    folder_path = Path(path_to_parent_folder) / f"{prefix}{counter}_{semantic_id}"
    while osp.exists(folder_path):
        counter -= 1
        folder_path = Path(path_to_parent_folder) / f"{prefix}{counter}_{semantic_id}"

        if counter <= 100:
            prefix += "#"
            counter = 999

    os.makedirs(folder_path, exist_ok=True)
    return Path(folder_path)




def novel_folder(path_to_parent_folder, folder_basic_name=""):



    prefix = "" # will be k*"#" if overflow
    counter=999
    
    folder_path = Path(path_to_parent_folder) / f"{folder_basic_name}_{prefix}{counter}"
    while osp.exists(folder_path):
        counter -= 1
        folder_path = Path(path_to_parent_folder) / f"{folder_basic_name}_{prefix}{counter}"

        if counter <= 100:
            prefix += "#"
            counter = 999

    os.makedirs(folder_path, exist_ok=True)
    return Path(folder_path)
    




def novel_filename(path_to_parent_folder, filename="", suffix=""):

    prefix = "" # will be k*"#" if overflow
    counter=999
    
    filepath = Path(path_to_parent_folder) / f"{filename}_{prefix}{counter}"
    while osp.exists(filepath):
        counter -= 1
        filepath = Path(path_to_parent_folder) / f"{filename}_{prefix}{counter}"

        if counter <= 100:
            prefix += "#"
            counter = 999

    os.makedirs(filepath, exist_ok=True)
    return Path(filepath)









def make_symlink(path_to_target, path_to_simlink):
    """
    Creates a symlink at `path_to_simlink` that points to `path_to_target`.
    If the symlink already exists, it will be removed and recreated.
    """
    if os.path.islink(path_to_simlink):
        os.remove(path_to_simlink)
    
    os.symlink(path_to_target, path_to_simlink)


def make_non_duplicate_backups(paths_of_files_to_back_up, path_to_backup_folder):
    """
    Moves files to a backup folder if they do not already exist there.
    Returns a list indicating whether each file was backed up (True),
    was backed up priorly (False), or the source file did not exist (None).
    We suggest you also save a .yaml of what files were supposed to be backed up on this backup,
    and what the return was for them.

    

    What is this fn for:

    You might want to make backups of model weights for models that performed well.
    E.g. I always kept the last model and 3 more best performing past models in my current state. 
    Then after each training loop, I save the current state, so that meant also making a 
    backup of all 4 of these model weights, so I could easily roll back to that state whenever I wanted.
    But there was a bunch of duplicate weights for no reason. So I started storing .yamls of which 
    model weights were the curr best ones, and saving the model weights into a shared backup/ 
    where I would only save them if the same-named weights didn't exist yet. Thus no duplication.
    It's really nice to have for various scenarios.

    """

    did_backup = []
    for path in paths_of_files_to_back_up:
        if not osp.exists(path):
            print(f"File {path} does not exist. Skipping backup.")
            did_backup.append(None)
            continue
        
        file_name = osp.basename(path)
        backup_path = osp.join(path_to_backup_folder, file_name)

        if osp.exists(backup_path):
            print(f"Backup for {file_name} already exists at {backup_path}. Skipping.")
            did_backup.append(False)
            continue
        
        os.makedirs(osp.dirname(backup_path), exist_ok=True)
        sh.copy2(path, backup_path)
        did_backup.append(True)
    return did_backup



def get_no_overwrite_path(file_path_no_suffix, suffix="", make_folders_on_path=True, warn_if_already_exists=False):
    """
    We suggest you do:
    if file_path != old_file_path:
        print(f"File {old_file_path} already exists. We made {file_path} instead.")
    """

    file_path = file_path_no_suffix + suffix
    old_file_path = file_path

    if osp.exists(file_path):
        add_id = 1
        file_path = file_path_no_suffix + f"_{add_id}{suffix}"
        while osp.exists(file_path):
            add_id += 1
            file_path = file_path_no_suffix + f"_{add_id}{suffix}"
    
    return file_path, old_file_path











# Base62 alphabet: digits + uppercase + lowercase
_ALPHANUM_CHARS = string.digits + string.ascii_uppercase + string.ascii_lowercase

def _to_base62(num, length):
    """Convert integer to fixed-length base62 string."""
    base = len(_ALPHANUM_CHARS)
    chars = []
    for _ in range(length):
        num, rem = divmod(num, base)
        chars.append(_ALPHANUM_CHARS[rem])
    return ''.join(reversed(chars))


def novel_folder_anum(path_to_parent_folder, digit_num=10):
    """
    Creates a new folder inside `path_to_parent_folder`
    with a unique base-62 alphanumeric name of length `digit_num`
    and returns the path to the new folder.
    """

    max_num = len(_ALPHANUM_CHARS) ** digit_num
    # Seed a random 0 ≤ n < max_num
    n = random.randrange(max_num)
    ptpf = Path(path_to_parent_folder)

    while True:
        name = _to_base62(n, digit_num)
        new_folder_path = ptpf / name
        if not osp.exists(new_folder_path):
            os.makedirs(new_folder_path, exist_ok=True)
            return new_folder_path
        # If taken, increment (wrap around modulo max_num to avoid overflow)
        n = (n + 1) % max_num


def novel_filename_anum(path_to_parent_folder, suffix='', digit_num=10):
    """
    Returns path to a unique filename inside `path_to_parent_folder` with:
      <base62-name><suffix>
    where base62-name has length `digit_num`.
    Creates folders on the path if they do not exist.
    Does not create the file — just ensures uniqueness.
    """

    max_num = len(_ALPHANUM_CHARS) ** digit_num
    n = random.randrange(max_num)
    ptpf = Path(path_to_parent_folder)

    while True:
        name = _to_base62(n, digit_num) + suffix
        new_path = ptpf / name
        if not os.path.exists(new_path):
            os.makedirs(ptpf, exist_ok=True)  # Ensure parent directory exists
            return new_path
        n = (n + 1) % max_num

