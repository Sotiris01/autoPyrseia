#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Path manager for autoPyrseia - Centralized path management
"""

import os
import sys
from pathlib import Path


class PathManager:
    """Centralized path management with automatic folder creation"""
    
    def __init__(self, base_dir=None):
        """Initialize path manager with base directory"""
        # Determine the correct base directory
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            self.base_dir = self._get_application_directory()
        
        # Define all application paths
        self._paths = {
            'data': self.base_dir / "DATA",
            'backup': self.base_dir / "BACK UP DATA", 
            'downloads': self.base_dir / "downloads",
            'templates': self.base_dir / "templates",
            'temp': self.base_dir / "temp"
        }
        
        # Ensure all required directories exist
        self._ensure_directories()
    
    def _get_application_directory(self):
        """Get the correct application directory whether running as script or executable"""
        # Check if we're running as a PyInstaller executable
        if getattr(sys, 'frozen', False):
            # We're running as a compiled executable
            # sys.executable is the path to the .exe file
            application_path = Path(sys.executable).parent
            
            # If we're in _internal folder, go up one level
            if application_path.name == '_internal':
                application_path = application_path.parent
            
            # IMPORTANT: Change the working directory to the correct location
            os.chdir(application_path)
            print(f"Running as executable from: {application_path}")
            print(f"Changed working directory to: {os.getcwd()}")
            return application_path
        else:
            # We're running as a Python script
            # Use the current working directory
            application_path = Path.cwd()
            print(f"Running as script from: {application_path}")
            return application_path
    
    def _ensure_directories(self):
        """Create all required directories if they don't exist"""
        print(f"Creating directories in: {self.base_dir}")
        for name, path in self._paths.items():
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"✓ Directory ensured: {path}")
            except Exception as e:
                print(f"✗ Failed to create directory {path}: {e}")
    
    @property
    def data_folder(self):
        """Get DATA folder path - always absolute"""
        return self._paths['data'].absolute()
    
    @property
    def project_root(self):
        """Get project root path - always absolute"""
        return self.base_dir.absolute()
    
    @property 
    def backup_folder(self):
        """Get BACK UP DATA folder path - always absolute"""
        return self._paths['backup'].absolute()
    
    @property
    def downloads_folder(self):
        """Get downloads folder path - always absolute"""
        return self._paths['downloads'].absolute()
    
    @property
    def templates_folder(self):
        """Get templates folder path - always absolute"""
        return self._paths['templates'].absolute()
    
    @property
    def temp_folder(self):
        """Get temp folder path - always absolute"""
        return self._paths['temp'].absolute()
    
    def get_path(self, name):
        """Get path by name - always absolute"""
        path = self._paths.get(name)
        return path.absolute() if path else None
    
    def ensure_path_exists(self, path):
        """Ensure a specific path exists"""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Failed to create path {path}: {e}")
            return False
    
    def get_recipient_folder(self, recipient_name, folder_type='data'):
        """Get recipient folder path in specified folder type"""
        base_folder = self._paths.get(folder_type, self._paths['data'])
        recipient_folder = base_folder / recipient_name
        
        # Ensure recipient folder exists
        self.ensure_path_exists(recipient_folder)
        return recipient_folder.absolute()
    
    def get_signal_folder(self, recipient_name, signal_id, folder_type='data'):
        """Get signal folder path for a specific recipient and signal"""
        recipient_folder = self.get_recipient_folder(recipient_name, folder_type)
        signal_folder = recipient_folder / signal_id
        
        # Don't auto-create signal folders - let the calling code decide
        return signal_folder.absolute()
    
    def validate_and_create_path(self, path_str):
        """Validate and create a path if it doesn't exist"""
        try:
            path = Path(path_str)
            path.mkdir(parents=True, exist_ok=True)
            return path
        except Exception as e:
            print(f"Path validation failed for {path_str}: {e}")
            return None


# Global instance for easy import
_path_manager = None

def get_path_manager():
    """Get the global path manager instance"""
    global _path_manager
    if _path_manager is None:
        _path_manager = PathManager()
    return _path_manager

def ensure_app_directories():
    """Ensure all application directories exist - call at app startup"""
    pm = get_path_manager()
    print("=== Ensuring Application Directories ===")
    print(f"Working directory: {os.getcwd()}")
    print(f"Base directory: {pm.base_dir}")
    return pm
