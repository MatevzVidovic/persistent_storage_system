# improved_storage.py
# A Clear, Semantic Storage System for Machine Learning Projects
# Now with meaningful checkpoint names and clear workflow!

import os
import os.path as osp
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import pickle
from datetime import datetime
from enum import Enum

# Import the persistent storage system modules (assumed to exist)
from persistent_storage_system.singleton_storage_fns import main as setup_storage, SetupNames
import persistent_storage_system.yaml_handler as yh
import persistent_storage_system.json_handler as jh
from persistent_storage_system.helpers_storage import (
    novel_filename, 
    get_no_overwrite_path,
    make_non_duplicate_backups
)


class TrainingPhase(Enum):
    """Clear names for different phases of training"""
    INITIALIZATION = "initialization"        # Setting up the project
    TRAINING_START = "training_start"       # Beginning training
    MID_TRAINING = "mid_training"           # Halfway through training  
    TRAINING_COMPLETE = "training_complete" # Finished training
    EVALUATION = "evaluation"               # Testing the model
    DEPLOYMENT_READY = "deployment_ready"   # Ready to use


class MLProjectStorage:
    """
    A storage system for machine learning projects that makes sense!
    
    Think of this like a smart filing cabinet that:
    - Organizes your ML project files
    - Saves your progress at important moments
    - Lets you go back to any saved point
    - Keeps track of what you've done
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLProjectStorage, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.storage_path: Optional[Path] = None
            self.project_config: Dict[str, Any] = {}      # Main project settings
            self.project_metadata: Dict[str, Any] = {}    # Info about the project
            self.saved_checkpoints: Dict[str, Any] = {}   # What we've saved and when
            self.current_phase = TrainingPhase.INITIALIZATION
            self.setup_names = SetupNames()
            MLProjectStorage._initialized = True
    
    def start_new_project(self, project_folder: str, project_name: str = ""):
        """
        Start a new ML project - like creating a new game save folder
        
        Args:
            project_folder: Where to save everything
            project_name: What to call this project
        """
        print(f"🚀 Starting new ML project: {project_name or 'Unnamed Project'}")
        
        # Create the folder structure
        self.storage_path = Path(setup_storage(
            project_folder, 
            path_is_only_to_container=True, 
            semantic_id_of_proc=project_name
        ))
        
        print(f"📁 Project folder created at: {self.storage_path}")
        
        # Load any existing files
        self._load_all_project_files()
        
        # Set up basic project info
        if not self.project_metadata:
            self.project_metadata = {
                'project_name': project_name,
                'created_at': datetime.now().isoformat(),
                'current_phase': self.current_phase.value,
                'total_saves': 0,
                'description': 'ML Project managed by semantic storage system'
            }
            self._save_project_metadata()
        
        print("✅ Project initialization complete!")
    
    def _load_all_project_files(self):
        """Load all the project files into memory"""
        if not self.storage_path:
            raise RuntimeError("No project started! Call start_new_project() first.")
        
        # Load main project config
        main_config_path = self.storage_path / self.setup_names.MAIN_YAML
        if osp.exists(main_config_path):
            self.project_config = yh.get_yaml(main_config_path) or {}
        
        # Load project metadata  
        metadata_path = self.storage_path / self.setup_names.SHARED_STORAGE_YAML
        if osp.exists(metadata_path):
            self.project_metadata = yh.get_yaml(metadata_path) or {}
            # Restore current phase
            if 'current_phase' in self.project_metadata:
                try:
                    self.current_phase = TrainingPhase(self.project_metadata['current_phase'])
                except ValueError:
                    self.current_phase = TrainingPhase.INITIALIZATION
        
        # Load checkpoint history
        checkpoints_path = self.storage_path / self.setup_names.TINY_DB_JSON
        if osp.exists(checkpoints_path):
            self.saved_checkpoints = jh.get_json(checkpoints_path) or {}
    
    def _save_project_metadata(self):
        """Save project info to file"""
        if not self.storage_path:
            return
        metadata_path = self.storage_path / self.setup_names.SHARED_STORAGE_YAML
        yh.write_yaml(self.project_metadata, metadata_path)
    
    def _save_project_config(self):
        """Save main config to file"""
        if not self.storage_path:
            return
        config_path = self.storage_path / self.setup_names.MAIN_YAML
        yh.write_yaml(self.project_config, config_path)
    
    def _save_checkpoint_history(self):
        """Save the list of all checkpoints"""
        if not self.storage_path:
            return
        checkpoints_path = self.storage_path / self.setup_names.TINY_DB_JSON
        jh.write_json(self.saved_checkpoints, checkpoints_path)
    
    def move_to_phase(self, new_phase: TrainingPhase, phase_config: Optional[Dict] = None):
        """
        Move to a new phase of the project
        
        Args:
            new_phase: Which phase we're moving to
            phase_config: Any settings for this phase
        """
        print(f"📊 Moving from {self.current_phase.value} to {new_phase.value}")
        
        old_phase = self.current_phase
        self.current_phase = new_phase
        
        # Update project config with phase info
        self.project_config[f'{new_phase.value}_started_at'] = datetime.now().isoformat()
        if phase_config:
            self.project_config[f'{new_phase.value}_config'] = phase_config
        
        # Update metadata
        self.project_metadata['current_phase'] = new_phase.value
        self.project_metadata['phase_history'] = self.project_metadata.get('phase_history', [])
        self.project_metadata['phase_history'].append({
            'from_phase': old_phase.value,
            'to_phase': new_phase.value,
            'changed_at': datetime.now().isoformat()
        })
        
        # Save the changes
        self._save_project_config()
        self._save_project_metadata()
        
        print(f"✅ Now in {new_phase.value} phase")
    
    def save_checkpoint(self, 
                       checkpoint_name: str,
                       model_state: Optional[Any] = None,
                       training_logs: Optional[Any] = None,
                       extra_data: Optional[Dict] = None,
                       description: str = ""):
        """
        Save your progress at any point - like saving your game
        
        Args:
            checkpoint_name: A clear name like "after_10_epochs" or "best_model"
            model_state: Your trained model
            training_logs: Training history and logs
            extra_data: Any other data you want to save
            description: Notes about this save point
        """
        print(f"💾 Saving checkpoint: {checkpoint_name}")
        
        if hasattr(training_logs, 'prepare_for_save'):
            training_logs.prepare_for_save()
        
        checkpoint_data = {
            'name': checkpoint_name,
            'phase': self.current_phase.value,
            'saved_at': datetime.now().isoformat(),
            'description': description,
            'files_saved': []
        }
        
        # Save model if provided
        if model_state is not None:
            model_filename = f"model_{checkpoint_name}.pkl"
            model_path = self._save_object_to_file(model_state, model_filename)
            checkpoint_data['model_file'] = model_filename
            checkpoint_data['files_saved'].append(f"Model: {model_filename}")
            
            # Update current model reference
            self.project_metadata['current_best_model'] = model_filename
        
        # Save training logs if provided
        if training_logs is not None:
            logs_filename = f"logs_{checkpoint_name}.pkl"
            logs_path = self._save_object_to_file(training_logs, logs_filename)
            checkpoint_data['logs_file'] = logs_filename
            checkpoint_data['files_saved'].append(f"Logs: {logs_filename}")
        
        # Save extra data if provided
        if extra_data is not None:
            extra_filename = f"extra_{checkpoint_name}.pkl"
            extra_path = self._save_object_to_file(extra_data, extra_filename)
            checkpoint_data['extra_file'] = extra_filename
            checkpoint_data['files_saved'].append(f"Extra data: {extra_filename}")
        
        # Record this checkpoint
        self.saved_checkpoints[checkpoint_name] = checkpoint_data
        self.project_metadata['total_saves'] += 1
        self.project_metadata['last_save'] = checkpoint_name
        self.project_metadata['last_save_time'] = datetime.now().isoformat()
        
        # Save everything
        self._save_checkpoint_history()
        self._save_project_metadata()
        
        print(f"✅ Checkpoint '{checkpoint_name}' saved successfully!")
        print(f"   Saved files: {', '.join(checkpoint_data['files_saved'])}")
    
    def load_checkpoint(self, checkpoint_name: str) -> Dict[str, Any]:
        """
        Load a previously saved checkpoint - like loading a game save
        
        Args:
            checkpoint_name: Name of the checkpoint to load
            
        Returns:
            Dictionary with all the loaded data
        """
        print(f"📂 Loading checkpoint: {checkpoint_name}")
        
        if checkpoint_name not in self.saved_checkpoints:
            available = list(self.saved_checkpoints.keys())
            raise ValueError(f"Checkpoint '{checkpoint_name}' not found. Available: {available}")
        
        checkpoint_info = self.saved_checkpoints[checkpoint_name]
        loaded_data = {
            'checkpoint_info': checkpoint_info,
            'checkpoint_name': checkpoint_name
        }
        
        # Load model if available
        if 'model_file' in checkpoint_info:
            print(f"   Loading model from {checkpoint_info['model_file']}")
            loaded_data['model'] = self._load_object_from_file(checkpoint_info['model_file'])
        
        # Load logs if available  
        if 'logs_file' in checkpoint_info:
            print(f"   Loading logs from {checkpoint_info['logs_file']}")
            loaded_data['logs'] = self._load_object_from_file(checkpoint_info['logs_file'])
        
        # Load extra data if available
        if 'extra_file' in checkpoint_info:
            print(f"   Loading extra data from {checkpoint_info['extra_file']}")
            loaded_data['extra_data'] = self._load_object_from_file(checkpoint_info['extra_file'])
        
        print(f"✅ Checkpoint '{checkpoint_name}' loaded successfully!")
        return loaded_data
    
    def _save_object_to_file(self, obj: Any, filename: str) -> str:
        """Internal method to save objects to files"""
        if not self.storage_path:
            raise RuntimeError("No project started!")
        
        files_folder = self.storage_path / self.setup_names.FILES_FOLDER
        full_path = files_folder / filename
        
        # Make sure folder exists
        os.makedirs(full_path.parent, exist_ok=True)
        
        # Don't overwrite existing files
        final_path, _ = get_no_overwrite_path(
            str(full_path.with_suffix('')), 
            suffix='.pkl',
            warn_if_already_exists=True
        )
        
        # Save using pickle
        with open(final_path, 'wb') as f:
            pickle.dump(obj, f)
        
        return final_path
    
    def _load_object_from_file(self, filename: str) -> Any:
        """Internal method to load objects from files"""
        if not self.storage_path:
            raise RuntimeError("No project started!")
        
        files_folder = self.storage_path / self.setup_names.FILES_FOLDER
        full_path = files_folder / filename
        
        if not osp.exists(full_path):
            raise FileNotFoundError(f"File not found: {full_path}")
        
        with open(full_path, 'rb') as f:
            return pickle.load(f)
    
    def get_project_summary(self) -> Dict[str, Any]:
        """Get a summary of your project - like checking your game stats"""
        return {
            'project_name': self.project_metadata.get('project_name', 'Unnamed'),
            'current_phase': self.current_phase.value,
            'total_saves': self.project_metadata.get('total_saves', 0),
            'last_save': self.project_metadata.get('last_save'),
            'available_checkpoints': list(self.saved_checkpoints.keys()),
            'project_folder': str(self.storage_path) if self.storage_path else None,
            'current_best_model': self.project_metadata.get('current_best_model')
        }
    
    def list_all_checkpoints(self):
        """Show all saved checkpoints with details"""
        print(f"\n📋 All Checkpoints for '{self.project_metadata.get('project_name', 'Project')}':")
        print("=" * 60)
        
        if not self.saved_checkpoints:
            print("   No checkpoints saved yet.")
            return
        
        for name, info in self.saved_checkpoints.items():
            print(f"🔖 {name}")
            print(f"   Phase: {info['phase']}")
            print(f"   Saved: {info['saved_at']}")
            if info.get('description'):
                print(f"   Notes: {info['description']}")
            print(f"   Files: {', '.join(info.get('files_saved', []))}")
            print()


# Create the global instance
ml_storage = MLProjectStorage()


# Mock classes for demonstration
class TrainingLogs:
    """Example training logs that can be saved"""
    def __init__(self):
        self.epochs = []
        self.losses = []
        self.accuracies = []
        self.is_saved = False
    
    def add_epoch(self, epoch, loss, accuracy):
        self.epochs.append(epoch)
        self.losses.append(loss)
        self.accuracies.append(accuracy)
    
    def prepare_for_save(self):
        """Mark as saved before storage"""
        self.is_saved = True
        print(f"   Prepared {len(self.epochs)} training epochs for saving")


def demo_realistic_workflow():
    """
    Show how this would work in a real ML project
    This is the sequence that makes sense!
    """
    print("🎯 Demo: Realistic ML Project Workflow")
    print("=" * 50)
    
    # 1. Start a new project
    ml_storage.start_new_project("./my_ml_project", "Image Classifier")
    
    # 2. Move to training phase and save initial setup
    ml_storage.move_to_phase(
        TrainingPhase.TRAINING_START, 
        {'learning_rate': 0.001, 'batch_size': 32, 'epochs': 100}
    )
    
    initial_model = {'layers': 3, 'params': 1000000, 'initialized': True}
    ml_storage.save_checkpoint(
        "initial_model",
        model_state=initial_model,
        description="Fresh model before any training"
    )
    
    # 3. Simulate some training and save progress
    logs = TrainingLogs()
    logs.add_epoch(1, 2.5, 0.3)
    logs.add_epoch(2, 1.8, 0.5)
    logs.add_epoch(3, 1.2, 0.7)
    
    early_model = {'layers': 3, 'params': 1000000, 'trained_epochs': 3, 'loss': 1.2}
    ml_storage.save_checkpoint(
        "after_3_epochs",
        model_state=early_model,
        training_logs=logs,
        description="Early training checkpoint"
    )
    
    # 4. Move to mid-training and save best model so far
    ml_storage.move_to_phase(TrainingPhase.MID_TRAINING)
    
    for i in range(4, 11):
        logs.add_epoch(i, 1.2 - (i * 0.1), 0.7 + (i * 0.02))
    
    mid_model = {'layers': 3, 'params': 1000000, 'trained_epochs': 10, 'loss': 0.5}
    ml_storage.save_checkpoint(
        "mid_training_best",
        model_state=mid_model,
        training_logs=logs,
        extra_data={'validation_accuracy': 0.85, 'overfitting_check': False},
        description="Best model at halfway point"
    )
    
    # 5. Complete training
    ml_storage.move_to_phase(TrainingPhase.TRAINING_COMPLETE)
    
    final_model = {'layers': 3, 'params': 1000000, 'trained_epochs': 50, 'loss': 0.1}
    ml_storage.save_checkpoint(
        "final_trained_model",
        model_state=final_model,
        training_logs=logs,
        extra_data={'final_test_accuracy': 0.95, 'training_time_hours': 4.5},
        description="Completed training - ready for evaluation"
    )
    
    # 6. Show project summary
    print("\n📊 Project Summary:")
    summary = ml_storage.get_project_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    # 7. List all checkpoints
    ml_storage.list_all_checkpoints()
    
    # 8. Demonstrate loading a checkpoint
    print("\n🔄 Loading the best mid-training model...")
    loaded = ml_storage.load_checkpoint("mid_training_best")
    print(f"   Loaded model trained for {loaded['model']['trained_epochs']} epochs")
    print(f"   Model loss: {loaded['model']['loss']}")
    print(f"   Validation accuracy: {loaded['extra_data']['validation_accuracy']}")


if __name__ == "__main__":
    demo_realistic_workflow()