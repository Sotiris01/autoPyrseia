#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
USB Extraction Tab for autoPyrseia
"""

import tkinter as tk
from tkinter import ttk
import os
from pathlib import Path
from app.ui.widgets.folder_button import FolderIconButton
from app.utils.path_manager import get_path_manager


class USBExtractionTab:
    """USB extraction tab component"""
    
    def __init__(self, notebook, app):
        self.app = app
        self.notebook = notebook
        self.frame = ttk.Frame(notebook)
        self.notebook.add(self.frame, text="Εξαγωγή σε USB")
        
        # Auto-save timers to prevent excessive file writes
        self.username_save_timer = None
        self.file_number_save_timer = None
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create USB extraction tab widgets"""
        # Extraction settings
        settings_frame = ttk.LabelFrame(self.frame, text="Ρυθμίσεις Εξαγωγής", padding=10)
        settings_frame.pack(fill='x', padx=10, pady=5)
        
        self._create_settings_section(settings_frame)
        
        # Recipients selection
        extraction_frame = ttk.LabelFrame(self.frame, text="Επιλογή Παραληπτών για Εξαγωγή", padding=10)
        extraction_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self._create_recipients_section(extraction_frame)
        
        # Extraction controls
        self._create_extraction_controls()
    
    def _create_settings_section(self, parent):
        """Create extraction settings section"""
        # Username (Combobox for typing + dropdown selection)
        tk.Label(parent, text="Όνομα Χρήστη:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.app.username_combobox = ttk.Combobox(parent, textvariable=self.app.username, width=28)
        self.app.username_combobox.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        # Populate combobox with username suggestions
        self._update_username_suggestions()
        
        # File Number
        tk.Label(parent, text="Αριθμός Φακέλου:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.app.file_number_entry = tk.Entry(parent, textvariable=self.app.file_number, width=30)
        self.app.file_number_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        # Auto-save functionality
        self.app.username.trace_add('write', self._auto_save_username)
        self.app.file_number.trace_add('write', self._auto_save_file_number)
        
        # Tooltips
        self.app.create_tooltip(self.app.username_combobox, "Εισάγετε ή επιλέξτε όνομα χρήστη - Αυτόματη αποθήκευση - Παλιά ονόματα (>5 ημέρες) αφαιρούνται αυτόματα")
        self.app.create_tooltip(self.app.file_number_entry, "Αριθμός φακέλου - Αυτόματη αποθήκευση - Αυξάνεται μετά από κάθε εξαγωγή")
    
    def _create_recipients_section(self, parent):
        """Create recipients selection section"""
        # Frame for checkboxes with scrollbar
        self.app.extraction_canvas = tk.Canvas(parent, height=200)
        extraction_scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.app.extraction_canvas.yview)
        self.app.extraction_checkbox_frame = tk.Frame(self.app.extraction_canvas)
        
        self.app.extraction_checkbox_frame.bind(
            "<Configure>",
            lambda e: self.app.extraction_canvas.configure(scrollregion=self.app.extraction_canvas.bbox("all"))
        )
        
        self.app.extraction_canvas.create_window((0, 0), window=self.app.extraction_checkbox_frame, anchor="nw")
        self.app.extraction_canvas.configure(yscrollcommand=extraction_scrollbar.set)
        
        self.app.extraction_canvas.pack(side='left', fill='x', expand=True)
        extraction_scrollbar.pack(side='right', fill='y')
    
    def _create_extraction_controls(self):
        """Create extraction control buttons"""
        extract_frame = tk.Frame(self.frame)
        extract_frame.pack(side='bottom', fill='x', padx=10, pady=10)
        
        # Control buttons
        control_buttons = tk.Frame(extract_frame)
        control_buttons.pack(fill='x', pady=(0, 10))
        
        refresh_button = tk.Button(control_buttons, text="Ανανέωση Λίστας", 
                 command=self.refresh_extraction_list, bg='#95a5a6', fg='white', 
                 font=('Arial', 9))
        refresh_button.pack(side='left', padx=5)
        
        # Undo button
        self.app.undo_button = tk.Button(control_buttons, text="ΑΝΑΙΡΕΣΗ ΤΕΛΕΥΤΑΙΑΣ ΕΞΑΓΩΓΗΣ", 
                                        command=self.undo_last_extraction, bg='#e74c3c', fg='white', 
                                        font=('Arial', 9, 'bold'), state='disabled')
        self.app.undo_button.pack(side='left', padx=15)
        
        # ΑΝΕΠΙΣΗΜΑ button
        self.app.unofficial_button = tk.Button(control_buttons, text="ΑΝΕΠΙΣΗΜΑ", 
                                              command=self.toggle_unofficial_mode, 
                                              bg='#95a5a6', fg='white', font=('Arial', 9, 'bold'),
                                              width=15, height=1)
        self.app.unofficial_button.pack(side='left', padx=5)
        
        # Tooltips
        self.app.create_tooltip(refresh_button, "Ανανέωση της λίστας παραληπτών (F5)")
        self.app.create_tooltip(self.app.undo_button, "Αναίρεση της τελευταίας εξαγωγής")
        self.app.create_tooltip(self.app.unofficial_button, "Λειτουργία ΑΝΕΠΙΣΗΜΑ: Δεν αυξάνει αριθμό φακέλου")
        
        # Extraction status
        status_frame = tk.Frame(extract_frame)
        status_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(status_frame, text="Κατάσταση Τελευταίας Εξαγωγής:", 
                font=('Arial', 10, 'bold')).pack(side='left')
        
        self.app.extraction_status_label = tk.Label(status_frame, text="Καμία εξαγωγή ακόμη", 
                                                   font=('Arial', 10), fg='gray')
        self.app.extraction_status_label.pack(side='left', padx=(10, 0))
        
        # Extract button
        self.app.extract_button = tk.Button(extract_frame, text="Εξαγωγή σε USB", 
                                           command=self.extract_to_usb, bg='#9b59b6', fg='white', 
                                           font=('Arial', 11, 'bold'), height=2)
        self.app.extract_button.pack(pady=5)
        
        self.app.create_tooltip(self.app.extract_button, "Εξαγωγή επιλεγμένων παραληπτών σε USB (Enter)")
    
    def refresh_extraction_list(self):
        """Refresh extraction list with checkboxes and folder buttons"""
        # Scan for JSON files before refreshing
        try:
            self.app.signal_manager.scan_and_generate_missing_json_files()
        except Exception as e:
            print(f"Σφάλμα στη σάρωση JSON κατά την ανανέωση: {e}")
        
        # Update username suggestions as well
        self._update_username_suggestions()
        
        # Clear previous checkboxes
        for widget in self.app.extraction_checkbox_frame.winfo_children():
            widget.destroy()
        self.app.extraction_checkboxes.clear()
        
        # Load available recipients from DATA folder
        path_manager = get_path_manager()
        data_path = path_manager.data_folder
        
        if data_path.exists():
            recipients = []
            for recipient_folder in data_path.iterdir():
                if recipient_folder.is_dir():
                    recipients.append(recipient_folder.name)
            
            # Create checkboxes for each recipient
            for recipient in sorted(recipients):
                var = tk.BooleanVar()
                
                # Get signal count for this recipient
                signal_count = 0
                try:
                    signals = self.app.signal_manager.get_recipient_signals(recipient)
                    signal_count = len(signals) if signals else 0
                except:
                    signal_count = 0
                
                # Create a frame to hold checkbox and folder button
                recipient_frame = tk.Frame(self.app.extraction_checkbox_frame)
                recipient_frame.pack(fill='x', padx=5, pady=1)
                
                # Create checkbox with signal count
                display_text = f"{recipient} ({signal_count} σήματα)"
                checkbox = tk.Checkbutton(
                    recipient_frame,
                    text=display_text,
                    variable=var,
                    font=('Arial', 10),
                    anchor='w',
                    command=lambda r=recipient, v=var, cb=None: self._on_recipient_selection_changed(r, v, cb)
                )
                checkbox.pack(side='left', fill='x', expand=True)
                
                # Update the lambda to pass the checkbox reference
                checkbox.config(command=lambda r=recipient, v=var, cb=checkbox: self._on_recipient_selection_changed(r, v, cb))
                
                # Create folder icon button
                folder_button = FolderIconButton.create(
                    recipient_frame, 
                    recipient, 
                    status_callback=lambda msg: self.app.progress_manager.global_message(msg)
                )
                folder_button.pack(side='right', padx=(5, 0))
                
                # Add keyboard navigation and context menu to checkbox
                self._setup_checkbox_bindings(checkbox, var, recipient)
                
                self.app.extraction_checkboxes.append({
                    'recipient': recipient,
                    'var': var,
                    'checkbox': checkbox,
                    'frame': recipient_frame,
                    'folder_button': folder_button
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
        context_menu.add_command(label="Επιλογή Όλων", command=lambda: self.select_all_extraction_checkboxes(True))
        context_menu.add_command(label="Αποεπιλογή Όλων", command=lambda: self.select_all_extraction_checkboxes(False))
        context_menu.add_separator()
        context_menu.add_command(label="Άνοιγμα Φακέλου", 
                               command=lambda r=recipient: self._open_recipient_folder(r))
        
        def show_context_menu(event):
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        
        checkbox.bind('<Button-3>', show_context_menu)
    
    def _on_recipient_selection_changed(self, recipient_name, var, checkbox):
        """Handle recipient selection change to update visual styling"""
        try:
            if var.get():  # Selected
                # Make selected recipient more noticeable
                checkbox.config(
                    font=('Arial', 12, 'bold'),  # Larger, bold font
                    bg='#e3f2fd',  # Light blue highlight background
                    fg='#1976d2',  # Dark blue text
                    activebackground='#bbdefb',  # Slightly darker when active
                    selectcolor='#2196f3'  # Blue checkbox color
                )
            else:  # Deselected
                # Return to normal styling
                checkbox.config(
                    font=('Arial', 10),  # Normal font
                    bg='SystemButtonFace',  # Default background
                    fg='SystemButtonText',  # Default text color
                    activebackground='SystemButtonFace',  # Default active background
                    selectcolor='SystemWindow'  # Default checkbox color
                )
        except Exception as e:
            print(f"Error updating checkbox styling: {e}")
    
    def _open_recipient_folder(self, recipient_name):
        """Open recipient folder in File Explorer"""
        try:
            import os
            path_manager = get_path_manager()
            folder_path = path_manager.get_recipient_folder(recipient_name)
            if folder_path.exists() and folder_path.is_dir():
                os.startfile(str(folder_path))
                self.app.progress_manager.global_message(f"Άνοιξε ο φάκελος: {recipient_name}")
            else:
                from tkinter import messagebox
                messagebox.showwarning("Φάκελος Δεν Βρέθηκε", 
                                     f"Ο φάκελος '{recipient_name}' δεν βρέθηκε στο DATA/")
                self.app.progress_manager.global_message(f"Ο φάκελος {recipient_name} δεν υπάρχει")
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Σφάλμα", f"Αδυναμία ανοίγματος φακέλου: {str(e)}")
            self.app.progress_manager.global_message(f"Σφάλμα ανοίγματος φακέλου: {recipient_name}")
    
    def select_all_extraction_checkboxes(self, state):
        """Select or deselect all extraction checkboxes"""
        for checkbox_data in self.app.extraction_checkboxes:
            checkbox_data['var'].set(state)
            # Trigger visual feedback for each checkbox
            self._on_recipient_selection_changed(
                checkbox_data['recipient'], 
                checkbox_data['var'], 
                checkbox_data['checkbox']
            )
    
    def get_selected_extraction_recipients(self):
        """Get selected recipients for extraction"""
        selected = []
        for checkbox_data in self.app.extraction_checkboxes:
            if checkbox_data['var'].get():
                selected.append(checkbox_data['recipient'])
        return selected
    
    def extract_to_usb(self):
        """Extract selected recipients to USB"""
        import threading
        from tkinter import filedialog, messagebox
        
        # Check that recipients are selected
        selected_recipients = self.get_selected_extraction_recipients()
        if not selected_recipients:
            messagebox.showwarning("Καμία Επιλογή", "Παρακαλώ επιλέξτε τουλάχιστον έναν παραλήπτη για εξαγωγή.")
            return
        
        # Check username
        username = self.app.username.get().strip()
        if not username:
            self.app.progress_manager.global_message("Εισάγετε όνομα χρήστη")
            return
        
        # Get file number
        try:
            file_number = int(self.app.file_number.get())
        except ValueError:
            self.app.progress_manager.global_message("Μη έγκυρος αριθμός φακέλου")
            return
        
        # Always ask user to select USB path
        usb_path = filedialog.askdirectory(title="Επιλογή Φακέλου USB για Εξαγωγή")
        if not usb_path:
            self.app.progress_manager.global_message("Ακυρώθηκε η επιλογή φακέλου USB")
            return
        
        # Start USB extraction operation
        self.app.progress_manager.start_operation("usb_extraction", "Εξαγωγή σε USB...", 5)
        
        def extract_in_thread():
            try:
                # Scan for JSON files only for selected recipients
                try:
                    self.app.signal_manager.scan_and_generate_missing_json_files(selected_recipients)
                except Exception as e:
                    print(f"Σφάλμα στη σάρωση JSON πριν την εξαγωγή: {e}")
                
                self.app.root.after(0, lambda: self.app.progress_manager.update_progress("usb_extraction", 15, "Προετοιμασία εξαγωγής..."))
                
                # Check if unofficial mode is enabled
                is_unofficial = self.app.unofficial_mode.get()
                
                if is_unofficial:
                    self.app.root.after(400, lambda: self.app.progress_manager.update_progress("usb_extraction", 30, "ΑΝΕΠΙΣΗΜΗ εξαγωγή - Μόνο αρχεία σημάτων..."))
                else:
                    self.app.root.after(400, lambda: self.app.progress_manager.update_progress("usb_extraction", 30, "Δημιουργία αρχείων Excel..."))
                
                success, result_data = self.app.usb_extractor.extract_to_usb(
                    usb_path, selected_recipients, file_number, username, is_unofficial
                )
                
                self.app.root.after(0, lambda: self.app.progress_manager.smooth_progress("usb_extraction", 80, 200))
                self.app.root.after(200, lambda: self.app.progress_manager.update_message("usb_extraction", "Αντιγραφή αρχείων..."))
                
                if success:
                    # Only increment file number if NOT in unofficial mode
                    if not is_unofficial:
                        self.app.config_manager.increment_file_number()
                        self.app.file_number.set(str(self.app.config_manager.get_next_file_number()))
                        
                    # Save username
                    self.app.config_manager.set_username(username)
                    
                    extraction_type = "ΑΝΕΠΙΣΗΜΗ" if is_unofficial else "κανονική"
                    
                    # Add extraction type info to result_data for undo handling
                    def handle_success_with_mode(result):
                        if result and not is_unofficial:
                            result['is_unofficial'] = False
                        elif result and is_unofficial:
                            result['is_unofficial'] = True
                        self.extraction_completed(result)
                        # Complete progress after extraction_completed
                        self.app.progress_manager.complete_operation("usb_extraction", f"Ολοκλήρωση {extraction_type} εξαγωγής...")
                        # Reset progress bar to 0% after 2 seconds
                        self.app.root.after(2000, lambda: self.app.progress_manager.reset_progress("usb_extraction", "Έτοιμο - Αναμονή για νέο σήμα..."))
                    
                    self.app.root.after(400, lambda: handle_success_with_mode(result_data))
                else:
                    self.app.root.after(0, lambda: self.extraction_completed(None))
                    # Reset progress bar to 0% after failure
                    self.app.root.after(2000, lambda: self.app.progress_manager.reset_progress("usb_extraction", "Έτοιμο - Αναμονή για νέο σήμα..."))
                
            except Exception as e:
                print(f"Σφάλμα εξαγωγής: {e}")
                self.app.root.after(0, lambda: self.extraction_completed(None))
                self.app.root.after(0, lambda: self.app.progress_manager.reset_progress("usb_extraction", f"Σφάλμα: {str(e)}"))
                # Reset to ready state after 3 seconds
                self.app.root.after(3000, lambda: self.app.progress_manager.reset_progress("usb_extraction", "Έτοιμο - Αναμονή για νέο σήμα..."))
        
        threading.Thread(target=extract_in_thread, daemon=True).start()
    
    def extraction_completed(self, result_data):
        """Completion of extraction with status display"""
        # Store extraction data for undo functionality
        self.app.last_extraction_data = result_data
        
        # Processing completed successfully
        if result_data:
            try:
                is_unofficial = result_data.get('is_unofficial', False)
                
                # Auto-disable unofficial mode after successful unofficial extraction
                if is_unofficial and self.app.unofficial_mode.get():
                    self.app.unofficial_mode.set(False)
                    self.app.unofficial_button.config(bg='#95a5a6', text="ΑΝΕΠΙΣΗΜΑ")
                    self.app.status_bar.update_status("Ανεπίσημη εξαγωγή ολοκληρώθηκε - Λειτουργία επαναφέρθηκε σε κανονική")
                
                extracted_recipients = result_data.get('extracted_recipients', [])
                
                # Process each recipient extraction
                for recipient_data in extracted_recipients:
                    recipient_name = recipient_data.get('name', 'Unknown')
                    # Fix: signals is a list, get the count
                    signals = recipient_data.get('signals', [])
                    signal_count = len(signals) if signals else 0
                    
                    # Add to history
                    if hasattr(self.app, 'history_tab'):
                        # Get the file number from result_data
                        file_number = result_data.get('file_number')
                        self.app.history_tab.add_extracted_recipient(recipient_name, signal_count, file_number)
                    
                    # Build backup path
                    backup_path = os.path.join("BACK UP DATA", recipient_name)
                    
            except Exception as e:
                import traceback
                traceback.print_exc()
        else:
            # No result_data - skipping processing
            pass
        
        # Refresh extraction list
        self.refresh_extraction_list()
        
        # Update status display
        if result_data:
            is_unofficial_extraction = result_data.get('is_unofficial', False)
            if is_unofficial_extraction:
                self.app.extraction_status_label.config(text="✓ Επιτυχής ΑΝΕΠΙΣΗΜΗ εξαγωγή", fg='orange', font=('Arial', 10, 'bold'))
            else:
                self.app.extraction_status_label.config(text="✓ Επιτυχής εξαγωγή", fg='green', font=('Arial', 10, 'bold'))
            
            # Enable undo for both official and unofficial extractions
            self.app.undo_button.config(state='normal')
        else:
            self.app.extraction_status_label.config(text="✗ Αποτυχία εξαγωγής", fg='red', font=('Arial', 10, 'bold'))
        
        # No additional status update needed - progress manager handles it
    
    def undo_last_extraction(self):
        """Undo last extraction"""
        import threading
        from tkinter import messagebox
        
        if not self.app.last_extraction_data:
            self.app.progress_manager.global_message("Δεν υπάρχει εξαγωγή για αναίρεση")
            return
        
        # Confirmation
        is_unofficial_extraction = self.app.last_extraction_data.get('is_unofficial', False)
        
        if is_unofficial_extraction:
            confirmation_text = ("Είστε σίγουροι ότι θέλετε να αναιρέσετε την τελευταία ΑΝΕΠΙΣΗΜΗ εξαγωγή?\n\n"
                                "Αυτή η ενέργεια θα:\n"
                                "• Επαναφέρει τα σήματα στο φάκελο DATA\n"
                                "• Διαγράψει τα αρχεία από το USB\n"
                                "• Διαγράψει τα backup αρχεία")
        else:
            confirmation_text = ("Είστε σίγουροι ότι θέλετε να αναιρέσετε την τελευταία εξαγωγή?\n\n"
                                "Αυτή η ενέργεια θα:\n"
                                "• Επαναφέρει τα σήματα στο φάκελο DATA\n"
                                "• Διαγράψει τα αρχεία από το USB\n"
                                "• Διαγράψει τα backup αρχεία\n"
                                "• Μειώσει τον αριθμό φακέλου")
        
        if not messagebox.askyesno("Επιβεβαίωση Αναίρεσης", confirmation_text):
            return
        
        # Start undo operation
        self.app.progress_manager.start_operation("usb_undo", "Αναίρεση εξαγωγής...", 10)
        
        def undo_in_thread():
            try:
                success, message = self.app.usb_extractor.undo_extraction(self.app.last_extraction_data)
                
                self.app.root.after(0, lambda: self.app.progress_manager.smooth_progress("usb_undo", 80, 300))
                self.app.root.after(300, lambda: self.app.progress_manager.update_message("usb_undo", "Ολοκλήρωση αναίρεσης..."))
                
                if success:
                    # Only decrement file number if it was NOT an unofficial extraction
                    if not is_unofficial_extraction:
                        self.app.config_manager.decrement_file_number()
                        self.app.file_number.set(str(self.app.config_manager.get_next_file_number()))
                    
                    # Clear last extraction data and disable undo
                    self.app.last_extraction_data = None
                    self.app.undo_button.config(state='disabled')
                    self.app.extraction_status_label.config(text="Αναίρεση ολοκληρώθηκε", fg='blue', font=('Arial', 10, 'bold'))
                    
                    # Refresh lists
                    self.refresh_extraction_list()
                    
                    self.app.root.after(500, lambda: self.app.progress_manager.complete_operation("usb_undo", f"Αναίρεση επιτυχής: {message}"))
                else:
                    self.app.root.after(0, lambda: self.app.progress_manager.reset_progress("usb_undo", f"Σφάλμα αναίρεσης: {message}"))
                
            except Exception as e:
                self.app.root.after(0, lambda: self.app.progress_manager.reset_progress("usb_undo", f"Σφάλμα αναίρεσης: {str(e)}"))
        
        threading.Thread(target=undo_in_thread, daemon=True).start()
    
    def toggle_unofficial_mode(self):
        """Toggle unofficial mode"""
        is_unofficial = self.app.unofficial_mode.get()
        
        if not is_unofficial:
            # Enable unofficial mode
            self.app.unofficial_mode.set(True)
            self.app.unofficial_button.config(bg='#e74c3c', text="ΑΝΕΠΙΣΗΜΑ ✓")
            self.app.status_bar.update_status("Λειτουργία ΑΝΕΠΙΣΗΜΑ ΕΝΕΡΓΟΠΟΙΗΘΗΚΕ - Δεν θα αυξηθεί ο αριθμός φακέλου")
        else:
            # Disable unofficial mode  
            self.app.unofficial_mode.set(False)
            self.app.unofficial_button.config(bg='#95a5a6', text="ΑΝΕΠΙΣΗΜΑ")
            self.app.status_bar.update_status("Λειτουργία ΑΝΕΠΙΣΗΜΑ απενεργοποιήθηκε - Κανονική λειτουργία")
    
    def _update_username_suggestions(self):
        """Update combobox with username suggestions from history"""
        try:
            suggestions = self.app.config_manager.get_username_suggestions()
            self.app.username_combobox['values'] = suggestions
        except Exception as e:
            print(f"Σφάλμα ενημέρωσης προτάσεων χρήστη: {e}")
            self.app.username_combobox['values'] = []
    
    def _auto_save_username(self, *args):
        """Auto-save username changes with delay to prevent excessive writes"""
        # Cancel previous timer if user is still typing
        if self.username_save_timer is not None:
            self.app.root.after_cancel(self.username_save_timer)
        
        # Schedule save after 2000ms (2 seconds) delay
        self.username_save_timer = self.app.root.after(2000, self._save_username)
    
    def _save_username(self):
        """Actually save the username to config and update suggestions"""
        try:
            username = self.app.username.get().strip()
            # Save even empty usernames to clear the field
            self.app.config_manager.set_username(username)
            
            # Update suggestions after saving (in case of new username)
            if username:
                self._update_username_suggestions()
            
            # Reset timer
            self.username_save_timer = None
            
            # Optional: Show brief visual feedback (without overwhelming status bar)
            if hasattr(self.app, 'status_bar') and username:
                # Show feedback only for a short time
                self.app.root.after(0, lambda: self.app.status_bar.update_status(f"💾 Αποθήκευση: {username}"))
                self.app.root.after(2000, lambda: self.app.status_bar.update_status("Έτοιμο"))
        except Exception as e:
            print(f"Σφάλμα αποθήκευσης username: {e}")
            self.username_save_timer = None
    
    def _auto_save_file_number(self, *args):
        """Auto-save file number changes with delay to prevent excessive writes"""
        # Cancel previous timer if user is still typing
        if self.file_number_save_timer is not None:
            self.app.root.after_cancel(self.file_number_save_timer)
        
        # Schedule save after 500ms delay
        self.file_number_save_timer = self.app.root.after(500, self._save_file_number)
    
    def _save_file_number(self):
        """Actually save the file number to config"""
        try:
            file_number_str = self.app.file_number.get().strip()
            if file_number_str and file_number_str.isdigit():
                file_number = int(file_number_str)
                # Only save valid positive numbers
                if file_number > 0:
                    self.app.config_manager.set_file_number(file_number)
                    
                    # Optional: Show brief visual feedback
                    if hasattr(self.app, 'status_bar'):
                        self.app.root.after(0, lambda: self.app.status_bar.update_status(f"💾 Αποθήκευση: Φάκελος #{file_number}"))
                        self.app.root.after(2000, lambda: self.app.status_bar.update_status("Έτοιμο"))
            
            # Reset timer
            self.file_number_save_timer = None
        except Exception as e:
            print(f"Σφάλμα αποθήκευσης file number: {e}")
            self.file_number_save_timer = None
