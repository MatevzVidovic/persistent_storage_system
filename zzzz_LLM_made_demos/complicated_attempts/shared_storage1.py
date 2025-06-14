# shared_storage.py
# Singleton Storage System implementation
# All filesystem interactions should go through this module

import os
import os.path as osp
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import pickle
from datetime import datetime

# Import the persistent storage system modules
from persistent_storage_system.singleton_storage_fns import main as setup_storage, SetupNames
import persistent_storage_system.yaml_handler as yh
import persistent_storage_system.json_handler as jh
from persistent_storage_system.helpers_storage import (
    novel_filename, 
    get_no_overwrite_path,
    make_non_duplicate_backups
)


class SharedStorage:
    """
    Singleton class to handle all filesystem operations.
    Centralizes path management and file operations.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SharedStorage, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.storage_path: Optional[Path] = None
            self.main_data: Dict[str, Any] = {}
            self.shared_storage_data: Dict[str, Any] = {}
            self.file_tree_data: Dict[str, Any] = {}
            self.tiny_db_data: Dict[str, Any] = {}
            self.setup_names = SetupNames()
            SharedStorage._initialized = True
    
    def initial_setup(self, file_storage_path: str, semantic_id: str = ""):
        """
        Initialize the storage system. Creates folder structure if needed.
        
        Args:
            file_storage_path: Path to storage location
            semantic_id: Optional semantic identifier for the process
        """
        # Setup the persistent storage structure
        self.storage_path = Path(setup_storage(
            file_storage_path, 
            path_is_only_to_container=True, 
            semantic_id_of_proc=semantic_id
        ))
        
        print(f"Storage initialized at: {self.storage_path}")
        
        # Load existing data into memory
        self._load_all_yamls()
        
        # Initialize shared_storage.yaml with basic metadata if empty
        if not self.shared_storage_data:
            self.shared_storage_data = {
                'created_at': datetime.now().isoformat(),
                'last_checkpoint': None,
                'current_model_weights': None,
                'process_metadata': {
                    'semantic_id': semantic_id,
                    'total_checkpoints': 0
                }
            }
            self._save_shared_storage_yaml()
    
    def _load_all_yamls(self):
        """Load all YAML files into global dictionaries."""
        if not self.storage_path:
            raise RuntimeError("Storage not initialized. Call initial_setup() first.")
        
        # Load main.yaml
        main_yaml_path = self.storage_path / self.setup_names.MAIN_YAML
        if osp.exists(main_yaml_path):
            self.main_data = yh.get_yaml(main_yaml_path) or {}
        
        # Load shared_storage.yaml
        shared_yaml_path = self.storage_path / self.setup_names.SHARED_STORAGE_YAML
        if osp.exists(shared_yaml_path):
            self.shared_storage_data = yh.get_yaml(shared_yaml_path) or {}
        
        # Load file_tree.yaml
        file_tree_path = self.storage_path / self.setup_names.FILE_TREE_YAML
        if osp.exists(file_tree_path):
            self.file_tree_data = yh.get_yaml(file_tree_path) or {}
        
        # Load tiny_db.json
        tiny_db_path = self.storage_path / self.setup_names.TINY_DB_JSON
        if osp.exists(tiny_db_path):
            self.tiny_db_data = jh.get_json(tiny_db_path) or {}
    
    def _save_shared_storage_yaml(self):
        """Save shared_storage data to YAML file."""
        if not self.storage_path:
            return
        shared_yaml_path = self.storage_path / self.setup_names.SHARED_STORAGE_YAML
        yh.write_yaml(self.shared_storage_data, shared_yaml_path)
    
    def _save_file_tree_yaml(self):
        """Save file_tree data to YAML file."""
        if not self.storage_path:
            return
        file_tree_path = self.storage_path / self.setup_names.FILE_TREE_YAML
        yh.write_yaml(self.file_tree_data, file_tree_path)
    
    def _save_tiny_db_json(self):
        """Save tiny_db data to JSON file."""
        if not self.storage_path:
            return
        tiny_db_path = self.storage_path / self.setup_names.TINY_DB_JSON
        jh.write_json(self.tiny_db_data, tiny_db_path)
    
    def _update_file_tree(self, relative_path: str, file_info: Dict[str, Any]):
        """Update the file tree structure tracking."""
        path_parts = Path(relative_path).parts
        current = self.file_tree_data
        
        # Navigate/create the nested structure
        for part in path_parts[:-1]:  # All parts except the filename
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Add the file info
        filename = path_parts[-1] if path_parts else relative_path
        current[filename] = file_info
        
        self._save_file_tree_yaml()
    
    def save_object_to_file(self, obj: Any, relative_path: str, use_pickle: bool = True) -> str:
        """
        Save an object to a file. Object should be prepared for saving before calling this.
        
        Args:
            obj: Object to save (should be prepared by calling prepare_for_save() if applicable)
            relative_path: Path relative to the files/ folder
            use_pickle: Whether to use pickle (True) or JSON (False)
        
        Returns:
            Actual path used for saving
        """
        if not self.storage_path:
            raise RuntimeError("Storage not initialized")
        
        files_folder = self.storage_path / self.setup_names.FILES_FOLDER
        full_path = files_folder / relative_path
        
        # Ensure parent directories exist
        os.makedirs(full_path.parent, exist_ok=True)
        
        # Get non-overwrite path if file exists
        suffix = '.pkl' if use_pickle else '.json'
        final_path, original_path = get_no_overwrite_path(
            str(full_path.with_suffix('')), 
            suffix=suffix,
            warn_if_already_exists=True
        )
        
        # Save the object
        if use_pickle:
            with open(final_path, 'wb') as f:
                pickle.dump(obj, f)
        else:
            with open(final_path, 'w') as f:
                json.dump(obj, f, indent=2, default=str)
        
        # Update file tree tracking
        relative_final_path = str(Path(final_path).relative_to(files_folder))
        self._update_file_tree(relative_final_path, {
            'saved_at': datetime.now().isoformat(),
            'type': 'pickle' if use_pickle else 'json',
            'size_bytes': os.path.getsize(final_path)
        })
        
        return final_path
    
    def load_object_from_file(self, relative_path: str, use_pickle: bool = True) -> Any:
        """Load an object from a file."""
        if not self.storage_path:
            raise RuntimeError("Storage not initialized")
        
        files_folder = self.storage_path / self.setup_names.FILES_FOLDER
        full_path = files_folder / relative_path
        
        if not osp.exists(full_path):
            raise FileNotFoundError(f"File not found: {full_path}")
        
        if use_pickle:
            with open(full_path, 'rb') as f:
                return pickle.load(f)
        else:
            with open(full_path, 'r') as f:
                return json.load(f)
    
    def backup_model_weights(self, weight_paths: List[str]) -> List[bool]:
        """
        Backup model weights to avoid duplication.
        
        Args:
            weight_paths: List of paths to model weight files
            
        Returns:
            List indicating which files were actually backed up
        """
        if not self.storage_path:
            raise RuntimeError("Storage not initialized")
        
        backup_folder = self.storage_path / "model_backups"
        os.makedirs(backup_folder, exist_ok=True)
        
        return make_non_duplicate_backups(weight_paths, str(backup_folder))
    
    def setup_checkpoint_1(self):
        """First checkpoint setup - initialize basic data structures."""
        if not self.storage_path:
            raise RuntimeError("Storage not initialized")
        
        print("Setting up checkpoint 1...")
        
        # Initialize main data with basic info
        self.main_data.update({
            'checkpoint_1_setup_at': datetime.now().isoformat(),
            'stage': 'initial_setup'
        })
        
        # Save main.yaml
        main_yaml_path = self.storage_path / self.setup_names.MAIN_YAML
        yh.write_yaml(self.main_data, main_yaml_path)
        
        # Update shared storage metadata
        self.shared_storage_data['last_checkpoint'] = 'checkpoint_1'
        self.shared_storage_data['process_metadata']['total_checkpoints'] += 1
        self._save_shared_storage_yaml()
    
    def save_checkpoint_1(self, model_state: Optional[Dict] = None, logs: Optional[Any] = None):
        """Save state at checkpoint 1."""
        print("Saving checkpoint 1...")
        
        checkpoint_data = {
            'saved_at': datetime.now().isoformat(),
            'checkpoint': 1
        }
        
        # Save model state if provided
        if model_state:
            model_path = self.save_object_to_file(model_state, 'model_checkpoint_1.pkl')
            checkpoint_data['model_path'] = str(Path(model_path).name)
            self.shared_storage_data['current_model_weights'] = str(Path(model_path).name)
        
        # Save logs if provided
        if logs:
            # Assume logs have a prepare_for_save method that marks them as saved
            if hasattr(logs, 'prepare_for_save'):
                logs.prepare_for_save()
            logs_path = self.save_object_to_file(logs, 'logs_checkpoint_1.pkl')
            checkpoint_data['logs_path'] = str(Path(logs_path).name)
        
        # Update tiny_db with checkpoint info
        self.tiny_db_data['checkpoint_1'] = checkpoint_data
        self._save_tiny_db_json()
        
        # Update shared storage
        self.shared_storage_data['last_checkpoint'] = 'checkpoint_1'
        self.shared_storage_data['checkpoint_1_saved_at'] = datetime.now().isoformat()
        self._save_shared_storage_yaml()
    
    def setup_checkpoint_2(self):
        """Second checkpoint setup - for more advanced state."""
        print("Setting up checkpoint 2...")
        
        self.main_data.update({
            'checkpoint_2_setup_at': datetime.now().isoformat(),
            'stage': 'advanced_setup'
        })
        
        main_yaml_path = self.storage_path / self.setup_names.MAIN_YAML
        yh.write_yaml(self.main_data, main_yaml_path)
        
        self.shared_storage_data['last_checkpoint'] = 'checkpoint_2'
        self.shared_storage_data['process_metadata']['total_checkpoints'] += 1
        self._save_shared_storage_yaml()
    
    def save_checkpoint_2(self, model_state: Optional[Dict] = None, additional_data: Optional[Dict] = None):
        """Save state at checkpoint 2."""
        print("Saving checkpoint 2...")
        
        checkpoint_data = {
            'saved_at': datetime.now().isoformat(),
            'checkpoint': 2
        }
        
        if model_state:
            model_path = self.save_object_to_file(model_state, 'model_checkpoint_2.pkl')
            checkpoint_data['model_path'] = str(Path(model_path).name)
            self.shared_storage_data['current_model_weights'] = str(Path(model_path).name)
        
        if additional_data:
            data_path = self.save_object_to_file(additional_data, 'additional_data_checkpoint_2.pkl')
            checkpoint_data['additional_data_path'] = str(Path(data_path).name)
        
        self.tiny_db_data['checkpoint_2'] = checkpoint_data
        self._save_tiny_db_json()
        
        self.shared_storage_data['last_checkpoint'] = 'checkpoint_2'
        self.shared_storage_data['checkpoint_2_saved_at'] = datetime.now().isoformat()
        self._save_shared_storage_yaml()
    
    def load_checkpoint_1(self) -> Dict[str, Any]:
        """Load data from checkpoint 1."""
        if 'checkpoint_1' not in self.tiny_db_data:
            raise ValueError("Checkpoint 1 data not found")
        
        checkpoint_info = self.tiny_db_data['checkpoint_1']
        loaded_data = {'checkpoint_info': checkpoint_info}
        
        # Load model if available
        if 'model_path' in checkpoint_info:
            model_data = self.load_object_from_file(checkpoint_info['model_path'])
            loaded_data['model'] = model_data
        
        # Load logs if available
        if 'logs_path' in checkpoint_info:
            logs_data = self.load_object_from_file(checkpoint_info['logs_path'])
            loaded_data['logs'] = logs_data
        
        return loaded_data
    
    def get_current_state_summary(self) -> Dict[str, Any]:
        """Get a summary of the current storage state."""
        return {
            'storage_path': str(self.storage_path) if self.storage_path else None,
            'last_checkpoint': self.shared_storage_data.get('last_checkpoint'),
            'current_model_weights': self.shared_storage_data.get('current_model_weights'),
            'total_checkpoints': self.shared_storage_data.get('process_metadata', {}).get('total_checkpoints', 0),
            'file_tree_size': len(self.file_tree_data),
            'available_checkpoints': list(self.tiny_db_data.keys())
        }
    
    def print_file_tree(self):
        """Print the current file tree structure."""
        print("Current file tree:")
        print(json.dumps(self.file_tree_data, indent=2))


# Global singleton instance
storage = SharedStorage()


# Simulate logs (with prepare_for_save method)
class MockLogs:
    def __init__(self):
        self.entries = [
            {'epoch': 1, 'loss': 0.8, 'saved': False},
            {'epoch': 2, 'loss': 0.6, 'saved': False},
            {'epoch': 3, 'loss': 0.4, 'saved': False}
        ]
    
    def prepare_for_save(self):
        """Mark all logs as saved before storage."""
        for entry in self.entries:
            entry['saved'] = True

            
# Example usage and demo functions
def demo_usage():
    """Demonstrate how to use the shared storage system."""
    
    # Initialize storage
    storage.initial_setup("./demo_storage", semantic_id="demo_process")
    
    # Setup first checkpoint
    storage.setup_checkpoint_1()
    
    # Simulate some model training state
    mock_model_state = {
        'epoch': 10,
        'loss': 0.25,
        'accuracy': 0.92,
        'weights': [1, 2, 3, 4, 5]  # Mock weights
    }
    
    
    mock_logs = MockLogs()
    
    # Save checkpoint 1
    storage.save_checkpoint_1(model_state=mock_model_state, logs=mock_logs)
    
    # Setup and save checkpoint 2
    storage.setup_checkpoint_2()
    
    updated_model_state = {
        'epoch': 20,
        'loss': 0.15,
        'accuracy': 0.95,
        'weights': [2, 3, 4, 5, 6]
    }
    
    additional_data = {
        'hyperparameters': {'lr': 0.001, 'batch_size': 32},
        'validation_scores': [0.85, 0.90, 0.92, 0.95]
    }
    
    storage.save_checkpoint_2(model_state=updated_model_state, additional_data=additional_data)
    
    # Print current state
    print("\nCurrent state summary:")
    print(json.dumps(storage.get_current_state_summary(), indent=2))
    
    # Print file tree
    storage.print_file_tree()
    
    # Demonstrate loading
    print("\nLoading checkpoint 1:")
    loaded_data = storage.load_checkpoint_1()
    print(f"Loaded model epoch: {loaded_data['model']['epoch']}")
    print(f"Loaded logs entries: {len(loaded_data['logs'].entries)}")


if __name__ == "__main__":
    demo_usage()