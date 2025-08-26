#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Signal Processing Tab for autoPyrseia
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from app.utils.file_operations import check_attachment_exists, find_similar_filename


class SignalProcessingTab:
    """Signal processing tab component"""
    
    def __init__(self, notebook, app):
        self.app = app
        self.notebook = notebook
        self.frame = ttk.Frame(notebook)
        self.notebook.add(self.frame, text="Επεξεργασία Σημάτων")
        
        self.create_widgets()
        
        # Track duplicate state
        self.is_duplicate_signal = False
        self.recipients_with_signal = []
    
    def create_widgets(self):
        """Create signal processing tab widgets"""
        # Main container for side-by-side layout
        main_container = tk.Frame(self.frame)
        main_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left side - Signal Information (50% width)
        info_frame = ttk.LabelFrame(main_container, text="Πληροφορίες Σήματος", padding=10)
        info_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        self._create_signal_info_section(info_frame)
        
        # Right side - Recipients (50% width)
        recipients_frame = ttk.LabelFrame(main_container, text="Παραλήπτες", padding=10)
        recipients_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        self._create_recipients_section(recipients_frame)
        
        # Process button - always visible at bottom
        self._create_process_button()
    
    def _create_signal_info_section(self, parent):
        """Create signal information section"""
        # Grid for signal information
        info_grid = tk.Frame(parent)
        info_grid.pack(fill='both', expand=True)
        
        # ID
        tk.Label(info_grid, text="ID:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', padx=5, pady=2)
        
        # ID display and entry
        self.app.id_var = tk.StringVar(value="Δεν έχει ανιχνευθεί σήμα")
        self.app.id_label = tk.Label(info_grid, textvariable=self.app.id_var, fg='gray', cursor='hand2')
        self.app.id_label.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        # ID Edit button
        self.app.id_edit_button = tk.Button(info_grid, text="Edit", 
                                           command=self.edit_id, bg='#f39c12', fg='white', 
                                           font=('Arial', 8), width=6)
        self.app.id_edit_button.grid(row=0, column=2, sticky='w', padx=5, pady=2)
        
        # Bind click event to copy ID to clipboard
        self.app.id_label.bind('<Button-1>', self.copy_id_to_clipboard)
        self.app.create_tooltip(self.app.id_label, "Κάντε κλικ για αντιγραφή του ID στο clipboard")
        self.app.create_tooltip(self.app.id_edit_button, "Επεξεργασία ID σήματος")
        
        # FM
        tk.Label(info_grid, text="FM:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', padx=5, pady=2)
        
        self.app.fm_var = tk.StringVar(value="")
        self.app.fm_label = tk.Label(info_grid, textvariable=self.app.fm_var, fg='gray', cursor='hand2')
        self.app.fm_label.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # FM Edit button
        self.app.fm_edit_button = tk.Button(info_grid, text="Edit", 
                                           command=self.edit_fm, bg='#f39c12', fg='white', 
                                           font=('Arial', 8), width=6)
        self.app.fm_edit_button.grid(row=1, column=2, sticky='w', padx=5, pady=2)
        
        self.app.fm_label.bind('<Button-1>', self.copy_fm_to_clipboard)
        self.app.create_tooltip(self.app.fm_label, "Κάντε κλικ για αντιγραφή του FM στο clipboard")
        self.app.create_tooltip(self.app.fm_edit_button, "Επεξεργασία FM σήματος")
        
        # ΘΕΜΑ
        tk.Label(info_grid, text="ΘΕΜΑ:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', padx=5, pady=2)
        
        self.app.theme_var = tk.StringVar(value="")
        self.app.theme_label = tk.Label(info_grid, textvariable=self.app.theme_var, fg='gray', 
                                       wraplength=250, cursor='hand2')
        self.app.theme_label.grid(row=2, column=1, sticky='w', padx=5, pady=2)
        
        # Theme Edit button
        self.app.theme_edit_button = tk.Button(info_grid, text="Edit", 
                                              command=self.edit_theme, bg='#f39c12', fg='white', 
                                              font=('Arial', 8), width=6)
        self.app.theme_edit_button.grid(row=2, column=2, sticky='w', padx=5, pady=2)
        
        self.app.theme_label.bind('<Button-1>', self.copy_theme_to_clipboard)
        self.app.create_tooltip(self.app.theme_label, "Κάντε κλικ για αντιγραφή του θέματος στο clipboard")
        self.app.create_tooltip(self.app.theme_edit_button, "Επεξεργασία θέματος σήματος")
        
        # Συνημμένα
        tk.Label(info_grid, text="Συνημμένα:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.app.attachments_frame = tk.Frame(info_grid)
        self.app.attachments_frame.grid(row=3, column=1, sticky='w', padx=5, pady=2)
        
        # Clear Downloads button (small and red)
        self.app.clear_downloads_button = tk.Button(info_grid, text="Εκκαθάριση", 
                                                   command=self.clear_downloads_folder, 
                                                   bg='#e74c3c', fg='white', 
                                                   font=('Arial', 7), 
                                                   width=15, height=1,
                                                   relief='raised', borderwidth=1)
        self.app.clear_downloads_button.grid(row=4, column=1, sticky='w', padx=5, pady=5)
        self.app.create_tooltip(self.app.clear_downloads_button, "Καθαρίστε τα αρχεία από τον φάκελο downloads")
    
    def _create_recipients_section(self, parent):
        """Create recipients section"""
        # Recipients buttons at the top
        recipients_buttons = tk.Frame(parent)
        recipients_buttons.pack(fill='x', pady=(0, 10))
        
        # Folder selection button (first)
        folder_button = tk.Button(recipients_buttons, text="Επιλογή Φακέλου", 
                 command=self.add_folder_as_recipient, bg='#e67e22', fg='white', font=('Arial', 9))
        folder_button.pack(side='left', padx=5)
        
        add_recipient_button = tk.Button(recipients_buttons, text="Προσθήκη Παραλήπτη", 
                 command=self.add_recipient, bg='#3498db', fg='white', font=('Arial', 9))
        add_recipient_button.pack(side='left', padx=5)
        
        self.app.create_tooltip(folder_button, "Επιλέξτε φάκελο ως προσωρινό παραλήπτη")
        self.app.create_tooltip(add_recipient_button, "Προσθέστε παραλήπτη από τη λίστα (Alt+A)")
        
        # Frame for checkboxes with scrollbar
        self.app.recipients_canvas = tk.Canvas(parent, height=200)
        recipients_scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.app.recipients_canvas.yview)
        self.app.recipients_checkbox_frame = tk.Frame(self.app.recipients_canvas)
        
        self.app.recipients_checkbox_frame.bind(
            "<Configure>",
            lambda e: self.app.recipients_canvas.configure(scrollregion=self.app.recipients_canvas.bbox("all"))
        )
        
        self.app.recipients_canvas.create_window((0, 0), window=self.app.recipients_checkbox_frame, anchor="nw")
        self.app.recipients_canvas.configure(yscrollcommand=recipients_scrollbar.set)
        
        self.app.recipients_canvas.pack(side='left', fill='both', expand=True)
        recipients_scrollbar.pack(side='right', fill='y')
    
    def _create_process_button(self):
        """Create process signal button"""
        process_frame = tk.Frame(self.frame)
        process_frame.pack(side='bottom', fill='x', padx=10, pady=10)
        
        self.app.process_button = tk.Button(process_frame, text="Επεξεργασία Σήματος", 
                                           command=self.app.process_signal, bg='#27ae60', fg='white', 
                                           font=('Arial', 11, 'bold'), height=2)
        self.app.process_button.pack(pady=5)
        self.app.process_button.config(state='disabled')
        
        self.app.create_tooltip(self.app.process_button, "Επεξεργαστείτε το σήμα για όλους τους επιλεγμένους παραλήπτες (Enter)")
    
    def display_signal_data(self, signal_data):
        """Display signal data in the tab"""
        self.app.current_signal_data = signal_data
        
        # Check if manual input is required
        if signal_data.get('manual_input'):
            self.app.handle_manual_input_required(signal_data)
            return
        
        # Check for duplicates
        signal_id = signal_data.get('id', '')
        fm = signal_data.get('fm', '')
        
        is_duplicate = self.app.duplicate_manager.is_duplicate(signal_id, fm)
        
        # Update StringVar variables
        self.app.id_var.set(signal_data.get('id', 'Μη διαθέσιμο'))
        self.app.fm_var.set(signal_data.get('fm', 'Μη διαθέσιμο'))
        self.app.theme_var.set(signal_data.get('theme', 'Μη διαθέσιμο'))
        
        # Update label colors
        self.app.id_label.config(fg='black')
        self.app.fm_label.config(fg='black')
        self.app.theme_label.config(fg='black')
        
        # Display attachments
        self.display_attachments(signal_data.get('attachments', []))
        
        # Display recipients with duplicate handling
        self.display_recipients_with_duplicate_check(signal_data.get('recipients', []), is_duplicate, signal_id, fm)
        
        # Show duplicate notification if needed
        if is_duplicate:
            self._show_duplicate_notification(signal_id, fm)
        
        # Enable process button
        self.app.process_button.config(state='normal')
        
        # Complete progress and update status
        self.app.status_bar.complete_progress()
        status_msg = "Σήμα φορτώθηκε επιτυχώς - Έτοιμο για επεξεργασία"
        if is_duplicate:
            status_msg += " (Ανιχνεύθηκε διπλότυπο)"
        self.app.root.after(300, lambda: self.app.status_bar.update_status(status_msg))
        self.app.root.after(800, lambda: self.app.status_bar.reset_progress())
    
    def display_attachments(self, attachments):
        """Display attachments"""
        # Clear previous attachments
        for widget in self.app.attachments_frame.winfo_children():
            widget.destroy()
        
        if not attachments:
            tk.Label(self.app.attachments_frame, text="Δεν υπάρχουν συνημμένα", fg='gray').pack()
            return
        
        for attachment in attachments:
            frame = tk.Frame(self.app.attachments_frame)
            frame.pack(fill='x', pady=1)
            
            # Status icon (✓ or ✗)
            status = "✓" if check_attachment_exists(attachment) else "✗"
            color = "green" if status == "✓" else "red"
            
            status_label = tk.Label(frame, text=status, fg=color, font=('Arial', 12, 'bold'))
            status_label.pack(side='left')
            
            # File name
            name_label = tk.Label(frame, text=attachment, wraplength=300, justify='left')
            name_label.pack(side='left', padx=(5, 0))
            
            # Store references for easy updating
            frame.status_label = status_label
            frame.name_label = name_label
            frame.attachment_name = attachment
    
    def display_recipients(self, recipients):
        """Display recipients with checkboxes"""
        # Clear previous checkboxes
        for widget in self.app.recipients_checkbox_frame.winfo_children():
            widget.destroy()
        self.app.recipients_checkboxes.clear()
        
        # Filter recipients if not from manual input
        if hasattr(self.app, 'current_signal_data') and self.app.current_signal_data and \
           self.app.current_signal_data.get('is_manual_input', False):
            filtered_recipients = recipients
        else:
            try:
                filtered_recipients = self.app.recipients_manager.filter_recipients(recipients)
            except Exception:
                filtered_recipients = recipients
        
        # Create checkboxes for each recipient
        for recipient in filtered_recipients:
            var = tk.BooleanVar()
            var.set(True)  # Auto-select all
            
            checkbox = tk.Checkbutton(
                self.app.recipients_checkbox_frame,
                text=recipient,
                variable=var,
                font=('Arial', 10),
                anchor='w'
            )
            checkbox.pack(fill='x', padx=5, pady=2)
            
            self.app.recipients_checkboxes.append({
                'recipient': recipient,
                'var': var,
                'checkbox': checkbox
            })
    
    def get_selected_recipients(self):
        """Get selected recipients"""
        selected = []
        for checkbox_data in self.app.recipients_checkboxes:
            if checkbox_data['var'].get():
                recipient_info = {
                    'name': checkbox_data['recipient'],
                    'is_temporary': checkbox_data.get('is_temporary', False)
                }
                
                # Add folder path for temporary recipients
                if checkbox_data.get('is_temporary', False):
                    if 'folder_path' in checkbox_data:
                        recipient_info['folder_path'] = checkbox_data['folder_path']
                    else:
                        print(f"ERROR: Temporary recipient '{checkbox_data['recipient']}' missing folder_path!")
                        # Skip this recipient to avoid creating DATA folder
                        continue
                
                selected.append(recipient_info)
        return selected
    
    def clear_signal_display(self):
        """Clear signal display"""
        # Clear labels
        self.app.id_var.set("Αναμονή σήματος...")
        self.app.fm_var.set("Αναμονή σήματος...")
        self.app.theme_var.set("Αναμονή σήματος...")
        
        self.app.id_label.config(fg='gray')
        self.app.fm_label.config(fg='gray')
        self.app.theme_label.config(fg='gray')
        
        # Clear attachments
        for widget in self.app.attachments_frame.winfo_children():
            widget.destroy()
        tk.Label(self.app.attachments_frame, text="Δεν υπάρχουν συνημμένα", fg='gray').pack()
        
        # Clear recipients
        for widget in self.app.recipients_checkbox_frame.winfo_children():
            widget.destroy()
        
        # Reset checkboxes list
        self.app.recipients_checkboxes = []
    
    def update_attachment_indicators(self):
        """Update attachment indicators"""
        if not self.app.current_signal_data:
            return
        
        attachments = self.app.current_signal_data.get('attachments', [])
        if not attachments:
            return
        
        # Update indicators
        for widget in self.app.attachments_frame.winfo_children():
            if isinstance(widget, tk.Frame) and hasattr(widget, 'attachment_name'):
                attachment_name = widget.attachment_name
                
                # Check if file exists
                exists = check_attachment_exists(attachment_name)
                new_status = "✓" if exists else "✗"
                new_color = "green" if exists else "red"
                
                # Update status icon if needed
                current_status = widget.status_label.cget('text')
                if current_status != new_status:
                    widget.status_label.config(text=new_status, fg=new_color)
                    if new_status == "✓":
                        self.app.status_bar.update_status(f"Ανιχνεύθηκε συνημμένο: {attachment_name}")
    
    def signal_processed_successfully(self, result=None, signal_data=None):
        """Handle successful signal processing"""
        self.app.process_button.config(state='disabled')
        
        # Complete progress to 100% first
        self.app.status_bar.complete_progress()
        
        # Use passed signal_data if available, otherwise fallback to app's current_signal_data
        if signal_data is not None:
            current_signal_data = signal_data
        else:
            current_signal_data = self.app.current_signal_data
        
        # Signal processing completed successfully
        if current_signal_data:
            try:
                # Get selected recipients from result if available, otherwise fallback to checkboxes
                if result and 'selected_recipients' in result:
                    selected_recipients = result['selected_recipients']
                else:
                    selected_recipients = [cb['recipient'] for cb in self.app.recipients_checkboxes if cb['var'].get()]
                
                # Ensure all recipients are strings (handle case where dicts might be passed)
                recipient_names = []
                for recipient in selected_recipients:
                    if isinstance(recipient, dict):
                        recipient_names.append(recipient.get('name', str(recipient)))
                    else:
                        recipient_names.append(str(recipient))
                
                # Always add to history if we have a history_tab and signal data
                if hasattr(self.app, 'history_tab'):
                    signal_id = current_signal_data.get('id', 'N/A')
                    fm = current_signal_data.get('fm', 'N/A')
                    # Use selected recipients or indicate none selected
                    recipients_for_log = recipient_names if recipient_names else ['(Δεν επιλέχθηκαν)']
                    self.app.history_tab.add_processed_signal(signal_id, fm, recipients_for_log)
                    
            except Exception as e:
                print(f"Error in signal processing: {e}")
                import traceback
                traceback.print_exc()
        
        # Show results after a brief delay
        if result:
            self.app.root.after(500, lambda: self.show_processing_results(result))
        
        # Clear signal data and UI
        self.app.current_signal_data = None
        self.clear_signal_display()
        
        # Clear downloads folder
        from app.utils.file_operations import clear_downloads_folder
        clear_downloads_folder()
        
        # Update final status
        def update_final_status():
            if result and result.get('total_processed', 0) > 0:
                self.app.status_bar.update_status("Σήμα επεξεργάστηκε επιτυχώς - Αναμονή για νέο σήμα...")
            else:
                self.app.status_bar.update_status("Επεξεργασία ολοκληρώθηκε - Αναμονή για νέο σήμα...")
            self.app.root.after(500, lambda: self.app.status_bar.reset_progress())
        
        self.app.root.after(800, update_final_status)
    
    def show_processing_results(self, result):
        """Show detailed processing results dialog with verification information"""
        dialog = tk.Toplevel(self.app.root)
        dialog.title("ΕΠΙΤΥΧΗΣ ΕΠΕΞΕΡΓΑΣΙΑ")
        dialog.geometry("600x450")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Center dialog
        dialog.transient(self.app.root)
        self.app.root.update_idletasks()
        
        main_x = self.app.root.winfo_x()
        main_y = self.app.root.winfo_y()
        main_width = self.app.root.winfo_width()
        main_height = self.app.root.winfo_height()
        
        center_x = main_x + (main_width - 600) // 2
        center_y = main_y + (main_height - 450) // 2
        
        dialog.geometry(f"600x450+{center_x}+{center_y}")
        
        # Main frame with scrollable content
        main_frame = tk.Frame(dialog, padx=25, pady=20, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True)
        
        # Create canvas and scrollbar for scrollable content
        canvas = tk.Canvas(main_frame, bg='#f8f9fa', highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f8f9fa')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Success title with decoration
        title_frame = tk.Frame(scrollable_frame, bg='#f8f9fa')
        title_frame.pack(fill='x', pady=(0, 10))
        
        title_label = tk.Label(title_frame, text="ΕΠΙΤΥΧΗΣ ΕΠΕΞΕΡΓΑΣΙΑ!", 
                              font=('Arial', 16, 'bold'),
                              fg='#27ae60', bg='#f8f9fa')
        title_label.pack()
        
        # Decorative separator
        separator1 = tk.Label(title_frame, text="━" * 40, 
                             font=('Courier', 10),
                             fg='#27ae60', bg='#f8f9fa')
        separator1.pack()
        
        # Signal information
        info_frame = tk.Frame(scrollable_frame, bg='#f8f9fa')
        info_frame.pack(fill='x', pady=(10, 5))
        
        # Get signal information
        signal_id = result.get('signal_id', 'N/A')
        recipients = result.get('selected_recipients', [])
        processing_time = result.get('processing_time', 'N/A')
        attachments_copied = result.get('attachments_copied', 0)
        
        # Format recipients list
        if isinstance(recipients, list):
            if recipients:
                recipient_names = []
                for r in recipients:
                    if isinstance(r, dict):
                        recipient_names.append(r.get('name', str(r)))
                    else:
                        recipient_names.append(str(r))
                recipients_str = ', '.join(recipient_names)
            else:
                recipients_str = '(Δεν επιλέχθηκαν)'
        else:
            recipients_str = str(recipients)
        
        # Signal ID
        signal_label = tk.Label(info_frame, text=f"Σήμα: {signal_id}", 
                               font=('Arial', 11, 'bold'),
                               fg='#2c3e50', bg='#f8f9fa', anchor='w')
        signal_label.pack(fill='x', pady=2)
        
        # Recipients
        recipients_label = tk.Label(info_frame, text=f"Παραλήπτες: {recipients_str}", 
                                   font=('Arial', 10),
                                   fg='#34495e', bg='#f8f9fa', anchor='w', wraplength=540)
        recipients_label.pack(fill='x', pady=2)
        
        # Processing time
        if processing_time != 'N/A':
            time_label = tk.Label(info_frame, text=f"Ώρα επεξεργασίας: {processing_time}", 
                                 font=('Arial', 10),
                                 fg='#34495e', bg='#f8f9fa', anchor='w')
            time_label.pack(fill='x', pady=2)
        
        # Separator
        separator2 = tk.Label(scrollable_frame, text="━" * 40, 
                             font=('Courier', 8),
                             fg='#bdc3c7', bg='#f8f9fa')
        separator2.pack(pady=5)
        
        # Verification section
        verification_frame = tk.Frame(scrollable_frame, bg='#f8f9fa')
        verification_frame.pack(fill='x', pady=5)
        
        verification_title = tk.Label(verification_frame, text="✅ ΕΠΙΒΕΒΑΙΩΣΕΙΣ:", 
                                     font=('Arial', 11, 'bold'),
                                     fg='#27ae60', bg='#f8f9fa', anchor='w')
        verification_title.pack(fill='x', pady=(0, 5))
        
        # Main PDF verification
        pdf_verified = result.get('pdf_copied_to_all', True)  # Default to True if not specified
        pdf_status = "✅" if pdf_verified else "❌"
        pdf_text = "Κύριο PDF αντιγράφηκε σε όλους τους παραλήπτες" if pdf_verified else "Σφάλμα αντιγραφής κύριου PDF"
        pdf_label = tk.Label(verification_frame, text=f"{pdf_status} {pdf_text}", 
                            font=('Arial', 10),
                            fg='#27ae60' if pdf_verified else '#e74c3c', 
                            bg='#f8f9fa', anchor='w')
        pdf_label.pack(fill='x', pady=1)
        
        # Attachments verification
        attachments_verified = result.get('attachments_copied_to_all', True)  # Default to True if not specified
        attachments_status = "✅" if attachments_verified else "❌"
        if attachments_copied > 0:
            attachments_text = f"Όλα τα συνημμένα ({attachments_copied} αρχεία) αντιγράφηκαν σε όλους τους παραλήπτες"
            if not attachments_verified:
                attachments_text = f"Σφάλμα αντιγραφής συνημμένων ({attachments_copied} αρχεία)"
        else:
            attachments_text = "Δεν υπάρχουν συνημμένα αρχεία"
            attachments_status = "ℹ️"
        
        attachments_label = tk.Label(verification_frame, text=f"{attachments_status} {attachments_text}", 
                                    font=('Arial', 10),
                                    fg='#27ae60' if attachments_verified else '#e74c3c' if attachments_copied > 0 else '#7f8c8d', 
                                    bg='#f8f9fa', anchor='w')
        attachments_label.pack(fill='x', pady=1)
        
        # Additional verifications
        history_updated = result.get('history_updated', True)
        history_status = "✅" if history_updated else "❌"
        history_text = "Ιστορικό ενημερώθηκε" if history_updated else "Σφάλμα ενημέρωσης ιστορικού"
        history_label = tk.Label(verification_frame, text=f"{history_status} {history_text}", 
                                font=('Arial', 10),
                                fg='#27ae60' if history_updated else '#e74c3c', 
                                bg='#f8f9fa', anchor='w')
        history_label.pack(fill='x', pady=1)
        
        # Files cleaned
        files_cleaned = result.get('downloads_cleaned', True)
        files_status = "✅" if files_cleaned else "❌"
        files_text = "Προσωρινά αρχεία καθαρίστηκαν" if files_cleaned else "Σφάλμα καθαρισμού αρχείων"
        files_label = tk.Label(verification_frame, text=f"{files_status} {files_text}", 
                              font=('Arial', 10),
                              fg='#27ae60' if files_cleaned else '#e74c3c', 
                              bg='#f8f9fa', anchor='w')
        files_label.pack(fill='x', pady=1)
        
        # Final separator
        separator3 = tk.Label(scrollable_frame, text="━" * 40, 
                             font=('Courier', 8),
                             fg='#27ae60', bg='#f8f9fa')
        separator3.pack(pady=(10, 15))
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Button frame
        button_frame = tk.Frame(dialog, bg='#f8f9fa')
        button_frame.pack(fill='x', padx=25, pady=(0, 20))
        
        # Close button
        close_button = tk.Button(button_frame, text="ΟΚ", 
                                command=dialog.destroy,
                                bg='#27ae60', fg='white', 
                                font=('Arial', 11, 'bold'),
                                width=12, height=1)
        close_button.pack(pady=5)
        close_button.focus_set()
        
        # Bind Enter key to close
        dialog.bind('<Return>', lambda e: dialog.destroy())
        
        # Do not auto-close - let user close manually
    
    def hide_processing_results(self):
        """Hide processing results and clear UI"""
        self.app.id_var.set("Δεν έχει ανιχνευθεί σήμα")
        self.app.fm_var.set("")
        self.app.theme_var.set("")
        
        self.app.id_label.config(fg='gray')
        self.app.fm_label.config(fg='gray')
        self.app.theme_label.config(fg='gray')
        
        # Clear recipients checkboxes
        for widget in self.app.recipients_checkbox_frame.winfo_children():
            widget.destroy()
        self.app.recipients_checkboxes.clear()
        
        # Clear attachments
        for widget in self.app.attachments_frame.winfo_children():
            widget.destroy()
        tk.Label(self.app.attachments_frame, text="Δεν υπάρχουν συνημμένα", fg='gray').pack()
    
    def add_recipient(self):
        """Add new recipient from approved list"""
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Επιλογή Παραλήπτη")
        dialog.geometry("550x600")
        dialog.resizable(True, True)
        dialog.grab_set()
        dialog.minsize(400, 450)
        
        # Center dialog on parent window
        dialog.transient(self.app.root)
        
        # Escape key to close dialog
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding=15)
        main_frame.pack(fill='both', expand=True)
        
        # Fixed buttons frame at bottom
        buttons_frame = tk.Frame(dialog)
        buttons_frame.pack(side='bottom', fill='x', padx=15, pady=15)
        
        # Title
        tk.Label(main_frame, text="Επιλέξτε παραλήπτη από τη λίστα:", 
                font=('Arial', 12, 'bold')).pack(pady=(0, 15))
        
        # Load recipients list from recipients_manager
        try:
            all_available_recipients = self.app.recipients_manager.get_all_recipients()
        except Exception as e:
            print(f"Error loading recipients: {e}")
            all_available_recipients = []
        
        if not all_available_recipients:
            tk.Label(main_frame, text="Δεν βρέθηκαν διαθέσιμοι παραλήπτες στη λίστα", 
                    fg='red', font=('Arial', 11)).pack(pady=20)
            close_btn = tk.Button(main_frame, text="Κλείσιμο", command=dialog.destroy, 
                     bg='#e74c3c', fg='white', font=('Arial', 11))
            close_btn.pack(pady=10)
            close_btn.focus_set()
            return
        
        # Search frame
        search_frame = tk.Frame(main_frame)
        search_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(search_frame, text="Αναζήτηση:", font=('Arial', 10)).pack(side='left')
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side='left', padx=(5, 0), fill='x', expand=True)
        
        # Recipients listbox
        listbox_frame = ttk.Frame(main_frame)
        listbox_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        available_listbox = tk.Listbox(listbox_frame, height=18, font=('Arial', 10))
        available_scrollbar = ttk.Scrollbar(listbox_frame, orient='vertical', command=available_listbox.yview)
        available_listbox.configure(yscrollcommand=available_scrollbar.set)
        
        # Function to filter recipients based on search
        def filter_recipients(*args):
            search_text = search_var.get().lower()
            available_listbox.delete(0, tk.END)
            
            current_recipients = [cb['recipient'] for cb in self.app.recipients_checkboxes]
            for recipient in sorted(all_available_recipients):
                if recipient not in current_recipients and search_text in recipient.lower():
                    available_listbox.insert(tk.END, recipient)
        
        # Bind search functionality
        search_var.trace('w', filter_recipients)
        
        # Initial population
        filter_recipients()
        
        available_listbox.pack(side='left', fill='both', expand=True)
        available_scrollbar.pack(side='right', fill='y')
        
        def add_selected():
            selected_indices = available_listbox.curselection()
            if selected_indices:
                for index in selected_indices:
                    recipient = available_listbox.get(index)
                    # Add as checkbox with keyboard support
                    var = tk.BooleanVar()
                    var.set(True)  # Selected by default
                    
                    checkbox = tk.Checkbutton(
                        self.app.recipients_checkbox_frame,
                        text=recipient,
                        variable=var,
                        font=('Arial', 10),
                        anchor='w'
                    )
                    checkbox.pack(fill='x', padx=5, pady=2)
                    
                    # Add keyboard navigation for the new checkbox
                    checkbox.bind('<Return>', lambda e, v=var: v.set(not v.get()))
                    checkbox.bind('<space>', lambda e, v=var: v.set(not v.get()))
                    checkbox.bind('<FocusIn>', lambda e, cb=checkbox: cb.config(bg='#e8f4fd'))
                    checkbox.bind('<FocusOut>', lambda e, cb=checkbox: cb.config(bg='SystemButtonFace'))
                    
                    self.app.recipients_checkboxes.append({
                        'recipient': recipient,
                        'var': var,
                        'checkbox': checkbox,
                        'is_temporary': False
                    })
                dialog.destroy()
                self.app.status_bar.update_status(f"Προστέθηκε παραλήπτης: {recipient}")
        
        # Fixed buttons at bottom
        add_button = tk.Button(buttons_frame, text="Προσθήκη Επιλεγμένου", command=add_selected, 
                 bg='#3498db', fg='white', font=('Arial', 11))
        add_button.pack(side='left', padx=10)
        
        cancel_button = tk.Button(buttons_frame, text="Άκυρο", command=dialog.destroy, 
                 bg='#95a5a6', fg='white', font=('Arial', 11))
        cancel_button.pack(side='left', padx=10)
        
        # Keyboard bindings
        available_listbox.bind('<Double-Button-1>', lambda e: add_selected())
        available_listbox.bind('<Return>', lambda e: add_selected())
        dialog.bind('<Return>', lambda e: add_selected() if available_listbox.curselection() else None)
        
        # Set initial focus to search entry
        search_entry.focus_set()
    
    def add_folder_as_recipient(self):
        """Select folder as temporary recipient and process any PDFs found"""
        from tkinter import filedialog, messagebox
        import os
        from pathlib import Path
        import threading
        
        # Open folder dialog
        folder_path = filedialog.askdirectory(title="Επιλογή Φακέλου ως Παραλήπτη")
        if not folder_path:
            return  # User cancelled
        
        # Get folder name as recipient name
        folder_name = os.path.basename(folder_path)
        if not folder_name:
            self.app.status_bar.update_status("Μη έγκυρος φάκελος")
            return
        
        # Check if this folder is already added as recipient
        current_recipients = [cb['recipient'] for cb in self.app.recipients_checkboxes]
        if folder_name in current_recipients:
            self.app.status_bar.update_status(f"Ο φάκελος '{folder_name}' είναι ήδη στη λίστα")
            return
        
        # Add as temporary recipient with special marking
        var = tk.BooleanVar()
        var.set(True)  # Selected by default
        
        # Create display text with folder indicator
        display_text = f"📁 {folder_name} (Προσωρινός)"
        
        checkbox = tk.Checkbutton(
            self.app.recipients_checkbox_frame,
            text=display_text,
            variable=var,
            font=('Arial', 10),
            anchor='w',
            fg='#e67e22'  # Orange color to distinguish temporary recipients
        )
        checkbox.pack(fill='x', padx=5, pady=2)
        
        # Add keyboard navigation
        checkbox.bind('<Return>', lambda e, v=var: v.set(not v.get()))
        checkbox.bind('<space>', lambda e, v=var: v.set(not v.get()))
        checkbox.bind('<FocusIn>', lambda e, cb=checkbox: cb.config(bg='#e8f4fd'))
        checkbox.bind('<FocusOut>', lambda e, cb=checkbox: cb.config(bg='SystemButtonFace'))
        
        self.app.recipients_checkboxes.append({
            'recipient': folder_name,  # Store the actual folder name for processing
            'var': var,
            'checkbox': checkbox,
            'is_temporary': True,  # Mark as temporary
            'folder_path': folder_path  # Store full path for reference
        })
        
        self.app.status_bar.update_status(f"Προστέθηκε προσωρινός παραλήπτης: {folder_name}")
        
        # Now scan the folder for PDF files and process them
        def scan_and_process_folder():
            try:
                folder_obj = Path(folder_path)
                pdf_files = list(folder_obj.glob("*.pdf"))
                
                if not pdf_files:
                    self.app.root.after(0, lambda: self.app.status_bar.update_status(f"Δεν βρέθηκαν PDF αρχεία στον φάκελο: {folder_name}"))
                    return
                
                self.app.root.after(0, lambda: self.app.status_bar.update_status(f"Βρέθηκαν {len(pdf_files)} PDF αρχεία. Επεξεργασία..."))
                
                # Process each PDF file
                processed_count = 0
                for pdf_file in pdf_files:
                    try:
                        # Update status for current file
                        self.app.root.after(0, lambda f=pdf_file.name: self.app.status_bar.update_status(f"Επεξεργασία: {f}"))
                        
                        # Process the PDF
                        signal_data = self.app.pdf_processor.process_pdf(str(pdf_file))
                        
                        if signal_data and not signal_data.get('manual_input'):
                            # Successfully processed - display the signal data
                            processed_count += 1
                            
                            # Update UI with the last processed signal (or first if only one)
                            if processed_count == 1 or len(pdf_files) == 1:
                                self.app.root.after(0, lambda data=signal_data: self.display_signal_data(data))
                        
                    except Exception as e:
                        print(f"Σφάλμα επεξεργασίας PDF {pdf_file.name}: {e}")
                        continue
                
                # Final status update
                if processed_count > 0:
                    self.app.root.after(0, lambda: self.app.status_bar.update_status(f"Επεξεργάστηκαν επιτυχώς {processed_count} από {len(pdf_files)} PDF αρχεία"))
                    if processed_count == 1:
                        self.app.root.after(1000, lambda: self.app.status_bar.update_status("Σήμα φορτώθηκε από φάκελο - Έτοιμο για επεξεργασία"))
                else:
                    self.app.root.after(0, lambda: self.app.status_bar.update_status(f"Δεν ήταν δυνατή η επεξεργασία κανενός PDF στον φάκελο: {folder_name}"))
                
            except Exception as e:
                error_msg = f"Σφάλμα σάρωσης φακέλου: {str(e)}"
                self.app.root.after(0, lambda: self.app.status_bar.update_status(error_msg))
                print(error_msg)
        
        # Run folder scanning in a separate thread to avoid blocking UI
        threading.Thread(target=scan_and_process_folder, daemon=True).start()
    
    def copy_id_to_clipboard(self, event=None):
        """Copy ID to clipboard"""
        id_text = self.app.id_var.get()
        
        if not id_text or id_text in ['', 'Μη διαθέσιμο', 'Δεν έχει ανιχνευθεί σήμα']:
            messagebox.showinfo("Πληροφορία", "Δεν υπάρχει ID προς αντιγραφή")
            return
        
        try:
            self.app.root.clipboard_clear()
            self.app.root.clipboard_append(id_text)
            self.app.root.update()
            
            self.app.status_bar.update_status(f"ID αντιγράφηκε στο clipboard: {id_text}")
            
            # Visual feedback
            original_bg = self.app.id_label.cget('bg')
            self.app.id_label.config(bg='#d5f4e6')
            self.app.root.after(300, lambda: self.app.id_label.config(bg=original_bg))
            
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Αποτυχία αντιγραφής στο clipboard: {str(e)}")
    
    def copy_fm_to_clipboard(self, event=None):
        """Copy FM to clipboard"""
        fm_text = self.app.fm_var.get()
        
        if not fm_text or fm_text in ['', 'Μη διαθέσιμο']:
            messagebox.showinfo("Πληροφορία", "Δεν υπάρχει FM προς αντιγραφή")
            return
        
        try:
            self.app.root.clipboard_clear()
            self.app.root.clipboard_append(fm_text)
            self.app.root.update()
            
            self.app.status_bar.update_status(f"FM αντιγράφηκε στο clipboard: {fm_text}")
            
            # Visual feedback
            original_bg = self.app.fm_label.cget('bg')
            self.app.fm_label.config(bg='#d5f4e6')
            self.app.root.after(300, lambda: self.app.fm_label.config(bg=original_bg))
            
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Αποτυχία αντιγραφής στο clipboard: {str(e)}")
    
    def copy_theme_to_clipboard(self, event=None):
        """Copy theme to clipboard"""
        theme_text = self.app.theme_var.get()
        
        if not theme_text or theme_text in ['', 'Μη διαθέσιμο', 'Αναμονή σήματος...']:
            messagebox.showinfo("Πληροφορία", "Δεν υπάρχει θέμα προς αντιγραφή")
            return
        
        try:
            self.app.root.clipboard_clear()
            self.app.root.clipboard_append(theme_text)
            self.app.root.update()
            
            self.app.status_bar.update_status(f"Θέμα αντιγράφηκε στο clipboard: {theme_text[:50]}{'...' if len(theme_text) > 50 else ''}")
            
            # Visual feedback
            original_bg = self.app.theme_label.cget('bg')
            self.app.theme_label.config(bg='#d5f4e6')
            self.app.root.after(300, lambda: self.app.theme_label.config(bg=original_bg))
            
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Αποτυχία αντιγραφής στο clipboard: {str(e)}")
    
    def edit_id(self):
        """Edit signal ID inline"""
        current_id = self.app.id_var.get()
        if current_id in ['Δεν έχει ανιχνευθεί σήμα', '']:
            messagebox.showinfo("Πληροφορία", "Δεν υπάρχει σήμα για επεξεργασία")
            return
        
        # Hide the label and show an entry widget in its place
        self.app.id_label.grid_remove()
        self.app.id_edit_button.config(text="Save", bg='#27ae60')
        
        # Create entry widget
        self.app.id_entry = tk.Entry(self.app.id_label.master, textvariable=self.app.id_var, 
                                    font=('Arial', 10), width=30)
        self.app.id_entry.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        self.app.id_entry.focus_set()
        self.app.id_entry.select_range(0, tk.END)
        
        def save_id():
            new_id = self.app.id_var.get().strip()
            if new_id:
                # Update the signal data
                if hasattr(self.app, 'current_signal_data') and self.app.current_signal_data:
                    self.app.current_signal_data['id'] = new_id
                
                self.app.progress_manager.global_message(f"ID ενημερώθηκε: {new_id}")
            
            # Remove entry and show label again
            self.app.id_entry.destroy()
            self.app.id_label.grid(row=0, column=1, sticky='w', padx=5, pady=2)
            self.app.id_edit_button.config(text="Edit", bg='#f39c12', command=self.edit_id)
        
        # Update button to save mode
        self.app.id_edit_button.config(command=save_id)
        
        # Bind Enter key to save
        self.app.id_entry.bind('<Return>', lambda e: save_id())
        self.app.id_entry.bind('<Escape>', lambda e: save_id())
    
    def edit_fm(self):
        """Edit signal FM inline"""
        current_fm = self.app.fm_var.get()
        if current_fm in ['Μη διαθέσιμο']:
            self.app.fm_var.set("")
        
        # Hide the label and show an entry widget in its place
        self.app.fm_label.grid_remove()
        self.app.fm_edit_button.config(text="Save", bg='#27ae60')
        
        # Create entry widget
        self.app.fm_entry = tk.Entry(self.app.fm_label.master, textvariable=self.app.fm_var, 
                                    font=('Arial', 10), width=30)
        self.app.fm_entry.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        self.app.fm_entry.focus_set()
        self.app.fm_entry.select_range(0, tk.END)
        
        def save_fm():
            new_fm = self.app.fm_var.get().strip()
            
            # Update the signal data
            if hasattr(self.app, 'current_signal_data') and self.app.current_signal_data:
                self.app.current_signal_data['fm'] = new_fm
            
            # Update display
            self.app.fm_var.set(new_fm if new_fm else "Μη διαθέσιμο")
            self.app.progress_manager.global_message(f"FM ενημερώθηκε: {new_fm if new_fm else 'Διαγράφηκε'}")
            
            # Remove entry and show label again
            self.app.fm_entry.destroy()
            self.app.fm_label.grid(row=1, column=1, sticky='w', padx=5, pady=2)
            self.app.fm_edit_button.config(text="Edit", bg='#f39c12', command=self.edit_fm)
        
        # Update button to save mode
        self.app.fm_edit_button.config(command=save_fm)
        
        # Bind Enter key to save
        self.app.fm_entry.bind('<Return>', lambda e: save_fm())
        self.app.fm_entry.bind('<Escape>', lambda e: save_fm())
    
    def edit_theme(self):
        """Edit signal theme inline"""
        current_theme = self.app.theme_var.get()
        if current_theme in ['Μη διαθέσιμο', 'Αναμονή σήματος...']:
            self.app.theme_var.set("")
        
        # Hide the label and show a text widget in its place
        self.app.theme_label.grid_remove()
        self.app.theme_edit_button.config(text="Save", bg='#27ae60')
        
        # Create text widget for multi-line editing
        text_frame = tk.Frame(self.app.theme_label.master)
        text_frame.grid(row=2, column=1, sticky='w', padx=5, pady=2)
        
        self.app.theme_text = tk.Text(text_frame, height=3, width=35, font=('Arial', 10), 
                                     wrap='word', relief='solid', borderwidth=1)
        theme_scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.app.theme_text.yview)
        self.app.theme_text.configure(yscrollcommand=theme_scrollbar.set)
        
        self.app.theme_text.pack(side='left', fill='both', expand=True)
        theme_scrollbar.pack(side='right', fill='y')
        
        # Insert current theme
        current_theme_text = current_theme if current_theme not in ['Μη διαθέσιμο', 'Αναμονή σήματος...'] else ""
        self.app.theme_text.insert('1.0', current_theme_text)
        self.app.theme_text.focus_set()
        
        def save_theme():
            new_theme = self.app.theme_text.get('1.0', tk.END).strip()
            
            # Update the signal data
            if hasattr(self.app, 'current_signal_data') and self.app.current_signal_data:
                self.app.current_signal_data['theme'] = new_theme
            
            # Update display
            self.app.theme_var.set(new_theme if new_theme else "Μη διαθέσιμο")
            self.app.progress_manager.global_message(f"Θέμα ενημερώθηκε: {new_theme[:50]}{'...' if len(new_theme) > 50 else ''}" if new_theme else "Θέμα διαγράφηκε")
            
            # Remove text widget and show label again
            text_frame.destroy()
            self.app.theme_label.grid(row=2, column=1, sticky='w', padx=5, pady=2)
            self.app.theme_edit_button.config(text="Edit", bg='#f39c12', command=self.edit_theme)
        
        # Update button to save mode
        self.app.theme_edit_button.config(command=save_theme)
        
        # Bind Escape key to save (Ctrl+Enter for new lines)
        self.app.theme_text.bind('<Escape>', lambda e: save_theme())
        self.app.theme_text.bind('<Control-Return>', lambda e: save_theme())
    
    def display_recipients_with_duplicate_check(self, recipients, is_duplicate, signal_id, fm):
        """Display recipients with checkboxes, handling duplicate detection"""
        # Clear previous checkboxes
        for widget in self.app.recipients_checkbox_frame.winfo_children():
            widget.destroy()
        self.app.recipients_checkboxes.clear()
        
        # Update duplicate state
        self.is_duplicate_signal = is_duplicate
        self.recipients_with_signal = []
        
        if is_duplicate:
            self.recipients_with_signal = self.app.duplicate_manager.get_recipients_with_signal(signal_id, fm)
        
        # Filter recipients if not from manual input
        if hasattr(self.app, 'current_signal_data') and self.app.current_signal_data and \
           self.app.current_signal_data.get('is_manual_input', False):
            filtered_recipients = recipients
        else:
            try:
                filtered_recipients = self.app.recipients_manager.filter_recipients(recipients)
            except Exception:
                filtered_recipients = recipients
        
        # Create checkboxes for each recipient
        for recipient in filtered_recipients:
            # Determine if this recipient should be unchecked (has the signal already)
            has_signal = recipient in self.recipients_with_signal
            default_checked = not has_signal  # Uncheck if they already have it
            
            var = tk.BooleanVar()
            var.set(default_checked)
            
            # Create checkbox with special styling for duplicates
            checkbox = tk.Checkbutton(
                self.app.recipients_checkbox_frame,
                text=recipient,
                variable=var,
                font=('Arial', 10),
                anchor='w',
                fg='gray' if has_signal else 'black'  # Gray out recipients that have it
            )
            checkbox.pack(fill='x', pady=1)
            
            # Add tooltip for recipients that already have the signal
            if has_signal:
                from app.ui.utils.tooltips import create_tooltip
                create_tooltip(checkbox, f"Ο παραλήπτης έχει ήδη αυτό το σήμα")
                
                # Bind event to handle re-checking
                var.trace('w', lambda *args, r=recipient, v=var: self._handle_duplicate_recipient_recheck(r, v))
            
            self.app.recipients_checkboxes.append({
                'recipient': recipient,
                'var': var,
                'checkbox': checkbox,
                'has_signal': has_signal
            })
        
        # Show info message if duplicates were unchecked
        if is_duplicate and self.recipients_with_signal:
            self._show_unchecked_recipients_info()
    
    def _handle_duplicate_recipient_recheck(self, recipient, var):
        """Handle when user re-checks a recipient that already has the signal"""
        if var.get():  # If user checked it
            # This will create a versioned copy when processed
            # Update the checkbox color to indicate it will be processed
            for cb_data in self.app.recipients_checkboxes:
                if cb_data['recipient'] == recipient:
                    cb_data['checkbox'].config(fg='blue')
                    from app.ui.utils.tooltips import create_tooltip
                    create_tooltip(cb_data['checkbox'], f"Θα δημιουργηθεί νέα έκδοση για τον παραλήπτη")
                    break
    
    def _show_duplicate_notification(self, signal_id, fm):
        """Show permanent duplicate notification"""
        # Create a permanent notification label
        notification_frame = tk.Frame(self.app.recipients_checkbox_frame)
        notification_frame.pack(fill='x', pady=5)
        
        serial_number = self.app.duplicate_manager.generate_serial_number(signal_id, fm)
        
        notification_label = tk.Label(
            notification_frame,
            text=f"⚠️ Ανιχνεύθηκε διπλότυπο σήμα (Serial: {serial_number[:8]}...)",
            font=('Arial', 8),
            fg='orange',
            bg='#fff8dc',
            relief='solid',
            borderwidth=1,
            padx=5,
            pady=2
        )
        notification_label.pack(fill='x')
        
        # Note: Notification stays permanently displayed (no auto-removal)
    
    def _show_unchecked_recipients_info(self):
        """Show permanent info about unchecked recipients"""
        info_frame = tk.Frame(self.app.recipients_checkbox_frame)
        info_frame.pack(fill='x', pady=2)
        
        unchecked_count = len(self.recipients_with_signal)
        
        info_label = tk.Label(
            info_frame,
            text=f"ℹ️ {unchecked_count} παραλήπτες αποεπιλέχθηκαν (έχουν ήδη το σήμα)",
            font=('Arial', 8),
            fg='blue',
            bg='#f0f8ff',
            relief='solid',
            borderwidth=1,
            padx=5,
            pady=2
        )
        info_label.pack(fill='x')
        
        # Note: Info stays permanently displayed (no auto-removal)
    
    def clear_downloads_folder(self):
        """Clear the downloads folder and reset signal display"""
        try:
            from app.utils.file_operations import clear_downloads_folder
            
            # Confirm with user
            if messagebox.askyesno("Επιβεβαίωση", 
                                 "Θέλετε να καθαρίσετε όλα τα αρχεία από τον φάκελο downloads;\n\n"
                                 "Αυτό θα διαγράψει το PDF σήματος και όλα τα συνημμένα.",
                                 icon='warning'):
                
                # Clear the downloads folder
                clear_downloads_folder()
                
                # Reset signal display
                self.app.clear_signal_display()
                
                # Reset current signal data
                self.app.current_signal_data = None
                
                # Update status
                self.app.progress_manager.global_message("Ο φάκελος downloads καθαρίστηκε - Έτοιμο για νέο σήμα")
                
                # Show success message
                messagebox.showinfo("Επιτυχία", "Ο φάκελος downloads καθαρίστηκε επιτυχώς!")
                
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Σφάλμα κατά τον καθαρισμό του φακέλου downloads:\n{str(e)}")
