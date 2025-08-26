#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Signal processing controller for autoPyrseia
"""

import threading
import tkinter as tk
from app.ui.dialogs.manual_input import ManualInputDialog
from app.utils.file_operations import check_attachment_exists


class SignalController:
    """Controller for signal processing operations"""
    
    def __init__(self, app_instance):
        self.app = app_instance
    
    def handle_new_signal(self):
        """Χειρισμός νέου σήματος"""
        # Hide processing results when new signal is detected
        self.app.hide_processing_results()
        
        # Switch to first tab (Signal Processing) when new signal detected
        self.app.root.after(0, lambda: self.app.notebook.select(0))
        
        # Start progress operation
        self.app.progress_manager.start_operation(
            "signal_detection", 
            "Ανιχνεύθηκε νέο σήμα - Επεξεργασία...", 
            5
        )
        
        def process_in_thread():
            try:
                self.app.root.after(0, lambda: self.app.progress_manager.smooth_progress("signal_detection", 15, 200))
                self.app.root.after(200, lambda: self.app.progress_manager.update_message("signal_detection", "Άνοιγμα PDF αρχείου..."))
                
                self.app.root.after(400, lambda: self.app.progress_manager.smooth_progress("signal_detection", 40, 300))
                self.app.root.after(700, lambda: self.app.progress_manager.update_message("signal_detection", "Ανάλυση περιεχομένου PDF..."))
                
                signal_data = self.app.pdf_processor.process_pdf("downloads/pyrseia_server.pdf")
                
                self.app.root.after(0, lambda: self.app.progress_manager.smooth_progress("signal_detection", 85, 200))
                self.app.root.after(200, lambda: self.app.progress_manager.update_message("signal_detection", "Ολοκλήρωση επεξεργασίας..."))
                
                self.app.root.after(400, lambda: self.app.display_signal_data(signal_data))
            except Exception as e:
                self.app.root.after(0, lambda: self.handle_pdf_error(str(e)))
        
        threading.Thread(target=process_in_thread, daemon=True).start()
    
    def handle_manual_input_required(self, signal_data):
        """Χειρισμός manual input requirement"""
        # Complete progress first
        self.app.progress_manager.complete_operation("signal_detection", "Απαιτείται χειροκίνητη εισαγωγή στοιχείων και επιλογή παραληπτών")
        self.app.root.after(800, lambda: self.app.progress_manager.reset_progress("signal_detection"))
        
        # Εμφάνιση dialog για manual input
        dialog = ManualInputDialog(self.app.root, signal_data.get('attachments', []))
        if dialog.result:
            # Δημιουργία νέου signal_data με manual input και παραλήπτες
            manual_signal_data = self.app.pdf_processor.create_manual_signal_data(
                dialog.result['id'], 
                dialog.result['fm'], 
                "downloads/pyrseia_server.pdf"
            )
            
            # Update theme if provided by user
            if dialog.result.get('theme'):
                manual_signal_data['theme'] = dialog.result['theme']
            
            # Update attachments with user selection
            if dialog.result.get('attachments'):
                manual_signal_data['attachments'] = dialog.result['attachments']
            
            # Προσθήκη των επιλεγμένων παραληπτών στα δεδομένα του σήματος
            manual_signal_data['recipients'] = dialog.result.get('recipients', [])
            
            # Μαρκάρισμα ότι είναι manual input για σωστό handling
            manual_signal_data['is_manual_input'] = True
            
            # Εμφάνιση των νέων δεδομένων
            self.app.display_signal_data(manual_signal_data)
        else:
            # Ο χρήστης ακύρωσε - επαναφορά στην αρχική κατάσταση
            self.app.progress_manager.reset_progress("signal_detection", "Ακυρώθηκε η εισαγωγή στοιχείων")
    
    def process_signal(self):
        """Επεξεργασία του σήματος"""
        if not self.app.current_signal_data:
            return
        
        # Start signal processing operation
        self.app.progress_manager.start_operation("signal_processing", "Επεξεργασία σήματος...", 5)
        
        def process_in_thread():
            try:
                # Έλεγχος συνημμένων
                self.app.root.after(0, lambda: self.app.progress_manager.smooth_progress("signal_processing", 15, 200))
                self.app.root.after(200, lambda: self.app.progress_manager.update_message("signal_processing", "Έλεγχος συνημμένων αρχείων..."))
                
                attachments = self.app.current_signal_data.get('attachments', [])
                missing_attachments = [att for att in attachments if not check_attachment_exists(att)]
                
                if missing_attachments:
                    self.app.root.after(0, lambda: self.app.progress_manager.reset_progress("signal_processing", f"Αναμονή για {len(missing_attachments)} συνημμένα"))
                    return
                
                # Λήψη επιλεγμένων παραληπτών από checkboxes
                self.app.root.after(400, lambda: self.app.progress_manager.smooth_progress("signal_processing", 35, 200))
                self.app.root.after(600, lambda: self.app.progress_manager.update_message("signal_processing", "Προετοιμασία παραληπτών..."))
                
                selected_recipients = self.app.get_selected_recipients()
                
                if not selected_recipients:
                    self.app.root.after(0, lambda: self.app.progress_manager.reset_progress("signal_processing", "Δεν επιλέχθηκαν παραλήπτες"))
                    return
                
                # Επεξεργασία με τον signal manager
                self.app.root.after(800, lambda: self.app.progress_manager.smooth_progress("signal_processing", 60, 300))
                self.app.root.after(1100, lambda: self.app.progress_manager.update_message("signal_processing", "Αποθήκευση σήματος..."))
                
                # Handle duplicate signal processing with versioning
                current_signal_data = self.app.current_signal_data
                signal_id = current_signal_data.get('id', '')
                fm = current_signal_data.get('fm', '')
                
                versioned_signal_data = current_signal_data.copy()
                
                # Process each recipient to handle different cases
                final_recipients = []
                for recipient in selected_recipients:
                    if isinstance(recipient, dict):
                        recipient_name = recipient.get('name', str(recipient))
                        is_temporary = recipient.get('is_temporary', False)
                        folder_path = recipient.get('folder_path', None)
                    else:
                        recipient_name = str(recipient)
                        is_temporary = False
                        folder_path = None
                    
                    # Check if this recipient already has this exact signal (same serial)
                    recipients_with_signal = self.app.duplicate_manager.get_recipients_with_signal(signal_id, fm)
                    
                    if recipient_name in recipients_with_signal:
                        # This is a duplicate for this recipient - create versioned ID
                        version_number = self.app.duplicate_manager.get_next_version_number(signal_id, fm, recipient_name)
                        versioned_id = self.app.duplicate_manager.get_versioned_signal_id(signal_id, version_number)
                        
                        # Register the new version
                        self.app.duplicate_manager.register_version(signal_id, fm, recipient_name, version_number)
                        
                        # Create a copy of signal data with versioned ID for this recipient
                        recipient_signal_data = versioned_signal_data.copy()
                        recipient_signal_data['id'] = versioned_id
                        recipient_signal_data['original_id'] = signal_id
                        recipient_signal_data['version_number'] = version_number
                        
                        # Process this recipient with versioned signal - preserve temporary recipient info
                        final_recipients.append({
                            'name': recipient_name,
                            'signal_data': recipient_signal_data,
                            'is_temporary': is_temporary,
                            'folder_path': folder_path
                        })
                    else:
                        # Check for folder conflict with different signal (same ID, different FM)
                        folder_version = self.app.duplicate_manager.check_folder_conflict_and_get_version(signal_id, fm, recipient_name)
                        
                        if folder_version > 0:
                            # Folder conflict exists - use versioned ID
                            versioned_id = self.app.duplicate_manager.get_versioned_signal_id(signal_id, folder_version)
                            
                            # Create a copy of signal data with versioned ID for this recipient
                            recipient_signal_data = versioned_signal_data.copy()
                            recipient_signal_data['id'] = versioned_id
                            recipient_signal_data['original_id'] = signal_id
                            recipient_signal_data['folder_conflict_version'] = folder_version
                            
                            # Process this recipient with versioned signal - preserve temporary recipient info
                            final_recipients.append({
                                'name': recipient_name,
                                'signal_data': recipient_signal_data,
                                'is_temporary': is_temporary,
                                'folder_path': folder_path
                            })
                        else:
                            # No conflict - use original signal - preserve temporary recipient info
                            final_recipients.append({
                                'name': recipient_name,
                                'signal_data': versioned_signal_data,
                                'is_temporary': is_temporary,
                                'folder_path': folder_path
                            })
                
                # Now process the recipients with their appropriate signal data
                result = self.app.signal_manager.process_signal_with_versions(final_recipients)
                
                self.app.root.after(0, lambda: self.app.progress_manager.smooth_progress("signal_processing", 90, 200))
                self.app.root.after(200, lambda: self.app.progress_manager.update_message("signal_processing", "Ολοκλήρωση επεξεργασίας..."))
                
                # Add detailed information to result for success message
                result['attachments_count'] = len(attachments)
                result['attachments_copied'] = len(attachments)  # For display purposes
                
                # Add processing time
                from datetime import datetime
                result['processing_time'] = datetime.now().strftime("%H:%M:%S")
                
                # Extract just the recipient names for history logging
                recipient_names = []
                processed_recipients = []
                
                for recipient_info in final_recipients:
                    recipient_name = recipient_info['name']
                    recipient_names.append(recipient_name)
                    processed_recipients.append(recipient_name)
                
                # Register the signal with selected recipients in duplicate manager
                self.app.duplicate_manager.register_signal(signal_id, fm, processed_recipients)
                
                result['selected_recipients'] = recipient_names
                
                # Add verification flags for success message
                result['pdf_copied_to_all'] = result.get('success', False) and len(result.get('failed_recipients', [])) == 0
                result['attachments_copied_to_all'] = result['pdf_copied_to_all']  # If PDF copied successfully, attachments were too
                result['history_updated'] = True  # Will be updated after this point
                result['downloads_cleaned'] = True  # Will be cleaned after success
                
                # Complete the progress and then call signal_processed_successfully
                self.app.root.after(400, lambda: self.app.progress_manager.complete_operation("signal_processing", "Επεξεργασία σήματος ολοκληρώθηκε"))
                self.app.root.after(600, lambda: self.app.signal_processed_successfully(result, versioned_signal_data))
                
            except Exception as e:
                self.app.root.after(0, lambda: self.app.progress_manager.reset_progress("signal_processing", f"Σφάλμα: {str(e)}"))
        
        threading.Thread(target=process_in_thread, daemon=True).start()
    
    def handle_pdf_error(self, error_message):
        """Χειρισμός σφάλματος PDF"""
        self.app.progress_manager.reset_progress("signal_detection", "Σφάλμα στην επεξεργασία του PDF")
        
        # Διαγραφή του downloads folder
        from app.utils.file_operations import clear_downloads_folder
        clear_downloads_folder()
        
        # Ενημέρωση χρήστη
        if hasattr(self.app, 'attachments_frame'):
            for widget in self.app.attachments_frame.winfo_children():
                widget.destroy()
            error_label = tk.Label(self.app.attachments_frame, 
                                  text="ΣΦΑΛΜΑ: Επανεκκίνηση λήψης σήματος", 
                                  fg='red', font=('Arial', 10, 'bold'))
            error_label.pack()
    
    def handle_pdf_deletion(self):
        """Χειρισμός διαγραφής του pyrseia_server.pdf από τον χρήστη"""
        self.app.progress_manager.global_message("Το PDF σήματος διαγράφηκε - Καθαρισμός δεδομένων...")
        
        # Καθαρισμός των εξαγμένων δεδομένων
        self.app.current_signal_data = None
        
        # Καθαρισμός του UI
        self.app.clear_signal_display()
        
        # Απενεργοποίηση του κουμπιού επεξεργασίας
        if hasattr(self.app, 'process_button'):
            self.app.process_button.config(state='disabled')
        
        # Ενημέρωση status
        self.app.progress_manager.global_message("Έτοιμο για νέο σήμα")
