
# we expect the cwd of the process running this is the root of your project.

# We expect: project_root/persistent_storage_system/
# Where persistent_storage_system/ is the inner folder where this file is located.
# Just clone this project somewhere else on your system,
# and make a symlink to this folder from the root of your main project.

# This positioning (project_root/persistent_storage_system/) enables us to make relative imports. 

# So call this with python3 -m if you are running this file directly.
# Or, if you are just using the fns (which is the way to go), make sure the cwd is the root of your project.
# Or, just give us the absolute path.

# If we get a relative path, we will assume it is relative to the root of the project.


import os
import os.path as osp
from pathlib import Path

from persistent_storage_system.helpers_storage import novel_start_of_folder
import persistent_storage_system.yaml_handler as yh
import persistent_storage_system.json_handler as jh

class NamesInStorage():
    """
    So intellisence can suggest and check if what you wrote in your code is correct.
    Because working with pure strings is honestly a bit unnerving to me.
    """

    MAIN_YAML = "main.yaml"
    TINY_DB_JSON = "tiny_db.json"
    OLD_YAMLS_FOLDER = "old_yamls"
    PICKLES_AND_SUCH_FOLDER = "pickles_and_such"
    SYMLINK_TREE_FOLDER = "symlink_tree"
    WRITE_ONLY_TREE_FOLDER = "write_only_tree"
    # add more as needed


def main(path_to_storage, path_is_only_to_container=False, semantic_id_of_proc=""):

    """

    if full path to storage folder is specified, we check if it exists.
    If id doesn't exist, we make the folder, do setup(), and return the new path.
    If exists, we just return the path.

    If the path is only to the storage container, not the actal storage folder,
    we make a novel folder inside it, 
    do setup(),
    and return the path to that folder.


    """

    path_to_storage = Path(path_to_storage).resolve()

    if not path_is_only_to_container:
        # if we got a full path to the storage folder, we check if it exists
        if not osp.exists(path_to_storage):
            # print(f"Storage folder {path_to_storage} does not exist. Creating it.")
            os.makedirs(path_to_storage, exist_ok=True)
            # do setup
            return setup(path_to_storage)

        else:
            # print(f"Storage folder {path_to_storage} already exists. Returning it.")
            return path_to_storage
        
    else:
        # if we got a path to the storage container, we make a novel folder inside it
        if not osp.exists(path_to_storage):
            # print(f"Storage container {path_to_storage} does not exist. Creating it.")
            os.makedirs(path_to_storage, exist_ok=True)

        # make a novel folder inside the storage container
        path_to_novel_folder = novel_start_of_folder(path_to_storage, semantic_id_of_proc)
        
        # do setup in the novel folder
        return setup(path_to_novel_folder)

    








def setup(path_to_novel_storage_folder):
    """
    path_to_storage:   diplomska_store/999_unet_large   or, give abspath
    semantic_id_of_proc:  "unet_large"
    """

    novel_folder_path = path_to_novel_storage_folder
    
    # - set up the following:
        # - main.yaml
        # - tiny_db.json 
        # - old_yamls/
        # - pickles_and_such/
        # - symlink_tree/
        # - write_only_tree/
    
    nis = NamesInStorage()
    
    main_yaml_path = novel_folder_path / nis.MAIN_YAML
    if not osp.exists(main_yaml_path):
        # create main.yaml
        yh.write_yaml({}, main_yaml_path)

    tiny_db_path = novel_folder_path / nis.TINY_DB_JSON
    if not osp.exists(tiny_db_path):
        # create tiny_db.json
        jh.write_json({}, tiny_db_path)
    
    old_yamls_path = novel_folder_path / nis.OLD_YAMLS_FOLDER
    os.makedirs(old_yamls_path, exist_ok=True)

    pickles_and_such_path = novel_folder_path / nis.PICKLES_AND_SUCH_FOLDER
    os.makedirs(pickles_and_such_path, exist_ok=True)

    symlink_tree_path = novel_folder_path / nis.SYMLINK_TREE_FOLDER
    os.makedirs(symlink_tree_path, exist_ok=True)

    write_only_tree_path = novel_folder_path / nis.WRITE_ONLY_TREE_FOLDER
    os.makedirs(write_only_tree_path, exist_ok=True)

    # return path to the novel folder we made

    return novel_folder_path






if __name__ == "__main__":
    
    import argparse
    parser = argparse.ArgumentParser(description="Persistent Storage System Setup")
    parser.add_argument("path_to_storage", type=str, help="Path to the storage folder or container")
    parser.add_argument("--path_is_only_to_container", action="store_true", help="Indicates that the provided path is only to the storage container, not the actual storage folder")
    parser.add_argument("--semantic_id_of_proc", type=str, default="", help="Semantic ID of the process for naming the storage folder")
    args = parser.parse_args()

    main(args.path_to_storage, args.path_is_only_to_container, args.semantic_id_of_proc)

