#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File watcher controller for autoPyrseia
"""

import threading
import time
from pathlib import Path
from app.utils.path_manager import get_path_manager


class FileWatcher:
    """File watcher for monitoring downloads folder"""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.running = False
        self.thread = None
        # Memory optimization - limit stored file references
        self._max_file_history = 1000  # Limit to prevent memory leak
    
    def start(self):
        """Start the file watcher"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._watch_downloads, daemon=True)
            self.thread.start()
    
    def stop(self):
        """Stop the file watcher"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)  # Wait for clean shutdown
    
    def _watch_downloads(self):
        """Watch downloads folder for changes"""
        path_manager = get_path_manager()
        downloads_path = path_manager.downloads_folder
        last_files = set()
        last_pdf_existed = False
        file_history = []  # Track file changes history
        
        while self.running:
            try:
                if downloads_path.exists():
                    current_files = set(f.name for f in downloads_path.glob("*") if f.is_file())
                    
                    # Έλεγχος για pyrseia_server.pdf
                    pdf_files = list(downloads_path.glob("pyrseia_server.pdf"))
                    pdf_exists = bool(pdf_files)
                    
                    # Έλεγχος για νέο pyrseia_server.pdf
                    if pdf_exists and not self.app.current_signal_data:
                        self.app.safe_schedule_ui_update(self.app.handle_new_signal)
                    
                    # Έλεγχος για διαγραφή του pyrseia_server.pdf
                    if last_pdf_existed and not pdf_exists and self.app.current_signal_data:
                        self.app.safe_schedule_ui_update(self.app.handle_pdf_deletion)
                    
                    # Έλεγχος για αλλαγές στα αρχεία (νέα συνημμένα)
                    if current_files != last_files and self.app.current_signal_data:
                        # Ενημέρωση των indicators για συνημμένα
                        self.app.safe_schedule_ui_update(self.app.update_attachment_indicators)
                    
                    # Memory management - cleanup old file history
                    if len(file_history) > self._max_file_history:
                        file_history = file_history[-self._max_file_history//2:]  # Keep only recent half
                    
                    # Store current state
                    file_history.append({
                        'timestamp': time.time(),
                        'files': current_files.copy(),
                        'pdf_exists': pdf_exists
                    })
                    
                    last_files = current_files
                    last_pdf_existed = pdf_exists
                
                time.sleep(1)  # Μειώνουμε το interval για πιο γρήγορη ανίχνευση
                
            except Exception as e:
                # Αν υπάρχει σφάλμα, συνεχίζουμε το loop χωρίς να σταματήσουμε
                print(f"Σφάλμα στο file watcher: {e}")
                time.sleep(2)  # Περιμένουμε λίγο παραπάνω σε περίπτωση σφάλματος
        
        # Cleanup on exit
        file_history.clear()
        last_files.clear()
