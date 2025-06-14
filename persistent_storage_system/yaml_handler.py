


import os
import os.path as osp
from pathlib import Path
import yaml


def get_yaml(path):
    if osp.exists(path):
        with open(path, 'r') as f:
            YD = yaml.safe_load(f)

            # when yaml is empty
            if YD is None:
                YD = {}
    else:
        YD = {}
    return YD




def write_yaml(yaml_dict, file_path_no_suffix, suffix="", no_overwrite=False, sort_keys=False, indent=4):
    """
    if no_overwrite is True, then you should: suffix=".yaml"
    """

    file_path = str(file_path_no_suffix) + str(suffix)

    if no_overwrite and osp.exists(file_path):
        add_id = 1
        old_file_path = file_path
        file_path = file_path_no_suffix + f"_{add_id}{suffix}"
        while osp.exists(file_path):
            add_id += 1
            file_path = file_path_no_suffix + f"_{add_id}{suffix}"
        print(f"YAML file {old_file_path} already exists. We made {file_path} instead.")

    os.makedirs(Path(file_path).parent, exist_ok=True)
    with open(file_path, 'w') as file:
        yaml.dump(yaml_dict, file, sort_keys=sort_keys, indent=indent)



    

    
def get_readable_dict_str(inp_dict, max_per_line=5):

    final_str = ""
    num_in_line = 0
        
    for key, val in inp_dict.items():
        final_str += f"{key}: {val}      "
        num_in_line += 1
        if num_in_line >= max_per_line:
            final_str += "\n"
            num_in_line = 0
    
    return final_str