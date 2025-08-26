#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Signal Manager για autoPyrseia
Δημιουργός: Σωτήριος Μπαλατσιάς

Διαχειρίζεται την επεξεργασία και αποθήκευση των σημάτων
"""

import json
import shutil
import os
from pathlib import Path
from datetime import datetime
from app.utils.path_manager import get_path_manager

class SignalManager:
    def __init__(self):
        # Use the centralized path manager instead of calculating paths manually
        self.path_manager = get_path_manager()
        self.data_folder = self.path_manager.data_folder
        self.downloads_folder = self.path_manager.downloads_folder
        self.backup_folder = self.path_manager.backup_folder
        
        print(f"SignalManager using DATA folder: {self.data_folder}")
        print(f"SignalManager using downloads folder: {self.downloads_folder}")
        
        # Δημιουργία φακέλων αν δεν υπάρχουν (path manager should have done this, but just in case)
        self.data_folder.mkdir(parents=True, exist_ok=True)
        self.backup_folder.mkdir(parents=True, exist_ok=True)
    
    def process_signal(self, signal_data, selected_recipients):
        """Επεξεργασία σήματος για τους επιλεγμένους παραλήπτες"""
        try:
            processed_recipients = []
            failed_recipients = []
            duplicate_recipients = []
            
            for recipient_data in selected_recipients:
                # Handle both old format (string) and new format (dict)
                if isinstance(recipient_data, str):
                    recipient_name = recipient_data
                    is_temporary = False
                    folder_path = None
                else:
                    recipient_name = recipient_data['name']
                    is_temporary = recipient_data.get('is_temporary', False)
                    folder_path = recipient_data.get('folder_path', None)
                
                result = self.process_recipient(signal_data, recipient_name, is_temporary, folder_path)
                if result['success']:
                    processed_recipients.append({
                        'name': recipient_name,
                        'folder_path': result['folder_path']
                    })
                elif result['duplicate']:
                    duplicate_recipients.append(recipient_name)
                else:
                    failed_recipients.append(recipient_name)
            
            if processed_recipients:
                # Καθαρισμός του downloads folder μετά την επιτυχή επεξεργασία
                self.clear_downloads_folder()
            
            return {
                'success': len(processed_recipients) > 0,
                'processed_recipients': processed_recipients,
                'failed_recipients': failed_recipients,
                'duplicate_recipients': duplicate_recipients,
                'signal_id': signal_data['id'],
                'total_processed': len(processed_recipients),
                'total_failed': len(failed_recipients),
                'total_duplicates': len(duplicate_recipients)
            }
            
        except Exception as e:
            print(f"Σφάλμα στην επεξεργασία σήματος: {e}")
            return {
                'success': False,
                'error': str(e),
                'processed_recipients': [],
                'failed_recipients': selected_recipients,
                'duplicate_recipients': []
            }
    
    def process_signal_with_versions(self, recipient_list):
        """Process signal with different signal data per recipient"""
        try:
            processed_recipients = []
            failed_recipients = []
            duplicate_recipients = []
            
            for recipient_info in recipient_list:
                recipient_name = recipient_info['name']
                signal_data = recipient_info['signal_data']
                is_temporary = recipient_info.get('is_temporary', False)
                folder_path = recipient_info.get('folder_path', None)
                
                # Use the signal data specific to this recipient with preserved temporary info
                result = self.process_recipient(signal_data, recipient_name, is_temporary, folder_path)
                if result['success']:
                    processed_recipients.append({
                        'name': recipient_name,
                        'folder_path': result['folder_path']
                    })
                elif result['duplicate']:
                    duplicate_recipients.append(recipient_name)
                else:
                    failed_recipients.append(recipient_name)
            
            if processed_recipients:
                # Καθαρισμός του downloads folder μετά την επιτυχή επεξεργασία
                self.clear_downloads_folder()
            
            # Use the original signal ID for reporting
            original_id = recipient_list[0]['signal_data'].get('original_id', recipient_list[0]['signal_data']['id'])
            
            return {
                'success': len(processed_recipients) > 0,
                'processed_recipients': processed_recipients,
                'failed_recipients': failed_recipients,
                'duplicate_recipients': duplicate_recipients,
                'signal_id': original_id,
                'total_processed': len(processed_recipients),
                'total_failed': len(failed_recipients),
                'total_duplicates': len(duplicate_recipients)
            }
            
        except Exception as e:
            print(f"Σφάλμα στην επεξεργασία σήματος με εκδόσεις: {e}")
            return {
                'success': False,
                'error': str(e),
                'processed_recipients': [],
                'failed_recipients': [r['name'] for r in recipient_list],
                'duplicate_recipients': []
            }
    
    def process_recipient(self, signal_data, recipient, is_temporary=False, temp_folder_path=None):
        """Επεξεργασία σήματος για έναν παραλήπτη"""
        try:
            # Handle temporary recipients differently - no DATA folder involvement
            if is_temporary:
                if not temp_folder_path:
                    print(f"Error: Temporary recipient '{recipient}' has no folder path specified")
                    return {'success': False, 'duplicate': False, 'error': 'No folder path specified for temporary recipient'}
                return self._process_temporary_recipient(signal_data, recipient, temp_folder_path)
            
            # Regular recipient processing in DATA folder
            recipient_folder = self.data_folder / recipient
            recipient_folder.mkdir(exist_ok=True)
            
            # Create signal folder using the signal ID (which may be versioned)
            signal_id = signal_data['id']
            signal_folder = recipient_folder / signal_id
            signal_folder.mkdir(exist_ok=True)
            
            # Αντιγραφή του PDF σήματος
            source_pdf = self.downloads_folder / "pyrseia_server.pdf"
            # Use original signal ID for PDF filename if this is a versioned signal
            original_id = signal_data.get('original_id', signal_id)
            target_pdf = signal_folder / f"{original_id}.pdf"
            shutil.copy2(source_pdf, target_pdf)
            
            # Αντιγραφή συνημμένων αρχείων
            self.copy_attachments(signal_data.get('attachments', []), signal_folder)
            
            # Create JSON file for regular recipients
            self.create_signal_json(signal_data, signal_folder, signal_id)
            
            return {'success': True, 'duplicate': False, 'folder_path': str(signal_folder)}
            
        except Exception as e:
            print(f"Σφάλμα στην επεξεργασία παραλήπτη {recipient}: {e}")
            return {'success': False, 'duplicate': False, 'error': str(e)}
    
    def _process_temporary_recipient(self, signal_data, recipient_name, temp_folder_path):
        """Process temporary recipient - completely independent of DATA folder"""
        try:
            # Use the selected folder directly as the target
            target_folder = Path(temp_folder_path)
            target_folder.mkdir(parents=True, exist_ok=True)
            
            # Create a subfolder with the signal ID for organization
            signal_id = signal_data['id']
            signal_folder = target_folder / signal_id
            
            # If folder exists, create a unique variant
            counter = 1
            original_signal_folder = signal_folder
            while signal_folder.exists():
                signal_folder = original_signal_folder.parent / f"{signal_id}_{counter}"
                counter += 1
            
            signal_folder.mkdir(exist_ok=True)
            
            # Copy the PDF signal
            source_pdf = self.downloads_folder / "pyrseia_server.pdf"
            target_pdf = signal_folder / f"{signal_id}.pdf"
            shutil.copy2(source_pdf, target_pdf)
            
            # Copy attachments
            self.copy_attachments(signal_data.get('attachments', []), signal_folder)
            
            # NO JSON file creation for temporary recipients
            # NO involvement with DATA folder structure
            
            return {'success': True, 'duplicate': False, 'folder_path': str(signal_folder)}
            
        except Exception as e:
            print(f"Σφάλμα στην επεξεργασία προσωρινού παραλήπτη {recipient_name}: {e}")
            return {'success': False, 'duplicate': False, 'error': str(e)}
    
    def create_unique_id_folder(self, recipient_folder, signal_id):
        """Δημιουργία μοναδικού φακέλου ID"""
        base_folder = recipient_folder / signal_id
        
        # Αν δεν υπάρχει, δημιουργούμε τον
        if not base_folder.exists():
            base_folder.mkdir()
            return base_folder
        
        # Αν υπάρχει, προσθέτουμε αριθμό
        counter = 1
        while True:
            new_folder = recipient_folder / f"{signal_id}({counter})"
            if not new_folder.exists():
                new_folder.mkdir()
                return new_folder
            counter += 1
    
    def copy_attachments(self, attachments, target_folder):
        """Αντιγραφή συνημμένων αρχείων"""
        for attachment in attachments:
            source_file = self.downloads_folder / attachment
            
            # Έλεγχος αν υπάρχει το αρχείο
            if source_file.exists():
                target_file = target_folder / attachment
                shutil.copy2(source_file, target_file)
            else:
                # Αναζήτηση για παρόμοιο όνομα αρχείου
                similar_file = self.find_similar_file(attachment)
                if similar_file:
                    target_file = target_folder / attachment
                    shutil.copy2(similar_file, target_file)
                else:
                    print(f"Προειδοποίηση: Δεν βρέθηκε το συνημμένο αρχείο {attachment}")
    
    def find_similar_file(self, target_filename):
        """Αναζήτηση για παρόμοιο όνομα αρχείου με βελτιωμένο fuzzy matching"""
        # Πρώτα έλεγχος ακριβούς ονόματος
        exact_file = self.downloads_folder / target_filename
        if exact_file.exists():
            return exact_file
        
        # Χρήση του προηγμένου fuzzy matching από file_operations
        from app.utils.file_operations import find_similar_filename
        similar_filename = find_similar_filename(target_filename, self.downloads_folder)
        
        if similar_filename:
            return self.downloads_folder / similar_filename
        
        return None
    
    def create_signal_json(self, signal_data, target_folder, signal_id):
        """Δημιουργία JSON αρχείου με τις πληροφορίες του σήματος"""
        json_data = {
            "id": signal_data['id'],
            "fm": signal_data['fm'],
            "theme": signal_data['theme'],
            "recipients": signal_data['recipients'],
            "attachments": signal_data['attachments'],
            "serial_number": signal_data['serial_number'],
            "processed_date": datetime.now().isoformat(),
            "pdf_filename": f"{signal_id}.pdf",
            "manual_input": signal_data.get('is_manual_input', False)  # Track if this was manual input
        }
        
        json_file = target_folder / "signal_info.json"
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    def clear_downloads_folder(self):
        """Καθαρισμός του φακέλου downloads"""
        try:
            for file in self.downloads_folder.glob("*"):
                if file.is_file():
                    file.unlink()
        except Exception as e:
            print(f"Σφάλμα στον καθαρισμό του φακέλου downloads: {e}")
    
    def get_recipient_signals(self, recipient_name):
        """Λήψη όλων των σημάτων για έναν παραλήπτη"""
        recipient_folder = self.data_folder / recipient_name
        signals = []
        
        if not recipient_folder.exists():
            return signals
        
        for signal_folder in recipient_folder.iterdir():
            if signal_folder.is_dir():
                # Αναζήτηση για JSON αρχείο (νέο naming pattern)
                json_file = signal_folder / "signal_info.json"
                
                # Fallback για παλιό naming pattern αν δεν υπάρχει το νέο
                if not json_file.exists():
                    old_json_files = list(signal_folder.glob("*_info.json"))
                    if old_json_files:
                        json_file = old_json_files[0]
                
                if json_file.exists():
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            signal_info = json.load(f)
                            signal_info['folder_path'] = str(signal_folder)
                            signal_info['folder_name'] = signal_folder.name
                            signals.append(signal_info)
                    except Exception as e:
                        print(f"Σφάλμα στην ανάγνωση JSON: {e}")
        
        return signals
    
    def get_all_recipients(self):
        """Λήψη όλων των παραληπτών που έχουν σήματα"""
        recipients = []
        
        if self.data_folder.exists():
            for recipient_folder in self.data_folder.iterdir():
                if recipient_folder.is_dir():
                    recipients.append(recipient_folder.name)
        
        return sorted(recipients)
    
    def move_to_backup(self, recipient_name, signal_folders, backup_subfolder):
        """Μετακίνηση σημάτων στο backup"""
        try:
            # Νέα δομή: BACK UP DATA/ΛΑΦ ΙΩΑΝΝΙΝΩΝ/Α.Φ. 8635/
            # Δημιουργία φακέλου παραλήπτη πρώτα
            recipient_backup_path = self.backup_folder / recipient_name
            recipient_backup_path.mkdir(parents=True, exist_ok=True)
            
            # Δημιουργία φακέλου αριθμού φακέλου μέσα στον παραλήπτη
            file_number_path = recipient_backup_path / backup_subfolder
            file_number_path.mkdir(exist_ok=True)
            
            # Μετακίνηση κάθε φακέλου σήματος
            for signal_folder in signal_folders:
                source_path = Path(signal_folder)
                target_path = file_number_path / source_path.name
                
                if source_path.exists():
                    shutil.move(str(source_path), str(target_path))
            
            return True
            
        except Exception as e:
            print(f"Σφάλμα στη μετακίνηση στο backup: {e}")
            return False
    
    def delete_recipient_signals(self, recipient_name, signal_folders):
        """Διαγραφή σημάτων παραλήπτη από το DATA"""
        try:
            for signal_folder in signal_folders:
                folder_path = Path(signal_folder)
                if folder_path.exists():
                    shutil.rmtree(folder_path)
            
            # Έλεγχος αν ο φάκελος παραλήπτη είναι άδειος
            recipient_folder = self.data_folder / recipient_name
            if recipient_folder.exists() and not any(recipient_folder.iterdir()):
                recipient_folder.rmdir()
            
            return True
            
        except Exception as e:
            print(f"Σφάλμα στη διαγραφή σημάτων: {e}")
            return False
    
    def scan_and_generate_missing_json_files(self, recipient_names=None):
        """Σάρωση και δημιουργία JSON αρχείων για σήματα που δεν έχουν"""
        try:
            generated_count = 0
            
            # Αν δεν δόθηκαν συγκεκριμένοι παραλήπτες, σαρώνουμε όλους
            if recipient_names is None:
                recipient_names = self.get_all_recipients()
            
            for recipient_name in recipient_names:
                recipient_folder = self.data_folder / recipient_name
                if not recipient_folder.exists():
                    continue
                
                # Σάρωση όλων των φακέλων σημάτων του παραλήπτη
                for signal_folder in recipient_folder.iterdir():
                    if not signal_folder.is_dir():
                        continue
                    
                    # Έλεγχος αν υπάρχει ήδη JSON αρχείο (νέο ή παλιό naming)
                    json_file = signal_folder / "signal_info.json"
                    old_json_files = list(signal_folder.glob("*_info.json")) if not json_file.exists() else []
                    
                    if json_file.exists() or old_json_files:
                        # Έλεγχος αν το JSON είναι από manual input - αν ναι, δεν το αντικαθιστούμε
                        try:
                            existing_json_file = json_file if json_file.exists() else old_json_files[0]
                            with open(existing_json_file, 'r', encoding='utf-8') as f:
                                existing_json = json.load(f)
                                if existing_json.get('manual_input', False):
                                    continue  # Δεν αντικαθιστούμε manual input JSON
                        except:
                            pass  # Αν δεν μπορούμε να διαβάσουμε το JSON, συνεχίζουμε
                        continue  # Υπάρχει ήδη JSON
                    
                    # Αναζήτηση PDF αρχείου με το όνομα του φακέλου
                    signal_id = signal_folder.name
                    pdf_file = signal_folder / f"{signal_id}.pdf"
                    
                    if not pdf_file.exists():
                        continue  # Δεν υπάρχει το αναμενόμενο PDF
                    
                    # Δημιουργία JSON από το PDF
                    if self.generate_json_from_pdf(pdf_file, signal_folder, signal_id):
                        generated_count += 1
            
            if generated_count > 0:
                pass

            
            return generated_count
            
        except Exception as e:
            print(f"Σφάλμα στη σάρωση JSON αρχείων: {e}")
            return 0
    
    def generate_json_from_pdf(self, pdf_file, signal_folder, signal_id):
        """Δημιουργία JSON αρχείου από PDF σήμα"""
        try:
            # Εισαγωγή PDFProcessor για ανάλυση του PDF
            from app.services.pdf_processor import PDFProcessor
            pdf_processor = PDFProcessor()
            
            # Ανάλυση του PDF αρχείου
            signal_data = pdf_processor.process_pdf(str(pdf_file))
            
            # Δημιουργία JSON δεδομένων
            json_data = {
                "id": signal_data.get('id', signal_id),
                "fm": signal_data.get('fm', ''),
                "theme": signal_data.get('theme', ''),
                "recipients": signal_data.get('recipients', []),
                "attachments": signal_data.get('attachments', []),  # Include attachments from PDF without scanning folder
                "serial_number": signal_data.get('serial_number', ''),
                "processed_date": datetime.now().isoformat(),
                "pdf_filename": f"{signal_id}.pdf",
                "auto_generated": True  # Σημάδι ότι δημιουργήθηκε αυτόματα
            }
            
            # Αποθήκευση JSON αρχείου
            json_file = signal_folder / "signal_info.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Σφάλμα στη δημιουργία JSON για {signal_id}: {e}")
            return False
