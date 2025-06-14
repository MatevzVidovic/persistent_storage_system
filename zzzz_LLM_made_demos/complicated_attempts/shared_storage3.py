# ml_storage.py
# A Simple, Intuitive Storage System for Machine Learning Projects
# Following the Singleton Storage System principles

import os
import pickle
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional, List
from enum import Enum

# Assume these are your persistent storage modules
try:
    from persistent_storage_system.singleton_storage_fns import main as setup_storage
    from persistent_storage_system import yaml_handler as yh
    from persistent_storage_system import json_handler as jh
    from persistent_storage_system.helpers_storage import get_no_overwrite_path
except ImportError:
    # Mock implementations for demonstration
    def setup_storage(path, **kwargs):
        os.makedirs(path, exist_ok=True)
        return path
    
    class yh:
        @staticmethod
        def get_yaml(path): 
            try:
                import yaml
                with open(path, 'r') as f:
                    return yaml.safe_load(f)
            except: return {}
        
        @staticmethod
        def write_yaml(data, path):
            import yaml
            with open(path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
    
    class jh:
        @staticmethod
        def get_json(path):
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except: return {}
        
        @staticmethod
        def write_json(data, path):
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
    
    def get_no_overwrite_path(base_path, suffix='', **kwargs):
        path = base_path + suffix
        counter = 1
        while os.path.exists(path):
            path = f"{base_path}_{counter}{suffix}"
            counter += 1
        return path, counter > 1


class ProjectPhase(Enum):
    """Simple, clear phases for any ML project"""
    SETUP = "setup"                    # Just starting out
    TRAINING = "training"              # Model is learning  
    EVALUATION = "evaluation"          # Testing how good it is
    READY = "ready"                   # Done and working


class MLStorage:
    """
    The ONE place where all file operations happen.
    
    This is your singleton - everything goes through here.
    No more scattered file operations across your codebase!
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # Core file paths - ALL paths are managed here
        self.project_path: Optional[Path] = None
        
        # The core state files (following your spec exactly)
        self.main_yaml_path = None          # main.yaml
        self.shared_storage_path = None     # shared_storage.yaml  
        self.file_tree_path = None          # file_tree.yaml
        self.tiny_db_path = None            # tiny_db.json
        self.old_yamls_dir = None           # old_yamls/
        self.files_dir = None               # files/
        
        # In-memory state (loaded from files)
        self.main_config = {}               # From main.yaml
        self.shared_storage = {}            # From shared_storage.yaml
        self.file_tree = {}                 # From file_tree.yaml
        self.checkpoint_db = {}             # From tiny_db.json
        
        self.current_phase = ProjectPhase.SETUP
        self._initialized = True
    
    def initial_setup(self, project_folder: str, project_name: str = "ML_Project"):
        """
        The ONLY setup function. Creates the exact file structure from your spec.
        """
        print(f"🏗️  Setting up project: {project_name}")
        
        # Create the main project folder
        self.project_path = Path(setup_storage(project_folder))
        
        # Create the exact file structure from your spec
        self.main_yaml_path = self.project_path / "main.yaml"
        self.shared_storage_path = self.project_path / "shared_storage.yaml"
        self.file_tree_path = self.project_path / "file_tree.yaml" 
        self.tiny_db_path = self.project_path / "tiny_db.json"
        self.old_yamls_dir = self.project_path / "old_yamls"
        self.files_dir = self.project_path / "files"
        
        # Create directories
        self.old_yamls_dir.mkdir(exist_ok=True)
        self.files_dir.mkdir(exist_ok=True)
        
        # Load existing files or create new ones
        self._load_all_state()
        
        # Initialize if this is a brand new project
        if not self.shared_storage:
            self.shared_storage = {
                'project_name': project_name,
                'created_at': datetime.now().isoformat(),
                'current_phase': self.current_phase.value,
                'latest_model_file': None,
                'latest_checkpoint': None,
                'total_checkpoints': 0
            }
            
            self.file_tree = {'root': {}}
            self.main_config = {'project_settings': {}}
            self.checkpoint_db = {}
            
            self._save_all_state()
        
        print(f"✅ Project ready at: {self.project_path}")
        return self.project_path
    
    def _load_all_state(self):
        """Load all YAML/JSON files into memory. Called only from here."""
        if self.main_yaml_path and self.main_yaml_path.exists():
            self.main_config = yh.get_yaml(self.main_yaml_path)
            
        if self.shared_storage_path and self.shared_storage_path.exists():
            self.shared_storage = yh.get_yaml(self.shared_storage_path)
            # Restore current phase
            if 'current_phase' in self.shared_storage:
                try:
                    self.current_phase = ProjectPhase(self.shared_storage['current_phase'])
                except ValueError:
                    self.current_phase = ProjectPhase.SETUP
                    
        if self.file_tree_path and self.file_tree_path.exists():
            self.file_tree = yh.get_yaml(self.file_tree_path)
            
        if self.tiny_db_path and self.tiny_db_path.exists():
            self.checkpoint_db = jh.get_json(self.tiny_db_path)
    
    def _save_all_state(self):
        """Save all state to files. Called only from here."""
        if not self.project_path:
            return
            
        yh.write_yaml(self.main_config, self.main_yaml_path)
        yh.write_yaml(self.shared_storage, self.shared_storage_path) 
        yh.write_yaml(self.file_tree, self.file_tree_path)
        jh.write_json(self.checkpoint_db, self.tiny_db_path)
    
    def change_phase(self, new_phase: ProjectPhase):
        """Move to a new phase of your project"""
        print(f"📊 Changing phase: {self.current_phase.value} → {new_phase.value}")
        
        old_phase = self.current_phase.value
        self.current_phase = new_phase
        
        # Update shared storage with phase info
        self.shared_storage['current_phase'] = new_phase.value
        self.shared_storage['phase_changes'] = self.shared_storage.get('phase_changes', [])
        self.shared_storage['phase_changes'].append({
            'from': old_phase,
            'to': new_phase.value,
            'at': datetime.now().isoformat()
        })
        
        self._save_all_state()
        print(f"✅ Now in {new_phase.value} phase")
    
    def save_checkpoint(self, name: str, **objects_to_save):
        """
        Save everything in one place. This is your main save function.
        
        Usage:
            storage.save_checkpoint("after_training", 
                                  model=my_model, 
                                  logs=training_logs,
                                  results=evaluation_results)
        """
        print(f"💾 Saving checkpoint: {name}")
        
        checkpoint_info = {
            'name': name,
            'phase': self.current_phase.value,
            'saved_at': datetime.now().isoformat(),
            'files': {}
        }
        
        # Save each object to the files/ directory
        for obj_name, obj in objects_to_save.items():
            if obj is None:
                continue
                
            # Prepare object for saving (your functional approach)
            if hasattr(obj, 'prepare_for_save'):
                obj.prepare_for_save()
            
            # Save to files/ directory
            filename = f"{name}_{obj_name}.pkl"
            filepath = self.files_dir / filename
            
            # Don't overwrite existing files
            final_path, was_renamed = get_no_overwrite_path(
                str(filepath.with_suffix('')), 
                suffix='.pkl'
            )
            
            with open(final_path, 'wb') as f:
                pickle.dump(obj, f)
            
            # Update file tree
            relative_path = Path(final_path).relative_to(self.project_path)
            self._update_file_tree(str(relative_path))
            
            checkpoint_info['files'][obj_name] = Path(final_path).name
            print(f"   Saved {obj_name} → {Path(final_path).name}")
        
        # Record this checkpoint
        self.checkpoint_db[name] = checkpoint_info
        
        # Update shared storage
        self.shared_storage['latest_checkpoint'] = name
        self.shared_storage['total_checkpoints'] += 1
        if 'model' in objects_to_save:
            self.shared_storage['latest_model_file'] = checkpoint_info['files']['model']
        
        self._save_all_state()
        print(f"✅ Checkpoint '{name}' saved with {len(checkpoint_info['files'])} files")
    
    def load_checkpoint(self, name: str) -> Dict[str, Any]:
        """Load a saved checkpoint"""
        print(f"📂 Loading checkpoint: {name}")
        
        if name not in self.checkpoint_db:
            available = list(self.checkpoint_db.keys())
            raise ValueError(f"Checkpoint '{name}' not found. Available: {available}")
        
        checkpoint_info = self.checkpoint_db[name]
        loaded = {'checkpoint_info': checkpoint_info}
        
        # Load each saved file
        for obj_name, filename in checkpoint_info['files'].items():
            filepath = self.files_dir / filename
            
            if not filepath.exists():
                print(f"   Warning: {filename} not found, skipping")
                continue
                
            with open(filepath, 'rb') as f:
                loaded[obj_name] = pickle.load(f)
            print(f"   Loaded {obj_name} from {filename}")
        
        print(f"✅ Loaded checkpoint '{name}' with {len(loaded)-1} objects")
        return loaded
    
    def _update_file_tree(self, relative_path: str):
        """Update the file_tree.yaml to track what files exist"""
        parts = Path(relative_path).parts
        current = self.file_tree.setdefault('root', {})
        
        # Navigate through folders
        for part in parts[:-1]:
            folder_key = f"{part}/"
            current = current.setdefault(folder_key, {})
        
        # Add the file
        current[parts[-1]] = {
            'added_at': datetime.now().isoformat(),
            'size_bytes': os.path.getsize(self.project_path / relative_path)
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current project status - like checking your save game"""
        return {
            'project_name': self.shared_storage.get('project_name', 'Unknown'),
            'current_phase': self.current_phase.value,
            'total_checkpoints': self.shared_storage.get('total_checkpoints', 0),
            'latest_checkpoint': self.shared_storage.get('latest_checkpoint'),
            'latest_model': self.shared_storage.get('latest_model_file'),
            'available_checkpoints': list(self.checkpoint_db.keys()),
            'project_folder': str(self.project_path) if self.project_path else None
        }
    
    def list_checkpoints(self):
        """Show all your saved checkpoints"""
        print(f"\n📋 Checkpoints for '{self.shared_storage.get('project_name', 'Project')}':")
        print("=" * 50)
        
        if not self.checkpoint_db:
            print("   No checkpoints saved yet.")
            return
        
        for name, info in self.checkpoint_db.items():
            print(f"🔖 {name}")
            print(f"   Phase: {info['phase']}")
            print(f"   Saved: {info['saved_at']}")
            print(f"   Files: {', '.join(info['files'].keys())}")
            print()
    
    def print_file_tree(self):
        """Show what files exist in your project"""
        print(f"\n🌳 File Tree:")
        print("=" * 30)
        self._print_tree_recursive(self.file_tree.get('root', {}), 0)
    
    def _print_tree_recursive(self, tree_dict: Dict, indent: int):
        """Helper to print the file tree nicely"""
        for key, value in tree_dict.items():
            print("  " * indent + f"📁 {key}" if key.endswith('/') else "  " * indent + f"📄 {key}")
            if isinstance(value, dict) and not value.get('added_at'):
                self._print_tree_recursive(value, indent + 1)


# The singleton instance - import this in your other files
storage = MLStorage()


# Example usage classes
class TrainingLogs:
    """Example of how objects should prepare for saving"""
    def __init__(self):
        self.epochs = []
        self.losses = []
        self.is_ready_for_save = False
    
    def add_epoch(self, epoch: int, loss: float):
        self.epochs.append(epoch)
        self.losses.append(loss) 
    
    def prepare_for_save(self):
        """This is called before saving - prepare your object"""
        self.is_ready_for_save = True
        print(f"   Prepared {len(self.epochs)} training epochs for saving")


def demo():
    """Demo showing the simple, intuitive workflow"""
    print("🎯 Demo: Simple ML Storage System")
    print("=" * 40)
    
    # 1. Setup (only done once)
    storage.initial_setup("./my_project", "Image Classifier")
    
    # 2. Move through phases and save at key points
    storage.change_phase(ProjectPhase.TRAINING)
    
    # Create some example objects
    model = {'layers': [128, 64, 10], 'weights': 'pretrained', 'accuracy': 0.0}
    logs = TrainingLogs()
    
    # Save initial state
    storage.save_checkpoint("initial", model=model, logs=logs)
    
    # Simulate training
    logs.add_epoch(1, 2.5)
    logs.add_epoch(2, 1.8) 
    logs.add_epoch(3, 1.2)
    model['accuracy'] = 0.85
    
    # Save training progress
    storage.save_checkpoint("after_training", 
                          model=model, 
                          logs=logs,
                          extra_data={'validation_acc': 0.82})
    
    # Move to evaluation
    storage.change_phase(ProjectPhase.EVALUATION)
    
    # Save final results
    results = {'test_accuracy': 0.89, 'confusion_matrix': [[1,2],[3,4]]}
    storage.save_checkpoint("final_results", 
                          model=model, 
                          logs=logs, 
                          results=results)
    
    # Show project status
    print("\n📊 Project Status:")
    status = storage.get_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # List all checkpoints
    storage.list_checkpoints()
    
    # Show file structure
    storage.print_file_tree()
    
    # Demo loading
    print("\n🔄 Loading checkpoint...")
    loaded = storage.load_checkpoint("after_training")
    print(f"   Loaded model accuracy: {loaded['model']['accuracy']}")
    print(f"   Loaded {len(loaded['logs'].epochs)} training epochs")


if __name__ == "__main__":
    demo()