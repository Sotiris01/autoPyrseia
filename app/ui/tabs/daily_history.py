"""
Multi-Day Daily History Tab - Navigation through multiple days
"""
import tkinter as tk
from tkinter import ttk
import os
import subprocess
import platform
from datetime import datetime


class DailyHistoryTab:
    """Multi-day history tab with navigation controls"""
    
    def __init__(self, notebook, app):
        self.app = app
        self.notebook = notebook
        
        # Create main frame
        self.frame = ttk.Frame(notebook)
        self.notebook.add(self.frame, text="Ιστορικό")
        
        # Create navigation frame at the top
        self._create_navigation_frame()
        
        # Create sub-notebook for two sub-tabs
        self.sub_notebook = ttk.Notebook(self.frame)
        self.sub_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Configure smaller style for sub-tabs
        style = ttk.Style()
        style.configure('Small.TNotebook.Tab', 
                       font=('TkDefaultFont', 8),  # Smaller font
                       padding=[8, 4])             # Smaller padding
        self.sub_notebook.configure(style='Small.TNotebook')
        
        # Create sub-tabs
        self._create_processed_signals_tab()
        self._create_extracted_recipients_tab()
        
        # Initial refresh
        self.refresh_all()
    
    def _create_navigation_frame(self):
        """Create navigation controls frame"""
        nav_frame = ttk.Frame(self.frame)
        nav_frame.pack(fill='x', padx=5, pady=5)
        
        # Left side - navigation buttons
        left_frame = ttk.Frame(nav_frame)
        left_frame.pack(side='left')
        
        self.prev_btn = ttk.Button(left_frame, text="<-", width=3, 
                                  command=self._navigate_previous)
        self.prev_btn.pack(side='left', padx=2)
        
        self.today_btn = ttk.Button(left_frame, text="TODAY", width=8, 
                                   command=self._navigate_today)
        self.today_btn.pack(side='left', padx=2)
        
        self.next_btn = ttk.Button(left_frame, text="->", width=3, 
                                  command=self._navigate_next)
        self.next_btn.pack(side='left', padx=2)
        
        # Center - current date display
        self.date_label = ttk.Label(nav_frame, text="", 
                                   font=('Arial', 11, 'bold'))
        self.date_label.pack(side='left', padx=20)
        
        # Right side - info
        info_label = ttk.Label(nav_frame, text="Πλοήγηση στο ιστορικό ημερών", 
                              font=('Arial', 9), foreground='gray')
        info_label.pack(side='right')
        
        # Update display
        self._update_navigation_display()
    
    def _navigate_previous(self):
        """Navigate to previous day with history"""
        if hasattr(self.app, 'daily_history'):
            if self.app.daily_history.navigate_to_previous_day():
                self._update_navigation_display()
                self.refresh_all()
    
    def _navigate_next(self):
        """Navigate to next day with history"""
        if hasattr(self.app, 'daily_history'):
            if self.app.daily_history.navigate_to_next_day():
                self._update_navigation_display()
                self.refresh_all()
    
    def _navigate_today(self):
        """Navigate to today's history"""
        if hasattr(self.app, 'daily_history'):
            self.app.daily_history.navigate_to_today()
            self._update_navigation_display()
            self.refresh_all()
    
    def _update_navigation_display(self):
        """Update the navigation display"""
        if hasattr(self.app, 'daily_history'):
            current_date = self.app.daily_history.get_current_viewing_date()
            available_dates = self.app.daily_history.get_available_dates()
            
            # Format date for display
            try:
                date_obj = datetime.strptime(current_date, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%d/%m/%Y")
                
                # Check if it's today
                today = datetime.now().strftime("%Y-%m-%d")
                if current_date == today:
                    formatted_date += " (Σήμερα)"
                    
            except:
                formatted_date = current_date
            
            self.date_label.config(text=formatted_date)
            
            # Enable/disable navigation buttons
            current_index = available_dates.index(current_date) if current_date in available_dates else -1
            
            # Previous button (older dates)
            self.prev_btn.config(state='normal' if current_index < len(available_dates) - 1 else 'disabled')
            
            # Next button (newer dates) 
            self.next_btn.config(state='normal' if current_index > 0 else 'disabled')
            
            # Today button
            today_date = datetime.now().strftime("%Y-%m-%d")
            self.today_btn.config(state='normal' if current_date != today_date else 'disabled')
    
    def _create_processed_signals_tab(self):
        """Create processed signals sub-tab"""
        self.processed_frame = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(self.processed_frame, text="Επεξεργασμένα Σήματα")
        
        # Title and count
        title_frame = ttk.Frame(self.processed_frame)
        title_frame.pack(fill='x', pady=5)
        
        self.processed_title_label = ttk.Label(title_frame, text="Σήματα που επεξεργάστηκαν:", 
                 font=('Arial', 12, 'bold'))
        self.processed_title_label.pack(side='left')
        
        self.processed_count_label = ttk.Label(title_frame, text="(0)", 
                                             font=('Arial', 10), foreground='gray')
        self.processed_count_label.pack(side='left', padx=(10, 0))
        
        # Instruction label
        ttk.Label(title_frame, text="💡 Κάντε διπλό κλικ για άνοιγμα φακέλου σήματος", 
                 font=('Arial', 9), foreground='blue').pack(side='right')
        
        # Treeview with columns
        tree_frame = ttk.Frame(self.processed_frame)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Define columns
        columns = ('time', 'signal_id', 'fm', 'recipients')
        self.processed_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configure column headings and widths
        self.processed_tree.heading('time', text='Ώρα')
        self.processed_tree.heading('signal_id', text='ID Σήματος')
        self.processed_tree.heading('fm', text='FM')
        self.processed_tree.heading('recipients', text='Παραλήπτες')
        
        self.processed_tree.column('time', width=80, minwidth=80, anchor='center')
        self.processed_tree.column('signal_id', width=150, minwidth=100, anchor='center')
        self.processed_tree.column('fm', width=200, minwidth=150, anchor='w')
        self.processed_tree.column('recipients', width=300, minwidth=200, anchor='w')
        
        # Configure alternating row colors
        self.processed_tree.tag_configure('oddrow', background='#f0f0f0')
        self.processed_tree.tag_configure('evenrow', background='white')
        
        # Scrollbar for treeview
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.processed_tree.yview)
        self.processed_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Pack treeview and scrollbar
        self.processed_tree.pack(side='left', fill='both', expand=True)
        tree_scrollbar.pack(side='right', fill='y')
        
        # Bind double-click event to open signal folder
        self.processed_tree.bind('<Double-1>', self._on_processed_signal_click)
    
    def _create_extracted_recipients_tab(self):
        """Create extracted recipients sub-tab"""
        self.extracted_frame = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(self.extracted_frame, text="Εξαγωγές USB")
        
        # Title and count
        title_frame = ttk.Frame(self.extracted_frame)
        title_frame.pack(fill='x', pady=5)
        
        self.extracted_title_label = ttk.Label(title_frame, text="Εξαγωγές που έγιναν:", 
                 font=('Arial', 12, 'bold'))
        self.extracted_title_label.pack(side='left')
        
        self.extracted_count_label = ttk.Label(title_frame, text="(0)", 
                                             font=('Arial', 10), foreground='gray')
        self.extracted_count_label.pack(side='left', padx=(10, 0))
        
        # Instruction label
        ttk.Label(title_frame, text="💡 Κάντε διπλό κλικ για άνοιγμα φακέλου backup", 
                 font=('Arial', 9), foreground='blue').pack(side='right')
        
        # Treeview with columns
        tree_frame2 = ttk.Frame(self.extracted_frame)
        tree_frame2.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Define columns
        columns2 = ('time', 'recipient', 'signal_count')
        self.extracted_tree = ttk.Treeview(tree_frame2, columns=columns2, show='headings', height=15)
        
        # Configure column headings and widths
        self.extracted_tree.heading('time', text='Ώρα')
        self.extracted_tree.heading('recipient', text='Παραλήπτης')
        self.extracted_tree.heading('signal_count', text='Αριθμός Σημάτων')
        
        self.extracted_tree.column('time', width=100, minwidth=80, anchor='center')
        self.extracted_tree.column('recipient', width=400, minwidth=300, anchor='w')
        self.extracted_tree.column('signal_count', width=150, minwidth=120, anchor='center')
        
        # Configure alternating row colors
        self.extracted_tree.tag_configure('oddrow', background='#f0f0f0')
        self.extracted_tree.tag_configure('evenrow', background='white')
        
        # Scrollbar for treeview
        tree_scrollbar2 = ttk.Scrollbar(tree_frame2, orient='vertical', command=self.extracted_tree.yview)
        self.extracted_tree.configure(yscrollcommand=tree_scrollbar2.set)
        
        # Pack treeview and scrollbar
        self.extracted_tree.pack(side='left', fill='both', expand=True)
        tree_scrollbar2.pack(side='right', fill='y')
        
        # Bind double-click event to open recipient backup folder
        self.extracted_tree.bind('<Double-1>', self._on_extracted_recipient_click)
    
    def refresh_processed_signals(self):
        """Refresh processed signals display for current viewing date"""
        if not hasattr(self.app, 'daily_history'):
            return
        
        # Clear treeview
        for item in self.processed_tree.get_children():
            self.processed_tree.delete(item)
        
        # Get processed signals for current viewing date
        processed = self.app.daily_history.get_processed_signals()
        
        # Update count and title
        self.processed_count_label.config(text=f"({len(processed)})")
        
        # Update title based on viewing date
        current_date = self.app.daily_history.get_current_viewing_date()
        today = datetime.now().strftime("%Y-%m-%d")
        
        if current_date == today:
            self.processed_title_label.config(text="Σήματα που επεξεργάστηκαν σήμερα:")
        else:
            try:
                date_obj = datetime.strptime(current_date, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%d/%m/%Y")
                self.processed_title_label.config(text=f"Σήματα που επεξεργάστηκαν στις {formatted_date}:")
            except:
                self.processed_title_label.config(text=f"Σήματα που επεξεργάστηκαν στις {current_date}:")
        
        # Add entries (newest first)
        for idx, entry in enumerate(reversed(processed)):
            time_str = entry.get('time', '')
            signal_id = entry.get('signal_id', 'N/A')
            fm = entry.get('fm', 'N/A')
            recipients = entry.get('recipients', 'N/A')
            
            # Handle recipients list display
            if isinstance(recipients, list):
                recipients_str = ', '.join(recipients)
            else:
                recipients_str = str(recipients)
            
            # Determine row tag for alternating colors
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            
            # Insert into treeview
            self.processed_tree.insert('', 'end', values=(time_str, signal_id, fm, recipients_str), tags=(tag,))
    
    def refresh_extracted_recipients(self):
        """Refresh extracted recipients display for current viewing date"""
        if not hasattr(self.app, 'daily_history'):
            return
        
        # Clear treeview
        for item in self.extracted_tree.get_children():
            self.extracted_tree.delete(item)
        
        # Get extracted recipients for current viewing date
        extracted = self.app.daily_history.get_extracted_recipients()
        
        # Update count
        self.extracted_count_label.config(text=f"({len(extracted)})")
        
        # Update title based on viewing date
        current_date = self.app.daily_history.get_current_viewing_date()
        today = datetime.now().strftime("%Y-%m-%d")
        
        if current_date == today:
            self.extracted_title_label.config(text="Εξαγωγές που έγιναν σήμερα:")
        else:
            try:
                date_obj = datetime.strptime(current_date, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%d/%m/%Y")
                self.extracted_title_label.config(text=f"Εξαγωγές που έγιναν στις {formatted_date}:")
            except:
                self.extracted_title_label.config(text=f"Εξαγωγές που έγιναν στις {current_date}:")
        
        # Add entries (newest first)
        for idx, entry in enumerate(reversed(extracted)):
            time_str = entry.get('time', '')
            recipient = entry.get('recipient', 'N/A')
            signal_count = entry.get('signal_count', 0)
            
            # Determine row tag for alternating colors
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            
            # Insert into treeview
            self.extracted_tree.insert('', 'end', values=(time_str, recipient, f"{signal_count} σήματα"), tags=(tag,))
    
    def refresh_all(self):
        """Refresh both sub-tabs and navigation"""
        self._update_navigation_display()
        self.refresh_processed_signals()
        self.refresh_extracted_recipients()
    
    def add_processed_signal(self, signal_id, fm, recipients):
        """Add processed signal and refresh display"""
        if hasattr(self.app, 'daily_history'):
            self.app.daily_history.add_processed_signal(signal_id, fm, recipients)
            self.refresh_processed_signals()
    
    def add_extracted_recipient(self, recipient, signal_count, file_number=None):
        """Add extracted recipient and refresh display"""
        if hasattr(self.app, 'daily_history'):
            self.app.daily_history.add_extracted_recipient(recipient, signal_count, file_number)
            self.refresh_extracted_recipients()
    
    def _on_processed_signal_click(self, event):
        """Handle double-click on processed signal - open all recipients' signal folders from DATA"""
        selection = self.processed_tree.selection()
        if not selection:
            return
        
        # Get the selected item values
        item = self.processed_tree.item(selection[0])
        values = item['values']
        
        if len(values) >= 4:
            signal_id = values[1]  # Signal ID column
            recipients_str = values[3]  # Recipients column
            
            # Parse recipients (handle both string and list formats)
            if isinstance(recipients_str, str):
                if recipients_str == '(Δεν επιλέχθηκαν)':
                    print("No recipients selected for this signal")
                    return
                recipients = [r.strip() for r in recipients_str.split(',')]
            else:
                recipients = [str(recipients_str)]
            
            # Open signal folder for ALL recipients
            opened_count = 0
            for recipient in recipients:
                data_path = os.path.join(os.getcwd(), "DATA", recipient, signal_id)
                
                if os.path.exists(data_path):
                    self._open_folder(data_path)
                    opened_count += 1
                    print(f"Opened signal folder: {data_path}")
                else:
                    print(f"Signal folder not found: {data_path}")
            
            if opened_count > 0:
                print(f"Opened {opened_count} signal folders for signal {signal_id}")
            else:
                print(f"No signal folders found for signal {signal_id}")
    
    def _on_extracted_recipient_click(self, event):
        """Handle double-click on extracted recipient - open specific ID folder in BACK UP DATA"""
        selection = self.extracted_tree.selection()
        if not selection:
            return
        
        # Get the selected item values
        item = self.extracted_tree.item(selection[0])
        values = item['values']
        
        if len(values) >= 2:
            recipient = values[1]  # Recipient column
            time_str = values[0]   # Time column
            
            # Find the corresponding history entry to get the file number
            file_number = None
            if hasattr(self.app, 'daily_history'):
                extracted_entries = self.app.daily_history.get_extracted_recipients()
                for entry in extracted_entries:
                    if (entry.get('recipient') == recipient and 
                        entry.get('time') == time_str):
                        file_number = entry.get('file_number')
                        break
            
            if file_number:
                # Build path to specific Α.Φ. folder: BACK UP DATA/recipient/Α.Φ. file_number/
                backup_folder_name = f"Α.Φ. {file_number}"
                specific_backup_path = os.path.join(os.getcwd(), "BACK UP DATA", recipient, backup_folder_name)
                
                if os.path.exists(specific_backup_path):
                    self._open_folder(specific_backup_path)
                    print(f"Opened specific backup folder: {specific_backup_path}")
                else:
                    print(f"Specific backup folder not found: {specific_backup_path}")
                    # Fallback to recipient folder
                    recipient_backup_path = os.path.join(os.getcwd(), "BACK UP DATA", recipient)
                    if os.path.exists(recipient_backup_path):
                        self._open_folder(recipient_backup_path)
                        print(f"Opened recipient backup folder: {recipient_backup_path}")
            else:
                # Fallback to recipient folder if file number is not available
                backup_path = os.path.join(os.getcwd(), "BACK UP DATA", recipient)
                if os.path.exists(backup_path):
                    self._open_folder(backup_path)
                    print(f"Opened backup folder: {backup_path}")
                else:
                    print(f"Backup folder not found: {backup_path}")
    
    def _open_folder(self, folder_path):
        """Open folder in file explorer"""
        try:
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])
        except Exception as e:
            print(f"Error opening folder {folder_path}: {e}")
