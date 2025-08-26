#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recipients Management Tab for autoPyrseia
"""

import tkinter as tk
from tkinter import ttk, messagebox


class RecipientsManagementTab:
    """Recipients management tab component"""
    
    def __init__(self, notebook, app):
        self.app = app
        self.notebook = notebook
        self.frame = ttk.Frame(notebook)
        self.notebook.add(self.frame, text="Διαχείριση Παραληπτών")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create recipients management tab widgets"""
        # Notification frame for user information
        self._create_notification_frame()
        
        # Recipients list
        recipients_frame = ttk.LabelFrame(self.frame, text="Λίστα Παραληπτών", padding=10)
        recipients_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self._create_recipients_section(recipients_frame)
        
        # Management buttons
        self._create_management_buttons(recipients_frame)
    
    def _create_notification_frame(self):
        """Create important notification frame and organization identity field"""
        # Organization identity frame
        org_frame = ttk.LabelFrame(self.frame, text="Ταυτότητα Οργανισμού", padding=10)
        org_frame.pack(fill='x', padx=10, pady=(5, 5))
        
        # Organization identity field
        org_identity_frame = tk.Frame(org_frame)
        org_identity_frame.pack(fill='x')
        
        tk.Label(org_identity_frame, text="Οργανισμός/Μονάδα:", font=('Arial', 10, 'bold')).pack(side='left')
        
        # Get organization identity from config
        org_identity = self.app.config_manager.get_organization_identity()
        self.org_identity_var = tk.StringVar(value=org_identity)
        
        org_entry = tk.Entry(org_identity_frame, textvariable=self.org_identity_var, 
                           font=('Arial', 10), width=40)
        org_entry.pack(side='left', padx=(10, 0), fill='x', expand=True)
        
        # Bind auto-save on change
        self.org_identity_var.trace('w', self._on_organization_identity_changed)
        
        # Info label
        info_label = tk.Label(org_frame, text="ℹ️ Αυτή η τιμή θα εμφανίζεται στο κελί B2 των Excel αρχείων USB εξαγωγής", 
                             font=('Arial', 9), fg='#666')
        info_label.pack(fill='x', pady=(5, 0))
        
        # Notification frame for warning
        notification_frame = tk.Frame(self.frame, bg='#fff3cd', relief='solid', bd=1)
        notification_frame.pack(fill='x', padx=10, pady=(10, 10))
        
        # Warning text
        warning_text = tk.Text(notification_frame, height=4, wrap='word', bg='#fff3cd', 
                              font=('Arial', 10), relief='flat', cursor='arrow')
        warning_text.pack(fill='x', padx=10, pady=8)
        
        # Insert warning message with formatting
        warning_text.insert('1.0', 'ΣΗΜΑΝΤΙΚΗ ΕΙΔΟΠΟΙΗΣΗ:\n', 'warning_title')
        warning_text.insert('end', 'Το όνομα κάθε παραλήπτη πρέπει να είναι ΑΚΡΙΒΩΣ το ίδιο με αυτό που εμφανίζεται στο περιεχόμενο των σημάτων, συμπεριλαμβανομένων των κεφαλαίων και μικρών γραμμάτων. Διαφορετικά, το autoPyrseia δεν θα μπορεί να αναγνωρίσει το όνομα του παραλήπτη από το περιεχόμενο του σήματος.', 'warning_text')
        
        # Configure text styles
        warning_text.tag_configure('warning_title', font=('Arial', 10, 'bold'), foreground='white', background='#e74c3c')
        warning_text.tag_configure('warning_text', font=('Arial', 9), foreground='#856404')
        
        # Make text read-only
        warning_text.config(state='disabled')
    
    def _create_recipients_section(self, parent):
        """Create recipients list section"""
        # Frame for checkboxes with scrollbar
        self.app.manage_canvas = tk.Canvas(parent)
        manage_scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.app.manage_canvas.yview)
        self.app.manage_checkbox_frame = tk.Frame(self.app.manage_canvas)
        
        self.app.manage_checkbox_frame.bind(
            "<Configure>",
            lambda e: self.app.manage_canvas.configure(scrollregion=self.app.manage_canvas.bbox("all"))
        )
        
        self.app.manage_canvas.create_window((0, 0), window=self.app.manage_checkbox_frame, anchor="nw")
        self.app.manage_canvas.configure(yscrollcommand=manage_scrollbar.set)
        
        self.app.manage_canvas.pack(side='left', fill='both', expand=True)
        manage_scrollbar.pack(side='right', fill='y')
    
    def _create_management_buttons(self, parent):
        """Create management buttons"""
        buttons_frame = tk.Frame(parent)
        buttons_frame.pack(fill='x', pady=(10, 0))
        
        add_button = tk.Button(buttons_frame, text="Προσθήκη Νέου Παραλήπτη", 
                 command=self.add_new_recipient, bg='#3498db', fg='white')
        add_button.pack(side='left', padx=5)
        
        delete_button = tk.Button(buttons_frame, text="Διαγραφή Επιλεγμένων", 
                 command=self.delete_selected_recipients, bg='#e74c3c', fg='white')
        delete_button.pack(side='left', padx=5)
        
        refresh_mgmt_button = tk.Button(buttons_frame, text="Ανανέωση Λίστας", 
                 command=self.refresh_recipients_list, bg='#95a5a6', fg='white')
        refresh_mgmt_button.pack(side='left', padx=5)
        
        # Tooltips
        self.app.create_tooltip(add_button, "Προσθέστε νέο παραλήπτη στη λίστα")
        self.app.create_tooltip(delete_button, "Διαγράψτε επιλεγμένους παραλήπτες (Delete)")
        self.app.create_tooltip(refresh_mgmt_button, "Ανανέωση της λίστας παραληπτών (F5)")
    
    def refresh_recipients_list(self):
        """Refresh recipients list with checkboxes"""
        # Clear previous checkboxes
        for widget in self.app.manage_checkbox_frame.winfo_children():
            widget.destroy()
        self.app.manage_checkboxes.clear()
        
        # Load recipients
        recipients = self.app.recipients_manager.get_all_recipients()
        for recipient in recipients:
            var = tk.BooleanVar()
            
            checkbox = tk.Checkbutton(
                self.app.manage_checkbox_frame,
                text=recipient,
                variable=var,
                font=('Arial', 10),
                anchor='w'
            )
            checkbox.pack(fill='x', padx=5, pady=2)
            
            # Add keyboard navigation and context menu
            self._setup_checkbox_bindings(checkbox, var, recipient)
            
            self.app.manage_checkboxes.append({
                'recipient': recipient,
                'var': var,
                'checkbox': checkbox
            })
    
    def _setup_checkbox_bindings(self, checkbox, var, recipient):
        """Setup keyboard and mouse bindings for checkbox"""
        checkbox.bind('<Return>', lambda e, v=var: v.set(not v.get()))
        checkbox.bind('<space>', lambda e, v=var: v.set(not v.get()))
        checkbox.bind('<FocusIn>', lambda e, cb=checkbox: cb.config(bg='#e8f4fd'))
        checkbox.bind('<FocusOut>', lambda e, cb=checkbox: cb.config(bg='SystemButtonFace'))
        
        # Context menu
        context_menu = tk.Menu(checkbox, tearoff=0)
        context_menu.add_command(label="Επιλογή", command=lambda v=var: v.set(True))
        context_menu.add_command(label="Αποεπιλογή", command=lambda v=var: v.set(False))
        context_menu.add_separator()
        context_menu.add_command(label="Επιλογή Όλων", command=lambda: self.select_all_manage_checkboxes(True))
        context_menu.add_command(label="Αποεπιλογή Όλων", command=lambda: self.select_all_manage_checkboxes(False))
        context_menu.add_separator()
        context_menu.add_command(label="Διαγραφή", command=lambda r=recipient: self.delete_single_recipient(r))
        
        def show_context_menu(event):
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        
        checkbox.bind('<Button-3>', show_context_menu)
    
    def select_all_manage_checkboxes(self, state):
        """Select or deselect all management checkboxes"""
        for checkbox_data in self.app.manage_checkboxes:
            checkbox_data['var'].set(state)
    
    def add_new_recipient(self):
        """Add new recipient to management"""
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Προσθήκη Νέου Παραλήπτη")
        dialog.geometry("400x180")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.transient(self.app.root)
        
        # Escape key to close dialog
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        
        # Main frame
        main_frame = tk.Frame(dialog, padx=25, pady=25)
        main_frame.pack(fill='both', expand=True)
        
        # Fixed buttons frame at bottom
        buttons_frame = tk.Frame(dialog)
        buttons_frame.pack(side='bottom', fill='x', padx=25, pady=15)
        
        tk.Label(main_frame, text="Όνομα Παραλήπτη:", font=('Arial', 12)).pack(pady=(0, 15))
        entry = tk.Entry(main_frame, width=35, font=('Arial', 11))
        entry.pack(pady=8)
        entry.focus()
        
        def add():
            recipient = entry.get().strip()
            if recipient:
                self.app.recipients_manager.add_recipient(recipient)
                self.refresh_recipients_list()
                dialog.destroy()
                self.app.progress_manager.global_message(f"Προστέθηκε παραλήπτης: {recipient}")
            else:
                entry.focus_set()
        
        add_button = tk.Button(buttons_frame, text="Προσθήκη", command=add, 
                 bg='#3498db', fg='white', font=('Arial', 11))
        add_button.pack(side='left', padx=8)
        
        cancel_button = tk.Button(buttons_frame, text="Άκυρο", command=dialog.destroy, 
                 bg='#95a5a6', fg='white', font=('Arial', 11))
        cancel_button.pack(side='left', padx=8)
        
        # Keyboard bindings
        entry.bind('<Return>', lambda e: add())
        dialog.bind('<Return>', lambda e: add())
    
    def delete_selected_recipients(self):
        """Delete selected recipients from management"""
        selected_recipients = []
        for checkbox_data in self.app.manage_checkboxes:
            if checkbox_data['var'].get():
                selected_recipients.append(checkbox_data['recipient'])
        
        if selected_recipients:
            # Confirmation
            if messagebox.askyesno("Επιβεβαίωση", 
                                  f"Διαγραφή {len(selected_recipients)} παραληπτών;"):
                for recipient in selected_recipients:
                    self.app.recipients_manager.remove_recipient(recipient)
                self.refresh_recipients_list()
                self.app.progress_manager.global_message(f"Διαγράφηκαν {len(selected_recipients)} παραλήπτες")
        else:
            messagebox.showinfo("Καμία Επιλογή", "Παρακαλώ επιλέξτε παραλήπτες για διαγραφή.")
    
    def delete_single_recipient(self, recipient):
        """Delete single recipient"""
        if messagebox.askyesno("Επιβεβαίωση Διαγραφής", 
                              f"Είστε σίγουροι ότι θέλετε να διαγράψετε τον παραλήπτη '{recipient}';"):
            self.app.recipients_manager.remove_recipient(recipient)
            self.refresh_recipients_list()
            self.app.progress_manager.global_message(f"Διαγράφηκε παραλήπτης: {recipient}")
    
    def _on_organization_identity_changed(self, *args):
        """Handle organization identity field changes and auto-save"""
        new_value = self.org_identity_var.get()
        self.app.config_manager.set_organization_identity(new_value)
        print(f"Organization identity updated to: {new_value}")
