# simple_storage.py
# A Simple, Clean Singleton Storage System for ML Projects

import os
import os.path as osp
from pathlib import Path
from typing import Dict, Any, Optional
import pickle
import shutil as sh
from datetime import datetime

# Import the persistent storage system modules
from persistent_storage_system.singleton_storage_fns import main as setup_storage, SetupNames
import persistent_storage_system.yaml_handler as yh
from persistent_storage_system.helpers_storage import make_non_duplicate_backups


class TrainingLogs:
    """Training logs that can be saved and loaded"""
    def __init__(self):
        self.epochs = []
        self.losses = []
        self.accuracies = []
        self.training_history = []
        self.is_saved = False
    
    def add_epoch(self, epoch, loss, accuracy):
        self.epochs.append(epoch)
        self.losses.append(loss)
        self.accuracies.append(accuracy)
        self.training_history.append({
            'epoch': epoch,
            'loss': loss,
            'accuracy': accuracy,
            'timestamp': datetime.now().isoformat()
        })
    
    def prepare_for_save(self):
        """Mark as saved before storage"""
        self.is_saved = True
        print(f"   Prepared {len(self.epochs)} training epochs for saving")


class ModelWrapper:
    """Wrapper for ML models with metadata"""
    def __init__(self, model=None):
        self.model = model
        self.model_type = None
        self.created_at = datetime.now().isoformat()
        self.last_updated = self.created_at
        self.training_epochs = 0
        self.metadata = {}
    
    def update_model(self, model):
        """Update the wrapped model"""
        self.model = model
        self.last_updated = datetime.now().isoformat()
        self.training_epochs += 1
    
    def add_metadata(self, key, value):
        """Add metadata to the model"""
        self.metadata[key] = value


class SimpleMLStorage:
    """
    Simple singleton storage for ML projects
    
    Key paths available:
    - files/graphs/
    - files/test_showcase_images/  
    - files/backups/weights/
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SimpleMLStorage, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            # Storage paths
            self.storage_path: Optional[Path] = None
            self.setup_names = SetupNames()
            
            # Available storage directories
            self.paths = {
                'graphs': None,
                'test_showcase_images': None,
                'backups_weights': None,
                'files_root': None
            }
            
            # YAML data dictionaries
            self.main_config: Dict[str, Any] = {}
            self.file_tree: Dict[str, Any] = {}
            
            # ML objects
            self.training_logs: Optional[TrainingLogs] = None
            self.model_wrapper: Optional[ModelWrapper] = None
            
            SimpleMLStorage._initialized = True
    
    def setup(self, project_folder: str, project_name: str = "ml_project"):
        """
        Set up the storage system and load existing data
        
        Args:
            project_folder: Root folder for the project
            project_name: Name identifier for the project
        """
        print(f"🚀 Setting up ML storage: {project_name}")
        
        # Create storage directory structure
        self.storage_path = Path(setup_storage(
            project_folder, 
            path_is_only_to_container=True, 
            semantic_id_of_proc=project_name
        ))
        
        # Set up available paths
        files_folder = self.storage_path / self.setup_names.FILES_FOLDER
        self.paths = {
            'graphs': files_folder / 'graphs',
            'test_showcase_images': files_folder / 'test_showcase_images',
            'backups_weights': files_folder / 'backups' / 'weights',
            'files_root': files_folder
        }
        
        # Create directories if they don't exist
        for path in self.paths.values():
            os.makedirs(path, exist_ok=True)
        
        # Load YAML configurations
        self._load_yaml_configs()
        
        print(f"✅ Storage setup complete at: {self.storage_path}")
        print(f"📁 Available paths: {list(self.paths.keys())}")
    
    def _load_yaml_configs(self):
        """Load YAML configuration files"""
        if not self.storage_path:
            return
        
        # Load main config
        main_config_path = self.storage_path / self.setup_names.MAIN_YAML
        if osp.exists(main_config_path):
            self.main_config = yh.get_yaml(main_config_path) or {}
            print(f"📋 Loaded main config with {len(self.main_config)} entries")
        
        # Load file tree
        file_tree_path = self.storage_path / "file_tree.yaml"
        if osp.exists(file_tree_path):
            self.file_tree = yh.get_yaml(file_tree_path) or {}
            print(f"🌳 Loaded file tree with {len(self.file_tree)} entries")
    
    def _save_yaml_configs(self):
        """Save YAML configuration files"""
        if not self.storage_path:
            return
        
        # Save main config
        main_config_path = self.storage_path / self.setup_names.MAIN_YAML
        yh.write_yaml(self.main_config, main_config_path)
        
        # Save file tree
        file_tree_path = self.storage_path / "file_tree.yaml"
        yh.write_yaml(self.file_tree, file_tree_path)
    
    def file_tree_manage(self, path: str, remove: bool = False):
        """
        Update the file tree dictionary with path information
        
        Args:
            path: File path to add or remove
            remove: If True, remove the path; if False, add it
        """
        if remove:
            if path in self.file_tree:
                del self.file_tree[path]
                print(f"🗑️  Removed {path} from file tree")
        else:
            self.file_tree[path] = {
                'added_at': datetime.now().isoformat(),
                'type': 'file' if osp.isfile(path) else 'directory',
                'exists': osp.exists(path)
            }
            print(f"📝 Added {path} to file tree")
    
    def load(self):
        """
        Load TrainingLogs and ModelWrapper from storage
        """
        print("📂 Loading ML objects...")
        
        if not self.storage_path:
            raise RuntimeError("Storage not set up! Call setup() first.")
        
        files_folder = self.paths['files_root']
        
        # Load TrainingLogs
        logs_path = files_folder / "training_logs.pkl"
        if osp.exists(logs_path):
            with open(logs_path, 'rb') as f:
                self.training_logs = pickle.load(f)
            print(f"✅ Loaded TrainingLogs with {len(self.training_logs.epochs)} epochs")
        else:
            self.training_logs = TrainingLogs()
            print("🆕 Created new TrainingLogs")
        
        # Load ModelWrapper
        model_path = files_folder / "model_wrapper.pkl"
        if osp.exists(model_path):
            with open(model_path, 'rb') as f:
                self.model_wrapper = pickle.load(f)
            print(f"✅ Loaded ModelWrapper (last updated: {self.model_wrapper.last_updated})")
        else:
            self.model_wrapper = ModelWrapper()
            print("🆕 Created new ModelWrapper")
    
    def save(self):
        """
        Save TrainingLogs and ModelWrapper to storage
        """
        print("💾 Saving ML objects...")
        
        if not self.storage_path:
            raise RuntimeError("Storage not set up! Call setup() first.")
        
        files_folder = self.paths['files_root']
        
        # Save TrainingLogs
        if self.training_logs:
            self.training_logs.prepare_for_save()
            logs_path = files_folder / "training_logs.pkl"
            
            with open(logs_path, 'wb') as f:
                pickle.dump(self.training_logs, f)
            
            # Update file tree
            self.file_tree_manage(str(logs_path), remove=False)
            
            # Update main config
            self.main_config['latest_training_logs'] = {
                'path': str(logs_path),
                'epochs_count': len(self.training_logs.epochs),
                'last_updated': datetime.now().isoformat()
            }
            
            print(f"✅ Saved TrainingLogs with {len(self.training_logs.epochs)} epochs")
        
        # Save ModelWrapper
        if self.model_wrapper:
            model_path = files_folder / "model_wrapper.pkl"
            
            with open(model_path, 'wb') as f:
                pickle.dump(self.model_wrapper, f)
            
            # Update file tree
            self.file_tree_manage(str(model_path), remove=False)
            
            # Update main config
            self.main_config['latest_model_wrapper'] = {
                'path': str(model_path),
                'training_epochs': self.model_wrapper.training_epochs,
                'last_updated': self.model_wrapper.last_updated
            }
            
            print(f"✅ Saved ModelWrapper (epochs: {self.model_wrapper.training_epochs})")
            
            # Backup model weights if model exists
            if self.model_wrapper.model is not None:
                self._backup_model_weights()
        
        # Save YAML configs
        self._save_yaml_configs()
        print("✅ Saved configuration files")
    
    def _backup_model_weights(self):
        """Backup the ModelWrapper file using the imported backup function"""
        if not self.model_wrapper:
            return
        
        # Path to the current ModelWrapper file
        files_folder = self.paths['files_root']
        model_wrapper_path = files_folder / "model_wrapper.pkl"
        
        # Only backup if the file exists
        if not model_wrapper_path.exists():
            print("❌ ModelWrapper file doesn't exist yet - nothing to backup")
            return
        
        # Use the backup function to copy ModelWrapper to backups folder
        backup_dir = self.paths['backups_weights']
        backup_results = make_non_duplicate_backups(
            [str(model_wrapper_path)], 
            str(backup_dir)
        )
        
        # Check if backup was successful
        if backup_results[0] is True:
            print(f"🔄 Backed up ModelWrapper file to backups folder")
        elif backup_results[0] is False:
            print(f"🔄 ModelWrapper backup already exists - skipped")
        else:
            print(f"❌ Failed to backup ModelWrapper file")
    
    def get_path(self, path_name: str) -> Path:
        """
        Get a specific storage path
        
        Args:
            path_name: One of 'graphs', 'test_showcase_images', 'backups_weights', 'files_root'
        
        Returns:
            Path object for the requested directory
        """
        if path_name not in self.paths:
            available = list(self.paths.keys())
            raise ValueError(f"Path '{path_name}' not available. Available: {available}")
        
        return self.paths[path_name]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the current storage state"""
        summary = {
            'storage_path': str(self.storage_path) if self.storage_path else None,
            'available_paths': list(self.paths.keys()),
            'main_config_entries': len(self.main_config),
            'file_tree_entries': len(self.file_tree),
            'training_logs_epochs': len(self.training_logs.epochs) if self.training_logs else 0,
            'model_wrapper_epochs': self.model_wrapper.training_epochs if self.model_wrapper else 0
        }
        return summary


# Create the global singleton instance
ml_storage = SimpleMLStorage()


def demo_simple_workflow():
    """
    Demonstrate the simple workflow: setup -> load -> train -> save
    """
    print("🎯 Demo: Simple ML Storage Workflow")
    print("=" * 50)
    
    # 1. Setup
    ml_storage.setup("./simple_ml_project", "image_classifier")
    
    # 2. Load existing data (or create new)
    ml_storage.load()
    


    for _ in range(3):

        # 3. Simulate training
        print("\n🏋️  Simulating training...")
        
        # Add some training data
        for epoch in range(1, 6):
            loss = 2.0 - (epoch * 0.3)  # Decreasing loss
            accuracy = 0.4 + (epoch * 0.1)  # Increasing accuracy
            ml_storage.training_logs.add_epoch(epoch, loss, accuracy)
        
        # Create/update model
        mock_model = {'layers': [128, 64, 10], 'weights': 'pretend_weights', 'optimizer': 'adam'}
        ml_storage.model_wrapper.update_model(mock_model)
        ml_storage.model_wrapper.add_metadata('architecture', 'CNN')
        ml_storage.model_wrapper.add_metadata('dataset', 'CIFAR-10')
        
        # 4. Save everything
        print("\n💾 Saving progress...")
        ml_storage.save()
        
        # 5. Show summary
        print("\n📊 Storage Summary:")
        summary = ml_storage.get_summary()
        for key, value in summary.items():
            print(f"   {key}: {value}")
        
        # 6. Show available paths
        print("\n📁 Available storage paths:")
        for name in ['graphs', 'test_showcase_images', 'backups_weights']:
            path = ml_storage.get_path(name)
            print(f"   {name}: {path}")


if __name__ == "__main__":
    demo_simple_workflow()