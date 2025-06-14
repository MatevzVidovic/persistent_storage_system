





import os
import os.path as osp
from pathlib import Path

import orjson # fast json library



def get_json(path):
    
    if osp.exists(path):
        with open(path, 'rb') as f:
            json_str = f.read()

            try:
                json_dict = orjson.loads(json_str)
            except orjson.JSONDecodeError:
                # when .json is empty, orjson had no string to load
                json_dict = {}

    else:
        json_dict = {}
    
    return json_dict




def write_json(json_dict, file_path_no_suffix, suffix="", no_overwrite=False):
    """
    if no_overwrite is True, then you should: suffix=".json"


    orjson can nicely write an empty dict also, so don't worry.
    just reading is the problem ig? Am not even sure.
    """

    j_path = str(file_path_no_suffix) + str(suffix)
    
    if no_overwrite and osp.exists(j_path):
        add_id = 1
        old_j_path = j_path
        j_path = file_path_no_suffix + f"_{add_id}{suffix}"
        while osp.exists(j_path):
            add_id += 1
            j_path = file_path_no_suffix + f"_{add_id}{suffix}"
        
        print(f"JSON file {old_j_path} already exists. We made {j_path} instead.")
    

    os.makedirs(Path(j_path).parent, exist_ok=True)
    with open(j_path, 'wb') as f:
        json_str = orjson.dumps(json_dict)
        f.write(json_str)


