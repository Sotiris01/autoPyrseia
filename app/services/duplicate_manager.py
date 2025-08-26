#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duplicate Signal Detection and Management for autoPyrseia
"""

import hashlib
import json
import os
from pathlib import Path
from datetime import datetime
from app.utils.path_manager import get_path_manager


class DuplicateManager:
    """Manages duplicate signal detection and versioning using file system scanning"""
    
    def __init__(self):
        # In-memory database for current session
        self.signals_db = {}
        # Don't scan at startup - scan on-demand when needed
        
    def _scan_existing_signals(self):
        """Scan only DATA folder to build in-memory database"""
        path_manager = get_path_manager()
        data_folder = path_manager.data_folder
        
        # Only scan DATA folder, not BACK UP DATA
        if data_folder.exists():
            self._scan_folder_for_signals(data_folder)
    
    def _scan_folder_for_signals(self, base_folder):
        """Scan a folder for existing signals"""
        try:
            for recipient_folder in base_folder.iterdir():
                if not recipient_folder.is_dir():
                    continue
                
                recipient_name = recipient_folder.name
                
                for signal_folder in recipient_folder.iterdir():
                    if not signal_folder.is_dir():
                        continue
                    
                    signal_id = signal_folder.name
                    
                    # Handle versioned signals - extract original ID
                    original_id = signal_id
                    version_number = 0
                    
                    if '(' in signal_id and signal_id.endswith(')'):
                        try:
                            parts = signal_id.split('(')
                            original_id = parts[0]
                            version_str = parts[1].rstrip(')')
                            version_number = int(version_str)
                        except (ValueError, IndexError):
                            pass
                    
                    # Try to extract FM from signal_info.json if it exists
                    signal_info_path = signal_folder / "signal_info.json"
                    fm = "UNKNOWN"
                    
                    if signal_info_path.exists():
                        try:
                            import json
                            with open(signal_info_path, 'r', encoding='utf-8') as f:
                                signal_info = json.load(f)
                                fm = signal_info.get('fm', 'UNKNOWN')
                        except Exception:
                            pass
                    
                    # Generate serial number and register
                    serial_number = self.generate_serial_number(original_id, fm)
                    
                    if serial_number not in self.signals_db:
                        self.signals_db[serial_number] = {
                            'signal_id': original_id,
                            'fm': fm,
                            'serial_number': serial_number,
                            'first_processed': datetime.now().isoformat(),
                            'recipients': [],
                            'versions': {}
                        }
                    
                    # Add recipient if not already there
                    if recipient_name not in self.signals_db[serial_number]['recipients']:
                        self.signals_db[serial_number]['recipients'].append(recipient_name)
                    
                    # Register version if applicable
                    if version_number > 0:
                        versions = self.signals_db[serial_number].setdefault('versions', {})
                        recipient_versions = versions.setdefault(recipient_name, [])
                        if version_number not in recipient_versions:
                            recipient_versions.append(version_number)
                            recipient_versions.sort()
                            
        except Exception as e:
            print(f"Error scanning folder {base_folder}: {e}")
    
    def generate_serial_number(self, signal_id, fm):
        """Generate unique serial number from ID and FM combination"""
        # Create a consistent string from ID and FM
        combined_string = f"{signal_id.strip()}|{fm.strip()}"
        
        # Generate SHA-256 hash and take first 12 characters for readability
        hash_object = hashlib.sha256(combined_string.encode('utf-8'))
        serial_number = hash_object.hexdigest()[:12].upper()
        
        return serial_number
    
    def is_duplicate(self, signal_id, fm):
        """Check if signal is a duplicate based on serial number - scans fresh each time"""
        # Refresh database to get latest state from DATA folder
        self.refresh_database()
        
        serial_number = self.generate_serial_number(signal_id, fm)
        return serial_number in self.signals_db
    
    def get_duplicate_info(self, signal_id, fm):
        """Get information about existing duplicate signal - scans fresh each time"""
        # Refresh database to get latest state from DATA folder
        self.refresh_database()
        
        serial_number = self.generate_serial_number(signal_id, fm)
        return self.signals_db.get(serial_number, None)
    
    def get_recipients_with_signal(self, signal_id, fm):
        """Get list of recipients that already have this signal - scans fresh each time"""
        duplicate_info = self.get_duplicate_info(signal_id, fm)
        if duplicate_info:
            return duplicate_info.get('recipients', [])
        return []
    
    def register_signal(self, signal_id, fm, recipients):
        """Register a new signal in the in-memory database"""
        serial_number = self.generate_serial_number(signal_id, fm)
        
        if serial_number not in self.signals_db:
            self.signals_db[serial_number] = {
                'signal_id': signal_id,
                'fm': fm,
                'serial_number': serial_number,
                'first_processed': datetime.now().isoformat(),
                'recipients': [],
                'versions': {}
            }
        
        # Add recipients to the signal record
        existing_recipients = set(self.signals_db[serial_number]['recipients'])
        new_recipients = [r for r in recipients if r not in existing_recipients]
        self.signals_db[serial_number]['recipients'].extend(new_recipients)
        
        return serial_number
    
    def get_next_version_number(self, signal_id, fm, recipient):
        """Get the next version number for a duplicate signal"""
        duplicate_info = self.get_duplicate_info(signal_id, fm)
        if not duplicate_info:
            return 0  # First version
        
        versions = duplicate_info.get('versions', {})
        recipient_versions = versions.get(recipient, [])
        
        # Find the next available version number
        version = 1
        while version in recipient_versions:
            version += 1
        
        return version
    
    def register_version(self, signal_id, fm, recipient, version_number):
        """Register a new version of a signal for a recipient"""
        serial_number = self.generate_serial_number(signal_id, fm)
        
        if serial_number in self.signals_db:
            versions = self.signals_db[serial_number].setdefault('versions', {})
            recipient_versions = versions.setdefault(recipient, [])
            
            if version_number not in recipient_versions:
                recipient_versions.append(version_number)
                recipient_versions.sort()
    
    def get_versioned_signal_id(self, signal_id, version_number):
        """Get the versioned signal ID (e.g., 'R 111045Z AUG 25(1)')"""
        if version_number == 0:
            return signal_id
        return f"{signal_id}({version_number})"
    
    def check_folder_conflict_and_get_version(self, signal_id, fm, recipient_name):
        """
        Check if signal ID folder exists for recipient but with different serial number.
        Returns version number to use if folder conflict exists, 0 if no conflict.
        Only checks DATA folder (not BACK UP DATA).
        """
        path_manager = get_path_manager()
        data_folder = path_manager.data_folder
        
        current_serial = self.generate_serial_number(signal_id, fm)
        
        # Check only DATA folder
        if not data_folder.exists():
            return 0
                
        recipient_folder = data_folder / recipient_name
        if not recipient_folder.exists():
            return 0
        
        # Check if exact signal ID folder exists
        signal_folder = recipient_folder / signal_id
        if signal_folder.exists():
            # Read the signal_info.json to get the FM and check serial
            signal_info_path = signal_folder / "signal_info.json"
            if signal_info_path.exists():
                try:
                    with open(signal_info_path, 'r', encoding='utf-8') as f:
                        signal_info = json.load(f)
                        existing_fm = signal_info.get('fm', 'UNKNOWN')
                        existing_serial = self.generate_serial_number(signal_id, existing_fm)
                        
                        # If different serial numbers, this is a different signal with same ID
                        if existing_serial != current_serial:
                            # Find the next available version number for this ID (not serial)
                            return self._get_next_id_version_number(recipient_folder, signal_id)
                except Exception:
                    # If we can't read the file, assume conflict and version it
                    return self._get_next_id_version_number(recipient_folder, signal_id)
        
        return 0  # No conflict
    
    def _get_next_id_version_number(self, recipient_folder, signal_id):
        """Get the next available version number for a signal ID in a recipient folder"""
        version = 1
        while True:
            versioned_folder = recipient_folder / f"{signal_id}({version})"
            if not versioned_folder.exists():
                return version
            version += 1
    
    def refresh_database(self):
        """Refresh the in-memory database by re-scanning folders"""
        self.signals_db = {}
        self._scan_existing_signals()
