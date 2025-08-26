#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core application module for autoPyrseia
"""

import tkinter as tk
from tkinter import ttk
import threading

# Import path manager first to ensure directories
from app.utils.path_manager import ensure_app_directories

# Import managers
from app.services.pdf_processor import PDFProcessor
from app.services.signal_manager import SignalManager
from app.services.usb_extractor import USBExtractor
from app.services.recipients_manager import RecipientsManager
from app.services.config_manager import ConfigManager
from app.services.duplicate_manager import DuplicateManager
from app.services.daily_history import DailyHistoryManager

# Import UI components
from app.ui.widgets.status_bar import StatusBar
from app.ui.utils.keyboard_handlers import KeyboardHandlerMixin
from app.ui.utils.tooltips import create_tooltip
from app.utils.progress_manager import ProgressManager

# Import controllers
from app.controllers.file_watcher import FileWatcher
from app.controllers.signal_controller import SignalController

# Import tab modules
from app.ui.tabs.signal_processing import SignalProcessingTab
from app.ui.tabs.usb_extraction import USBExtractionTab
from app.ui.tabs.recipients_mgmt import RecipientsManagementTab
from app.ui.tabs.daily_history import DailyHistoryTab


class AutoPyrseiaApp(KeyboardHandlerMixin):
    """Main application class"""
    
    def __init__(self):
        # Ensure all application directories exist before anything else
        self.path_manager = ensure_app_directories()
        
        self.root = tk.Tk()
        self.root.title("autoPyrseia v2.0 - Διαχείριση Σημάτων")
        self.root.geometry("800x700")
        self.root.minsize(700, 550)
        self.root.configure(bg='#f0f0f0')
        
        # Initialize managers
        self._init_managers()
        
        # Initialize variables
        self._init_variables()
        
        # Initialize controllers
        self._init_controllers()
        
        # Create UI
        self.create_ui()
        
        # Setup keyboard bindings after UI creation
        self.setup_keyboard_bindings()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _init_managers(self):
        """Initialize all manager instances"""
        self.config_manager = ConfigManager()
        self.pdf_processor = PDFProcessor()
        self.signal_manager = SignalManager()
        self.usb_extractor = USBExtractor(self.config_manager)
        self.recipients_manager = RecipientsManager()
        self.duplicate_manager = DuplicateManager()
        
        # Initialize daily history manager
        self.daily_history = DailyHistoryManager()
        
        # Connect managers
        self.usb_extractor.set_signal_manager(self.signal_manager)
    
    def _init_variables(self):
        """Initialize application variables"""
        self.current_signal_data = None
        self.file_number = tk.StringVar(value=str(self.config_manager.get_next_file_number()))
        self.username = tk.StringVar(value=self.config_manager.get_username())
        self.unofficial_mode = tk.BooleanVar(value=False)
        
        # Lists for checkboxes
        self.recipients_checkboxes = []
        self.extraction_checkboxes = []
        self.manage_checkboxes = []
        
        # Store last extraction data for undo functionality
        self.last_extraction_data = None
        
        # Store references to UI elements for keyboard navigation
        self.username_entry = None
        self.file_number_entry = None
    
    def _init_controllers(self):
        """Initialize controllers"""
        self.file_watcher = FileWatcher(self)
        self.signal_controller = SignalController(self)
    
    def _start_background_tasks(self):
        """Start background tasks"""
        # Scan for JSON files on startup (silently in background)
        self.scan_missing_json_on_startup()
        
        # Start file watcher
        self.file_watcher.start()
    
    def scan_missing_json_on_startup(self):
        """Σάρωση για JSON αρχεία κατά την εκκίνηση της εφαρμογής"""
        def scan_in_background():
            try:
                # Σιωπηλή σάρωση όλων των παραληπτών
                self.signal_manager.scan_and_generate_missing_json_files()
            except Exception as e:
                print(f"Σφάλμα στη σάρωση JSON κατά την εκκίνηση: {e}")
        
        # Εκτέλεση σε background thread για να μην παγώσει το UI
        threading.Thread(target=scan_in_background, daemon=True).start()
    
    def create_ui(self):
        """Create the main user interface"""
        # Header
        self._create_header()
        
        # Status bar - create before tabs to ensure it's always visible
        self.status_bar = StatusBar(self.root)
        
        # Initialize progress manager for coordinated progress updates
        self.progress_manager = ProgressManager(self.status_bar, self.root)
        
        # Configure notebook styling
        self._configure_notebook_style()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=(5, 35))
        
        # Create tabs
        self._create_tabs()
    
    def _create_header(self):
        """Create application header"""
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        header_frame.pack(fill='x', pady=(0, 10))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="autoPyrseia - Διαχείριση Σημάτων", 
                              font=('Arial', 16, 'bold'), bg='#2c3e50', fg='white')
        title_label.pack(pady=15)
    
    def _configure_notebook_style(self):
        """Configure notebook tab styling"""
        style = ttk.Style()
        
        style.configure('TNotebook.Tab', 
                       padding=[20, 8],
                       font=('Arial', 11, 'bold'),
                       focuscolor='none')
        
        style.map('TNotebook.Tab',
                 background=[('selected', '#2c3e50'),
                           ('!selected', '#ecf0f1')],
                 foreground=[('selected', '#2c3e50'),
                           ('!selected', '#2c3e50')],
                 expand=[('selected', [1, 1, 1, 0])])
    
    def _create_tabs(self):
        """Create all application tabs"""
        # Signal Processing Tab
        self.signal_tab = SignalProcessingTab(self.notebook, self)
        
        # USB Extraction Tab
        self.usb_tab = USBExtractionTab(self.notebook, self)
        
        # Recipients Management Tab
        self.recipients_tab = RecipientsManagementTab(self.notebook, self)
        
        # Daily History Tab
        self.history_tab = DailyHistoryTab(self.notebook, self)
    
    def safe_schedule_ui_update(self, callback):
        """Safely schedule UI update from background thread"""
        try:
            if self.root and self.root.winfo_exists():
                self.root.after(0, callback)
        except tk.TclError:
            # Main window has been closed, ignore the update
            pass
        except RuntimeError:
            # Main thread is not in main loop, ignore the update
            pass
    
    def create_tooltip(self, widget, text):
        """Create tooltip for a widget - wrapper for UI utility"""
        create_tooltip(widget, text)
    
    # Delegate methods to signal controller
    def handle_new_signal(self):
        """Handle new signal detection"""
        self.signal_controller.handle_new_signal()
    
    def handle_manual_input_required(self, signal_data):
        """Handle manual input requirement"""
        self.signal_controller.handle_manual_input_required(signal_data)
    
    def process_signal(self):
        """Process the current signal"""
        self.signal_controller.process_signal()
    
    def handle_pdf_error(self, error_message):
        """Handle PDF processing error"""
        self.signal_controller.handle_pdf_error(error_message)
    
    def handle_pdf_deletion(self):
        """Handle PDF deletion"""
        self.signal_controller.handle_pdf_deletion()
    
    # These methods will be delegated to appropriate tab classes
    def display_signal_data(self, signal_data):
        """Display signal data - delegated to signal tab"""
        self.signal_tab.display_signal_data(signal_data)
    
    def clear_signal_display(self):
        """Clear signal display - delegated to signal tab"""
        self.signal_tab.clear_signal_display()
    
    def get_selected_recipients(self):
        """Get selected recipients - delegated to signal tab"""
        return self.signal_tab.get_selected_recipients()
    
    def update_attachment_indicators(self):
        """Update attachment indicators - delegated to signal tab"""
        self.signal_tab.update_attachment_indicators()
    
    def signal_processed_successfully(self, result=None, signal_data=None):
        """Handle successful signal processing"""
        self.signal_tab.signal_processed_successfully(result, signal_data)
        # Also refresh USB extraction list
        self.usb_tab.refresh_extraction_list()
    
    def show_processing_results(self, result):
        """Show processing results - delegated to signal tab"""
        self.signal_tab.show_processing_results(result)
    
    def hide_processing_results(self):
        """Hide processing results - delegated to signal tab"""
        self.signal_tab.hide_processing_results()
    
    def refresh_extraction_list(self):
        """Refresh extraction list - delegated to USB tab"""
        self.usb_tab.refresh_extraction_list()
    
    def extract_to_usb(self):
        """Extract to USB - delegated to USB tab"""
        self.usb_tab.extract_to_usb()
    
    def refresh_recipients_list(self):
        """Refresh recipients list - delegated to recipients tab"""
        self.recipients_tab.refresh_recipients_list()
    
    def run(self):
        """Start the application"""
        # Load initial data
        self.refresh_recipients_list()
        self.refresh_extraction_list()
        
        # Start main loop
        try:
            self.root.mainloop()
        finally:
            # Stop file watcher when application closes
            self.file_watcher.stop()
