#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Missing Attachments Dialog for autoPyrseia
"""

import tkinter as tk
from tkinter import ttk, messagebox


class MissingAttachmentsDialog:
    """Dialog για ενημέρωση χρήστη για συνημμένα που λείπουν"""
    
    def __init__(self, parent, missing_attachments, total_attachments):
        self.result = None  # Will be True if user wants to continue, False if canceled
        self.missing_attachments = missing_attachments
        self.total_attachments = total_attachments
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Προειδοποίηση - Συνημμένα Αρχεία")
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Setup UI first
        self.setup_ui()
        
        # Update and calculate proper size after UI is created
        self.dialog.update_idletasks()
        
        # Calculate dialog height based on content
        base_height = 400  # Increased base height for all dialog elements including buttons
        files_height = min(len(missing_attachments) * 22, 176)  # Max 8 lines * 22px per line
        dialog_height = base_height + files_height
        
        self.dialog.geometry(f"600x{dialog_height}")
        self.dialog.resizable(False, True)  # Allow vertical resize only
        
        # Center the dialog after sizing
        self.center_dialog()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def center_dialog(self):
        """Κεντράρισμα του dialog στην οθόνη"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Δημιουργία του UI"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20 20 20 25")  # Extra bottom padding
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Warning icon and title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Warning symbol
        warning_label = ttk.Label(title_frame, text="⚠️", font=("Arial", 24))
        warning_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Title
        title_label = ttk.Label(title_frame, 
                              text="Προειδοποίηση - Συνημμένα Αρχεία Λείπουν", 
                              font=("Arial", 14, "bold"))
        title_label.pack(side=tk.LEFT, anchor=tk.W)
        
        # Information text
        info_text = f"""Βρέθηκαν {len(self.missing_attachments)} από {self.total_attachments} συνημμένα αρχεία που λείπουν από τον φάκελο downloads.

Τα παρακάτω αρχεία δεν μπορούν να βρεθούν:"""
        
        info_label = ttk.Label(main_frame, text=info_text, 
                             font=("Arial", 11), wraplength=550)
        info_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Missing files list
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Scrollable listbox for missing files
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(fill=tk.X)
        
        # Calculate appropriate height based on number of files (min 3, max 8 lines visible)
        listbox_height = max(3, min(len(self.missing_attachments), 8))
        
        # Listbox with scrollbar
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(listbox_frame, 
                                 yscrollcommand=scrollbar.set,
                                 font=("Consolas", 9),
                                 selectmode=tk.NONE,
                                 height=listbox_height,
                                 activestyle='none')
        self.listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # Add missing files to listbox
        for i, filename in enumerate(self.missing_attachments, 1):
            self.listbox.insert(tk.END, f"{i}. {filename}")
        
        # Options text
        options_text = """Επιλογές:
• Συνέχεια: Η επεξεργασία θα συνεχιστεί χωρίς τα συνημμένα αρχεία
• Ακύρωση: Η επεξεργασία θα διακοπεί για να προσθέσετε τα αρχεία"""
        
        options_label = ttk.Label(main_frame, text=options_text, 
                                font=("Arial", 10), wraplength=550)
        options_label.pack(anchor=tk.W, pady=(15, 20))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(20, 15))  # Increased padding to ensure visibility
        
        # Continue button (primary action)
        continue_button = ttk.Button(buttons_frame, 
                                   text="Συνέχεια χωρίς συνημμένα", 
                                   command=self.continue_processing,
                                   style="Accent.TButton")
        continue_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Cancel button
        cancel_button = ttk.Button(buttons_frame, 
                                 text="Ακύρωση", 
                                 command=self.cancel_processing)
        cancel_button.pack(side=tk.RIGHT)
        
        # Bind Escape key to cancel
        self.dialog.bind('<Escape>', lambda e: self.cancel_processing())
        
        # Bind Enter key to continue
        self.dialog.bind('<Return>', lambda e: self.continue_processing())
        
        # Set focus to continue button
        continue_button.focus_set()
    
    def continue_processing(self):
        """Συνέχεια επεξεργασίας χωρίς τα συνημμένα"""
        self.result = True
        self.dialog.destroy()
    
    def cancel_processing(self):
        """Ακύρωση επεξεργασίας"""
        self.result = False
        self.dialog.destroy()


# Test the dialog (for development purposes)
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    # Test data
    missing_files = [
        "very_long_document_name_that_exceeds_normal_limits.pdf",
        "report_2025.xlsx",
        "image_attachment.png"
    ]
    
    dialog = MissingAttachmentsDialog(root, missing_files, 5)
    print(f"User choice: {'Continue' if dialog.result else 'Cancel'}")
    
    root.destroy()
