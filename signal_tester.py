#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Signal Tester for autoPyrseia
Δημιουργός: Σωτήριος Μπαλατσιάς

Βοηθητικό εργαλείο για τεστάρισμα του autoPyrseia με σήματα από φάκελο.
Διαβάζει σήματα από έναν φάκελο και τα αντιγράφει στο downloads για δοκιμή.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
from pathlib import Path
import json
from datetime import datetime
import re
import random  # Add this import

# Try to import PDF processor for theme extraction
try:
    from app.services.pdf_processor import PDFProcessor
    PDF_PROCESSOR_AVAILABLE = True
except ImportError:
    PDF_PROCESSOR_AVAILABLE = False

class SignalTester:
    def __init__(self, root):
        self.root = root
        self.root.title("autoPyrseia Signal Tester")
        self.root.geometry("800x600")
        
        # Configuration file path
        self.config_file = Path("signal_tester_config.json")
        
        # Paths
        self.source_path = ""
        self.downloads_path = ""
        
        # Signal data
        self.signals = []
        self.current_signal_index = 0
        
        # PDF processor for theme extraction
        self.pdf_processor = None
        if PDF_PROCESSOR_AVAILABLE:
            try:
                self.pdf_processor = PDFProcessor()
            except Exception as e:
                print(f"Could not initialize PDF processor: {e}")
        
        # Load saved configuration
        self.load_config()
        
        self.setup_ui()
        
        # Save config when window is closed
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        """Δημιουργία του UI"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="autoPyrseia Signal Tester", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Source folder selection
        ttk.Label(main_frame, text="Φάκελος Σημάτων:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.source_var = tk.StringVar(value=self.source_path)
        source_entry = ttk.Entry(main_frame, textvariable=self.source_var, width=50)
        source_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        ttk.Button(main_frame, text="Επιλογή", 
                  command=self.select_source_folder).grid(row=1, column=2, pady=5)
        
        # Downloads folder selection
        ttk.Label(main_frame, text="Φάκελος Downloads:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.downloads_var = tk.StringVar(value=self.downloads_path)
        downloads_entry = ttk.Entry(main_frame, textvariable=self.downloads_var, width=50)
        downloads_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        ttk.Button(main_frame, text="Επιλογή", 
                  command=self.select_downloads_folder).grid(row=2, column=2, pady=5)
        
        # Scan button
        ttk.Button(main_frame, text="Σάρωση Σημάτων", 
                  command=self.scan_signals).grid(row=3, column=0, columnspan=3, pady=20)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=4, column=0, columnspan=3, 
                                                           sticky=(tk.W, tk.E), pady=10)
        
        # Signal info frame
        signal_frame = ttk.LabelFrame(main_frame, text="Πληροφορίες Σήματος", padding="10")
        signal_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        signal_frame.columnconfigure(1, weight=1)
        
        # Signal counter
        self.counter_var = tk.StringVar(value="0 / 0")
        ttk.Label(signal_frame, text="Σήμα:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(signal_frame, textvariable=self.counter_var).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Signal folder name
        ttk.Label(signal_frame, text="Φάκελος:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.folder_var = tk.StringVar()
        ttk.Label(signal_frame, textvariable=self.folder_var, 
                 foreground="blue").grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Signal PDF name
        ttk.Label(signal_frame, text="Σήμα PDF:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.signal_name_var = tk.StringVar()
        ttk.Label(signal_frame, textvariable=self.signal_name_var, 
                 foreground="darkgreen").grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Attachments (moved up to row 3, removing theme section)
        ttk.Label(signal_frame, text="Συνημμένα:").grid(row=3, column=0, sticky=(tk.W, tk.N), pady=5)
        
        # Attachments listbox with scrollbar
        attachments_frame = ttk.Frame(signal_frame)
        attachments_frame.grid(row=3, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        attachments_frame.columnconfigure(0, weight=1)
        
        self.attachments_listbox = tk.Listbox(attachments_frame, height=4)
        self.attachments_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(attachments_frame, orient="vertical", 
                                 command=self.attachments_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.attachments_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Status (moved to row 4)
        ttk.Label(signal_frame, text="Κατάσταση:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.status_var = tk.StringVar(value="Μη επεξεργασμένο")
        self.status_label = ttk.Label(signal_frame, textvariable=self.status_var)
        self.status_label.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Configure signal_frame grid weights (changed to row 3)
        signal_frame.rowconfigure(3, weight=1)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        self.prev_button = ttk.Button(button_frame, text="← Προηγούμενο", 
                                     command=self.prev_signal, state='disabled')
        self.prev_button.grid(row=0, column=0, padx=5)
        
        self.next_button = ttk.Button(button_frame, text="Επόμενο →", 
                                     command=self.next_signal, state='disabled')
        self.next_button.grid(row=0, column=1, padx=5)
        
        self.send_button = ttk.Button(button_frame, text="Send", 
                                     command=self.send_signal, state='disabled')
        self.send_button.grid(row=0, column=2, padx=10)
        
        self.reset_button = ttk.Button(button_frame, text="Reset Status", 
                                      command=self.reset_signal_status, state='disabled')
        self.reset_button.grid(row=0, column=3, padx=10)
        
        # Configure main_frame grid weights
        main_frame.rowconfigure(5, weight=1)
        
    def load_config(self):
        """Φόρτωση αποθηκευμένης διαμόρφωσης"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.source_path = config.get('source_path', '')
                    self.downloads_path = config.get('downloads_path', '')
                    
                    # Έλεγχος αν οι φάκελοι υπάρχουν ακόμη
                    if self.source_path and not Path(self.source_path).exists():
                        self.source_path = ''
                    if self.downloads_path and not Path(self.downloads_path).exists():
                        self.downloads_path = ''
        except Exception as e:
            print(f"Σφάλμα φόρτωσης διαμόρφωσης: {e}")
            self.source_path = ''
            self.downloads_path = ''
    
    def save_config(self):
        """Αποθήκευση διαμόρφωσης"""
        try:
            config = {
                'source_path': self.source_path,
                'downloads_path': self.downloads_path
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Σφάλμα αποθήκευσης διαμόρφωσης: {e}")
        
    def select_source_folder(self):
        """Επιλογή φακέλου σημάτων"""
        # Use saved path as initial directory if available
        initial_dir = self.source_path if self.source_path and Path(self.source_path).exists() else None
        folder = filedialog.askdirectory(title="Επιλέξτε φάκελο με σήματα", initialdir=initial_dir)
        if folder:
            self.source_var.set(folder)
            self.source_path = folder
            self.save_config()
            
    def select_downloads_folder(self):
        """Επιλογή φακέλου downloads"""
        # Use saved path as initial directory if available
        initial_dir = self.downloads_path if self.downloads_path and Path(self.downloads_path).exists() else None
        folder = filedialog.askdirectory(title="Επιλέξτε φάκελο downloads", initialdir=initial_dir)
        if folder:
            self.downloads_var.set(folder)
            self.downloads_path = folder
            self.save_config()
            
    def scan_signals(self):
        """Σάρωση για σήματα στον φάκελο"""
        if not self.source_path or not self.downloads_path:
            self.status_var.set("Σφάλμα: Επιλέξτε και τους δύο φακέλους")
            self.status_label.configure(foreground="red")
            return
            
        self.signals = []
        self.scan_directory(Path(self.source_path))
        
        if not self.signals:
            self.status_var.set("Δεν βρέθηκαν σήματα στον φάκελο")
            self.status_label.configure(foreground="orange")
            return
        
        # Randomize the order of signals
        random.shuffle(self.signals)
            
        self.current_signal_index = 0
        self.update_display()
        self.update_buttons()
        
        # Update status to show scan results
        self.status_var.set(f"Βρέθηκαν {len(self.signals)} σήματα (τυχαία σειρά)")
        self.status_label.configure(foreground="green")
        
    def scan_directory(self, directory):
        """Αναδρομική σάρωση φακέλου για σήματα"""
        try:
            for item in directory.iterdir():
                if item.is_dir():
                    # Έλεγχος αν ο φάκελος περιέχει σήμα
                    signal_data = self.analyze_signal_folder(item)
                    if signal_data:
                        self.signals.append(signal_data)
                    
                    # Αναδρομική σάρωση υποφακέλων
                    self.scan_directory(item)
                    
        except PermissionError:
            pass  # Αγνοούμε φακέλους χωρίς δικαιώματα
            
    def analyze_signal_folder(self, folder_path):
        """Ανάλυση φακέλου για εντοπισμό σήματος"""
        pdf_files = list(folder_path.glob("*.pdf"))
        
        if not pdf_files:
            return None
            
        # Βρίσκουμε το κύριο σήμα PDF
        signal_pdf = self.identify_signal_pdf(pdf_files)
        
        if not signal_pdf:
            return None
            
        # Βρίσκουμε τα συνημμένα αρχεία
        all_files = [f for f in folder_path.iterdir() if f.is_file()]
        
        # Φιλτράρισμα συνημμένων: αποκλείουμε το κύριο PDF, JSON info files, και txt markers
        attachments = [f for f in all_files 
                      if f != signal_pdf 
                      and not f.name.endswith('.txt')  # marker files
                      and not f.name.endswith('_info.json')  # JSON info files
                      and not f.name == 'sent_to_downloads.txt']
        
        # Έλεγχος αν έχει ήδη σταλεί
        sent_marker = folder_path / "sent_to_downloads.txt"
        is_sent = sent_marker.exists()
        
        return {
            'folder_path': folder_path,
            'folder_name': folder_path.name,
            'signal_pdf': signal_pdf,
            'attachments': attachments,
            'is_sent': is_sent
        }
        
    def identify_signal_pdf(self, pdf_files):
        """Εντοπισμός του κύριου σήματος PDF"""
        if len(pdf_files) == 1:
            return pdf_files[0]
            
        # Προτεραιότητα 1: Σήματα με το τυπικό pattern ID σήματος
        # Pattern: [R|P|O] DDHHMMZ [Month] YY (π.χ. "R 250417Z JUL 25.pdf")
        signal_id_pattern = r'^[RPO]\s+\d{6}Z\s+[A-Z]{3}\s+\d{2}\.pdf$'
        
        for pdf in pdf_files:
            if re.match(signal_id_pattern, pdf.name, re.IGNORECASE):
                return pdf
        
        # Προτεραιότητα 2: Αρχεία που ταιριάζουν με το όνομα του φακέλου
        # (π.χ. φάκελος "R 250417Z JUL 25" και αρχείο "R 250417Z JUL 25.pdf")
        folder_name = pdf_files[0].parent.name
        for pdf in pdf_files:
            if pdf.stem == folder_name:  # stem είναι το όνομα χωρίς την επέκταση
                return pdf
        
        # Προτεραιότητα 3: Αρχεία με συγκεκριμένα ονόματα
        priority_patterns = [
            r'signal', r'σήμα', r'message', r'μήνυμα',
            r'pyrseia', r'πυρσεία'
        ]
        
        for pattern in priority_patterns:
            for pdf in pdf_files:
                if re.search(pattern, pdf.name, re.IGNORECASE):
                    return pdf
        
        # Προτεραιότητα 4: Αποκλεισμός UUID αρχείων (πιθανά συνημμένα)
        # UUID pattern: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.pdf
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.pdf$'
        non_uuid_pdfs = [pdf for pdf in pdf_files if not re.match(uuid_pattern, pdf.name, re.IGNORECASE)]
        
        if non_uuid_pdfs:
            # Από τα μη-UUID αρχεία, επιλέγουμε το μεγαλύτερο
            return max(non_uuid_pdfs, key=lambda x: x.stat().st_size)
                    
        # Τελευταία επιλογή: το μεγαλύτερο αρχείο
        return max(pdf_files, key=lambda x: x.stat().st_size)
    
    def copy_theme(self, event=None):
        """Copy theme to clipboard when clicked"""
        if not self.signals:
            return
        
        signal = self.signals[self.current_signal_index]
        theme = signal.get('theme', '')
        
        if theme and theme != "Δεν είναι διαθέσιμος ο PDF processor" and not theme.startswith("Σφάλμα"):
            # Copy to clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(theme)
            self.root.update()  # Required for clipboard to work
            
            # Show feedback
            original_color = self.theme_label.cget('foreground')
            self.theme_label.configure(foreground='green')
            self.root.after(1000, lambda: self.theme_label.configure(foreground=original_color))
            
            # Update status temporarily
            original_status = self.status_var.get()
            original_status_color = self.status_label.cget('foreground')
            self.status_var.set("Θέμα αντιγράφηκε στο clipboard!")
            self.status_label.configure(foreground='green')
            self.root.after(2000, lambda: (
                self.status_var.set(original_status),
                self.status_label.configure(foreground=original_status_color)
            ))
        else:
            # Show error feedback
            self.status_var.set("Δεν είναι δυνατή η αντιγραφή του θέματος")
            self.status_label.configure(foreground="red")
            self.root.after(3000, lambda: self.update_display())
        
    def update_display(self):
        """Ενημέρωση της οθόνης με τα δεδομένα του τρέχοντος σήματος"""
        if not self.signals:
            return
            
        signal = self.signals[self.current_signal_index]
        
        # Counter
        self.counter_var.set(f"{self.current_signal_index + 1} / {len(self.signals)}")
        
        # Folder name
        self.folder_var.set(signal['folder_name'])
        
        # Signal PDF name
        self.signal_name_var.set(signal['signal_pdf'].name)
        
        # Attachments
        self.attachments_listbox.delete(0, tk.END)
        for attachment in signal['attachments']:
            self.attachments_listbox.insert(tk.END, attachment.name)
            
        # Status
        if signal['is_sent']:
            self.status_var.set("Έχει σταλεί")
            self.status_label.configure(foreground="red")
        else:
            self.status_var.set("Μη επεξεργασμένο")
            self.status_label.configure(foreground="green")
            
    def update_buttons(self):
        """Ενημέρωση κατάστασης κουμπιών"""
        if not self.signals:
            self.prev_button.configure(state='disabled')
            self.next_button.configure(state='disabled')
            self.send_button.configure(state='disabled')
            self.reset_button.configure(state='disabled')
            return
            
        # Previous button
        if self.current_signal_index > 0:
            self.prev_button.configure(state='normal')
        else:
            self.prev_button.configure(state='disabled')
            
        # Next button
        if self.current_signal_index < len(self.signals) - 1:
            self.next_button.configure(state='normal')
        else:
            self.next_button.configure(state='disabled')
            
        # Send button - always enabled when signals are available
        self.send_button.configure(state='normal')
        
        # Reset button - only enabled for sent signals
        signal = self.signals[self.current_signal_index]
        if signal['is_sent']:
            self.reset_button.configure(state='normal')
        else:
            self.reset_button.configure(state='disabled')
            
    def prev_signal(self):
        """Μετάβαση στο προηγούμενο σήμα"""
        if self.current_signal_index > 0:
            self.current_signal_index -= 1
            self.update_display()
            self.update_buttons()
            
    def next_signal(self):
        """Μετάβαση στο επόμενο σήμα"""
        if self.current_signal_index < len(self.signals) - 1:
            self.current_signal_index += 1
            self.update_display()
            self.update_buttons()
            
    def send_signal(self):
        """Αποστολή/επαναποστολή του τρέχοντος σήματος στο downloads"""
        if not self.signals:
            return
            
        signal = self.signals[self.current_signal_index]
        is_resend = signal['is_sent']
            
        try:
            downloads_path = Path(self.downloads_path)
            
            # Καθαρισμός downloads folder πρώτα (για resend ή για καθαρό περιβάλλον)
            for existing_file in downloads_path.glob("*"):
                if existing_file.is_file():
                    existing_file.unlink()
            
            # Αντιγραφή του PDF σήματος ως pyrseia_server.pdf
            signal_dest = downloads_path / "pyrseia_server.pdf"
            shutil.copy2(signal['signal_pdf'], signal_dest)
            
            # Αντιγραφή των συνημμένων
            for attachment in signal['attachments']:
                attachment_dest = downloads_path / attachment.name
                shutil.copy2(attachment, attachment_dest)
                
            # Ενημέρωση του marker file
            sent_marker = signal['folder_path'] / "sent_to_downloads.txt"
            
            if is_resend:
                # Append για resend
                with open(sent_marker, 'a', encoding='utf-8') as f:
                    f.write(f"\n--- ΕΠΑΝΑΠΟΣΤΟΛΗ ---\n")
                    f.write(f"Επαναστάλθηκε στις {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Αρχικό PDF: {signal['signal_pdf'].name}\n")
                    f.write(f"Συνημμένα: {len(signal['attachments'])}\n")
                    for attachment in signal['attachments']:
                        f.write(f"  - {attachment.name}\n")
            else:
                # Write για πρώτη φορά
                with open(sent_marker, 'w', encoding='utf-8') as f:
                    f.write(f"Σήμα στάλθηκε στο downloads στις {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Αρχικό PDF: {signal['signal_pdf'].name}\n")
                    f.write(f"Συνημμένα: {len(signal['attachments'])}\n")
                    for attachment in signal['attachments']:
                        f.write(f"  - {attachment.name}\n")
                    
            # Ενημέρωση της κατάστασης
            signal['is_sent'] = True
            self.update_display()
            self.update_buttons()
            
            # Update status
            action = "επαναστάλθηκε" if is_resend else "στάλθηκε"
            color = "blue" if is_resend else "green"
            self.status_var.set(f"Σήμα {action}: PDF + {len(signal['attachments'])} συνημμένα")
            self.status_label.configure(foreground=color)
                              
        except Exception as e:
            action = "επαναποστολής" if is_resend else "αποστολής"
            self.status_var.set(f"Σφάλμα {action}: {str(e)}")
            self.status_label.configure(foreground="red")

    def reset_signal_status(self):
        """Επαναφορά κατάστασης σήματος σε 'μη επεξεργασμένο'"""
        if not self.signals:
            return
            
        signal = self.signals[self.current_signal_index]
        
        if not signal['is_sent']:
            self.status_var.set("Το σήμα δεν έχει σταλεί")
            self.status_label.configure(foreground="orange")
            return
            
        try:
            # Διαγραφή του marker file
            sent_marker = signal['folder_path'] / "sent_to_downloads.txt"
            if sent_marker.exists():
                sent_marker.unlink()
            
            # Ενημέρωση της κατάστασης
            signal['is_sent'] = False
            self.update_display()
            self.update_buttons()
            
            # Update status
            self.status_var.set("Κατάσταση επαναφέρθηκε σε 'μη επεξεργασμένο'")
            self.status_label.configure(foreground="purple")
                              
        except Exception as e:
            self.status_var.set(f"Σφάλμα επαναφοράς: {str(e)}")
            self.status_label.configure(foreground="red")

    def on_closing(self):
        """Χειρισμός κλεισίματος παραθύρου"""
        self.save_config()
        self.root.destroy()

def main():
    """Κύρια συνάρτηση"""
    root = tk.Tk()
    app = SignalTester(root)
    root.mainloop()

if __name__ == "__main__":
    main()
