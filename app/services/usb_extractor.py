#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
USB Extractor για autoPyrseia
Δημιουργός: Σωτήριος Μπαλατσιάς

Διαχειρίζεται την εξαγωγή σημάτων σε USB stick
"""

import shutil
import os
import re
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.drawing.image import Image
import tempfile
import subprocess
import platform
from app.utils.path_manager import get_path_manager

class USBExtractor:
    def __init__(self, config_manager=None):
        # Use the centralized path manager instead of calculating paths manually
        self.path_manager = get_path_manager()
        self.data_folder = self.path_manager.data_folder
        self.backup_folder = self.path_manager.backup_folder
        self.templates_folder = self.path_manager.templates_folder
        self.signal_manager = None
        self.config_manager = config_manager
        
        print(f"USBExtractor using DATA folder: {self.data_folder}")
        print(f"USBExtractor using BACKUP folder: {self.backup_folder}")
        print(f"USBExtractor using templates folder: {self.templates_folder}")
    
    def set_signal_manager(self, signal_manager):
        """Ορισμός του signal manager"""
        self.signal_manager = signal_manager
    
    def copy_signal_folder_without_json(self, source_folder, target_folder):
        """Αντιγραφή φακέλου σήματος εκτός από JSON αρχεία"""
        source_path = Path(source_folder)
        target_path = Path(target_folder)
        
        # Δημιουργία φακέλου προορισμού
        target_path.mkdir(parents=True, exist_ok=True)
        
        # Αντιγραφή όλων των αρχείων εκτός από JSON
        for file in source_path.iterdir():
            if file.is_file() and not file.name.endswith('.json'):
                target_file = target_path / file.name
                shutil.copy2(file, target_file)
    
    def extract_to_usb(self, usb_path, selected_recipients, file_number, username, is_unofficial=False):
        """Κύρια μέθοδος εξαγωγής σε USB"""
        try:
            if is_unofficial:
                # For unofficial mode, use current date as folder name
                from datetime import datetime
                
                current_date = datetime.now()
                # Format as "08 ΑΥΓ 25" 
                day = current_date.strftime("%d")
                month_num = current_date.month
                year = current_date.strftime("%y")
                
                # Direct Greek month mapping using month number to avoid encoding issues
                greek_months = {
                    1: 'ΙΑΝ', 2: 'ΦΕΒ', 3: 'ΜΑΡ', 4: 'ΑΠΡ',
                    5: 'ΜΑΪ', 6: 'ΙΟΥΝ', 7: 'ΙΟΥΛ', 8: 'ΑΥΓ',
                    9: 'ΣΕΠ', 10: 'ΟΚΤ', 11: 'ΝΟΕ', 12: 'ΔΕΚ'
                }
                month = greek_months.get(month_num, 'ΑΥΓ')  # Default to ΑΥΓ if something goes wrong
                
                usb_folder_name = f"{day} {month} {year}"
            else:
                # Normal mode - use file number
                usb_folder_name = f"Α.Φ. {file_number}"
            
            usb_extraction_path = Path(usb_path) / usb_folder_name
            
            # Δημιουργία φακέλου εξαγωγής
            usb_extraction_path.mkdir(parents=True, exist_ok=True)
            
            # Συλλογή όλων των σημάτων για εξαγωγή
            all_signals_data = {}
            
            for recipient in selected_recipients:
                signals = self.signal_manager.get_recipient_signals(recipient)
                if signals:
                    # Δημιουργία φακέλου παραλήπτη στο USB
                    if len(selected_recipients) > 1:
                        recipient_usb_path = usb_extraction_path / recipient
                    else:
                        recipient_usb_path = usb_extraction_path
                    
                    recipient_usb_path.mkdir(exist_ok=True)
                    
                    # Αντιγραφή φακέλων σημάτων (εκτός από JSON αρχεία)
                    signal_folders = []
                    for signal in signals:
                        source_folder = Path(signal['folder_path'])
                        target_folder = recipient_usb_path / source_folder.name
                        
                        # Χρήση helper method για αντιγραφή χωρίς JSON
                        self.copy_signal_folder_without_json(source_folder, target_folder)
                        
                        signal_folders.append(signal['folder_path'])
                    
                    # Αποθήκευση δεδομένων για backup και Excel
                    all_signals_data[recipient] = {
                        'signals': signals,
                        'folders': signal_folders
                    }
            
            # Δημιουργία backup
            if is_unofficial:
                backup_folder_name = usb_folder_name  # Use date-based name for unofficial
            else:
                backup_folder_name = f"Α.Φ. {file_number}"
            self.create_backup(all_signals_data, backup_folder_name)
            
            # Δημιουργία Excel και PDF για κάθε παραλήπτη ξεχωριστά (only in official mode)
            pdf_paths = []
            if not is_unofficial:
                for recipient in all_signals_data.keys():
                    recipient_signals = {recipient: all_signals_data[recipient]}
                    pdf_path = self.create_excel_and_pdf_for_recipient(
                        recipient_signals, file_number, username, backup_folder_name
                    )
                    if pdf_path:
                        pdf_paths.append(pdf_path)
                
                # Άνοιγμα όλων των PDF αρχείων για εκτύπωση (only in official mode)
                self.open_pdfs_for_printing(pdf_paths)
            
            # Διαγραφή σημάτων από DATA
            self.cleanup_data_folder(all_signals_data)
            
            # Δημιουργία αναλυτικών αποτελεσμάτων
            result_data = self.create_extraction_results(
                all_signals_data, file_number, username, usb_path, 
                None, pdf_paths, usb_extraction_path, is_unofficial, backup_folder_name
            )
            
            return True, result_data
            
        except Exception as e:
            print(f"Σφάλμα στην εξαγωγή USB: {e}")
            return False, None
    
    def create_backup(self, signals_data, backup_folder_name):
        """Δημιουργία backup των σημάτων"""
        try:
            for recipient, data in signals_data.items():
                self.signal_manager.move_to_backup(
                    recipient, data['folders'], backup_folder_name
                )
        except Exception as e:
            print(f"Σφάλμα στη δημιουργία backup: {e}")
    
    def create_excel_and_pdf_for_recipient(self, recipient_signals_data, file_number, username, backup_folder_name):
        """Δημιουργία Excel και PDF για έναν παραλήπτη"""
        import time
        
        try:
            recipient_name = list(recipient_signals_data.keys())[0]
            
            # 1. Δημιουργία temp folder
            temp_folder = self.path_manager.temp_folder
            temp_folder.mkdir(exist_ok=True)
            
            # 2. Αντιγραφή template στο temp folder
            template_path = self.templates_folder / "print.xlsx"
            if not template_path.exists():
                print("Δεν βρέθηκε το template print.xlsx")
                return None
            
            temp_excel_path = temp_folder / "print-copy.xlsx"
            # Διαγραφή προηγούμενου αρχείου αν υπάρχει
            if temp_excel_path.exists():
                temp_excel_path.unlink()
            
            shutil.copy2(template_path, temp_excel_path)
            
            # 3. Άνοιγμα και συμπλήρωση του Excel με Microsoft Excel
            import win32com.client
            
            excel_app = None
            workbook = None
            
            try:
                excel_app = win32com.client.Dispatch("Excel.Application")
                excel_app.Visible = False
                excel_app.DisplayAlerts = False
                excel_app.ScreenUpdating = False
                
                # Άνοιγμα του workbook
                workbook = excel_app.Workbooks.Open(str(temp_excel_path.absolute()))
                worksheet = workbook.ActiveSheet
                
                # Συμπλήρωση των βασικών πληροφοριών
                worksheet.Cells(2, 2).Value = self.config_manager.get_organization_identity() if self.config_manager else "ΚΕΠΙΚ 8 Μ/Π ΤΑΞ"  # B2 - Organization Identity
                worksheet.Cells(5, 3).Value = recipient_name  # C5
                worksheet.Cells(5, 4).Value = file_number     # D5
                worksheet.Cells(38, 2).Value = username       # B38
                
                # Συμπλήρωση σημάτων
                self.fill_excel_signals_com(worksheet, recipient_signals_data)
                
                # Υπολογισμός συνολικού αριθμού σημάτων για PDF pages
                total_signals = sum(len(data['signals']) for data in recipient_signals_data.values())
                
                # Αποθήκευση
                workbook.Save()
                
            finally:
                # Κλείσιμο του Excel
                if workbook is not None:
                    workbook.Close(SaveChanges=False)
                if excel_app is not None:
                    excel_app.Quit()
                # Περιμένω για να κλείσει το Excel πλήρως
                time.sleep(2)
            
            # 4. Εξαγωγή σε PDF
            pdf_path = self.export_excel_to_pdf_new(temp_excel_path, recipient_name, file_number, backup_folder_name, total_signals)
            
            # 5. Καθαρισμός temp folder
            if temp_excel_path.exists():
                temp_excel_path.unlink(missing_ok=True)
            
            return pdf_path
            
        except Exception as e:
            print(f"Σφάλμα στη δημιουργία Excel για {recipient_name}: {e}")
            
            # Καθαρισμός σε περίπτωση σφάλματος
            if 'workbook' in locals() and workbook is not None:
                workbook.Close(SaveChanges=False)
            if 'excel_app' in locals() and excel_app is not None:
                excel_app.Quit()
            if 'temp_excel_path' in locals() and temp_excel_path.exists():
                temp_excel_path.unlink(missing_ok=True)
            
            return None
    
    def fill_excel_signals_com(self, worksheet, signals_data):
        """Συμπλήρωση σημάτων στο Excel με COM"""
        # Περιοχές για ID και FM
        id_ranges = [
            (8, 32),   # C8-C32
            (48, 72),  # C48-C72
            (88, 112)  # C88-C112
        ]
        
        fm_ranges = [
            (8, 32),   # D8-D32
            (48, 72),  # D48-D72
            (88, 112)  # D88-D112
        ]
        
        current_row = 0
        current_range = 0
        
        for recipient, data in signals_data.items():
            for signal in data['signals']:
                if current_range < len(id_ranges):
                    id_start, id_end = id_ranges[current_range]
                    fm_start, fm_end = fm_ranges[current_range]
                    
                    row = id_start + current_row
                    
                    if row <= id_end:
                        # ID στη στήλη C (3)
                        worksheet.Cells(row, 3).Value = signal.get('id', '')
                        # FM στη στήλη D (4)
                        worksheet.Cells(row, 4).Value = signal.get('fm', '')
                        
                        current_row += 1
                    
                    # Αν γεμίσαμε την περιοχή, πάμε στην επόμενη
                    if row >= id_end:
                        current_range += 1
                        current_row = 0
    
    def fill_excel_signals(self, worksheet, signals_data):
        """Συμπλήρωση σημάτων στο Excel"""
        # Περιοχές για ID και FM
        id_ranges = [
            (8, 32),   # C8-C32
            (48, 72),  # C48-C72
            (88, 112)  # C88-C112
        ]
        
        fm_ranges = [
            (8, 32),   # D8-D32
            (48, 72),  # D48-D72
            (88, 112)  # D88-D112
        ]
        
        current_row = 0
        current_range = 0
        
        for recipient, data in signals_data.items():
            for signal in data['signals']:
                if current_range < len(id_ranges):
                    id_start, id_end = id_ranges[current_range]
                    fm_start, fm_end = fm_ranges[current_range]
                    
                    row = id_start + current_row
                    
                    if row <= id_end:
                        # ID στη στήλη C
                        worksheet[f'C{row}'] = signal.get('id', '')
                        # FM στη στήλη D
                        worksheet[f'D{row}'] = signal.get('fm', '')
                        
                        current_row += 1
                    
                    # Αν γεμίσαμε την περιοχή, πάμε στην επόμενη
                    if row >= id_end:
                        current_range += 1
                        current_row = 0
    
    def export_excel_to_pdf_new(self, excel_path, recipient_name, file_number, backup_folder_name, total_signals=0):
        """Νέα μέθοδος εξαγωγής Excel σε PDF με Microsoft Excel"""
        import time
        import re
        
        try:
            # Υπολογισμός αριθμού σελίδων βάσει αριθμού σημάτων
            # 0-25 signals: 1 page, 26-50: 2 pages, 51-75: 3 pages
            if total_signals <= 25:
                pages_to_export = 1
            elif total_signals <= 50:
                pages_to_export = 2
            else:
                pages_to_export = 3
            

            
            # Νέα δομή backup: BACK UP DATA/ΛΑΦ ΙΩΑΝΝΙΝΩΝ/Α.Φ. 8635/
            recipient_backup_path = self.backup_folder / recipient_name
            recipient_backup_path.mkdir(parents=True, exist_ok=True)
            
            file_number_backup_path = recipient_backup_path / backup_folder_name
            file_number_backup_path.mkdir(parents=True, exist_ok=True)
            
            pdf_filename = f"{recipient_name}-Α.Φ.{file_number}.pdf"
            pdf_path = file_number_backup_path / pdf_filename
            
            # Έλεγχος αν το αρχείο υπάρχει ήδη και διαγραφή του
            if pdf_path.exists():
                pdf_path.unlink(missing_ok=True)
            
            # Χρήση Microsoft Excel για εξαγωγή
            import win32com.client
            
            excel_app = None
            workbook = None
            
            try:
                excel_app = win32com.client.Dispatch("Excel.Application")
                excel_app.Visible = False
                excel_app.DisplayAlerts = False
                excel_app.ScreenUpdating = False
                
                # Άνοιγμα του workbook
                workbook = excel_app.Workbooks.Open(str(excel_path.absolute()))
                
                workbook.ExportAsFixedFormat(
                    Type=0,  # xlTypePDF
                    Filename=str(pdf_path.absolute()),
                    Quality=0,  # xlQualityStandard
                    IncludeDocProperties=True,
                    IgnorePrintAreas=False,
                    From=1,
                    To=pages_to_export,  # Dynamic page count based on signals
                    OpenAfterPublish=False
                )
                
            finally:
                # Εξασφάλιση κλεισίματος των αρχείων
                if workbook is not None:
                    workbook.Close(SaveChanges=False)
                if excel_app is not None:
                    excel_app.Quit()
                # Περιμένω για να κλείσει το Excel
                time.sleep(1)
            
            if pdf_path.exists() and pdf_path.stat().st_size > 0:
                return pdf_path
            else:
                return None
            
        except Exception as e:
            print(f"Σφάλμα στην εξαγωγή PDF για {recipient_name}: {e}")
            
            # Καθαρισμός σε περίπτωση σφάλματος
            if 'workbook' in locals() and workbook is not None:
                workbook.Close(SaveChanges=False)
            if 'excel_app' in locals() and excel_app is not None:
                excel_app.Quit()
            
            return None
    
    def open_pdfs_for_printing(self, pdf_paths):
        """Άνοιγμα όλων των PDF αρχείων για εκτύπωση"""
        try:
            for pdf_path in pdf_paths:
                if pdf_path and pdf_path.exists():
                    os.startfile(str(pdf_path))
        except Exception as e:
            print(f"Σφάλμα στο άνοιγμα PDF: {e}")
    
    def export_with_excel_com(self, excel_path, pdf_path):
        """Εξαγωγή σε PDF με COM (Windows Excel)"""
        try:
            import win32com.client
            
            excel_app = win32com.client.Dispatch("Excel.Application")
            excel_app.Visible = False
            excel_app.DisplayAlerts = False
            
            workbook = excel_app.Workbooks.Open(str(excel_path.absolute()))
            
            # Εξαγωγή σε PDF
            workbook.ExportAsFixedFormat(
                0,  # PDF format
                str(pdf_path.absolute()),
                0,  # Quality
                True,  # IncludeDocProperties
                True,  # IgnorePrintAreas
                1,  # From page
                1,  # To page
                False  # OpenAfterPublish
            )
            
            workbook.Close()
            excel_app.Quit()
            
            # Άνοιγμα του PDF
            if pdf_path.exists():
                os.startfile(str(pdf_path))
            
        except ImportError:

            raise
        except Exception as e:
            print(f"Σφάλμα COM Excel: {e}")
            raise
    
    def export_with_libreoffice(self, excel_path, pdf_path):
        """Εξαγωγή σε PDF με LibreOffice"""
        try:
            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', str(pdf_path.parent),
                str(excel_path)
            ]
            
            subprocess.run(cmd, check=True)
            
            # Μετονομασία του παραγόμενου PDF
            generated_pdf = pdf_path.parent / f"{excel_path.stem}.pdf"
            if generated_pdf.exists():
                generated_pdf.rename(pdf_path)
            
        except subprocess.CalledProcessError as e:
            print(f"Σφάλμα LibreOffice: {e}")
            raise
        except FileNotFoundError:

            raise
    
    def cleanup_data_folder(self, signals_data):
        """Καθαρισμός του φακέλου DATA"""
        try:
            for recipient, data in signals_data.items():
                self.signal_manager.delete_recipient_signals(recipient, data['folders'])
        except Exception as e:
            print(f"Σφάλμα στον καθαρισμό DATA: {e}")
    
    def create_extraction_results(self, signals_data, file_number, username, usb_path, excel_path, pdf_paths, extraction_path, is_unofficial=False, backup_folder_name=None):
        """Δημιουργία αναλυτικών αποτελεσμάτων εξαγωγής"""
        from datetime import datetime
        
        extracted_recipients = []
        
        for recipient, data in signals_data.items():
            signals = data['signals']
            
            extracted_recipients.append({
                'name': recipient,
                'signals': signals
            })
        
        return {
            'file_number': file_number,
            'username': username,
            'usb_path': str(usb_path),
            'excel_path': None,  # Δεν χρειαζόμαστε πια Excel path καθώς διαγράφεται
            'pdf_paths': [str(p) for p in pdf_paths if p] if pdf_paths else [],
            'extraction_path': str(extraction_path),
            'extraction_date': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'extracted_recipients': extracted_recipients,
            'backup_folder_name': backup_folder_name or f"Α.Φ. {file_number}",
            'is_unofficial': is_unofficial
        }
    
    def format_size(self, size_bytes):
        """Μορφοποίηση μεγέθους αρχείου"""
        if size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.1f} TB"
    
    def get_available_recipients(self):
        """Λήψη διαθέσιμων παραληπτών για εξαγωγή"""
        if not self.signal_manager:
            return []
        
        return self.signal_manager.get_all_recipients()
    
    def undo_extraction(self, result_data):
        """Αναίρεση εξαγωγής - επαναφορά σημάτων στη θέση τους"""
        try:
            file_number = result_data.get('file_number')
            backup_folder_name = result_data.get('backup_folder_name', f"Α.Φ. {file_number}")
            extraction_path = Path(result_data.get('extraction_path'))
            
            # Έλεγχος αν υπάρχουν τα αναγκαία δεδομένα
            if not result_data.get('extracted_recipients'):
                return False, "Δεν βρέθηκαν δεδομένα παραληπτών για αναίρεση"
            
            restored_count = 0
            
            # 1. Επαναφορά σημάτων από backup στο DATA (νέα δομή)
            for recipient_data in result_data.get('extracted_recipients', []):
                recipient_name = recipient_data['name']
                
                # Νέα δομή backup: BACK UP DATA/ΛΑΦ ΙΩΑΝΝΙΝΩΝ/Α.Φ. 8635/
                recipient_backup_path = self.backup_folder / recipient_name
                file_number_backup_path = recipient_backup_path / backup_folder_name
                
                if file_number_backup_path.exists():
                    # Δημιουργία φακέλου παραλήπτη στο DATA
                    data_recipient_path = self.data_folder / recipient_name
                    data_recipient_path.mkdir(parents=True, exist_ok=True)
                    
                    # Αντιγραφή όλων των φακέλων σημάτων πίσω στο DATA
                    for signal_folder in file_number_backup_path.iterdir():
                        if signal_folder.is_dir():
                            target_path = data_recipient_path / signal_folder.name
                            if not target_path.exists():
                                shutil.copytree(signal_folder, target_path)
                                restored_count += 1
                            else:
                                # Αν υπάρχει ήδη, απλά αγνοούμε
                                pass

                else:
                    print(f"Δεν βρέθηκε το backup για {recipient_name}: {file_number_backup_path}")
            
            # 2. Διαγραφή από backup (νέα δομή)
            for recipient_data in result_data.get('extracted_recipients', []):
                recipient_name = recipient_data['name']
                recipient_backup_path = self.backup_folder / recipient_name
                file_number_backup_path = recipient_backup_path / backup_folder_name
                
                if file_number_backup_path.exists():
                    shutil.rmtree(file_number_backup_path)
                    
                    # Αν ο φάκελος παραλήπτη είναι άδειος, διαγραφή του
                    if recipient_backup_path.exists() and not any(recipient_backup_path.iterdir()):
                        recipient_backup_path.rmdir()
            
            # 3. Διαγραφή από USB
            if extraction_path.exists():
                shutil.rmtree(extraction_path)
            
            # 4. Διαγραφή όλων των PDF αρχείων από backup folder (αν υπάρχουν)
            pdf_paths = result_data.get('pdf_paths', [])
            if pdf_paths:
                for pdf_path_str in pdf_paths:
                    pdf_path = Path(pdf_path_str)
                    if pdf_path.exists():
                        pdf_path.unlink(missing_ok=True)
            
            # Υποστήριξη παλιού format για συμβατότητα
            old_pdf_path = result_data.get('pdf_path')
            if old_pdf_path and Path(old_pdf_path).exists():
                Path(old_pdf_path).unlink(missing_ok=True)
            
            # Τα Excel είναι προσωρινά αρχεία, δεν χρειάζεται διαγραφή
            
            success_message = f"Επαναφέρθηκαν {restored_count} φάκελοι σημάτων επιτυχώς"
            return True, success_message
            
        except Exception as e:
            return False, f"Σφάλμα στην αναίρεση εξαγωγής: {e}"
