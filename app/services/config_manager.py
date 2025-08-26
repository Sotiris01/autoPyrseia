#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Config Manager για autoPyrseia
Δημιουργός: Σωτήριος Μπαλατσιάς

Διαχειρίζεται τις ρυθμίσεις της εφαρμογής
"""

import json
from pathlib import Path
from app.utils.path_manager import get_path_manager

class ConfigManager:
    def __init__(self):
        # Use the centralized path manager instead of calculating paths manually
        self.path_manager = get_path_manager()
        self.config_file = self.path_manager.project_root / "config.json"
        
        print(f"ConfigManager using config file: {self.config_file}")
        
        self.load_config()
    
    def load_config(self):
        """Φόρτωση των ρυθμίσεων"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                # Προεπιλεγμένες ρυθμίσεις
                self.config = {
                    "file_number": 1,
                    "username": "ΜΠΑΛΑΤΣΙΑΣ ΣΩΤΗΡΙΟΣ",
                    "organization_identity": "ΚΕΠΙΚ 8 Μ/Π ΤΑΞ",
                    "last_usb_path": "",
                    "auto_process": True,
                    "watch_downloads": True,
                    "backup_enabled": True
                }
                self.save_config()
        except Exception as e:
            print(f"Σφάλμα στη φόρτωση ρυθμίσεων: {e}")
            self.config = {}
    
    def save_config(self):
        """Αποθήκευση των ρυθμίσεων"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Σφάλμα στην αποθήκευση ρυθμίσεων: {e}")
    
    def get_next_file_number(self):
        """Λήψη του επόμενου αριθμού φακέλου"""
        return self.config.get("file_number", 8606)
    
    def increment_file_number(self):
        """Αύξηση του αριθμού φακέλου κατά 1"""
        current = self.get_next_file_number()
        self.config["file_number"] = current + 1
        self.save_config()
        return current
    
    def decrement_file_number(self):
        """Μείωση του αριθμού φακέλου κατά 1"""
        current = self.get_next_file_number()
        if current > 1:  # Prevent going below 1
            self.config["file_number"] = current - 1
            self.save_config()
        return current
    
    def set_file_number(self, file_number):
        """Ορισμός του αριθμού φακέλου"""
        self.config["file_number"] = file_number
        self.save_config()
    
    def get_username(self):
        """Λήψη του ονόματος χρήστη"""
        return self.config.get("username", "")
    
    def set_username(self, username):
        """Ορισμός του ονόματος χρήστη"""
        self.config["username"] = username
        self.save_config()
    
    def get_organization_identity(self):
        """Λήψη της ταυτότητας του οργανισμού"""
        return self.config.get("organization_identity", "ΚΕΠΙΚ 8 Μ/Π ΤΑΞ")
    
    def set_organization_identity(self, org_identity):
        """Ορισμός της ταυτότητας του οργανισμού"""
        self.config["organization_identity"] = org_identity
        self.save_config()
    
    def get_last_usb_path(self):
        """Λήψη της τελευταίας διαδρομής USB"""
        return self.config.get("last_usb_path", "")
    
    def set_last_usb_path(self, path):
        """Ορισμός της τελευταίας διαδρομής USB"""
        self.config["last_usb_path"] = path
        self.save_config()
    
    def get_setting(self, key, default=None):
        """Λήψη ρύθμισης"""
        return self.config.get(key, default)
    
    def set_setting(self, key, value):
        """Ορισμός ρύθμισης"""
        self.config[key] = value
        self.save_config()
