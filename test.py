



import persistent_storage_system.persistent_storage_fns as pss
import persistent_storage_system.singleton_storage_fns as ssf
import persistent_storage_system.helpers_storage as hs


process_args = [
    ("diplomska_storage", True, "unet_large"),
    ("diplomska_storage", True, "unet_small"),
    ("diplomska_storage", True, "segnet_large"),
    ("diplomska_storage", True, "segnet_small"),
    ("diplomska_storage", True, "unet_large"),
    ("diplomska_storage", True, "unet_small"),
    ("diplomska_storage", True, "segnet_large"),
    ("diplomska_storage", True, "segnet_small")
]



# initial setup

for args in process_args:

    path_to_storage, path_is_only_to_container, semantic_id_of_proc = args
    
    
    pss_paths = []
    print(f"\n\n\n\n\nRunning persistent_storage_fns.main with args: {args}")
    pss_paths.append(
        pss.main(path_to_storage + "_pss", path_is_only_to_container, semantic_id_of_proc)
    )
    
    ssf_paths = []
    print(f"\n\n\n\n\nRunning singleton_storage_fns.main with args: {args}")
    ssf_paths.append(
        ssf.main(path_to_storage + "_ssf", path_is_only_to_container, semantic_id_of_proc)
    )




# working with it after setup

new_process_args = []
for path in pss_paths:
    new_process_args.append((path, False, ""))

for args in new_process_args:
    path_to_storage, path_is_only_to_container, semantic_id_of_proc = args
    print(f"\n\n\n\n\nRunning persistent_storage_fns.main with args: {args}")
    pss.main(path_to_storage, path_is_only_to_container, semantic_id_of_proc)




new_process_args = []
for path in ssf_paths:
    new_process_args.append((path, False, ""))

for args in new_process_args:
    path_to_storage, path_is_only_to_container, semantic_id_of_proc = args
    print(f"\n\n\n\n\nRunning singleton_storage_fns.main with args: {args}")
    ssf.main(path_to_storage, path_is_only_to_container, semantic_id_of_proc)





# working with specified paths from the start


process_args = [
    ("diplomska_storage_pss/unet_large", False, ""),
    ("diplomska_storage_pss/unet_small", False, ""),
    ("diplomska_storage_pss/segnet_large", False, ""),
    ("diplomska_storage_pss/segnet_small", False, ""),
]

for args in process_args:
    path_to_storage, path_is_only_to_container, semantic_id_of_proc = args
    print(f"\n\n\n\n\nRunning persistent_storage_fns.main with args: {args}")
    pss.main(path_to_storage, path_is_only_to_container, semantic_id_of_proc)




process_args = [
    ("diplomska_storage_ssf/unet_large", False, ""),
    ("diplomska_storage_ssf/unet_small", False, ""),
    ("diplomska_storage_ssf/segnet_large", False, ""),
    ("diplomska_storage_ssf/segnet_small", False, "")
]

for args in process_args:
    path_to_storage, path_is_only_to_container, semantic_id_of_proc = args
    print(f"\n\n\n\n\nRunning singleton_storage_fns.main with args: {args}")
    ssf.main(path_to_storage, path_is_only_to_container, semantic_id_of_proc)







