#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manual Input Dialog for autoPyrseia
Handles manual signal data entry when PDF cannot be processed automatically
"""

import tkinter as tk
from tkinter import messagebox
from app.services.recipients_manager import RecipientsManager


class ManualInputDialog:
    """Dialog για χειροκίνητη εισαγωγή ID και FM"""
    def __init__(self, parent, attachments):
        self.result = None
        self.attachments = attachments
        self.recipients_manager = RecipientsManager()
        self.recipient_vars = []  # List to store checkbox variables
        self.attachment_vars = []  # List to store attachment checkbox variables
        
        # Δημιουργία dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Χειροκίνητη Εισαγωγή Στοιχείων")
        self.dialog.geometry("900x600")  # Increased width for three-column layout, reduced height since components are side by side
        self.dialog.resizable(False, False)
        self.dialog.grab_set()  # Modal dialog
        
        # Center the dialog
        self.dialog.transient(parent)
        self.center_window()
        
        self.create_widgets()
        
        # Focus on ID entry
        self.id_entry.focus()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def center_window(self):
        """Κεντράρισμα του dialog"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"900x600+{x}+{y}")
    
    def create_widgets(self):
        """Δημιουργία widgets του dialog"""
        # Main frame
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="Το PDF δεν περιέχει αναγνώσιμο κείμενο", 
                              font=('Arial', 12, 'bold'), 
                              fg='red')
        title_label.pack(pady=(0, 10))
        
        subtitle_label = tk.Label(main_frame, 
                                 text="Παρακαλώ εισάγετε τα στοιχεία του σήματος χειροκίνητα", 
                                 font=('Arial', 10))
        subtitle_label.pack(pady=(0, 15))
        
        # Create three-column layout: left for ID/FM/Theme, middle for recipients, right for attachments
        columns_frame = tk.Frame(main_frame)
        columns_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Left column - Signal Information (ID, FM, Theme)
        left_column = tk.Frame(columns_frame)
        left_column.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # ID Section
        id_frame = tk.Frame(left_column)
        id_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(id_frame, text="Αναγνωριστικό Σήματος:", font=('Arial', 10, 'bold')).pack(anchor='w')
        self.id_entry = tk.Entry(id_frame, font=('Arial', 10), width=25)
        self.id_entry.pack(fill='x', pady=(5, 0))
        
        # FM Section
        fm_frame = tk.Frame(left_column)
        fm_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(fm_frame, text="FM (Αποστολέας):", font=('Arial', 10, 'bold')).pack(anchor='w')
        self.fm_entry = tk.Entry(fm_frame, font=('Arial', 10), width=25)
        self.fm_entry.pack(fill='x', pady=(5, 0))
        
        # Theme Section (Optional)
        theme_frame = tk.Frame(left_column)
        theme_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(theme_frame, text="Θέμα (Προαιρετικό):", font=('Arial', 10)).pack(anchor='w')
        self.theme_entry = tk.Entry(theme_frame, font=('Arial', 10), width=25)
        self.theme_entry.pack(fill='x', pady=(5, 0))
        
        # Middle column - Recipients
        middle_column = tk.Frame(columns_frame)
        middle_column.pack(side='left', fill='both', expand=True, padx=(5, 5))
        
        # Recipients selection label
        recipients_label = tk.Label(middle_column, 
                                  text="Επιλογή Παραληπτών:", 
                                  font=('Arial', 10, 'bold'))
        recipients_label.pack(anchor='w', pady=(0, 5))
        
        # Recipients selection frame with scrollbar
        recipients_selection_frame = tk.Frame(middle_column)
        recipients_selection_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Create canvas and scrollbar for recipients
        self.recipients_canvas = tk.Canvas(recipients_selection_frame, height=200, width=250, bg='white', relief='sunken', bd=1)
        recipients_scrollbar = tk.Scrollbar(recipients_selection_frame, orient=tk.VERTICAL, command=self.recipients_canvas.yview)
        self.recipients_scrollable_frame = tk.Frame(self.recipients_canvas)
        
        self.recipients_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.recipients_canvas.configure(scrollregion=self.recipients_canvas.bbox("all"))
        )
        
        self.recipients_canvas.create_window((0, 0), window=self.recipients_scrollable_frame, anchor="nw")
        self.recipients_canvas.configure(yscrollcommand=recipients_scrollbar.set)
        
        self.recipients_canvas.pack(side='left', fill='y')
        recipients_scrollbar.pack(side='right', fill='y')
        
        # Load and display recipients
        self.load_recipients()
        
        # Select All / Deselect All buttons for recipients
        select_buttons_frame = tk.Frame(middle_column)
        select_buttons_frame.pack(fill='x', pady=(5, 0))
        
        tk.Button(select_buttons_frame, text="Επιλογή Όλων", 
                 command=self.select_all_recipients, font=('Arial', 8), 
                 bg='#3498db', fg='white').pack(side='left', padx=(0, 5))
        
        tk.Button(select_buttons_frame, text="Αποεπιλογή Όλων", 
                 command=self.deselect_all_recipients, font=('Arial', 8), 
                 bg='#95a5a6', fg='white').pack(side='left')
        
        # Right column - Attachments
        right_column = tk.Frame(columns_frame)
        right_column.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Attachments Section
        att_label = tk.Label(right_column, 
                            text=f"Επιλογή Συνημμένων ({len(self.attachments)}):", 
                            font=('Arial', 10, 'bold'))
        att_label.pack(anchor='w', pady=(0, 5))
        
        # Attachments selection frame with scrollbar
        att_frame = tk.Frame(right_column)
        att_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Create canvas and scrollbar for attachments
        self.attachments_canvas = tk.Canvas(att_frame, height=200, bg='white', relief='sunken', bd=1)
        att_scrollbar = tk.Scrollbar(att_frame, orient=tk.VERTICAL, command=self.attachments_canvas.yview)
        self.attachments_scrollable_frame = tk.Frame(self.attachments_canvas)
        
        self.attachments_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.attachments_canvas.configure(scrollregion=self.attachments_canvas.bbox("all"))
        )
        
        self.attachments_canvas.create_window((0, 0), window=self.attachments_scrollable_frame, anchor="nw")
        self.attachments_canvas.configure(yscrollcommand=att_scrollbar.set)
        
        self.attachments_canvas.pack(side='left', fill='both', expand=True)
        att_scrollbar.pack(side='right', fill='y')
        
        # Load and display attachments
        self.load_attachments()
        
        # Attachment Select All / Deselect All buttons
        att_select_buttons_frame = tk.Frame(right_column)
        att_select_buttons_frame.pack(fill='x', pady=(5, 0))
        
        tk.Button(att_select_buttons_frame, text="Επιλογή Όλων", 
                 command=self.select_all_attachments, font=('Arial', 8), 
                 bg='#f39c12', fg='white').pack(side='left', padx=(0, 5))
        
        tk.Button(att_select_buttons_frame, text="Αποεπιλογή Όλων", 
                 command=self.deselect_all_attachments, font=('Arial', 8), 
                 bg='#95a5a6', fg='white').pack(side='left')
        
        # Buttons - Fixed at bottom right with proper spacing
        button_frame = tk.Frame(main_frame)
        button_frame.pack(side='bottom', fill='x', pady=(10, 0))
        
        # Add some space before buttons
        spacer = tk.Frame(button_frame, height=10)
        spacer.pack(fill='x')
        
        # Button container for right alignment
        button_container = tk.Frame(button_frame)
        button_container.pack(side='right')
        
        tk.Button(button_container, text="OK", command=self.ok, 
                 bg='#27ae60', fg='white', font=('Arial', 10), width=8).pack(side='right', padx=(0, 5))
        
        # Bind Enter key to OK
        self.dialog.bind('<Return>', lambda e: self.ok())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
        # Set up tab order for entries
        self.id_entry.bind('<Tab>', lambda e: self.fm_entry.focus_set())
        self.fm_entry.bind('<Tab>', lambda e: self.theme_entry.focus_set())
        self.theme_entry.bind('<Tab>', lambda e: self.id_entry.focus_set())  # Cycle back to ID
    
    def load_recipients(self):
        """Φόρτωση και εμφάνιση των παραληπτών με checkboxes"""
        recipients = self.recipients_manager.get_all_recipients()
        self.recipient_vars = []
        
        # Clear existing widgets
        for widget in self.recipients_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Create checkboxes for each recipient
        for i, recipient in enumerate(recipients):
            var = tk.BooleanVar()
            self.recipient_vars.append({'recipient': recipient, 'var': var})
            
            checkbox = tk.Checkbutton(
                self.recipients_scrollable_frame,
                text=recipient,
                variable=var,
                font=('Arial', 9),
                anchor='w'
            )
            checkbox.pack(fill='x', padx=5, pady=1)
    
    def select_all_recipients(self):
        """Επιλογή όλων των παραληπτών"""
        for item in self.recipient_vars:
            item['var'].set(True)
    
    def deselect_all_recipients(self):
        """Αποεπιλογή όλων των παραληπτών"""
        for item in self.recipient_vars:
            item['var'].set(False)
    
    def load_attachments(self):
        """Φόρτωση και εμφάνιση των συνημμένων με checkboxes"""
        self.attachment_vars = []
        
        # Clear existing widgets
        for widget in self.attachments_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Create checkboxes for each attachment
        for i, attachment in enumerate(self.attachments):
            var = tk.BooleanVar()
            var.set(True)  # All attachments selected by default
            self.attachment_vars.append({'attachment': attachment, 'var': var})
            
            checkbox = tk.Checkbutton(
                self.attachments_scrollable_frame,
                text=attachment,
                variable=var,
                font=('Arial', 9),
                anchor='w'
            )
            checkbox.pack(fill='x', padx=5, pady=1)
    
    def select_all_attachments(self):
        """Επιλογή όλων των συνημμένων"""
        for item in self.attachment_vars:
            item['var'].set(True)
    
    def deselect_all_attachments(self):
        """Αποεπιλογή όλων των συνημμένων"""
        for item in self.attachment_vars:
            item['var'].set(False)
    
    def get_selected_attachments(self):
        """Λήψη των επιλεγμένων συνημμένων"""
        selected = []
        for item in self.attachment_vars:
            if item['var'].get():
                selected.append(item['attachment'])
        return selected
    
    def get_selected_recipients(self):
        """Λήψη των επιλεγμένων παραληπτών"""
        selected = []
        for item in self.recipient_vars:
            if item['var'].get():
                selected.append(item['recipient'])
        return selected
    
    def ok(self):
        """OK button callback"""
        signal_id = self.id_entry.get().strip()
        fm = self.fm_entry.get().strip()
        theme = self.theme_entry.get().strip()  # Optional field
        
        if not signal_id:
            messagebox.showerror("Σφάλμα", "Παρακαλώ εισάγετε το Αναγνωριστικό Σήματος")
            self.id_entry.focus()
            return
        
        if not fm:
            messagebox.showerror("Σφάλμα", "Παρακαλώ εισάγετε το FM")
            self.fm_entry.focus()
            return
        
        # Get selected recipients
        selected_recipients = self.get_selected_recipients()
        
        if not selected_recipients:
            messagebox.showerror("Σφάλμα", 
                               "Παρακαλώ επιλέξτε τουλάχιστον έναν παραλήπτη.\n"
                               "Η επεξεργασία σήματος απαιτεί την επιλογή παραληπτών.")
            return
        
        # Get selected attachments
        selected_attachments = self.get_selected_attachments()
        
        self.result = {
            'id': signal_id,
            'fm': fm,
            'theme': theme if theme else None,  # Include theme if provided
            'recipients': selected_recipients,
            'attachments': selected_attachments
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel button callback"""
        self.result = None
        self.dialog.destroy()
